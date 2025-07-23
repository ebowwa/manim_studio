"""Resource management utilities for Manim Studio."""

import os
import gc
import threading
import weakref
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Generator
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ResourceInfo:
    """Information about a managed resource."""
    resource_id: str
    resource_type: str
    size_bytes: int = 0
    cleanup_func: Optional[Callable] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: float = field(default_factory=lambda: __import__('time').time())


class ResourceManager:
    """Thread-safe resource manager for handling memory-intensive operations."""
    
    def __init__(self, max_memory_mb: float = 1000):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.resources: Dict[str, ResourceInfo] = {}
        self.resource_refs: Dict[str, Any] = {}
        self._lock = threading.RLock()
        self._cleanup_callbacks: List[Callable] = []
        
    def register_resource(
        self,
        resource_id: str,
        resource: Any,
        resource_type: str,
        size_bytes: int = 0,
        cleanup_func: Optional[Callable] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Register a resource for management."""
        with self._lock:
            # Calculate size if not provided
            if size_bytes == 0:
                size_bytes = self._estimate_size(resource)
            
            # Clean up existing resource with same ID
            if resource_id in self.resources:
                self.release_resource(resource_id)
            
            resource_info = ResourceInfo(
                resource_id=resource_id,
                resource_type=resource_type,
                size_bytes=size_bytes,
                cleanup_func=cleanup_func,
                metadata=metadata or {}
            )
            
            self.resources[resource_id] = resource_info
            self.resource_refs[resource_id] = resource
            
            logger.debug(f"Registered resource {resource_id} ({size_bytes} bytes)")
            
            # Check if we need to clean up resources
            self._check_memory_limits()
    
    def get_resource(self, resource_id: str) -> Optional[Any]:
        """Get a managed resource."""
        with self._lock:
            return self.resource_refs.get(resource_id)
    
    def release_resource(self, resource_id: str) -> bool:
        """Release a specific resource."""
        with self._lock:
            if resource_id not in self.resources:
                return False
            
            resource_info = self.resources[resource_id]
            resource = self.resource_refs.get(resource_id)
            
            # Call custom cleanup function if provided
            if resource_info.cleanup_func and resource:
                try:
                    resource_info.cleanup_func(resource)
                except Exception as e:
                    logger.warning(f"Error in cleanup function for {resource_id}: {e}")
            
            # Generic cleanup based on resource type
            if resource:
                self._generic_cleanup(resource, resource_info.resource_type)
            
            # Remove from tracking
            del self.resources[resource_id]
            if resource_id in self.resource_refs:
                del self.resource_refs[resource_id]
            
            logger.debug(f"Released resource {resource_id}")
            return True
    
    def release_all(self) -> None:
        """Release all managed resources."""
        with self._lock:
            resource_ids = list(self.resources.keys())
            for resource_id in resource_ids:
                self.release_resource(resource_id)
    
    def get_memory_usage(self) -> Dict[str, Any]:
        """Get current memory usage statistics."""
        with self._lock:
            total_size = sum(info.size_bytes for info in self.resources.values())
            
            by_type = {}
            for info in self.resources.values():
                by_type[info.resource_type] = by_type.get(info.resource_type, 0) + info.size_bytes
            
            return {
                'total_bytes': total_size,
                'total_mb': total_size / (1024 * 1024),
                'resource_count': len(self.resources),
                'by_type': by_type,
                'max_memory_mb': self.max_memory_bytes / (1024 * 1024)
            }
    
    def _estimate_size(self, obj: Any) -> int:
        """Estimate the memory size of an object."""
        try:
            import sys
            size = sys.getsizeof(obj)
            
            # For common types, add size of contents
            if hasattr(obj, '__dict__'):
                size += sum(sys.getsizeof(v) for v in obj.__dict__.values())
            elif hasattr(obj, '__len__'):
                try:
                    size += sum(sys.getsizeof(item) for item in obj)
                except (TypeError, AttributeError):
                    pass
            
            return size
        except Exception:
            return 1024  # Default estimate
    
    def _generic_cleanup(self, resource: Any, resource_type: str) -> None:
        """Perform generic cleanup based on resource type."""
        try:
            # Handle different resource types
            if resource_type in ['image', 'texture']:
                # For PIL Images or similar
                if hasattr(resource, 'close'):
                    resource.close()
                elif hasattr(resource, 'unload'):
                    resource.unload()
            
            elif resource_type in ['3d_model', 'mesh']:
                # For 3D models/meshes
                if hasattr(resource, 'unload'):
                    resource.unload()
                elif hasattr(resource, 'clear'):
                    resource.clear()
            
            elif resource_type == 'file_handle':
                # For file handles
                if hasattr(resource, 'close'):
                    resource.close()
            
            elif resource_type == 'numpy_array':
                # For numpy arrays, clear data if possible, but don't use del
                if hasattr(resource, 'resize') and hasattr(resource, 'shape'):
                    try:
                        # Only resize if it's actually a numpy array
                        if hasattr(resource, '__array__'):
                            resource.resize((0,), refcheck=False)
                    except (ValueError, AttributeError):
                        # If resize fails, just let garbage collection handle it
                        pass
            
            # For any resource with explicit cleanup methods
            elif hasattr(resource, '__del__'):
                # Let the object's destructor handle cleanup naturally
                pass
            
        except Exception as e:
            logger.warning(f"Error during generic cleanup: {e}")
    
    def _check_memory_limits(self) -> None:
        """Check memory limits and clean up if necessary."""
        current_usage = sum(info.size_bytes for info in self.resources.values())
        
        if current_usage > self.max_memory_bytes:
            # Sort by age (oldest first) and size (largest first)
            sorted_resources = sorted(
                self.resources.items(),
                key=lambda x: (x[1].created_at, -x[1].size_bytes)
            )
            
            # Release resources until we're under the limit
            for resource_id, _ in sorted_resources:
                if current_usage <= self.max_memory_bytes * 0.8:  # Leave some headroom
                    break
                
                resource_info = self.resources.get(resource_id)
                if resource_info:
                    current_usage -= resource_info.size_bytes
                    self.release_resource(resource_id)
                    logger.info(f"Released resource {resource_id} due to memory limits")
    
    def add_cleanup_callback(self, callback: Callable) -> None:
        """Add a callback to be called during cleanup."""
        self._cleanup_callbacks.append(callback)
    
    def __del__(self):
        """Cleanup when the manager is destroyed."""
        try:
            self.release_all()
            for callback in self._cleanup_callbacks:
                try:
                    callback()
                except Exception as e:
                    logger.warning(f"Error in cleanup callback: {e}")
        except Exception:
            pass


@contextmanager
def managed_resource(
    resource_manager: ResourceManager,
    resource_id: str,
    resource_type: str,
    cleanup_func: Optional[Callable] = None
) -> Generator[Callable[[Any], None], None, None]:
    """Context manager for automatically managed resources.
    
    Usage:
        with managed_resource(manager, "my_image", "image") as register:
            image = load_image("path.jpg")
            register(image)
            # Use image...
        # image is automatically cleaned up
    """
    registered_resource = None
    
    def register(resource: Any, size_bytes: int = 0, metadata: Optional[Dict] = None):
        nonlocal registered_resource
        registered_resource = resource
        resource_manager.register_resource(
            resource_id, resource, resource_type, size_bytes, cleanup_func, metadata
        )
    
    try:
        yield register
    finally:
        if registered_resource is not None:
            resource_manager.release_resource(resource_id)


@contextmanager
def temporary_file_manager(base_dir: Union[str, Path] = None) -> Generator[Path, None, None]:
    """Context manager for temporary file cleanup."""
    import tempfile
    import shutil
    
    if base_dir:
        temp_dir = Path(base_dir) / f"manim_temp_{os.getpid()}"
        temp_dir.mkdir(parents=True, exist_ok=True)
    else:
        temp_dir = Path(tempfile.mkdtemp(prefix="manim_temp_"))
    
    try:
        yield temp_dir
    finally:
        try:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
        except Exception as e:
            logger.warning(f"Failed to cleanup temporary directory {temp_dir}: {e}")


class FileResourceManager:
    """Specialized resource manager for file operations."""
    
    def __init__(self):
        self.open_files: Dict[str, Any] = {}
        self._lock = threading.Lock()
    
    @contextmanager
    def open_file(self, file_path: Union[str, Path], mode: str = 'r', **kwargs) -> Generator[Any, None, None]:
        """Context manager for safe file operations."""
        file_path = str(file_path)
        file_handle = None
        
        try:
            with self._lock:
                file_handle = open(file_path, mode, **kwargs)
                self.open_files[file_path] = file_handle
            
            yield file_handle
            
        except Exception as e:
            logger.error(f"Error with file {file_path}: {e}")
            raise
        finally:
            if file_handle:
                try:
                    file_handle.close()
                except Exception as e:
                    logger.warning(f"Error closing file {file_path}: {e}")
                finally:
                    with self._lock:
                        self.open_files.pop(file_path, None)
    
    def close_all(self) -> None:
        """Close all open files."""
        with self._lock:
            for file_path, file_handle in list(self.open_files.items()):
                try:
                    file_handle.close()
                except Exception as e:
                    logger.warning(f"Error closing file {file_path}: {e}")
            self.open_files.clear()
    
    def __del__(self):
        """Cleanup when the manager is destroyed."""
        try:
            self.close_all()
        except Exception:
            pass


# Global instances
_global_resource_manager: Optional[ResourceManager] = None
_global_file_manager: Optional[FileResourceManager] = None


def get_resource_manager() -> ResourceManager:
    """Get the global resource manager instance."""
    global _global_resource_manager
    if _global_resource_manager is None:
        _global_resource_manager = ResourceManager()
    return _global_resource_manager


def get_file_manager() -> FileResourceManager:
    """Get the global file manager instance."""
    global _global_file_manager
    if _global_file_manager is None:
        _global_file_manager = FileResourceManager()
    return _global_file_manager


def cleanup_all_resources() -> None:
    """Clean up all global resources."""
    global _global_resource_manager, _global_file_manager
    
    try:
        if _global_resource_manager:
            _global_resource_manager.release_all()
        if _global_file_manager:
            _global_file_manager.close_all()
        
        # Force garbage collection
        gc.collect()
        
    except Exception as e:
        logger.warning(f"Error during global cleanup: {e}")


# Register cleanup at module exit
import atexit
atexit.register(cleanup_all_resources)
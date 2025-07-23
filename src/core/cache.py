"""Caching system for Manim Studio."""

import os
import json
import pickle
import hashlib
import time
from pathlib import Path
from typing import Any, Dict, Optional, Union, Callable, Tuple
from functools import wraps
import shutil


class CacheManager:
    """Manages caching for Manim Studio operations."""
    
    def __init__(
        self,
        cache_dir: Optional[Union[str, Path]] = None,
        max_size_mb: float = 500,
        ttl_seconds: Optional[int] = None,
        enabled: bool = True
    ):
        """
        Initialize the cache manager.
        
        Args:
            cache_dir: Directory for cache storage (defaults to .manim_cache)
            max_size_mb: Maximum cache size in MB
            ttl_seconds: Time-to-live for cache entries in seconds
            enabled: Whether caching is enabled
        """
        self.enabled = enabled
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.ttl_seconds = ttl_seconds
        
        # Set up cache directory
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path.home() / '.manim_studio_cache'
        
        if self.enabled:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            
        # Cache metadata file
        self.metadata_file = self.cache_dir / 'cache_metadata.json'
        self.metadata = self._load_metadata()
        
        # In-memory cache for quick access
        self.memory_cache: Dict[str, Any] = {}
        self.memory_cache_size = 0
        self.max_memory_cache_size = 50 * 1024 * 1024  # 50MB
    
    def _load_metadata(self) -> Dict[str, Any]:
        """Load cache metadata from disk."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except:
                return {'entries': {}, 'total_size': 0}
        return {'entries': {}, 'total_size': 0}
    
    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f, indent=2)
    
    def _generate_cache_key(self, *args, **kwargs) -> str:
        """Generate a unique cache key from arguments."""
        key_data = {
            'args': args,
            'kwargs': kwargs
        }
        key_str = json.dumps(key_data, sort_keys=True, default=str)
        return hashlib.sha256(key_str.encode()).hexdigest()
    
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get the file path for a cache key."""
        # Use subdirectories to avoid too many files in one directory
        subdir = cache_key[:2]
        return self.cache_dir / subdir / f"{cache_key}.pkl"
    
    def _is_expired(self, cache_key: str) -> bool:
        """Check if a cache entry has expired."""
        if not self.ttl_seconds:
            return False
            
        if cache_key not in self.metadata['entries']:
            return True
            
        entry = self.metadata['entries'][cache_key]
        age = time.time() - entry['timestamp']
        return age > self.ttl_seconds
    
    def get(self, cache_key: str) -> Optional[Any]:
        """Get a value from cache with proper error handling."""
        if not self.enabled:
            return None
            
        # Check memory cache first
        if cache_key in self.memory_cache:
            if not self._is_expired(cache_key):
                return self.memory_cache[cache_key]
            else:
                del self.memory_cache[cache_key]
        
        # Check disk cache
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists() and not self._is_expired(cache_key):
            try:
                with open(cache_path, 'rb') as f:
                    value = pickle.load(f)
                
                # Add to memory cache if it fits
                try:
                    value_size = len(pickle.dumps(value))
                    if value_size < self.max_memory_cache_size:
                        self.memory_cache[cache_key] = value
                        self.memory_cache_size += value_size
                        self._evict_memory_cache()
                except (pickle.PicklingError, MemoryError) as e:
                    # Skip memory caching if serialization fails
                    pass
                
                return value
            except (pickle.UnpicklingError, IOError, EOFError) as e:
                # Invalid cache file, remove it
                self.delete(cache_key)
                
        return None
    
    def set(self, cache_key: str, value: Any) -> None:
        """Set a value in cache with proper error handling."""
        if not self.enabled:
            return
            
        try:
            # Serialize the value
            serialized = pickle.dumps(value)
            size = len(serialized)
            
            # Check if we need to make room
            self._evict_disk_cache(size)
            
            # Save to disk
            cache_path = self._get_cache_path(cache_key)
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                with open(cache_path, 'wb') as f:
                    f.write(serialized)
            except IOError as e:
                # Failed to write to disk, skip caching
                return
            
            # Update metadata
            self.metadata['entries'][cache_key] = {
                'size': size,
                'timestamp': time.time(),
                'path': str(cache_path)
            }
            self.metadata['total_size'] = self.metadata.get('total_size', 0) + size
            
            try:
                self._save_metadata()
            except IOError:
                # Failed to save metadata, clean up the cache file
                if cache_path.exists():
                    cache_path.unlink()
                return
            
            # Add to memory cache if it fits
            if size < self.max_memory_cache_size:
                try:
                    self.memory_cache[cache_key] = value
                    self.memory_cache_size += size
                    self._evict_memory_cache()
                except MemoryError:
                    # Skip memory caching if we're out of memory
                    pass
                    
        except (pickle.PicklingError, AttributeError, MemoryError) as e:
            # Cannot serialize the value, skip caching
            return
    
    def delete(self, cache_key: str) -> None:
        """Delete a cache entry with proper error handling."""
        if cache_key in self.memory_cache:
            del self.memory_cache[cache_key]
            
        if cache_key in self.metadata['entries']:
            entry = self.metadata['entries'][cache_key]
            cache_path = Path(entry['path'])
            
            try:
                if cache_path.exists():
                    cache_path.unlink()
            except (IOError, OSError) as e:
                # Log but continue with metadata cleanup
                pass
                
            self.metadata['total_size'] -= entry['size']
            del self.metadata['entries'][cache_key]
            
            try:
                self._save_metadata()
            except IOError:
                # Failed to save metadata, but entry is already removed
                pass
    
    def _evict_memory_cache(self) -> None:
        """Evict entries from memory cache if it's too large."""
        if self.memory_cache_size <= self.max_memory_cache_size:
            return
            
        # Sort by access time (simple LRU)
        # In a real implementation, we'd track access times
        keys = list(self.memory_cache.keys())
        
        # Track size reduction as we remove items
        size_removed = 0
        for key in keys[:len(keys)//2]:  # Remove half
            value = self.memory_cache[key]
            try:
                # Calculate size before removing
                size_removed += len(pickle.dumps(value))
            except (pickle.PicklingError, TypeError, MemoryError):
                # If we can't serialize, estimate size as 0 for safety
                # This prevents the cache size from becoming negative
                pass
            del self.memory_cache[key]
            
        # Update size incrementally instead of recalculating
        self.memory_cache_size = max(0, self.memory_cache_size - size_removed)
    
    def _evict_disk_cache(self, needed_size: int) -> None:
        """Evict entries from disk cache to make room."""
        current_size = self.metadata.get('total_size', 0)
        
        if current_size + needed_size <= self.max_size_bytes:
            return
            
        # Sort entries by timestamp (oldest first)
        entries = sorted(
            self.metadata['entries'].items(),
            key=lambda x: x[1]['timestamp']
        )
        
        # Remove oldest entries until we have enough space
        for cache_key, entry in entries:
            if current_size + needed_size <= self.max_size_bytes:
                break
                
            self.delete(cache_key)
            current_size -= entry['size']
    
    def clear(self) -> None:
        """Clear all cache entries with proper error handling."""
        try:
            if self.cache_dir.exists():
                shutil.rmtree(self.cache_dir)
                self.cache_dir.mkdir(parents=True, exist_ok=True)
        except (IOError, OSError) as e:
            # If we can't remove the directory, try to clean individual files
            try:
                for cache_key in list(self.metadata.get('entries', {}).keys()):
                    self.delete(cache_key)
            except Exception:
                pass
            
        self.memory_cache.clear()
        self.memory_cache_size = 0
        self.metadata = {'entries': {}, 'total_size': 0}
        
        try:
            self._save_metadata()
        except IOError:
            # Can't save metadata, but cache is cleared
            pass
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            'enabled': self.enabled,
            'disk_entries': len(self.metadata['entries']),
            'disk_size_mb': self.metadata.get('total_size', 0) / (1024 * 1024),
            'memory_entries': len(self.memory_cache),
            'memory_size_mb': self.memory_cache_size / (1024 * 1024),
            'max_size_mb': self.max_size_bytes / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }
    
    def cached(self, prefix: str = "") -> Callable:
        """Decorator for caching function results."""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs):
                if not self.enabled:
                    return func(*args, **kwargs)
                    
                # Generate cache key
                func_name = f"{prefix}_{func.__name__}" if prefix else func.__name__
                cache_key = self._generate_cache_key(func_name, *args, **kwargs)
                
                # Try to get from cache
                result = self.get(cache_key)
                if result is not None:
                    return result
                
                # Compute and cache result
                result = func(*args, **kwargs)
                self.set(cache_key, result)
                
                return result
            
            return wrapper
        return decorator


class SceneCache:
    """Specialized cache for Manim scenes and animations."""
    
    def __init__(self, cache_manager: CacheManager):
        self.cache_manager = cache_manager
        
    def cache_animation(
        self,
        scene_name: str,
        animation_id: str,
        frames: Any,
        metadata: Optional[Dict] = None
    ) -> None:
        """Cache animation frames."""
        cache_key = f"animation_{scene_name}_{animation_id}"
        cache_data = {
            'frames': frames,
            'metadata': metadata or {},
            'timestamp': time.time()
        }
        self.cache_manager.set(cache_key, cache_data)
    
    def get_animation(
        self,
        scene_name: str,
        animation_id: str
    ) -> Optional[Tuple[Any, Dict]]:
        """Get cached animation frames."""
        cache_key = f"animation_{scene_name}_{animation_id}"
        cache_data = self.cache_manager.get(cache_key)
        
        if cache_data:
            return cache_data['frames'], cache_data['metadata']
        return None
    
    def cache_render(
        self,
        config_hash: str,
        output_path: Path,
        metadata: Optional[Dict] = None
    ) -> None:
        """Cache a rendered video file."""
        cache_key = f"render_{config_hash}"
        
        # Copy the file to cache
        cache_path = self.cache_manager._get_cache_path(cache_key).with_suffix('.mp4')
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(output_path, cache_path)
        
        # Store metadata
        cache_data = {
            'cache_path': str(cache_path),
            'original_path': str(output_path),
            'metadata': metadata or {},
            'timestamp': time.time()
        }
        self.cache_manager.set(cache_key, cache_data)
    
    def get_render(self, config_hash: str) -> Optional[Path]:
        """Get cached render file."""
        cache_key = f"render_{config_hash}"
        cache_data = self.cache_manager.get(cache_key)
        
        if cache_data:
            cache_path = Path(cache_data['cache_path'])
            if cache_path.exists():
                return cache_path
                
        return None


# Global cache instance
_global_cache: Optional[CacheManager] = None


def get_cache() -> CacheManager:
    """Get the global cache instance."""
    global _global_cache
    if _global_cache is None:
        _global_cache = CacheManager()
    return _global_cache


def configure_cache(**kwargs) -> None:
    """Configure the global cache instance."""
    global _global_cache
    _global_cache = CacheManager(**kwargs)
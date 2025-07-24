"""Buffer Manager for Neovim Integration

Manages buffer synchronization and live preview functionality for Manim Studio scenes.
Provides real-time updates and preview generation as users edit YAML files.
"""

import asyncio
import hashlib
import json
import logging
import os
import threading
import time
import yaml
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable
from dataclasses import dataclass
from datetime import datetime

# Import shared features
from src.interfaces.shared import (
    ManimStudioCore, 
    AnimationType, 
    ShapeType, 
    RenderQuality,
    InterfaceResult
)

logger = logging.getLogger(__name__)


@dataclass
class BufferState:
    """Represents the state of a buffer being managed."""
    filepath: str
    content: str
    content_hash: str
    last_modified: float
    last_rendered: Optional[float] = None
    render_output: Optional[str] = None
    is_valid: bool = True
    validation_errors: List[str] = None
    
    def __post_init__(self):
        if self.validation_errors is None:
            self.validation_errors = []


class BufferManager:
    """Manages Neovim buffers for live preview and synchronization."""
    
    def __init__(self, auto_render: bool = False, render_delay: float = 2.0):
        from src.interfaces.shared import shared_core
        self.core = shared_core
        
        # Configuration
        self.auto_render = auto_render
        self.render_delay = render_delay  # Seconds to wait before auto-render
        self.preview_quality = RenderQuality.LOW
        
        # Buffer tracking
        self.buffers: Dict[str, BufferState] = {}
        self.preview_outputs: Dict[str, str] = {}  # filepath -> output_path
        
        # Threading for background operations
        self.render_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.render_queue: asyncio.Queue = asyncio.Queue()
        
        # Callbacks
        self.on_buffer_changed: Optional[Callable[[str, BufferState], None]] = None
        self.on_render_complete: Optional[Callable[[str, str], None]] = None
        self.on_validation_error: Optional[Callable[[str, List[str]], None]] = None
        
        # Initialize YAML validator if available
        try:
            from src.core.yaml_validator import YAMLValidator
            self.validator = YAMLValidator()
        except ImportError:
            self.validator = None
            logger.warning("YAML validator not available - basic validation only")
    
    def register_buffer(self, filepath: str, content: str = None) -> BufferState:
        """Register a new buffer for management."""
        filepath = os.path.abspath(filepath)
        
        # Read content from file if not provided
        if content is None:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
            except (IOError, OSError) as e:
                logger.error(f"Failed to read file {filepath}: {e}")
                content = ""
        
        # Create buffer state
        buffer_state = BufferState(
            filepath=filepath,
            content=content,
            content_hash=self._calculate_hash(content),
            last_modified=time.time()
        )
        
        # Validate content
        self._validate_buffer(buffer_state)
        
        # Store buffer
        self.buffers[filepath] = buffer_state
        
        logger.info(f"Registered buffer: {filepath}")
        
        # Trigger callback
        if self.on_buffer_changed:
            self.on_buffer_changed(filepath, buffer_state)
        
        return buffer_state
    
    def update_buffer(self, filepath: str, content: str) -> BufferState:
        """Update buffer content and trigger processing."""
        filepath = os.path.abspath(filepath)
        
        # Calculate new hash
        new_hash = self._calculate_hash(content)
        
        # Check if content actually changed
        if filepath in self.buffers:
            old_buffer = self.buffers[filepath]
            if old_buffer.content_hash == new_hash:
                return old_buffer  # No change
        
        # Update or create buffer state
        buffer_state = BufferState(
            filepath=filepath,
            content=content,
            content_hash=new_hash,
            last_modified=time.time(),
            last_rendered=self.buffers.get(filepath, {}).get('last_rendered') if filepath in self.buffers else None,
            render_output=self.buffers.get(filepath, {}).get('render_output') if filepath in self.buffers else None
        )
        
        # Validate content
        self._validate_buffer(buffer_state)
        
        # Store updated buffer
        self.buffers[filepath] = buffer_state
        
        logger.debug(f"Updated buffer: {filepath}")
        
        # Trigger callback
        if self.on_buffer_changed:
            self.on_buffer_changed(filepath, buffer_state)
        
        # Queue for auto-render if enabled and valid
        if self.auto_render and buffer_state.is_valid:
            self._queue_render(filepath)
        
        return buffer_state
    
    def remove_buffer(self, filepath: str) -> bool:
        """Remove buffer from management."""
        filepath = os.path.abspath(filepath)
        
        if filepath in self.buffers:
            del self.buffers[filepath]
            
            # Clean up preview output if exists
            if filepath in self.preview_outputs:
                output_path = self.preview_outputs[filepath]
                try:
                    if os.path.exists(output_path):
                        os.remove(output_path)
                except (IOError, OSError):
                    pass
                del self.preview_outputs[filepath]
            
            logger.info(f"Removed buffer: {filepath}")
            return True
        
        return False
    
    def get_buffer_state(self, filepath: str) -> Optional[BufferState]:
        """Get current state of a buffer."""
        filepath = os.path.abspath(filepath)
        return self.buffers.get(filepath)
    
    def list_buffers(self) -> List[str]:
        """List all managed buffer filepaths."""
        return list(self.buffers.keys())
    
    def render_buffer(self, filepath: str, quality: Optional[RenderQuality] = None, 
                     force: bool = False) -> InterfaceResult:
        """Render a specific buffer to video."""
        filepath = os.path.abspath(filepath)
        
        if filepath not in self.buffers:
            return InterfaceResult(
                status="error",
                error=f"Buffer not found: {filepath}"
            )
        
        buffer_state = self.buffers[filepath]
        
        # Check if valid
        if not buffer_state.is_valid and not force:
            return InterfaceResult(
                status="error",
                error="Buffer has validation errors. Use force=True to render anyway.",
                data={"validation_errors": buffer_state.validation_errors}
            )
        
        # Use default quality if not specified
        if quality is None:
            quality = self.preview_quality
        
        try:
            # Parse YAML content
            yaml_data = yaml.safe_load(buffer_state.content)
            
            # Import scene
            import_result = self.core.import_scene(yaml_data)
            if import_result.status != "success":
                return InterfaceResult(
                    status="error",
                    error=f"Failed to import scene: {import_result.error}"
                )
            
            # Generate output path
            output_dir = Path(filepath).parent / "preview_output"
            output_dir.mkdir(exist_ok=True)
            
            scene_name = yaml_data.get('scene', {}).get('name', 'preview')
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_filename = f"{scene_name}_{timestamp}.mp4"
            output_path = str(output_dir / output_filename)
            
            # Render scene
            render_result = self.core.render_scene(
                output_path=output_path,
                quality=quality.value if isinstance(quality, RenderQuality) else quality,
                preview=False,
                save_script=True
            )
            
            if render_result.status == "success":
                # Update buffer state
                buffer_state.last_rendered = time.time()
                buffer_state.render_output = output_path
                self.preview_outputs[filepath] = output_path
                
                # Trigger callback
                if self.on_render_complete:
                    self.on_render_complete(filepath, output_path)
                
                logger.info(f"Rendered buffer {filepath} to {output_path}")
                
                return InterfaceResult(
                    status="success",
                    data={
                        "output_path": output_path,
                        "filepath": filepath,
                        "quality": quality.value if isinstance(quality, RenderQuality) else quality,
                        "file_size": os.path.getsize(output_path) if os.path.exists(output_path) else None
                    },
                    message=f"Buffer rendered successfully to {output_path}"
                )
            else:
                return render_result
                
        except yaml.YAMLError as e:
            return InterfaceResult(
                status="error",
                error=f"YAML parsing error: {str(e)}"
            )
        except Exception as e:
            logger.error(f"Error rendering buffer {filepath}: {e}")
            return InterfaceResult(
                status="error",
                error=f"Render error: {str(e)}"
            )
    
    def get_preview_path(self, filepath: str) -> Optional[str]:
        """Get the preview output path for a buffer."""
        filepath = os.path.abspath(filepath)
        return self.preview_outputs.get(filepath)
    
    def start_auto_render(self):
        """Start background auto-rendering."""
        if self.render_thread and self.render_thread.is_alive():
            return  # Already running
        
        self.stop_event.clear()
        self.render_thread = threading.Thread(target=self._render_worker, daemon=True)
        self.render_thread.start()
        
        logger.info("Started auto-render background thread")
    
    def stop_auto_render(self):
        """Stop background auto-rendering."""
        if self.render_thread and self.render_thread.is_alive():
            self.stop_event.set()
            self.render_thread.join(timeout=5.0)
            
        logger.info("Stopped auto-render background thread")
    
    def cleanup(self):
        """Clean up resources."""
        self.stop_auto_render()
        
        # Clean up preview outputs
        for output_path in self.preview_outputs.values():
            try:
                if os.path.exists(output_path):
                    os.remove(output_path)
            except (IOError, OSError):
                pass
        
        self.buffers.clear()
        self.preview_outputs.clear()
        
        logger.info("Buffer manager cleaned up")
    
    def _calculate_hash(self, content: str) -> str:
        """Calculate MD5 hash of content."""
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def _validate_buffer(self, buffer_state: BufferState):
        """Validate buffer content and update state."""
        try:
            # Basic YAML parsing
            yaml_data = yaml.safe_load(buffer_state.content)
            
            # Enhanced validation if validator available
            if self.validator:
                result = self.validator.validate_content(
                    buffer_state.content, 
                    buffer_state.filepath
                )
                
                buffer_state.is_valid = result.get('valid', True)
                buffer_state.validation_errors = []
                
                # Collect errors and warnings
                for error in result.get('errors', []):
                    buffer_state.validation_errors.append(f"Error: {error['message']}")
                
                for warning in result.get('warnings', []):
                    buffer_state.validation_errors.append(f"Warning: {warning['message']}")
            else:
                # Basic validation - just check if YAML is parseable
                buffer_state.is_valid = yaml_data is not None
                buffer_state.validation_errors = []
            
            # Trigger validation callback if there are errors
            if buffer_state.validation_errors and self.on_validation_error:
                self.on_validation_error(buffer_state.filepath, buffer_state.validation_errors)
                
        except yaml.YAMLError as e:
            buffer_state.is_valid = False
            buffer_state.validation_errors = [f"YAML Error: {str(e)}"]
            
            if self.on_validation_error:
                self.on_validation_error(buffer_state.filepath, buffer_state.validation_errors)
        
        except Exception as e:
            logger.error(f"Validation error for {buffer_state.filepath}: {e}")
            buffer_state.is_valid = False
            buffer_state.validation_errors = [f"Validation Error: {str(e)}"]
    
    def _queue_render(self, filepath: str):
        """Queue a file for rendering after delay."""
        try:
            # Use asyncio queue in a thread-safe way
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.render_queue.put((filepath, time.time())))
            loop.close()
        except Exception as e:
            logger.error(f"Error queuing render for {filepath}: {e}")
    
    def _render_worker(self):
        """Background thread worker for auto-rendering."""
        logger.info("Auto-render worker started")
        
        while not self.stop_event.is_set():
            try:
                # Check render queue
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    # Wait for items with timeout
                    filepath, queue_time = loop.run_until_complete(
                        asyncio.wait_for(self.render_queue.get(), timeout=1.0)
                    )
                    
                    # Check if enough time has passed since queuing
                    if time.time() - queue_time >= self.render_delay:
                        # Check if buffer still exists and is valid
                        if filepath in self.buffers:
                            buffer_state = self.buffers[filepath]
                            
                            # Only render if content hasn't changed since queuing
                            if buffer_state.is_valid:
                                logger.info(f"Auto-rendering {filepath}")
                                self.render_buffer(filepath, self.preview_quality)
                            else:
                                logger.debug(f"Skipping auto-render for {filepath} - validation errors")
                    else:
                        # Re-queue for later
                        loop.run_until_complete(self.render_queue.put((filepath, queue_time)))
                
                except asyncio.TimeoutError:
                    # No items in queue, continue loop
                    pass
                
                finally:
                    loop.close()
                
            except Exception as e:
                logger.error(f"Error in render worker: {e}")
            
            # Small delay to prevent busy waiting
            time.sleep(0.1)
        
        logger.info("Auto-render worker stopped")


# Utility functions for Neovim integration
def create_buffer_manager(auto_render: bool = False, render_delay: float = 2.0) -> BufferManager:
    """Create a new buffer manager instance."""
    return BufferManager(auto_render=auto_render, render_delay=render_delay)


def setup_buffer_callbacks(manager: BufferManager, 
                          on_change: Optional[Callable] = None,
                          on_render: Optional[Callable] = None,
                          on_error: Optional[Callable] = None):
    """Setup callbacks for buffer events."""
    if on_change:
        manager.on_buffer_changed = on_change
    if on_render:
        manager.on_render_complete = on_render
    if on_error:
        manager.on_validation_error = on_error


if __name__ == "__main__":
    import sys
    
    # Simple test/demo
    if len(sys.argv) < 2:
        print("Usage: python buffer_manager.py <yaml_file>")
        sys.exit(1)
    
    yaml_file = sys.argv[1]
    
    # Create buffer manager
    manager = BufferManager(auto_render=True, render_delay=1.0)
    
    # Setup callbacks
    def on_change(filepath, state):
        print(f"Buffer changed: {filepath} (valid: {state.is_valid})")
    
    def on_render(filepath, output):
        print(f"Render complete: {filepath} -> {output}")
    
    def on_error(filepath, errors):
        print(f"Validation errors in {filepath}:")
        for error in errors:
            print(f"  {error}")
    
    setup_buffer_callbacks(manager, on_change, on_render, on_error)
    
    # Register buffer
    try:
        buffer_state = manager.register_buffer(yaml_file)
        print(f"Registered buffer: {yaml_file}")
        print(f"Valid: {buffer_state.is_valid}")
        
        if buffer_state.validation_errors:
            print("Validation errors:")
            for error in buffer_state.validation_errors:
                print(f"  {error}")
        
        # Start auto-render
        manager.start_auto_render()
        
        # Keep running for demo
        print("Press Ctrl+C to stop...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nStopping...")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        manager.cleanup()
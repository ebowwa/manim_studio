"""Auto-layered scene implementation with automatic mobject registration."""

from typing import Optional, Union, List, Dict, Any
from contextlib import contextmanager
from manim import Scene, Mobject, VGroup, Animation
from .composer_timeline import ComposerTimeline
from .layer_manager import LayerManager


class AutoLayeredScene(Scene):
    """Scene with automatic layer management for all mobjects.
    
    This scene automatically handles layer registration without requiring
    manual calls to register_mobject(). Simply use add() with an optional
    layer parameter.
    
    Example:
        scene = AutoLayeredScene()
        scene.add(circle, layer="Foreground")  # Auto-registered
        scene.add(square)  # Goes to default layer
    """
    
    def __init__(self, timeline: Optional[ComposerTimeline] = None, 
                 default_layer: str = "Main", **kwargs):
        super().__init__(**kwargs)
        
        # Initialize timeline and layer system
        self.timeline = timeline or ComposerTimeline(duration=30.0)
        self.layer_manager = LayerManager(self.timeline)
        self.default_layer = default_layer
        self.current_layer = default_layer
        
        # Track which objects are in which layers
        self._mobject_layers: Dict[int, str] = {}  # id(mob) -> layer_name
        
        # Ensure default layers exist
        self._ensure_default_layers()
        
        # Auto-apply ordering after animations
        self._auto_reorder = True
        self._reorder_pending = False
    
    def _ensure_default_layers(self):
        """Ensure common layers exist with proper z-indices."""
        default_layers = [
            ("Background", 0),
            ("Main", 100),
            ("Foreground", 200),
            ("UI", 300),
            ("Overlay", 400)
        ]
        
        for layer_name, z_index in default_layers:
            if not self.timeline.get_layer(layer_name):
                self.timeline.add_layer(layer_name, z_index=z_index)
    
    def add(self, *mobjects: Mobject, layer: Optional[str] = None, 
            auto_order: bool = True, **kwargs) -> None:
        """Add mobjects to the scene with automatic layer registration.
        
        Args:
            *mobjects: Mobjects to add
            layer: Layer name (uses current_layer if None)
            auto_order: Whether to automatically reorder layers
            **kwargs: Additional arguments passed to parent add()
        """
        # Determine which layer to use
        target_layer = layer or self.current_layer
        
        # Ensure layer exists
        if not self.timeline.get_layer(target_layer):
            # Auto-create layer with next available z-index
            max_z = max((l.z_index for l in self.timeline.layers), default=0)
            self.timeline.add_layer(target_layer, z_index=max_z + 100)
        
        # Add mobjects to scene first
        super().add(*mobjects, **kwargs)
        
        # Register each mobject with the layer system
        for mob in mobjects:
            self._register_mobject_tree(mob, target_layer)
        
        # Apply ordering if requested
        if auto_order and self._auto_reorder:
            self._schedule_reorder()
    
    def _register_mobject_tree(self, mobject: Mobject, layer: str):
        """Recursively register a mobject and its submobjects."""
        # Register the mobject
        mob_id = id(mobject)
        self._mobject_layers[mob_id] = layer
        self.layer_manager.register_mobject(layer, mobject)
        
        # Handle VGroups and submobjects
        if isinstance(mobject, VGroup):
            for submob in mobject.submobjects:
                self._register_mobject_tree(submob, layer)
    
    def remove(self, *mobjects: Mobject, auto_order: bool = True) -> None:
        """Remove mobjects with automatic layer deregistration.
        
        Args:
            *mobjects: Mobjects to remove
            auto_order: Whether to automatically reorder layers
        """
        # Deregister each mobject
        for mob in mobjects:
            self._deregister_mobject_tree(mob)
        
        # Remove from scene
        super().remove(*mobjects)
        
        # Apply ordering if requested
        if auto_order and self._auto_reorder:
            self._schedule_reorder()
    
    def _deregister_mobject_tree(self, mobject: Mobject):
        """Recursively deregister a mobject and its submobjects."""
        mob_id = id(mobject)
        
        # Deregister if tracked
        if mob_id in self._mobject_layers:
            self.layer_manager.unregister_mobject(mobject)
            del self._mobject_layers[mob_id]
        
        # Handle submobjects
        if isinstance(mobject, VGroup):
            for submob in mobject.submobjects:
                self._deregister_mobject_tree(submob)
    
    def move_to_layer(self, mobject: Mobject, new_layer: str, 
                      auto_order: bool = True) -> bool:
        """Move a mobject to a different layer.
        
        Args:
            mobject: The mobject to move
            new_layer: Target layer name
            auto_order: Whether to automatically reorder
            
        Returns:
            bool: True if successful
        """
        mob_id = id(mobject)
        
        # Check if mobject is tracked
        if mob_id not in self._mobject_layers:
            # Not tracked, just add it to the new layer
            self._register_mobject_tree(mobject, new_layer)
        else:
            # Move to new layer
            old_layer = self._mobject_layers[mob_id]
            if self.layer_manager.move_mobject_to_layer(mobject, new_layer):
                self._mobject_layers[mob_id] = new_layer
                
                # Update submobjects if it's a VGroup
                if isinstance(mobject, VGroup):
                    for submob in mobject.submobjects:
                        sub_id = id(submob)
                        if sub_id in self._mobject_layers:
                            self._mobject_layers[sub_id] = new_layer
        
        if auto_order and self._auto_reorder:
            self._schedule_reorder()
        
        return True
    
    @contextmanager
    def use_layer(self, layer_name: str):
        """Context manager to temporarily switch the current layer.
        
        Example:
            with scene.use_layer("Background"):
                scene.add(background_rect)  # Goes to Background layer
                scene.add(stars)  # Also goes to Background layer
        """
        previous_layer = self.current_layer
        self.current_layer = layer_name
        try:
            yield
        finally:
            self.current_layer = previous_layer
    
    @contextmanager
    def auto_ordering(self, enabled: bool = True):
        """Context manager to control automatic ordering.
        
        Example:
            with scene.auto_ordering(False):
                # Add many objects without reordering each time
                for i in range(100):
                    scene.add(Dot(), layer="Particles")
            # Reordering happens once at the end
        """
        previous_state = self._auto_reorder
        self._auto_reorder = enabled
        try:
            yield
        finally:
            self._auto_reorder = previous_state
            if self._reorder_pending and enabled:
                self.apply_layer_ordering()
    
    def _schedule_reorder(self):
        """Schedule a reorder to happen at the next opportunity."""
        if self._auto_reorder:
            self.apply_layer_ordering()
        else:
            self._reorder_pending = True
    
    def apply_layer_ordering(self):
        """Apply the current layer ordering to all mobjects."""
        self.layer_manager.apply_layer_ordering(self)
        self._reorder_pending = False
    
    def play(self, *animations: Animation, **kwargs) -> None:
        """Play animations with automatic layer ordering maintenance."""
        result = super().play(*animations, **kwargs)
        
        # Check if any new objects were added during animation
        for animation in animations:
            if hasattr(animation, 'mobject') and animation.mobject:
                mob_id = id(animation.mobject)
                if mob_id not in self._mobject_layers:
                    # Auto-register objects created during animation
                    self._register_mobject_tree(animation.mobject, self.current_layer)
        
        # Reorder after animation if needed
        if self._auto_reorder:
            self.apply_layer_ordering()
        
        return result
    
    def wait(self, duration: float = 1.0, **kwargs) -> None:
        """Wait with layer ordering maintenance."""
        if self._reorder_pending and self._auto_reorder:
            self.apply_layer_ordering()
        super().wait(duration, **kwargs)
    
    # Layer manipulation shortcuts
    
    def bring_to_layer_front(self, layer_name: str):
        """Bring a layer to the front (highest z-index)."""
        self.timeline.move_layer_to_top(layer_name)
        self.apply_layer_ordering()
    
    def send_to_layer_back(self, layer_name: str):
        """Send a layer to the back (lowest z-index)."""
        self.timeline.move_layer_to_bottom(layer_name)
        self.apply_layer_ordering()
    
    def hide_layer(self, layer_name: str):
        """Hide all objects in a layer."""
        self.layer_manager.hide_layer(self, layer_name)
    
    def show_layer(self, layer_name: str):
        """Show all objects in a layer."""
        self.layer_manager.show_layer(self, layer_name)
    
    def solo_layer(self, layer_name: str):
        """Solo a layer (hide all others)."""
        self.layer_manager.solo_layer(self, layer_name)
    
    def unsolo_all_layers(self):
        """Remove solo from all layers."""
        self.layer_manager.unsolo_all_layers(self)
    
    def get_layer_objects(self, layer_name: str) -> List[Mobject]:
        """Get all objects in a specific layer."""
        return self.layer_manager.get_layer_mobjects(layer_name)
    
    def get_object_layer(self, mobject: Mobject) -> Optional[str]:
        """Get the layer name for a mobject."""
        mob_id = id(mobject)
        return self._mobject_layers.get(mob_id)
    
    # Batch operations
    
    def add_batch(self, mobjects_by_layer: Dict[str, List[Mobject]]):
        """Add multiple objects to different layers efficiently.
        
        Args:
            mobjects_by_layer: Dict mapping layer names to lists of mobjects
        """
        with self.auto_ordering(False):
            for layer_name, mobjects in mobjects_by_layer.items():
                self.add(*mobjects, layer=layer_name)
        self.apply_layer_ordering()
    
    def clear_layer(self, layer_name: str):
        """Remove all objects from a specific layer."""
        objects = self.get_layer_objects(layer_name)
        if objects:
            self.remove(*objects)
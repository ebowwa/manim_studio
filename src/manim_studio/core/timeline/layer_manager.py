"""Layer management utilities for integrating timeline layers with Manim scenes."""

from typing import Dict, List, Any, Optional, Callable
from manim import Scene, Mobject, VGroup
from .composer_timeline import ComposerTimeline, TimelineLayer


class LayerManager:
    """Manages the integration between timeline layers and Manim scene rendering."""
    
    def __init__(self, timeline: ComposerTimeline):
        self.timeline = timeline
        self.layer_mobjects: Dict[str, List[Mobject]] = {}
        self.layer_groups: Dict[str, VGroup] = {}
        self.update_callbacks: Dict[str, List[Callable]] = {}
        
    def register_mobject(self, layer_name: str, mobject: Mobject, 
                        tag: Optional[str] = None) -> bool:
        """Register a mobject with a specific layer.
        
        Args:
            layer_name: Name of the layer
            mobject: The Manim mobject to register
            tag: Optional tag for categorizing the mobject
            
        Returns:
            bool: True if successful, False if layer doesn't exist
        """
        layer = self.timeline.get_layer(layer_name)
        if not layer:
            return False
        
        if layer_name not in self.layer_mobjects:
            self.layer_mobjects[layer_name] = []
            self.layer_groups[layer_name] = VGroup()
        
        self.layer_mobjects[layer_name].append(mobject)
        self.layer_groups[layer_name].add(mobject)
        
        # Add metadata
        mobject.layer_name = layer_name
        mobject.layer_tag = tag
        
        return True
    
    def unregister_mobject(self, mobject: Mobject) -> bool:
        """Remove a mobject from its layer.
        
        Args:
            mobject: The mobject to remove
            
        Returns:
            bool: True if found and removed, False otherwise
        """
        if hasattr(mobject, 'layer_name'):
            layer_name = mobject.layer_name
            if layer_name in self.layer_mobjects:
                if mobject in self.layer_mobjects[layer_name]:
                    self.layer_mobjects[layer_name].remove(mobject)
                    self.layer_groups[layer_name].remove(mobject)
                    return True
        return False
    
    def apply_layer_ordering(self, scene: Scene):
        """Apply layer z-ordering to all registered mobjects in the scene.
        
        This method removes all mobjects and re-adds them in the proper
        z-order based on their layer's z_index.
        
        Args:
            scene: The Manim scene to reorder
        """
        # Get all current mobjects
        all_mobjects = list(scene.mobjects)
        
        # Build ordered list based on layers
        ordered_mobjects = []
        
        for layer in self.timeline.get_layers_ordered():
            if layer.name in self.layer_mobjects:
                # Apply layer properties
                for mob in self.layer_mobjects[layer.name]:
                    # Apply visibility
                    if hasattr(mob, 'set_opacity'):
                        mob.set_opacity(layer.opacity if layer.visible else 0)
                    
                    # Apply transform if supported
                    if layer.transform and hasattr(mob, 'shift') and hasattr(mob, 'scale'):
                        if layer.transform.get('x', 0) != 0 or layer.transform.get('y', 0) != 0:
                            mob.shift([layer.transform['x'], layer.transform['y'], 0])
                        if layer.transform.get('scale', 1) != 1:
                            mob.scale(layer.transform['scale'])
                        if layer.transform.get('rotation', 0) != 0:
                            mob.rotate(layer.transform['rotation'])
                
                if layer.visible:
                    ordered_mobjects.extend(self.layer_mobjects[layer.name])
        
        # Add any unregistered mobjects at the end
        for mob in all_mobjects:
            if not hasattr(mob, 'layer_name'):
                ordered_mobjects.append(mob)
        
        # Clear and re-add in order
        scene.remove(*all_mobjects)
        scene.add(*ordered_mobjects)
    
    def create_layer_scene_wrapper(self, scene_class):
        """Create a scene wrapper that automatically handles layer ordering.
        
        Args:
            scene_class: The original Scene class to wrap
            
        Returns:
            A new Scene class with automatic layer management
        """
        layer_manager = self
        
        class LayeredScene(scene_class):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.layer_manager = layer_manager
                
            def add(self, *mobjects, layer: Optional[str] = None):
                """Override add to register with layers."""
                super().add(*mobjects)
                
                if layer:
                    for mob in mobjects:
                        self.layer_manager.register_mobject(layer, mob)
                    self.layer_manager.apply_layer_ordering(self)
            
            def remove(self, *mobjects):
                """Override remove to unregister from layers."""
                for mob in mobjects:
                    self.layer_manager.unregister_mobject(mob)
                super().remove(*mobjects)
            
            def wait(self, *args, **kwargs):
                """Override wait to maintain layer ordering."""
                self.layer_manager.apply_layer_ordering(self)
                super().wait(*args, **kwargs)
            
            def play(self, *animations, **kwargs):
                """Override play to maintain layer ordering."""
                result = super().play(*animations, **kwargs)
                self.layer_manager.apply_layer_ordering(self)
                return result
        
        return LayeredScene
    
    def move_mobject_to_layer(self, mobject: Mobject, new_layer: str) -> bool:
        """Move a mobject from its current layer to a new layer.
        
        Args:
            mobject: The mobject to move
            new_layer: Name of the target layer
            
        Returns:
            bool: True if successful
        """
        # First unregister from current layer
        self.unregister_mobject(mobject)
        
        # Then register with new layer
        return self.register_mobject(new_layer, mobject)
    
    def get_layer_mobjects(self, layer_name: str) -> List[Mobject]:
        """Get all mobjects in a specific layer.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            List of mobjects in the layer
        """
        return self.layer_mobjects.get(layer_name, [])
    
    def get_layer_group(self, layer_name: str) -> Optional[VGroup]:
        """Get the VGroup containing all mobjects in a layer.
        
        Args:
            layer_name: Name of the layer
            
        Returns:
            VGroup of layer mobjects or None
        """
        return self.layer_groups.get(layer_name)
    
    def hide_layer(self, scene: Scene, layer_name: str):
        """Hide all mobjects in a layer.
        
        Args:
            scene: The Manim scene
            layer_name: Name of the layer to hide
        """
        layer = self.timeline.get_layer(layer_name)
        if layer:
            layer.visible = False
            self.apply_layer_ordering(scene)
    
    def show_layer(self, scene: Scene, layer_name: str):
        """Show all mobjects in a layer.
        
        Args:
            scene: The Manim scene
            layer_name: Name of the layer to show
        """
        layer = self.timeline.get_layer(layer_name)
        if layer:
            layer.visible = True
            self.apply_layer_ordering(scene)
    
    def solo_layer(self, scene: Scene, layer_name: str):
        """Solo a layer (hide all others).
        
        Args:
            scene: The Manim scene
            layer_name: Name of the layer to solo
        """
        for layer in self.timeline.layers:
            layer.solo = (layer.name == layer_name)
        self.apply_layer_ordering(scene)
    
    def unsolo_all_layers(self, scene: Scene):
        """Remove solo from all layers.
        
        Args:
            scene: The Manim scene
        """
        for layer in self.timeline.layers:
            layer.solo = False
        self.apply_layer_ordering(scene)
    
    def add_layer_update_callback(self, layer_name: str, callback: Callable):
        """Add a callback that's triggered when a layer is updated.
        
        Args:
            layer_name: Name of the layer
            callback: Function to call on layer update
        """
        if layer_name not in self.update_callbacks:
            self.update_callbacks[layer_name] = []
        self.update_callbacks[layer_name].append(callback)
    
    def trigger_layer_updates(self, layer_name: str):
        """Trigger all update callbacks for a layer.
        
        Args:
            layer_name: Name of the layer
        """
        if layer_name in self.update_callbacks:
            for callback in self.update_callbacks[layer_name]:
                callback(self.timeline.get_layer(layer_name))


def create_layered_scene(timeline: ComposerTimeline):
    """Factory function to create a Scene with built-in layer support.
    
    Args:
        timeline: The ComposerTimeline to use
        
    Returns:
        A Scene class with layer management
    """
    layer_manager = LayerManager(timeline)
    
    class LayeredScene(Scene):
        def __init__(self):
            super().__init__()
            self.timeline = timeline
            self.layers = layer_manager
            
        def add_to_layer(self, layer_name: str, *mobjects):
            """Add mobjects to a specific layer."""
            self.add(*mobjects)
            for mob in mobjects:
                self.layers.register_mobject(layer_name, mob)
            self.layers.apply_layer_ordering(self)
        
        def remove_from_layer(self, *mobjects):
            """Remove mobjects and unregister from layers."""
            for mob in mobjects:
                self.layers.unregister_mobject(mob)
            self.remove(*mobjects)
        
        def play(self, *animations, **kwargs):
            """Override play to maintain layer ordering."""
            result = super().play(*animations, **kwargs)
            self.layers.apply_layer_ordering(self)
            return result
        
        def wait(self, *args, **kwargs):
            """Override wait to maintain layer ordering."""
            self.layers.apply_layer_ordering(self)
            super().wait(*args, **kwargs)
        
        def bring_layer_to_front(self, layer_name: str):
            """Bring a layer to the front."""
            self.timeline.move_layer_to_top(layer_name)
            self.layers.apply_layer_ordering(self)
        
        def send_layer_to_back(self, layer_name: str):
            """Send a layer to the back."""
            self.timeline.move_layer_to_bottom(layer_name)
            self.layers.apply_layer_ordering(self)
        
        def reorder_layers(self):
            """Apply current layer ordering."""
            self.layers.apply_layer_ordering(self)
    
    return LayeredScene
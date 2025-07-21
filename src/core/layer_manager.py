"""Layer manager for proper z-index management in 2D animations."""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import IntEnum

class LayerDepth(IntEnum):
    """Predefined layer depths for consistent z-ordering."""
    BACKGROUND = -1000
    ENVIRONMENT = -500
    MAIN_BACK = -100
    MAIN = 0
    MAIN_FRONT = 100
    EFFECTS_BACK = 200
    EFFECTS = 300
    EFFECTS_FRONT = 400
    FOREGROUND = 500
    OVERLAY = 800
    UI = 1000

@dataclass
class LayerObject:
    """Represents an object in a layer with depth information."""
    mobject: any
    layer_name: str
    sub_index: int = 0
    custom_z_offset: float = 0

class LayerManager:
    """Manages z-index ordering for objects based on layer hierarchy."""
    
    def __init__(self):
        self.layer_depths = {
            "background": LayerDepth.BACKGROUND,
            "environment": LayerDepth.ENVIRONMENT,
            "main": LayerDepth.MAIN,
            "objects": LayerDepth.MAIN,
            "text": LayerDepth.MAIN_FRONT,
            "shapes": LayerDepth.MAIN,
            "effects": LayerDepth.EFFECTS,
            "particles": LayerDepth.EFFECTS,
            "shaders": LayerDepth.EFFECTS_BACK,
            "filters": LayerDepth.EFFECTS_FRONT,
            "foreground": LayerDepth.FOREGROUND,
            "overlays": LayerDepth.OVERLAY,
            "ui": LayerDepth.UI,
        }
        
        self.layer_objects: Dict[str, List[LayerObject]] = {}
        self.sub_index_spacing = 10
        
    def add_object(self, mobject: any, layer_name: str, custom_z_offset: float = 0):
        """Add an object to a specific layer."""
        if layer_name not in self.layer_objects:
            self.layer_objects[layer_name] = []
        
        sub_index = len(self.layer_objects[layer_name])
        layer_obj = LayerObject(
            mobject=mobject,
            layer_name=layer_name,
            sub_index=sub_index,
            custom_z_offset=custom_z_offset
        )
        
        self.layer_objects[layer_name].append(layer_obj)
        self._apply_z_index(layer_obj)
        
    def _apply_z_index(self, layer_obj: LayerObject):
        """Apply the calculated z-index to a mobject."""
        z_index = self.calculate_z_index(
            layer_obj.layer_name,
            layer_obj.sub_index,
            layer_obj.custom_z_offset
        )
        
        if hasattr(layer_obj.mobject, 'set_z_index'):
            layer_obj.mobject.set_z_index(z_index)
    
    def calculate_z_index(self, layer_name: str, sub_index: int = 0, 
                         custom_offset: float = 0) -> float:
        """Calculate z-index based on layer hierarchy."""
        base_depth = self.layer_depths.get(layer_name.lower(), LayerDepth.MAIN)
        sub_depth = sub_index * self.sub_index_spacing
        return base_depth + sub_depth + custom_offset
    
    def reorder_layer(self, layer_name: str):
        """Reorder all objects in a layer based on their sub-indices."""
        if layer_name not in self.layer_objects:
            return
        
        for i, layer_obj in enumerate(self.layer_objects[layer_name]):
            layer_obj.sub_index = i
            self._apply_z_index(layer_obj)
    
    def move_to_front(self, mobject: any, layer_name: str):
        """Move an object to the front of its layer."""
        if layer_name not in self.layer_objects:
            return
        
        layer_objs = self.layer_objects[layer_name]
        for obj in layer_objs:
            if obj.mobject == mobject:
                layer_objs.remove(obj)
                layer_objs.append(obj)
                self.reorder_layer(layer_name)
                break
    
    def move_to_back(self, mobject: any, layer_name: str):
        """Move an object to the back of its layer."""
        if layer_name not in self.layer_objects:
            return
        
        layer_objs = self.layer_objects[layer_name]
        for obj in layer_objs:
            if obj.mobject == mobject:
                layer_objs.remove(obj)
                layer_objs.insert(0, obj)
                self.reorder_layer(layer_name)
                break
    
    def get_layer_z_range(self, layer_name: str) -> Tuple[float, float]:
        """Get the z-index range for a layer."""
        base_depth = self.layer_depths.get(layer_name.lower(), LayerDepth.MAIN)
        max_objects = 50
        return (base_depth, base_depth + max_objects * self.sub_index_spacing)
    
    def clear_layer(self, layer_name: str):
        """Clear all objects from a layer."""
        if layer_name in self.layer_objects:
            self.layer_objects[layer_name] = []
    
    def get_all_objects_sorted(self) -> List[any]:
        """Get all objects sorted by their z-index."""
        all_objects = []
        for layer_objs in self.layer_objects.values():
            all_objects.extend(layer_objs)
        
        all_objects.sort(key=lambda obj: self.calculate_z_index(
            obj.layer_name, obj.sub_index, obj.custom_z_offset
        ))
        
        return [obj.mobject for obj in all_objects]
    
    def set_layer_depth(self, layer_name: str, depth: int):
        """Set a custom depth for a layer."""
        self.layer_depths[layer_name.lower()] = depth
        
        if layer_name in self.layer_objects:
            for obj in self.layer_objects[layer_name]:
                self._apply_z_index(obj)
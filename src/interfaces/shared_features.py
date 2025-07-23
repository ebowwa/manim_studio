"""Shared Features Module for Manim Studio Interfaces

This module provides common functionality that can be reused across all interfaces:
- MCP (Model Context Protocol)
- GUI (Gradio/Streamlit/etc)
- API (REST/FastAPI)

Design principles:
1. Interface-agnostic core functionality
2. Consistent data models across interfaces
3. Centralized business logic
4. Easy testing and maintenance
"""

import json
import logging
import tempfile
import asyncio
import hashlib
import subprocess
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass, asdict, fields
from enum import Enum
import abc

# Core imports
from src.core.config import Config, SceneConfig, AnimationConfig, EffectConfig
from src.core.scene_builder import SceneBuilder
from src.core.asset_manager import AssetManager
from src.core.timeline.composer_timeline import ComposerTimeline, InterpolationType
from src.core.timeline.timeline_presets import TimelinePresets

logger = logging.getLogger(__name__)


def safe_asdict(obj):
    """Convert dataclass to dict, handling Enum values properly."""
    if hasattr(obj, '__dataclass_fields__'):
        result = {}
        for field in fields(obj):
            value = getattr(obj, field.name)
            if isinstance(value, Enum):
                result[field.name] = value.value
            elif isinstance(value, list):
                result[field.name] = [safe_asdict(item) if hasattr(item, '__dataclass_fields__') else item for item in value]
            elif hasattr(value, '__dataclass_fields__'):
                result[field.name] = safe_asdict(value)
            else:
                result[field.name] = value
        return result
    else:
        return obj


class AnimationType(Enum):
    """Standardized animation types across interfaces."""
    WRITE = "write"
    FADEIN = "fadein" 
    FADEOUT = "fadeout"
    CREATE = "create"
    UNCREATE = "uncreate"
    MOVE = "move"
    SCALE = "scale"
    ROTATE = "rotate"
    MORPH = "morph"
    TRANSFORM = "transform"


class ShapeType(Enum):
    """Standardized shape types across interfaces."""
    CIRCLE = "circle"
    SQUARE = "square"
    RECTANGLE = "rectangle"
    TRIANGLE = "triangle"
    POLYGON = "polygon"
    STAR = "star"
    ARROW = "arrow"
    # CAD shapes
    ROUNDED_SHAPE = "rounded_shape"
    CHAMFERED_SHAPE = "chamfered_shape"
    HATCHED_SHAPE = "hatched_shape"
    DASHED_SHAPE = "dashed_shape"


class RenderQuality(Enum):
    """Standardized render quality levels."""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    ULTRA = "4k"


@dataclass
class TextObject:
    """Standardized text object model."""
    id: str
    content: str
    color: str = "#FFFFFF"
    position: List[float] = None
    font_size: int = 48
    font: str = "Arial"
    
    def __post_init__(self):
        if self.position is None:
            self.position = [0, 0, 0]


@dataclass
class ShapeObject:
    """Standardized shape object model."""
    id: str
    shape_type: ShapeType
    color: str = "#FFFFFF"
    size: float = 1.0
    position: List[float] = None
    # CAD-specific properties
    corner_radius: Optional[float] = None
    chamfer_offset: Optional[float] = None
    hatch_angle: Optional[float] = None
    hatch_spacing: Optional[float] = None
    num_dashes: Optional[int] = None
    dashed_ratio: Optional[float] = None
    
    def __post_init__(self):
        if self.position is None:
            self.position = [0, 0, 0]


@dataclass
class CADDimensionObject:
    """Standardized CAD dimension object model."""
    id: str
    dimension_type: str  # "linear", "angular", "pointer"
    start: List[float]
    end: List[float]
    text: str = ""
    offset: float = 1.0
    color: str = "#FF6B6B"
    # Angular dimension specific
    center: Optional[List[float]] = None
    # Pointer specific  
    point: Optional[List[float]] = None
    offset_vector: Optional[List[float]] = None


@dataclass
class AnimationSequence:
    """Standardized animation model."""
    target: str
    animation_type: AnimationType
    start_time: float = 0.0
    duration: float = 1.0
    easing: str = "ease_in_out"
    properties: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = {}


@dataclass
class SceneDefinition:
    """Standardized scene model."""
    name: str
    duration: float = 5.0
    background_color: str = "#000000"
    resolution: List[int] = None
    fps: int = 60
    objects: List[Union[TextObject, ShapeObject, CADDimensionObject]] = None
    animations: List[AnimationSequence] = None
    timeline_preset: Optional[str] = None
    
    def __post_init__(self):
        if self.resolution is None:
            self.resolution = [1920, 1080]
        if self.objects is None:
            self.objects = []
        if self.animations is None:
            self.animations = []


class InterfaceResult:
    """Standardized result object for all interface operations."""
    
    def __init__(self, status: str, data: Any = None, message: str = "", error: str = ""):
        self.status = status  # "success", "error", "warning"
        self.data = data
        self.message = message
        self.error = error
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {"status": self.status}
        if self.data is not None:
            result["data"] = self.data
        if self.message:
            result["message"] = self.message
        if self.error:
            result["error"] = self.error
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict(), indent=2)


class SceneManager:
    """Core scene management functionality shared across interfaces."""
    
    def __init__(self):
        self.scenes: Dict[str, SceneDefinition] = {}
        self.current_scene: Optional[SceneDefinition] = None
        self.timeline: Optional[ComposerTimeline] = None
        self.timeline_presets = TimelinePresets()
        # Add initialization logging
        logger.info("SceneManager initialized with empty scenes dict")
    
    def create_scene(self, 
                    name: str,
                    duration: float = 5.0,
                    background_color: str = "#000000",
                    resolution: List[int] = None,
                    fps: int = 60) -> InterfaceResult:
        """Create a new scene with standardized parameters."""
        try:
            # Log incoming parameters for debugging
            logger.info(f"Creating scene with params: name={name}, duration={duration}, "
                       f"bg_color={background_color}, resolution={resolution}, fps={fps}")
            if resolution is None:
                resolution = [1920, 1080]
            
            scene = SceneDefinition(
                name=name,
                duration=duration,
                background_color=background_color,
                resolution=resolution,
                fps=fps
            )
            
            self.scenes[name] = scene
            self.current_scene = scene
            
            # Create associated timeline
            self.timeline = ComposerTimeline(duration=duration, fps=fps)
            
            return InterfaceResult(
                status="success",
                data=safe_asdict(scene),
                message=f"Scene '{name}' created successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to create scene: {e}")
            return InterfaceResult(
                status="error",
                error=str(e)
            )
    
    def add_text(self, 
                text_id: str,
                content: str,
                color: str = "#FFFFFF",
                position: List[float] = None,
                font_size: int = 48,
                font: str = "Arial") -> InterfaceResult:
        """Add text object to current scene."""
        if not self.current_scene:
            return InterfaceResult(status="error", error="No active scene")
        
        try:
            text_obj = TextObject(
                id=text_id,
                content=content,
                color=color,
                position=position or [0, 0, 0],
                font_size=font_size,
                font=font
            )
            
            self.current_scene.objects.append(text_obj)
            
            return InterfaceResult(
                status="success",
                data=safe_asdict(text_obj),
                message=f"Text object '{text_id}' added"
            )
            
        except Exception as e:
            logger.error(f"Failed to add text: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def add_shape(self,
                 shape_id: str,
                 shape_type: Union[str, ShapeType],
                 color: str = "#FFFFFF",
                 size: float = 1.0,
                 position: List[float] = None,
                 # CAD-specific parameters
                 corner_radius: Optional[float] = None,
                 chamfer_offset: Optional[float] = None,
                 hatch_angle: Optional[float] = None,
                 hatch_spacing: Optional[float] = None,
                 num_dashes: Optional[int] = None,
                 dashed_ratio: Optional[float] = None) -> InterfaceResult:
        """Add shape object to current scene."""
        if not self.current_scene:
            return InterfaceResult(status="error", error="No active scene")
        
        try:
            if isinstance(shape_type, str):
                shape_type = ShapeType(shape_type)
            
            shape_obj = ShapeObject(
                id=shape_id,
                shape_type=shape_type,
                color=color,
                size=size,
                position=position or [0, 0, 0],
                corner_radius=corner_radius,
                chamfer_offset=chamfer_offset,
                hatch_angle=hatch_angle,
                hatch_spacing=hatch_spacing,
                num_dashes=num_dashes,
                dashed_ratio=dashed_ratio
            )
            
            self.current_scene.objects.append(shape_obj)
            
            return InterfaceResult(
                status="success",
                data=safe_asdict(shape_obj),
                message=f"Shape object '{shape_id}' added"
            )
            
        except Exception as e:
            logger.error(f"Failed to add shape: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def add_cad_dimension(self,
                         dimension_id: str,
                         dimension_type: str,
                         start: List[float],
                         end: List[float],
                         text: str = "",
                         offset: float = 1.0,
                         color: str = "#FF6B6B",
                         center: Optional[List[float]] = None,
                         point: Optional[List[float]] = None,
                         offset_vector: Optional[List[float]] = None) -> InterfaceResult:
        """Add CAD dimension object to current scene."""
        if not self.current_scene:
            return InterfaceResult(status="error", error="No active scene")
        
        try:
            dimension_obj = CADDimensionObject(
                id=dimension_id,
                dimension_type=dimension_type,
                start=start,
                end=end,
                text=text,
                offset=offset,
                color=color,
                center=center,
                point=point,
                offset_vector=offset_vector
            )
            
            self.current_scene.objects.append(dimension_obj)
            
            return InterfaceResult(
                status="success",
                data=safe_asdict(dimension_obj),
                message=f"CAD dimension '{dimension_id}' added"
            )
            
        except Exception as e:
            logger.error(f"Failed to add CAD dimension: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def add_animation(self,
                     target: str,
                     animation_type: Union[str, AnimationType],
                     start_time: float = 0.0,
                     duration: float = 1.0,
                     easing: str = "ease_in_out",
                     properties: Dict[str, Any] = None) -> InterfaceResult:
        """Add animation to current scene."""
        if not self.current_scene:
            return InterfaceResult(status="error", error="No active scene")
        
        try:
            # Check if target exists
            target_exists = any(obj.id == target for obj in self.current_scene.objects)
            if not target_exists:
                return InterfaceResult(status="error", error=f"Target '{target}' not found")
            
            if isinstance(animation_type, str):
                animation_type = AnimationType(animation_type)
            
            animation = AnimationSequence(
                target=target,
                animation_type=animation_type,
                start_time=start_time,
                duration=duration,
                easing=easing,
                properties=properties or {}
            )
            
            self.current_scene.animations.append(animation)
            
            return InterfaceResult(
                status="success",
                data=safe_asdict(animation),
                message=f"Animation added to '{target}'"
            )
            
        except Exception as e:
            logger.error(f"Failed to add animation: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def list_scenes(self) -> InterfaceResult:
        """List all created scenes."""
        try:
            logger.info(f"Listing scenes. Current scenes: {list(self.scenes.keys())}")
            return InterfaceResult(
                status="success",
                data={
                    "scenes": list(self.scenes.keys()),
                    "current_scene": self.current_scene.name if self.current_scene else None,
                    "total": len(self.scenes)
                }
            )
        except Exception as e:
            logger.error(f"Error listing scenes: {e}", exc_info=True)
            return InterfaceResult(
                status="error",
                error=f"Failed to list scenes: {str(e)}"
            )
    
    def get_scene(self, scene_name: Optional[str] = None) -> InterfaceResult:
        """Get scene configuration."""
        try:
            if scene_name:
                if scene_name not in self.scenes:
                    return InterfaceResult(status="error", error=f"Scene '{scene_name}' not found")
                scene = self.scenes[scene_name]
            else:
                if not self.current_scene:
                    return InterfaceResult(status="error", error="No active scene")
                scene = self.current_scene
            
            return InterfaceResult(
                status="success",
                data=safe_asdict(scene)
            )
            
        except Exception as e:
            logger.error(f"Failed to get scene: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def export_scene(self, scene_name: Optional[str] = None) -> InterfaceResult:
        """Export scene as YAML configuration."""
        try:
            # Get the scene to export
            scene_result = self.get_scene(scene_name)
            if scene_result.status == "error":
                return scene_result
            
            scene_data = scene_result.data
            
            # Convert to YAML-compatible format
            yaml_config = {
                "scene": {
                    "name": scene_data["name"],
                    "duration": scene_data["duration"],
                    "background_color": scene_data["background_color"],
                    "resolution": f"{scene_data['resolution'][0]}x{scene_data['resolution'][1]}",
                    "fps": scene_data["fps"],
                    "objects": [],
                    "animations": []
                }
            }
            
            # Convert objects
            for obj in scene_data.get("objects", []):
                if "content" in obj:  # Text object
                    yaml_config["scene"]["objects"].append({
                        "type": "text",
                        "id": obj["id"],
                        "content": obj["content"],
                        "color": obj["color"],
                        "position": obj["position"],
                        "font_size": obj["font_size"],
                        "font": obj["font"]
                    })
                elif "shape_type" in obj:  # Shape object
                    yaml_config["scene"]["objects"].append({
                        "type": obj["shape_type"]["value"] if isinstance(obj["shape_type"], dict) else obj["shape_type"],
                        "id": obj["id"],
                        "color": obj["color"],
                        "size": obj["size"],
                        "position": obj["position"]
                    })
            
            # Convert animations
            for anim in scene_data.get("animations", []):
                yaml_config["scene"]["animations"].append({
                    "type": anim["animation_type"]["value"] if isinstance(anim["animation_type"], dict) else anim["animation_type"],
                    "target": anim["target"],
                    "start_time": anim["start_time"],
                    "duration": anim["duration"],
                    "easing": anim["easing"],
                    "properties": anim.get("properties", {})
                })
            
            return InterfaceResult(
                status="success",
                data=yaml_config,
                message=f"Scene '{scene_data['name']}' exported successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to export scene: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def import_scene(self, yaml_config: Dict[str, Any]) -> InterfaceResult:
        """Import scene from YAML configuration."""
        try:
            scene_config = yaml_config.get("scene", yaml_config)
            
            # Parse resolution
            resolution = scene_config.get("resolution", "1920x1080")
            if isinstance(resolution, str):
                width, height = map(int, resolution.split("x"))
                resolution = [width, height]
            
            # Create the scene
            create_result = self.create_scene(
                name=scene_config["name"],
                duration=scene_config.get("duration", 5.0),
                background_color=scene_config.get("background_color", "#000000"),
                resolution=resolution,
                fps=scene_config.get("fps", 60)
            )
            
            if create_result.status == "error":
                return create_result
            
            # Import objects
            for obj in scene_config.get("objects", []):
                if obj["type"] == "text":
                    self.current_scene.objects.append(TextObject(
                        id=obj["id"],
                        content=obj["content"],
                        color=obj.get("color", "#FFFFFF"),
                        position=obj.get("position", [0, 0, 0]),
                        font_size=obj.get("font_size", 48),
                        font=obj.get("font", "Arial")
                    ))
                else:  # Shape
                    self.current_scene.objects.append(ShapeObject(
                        id=obj["id"],
                        shape_type=ShapeType(obj["type"]),
                        color=obj.get("color", "#FFFFFF"),
                        size=obj.get("size", 1.0),
                        position=obj.get("position", [0, 0, 0])
                    ))
            
            # Import animations
            for anim in scene_config.get("animations", []):
                self.current_scene.animations.append(AnimationSequence(
                    target=anim["target"],
                    animation_type=AnimationType(anim["type"]),
                    start_time=anim.get("start_time", 0.0),
                    duration=anim.get("duration", 1.0),
                    easing=anim.get("easing", "ease_in_out"),
                    properties=anim.get("properties", {})
                ))
            
            return InterfaceResult(
                status="success",
                data=safe_asdict(self.current_scene),
                message=f"Scene '{scene_config['name']}' imported successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to import scene: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def clear_workspace(self) -> InterfaceResult:
        """Clear all scenes and reset to initial state."""
        try:
            self.scenes.clear()
            self.current_scene = None
            self.timeline = None
            
            return InterfaceResult(
                status="success",
                message="Workspace cleared successfully"
            )
            
        except Exception as e:
            logger.error(f"Failed to clear workspace: {e}")
            return InterfaceResult(status="error", error=str(e))


class PresetManager:
    """Timeline preset management functionality."""
    
    def __init__(self):
        self.timeline_presets = TimelinePresets()
    
    def list_presets(self, category: Optional[str] = None) -> InterfaceResult:
        """List available timeline presets."""
        try:
            presets_list = []
            
            for preset_name, preset in self.timeline_presets.presets.items():
                if category and preset.category.value != category:
                    continue
                
                presets_list.append({
                    "name": preset.name,
                    "category": preset.category.value,
                    "description": preset.description,
                    "duration": preset.duration,
                    "tags": preset.tags or []
                })
            
            return InterfaceResult(
                status="success",
                data={
                    "presets": presets_list,
                    "total": len(presets_list)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to list presets: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def get_preset_info(self, preset_name: str) -> InterfaceResult:
        """Get detailed preset information."""
        try:
            preset = self.timeline_presets.get_preset(preset_name)
            if not preset:
                return InterfaceResult(status="error", error=f"Preset '{preset_name}' not found")
            
            return InterfaceResult(
                status="success",
                data={
                    "name": preset.name,
                    "category": preset.category.value,
                    "description": preset.description,
                    "duration": preset.duration,
                    "parameters": preset.parameters,
                    "tags": preset.tags or []
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to get preset info: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def apply_preset(self, timeline: ComposerTimeline, preset_name: str, 
                    parameters: Dict[str, Any] = None) -> InterfaceResult:
        """Apply preset to timeline."""
        try:
            preset = self.timeline_presets.get_preset(preset_name)
            if not preset:
                return InterfaceResult(status="error", error=f"Preset '{preset_name}' not found")
            
            preset.apply(timeline, parameters or {})
            
            return InterfaceResult(
                status="success",
                data={
                    "preset_name": preset_name,
                    "duration": preset.duration,
                    "parameters": parameters or {}
                },
                message=f"Applied preset '{preset_name}'"
            )
            
        except Exception as e:
            logger.error(f"Failed to apply preset: {e}")
            return InterfaceResult(status="error", error=str(e))


class RenderEngine:
    """Rendering functionality shared across interfaces."""
    
    def __init__(self):
        self.quality_map = {
            RenderQuality.LOW: "l",
            RenderQuality.MEDIUM: "m",
            RenderQuality.HIGH: "h", 
            RenderQuality.ULTRA: "k"
        }
        # Configure script storage directory
        self.script_storage_dir = Path("/Users/ebowwa/apps/manim_studio/user-data/mcp-scripts")
        self.script_storage_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_manim_script(self, scene: SceneDefinition) -> str:
        """Generate Manim script from scene definition."""
        script = f'''from manim import *
import numpy as np

class Scene(Scene):
    def construct(self):
        # Set background
        self.camera.background_color = "{scene.background_color}"
        
        # Create objects
        objects = {{}}
'''
        
        # Add objects
        for obj in scene.objects:
            if isinstance(obj, TextObject):
                script += f'''        objects["{obj.id}"] = Text("{obj.content}", '''
                script += f'''color="{obj.color}", font_size={obj.font_size})\n'''
                script += f'''        objects["{obj.id}"].move_to([{obj.position[0]}, {obj.position[1]}, {obj.position[2]}])\n'''
            elif isinstance(obj, ShapeObject):
                shape_type = obj.shape_type.value
                if shape_type == "circle":
                    script += f'''        objects["{obj.id}"] = Circle(radius={obj.size}, color="{obj.color}")\n'''
                elif shape_type == "square":
                    script += f'''        objects["{obj.id}"] = Square(side_length={obj.size * 2}, color="{obj.color}")\n'''
                elif shape_type == "triangle":
                    script += f'''        objects["{obj.id}"] = Triangle(color="{obj.color}").scale({obj.size})\n'''
                elif shape_type == "star":
                    script += f'''        objects["{obj.id}"] = Star(color="{obj.color}").scale({obj.size})\n'''
                elif shape_type == "rounded_shape":
                    # Create base shape first, then apply rounding
                    base_shape = obj.corner_radius  # Assuming this contains base shape info
                    script += f'''        from src.components.cad_objects import RoundCorners\n'''
                    script += f'''        base = Square(side_length={obj.size * 2}, color="{obj.color}")\n'''
                    script += f'''        objects["{obj.id}"] = RoundCorners.apply(base, radius={obj.corner_radius or 0.2})\n'''
                elif shape_type == "chamfered_shape":
                    script += f'''        from src.components.cad_objects import ChamferCorners\n'''
                    script += f'''        base = Square(side_length={obj.size * 2}, color="{obj.color}")\n'''
                    script += f'''        objects["{obj.id}"] = ChamferCorners.apply(base, offset={obj.chamfer_offset or 0.2})\n'''
                elif shape_type == "hatched_shape":
                    script += f'''        from src.components.cad_objects import HatchPattern\n'''
                    script += f'''        base = Circle(radius={obj.size}, color="{obj.color}")\n'''
                    script += f'''        hatch = HatchPattern(base, angle={obj.hatch_angle or 0.785}, spacing={obj.hatch_spacing or 0.2})\n'''
                    script += f'''        objects["{obj.id}"] = VGroup(base, hatch)\n'''
                elif shape_type == "dashed_shape":
                    script += f'''        from src.components.cad_objects import DashedLine\n'''
                    script += f'''        base = Circle(radius={obj.size}, color="{obj.color}")\n'''
                    script += f'''        objects["{obj.id}"] = DashedLine(base, num_dashes={obj.num_dashes or 15}, dashed_ratio={obj.dashed_ratio or 0.5})\n'''
                
                script += f'''        objects["{obj.id}"].move_to([{obj.position[0]}, {obj.position[1]}, {obj.position[2]}])\n'''
            elif isinstance(obj, CADDimensionObject):
                # Handle CAD dimensions
                script += f'''        from src.components.cad_objects import LinearDimension, AngularDimension, PointerLabel\n'''
                if obj.dimension_type == "linear":
                    script += f'''        objects["{obj.id}"] = LinearDimension(\n'''
                    script += f'''            start=np.array([{obj.start[0]}, {obj.start[1]}, {obj.start[2]}]),\n'''
                    script += f'''            end=np.array([{obj.end[0]}, {obj.end[1]}, {obj.end[2]}]),\n'''
                    script += f'''            text="{obj.text}",\n'''
                    script += f'''            offset={obj.offset},\n'''
                    script += f'''            color="{obj.color}"\n'''
                    script += f'''        )\n'''
                elif obj.dimension_type == "angular":
                    script += f'''        objects["{obj.id}"] = AngularDimension(\n'''
                    script += f'''            start=np.array([{obj.start[0]}, {obj.start[1]}, {obj.start[2]}]),\n'''
                    script += f'''            end=np.array([{obj.end[0]}, {obj.end[1]}, {obj.end[2]}]),\n'''
                    script += f'''            arc_center=np.array([{obj.center[0]}, {obj.center[1]}, {obj.center[2]}]),\n'''
                    script += f'''            text="{obj.text}",\n'''
                    script += f'''            offset={obj.offset},\n'''
                    script += f'''            color="{obj.color}"\n'''
                    script += f'''        )\n'''
                elif obj.dimension_type == "pointer":
                    script += f'''        objects["{obj.id}"] = PointerLabel(\n'''
                    script += f'''            point=np.array([{obj.point[0]}, {obj.point[1]}, {obj.point[2]}]),\n'''
                    script += f'''            text="{obj.text}",\n'''
                    script += f'''            offset_vector=np.array([{obj.offset_vector[0]}, {obj.offset_vector[1]}, {obj.offset_vector[2]}]),\n'''
                    script += f'''            color="{obj.color}"\n'''
                    script += f'''        )\n'''
        
        script += '''        
        # Execute animations\n'''
        
        # Sort animations by start time
        animations = sorted(scene.animations, key=lambda a: a.start_time)
        
        current_time = 0
        for anim in animations:
            # Add wait if needed
            if anim.start_time > current_time:
                wait_time = anim.start_time - current_time
                script += f'''        self.wait({wait_time})\n'''
                current_time = anim.start_time
            
            # Generate animation code
            script += self._generate_animation_code(anim)
            current_time += anim.duration
        
        # Final wait
        if current_time < scene.duration:
            script += f'''        self.wait({scene.duration - current_time})\n'''
        
        return script
    
    def _generate_animation_code(self, anim: AnimationSequence) -> str:
        """Generate animation-specific Manim code."""
        target = anim.target
        anim_type = anim.animation_type.value
        duration = anim.duration
        
        # Map easing to rate_func
        easing_map = {
            "linear": "linear",
            "ease_in": "ease_in_quad",
            "ease_out": "ease_out_quad",
            "ease_in_out": "smooth",
            "bounce": "there_and_back",
            "elastic": "wiggle",
            "back": "ease_out_back",
            "expo": "ease_out_expo"
        }
        rate_func = easing_map.get(anim.easing, "linear")
        
        if anim_type == "create":
            return f'''        self.play(Create(objects["{target}"], rate_func={rate_func}), run_time={duration})\n'''
        elif anim_type == "write":
            return f'''        self.play(Write(objects["{target}"], rate_func={rate_func}), run_time={duration})\n'''
        elif anim_type == "fadein":
            return f'''        self.play(FadeIn(objects["{target}"], rate_func={rate_func}), run_time={duration})\n'''
        elif anim_type == "fadeout":
            return f'''        self.play(FadeOut(objects["{target}"], rate_func={rate_func}), run_time={duration})\n'''
        elif anim_type == "move" and "position" in anim.properties:
            pos = anim.properties["position"]
            return f'''        self.play(objects["{target}"].animate.move_to([{pos[0]}, {pos[1]}, {pos[2]}]), rate_func={rate_func}, run_time={duration})\n'''
        elif anim_type == "scale" and "scale" in anim.properties:
            scale = anim.properties["scale"]
            return f'''        self.play(objects["{target}"].animate.scale({scale}), rate_func={rate_func}, run_time={duration})\n'''
        elif anim_type == "rotate" and "angle" in anim.properties:
            angle = anim.properties["angle"]
            return f'''        self.play(objects["{target}"].animate.rotate({angle}), rate_func={rate_func}, run_time={duration})\n'''
        
        return f'''        # TODO: Animation {anim_type} for {target}\n'''
    
    def prepare_render(self, scene: SceneDefinition, 
                      output_path: str,
                      quality: Union[str, RenderQuality] = RenderQuality.HIGH,
                      save_script: bool = True) -> InterfaceResult:
        """Prepare scene for rendering with optional script preservation."""
        try:
            if isinstance(quality, str):
                quality = RenderQuality(quality)
            
            # Generate script
            script_content = self.generate_manim_script(scene)
            
            # Save to permanent location if requested
            permanent_path = None
            if save_script:
                # Calculate script hash
                script_hash = hashlib.md5(script_content.encode()).hexdigest()[:8]
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                scene_name = scene.name.replace(" ", "_")
                permanent_filename = f"{timestamp}_{scene_name}_{script_hash}.py"
                permanent_path = self.script_storage_dir / permanent_filename
                
                # Check if identical script already exists
                existing_scripts = list(self.script_storage_dir.glob(f"*_{scene_name}_*.py"))
                script_already_saved = False
                
                for existing_script in existing_scripts:
                    try:
                        existing_content = existing_script.read_text()
                        if existing_content == script_content:
                            script_already_saved = True
                            permanent_path = existing_script
                            break
                    except Exception:
                        continue
                
                # Save script if not already saved
                if not script_already_saved:
                    permanent_path.write_text(script_content)
                    
                    # Create metadata file
                    metadata = {
                        "scene_name": scene.name,
                        "timestamp": timestamp,
                        "quality": quality.value,
                        "output_path": output_path,
                        "scene_config": safe_asdict(scene),
                        "script_hash": script_hash
                    }
                    
                    metadata_path = permanent_path.with_suffix('.json')
                    metadata_path.write_text(json.dumps(metadata, indent=2))
            
            # Save to temporary file for immediate rendering
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
            temp_file.write(script_content)
            temp_file.close()
            
            # Generate render command
            quality_flag = self.quality_map[quality]
            render_command = f"manim {temp_file.name} Scene -{quality_flag} -o {output_path}"
            
            result_data = {
                "script_path": temp_file.name,
                "output_path": output_path,
                "render_command": render_command,
                "quality": quality.value,
                "scene_name": scene.name
            }
            
            if permanent_path:
                result_data["permanent_script_path"] = str(permanent_path)
                result_data["saved_as"] = permanent_path.name
            
            return InterfaceResult(
                status="success",
                data=result_data,
                message=f"Scene prepared for rendering{' and script saved' if permanent_path else ''}"
            )
            
        except Exception as e:
            logger.error(f"Failed to prepare render: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def execute_render(self, render_command: str, script_path: str = None) -> InterfaceResult:
        """Execute the render command and track progress."""
        try:
            # Ensure we have the media_dir flag
            if "--media_dir user-data" not in render_command:
                render_command = render_command.replace("manim ", "manim --media_dir user-data ")
            
            logger.info(f"Executing render: {render_command}")
            
            # Execute the command
            process = subprocess.Popen(
                render_command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=dict(os.environ, PYTHONPATH=str(Path(__file__).parent.parent.parent))
            )
            
            # Collect output
            stdout_lines = []
            stderr_lines = []
            
            # Read output in real-time
            while True:
                stdout_line = process.stdout.readline()
                stderr_line = process.stderr.readline()
                
                if stdout_line:
                    stdout_lines.append(stdout_line.strip())
                    logger.info(f"Manim: {stdout_line.strip()}")
                
                if stderr_line:
                    stderr_lines.append(stderr_line.strip())
                    if "error" not in stderr_line.lower():
                        logger.info(f"Manim: {stderr_line.strip()}")
                    else:
                        logger.error(f"Manim Error: {stderr_line.strip()}")
                
                # Check if process is done
                if process.poll() is not None:
                    break
            
            # Get remaining output
            remaining_stdout, remaining_stderr = process.communicate()
            if remaining_stdout:
                stdout_lines.extend(remaining_stdout.strip().split('\n'))
            if remaining_stderr:
                stderr_lines.extend(remaining_stderr.strip().split('\n'))
            
            # Check if render was successful
            if process.returncode == 0:
                # Find the output file path from the logs
                output_file = None
                for line in stdout_lines + stderr_lines:
                    if "File ready at" in line or "saved to" in line:
                        parts = line.split("'")
                        if len(parts) >= 2:
                            output_file = parts[1]
                            break
                
                return InterfaceResult(
                    status="success",
                    data={
                        "output_file": output_file,
                        "stdout": "\n".join(stdout_lines),
                        "stderr": "\n".join(stderr_lines),
                        "return_code": process.returncode
                    },
                    message=f"Render completed successfully{f' at {output_file}' if output_file else ''}"
                )
            else:
                return InterfaceResult(
                    status="error",
                    data={
                        "stdout": "\n".join(stdout_lines),
                        "stderr": "\n".join(stderr_lines),
                        "return_code": process.returncode
                    },
                    error=f"Render failed with code {process.returncode}"
                )
                
        except Exception as e:
            logger.error(f"Failed to execute render: {e}")
            return InterfaceResult(status="error", error=str(e))
    
    def render_scene(self, scene: SceneDefinition, output_path: str, 
                    quality: Union[str, RenderQuality] = RenderQuality.HIGH,
                    save_script: bool = True, preview: bool = False) -> InterfaceResult:
        """Complete render pipeline: prepare and execute."""
        try:
            # First prepare the render
            prepare_result = self.prepare_render(scene, output_path, quality, save_script)
            if prepare_result.status == "error":
                return prepare_result
            
            # Extract render command and script path
            render_data = prepare_result.data
            render_command = render_data["render_command"]
            script_path = render_data["script_path"]
            
            # Add preview flag if requested
            if preview:
                render_command += " -p"
            
            # Execute the render
            render_result = self.execute_render(render_command, script_path)
            
            # Clean up temp file if render succeeded
            if render_result.status == "success" and script_path:
                try:
                    os.unlink(script_path)
                except:
                    pass
            
            # Combine results
            if render_result.status == "success":
                final_data = {**render_data, **render_result.data}
                return InterfaceResult(
                    status="success",
                    data=final_data,
                    message=render_result.message
                )
            else:
                return render_result
                
        except Exception as e:
            logger.error(f"Failed to render scene: {e}")
            return InterfaceResult(status="error", error=str(e))


class ManimStudioCore:
    """Main shared features class that combines all functionality."""
    
    def __init__(self):
        self.scene_manager = SceneManager()
        self.preset_manager = PresetManager()
        self.render_engine = RenderEngine()
    
    # Delegate methods for easier access
    def create_scene(self, *args, **kwargs) -> InterfaceResult:
        return self.scene_manager.create_scene(*args, **kwargs)
    
    def add_text(self, *args, **kwargs) -> InterfaceResult:
        return self.scene_manager.add_text(*args, **kwargs)
    
    def add_shape(self, *args, **kwargs) -> InterfaceResult:
        return self.scene_manager.add_shape(*args, **kwargs)
    
    def add_cad_dimension(self, *args, **kwargs) -> InterfaceResult:
        return self.scene_manager.add_cad_dimension(*args, **kwargs)
    
    def add_animation(self, *args, **kwargs) -> InterfaceResult:
        return self.scene_manager.add_animation(*args, **kwargs)
    
    def list_scenes(self) -> InterfaceResult:
        return self.scene_manager.list_scenes()
    
    def get_scene(self, *args, **kwargs) -> InterfaceResult:
        return self.scene_manager.get_scene(*args, **kwargs)
    
    def export_scene(self, *args, **kwargs) -> InterfaceResult:
        return self.scene_manager.export_scene(*args, **kwargs)
    
    def import_scene(self, *args, **kwargs) -> InterfaceResult:
        return self.scene_manager.import_scene(*args, **kwargs)
    
    def clear_workspace(self) -> InterfaceResult:
        return self.scene_manager.clear_workspace()
    
    def list_presets(self, *args, **kwargs) -> InterfaceResult:
        return self.preset_manager.list_presets(*args, **kwargs)
    
    def get_preset_info(self, *args, **kwargs) -> InterfaceResult:
        return self.preset_manager.get_preset_info(*args, **kwargs)
    
    def apply_preset(self, preset_name: str, parameters: Dict[str, Any] = None) -> InterfaceResult:
        if not self.scene_manager.timeline:
            return InterfaceResult(status="error", error="No timeline available")
        return self.preset_manager.apply_preset(
            self.scene_manager.timeline, preset_name, parameters
        )
    
    def prepare_render(self, *args, **kwargs) -> InterfaceResult:
        if not self.scene_manager.current_scene:
            return InterfaceResult(status="error", error="No active scene")
        return self.render_engine.prepare_render(
            self.scene_manager.current_scene, *args, **kwargs
        )
    
    def execute_render(self, *args, **kwargs) -> InterfaceResult:
        return self.render_engine.execute_render(*args, **kwargs)
    
    def render_scene(self, *args, **kwargs) -> InterfaceResult:
        if not self.scene_manager.current_scene:
            return InterfaceResult(status="error", error="No active scene")
        return self.render_engine.render_scene(
            self.scene_manager.current_scene, *args, **kwargs
        )
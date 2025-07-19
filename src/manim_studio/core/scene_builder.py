"""Scene builder that creates scenes from configuration."""

from typing import Any, Dict, List, Optional, Type
from manim import *
from ..core.config import Config, SceneConfig, AnimationConfig, EffectConfig
from ..core.timeline import Timeline
from ..core.asset_manager import AssetManager
from ..components.effects import EffectRegistry
from ..scenes.base_scene import StudioScene


class SceneBuilder:
    """Builds Manim scenes from configuration."""
    
    def __init__(
        self,
        config: Optional[Config] = None,
        asset_manager: Optional[AssetManager] = None
    ):
        self.config = config
        self.asset_manager = asset_manager or AssetManager()
        self.effect_registry = EffectRegistry()
        self.object_cache: Dict[str, Mobject] = {}
    
    def build_scene(self, scene_config: SceneConfig) -> Type[Scene]:
        """Build a Scene class from configuration."""
        
        # Capture builder instance for use in scene
        builder = self
        
        # Create a new scene class dynamically
        class ConfiguredScene(StudioScene):
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self.scene_config = scene_config
                self.timeline = Timeline()
                self.objects = {}
                self.builder = builder
            
            def construct(self):
                # Set background
                self.camera.background_color = self.scene_config.background_color
                
                # Create objects
                for obj_name, obj_config in self.scene_config.objects.items():
                    obj = self.builder.create_object(obj_name, obj_config)
                    if obj:
                        self.objects[obj_name] = obj
                
                # Setup effects
                for effect_config in self.scene_config.effects:
                    effect = self.builder.create_effect(effect_config)
                    if effect:
                        self.timeline.add_event(
                            effect_config.start_time,
                            lambda s, e=effect: e.animate(s),
                            name=f"effect_{effect_config.type}"
                        )
                
                # Setup animations
                for anim_config in self.scene_config.animations:
                    animation = self.builder.create_animation(
                        anim_config,
                        self.objects
                    )
                    if animation:
                        self.timeline.add_animation(
                            anim_config.start_time,
                            animation,
                            name=f"anim_{anim_config.animation_type}"
                        )
                
                # Play timeline
                self.timeline.play(self)
        
        # Set scene metadata
        ConfiguredScene.__name__ = scene_config.name
        ConfiguredScene.__doc__ = scene_config.description
        
        return ConfiguredScene
    
    def create_object(self, name: str, config: Dict[str, Any]) -> Optional[Mobject]:
        """Create a Mobject from configuration."""
        obj_type = config.get('type', 'text')
        
        if obj_type == 'text':
            return self._create_text(config)
        elif obj_type == 'image':
            return self._create_image(config)
        elif obj_type == 'shape':
            return self._create_shape(config)
        elif obj_type == 'group':
            return self._create_group(config)
        else:
            print(f"Unknown object type: {obj_type}")
            return None
    
    def _create_text(self, config: Dict[str, Any]) -> Text:
        """Create a text object."""
        text = config.get('text', '')
        params = config.get('params', {})
        
        # Extract common parameters
        color = params.get('color', WHITE)
        scale = params.get('scale', 1.0)
        font = params.get('font')
        weight = params.get('weight', 'NORMAL')
        
        # Create text
        if params.get('gradient'):
            text_obj = Text(text, gradient=tuple(params['gradient']), weight=weight)
        else:
            # Only pass font if it's specified
            text_kwargs = {'color': color, 'weight': weight}
            if font:
                text_kwargs['font'] = font
            text_obj = Text(text, **text_kwargs)
        
        text_obj.scale(scale)
        
        # Position
        if 'position' in params:
            text_obj.move_to(params['position'])
        
        return text_obj
    
    def _create_image(self, config: Dict[str, Any]) -> Mobject:
        """Create an image object."""
        asset_name = config.get('asset')
        params = config.get('params', {})
        
        scale = params.get('scale', 1.0)
        
        try:
            image = self.asset_manager.load_image(asset_name, scale)
        except (ValueError, FileNotFoundError):
            # Create placeholder
            image = self.asset_manager.create_placeholder(asset_name)
        
        # Position
        if 'position' in params:
            image.move_to(params['position'])
        
        return image
    
    def _create_shape(self, config: Dict[str, Any]) -> Mobject:
        """Create a shape object."""
        shape_type = config.get('shape', 'circle')
        params = config.get('params', {})
        
        # Common parameters
        color = params.get('color', WHITE)
        fill_color = params.get('fill_color', None)
        fill_opacity = params.get('fill_opacity', 0)
        stroke_width = params.get('stroke_width', 2)
        
        # Create shape
        if shape_type == 'circle':
            radius = params.get('radius', 1.0)
            shape = Circle(radius=radius, color=color)
        elif shape_type == 'rectangle':
            width = params.get('width', 2.0)
            height = params.get('height', 1.0)
            shape = Rectangle(width=width, height=height, color=color)
        elif shape_type == 'polygon':
            vertices = params.get('vertices', 3)
            shape = RegularPolygon(n=vertices, color=color)
        else:
            # Default to circle
            shape = Circle(color=color)
        
        # Apply styling
        shape.set_stroke(color=color, width=stroke_width)
        if fill_color:
            shape.set_fill(fill_color, opacity=fill_opacity)
        
        # Position and scale
        if 'position' in params:
            shape.move_to(params['position'])
        if 'scale' in params:
            shape.scale(params['scale'])
        
        return shape
    
    def _create_group(self, config: Dict[str, Any]) -> VGroup:
        """Create a group of objects."""
        children = config.get('children', [])
        group = VGroup()
        
        for child_config in children:
            child_name = child_config.get('name', '')
            child = self.create_object(child_name, child_config)
            if child:
                group.add(child)
        
        # Apply group transformations
        params = config.get('params', {})
        if 'position' in params:
            group.move_to(params['position'])
        if 'scale' in params:
            group.scale(params['scale'])
        
        return group
    
    def create_effect(self, effect_config: EffectConfig) -> Optional[Any]:
        """Create an effect from configuration."""
        effect_class = self.effect_registry.get(effect_config.type)
        if not effect_class:
            print(f"Unknown effect type: {effect_config.type}")
            return None
        
        return effect_class(**effect_config.params)
    
    def create_animation(
        self,
        anim_config: AnimationConfig,
        objects: Dict[str, Mobject]
    ) -> Optional[Animation]:
        """Create an animation from configuration."""
        target_name = anim_config.target
        
        if target_name not in objects:
            print(f"Target object '{target_name}' not found")
            return None
        
        target = objects[target_name]
        anim_type = anim_config.animation_type
        params = anim_config.params
        duration = anim_config.duration
        
        # Create animation based on type
        if anim_type == 'fadein':
            # Handle shift parameter properly
            if 'shift' in params:
                shift_val = params.pop('shift')
                # Convert list to numpy array for shift
                import numpy as np
                shift_vector = np.array(shift_val) if isinstance(shift_val, list) else shift_val
                return FadeIn(target, shift=shift_vector, run_time=duration, **params)
            else:
                return FadeIn(target, run_time=duration, **params)
        elif anim_type == 'fadeout':
            return FadeOut(target, run_time=duration, **params)
        elif anim_type == 'write':
            return Write(target, run_time=duration, **params)
        elif anim_type == 'create':
            return Create(target, run_time=duration, **params)
        elif anim_type == 'transform':
            # Transform requires a target state
            if 'to' in params:
                to_config = params['to']
                to_object = self.create_object(f"{target_name}_transformed", to_config)
                return Transform(target, to_object, run_time=duration)
        elif anim_type == 'move':
            if 'to' in params:
                return target.animate.move_to(params['to']).set_run_time(duration)
        elif anim_type == 'scale':
            if 'factor' in params:
                return target.animate.scale(params['factor']).set_run_time(duration)
        elif anim_type == 'rotate':
            angle = params.get('angle', PI)
            return Rotate(target, angle, run_time=duration, **params)
        else:
            print(f"Unknown animation type: {anim_type}")
            return None
    
    @classmethod
    def from_config_file(cls, config_path: str) -> 'SceneBuilder':
        """Create SceneBuilder from configuration file."""
        config = Config(config_path)
        asset_manager = AssetManager.from_config(config.get('assets', {}))
        
        return cls(config, asset_manager)
"""Scene builder that creates scenes from configuration."""

from typing import Any, Dict, List, Optional, Type, Union
from manim import *
from .config import Config, SceneConfig, AnimationConfig, EffectConfig, Camera2DConfig, Camera3DConfig
from .timeline import Timeline
from .asset_manager import AssetManager
from .layer_manager import LayerManager
from .render_hooks import RenderHooks, RenderHookConfig, FrameExtractionMixin
from .camera_controller import Camera2DController, Camera3DController
from src.components.effects import EffectRegistry
# Avoid circular import - StudioScene will be imported when needed


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
        self.layer_manager = LayerManager()
    
    def build_scene(self, scene_config: SceneConfig) -> Type[Scene]:
        """Build a Scene class from configuration."""
        
        # Capture builder instance for use in scene
        builder = self
        
        # Determine base class based on camera type and frame extraction config
        is_3d = scene_config.camera_type == '3d' and isinstance(scene_config.camera, Camera3DConfig)
        if is_3d:
            from src.scenes.base_scene_3d import StudioScene3D
            base_scene_class = StudioScene3D
        else:
            from src.scenes.base_scene import StudioScene
            base_scene_class = StudioScene
        
        # Add frame extraction if needed
        if scene_config.frame_extraction and scene_config.frame_extraction.get('enabled', False):
            # Create a class with frame extraction capabilities
            if is_3d:
                from src.scenes.base_scene_3d import StudioScene3D
                class ExtractableStudioScene3D(FrameExtractionMixin, StudioScene3D):
                    pass
                base_class = ExtractableStudioScene3D
            else:
                from src.scenes.base_scene import StudioScene
                class ExtractableStudioScene(FrameExtractionMixin, StudioScene):
                    pass
                base_class = ExtractableStudioScene
        else:
            base_class = base_scene_class
        
        # Create a new scene class dynamically
        class ConfiguredScene(base_class):
            def __init__(self, **kwargs):
                # Pass camera config to 3D scenes
                if is_3d and scene_config.camera:
                    kwargs['camera_config'] = scene_config.camera
                
                super().__init__(**kwargs)
                self.scene_config = scene_config
                self.timeline = Timeline()
                self.objects = {}
                self.builder = builder
                self.layer_manager = builder.layer_manager
                
                # Initialize camera controller for 2D scenes
                if not is_3d and scene_config.camera:
                    self.camera_controller = Camera2DController(self, scene_config.camera)
                
                # Configure frame extraction if enabled
                if hasattr(self, 'enable_frame_extraction') and scene_config.frame_extraction:
                    extraction_config = scene_config.frame_extraction
                    self.enable_frame_extraction(
                        frame_interval=extraction_config.get('frame_interval', 30),
                        analyze=extraction_config.get('analyze', True),
                        output_dir=extraction_config.get('output_dir'),
                        keyframe_extraction=extraction_config.get('keyframe_extraction', False),
                        keyframe_threshold=extraction_config.get('keyframe_threshold', 30.0),
                        max_frames=extraction_config.get('max_frames'),
                        generate_report=extraction_config.get('generate_report', True)
                    )
            
            def construct(self):
                print(f"[DEBUG] construct() called for scene: {self.scene_config.name}")
                print(f"[DEBUG] Number of objects: {len(self.scene_config.objects) if hasattr(self.scene_config, 'objects') else 'No objects'}")
                
                # Set background
                self.camera.background_color = self.scene_config.background_color
                
                # Configure camera if specified
                if self.scene_config.camera:
                    self.builder.configure_camera(self.camera, self.scene_config.camera, self.scene_config)
                
                # Create objects and add to scene
                if isinstance(self.scene_config.objects, dict):
                    # Dict format (older style)
                    for obj_name, obj_config in self.scene_config.objects.items():
                        obj = self.builder.create_object(obj_name, obj_config)
                        if obj:
                            self.objects[obj_name] = obj
                            self.add(obj)  # Add object to scene!
                else:
                    # List format (newer style)
                    print(f"Creating {len(self.scene_config.objects)} objects...")
                    for obj_config in self.scene_config.objects:
                        obj_name = obj_config.get('name', f'object_{len(self.objects)}')
                        print(f"Creating object: {obj_name}")
                        obj = self.builder.create_object(obj_name, obj_config)
                        if obj:
                            self.objects[obj_name] = obj
                            self.add(obj)  # Add object to scene!
                            print(f"Added {obj_name} to scene")
                        else:
                            print(f"Failed to create {obj_name}")
                
                # Setup effects
                for effect_config in self.scene_config.effects:
                    effect = self.builder.create_effect(effect_config)
                    if effect:
                        self.timeline.add_event(
                            effect_config.start_time,
                            lambda s, e=effect: e.animate(s),
                            name=f"effect_{effect_config.type}"
                        )
                
                # Group animations by start time
                from collections import defaultdict
                animations_by_time = defaultdict(list)
                
                for anim_config in self.scene_config.animations:
                    animation = self.builder.create_animation(anim_config, self.objects)
                    if animation:
                        animations_by_time[anim_config.start_time].append((animation, anim_config.duration))
                
                # Play animations in chronological order
                current_time = 0.0
                for start_time in sorted(animations_by_time.keys()):
                    # Wait until the next animation group
                    if start_time > current_time:
                        self.wait(start_time - current_time)
                        current_time = start_time
                    
                    # Play all animations that start at this time
                    anim_data = animations_by_time[start_time]
                    anims = [a[0] for a in anim_data]
                    
                    if len(anims) == 1:
                        self.play(anims[0])
                    else:
                        self.play(*anims)  # Play multiple animations simultaneously
                    
                    # Update current time (use max duration for overlapping animations)
                    if anim_data:
                        max_duration = max(a[1] for a in anim_data)
                        current_time = start_time + max_duration
                
                # Wait for remaining scene duration
                if current_time < self.scene_config.duration:
                    self.wait(self.scene_config.duration - current_time)
        
        # Set scene metadata
        ConfiguredScene.__name__ = scene_config.name
        ConfiguredScene.__doc__ = scene_config.description
        
        return ConfiguredScene
    
    def configure_camera(self, camera, camera_config, scene_config=None):
        """Configure camera from CameraConfig (2D or 3D)."""
        if isinstance(camera_config, Camera3DConfig):
            # 3D camera configuration
            # Note: Most 3D camera setup happens in StudioScene3D.__init__
            # This is for any additional runtime configuration
            if hasattr(camera, 'set_focal_distance') and camera_config.dof_enabled:
                camera.set_focal_distance(camera_config.focal_distance)
            
            # Background color is still set here
            if scene_config:
                camera.background_color = scene_config.background_color
            
        else:  # Camera2DConfig
            # 2D camera configuration
            # Set camera position (limited in 2D)
            if hasattr(camera, 'set_position'):
                camera.set_position(camera_config.position)
            
            # Set camera rotation (limited in 2D)
            if hasattr(camera, 'set_euler_angles'):
                camera.set_euler_angles(
                    phi=camera_config.rotation[0],
                    theta=camera_config.rotation[1],
                    gamma=camera_config.rotation[2]
                )
            
            # Set zoom
            if hasattr(camera, 'set_zoom'):
                camera.set_zoom(camera_config.zoom)
            
            # Set field of view (mostly cosmetic in 2D)
            if hasattr(camera, 'set_field_of_view'):
                camera.set_field_of_view(camera_config.fov)
            
            # Background color
            camera.background_color = self.scene_config.background_color
    
    def create_object(self, name: str, config: Dict[str, Any]) -> Optional[Mobject]:
        """Create a Mobject from configuration."""
        print(f"[DEBUG] create_object called with name={name}, config={config}")
        obj_type = config.get('type', 'text')
        layer = config.get('layer', 'main')
        z_offset = config.get('z_offset', 0)
        
        mobject = None
        if obj_type == 'text':
            mobject = self._create_text(config)
        elif obj_type == 'image':
            mobject = self._create_image(config)
        elif obj_type == 'shape':
            mobject = self._create_shape(config)
        elif obj_type == 'group':
            mobject = self._create_group(config)
        elif obj_type == '3d_model':
            mobject = self._create_3d_model(config)
        elif obj_type.startswith('physics.'):
            mobject = self._create_physics_object(config)
        elif obj_type == 'visual_array':
            mobject = self._create_visual_array(config)
        elif obj_type in ['rounded_shape', 'chamfered_shape', 'hatched_shape', 'dashed_shape']:
            # CAD objects
            mobject = self._create_cad_object(config)
        else:
            print(f"Unknown object type: {obj_type}")
            return None
        
        # Register with layer manager
        if mobject:
            self.layer_manager.add_object(mobject, layer, z_offset)
        
        return mobject
    
    def _create_text(self, config: Dict[str, Any]) -> Text:
        """Create a text object."""
        params = config.get('params', {})
        text = params.get('text', config.get('text', ''))
        
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
        
        # Apply scale or font_size
        if 'font_size' in params:
            text_obj.scale(params['font_size'] / 48)  # 48 is default font size
        else:
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
    
    def _create_3d_model(self, config: Dict[str, Any]) -> Mobject:
        """Create a 3D model object."""
        asset_name = config.get('asset')
        params = config.get('params', {})
        
        if not asset_name:
            print("Warning: No asset specified for 3D model")
            return self.asset_manager._create_3d_placeholder("No asset specified")
        
        # Extract 3D model parameters
        scale = params.get('scale', 1.0)
        center = params.get('center', True)
        max_points = params.get('max_points', 1000)
        
        try:
            model = self.asset_manager.load_3d_model(
                asset_name, 
                scale=scale, 
                center=center,
                max_points=max_points
            )
        except (ValueError, FileNotFoundError, ImportError) as e:
            # Create placeholder for failed loading
            print(f"Warning: Failed to load 3D model '{asset_name}': {e}")
            model = self.asset_manager._create_3d_placeholder(f"Failed: {asset_name}")
        
        # Apply transformations
        if 'position' in params:
            model.move_to(params['position'])
        
        if 'rotation' in params:
            rotation = params['rotation']
            if isinstance(rotation, (list, tuple)) and len(rotation) == 3:
                # Apply XYZ rotations
                import numpy as np
                if rotation[0] != 0:  # X rotation
                    model.rotate(rotation[0], axis=np.array([1, 0, 0]))
                if rotation[1] != 0:  # Y rotation
                    model.rotate(rotation[1], axis=np.array([0, 1, 0]))
                if rotation[2] != 0:  # Z rotation
                    model.rotate(rotation[2], axis=np.array([0, 0, 1]))
        
        # Apply material properties if specified
        material = params.get('material', {})
        if material:
            self._apply_3d_material(model, material)
        
        return model
    
    def _create_physics_object(self, config: Dict[str, Any]) -> Optional[Mobject]:
        """Create a physics object."""
        try:
            from src.components.physics_objects import create_physics_object, create_physics_updater
        except ImportError:
            print("Warning: Physics objects not available")
            return None
            
        obj_type = config.get('type', '').replace('physics.', '')
        params = config.get('params', {})
        
        try:
            mobject = create_physics_object(obj_type, params)
            
            # Add physics updater if auto_update is True
            if params.get('auto_update', True):
                mobject.add_updater(create_physics_updater(mobject))
                
            # Apply position if specified
            if 'position' in params:
                mobject.move_to(params['position'])
                
            return mobject
        except ValueError as e:
            print(f"Warning: {e}")
            return None
    
    def _create_cad_object(self, config: Dict[str, Any]) -> Optional[Mobject]:
        """Create a CAD object."""
        try:
            from src.components.cad_objects import create_cad_object
            
            obj_type = config.get('type')
            params = config.get('params', {})
            
            # Convert shape-specific parameters
            if 'shape' in params:
                # For rounded_shape and chamfered_shape
                shape_params = params.copy()
                shape_params['shape_type'] = params.get('shape', 'square')
                return create_cad_object(obj_type, **shape_params)
            else:
                # For other CAD objects
                return create_cad_object(obj_type, **params)
                
        except Exception as e:
            print(f"Error creating CAD object: {e}")
            return None
    
    def _create_visual_array(self, config: Dict[str, Any]) -> Optional[Mobject]:
        """Create a visual array object."""
        try:
            from src.components.visual_array import VisualArray, ArrayBuilder
        except ImportError:
            print("Warning: Visual array components not available")
            return None
        
        params = config.get('params', {})
        
        # Extract array values
        values = params.get('values', [])
        if not values:
            print("Warning: Visual array requires 'values' parameter")
            return None
        
        # Use builder pattern if complex configuration
        if any(key in params for key in ['labels', 'formatter', 'hex_indices', 'binary_format']):
            builder = ArrayBuilder().with_values(values)
            
            # Add labels if provided
            if 'labels' in params:
                builder.with_labels(params['labels'])
            
            # Configure display format
            if params.get('hex_indices'):
                builder.with_hex_indices(params.get('index_offset', 0))
            elif params.get('binary_format'):
                builder.with_binary_format()
            elif 'formatter' in params:
                builder.formatter = params['formatter']
            
            # Configure indices display
            if 'show_indices' in params:
                builder.with_indices(params['show_indices'])
            
            # Configure growth direction
            if 'growth_direction' in params:
                direction_map = {
                    'right': RIGHT,
                    'left': LEFT,
                    'up': UP,
                    'down': DOWN
                }
                direction = direction_map.get(params['growth_direction'].lower(), RIGHT)
                builder.with_growth_direction(direction)
            
            # Configure spacing
            if 'element_spacing' in params:
                builder.with_spacing(params['element_spacing'])
            
            # Add style parameters
            style_params = {}
            if 'value_args' in params:
                style_params['value_args'] = params['value_args']
            if 'index_args' in params:
                style_params['index_args'] = params['index_args']
            if 'body_args' in params:
                style_params['body_args'] = params['body_args']
            if 'label_args' in params:
                style_params['label_args'] = params['label_args']
            
            if style_params:
                builder.with_style(**style_params)
            
            array = builder.build()
        else:
            # Simple array creation
            array = VisualArray(
                values=values,
                show_indices=params.get('show_indices', True),
                growth_direction=RIGHT if params.get('growth_direction', 'right').lower() == 'right' else LEFT,
                element_spacing=params.get('element_spacing', 0.1)
            )
        
        # Apply position
        if 'position' in params:
            array.move_to(params['position'])
        
        # Apply scale
        if 'scale' in params:
            array.scale(params['scale'])
        
        return array
    
    def _apply_3d_material(self, model: Mobject, material: Dict[str, Any]) -> None:
        """Apply material properties to a 3D model."""
        # Basic material properties
        if 'color' in material:
            model.set_color(material['color'])
        
        if 'opacity' in material:
            model.set_fill(opacity=material['opacity'])
        
        # Advanced material properties (for future implementation)
        # These would be used when full PBR material support is added
        metallic = material.get('metallic', 0.0)
        roughness = material.get('roughness', 0.5)
        emission = material.get('emission')
        
        # For now, just store these as metadata on the object
        if hasattr(model, 'material_data'):
            model.material_data = material
        else:
            # Add material data as an attribute
            setattr(model, 'material_data', material)
    
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
        if anim_type == 'fadein' or anim_type == 'fade_in':
            # Handle shift parameter properly
            if 'shift' in params:
                shift_val = params.pop('shift')
                # Convert list to numpy array for shift
                import numpy as np
                shift_vector = np.array(shift_val) if isinstance(shift_val, list) else shift_val
                return FadeIn(target, shift=shift_vector, run_time=duration, **params)
            else:
                return FadeIn(target, run_time=duration, **params)
        elif anim_type == 'fadeout' or anim_type == 'fade_out':
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
            angle = params.pop('angle', PI)
            # Convert degrees to radians if angle is large (likely degrees)
            if angle > 6.3:  # Larger than 2*PI, probably degrees
                angle = angle * PI / 180
            return Rotate(target, angle, run_time=duration, **params)
        elif anim_type == 'indicate':
            scale_factor = params.pop('scale_factor', 1.2)
            color = params.pop('color', None)
            return Indicate(target, scale_factor=scale_factor, color=color, run_time=duration, **params)
        elif anim_type == 'camera_move':
            # Camera animation - requires scene reference
            if 'position' in params:
                # This is a placeholder - actual camera animation would need scene context
                print(f"Camera move animation to {params['position']} - implement in timeline")
                return None
        elif anim_type == 'camera_zoom':
            # Camera zoom animation
            if 'zoom' in params:
                print(f"Camera zoom animation to {params['zoom']} - implement in timeline")
                return None
        else:
            print(f"Unknown animation type: {anim_type}")
            return None
    
    @classmethod
    def from_config_file(cls, config_path: str) -> 'SceneBuilder':
        """Create SceneBuilder from configuration file."""
        config = Config(config_path)
        asset_manager = AssetManager.from_config(config.get('assets', {}))
        
        return cls(config, asset_manager)
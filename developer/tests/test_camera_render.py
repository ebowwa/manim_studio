#!/usr/bin/env python3
"""
Simple test script to render camera configuration scenes
"""

# Configure Manim to use user-data directory
from src.config.manim_config import config

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from manim import *
from src.core.config import Config, SceneConfig
from src.core.scene_builder import SceneBuilder
import json
import yaml

def render_config_scene(config_path: str):
    """Render a scene from configuration file."""
    
    print(f"Loading configuration from: {config_path}")
    
    # Load the config file
    config_data = {}
    if config_path.endswith('.yaml') or config_path.endswith('.yml'):
        with open(config_path, 'r') as f:
            config_data = yaml.safe_load(f)
    elif config_path.endswith('.json'):
        with open(config_path, 'r') as f:
            config_data = json.load(f)
    else:
        raise ValueError("Unsupported config format")
    
    print(f"Creating scene: {config_data.get('name', 'Unknown')}")
    
    # Create scene config
    scene_config = SceneConfig.from_dict(config_data)
    
    # Create scene builder (simplified without some complex dependencies)
    class SimpleSceneBuilder:
        def __init__(self):
            self.object_cache = {}
        
        def build_scene(self, scene_config):
            # Create a simple scene class
            class ConfiguredScene(Scene):
                def __init__(self, **kwargs):
                    super().__init__(**kwargs)
                    self.scene_config = scene_config
                
                def construct(self):
                    print("Constructing scene...")
                    
                    # Set background
                    self.camera.background_color = self.scene_config.background_color
                    
                    # Configure camera if specified
                    if self.scene_config.camera:
                        print(f"Camera config: {self.scene_config.camera}")
                        # Note: Basic Manim camera doesn't support all these features
                        # but we can at least acknowledge them
                    
                    # Create simple objects
                    scene_objects = {}
                    
                    for obj_name, obj_config in self.scene_config.objects.items():
                        print(f"Creating object: {obj_name}")
                        obj = self.create_simple_object(obj_config)
                        if obj:
                            scene_objects[obj_name] = obj
                            self.add(obj)
                    
                    # Simple animations
                    for anim_config in self.scene_config.animations:
                        if anim_config.target in scene_objects:
                            target = scene_objects[anim_config.target]
                            self.wait(anim_config.start_time)
                            
                            if anim_config.animation_type == 'write':
                                self.play(Write(target), run_time=anim_config.duration)
                            elif anim_config.animation_type == 'fadein':
                                self.play(FadeIn(target), run_time=anim_config.duration)
                            elif anim_config.animation_type == 'fadeout':
                                self.play(FadeOut(target), run_time=anim_config.duration)
                            elif anim_config.animation_type == 'create':
                                self.play(Create(target), run_time=anim_config.duration)
                
                def create_simple_object(self, config):
                    """Create a simple object from config."""
                    obj_type = config.get('type', 'text')
                    
                    if obj_type == 'text':
                        text = config.get('text', '')
                        params = config.get('params', {})
                        
                        # Create text with basic parameters
                        if 'gradient' in params:
                            text_obj = Text(text)
                            # Simple gradient approximation
                            text_obj.set_color_by_gradient(*params['gradient'])
                        else:
                            color = params.get('color', WHITE)
                            text_obj = Text(text, color=color)
                        
                        # Scale and position
                        scale = params.get('scale', 1.0)
                        text_obj.scale(scale)
                        
                        if 'position' in params:
                            text_obj.move_to(params['position'])
                        
                        return text_obj
                    
                    elif obj_type == 'shape':
                        shape_type = config.get('shape', 'circle')
                        params = config.get('params', {})
                        
                        if shape_type == 'circle':
                            radius = params.get('radius', 1.0)
                            shape_obj = Circle(radius=radius)
                        elif shape_type == 'rectangle':
                            width = params.get('width', 2.0)
                            height = params.get('height', 1.0)
                            shape_obj = Rectangle(width=width, height=height)
                        else:
                            shape_obj = Circle()  # Default
                        
                        # Styling
                        color = params.get('color', WHITE)
                        fill_color = params.get('fill_color')
                        fill_opacity = params.get('fill_opacity', 0)
                        
                        shape_obj.set_stroke(color=color)
                        if fill_color:
                            shape_obj.set_fill(fill_color, opacity=fill_opacity)
                        
                        # Position and scale
                        if 'position' in params:
                            shape_obj.move_to(params['position'])
                        if 'scale' in params:
                            shape_obj.scale(params['scale'])
                        
                        return shape_obj
                    
                    return None
            
            return ConfiguredScene
    
    # Build and render the scene
    builder = SimpleSceneBuilder()
    SceneClass = builder.build_scene(scene_config)
    
    # Set scene name
    SceneClass.__name__ = scene_config.name.replace(' ', '')
    
    return SceneClass

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_camera_render.py <config_file>")
        sys.exit(1)
    
    config_file = sys.argv[1]
    
    try:
        SceneClass = render_config_scene(config_file)
        print(f"Scene class created: {SceneClass.__name__}")
        print("Use this with Manim CLI:")
        print(f"manim test_camera_render.py {SceneClass.__name__} -pqh")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
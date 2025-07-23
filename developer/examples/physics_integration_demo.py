"""
Proof of concept for integrating physics simulations into Manim Studio.

This demonstrates how we could wrap manim-physics objects to work with 
the Manim Studio YAML configuration system.
"""

from src.config.manim_config import config
from manim import *
import numpy as np
from typing import Dict, Any, List

# Import manim-physics components
try:
    from manim_physics import Pendulum, MultiPendulum, RadialWave, LinearWave
    PHYSICS_AVAILABLE = True
except ImportError:
    PHYSICS_AVAILABLE = False
    print("manim-physics not installed. Run: pip install manim-physics")


class PhysicsObjectFactory:
    """Factory for creating physics-enabled objects from YAML config."""
    
    @staticmethod
    def create_pendulum(properties: Dict[str, Any]) -> VGroup:
        """Create a pendulum from configuration."""
        if not PHYSICS_AVAILABLE:
            # Fallback to simple visual representation
            pivot = Dot(properties.get('pivot_point', UP * 2))
            bob_pos = properties.get('bob_position', DOWN + RIGHT)
            bob = Dot(bob_pos, radius=0.2, color=ORANGE)
            rod = Line(pivot.get_center(), bob.get_center())
            return VGroup(pivot, rod, bob)
        
        # Create actual physics pendulum
        return Pendulum(
            bob_position=properties.get('bob_position', DOWN + RIGHT),
            pivot_point=properties.get('pivot_point', UP * 2),
            length=properties.get('length', 3),
            gravity=properties.get('gravity', 9.8),
            damping=properties.get('damping', 0.1)
        )
    
    @staticmethod
    def create_wave(properties: Dict[str, Any]) -> Surface:
        """Create a wave surface from configuration."""
        if not PHYSICS_AVAILABLE:
            # Fallback to static surface
            return Surface(
                lambda u, v: np.array([u, v, 0.1 * np.sin(2 * PI * u)]),
                u_range=properties.get('x_range', [-5, 5]),
                v_range=properties.get('y_range', [-5, 5])
            )
        
        wave_type = properties.get('wave_type', 'radial')
        
        if wave_type == 'radial':
            sources = properties.get('sources', [[0, 0, 0]])
            return RadialWave(
                *[np.array(s) for s in sources],
                wavelength=properties.get('wavelength', 1),
                period=properties.get('period', 1),
                amplitude=properties.get('amplitude', 0.1),
                x_range=properties.get('x_range', [-5, 5]),
                y_range=properties.get('y_range', [-5, 5])
            )
        elif wave_type == 'linear':
            return LinearWave(
                wavelength=properties.get('wavelength', 1),
                period=properties.get('period', 1),
                amplitude=properties.get('amplitude', 0.1),
                x_range=properties.get('x_range', [-5, 5])
            )
        else:
            raise ValueError(f"Unknown wave type: {wave_type}")


class PhysicsStudioScene(Scene):
    """Example scene demonstrating physics integration."""
    
    def __init__(self, physics_config: Dict[str, Any] = None):
        super().__init__()
        self.physics_config = physics_config or {}
        self.physics_objects = {}
        
    def create_physics_object(self, obj_config: Dict[str, Any]) -> Mobject:
        """Create a physics object from configuration."""
        obj_type = obj_config.get('type', '').replace('physics.', '')
        properties = obj_config.get('properties', {})
        
        if obj_type == 'pendulum':
            return PhysicsObjectFactory.create_pendulum(properties)
        elif obj_type in ['radial_wave', 'linear_wave']:
            properties['wave_type'] = obj_type.replace('_wave', '')
            return PhysicsObjectFactory.create_wave(properties)
        else:
            raise ValueError(f"Unknown physics object type: {obj_type}")
    
    def construct(self):
        """Construct the scene with physics objects."""
        # Example configuration that would come from YAML
        scene_config = {
            'objects': [
                {
                    'name': 'pendulum1',
                    'type': 'physics.pendulum',
                    'properties': {
                        'pivot_point': [0, 3, 0],
                        'bob_position': [2, 0, 0],
                        'length': 3,
                        'gravity': 9.8,
                        'damping': 0.05
                    }
                },
                {
                    'name': 'wave_field',
                    'type': 'physics.radial_wave',
                    'properties': {
                        'sources': [[0, 0, 0], [2, 2, 0]],
                        'wavelength': 1.5,
                        'period': 2,
                        'amplitude': 0.2,
                        'x_range': [-4, 4],
                        'y_range': [-4, 4]
                    }
                }
            ],
            'animations': [
                {
                    'type': 'physics_simulation',
                    'target': 'pendulum1',
                    'duration': 5
                },
                {
                    'type': 'wave_animation',
                    'target': 'wave_field',
                    'duration': 5
                }
            ]
        }
        
        # Create physics objects
        for obj_config in scene_config['objects']:
            name = obj_config['name']
            mob = self.create_physics_object(obj_config)
            self.physics_objects[name] = mob
            
        # Demo 1: Pendulum
        if 'pendulum1' in self.physics_objects:
            pendulum = self.physics_objects['pendulum1']
            self.add(pendulum)
            self.wait(5)
            self.remove(pendulum)
        
        # Demo 2: Wave field (if 3D)
        if 'wave_field' in self.physics_objects and hasattr(self, 'set_camera_orientation'):
            wave = self.physics_objects['wave_field']
            self.set_camera_orientation(phi=75 * DEGREES, theta=30 * DEGREES)
            self.add(wave)
            self.wait(5)


class PhysicsYAMLExample(Scene):
    """Example showing how physics would work with YAML configuration."""
    
    def construct(self):
        # Display example YAML configuration
        yaml_text = '''# physics_demo.yaml
scene:
  name: PhysicsDemo
  type: physics_scene
  duration: 20
  
physics_config:
  engine: pymunk
  gravity: [0, -9.8, 0]
  time_scale: 1.0
  
objects:
  - name: double_pendulum
    type: physics.multi_pendulum
    properties:
      bobs:
        - position: [0, -1.5, 0]
          mass: 1.0
        - position: [0.5, -3, 0]
          mass: 0.5
      pivot_point: [0, 2, 0]
      
  - name: wave_pool
    type: physics.radial_wave
    properties:
      sources: [[0, 0, 0]]
      wavelength: 1.0
      amplitude: 0.3
      
animations:
  - type: physics_simulation
    target: double_pendulum
    duration: 10
    start_time: 0
    
  - type: wave_propagation
    target: wave_pool
    duration: 10
    start_time: 5'''
        
        yaml_mob = Code(
            code=yaml_text,
            language="yaml",
            font_size=20,
            background="window",
            tab_width=2
        )
        
        title = Text("Physics Integration with YAML", font_size=36)
        title.to_edge(UP)
        
        benefits = BulletedList(
            "Real physics simulations",
            "Easy YAML configuration",
            "Educational animations",
            "Scientific accuracy",
            font_size=24
        )
        benefits.next_to(yaml_mob, RIGHT, buff=0.5)
        
        self.play(Write(title))
        self.play(FadeIn(yaml_mob))
        self.play(Write(benefits))
        self.wait(3)


if __name__ == "__main__":
    # Run the demos
    import os
    os.system(f"manim --media_dir user-data -pql {__file__} PhysicsStudioScene")
    os.system(f"manim --media_dir user-data -pql {__file__} PhysicsYAMLExample")
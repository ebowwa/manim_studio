"""Test physics integration in Manim Studio."""
from src.config.manim_config import config
from manim import *
import numpy as np


def test_physics_objects():
    """Test creating physics objects."""
    from src.components.physics_objects import SimplePendulum, Spring, ProjectileMotion
    
    # Test pendulum
    pendulum = SimplePendulum(length=2, angle=PI/4)
    assert isinstance(pendulum, VGroup)
    assert hasattr(pendulum, 'physics_step')
    
    # Test spring
    spring = Spring(rest_length=3, spring_constant=10)
    assert isinstance(spring, VGroup)
    assert hasattr(spring, 'physics_step')
    
    # Test projectile
    projectile = ProjectileMotion(initial_velocity=np.array([3, 4, 0]))
    assert isinstance(projectile, VGroup)
    assert hasattr(projectile, 'physics_step')
    
    print("✓ Physics objects created successfully")


def test_physics_effects():
    """Test physics effects."""
    try:
        from src.components.effects.physics_effects import (
            GravityEffect, OscillationEffect, SpringForceEffect
        )
        
        # Test that effects have create method
        assert hasattr(GravityEffect, 'create')
        assert hasattr(OscillationEffect, 'create')
        assert hasattr(SpringForceEffect, 'create')
        
        print("✓ Physics effects loaded successfully")
    except ImportError:
        print("⚠ Physics effects not available")


def test_physics_in_scene_builder():
    """Test physics object creation in scene builder."""
    from src.core.scene_builder import SceneBuilder
    
    builder = SceneBuilder()
    
    # Test creating physics object
    config = {
        'type': 'physics.pendulum',
        'params': {
            'length': 2,
            'angle': 0.5
        }
    }
    
    obj = builder.create_object('test_pendulum', config)
    assert obj is not None
    print("✓ Physics object created via scene builder")


class SimplePhysicsScene(Scene):
    """Simple scene to test physics rendering."""
    
    def construct(self):
        from src.components.physics_objects import SimplePendulum, create_physics_updater
        
        # Create and add pendulum
        pendulum = SimplePendulum(length=2, angle=PI/4)
        pendulum.add_updater(create_physics_updater(pendulum))
        
        title = Text("Physics Test", scale=0.8).to_edge(UP)
        
        self.add(title)
        self.add(pendulum)
        self.wait(3)


if __name__ == "__main__":
    print("Testing physics integration...\n")
    
    try:
        test_physics_objects()
        test_physics_effects()
        test_physics_in_scene_builder()
        
        print("\n✓ All physics tests passed!")
        print("\nTo see physics in action, run:")
        print("  manim --media_dir user-data -ql developer/tests/test_physics_integration.py SimplePhysicsScene")
        
    except Exception as e:
        print(f"\n✗ Physics test failed: {e}")
        import traceback
        traceback.print_exc()
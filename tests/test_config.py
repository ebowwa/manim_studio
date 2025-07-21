"""Tests for configuration models in manim_studio.core.config"""

import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, Any

from manim_studio.core.config import EffectConfig, AnimationConfig, SceneConfig, Config, CameraConfig


class TestEffectConfig:
    """Test cases for EffectConfig model."""
    
    def test_default_initialization(self):
        """Test EffectConfig with default values."""
        effect = EffectConfig(type="glow")
        assert effect.type == "glow"
        assert effect.params == {}
        assert effect.start_time == 0.0
        assert effect.duration is None
    
    def test_full_initialization(self):
        """Test EffectConfig with all parameters."""
        params = {"intensity": 0.8, "color": "#FF0000"}
        effect = EffectConfig(
            type="sparkle",
            params=params,
            start_time=2.5,
            duration=3.0
        )
        assert effect.type == "sparkle"
        assert effect.params == params
        assert effect.start_time == 2.5
        assert effect.duration == 3.0
    
    def test_from_dict(self):
        """Test creating EffectConfig from dictionary."""
        data = {
            "type": "fade",
            "params": {"opacity": 0.5},
            "start_time": 1.0,
            "duration": 2.0
        }
        effect = EffectConfig.from_dict(data)
        assert effect.type == "fade"
        assert effect.params["opacity"] == 0.5
        assert effect.start_time == 1.0
        assert effect.duration == 2.0
    
    def test_from_dict_with_missing_fields(self):
        """Test from_dict with minimal data."""
        data = {"type": "blur"}
        effect = EffectConfig.from_dict(data)
        assert effect.type == "blur"
        assert effect.params == {}
        assert effect.start_time == 0.0
        assert effect.duration is None
    
    def test_to_dict(self):
        """Test converting EffectConfig to dictionary."""
        effect = EffectConfig(
            type="rotate",
            params={"angle": 45},
            start_time=1.5,
            duration=2.0
        )
        data = effect.to_dict()
        assert data['type'] == "rotate"
        assert data['params']['angle'] == 45
        assert data['start_time'] == 1.5
        assert data['duration'] == 2.0
    
    def test_to_dict_without_duration(self):
        """Test to_dict when duration is None."""
        effect = EffectConfig(type="fade", params={"opacity": 0.5})
        data = effect.to_dict()
        assert 'duration' not in data
    
    def test_validation(self):
        """Test validation of EffectConfig fields."""
        # Empty type should raise error
        with pytest.raises(ValueError, match="Effect type cannot be empty"):
            EffectConfig(type="")
        
        # Negative start time should raise error
        with pytest.raises(ValueError, match="Start time cannot be negative"):
            EffectConfig(type="glow", start_time=-1.0)
        
        # Zero or negative duration should raise error
        with pytest.raises(ValueError, match="Duration must be positive"):
            EffectConfig(type="glow", duration=0.0)
        
        with pytest.raises(ValueError, match="Duration must be positive"):
            EffectConfig(type="glow", duration=-1.0)
    
    def test_copy(self):
        """Test copying EffectConfig."""
        original = EffectConfig(
            type="sparkle",
            params={"intensity": 0.8, "color": "#FF0000"},
            start_time=1.0,
            duration=2.0
        )
        copy = original.copy()
        
        # Check that values are the same
        assert copy.type == original.type
        assert copy.params == original.params
        assert copy.start_time == original.start_time
        assert copy.duration == original.duration
        
        # Check that modifying copy doesn't affect original
        copy.params["intensity"] = 0.5
        assert original.params["intensity"] == 0.8


class TestAnimationConfig:
    """Test cases for AnimationConfig model."""
    
    def test_default_initialization(self):
        """Test AnimationConfig with default values."""
        anim = AnimationConfig(
            target="circle",
            animation_type="FadeIn"
        )
        assert anim.target == "circle"
        assert anim.animation_type == "FadeIn"
        assert anim.params == {}
        assert anim.start_time == 0.0
        assert anim.duration == 1.0
    
    def test_full_initialization(self):
        """Test AnimationConfig with all parameters."""
        params = {"direction": "UP", "rate_func": "smooth"}
        anim = AnimationConfig(
            target="square",
            animation_type="MoveToTarget",
            params=params,
            start_time=3.0,
            duration=2.5
        )
        assert anim.target == "square"
        assert anim.animation_type == "MoveToTarget"
        assert anim.params == params
        assert anim.start_time == 3.0
        assert anim.duration == 2.5
    
    def test_from_dict(self):
        """Test creating AnimationConfig from dictionary."""
        data = {
            "target": "text",
            "animation_type": "Write",
            "params": {"run_time": 2.0},
            "start_time": 0.5,
            "duration": 2.0
        }
        anim = AnimationConfig.from_dict(data)
        assert anim.target == "text"
        assert anim.animation_type == "Write"
        assert anim.params["run_time"] == 2.0
        assert anim.start_time == 0.5
        assert anim.duration == 2.0
    
    def test_from_dict_with_defaults(self):
        """Test from_dict with minimal required data."""
        data = {
            "target": "dot",
            "animation_type": "GrowFromCenter"
        }
        anim = AnimationConfig.from_dict(data)
        assert anim.target == "dot"
        assert anim.animation_type == "GrowFromCenter"
        assert anim.params == {}
        assert anim.start_time == 0.0
        assert anim.duration == 1.0
    
    def test_to_dict(self):
        """Test converting AnimationConfig to dictionary."""
        anim = AnimationConfig(
            target="triangle",
            animation_type="Transform",
            params={"position": [1, 2, 0]},
            start_time=2.0,
            duration=1.5
        )
        data = anim.to_dict()
        assert data['target'] == "triangle"
        assert data['animation_type'] == "Transform"
        assert data['params']['position'] == [1, 2, 0]
        assert data['start_time'] == 2.0
        assert data['duration'] == 1.5
    
    def test_validation(self):
        """Test validation of AnimationConfig fields."""
        # Empty target should raise error
        with pytest.raises(ValueError, match="Animation target cannot be empty"):
            AnimationConfig(target="", animation_type="FadeIn")
        
        # Empty animation type should raise error
        with pytest.raises(ValueError, match="Animation type cannot be empty"):
            AnimationConfig(target="object", animation_type="")
        
        # Negative start time should raise error
        with pytest.raises(ValueError, match="Start time cannot be negative"):
            AnimationConfig(target="object", animation_type="FadeIn", start_time=-1.0)
        
        # Zero or negative duration should raise error
        with pytest.raises(ValueError, match="Duration must be positive"):
            AnimationConfig(target="object", animation_type="FadeIn", duration=0.0)
        
        with pytest.raises(ValueError, match="Duration must be positive"):
            AnimationConfig(target="object", animation_type="FadeIn", duration=-1.0)
    
    def test_copy(self):
        """Test copying AnimationConfig."""
        original = AnimationConfig(
            target="circle",
            animation_type="Rotate",
            params={"angle": 90, "axis": "Z"},
            start_time=1.0,
            duration=2.0
        )
        copy = original.copy()
        
        # Check that values are the same
        assert copy.target == original.target
        assert copy.animation_type == original.animation_type
        assert copy.params == original.params
        assert copy.start_time == original.start_time
        assert copy.duration == original.duration
        
        # Check that modifying copy doesn't affect original
        copy.params["angle"] = 180
        assert original.params["angle"] == 90
    
    def test_overlaps_with(self):
        """Test animation overlap detection."""
        anim1 = AnimationConfig(
            target="square",
            animation_type="MoveToTarget",
            start_time=1.0,
            duration=2.0
        )
        
        # Same target, overlapping time
        anim2 = AnimationConfig(
            target="square",
            animation_type="Rotate",
            start_time=2.0,
            duration=2.0
        )
        assert anim1.overlaps_with(anim2)
        assert anim2.overlaps_with(anim1)
        
        # Same target, non-overlapping time
        anim3 = AnimationConfig(
            target="square",
            animation_type="FadeOut",
            start_time=3.0,
            duration=1.0
        )
        assert not anim1.overlaps_with(anim3)
        assert not anim3.overlaps_with(anim1)
        
        # Different target, overlapping time
        anim4 = AnimationConfig(
            target="circle",
            animation_type="Create",
            start_time=1.5,
            duration=1.0
        )
        assert not anim1.overlaps_with(anim4)
        assert not anim4.overlaps_with(anim1)


class TestCameraConfig:
    """Test cases for CameraConfig model."""
    
    def test_default_initialization(self):
        """Test CameraConfig with default values."""
        camera = CameraConfig()
        assert camera.position == [0.0, 0.0, 5.0]
        assert camera.rotation == [0.0, 0.0, 0.0]
        assert camera.zoom == 1.0
        assert camera.fov == 60.0
        assert camera.near_clip == 0.1
        assert camera.far_clip == 100.0
    
    def test_full_initialization(self):
        """Test CameraConfig with all parameters."""
        camera = CameraConfig(
            position=[1.0, 2.0, 3.0],
            rotation=[45.0, 90.0, 0.0],
            zoom=2.0,
            fov=90.0,
            near_clip=0.5,
            far_clip=200.0
        )
        assert camera.position == [1.0, 2.0, 3.0]
        assert camera.rotation == [45.0, 90.0, 0.0]
        assert camera.zoom == 2.0
        assert camera.fov == 90.0
        assert camera.near_clip == 0.5
        assert camera.far_clip == 200.0
    
    def test_from_dict(self):
        """Test creating CameraConfig from dictionary."""
        data = {
            "position": [2.0, 3.0, 4.0],
            "rotation": [30.0, 60.0, 90.0],
            "zoom": 1.5,
            "fov": 75.0,
            "near_clip": 0.2,
            "far_clip": 150.0
        }
        camera = CameraConfig.from_dict(data)
        assert camera.position == [2.0, 3.0, 4.0]
        assert camera.rotation == [30.0, 60.0, 90.0]
        assert camera.zoom == 1.5
        assert camera.fov == 75.0
        assert camera.near_clip == 0.2
        assert camera.far_clip == 150.0
    
    def test_from_dict_with_defaults(self):
        """Test from_dict with minimal data."""
        data = {}
        camera = CameraConfig.from_dict(data)
        assert camera.position == [0.0, 0.0, 5.0]
        assert camera.rotation == [0.0, 0.0, 0.0]
        assert camera.zoom == 1.0
        assert camera.fov == 60.0
        assert camera.near_clip == 0.1
        assert camera.far_clip == 100.0
    
    def test_from_dict_with_partial_data(self):
        """Test from_dict with partial data."""
        data = {
            "position": [1.0, 1.0, 1.0],
            "fov": 45.0
        }
        camera = CameraConfig.from_dict(data)
        assert camera.position == [1.0, 1.0, 1.0]
        assert camera.rotation == [0.0, 0.0, 0.0]  # default
        assert camera.zoom == 1.0  # default
        assert camera.fov == 45.0
        assert camera.near_clip == 0.1  # default
        assert camera.far_clip == 100.0  # default
    
    def test_to_dict(self):
        """Test converting CameraConfig to dictionary."""
        camera = CameraConfig(
            position=[3.0, 4.0, 5.0],
            rotation=[15.0, 30.0, 45.0],
            zoom=0.5,
            fov=120.0,
            near_clip=0.01,
            far_clip=500.0
        )
        data = camera.to_dict()
        assert data['position'] == [3.0, 4.0, 5.0]
        assert data['rotation'] == [15.0, 30.0, 45.0]
        assert data['zoom'] == 0.5
        assert data['fov'] == 120.0
        assert data['near_clip'] == 0.01
        assert data['far_clip'] == 500.0
    
    def test_validation_position(self):
        """Test validation of camera position."""
        # Wrong number of coordinates
        with pytest.raises(ValueError, match="Camera position must have 3 coordinates"):
            CameraConfig(position=[0.0, 0.0])
        
        with pytest.raises(ValueError, match="Camera position must have 3 coordinates"):
            CameraConfig(position=[0.0, 0.0, 0.0, 0.0])
    
    def test_validation_rotation(self):
        """Test validation of camera rotation."""
        # Wrong number of angles
        with pytest.raises(ValueError, match="Camera rotation must have 3 angles"):
            CameraConfig(rotation=[0.0, 0.0])
        
        with pytest.raises(ValueError, match="Camera rotation must have 3 angles"):
            CameraConfig(rotation=[0.0])
    
    def test_validation_zoom(self):
        """Test validation of camera zoom."""
        # Zero zoom
        with pytest.raises(ValueError, match="Camera zoom must be positive"):
            CameraConfig(zoom=0.0)
        
        # Negative zoom
        with pytest.raises(ValueError, match="Camera zoom must be positive"):
            CameraConfig(zoom=-1.0)
    
    def test_validation_fov(self):
        """Test validation of field of view."""
        # Zero FOV
        with pytest.raises(ValueError, match="Field of view must be between 0 and 180 degrees"):
            CameraConfig(fov=0.0)
        
        # Negative FOV
        with pytest.raises(ValueError, match="Field of view must be between 0 and 180 degrees"):
            CameraConfig(fov=-10.0)
        
        # FOV too large
        with pytest.raises(ValueError, match="Field of view must be between 0 and 180 degrees"):
            CameraConfig(fov=180.0)
        
        with pytest.raises(ValueError, match="Field of view must be between 0 and 180 degrees"):
            CameraConfig(fov=200.0)
    
    def test_validation_near_clip(self):
        """Test validation of near clip plane."""
        # Zero near clip
        with pytest.raises(ValueError, match="Near clip plane must be positive"):
            CameraConfig(near_clip=0.0)
        
        # Negative near clip
        with pytest.raises(ValueError, match="Near clip plane must be positive"):
            CameraConfig(near_clip=-0.1)
    
    def test_validation_far_clip(self):
        """Test validation of far clip plane."""
        # Far clip equal to near clip
        with pytest.raises(ValueError, match="Far clip plane must be greater than near clip plane"):
            CameraConfig(near_clip=1.0, far_clip=1.0)
        
        # Far clip less than near clip
        with pytest.raises(ValueError, match="Far clip plane must be greater than near clip plane"):
            CameraConfig(near_clip=10.0, far_clip=5.0)
    
    def test_valid_edge_cases(self):
        """Test valid edge case values."""
        # Very small but valid FOV
        camera = CameraConfig(fov=0.1)
        assert camera.fov == 0.1
        
        # Large but valid FOV
        camera = CameraConfig(fov=179.9)
        assert camera.fov == 179.9
        
        # Very small near clip
        camera = CameraConfig(near_clip=0.001, far_clip=1000.0)
        assert camera.near_clip == 0.001
        
        # Very large far clip
        camera = CameraConfig(far_clip=10000.0)
        assert camera.far_clip == 10000.0
    
    def test_copy(self):
        """Test copying CameraConfig."""
        original = CameraConfig(
            position=[1.0, 2.0, 3.0],
            rotation=[45.0, 90.0, 135.0],
            zoom=1.5,
            fov=75.0,
            near_clip=0.5,
            far_clip=250.0
        )
        copy = original.copy()
        
        # Check that values are the same
        assert copy.position == original.position
        assert copy.rotation == original.rotation
        assert copy.zoom == original.zoom
        assert copy.fov == original.fov
        assert copy.near_clip == original.near_clip
        assert copy.far_clip == original.far_clip
        
        # Check that modifying copy doesn't affect original
        copy.position[0] = 10.0
        assert original.position[0] == 1.0
        
        copy.rotation[1] = 180.0
        assert original.rotation[1] == 90.0


class TestSceneConfig:
    """Test cases for SceneConfig model."""
    
    def test_default_initialization(self):
        """Test SceneConfig with default values."""
        scene = SceneConfig(name="TestScene")
        assert scene.name == "TestScene"
        assert scene.description == ""
        assert scene.duration == 10.0
        assert scene.background_color == "#000000"
        assert scene.resolution == (1920, 1080)
        assert scene.fps == 60
        assert scene.objects == {}
        assert scene.effects == []
        assert scene.animations == []
        assert scene.assets == {}
    
    def test_full_initialization(self):
        """Test SceneConfig with all parameters."""
        effect = EffectConfig(type="glow")
        anim = AnimationConfig(target="circle", animation_type="Create")
        
        scene = SceneConfig(
            name="ComplexScene",
            description="A complex test scene",
            duration=20.0,
            background_color="#FFFFFF",
            resolution=(3840, 2160),
            fps=120,
            objects={"circle": {"radius": 1.0}},
            effects=[effect],
            animations=[anim],
            assets={"logo": "path/to/logo.png"}
        )
        
        assert scene.name == "ComplexScene"
        assert scene.description == "A complex test scene"
        assert scene.duration == 20.0
        assert scene.background_color == "#FFFFFF"
        assert scene.resolution == (3840, 2160)
        assert scene.fps == 120
        assert len(scene.effects) == 1
        assert len(scene.animations) == 1
        assert "logo" in scene.assets
    
    def test_from_dict(self):
        """Test creating SceneConfig from dictionary."""
        data = {
            "name": "DictScene",
            "description": "Scene from dict",
            "duration": 15.0,
            "background_color": "#FF0000",
            "resolution": [2560, 1440],
            "fps": 30,
            "objects": {"square": {"side_length": 2.0}},
            "effects": [{"type": "blur", "params": {"radius": 5}}],
            "animations": [{"target": "square", "animation_type": "Rotate"}],
            "assets": {"texture": "path/to/texture.jpg"}
        }
        
        scene = SceneConfig.from_dict(data)
        assert scene.name == "DictScene"
        assert scene.description == "Scene from dict"
        assert scene.duration == 15.0
        assert scene.background_color == "#FF0000"
        assert scene.resolution == (2560, 1440)
        assert scene.fps == 30
        assert "square" in scene.objects
        assert len(scene.effects) == 1
        assert scene.effects[0].type == "blur"
        assert len(scene.animations) == 1
        assert scene.animations[0].target == "square"
        assert "texture" in scene.assets
    
    def test_from_dict_with_defaults(self):
        """Test from_dict with minimal data."""
        data = {"name": "MinimalScene"}
        scene = SceneConfig.from_dict(data)
        assert scene.name == "MinimalScene"
        assert scene.description == ""
        assert scene.duration == 10.0
        assert scene.background_color == "#000000"
        assert scene.resolution == (1920, 1080)
        assert scene.fps == 60
    
    def test_to_dict(self):
        """Test converting SceneConfig to dictionary."""
        effect = EffectConfig(type="glow")
        anim = AnimationConfig(target="circle", animation_type="Create")
        
        scene = SceneConfig(
            name="TestScene",
            description="Test description",
            duration=15.0,
            background_color="#FF00FF",
            resolution=(2560, 1440),
            fps=30,
            objects={"square": {"side_length": 2.0}},
            effects=[effect],
            animations=[anim],
            assets={"logo": "path/to/logo.png"}
        )
        
        data = scene.to_dict()
        assert data['name'] == "TestScene"
        assert data['description'] == "Test description"
        assert data['duration'] == 15.0
        assert data['background_color'] == "#FF00FF"
        assert data['resolution'] == [2560, 1440]
        assert data['fps'] == 30
        assert "square" in data['objects']
        assert len(data['effects']) == 1
        assert len(data['animations']) == 1
        assert "logo" in data['assets']
    
    def test_validation(self):
        """Test validation of SceneConfig fields."""
        # Empty name should raise error
        with pytest.raises(ValueError, match="Scene name cannot be empty"):
            SceneConfig(name="")
        
        # Negative duration should raise error
        with pytest.raises(ValueError, match="Duration must be positive"):
            SceneConfig(name="Test", duration=0.0)
        
        # Invalid FPS should raise error
        with pytest.raises(ValueError, match="FPS must be positive"):
            SceneConfig(name="Test", fps=0)
        
        # Invalid resolution format
        with pytest.raises(ValueError, match="Resolution must be a tuple"):
            SceneConfig(name="Test", resolution=[1920, 1080])
        
        # Invalid resolution dimensions
        with pytest.raises(ValueError, match="Resolution dimensions must be positive"):
            SceneConfig(name="Test", resolution=(0, 1080))
        
        # Invalid color format
        with pytest.raises(ValueError, match="Invalid background color format"):
            SceneConfig(name="Test", background_color="red")
        
        with pytest.raises(ValueError, match="Invalid background color format"):
            SceneConfig(name="Test", background_color="#GGGGGG")
    
    def test_color_validation(self):
        """Test various color formats."""
        # Valid colors
        SceneConfig(name="Test", background_color="#000000")
        SceneConfig(name="Test", background_color="#FFFFFF")
        SceneConfig(name="Test", background_color="#FF0000")
        SceneConfig(name="Test", background_color="#123")
        SceneConfig(name="Test", background_color="#abc")
        SceneConfig(name="Test", background_color="#ABC")
    
    def test_add_effect(self):
        """Test adding effects to scene."""
        scene = SceneConfig(name="TestScene")
        effect = EffectConfig(type="blur", params={"radius": 5})
        
        scene.add_effect(effect)
        assert len(scene.effects) == 1
        assert scene.effects[0].type == "blur"
    
    def test_add_animation(self):
        """Test adding animations to scene."""
        scene = SceneConfig(name="TestScene")
        anim = AnimationConfig(target="text", animation_type="Write")
        
        scene.add_animation(anim)
        assert len(scene.animations) == 1
        assert scene.animations[0].target == "text"
    
    def test_add_object(self):
        """Test adding objects to scene."""
        scene = SceneConfig(name="TestScene")
        
        scene.add_object("circle", {"radius": 1.0, "color": "#FF0000"})
        assert "circle" in scene.objects
        assert scene.objects["circle"]["radius"] == 1.0
        
        # Adding duplicate should raise error
        with pytest.raises(ValueError, match="Object 'circle' already exists"):
            scene.add_object("circle", {"radius": 2.0})
    
    def test_add_asset(self):
        """Test adding assets to scene."""
        scene = SceneConfig(name="TestScene")
        
        scene.add_asset("background", "path/to/bg.jpg")
        assert "background" in scene.assets
        assert scene.assets["background"] == "path/to/bg.jpg"
        
        # Adding duplicate should raise error
        with pytest.raises(ValueError, match="Asset 'background' already exists"):
            scene.add_asset("background", "path/to/other.jpg")
    
    def test_get_animations_for_target(self):
        """Test getting animations for specific target."""
        scene = SceneConfig(name="TestScene")
        scene.add_animation(AnimationConfig(target="circle", animation_type="Create"))
        scene.add_animation(AnimationConfig(target="square", animation_type="FadeIn"))
        scene.add_animation(AnimationConfig(target="circle", animation_type="Rotate"))
        
        circle_anims = scene.get_animations_for_target("circle")
        assert len(circle_anims) == 2
        assert circle_anims[0].animation_type == "Create"
        assert circle_anims[1].animation_type == "Rotate"
        
        square_anims = scene.get_animations_for_target("square")
        assert len(square_anims) == 1
        assert square_anims[0].animation_type == "FadeIn"
    
    def test_get_effects_at_time(self):
        """Test getting active effects at specific time."""
        scene = SceneConfig(name="TestScene", duration=10.0)
        
        # Effect that starts at 0 and runs forever
        scene.add_effect(EffectConfig(type="glow", start_time=0.0))
        
        # Effect that runs from 2 to 5
        scene.add_effect(EffectConfig(type="blur", start_time=2.0, duration=3.0))
        
        # Effect that runs from 7 to 9
        scene.add_effect(EffectConfig(type="fade", start_time=7.0, duration=2.0))
        
        # Test at different times
        effects_at_1 = scene.get_effects_at_time(1.0)
        assert len(effects_at_1) == 1
        assert effects_at_1[0].type == "glow"
        
        effects_at_3 = scene.get_effects_at_time(3.0)
        assert len(effects_at_3) == 2
        assert {e.type for e in effects_at_3} == {"glow", "blur"}
        
        effects_at_8 = scene.get_effects_at_time(8.0)
        assert len(effects_at_8) == 2
        assert {e.type for e in effects_at_8} == {"glow", "fade"}
        
        effects_at_10 = scene.get_effects_at_time(10.0)
        assert len(effects_at_10) == 1
        assert effects_at_10[0].type == "glow"
    
    def test_validate_timeline(self):
        """Test timeline validation."""
        scene = SceneConfig(name="TestScene", duration=5.0)
        
        # Add overlapping animations on same target
        scene.add_animation(AnimationConfig(
            target="circle", 
            animation_type="Create",
            start_time=1.0,
            duration=2.0
        ))
        scene.add_animation(AnimationConfig(
            target="circle",
            animation_type="Rotate",
            start_time=2.0,
            duration=2.0
        ))
        
        # Add animation that exceeds scene duration
        scene.add_animation(AnimationConfig(
            target="square",
            animation_type="FadeIn",
            start_time=4.0,
            duration=2.0
        ))
        
        # Add effect that exceeds scene duration
        scene.add_effect(EffectConfig(
            type="blur",
            start_time=3.0,
            duration=3.0
        ))
        
        warnings = scene.validate_timeline()
        assert len(warnings) == 3
        
        # Check for overlap warning
        assert any("Animation conflict" in w and "circle" in w for w in warnings)
        
        # Check for duration warnings
        assert any("square" in w and "extends beyond" in w for w in warnings)
        assert any("blur" in w and "extends beyond" in w for w in warnings)
    
    def test_scene_with_camera_config(self):
        """Test SceneConfig with camera configuration."""
        camera = CameraConfig(
            position=[0.0, 5.0, 10.0],
            rotation=[30.0, 0.0, 0.0],
            zoom=1.5,
            fov=75.0
        )
        scene = SceneConfig(name="CameraScene", camera=camera)
        
        assert scene.camera is not None
        assert scene.camera.position == [0.0, 5.0, 10.0]
        assert scene.camera.rotation == [30.0, 0.0, 0.0]
        assert scene.camera.zoom == 1.5
        assert scene.camera.fov == 75.0
    
    def test_scene_camera_from_dict(self):
        """Test SceneConfig with camera from dictionary."""
        data = {
            "name": "SceneWithCamera",
            "camera": {
                "position": [1.0, 2.0, 3.0],
                "rotation": [45.0, 0.0, 0.0],
                "zoom": 2.0,
                "fov": 90.0,
                "near_clip": 0.5,
                "far_clip": 200.0
            }
        }
        scene = SceneConfig.from_dict(data)
        
        assert scene.camera is not None
        assert scene.camera.position == [1.0, 2.0, 3.0]
        assert scene.camera.rotation == [45.0, 0.0, 0.0]
        assert scene.camera.zoom == 2.0
        assert scene.camera.fov == 90.0
        assert scene.camera.near_clip == 0.5
        assert scene.camera.far_clip == 200.0
    
    def test_scene_camera_to_dict(self):
        """Test SceneConfig to_dict with camera."""
        camera = CameraConfig(
            position=[5.0, 5.0, 5.0],
            rotation=[0.0, 45.0, 0.0],
            zoom=0.8,
            fov=50.0
        )
        scene = SceneConfig(name="TestScene", camera=camera)
        
        data = scene.to_dict()
        assert 'camera' in data
        assert data['camera']['position'] == [5.0, 5.0, 5.0]
        assert data['camera']['rotation'] == [0.0, 45.0, 0.0]
        assert data['camera']['zoom'] == 0.8
        assert data['camera']['fov'] == 50.0
    
    def test_scene_without_camera(self):
        """Test SceneConfig without camera configuration."""
        scene = SceneConfig(name="NoCameraScene")
        assert scene.camera is None
        
        # to_dict should not include camera key
        data = scene.to_dict()
        assert 'camera' not in data
    
    def test_scene_camera_none_in_dict(self):
        """Test SceneConfig from_dict with explicit None camera."""
        data = {
            "name": "SceneNullCamera",
            "camera": None
        }
        scene = SceneConfig.from_dict(data)
        assert scene.camera is None
    
    def test_scene_full_with_camera(self):
        """Test SceneConfig with all features including camera."""
        camera = CameraConfig(position=[0.0, 0.0, 10.0])
        effect = EffectConfig(type="blur")
        anim = AnimationConfig(target="box", animation_type="Rotate")
        
        scene = SceneConfig(
            name="FullScene",
            description="Full scene with camera",
            duration=15.0,
            camera=camera,
            effects=[effect],
            animations=[anim],
            objects={"box": {"size": 1.0}},
            assets={"texture": "path/to/texture.png"}
        )
        
        # Convert to dict and back
        data = scene.to_dict()
        scene2 = SceneConfig.from_dict(data)
        
        # Verify everything is preserved
        assert scene2.name == "FullScene"
        assert scene2.description == "Full scene with camera"
        assert scene2.duration == 15.0
        assert scene2.camera is not None
        assert scene2.camera.position == [0.0, 0.0, 10.0]
        assert len(scene2.effects) == 1
        assert len(scene2.animations) == 1
        assert "box" in scene2.objects
        assert "texture" in scene2.assets


class TestConfig:
    """Test cases for Config manager class."""
    
    def test_initialization_without_file(self):
        """Test Config initialization without file."""
        config = Config()
        assert config.config_path is None
        assert config.data == {}
    
    def test_initialization_with_nonexistent_file(self):
        """Test Config initialization with non-existent file."""
        config = Config("nonexistent.json")
        assert config.config_path == Path("nonexistent.json")
        assert config.data == {}
    
    def test_load_json(self):
        """Test loading JSON configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "value"}, f)
            temp_path = f.name
        
        try:
            config = Config(temp_path)
            assert config.data["test"] == "value"
        finally:
            Path(temp_path).unlink()
    
    def test_save_json(self):
        """Test saving JSON configuration."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            # Write empty JSON to avoid load error
            json.dump({}, f)
            temp_path = f.name
        
        try:
            config = Config(temp_path)
            config.data = {"saved": "data"}
            config.save()
            
            # Reload and verify
            with open(temp_path, 'r') as f:
                loaded = json.load(f)
            assert loaded["saved"] == "data"
        finally:
            Path(temp_path).unlink()
    
    def test_get_value(self):
        """Test getting configuration values."""
        config = Config()
        config.data = {
            "level1": {
                "level2": {
                    "value": "nested"
                }
            }
        }
        
        assert config.get("level1.level2.value") == "nested"
        assert config.get("level1.level2") == {"value": "nested"}
        assert config.get("nonexistent", "default") == "default"
    
    def test_set_value(self):
        """Test setting configuration values."""
        config = Config()
        
        config.set("new.nested.value", "test")
        assert config.data["new"]["nested"]["value"] == "test"
        
        config.set("new.nested.another", "test2")
        assert config.data["new"]["nested"]["another"] == "test2"
    
    def test_get_scene_config(self):
        """Test getting scene configuration."""
        config = Config()
        config.data = {
            "scenes": {
                "test_scene": {
                    "name": "test_scene",
                    "duration": 5.0
                }
            }
        }
        
        scene = config.get_scene_config("test_scene")
        assert scene.name == "test_scene"
        assert scene.duration == 5.0
        
        with pytest.raises(ValueError):
            config.get_scene_config("nonexistent")
    
    def test_list_scenes(self):
        """Test listing available scenes."""
        config = Config()
        config.data = {
            "scenes": {
                "scene1": {},
                "scene2": {},
                "scene3": {}
            }
        }
        
        scenes = config.list_scenes()
        assert len(scenes) == 3
        assert "scene1" in scenes
        assert "scene2" in scenes
        assert "scene3" in scenes


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
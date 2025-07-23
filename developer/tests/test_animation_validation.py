"""Tests for animation parameter validation in SceneBuilder."""

import pytest
import logging
import numpy as np
from unittest.mock import Mock, patch
from manim import Circle, FadeIn

from src.core.scene_builder import SceneBuilder
from src.core.config import AnimationConfig
from src.core.asset_manager import AssetManager


class TestAnimationParameterValidation:
    """Test suite for animation parameter validation."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.builder = SceneBuilder()
        self.mock_objects = {'test_circle': Mock(spec=Circle)}
        
        # Set up logging capture
        self.log_records = []
        self.handler = logging.Handler()
        self.handler.emit = lambda record: self.log_records.append(record)
        logger = logging.getLogger('src.core.scene_builder')
        logger.addHandler(self.handler)
        logger.setLevel(logging.DEBUG)
    
    def teardown_method(self):
        """Clean up test fixtures."""
        logger = logging.getLogger('src.core.scene_builder')
        logger.removeHandler(self.handler)
    
    def test_fadein_valid_shift_parameter(self):
        """Test FadeIn animation with valid shift parameter."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='fade_in',
            params={'shift': [1, 0, 0]},
            duration=1.0
        )
        
        with patch('manim.FadeIn') as mock_fadein:
            mock_fadein.return_value = Mock()
            result = self.builder.create_animation(anim_config, self.mock_objects)
            
            # Should succeed and create FadeIn animation
            assert result is not None
            mock_fadein.assert_called_once()
            
            # Check that shift was converted to numpy array
            call_args = mock_fadein.call_args
            shift_arg = call_args.kwargs.get('shift')
            assert isinstance(shift_arg, np.ndarray)
            np.testing.assert_array_equal(shift_arg, [1, 0, 0])
    
    def test_fadein_invalid_shift_type(self):
        """Test FadeIn animation with invalid shift parameter type."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='fade_in',
            params={'shift': 'invalid'},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert 'shift parameter must be array-like' in error_logs[0].getMessage()
    
    def test_fadein_invalid_shift_length(self):
        """Test FadeIn animation with invalid shift parameter length."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='fade_in',
            params={'shift': [1]},  # Too short
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert 'must have 2 or 3 components' in error_logs[0].getMessage()
    
    def test_fadein_invalid_shift_values(self):
        """Test FadeIn animation with non-numeric shift values."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='fade_in',
            params={'shift': ['invalid', 'values', 'here']},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert 'contains invalid values' in error_logs[0].getMessage()
    
    def test_move_missing_to_parameter(self):
        """Test move animation missing required 'to' parameter."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='move',
            params={},  # Missing 'to' parameter
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert "missing required 'to' parameter" in error_logs[0].getMessage()
    
    def test_move_invalid_to_parameter_type(self):
        """Test move animation with invalid 'to' parameter type."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='move',
            params={'to': 'invalid'},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert "'to' parameter must be array-like" in error_logs[0].getMessage()
    
    def test_move_valid_to_parameter(self):
        """Test move animation with valid 'to' parameter."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='move',
            params={'to': [2, 1, 0]},
            duration=1.0
        )
        
        with patch.object(self.mock_objects['test_circle'], 'animate') as mock_animate:
            mock_animate.move_to.return_value.set_run_time.return_value = Mock()
            
            result = self.builder.create_animation(anim_config, self.mock_objects)
            
            # Should succeed
            assert result is not None
            mock_animate.move_to.assert_called_once()
    
    def test_scale_missing_factor_parameter(self):
        """Test scale animation missing required 'factor' parameter."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='scale',
            params={},  # Missing 'factor' parameter
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert "missing required 'factor' parameter" in error_logs[0].getMessage()
    
    def test_scale_invalid_factor_type(self):
        """Test scale animation with invalid factor type."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='scale',
            params={'factor': 'invalid'},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert "'factor' parameter must be numeric" in error_logs[0].getMessage()
    
    def test_scale_negative_factor(self):
        """Test scale animation with negative factor."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='scale',
            params={'factor': -0.5},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert "'factor' parameter must be positive" in error_logs[0].getMessage()
    
    def test_scale_valid_factor(self):
        """Test scale animation with valid factor."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='scale',
            params={'factor': 2.0},
            duration=1.0
        )
        
        with patch.object(self.mock_objects['test_circle'], 'animate') as mock_animate:
            mock_animate.scale.return_value.set_run_time.return_value = Mock()
            
            result = self.builder.create_animation(anim_config, self.mock_objects)
            
            # Should succeed
            assert result is not None
            mock_animate.scale.assert_called_once_with(2.0)
    
    def test_transform_missing_to_parameter(self):
        """Test transform animation missing required 'to' parameter."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='transform',
            params={},  # Missing 'to' parameter
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert "missing required 'to' parameter" in error_logs[0].getMessage()
    
    def test_transform_invalid_to_parameter_type(self):
        """Test transform animation with invalid 'to' parameter type."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='transform',
            params={'to': 'invalid'},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert "'to' parameter must be a dict" in error_logs[0].getMessage()
    
    def test_transform_missing_type_in_to_parameter(self):
        """Test transform animation with 'to' parameter missing 'type' field."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='transform',
            params={'to': {'params': {}}},  # Missing 'type' field
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert "missing 'type' field" in error_logs[0].getMessage()
    
    def test_rotate_invalid_angle_type(self):
        """Test rotate animation with invalid angle type."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='rotate',
            params={'angle': 'invalid'},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail validation and return None
        assert result is None
        
        # Check that error was logged
        error_logs = [r for r in self.log_records if r.levelno >= logging.ERROR]
        assert len(error_logs) > 0
        assert "'angle' parameter must be numeric" in error_logs[0].getMessage()
    
    def test_nonexistent_target(self):
        """Test animation with nonexistent target object."""
        anim_config = AnimationConfig(
            target='nonexistent',
            animation_type='fade_in',
            params={},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail and return None
        assert result is None
        
        # Check that warning was logged
        warning_logs = [r for r in self.log_records if r.levelno >= logging.WARNING]
        assert len(warning_logs) > 0
        assert "not found" in warning_logs[0].getMessage()
    
    def test_empty_target_name(self):
        """Test animation with empty target name."""
        anim_config = AnimationConfig(
            target='',
            animation_type='fade_in',
            params={},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail and return None
        assert result is None
        
        # Check that warning was logged
        warning_logs = [r for r in self.log_records if r.levelno >= logging.WARNING]
        assert len(warning_logs) > 0
        assert "no target specified" in warning_logs[0].getMessage()
    
    def test_unknown_animation_type(self):
        """Test animation with unknown animation type."""
        anim_config = AnimationConfig(
            target='test_circle',
            animation_type='unknown_animation',
            params={},
            duration=1.0
        )
        
        result = self.builder.create_animation(anim_config, self.mock_objects)
        
        # Should fail and return None
        assert result is None
        
        # Check that warning was logged
        warning_logs = [r for r in self.log_records if r.levelno >= logging.WARNING]
        assert len(warning_logs) > 0
        assert "Unknown animation type" in warning_logs[0].getMessage()


if __name__ == '__main__':
    pytest.main([__file__])
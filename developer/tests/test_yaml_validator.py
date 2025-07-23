"""Tests for YAML validation functionality."""

import pytest
import tempfile
import os
from pathlib import Path
from src.core.yaml_validator import YamlValidator, ValidationSeverity, validate_yaml_file

class TestYamlValidator:
    """Test cases for YamlValidator class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.validator = YamlValidator()
    
    def create_temp_yaml(self, content: str) -> str:
        """Create a temporary YAML file with given content."""
        fd, path = tempfile.mkstemp(suffix='.yaml')
        try:
            with os.fdopen(fd, 'w') as tmp:
                tmp.write(content)
        except:
            os.close(fd)
            raise
        return path
    
    def test_valid_yaml_file(self):
        """Test validation of a valid YAML file."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  fps: 30
  resolution: "1080p"
  background_color: "#000000"
  objects:
    - type: "circle"
      name: "circle1"
      position: [0, 0, 0]
  animations:
    - type: "create"
      target: "circle1"
      start_time: 0
      duration: 1.0
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert is_valid
            # Should have no errors
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert len(errors) == 0
        finally:
            os.unlink(path)
    
    def test_invalid_yaml_syntax(self):
        """Test detection of YAML syntax errors."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  objects:
    - type: circle
      name: circle1
      invalid_indent
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            # Should have syntax error
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert len(errors) > 0
            assert any("syntax error" in r.message.lower() for r in errors)
        finally:
            os.unlink(path)
    
    def test_missing_required_fields(self):
        """Test detection of missing required fields."""
        content = """
scene:
  # Missing name
  duration: 5.0
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert any("name is required" in r.message for r in errors)
        finally:
            os.unlink(path)
    
    def test_invalid_duration(self):
        """Test detection of invalid duration values."""
        content = """
scene:
  name: "TestScene"
  duration: -1.0  # Invalid negative duration
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert any("duration" in r.message.lower() and ">=" in r.message for r in errors)
        finally:
            os.unlink(path)
    
    def test_invalid_fps(self):
        """Test detection of invalid FPS values."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  fps: 0  # Invalid FPS
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert any("fps" in r.message.lower() and ">=" in r.message for r in errors)
        finally:
            os.unlink(path)
    
    def test_invalid_resolution(self):
        """Test detection of invalid resolution values."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  resolution: "invalid_resolution"
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert any("resolution" in r.message.lower() for r in errors)
        finally:
            os.unlink(path)
    
    def test_invalid_color_format(self):
        """Test detection of invalid color formats."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  background_color: "#invalid"  # Invalid hex color
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert any("color" in r.message.lower() for r in errors)
        finally:
            os.unlink(path)
    
    def test_invalid_object_structure(self):
        """Test detection of invalid object structure."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  objects:
    - type: "circle"
      # Missing name
      position: [0, 0, 0]
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert any("name is required" in r.message for r in errors)
        finally:
            os.unlink(path)
    
    def test_invalid_animation_structure(self):
        """Test detection of invalid animation structure."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  animations:
    - type: "create"
      # Missing target
      start_time: 0
      duration: 1.0
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert any("target" in r.message and "required" in r.message for r in errors)
        finally:
            os.unlink(path)
    
    def test_unknown_object_type_warning(self):
        """Test that unknown object types generate warnings."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  objects:
    - type: "unknown_object_type"
      name: "obj1"
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            # Should be valid but with warnings
            assert is_valid
            warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
            assert any("unknown object type" in r.message.lower() for r in warnings)
        finally:
            os.unlink(path)
    
    def test_unknown_animation_type_warning(self):
        """Test that unknown animation types generate warnings."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  animations:
    - type: "unknown_animation"
      target: "obj1"
      start_time: 0
      duration: 1.0
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            # Should be valid but with warnings
            assert is_valid
            warnings = [r for r in results if r.severity == ValidationSeverity.WARNING]
            assert any("unknown animation type" in r.message.lower() for r in warnings)
        finally:
            os.unlink(path)
    
    def test_camera_validation(self):
        """Test camera configuration validation."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
  camera:
    type: "invalid_camera_type"
    position: [0, 0, 1, 2]  # Too many coordinates
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            # Should have errors for both invalid camera type and position
            assert len(errors) >= 2
        finally:
            os.unlink(path)
    
    def test_nonexistent_file(self):
        """Test handling of nonexistent files."""
        is_valid, results = self.validator.validate_file("/nonexistent/file.yaml")
        assert not is_valid
        errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
        assert any("does not exist" in r.message for r in errors)
    
    def test_empty_file(self):
        """Test handling of empty YAML files."""
        content = ""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert not is_valid
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert any("empty" in r.message.lower() for r in errors)
        finally:
            os.unlink(path)
    
    def test_validate_yaml_file_function(self):
        """Test the standalone validate_yaml_file function."""
        content = """
scene:
  name: "TestScene"
  duration: 5.0
"""
        path = self.create_temp_yaml(content)
        try:
            # Test valid file
            result = validate_yaml_file(path, verbose=False)
            assert result == True
            
            # Test with verbose output - just ensure it doesn't crash
            result = validate_yaml_file(path, verbose=True)
            assert result == True
        finally:
            os.unlink(path)
    
    def test_complex_scene_validation(self):
        """Test validation of a complex scene configuration."""
        content = """
scene:
  name: "ComplexScene"
  duration: 10.0
  fps: 60
  resolution: [1920, 1080]
  background_color: [0, 0, 0]
  camera:
    type: "3d"
    position: [0, 0, 5]
  objects:
    - type: "circle"
      name: "circle1"
      position: [0, 0, 0]
      color: "#FF0000"
    - type: "text"
      name: "title"
      text: "Hello World"
      position: [0, 2, 0]
  animations:
    - type: "create"
      target: "circle1"
      start_time: 0
      duration: 2.0
    - type: "write"
      target: "title"
      start_time: 1.0
      duration: 1.5
  effects:
    - type: "glow"
      start_time: 2.0
      duration: 3.0
      intensity: 0.8
"""
        path = self.create_temp_yaml(content)
        try:
            is_valid, results = self.validator.validate_file(path)
            assert is_valid
            # Should have no errors
            errors = [r for r in results if r.severity == ValidationSeverity.ERROR]
            assert len(errors) == 0
        finally:
            os.unlink(path)

if __name__ == "__main__":
    pytest.main([__file__])
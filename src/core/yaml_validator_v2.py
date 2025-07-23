"""Enhanced YAML validator that integrates with Pydantic types.

This validator combines YAML syntax checking with Pydantic model validation
for comprehensive configuration validation.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from pydantic import ValidationError

from .types import (
    ManimStudioConfig, SceneConfig, ValidationResult,
    ValidationError as TypedValidationError
)


class EnhancedYamlValidator:
    """Enhanced YAML validator with Pydantic integration."""
    
    def __init__(self):
        """Initialize the enhanced validator."""
        self.pydantic_errors: List[ValidationError] = []
        
    def validate_file(
        self, 
        file_path: Union[str, Path],
        full_validation: bool = True
    ) -> ValidationResult:
        """Validate a YAML file with full type checking.
        
        Args:
            file_path: Path to YAML file
            full_validation: If True, perform Pydantic validation too
            
        Returns:
            ValidationResult with all errors and warnings
        """
        result = ValidationResult(valid=True)
        file_path = Path(file_path)
        
        # Check file exists
        if not file_path.exists():
            result.add_error("file", f"File not found: {file_path}")
            return result
        
        # Step 1: Validate YAML syntax
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
        except yaml.YAMLError as e:
            result.add_error(
                "yaml_syntax",
                f"YAML syntax error: {str(e)}",
                line=getattr(e, 'problem_mark', {}).get('line')
            )
            return result
        
        if not isinstance(data, dict):
            result.add_error("yaml_structure", "YAML must contain a dictionary at root level")
            return result
        
        # Step 2: Basic structure validation
        self._validate_basic_structure(data, result)
        
        # Step 3: Full Pydantic validation
        if full_validation and result.valid:
            self._validate_with_pydantic(data, result)
        
        return result
    
    def _validate_basic_structure(
        self, 
        data: Dict[str, Any], 
        result: ValidationResult
    ) -> None:
        """Validate basic YAML structure before Pydantic."""
        # Check for scene or root-level config
        if 'scene' not in data and 'name' not in data:
            result.add_error(
                "structure",
                "YAML must contain either 'scene' section or root-level scene config"
            )
            return
        
        # Get scene data
        scene_data = data.get('scene', data)
        
        # Check required fields
        if not scene_data.get('name'):
            result.add_error("scene.name", "Scene name is required")
        
        if 'duration' not in scene_data:
            result.add_error("scene.duration", "Scene duration is required")
        elif not isinstance(scene_data['duration'], (int, float)):
            result.add_error(
                "scene.duration", 
                f"Duration must be a number, got {type(scene_data['duration']).__name__}"
            )
        
        # Check objects
        if 'objects' in scene_data:
            if not isinstance(scene_data['objects'], list):
                result.add_error(
                    "scene.objects",
                    "Objects must be a list"
                )
            else:
                for i, obj in enumerate(scene_data['objects']):
                    self._validate_object_basic(obj, f"scene.objects[{i}]", result)
        
        # Check animations
        if 'animations' in scene_data:
            if not isinstance(scene_data['animations'], list):
                result.add_error(
                    "scene.animations",
                    "Animations must be a list"
                )
            else:
                for i, anim in enumerate(scene_data['animations']):
                    self._validate_animation_basic(anim, f"scene.animations[{i}]", result)
    
    def _validate_object_basic(
        self, 
        obj: Any, 
        path: str, 
        result: ValidationResult
    ) -> None:
        """Basic object validation."""
        if not isinstance(obj, dict):
            result.add_error(path, "Object must be a dictionary")
            return
        
        if not obj.get('id'):
            result.add_error(f"{path}.id", "Object ID is required")
        
        if not obj.get('type'):
            result.add_error(f"{path}.type", "Object type is required")
    
    def _validate_animation_basic(
        self, 
        anim: Any, 
        path: str, 
        result: ValidationResult
    ) -> None:
        """Basic animation validation."""
        if not isinstance(anim, dict):
            result.add_error(path, "Animation must be a dictionary")
            return
        
        if not anim.get('target'):
            result.add_error(f"{path}.target", "Animation target is required")
        
        if not anim.get('type'):
            result.add_error(f"{path}.type", "Animation type is required")
    
    def _validate_with_pydantic(
        self, 
        data: Dict[str, Any], 
        result: ValidationResult
    ) -> None:
        """Validate with Pydantic models for full type checking."""
        try:
            # Try to create ManimStudioConfig
            config = ManimStudioConfig.from_dict(data)
            
            # Perform semantic validation
            semantic_result = config.validate_semantics()
            
            # Add semantic errors/warnings
            for error in semantic_result.errors:
                result.add_error(error.field, error.message, error.line)
            
            for warning in semantic_result.warnings:
                result.add_warning(warning.field, warning.message, warning.line)
                
        except ValidationError as e:
            # Convert Pydantic errors to our format
            for error in e.errors():
                field_path = '.'.join(str(loc) for loc in error['loc'])
                message = error['msg']
                
                # Make messages more user-friendly
                if 'enum' in error['type']:
                    allowed = error.get('ctx', {}).get('enum_values', [])
                    if allowed:
                        message = f"{message}. Allowed values: {', '.join(map(str, allowed))}"
                
                result.add_error(field_path, message)
        except Exception as e:
            result.add_error("validation", f"Unexpected validation error: {str(e)}")
    
    def validate_and_fix(
        self, 
        file_path: Union[str, Path]
    ) -> Tuple[ValidationResult, Optional[Dict[str, Any]]]:
        """Validate and attempt to fix common issues.
        
        Returns:
            Tuple of (validation_result, fixed_data)
        """
        result = self.validate_file(file_path, full_validation=False)
        
        if not result.valid:
            return result, None
        
        # Load data
        with open(file_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Apply fixes
        fixed_data = self._apply_common_fixes(data)
        
        # Re-validate
        try:
            config = ManimStudioConfig.from_dict(fixed_data)
            result = ValidationResult(valid=True)
            return result, fixed_data
        except ValidationError as e:
            # Return original validation result
            return self.validate_file(file_path), None
    
    def _apply_common_fixes(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Apply common fixes to YAML data."""
        import copy
        fixed = copy.deepcopy(data)
        
        # Ensure scene wrapper if needed
        if 'name' in fixed and 'scene' not in fixed:
            fixed = {'scene': fixed}
        
        scene = fixed.get('scene', {})
        
        # Fix common issues
        # 1. Add default duration if missing
        if 'duration' not in scene and 'animations' in scene:
            # Calculate from animations
            max_time = 0.0
            for anim in scene.get('animations', []):
                end_time = anim.get('start_time', 0) + anim.get('duration', 1)
                max_time = max(max_time, end_time)
            scene['duration'] = max_time + 1.0
        
        # 2. Add IDs to objects if missing
        if 'objects' in scene:
            for i, obj in enumerate(scene['objects']):
                if 'id' not in obj:
                    obj_type = obj.get('type', 'object')
                    obj['id'] = f"{obj_type}_{i}"
        
        # 3. Fix color formats
        def fix_color(color_value):
            if isinstance(color_value, str):
                # Add # if missing for hex colors
                if len(color_value) == 6 and all(c in '0123456789ABCDEFabcdef' for c in color_value):
                    return f"#{color_value}"
            return color_value
        
        # Apply color fixes
        for obj in scene.get('objects', []):
            if 'color' in obj:
                obj['color'] = fix_color(obj['color'])
            if 'fill_color' in obj:
                obj['fill_color'] = fix_color(obj['fill_color'])
        
        fixed['scene'] = scene
        return fixed
    
    def generate_report(
        self, 
        validation_result: ValidationResult,
        format: str = "text"
    ) -> str:
        """Generate a validation report.
        
        Args:
            validation_result: The validation result
            format: Output format ('text', 'markdown', 'json')
            
        Returns:
            Formatted report string
        """
        if format == "json":
            import json
            return json.dumps({
                "valid": validation_result.valid,
                "errors": [
                    {
                        "field": e.field,
                        "message": e.message,
                        "severity": e.severity,
                        "line": e.line
                    }
                    for e in validation_result.errors + validation_result.warnings
                ]
            }, indent=2)
        
        elif format == "markdown":
            lines = ["# YAML Validation Report\n"]
            
            if validation_result.valid:
                lines.append("✅ **Validation Passed**\n")
            else:
                lines.append("❌ **Validation Failed**\n")
            
            if validation_result.errors:
                lines.append("## Errors\n")
                for error in validation_result.errors:
                    line_info = f" (line {error.line})" if error.line else ""
                    lines.append(f"- **{error.field}**: {error.message}{line_info}")
                lines.append("")
            
            if validation_result.warnings:
                lines.append("## Warnings\n")
                for warning in validation_result.warnings:
                    line_info = f" (line {warning.line})" if warning.line else ""
                    lines.append(f"- **{warning.field}**: {warning.message}{line_info}")
            
            return "\n".join(lines)
        
        else:  # text format
            lines = []
            
            if validation_result.valid:
                lines.append("✅ Validation Passed")
            else:
                lines.append("❌ Validation Failed")
            
            if validation_result.errors:
                lines.append("\nErrors:")
                for error in validation_result.errors:
                    line_info = f" (line {error.line})" if error.line else ""
                    lines.append(f"  - {error.field}: {error.message}{line_info}")
            
            if validation_result.warnings:
                lines.append("\nWarnings:")
                for warning in validation_result.warnings:
                    line_info = f" (line {warning.line})" if warning.line else ""
                    lines.append(f"  - {warning.field}: {warning.message}{line_info}")
            
            return "\n".join(lines)


# Example usage
if __name__ == "__main__":
    validator = EnhancedYamlValidator()
    
    # Example validation
    result = validator.validate_file("example_scene.yaml")
    print(validator.generate_report(result, format="text"))
    
    # Try to fix and validate
    result, fixed_data = validator.validate_and_fix("example_scene.yaml")
    if fixed_data:
        print("\n✨ Fixed YAML data available")
        # Save fixed version
        with open("example_scene_fixed.yaml", 'w') as f:
            yaml.dump(fixed_data, f, sort_keys=False)
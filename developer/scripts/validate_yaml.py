#!/usr/bin/env python3
"""
Standalone YAML validation script for Manim Studio.

Usage:
    python validate_yaml.py <file.yaml> [--verbose]
    python validate_yaml.py --help
"""

import sys
import argparse
from pathlib import Path

# Add src to path so we can import our modules
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.yaml_validator import validate_yaml_file

def main():
    """Main entry point for standalone YAML validation."""
    parser = argparse.ArgumentParser(
        description="Validate YAML scene files for Manim Studio",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python validate_yaml.py scenes/my_scene.yaml
  python validate_yaml.py scenes/my_scene.yaml --verbose
  python validate_yaml.py scenes/*.yaml --verbose

Exit codes:
  0 - All files are valid
  1 - One or more files have validation errors
  2 - Script error (file not found, etc.)
        """
    )
    
    parser.add_argument(
        "files",
        nargs="+",
        help="YAML files to validate (supports glob patterns)"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed validation results (warnings and info)"
    )
    
    args = parser.parse_args()
    
    # Expand glob patterns and collect all files
    files_to_validate = []
    for file_pattern in args.files:
        if "*" in file_pattern or "?" in file_pattern:
            # Handle glob patterns
            pattern_path = Path(file_pattern)
            if pattern_path.is_absolute():
                matches = Path("/").glob(str(pattern_path).lstrip("/"))
            else:
                matches = Path(".").glob(file_pattern)
            files_to_validate.extend(matches)
        else:
            files_to_validate.append(Path(file_pattern))
    
    if not files_to_validate:
        print("❌ No files found to validate")
        return 2
    
    # Validate each file
    all_valid = True
    total_files = len(files_to_validate)
    
    print(f"🔍 Validating {total_files} YAML file{'s' if total_files != 1 else ''}...\n")
    
    for file_path in files_to_validate:
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            all_valid = False
            continue
        
        if file_path.suffix.lower() not in ['.yaml', '.yml']:
            print(f"⚠️  Skipping non-YAML file: {file_path}")
            continue
        
        try:
            is_valid = validate_yaml_file(str(file_path), verbose=args.verbose)
            if not is_valid:
                all_valid = False
        except Exception as e:
            print(f"❌ Error validating {file_path}: {e}")
            all_valid = False
    
    # Summary
    print("\n" + "="*50)
    if all_valid:
        print("✅ All files passed validation!")
        return 0
    else:
        print("❌ Some files failed validation")
        return 1

if __name__ == "__main__":
    sys.exit(main())
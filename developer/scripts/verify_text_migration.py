#!/usr/bin/env python3
"""
Verification script to check TextManager migration status
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


def find_direct_text_usage(directory: Path) -> Dict[str, List[Tuple[int, str]]]:
    """Find all direct text creation patterns in Python files"""
    
    patterns = [
        r'\bText\s*\(',           # Text(
        r'\bMathTex\s*\(',        # MathTex(
        r'\bTex\s*\(',            # Tex(
        r'\bMarkupText\s*\(',     # MarkupText(
        r'\.to_edge\s*\(',        # .to_edge( - positioning that should use layouts
        r'\.set_color\s*\(',      # .set_color( - styling that should use styles
        r'\.scale\s*\(',          # .scale( - sizing that should be in styles
        r'add_fixed_in_frame_mobjects.*Text' # 3D text handling
    ]
    
    # Compile patterns
    compiled_patterns = [re.compile(pattern) for pattern in patterns]
    pattern_names = [
        'Text()', 'MathTex()', 'Tex()', 'MarkupText()',
        '.to_edge()', '.set_color()', '.scale()', '3D text'
    ]
    
    results = {}
    
    # Search through all Python files
    for py_file in directory.rglob('*.py'):
        # Skip certain files
        if any(skip in str(py_file) for skip in [
            '__pycache__', 
            '.git', 
            'venv', 
            'text_manager.py',  # TextManager itself is allowed to use Text()
            'text_policy.py',   # Policy file references are allowed
            'verify_text_migration.py'  # This script
        ]):
            continue
            
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            file_issues = []
            
            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()
                
                # Skip comments
                if line_stripped.startswith('#'):
                    continue
                    
                # Skip docstrings (basic detection)
                if '"""' in line or "'''" in line:
                    continue
                
                # Check each pattern
                for pattern, name in zip(compiled_patterns, pattern_names):
                    if pattern.search(line):
                        file_issues.append((line_num, f"{name}: {line_stripped}"))
                        
            if file_issues:
                results[str(py_file.relative_to(directory))] = file_issues
                
        except Exception as e:
            print(f"Error reading {py_file}: {e}")
            
    return results


def generate_migration_report(results: Dict[str, List[Tuple[int, str]]]) -> str:
    """Generate a migration status report"""
    
    if not results:
        return "✅ **ALL TEXT MIGRATION COMPLETE!** ✅\n\nNo direct text usage found. All text is properly managed through TextManager."
    
    report = "📋 **TEXT MIGRATION STATUS REPORT** 📋\n\n"
    
    # Summary
    total_files = len(results)
    total_issues = sum(len(issues) for issues in results.values())
    
    report += f"**Summary:**\n"
    report += f"- Files needing migration: {total_files}\n"
    report += f"- Total issues found: {total_issues}\n\n"
    
    # Priority categories
    high_priority = []
    medium_priority = []
    low_priority = []
    
    for file_path, issues in results.items():
        if any(key in file_path for key in ['src/scenes/', 'src/components/', 'examples/']):
            high_priority.append((file_path, issues))
        elif 'developer/examples/' in file_path or 'developer/tests/' in file_path:
            medium_priority.append((file_path, issues))
        else:
            low_priority.append((file_path, issues))
    
    # High priority section
    if high_priority:
        report += "## 🚨 HIGH PRIORITY (Critical)\n\n"
        for file_path, issues in high_priority:
            report += f"**{file_path}**\n"
            for line_num, issue in issues[:5]:  # Limit to first 5 issues per file
                report += f"  - Line {line_num}: {issue}\n"
            if len(issues) > 5:
                report += f"  - ... and {len(issues) - 5} more issues\n"
            report += "\n"
    
    # Medium priority section  
    if medium_priority:
        report += "## ⚠️  MEDIUM PRIORITY\n\n"
        for file_path, issues in medium_priority:
            report += f"**{file_path}** ({len(issues)} issues)\n"
        report += "\n"
    
    # Low priority section
    if low_priority:
        report += "## ℹ️  LOW PRIORITY\n\n"
        for file_path, issues in low_priority:
            report += f"**{file_path}** ({len(issues)} issues)\n"
        report += "\n"
    
    # Migration instructions
    report += "## 🔧 Next Steps\n\n"
    report += "1. **High Priority**: Update core scene and component files immediately\n"
    report += "2. **Medium Priority**: Update example and test files as needed\n" 
    report += "3. **Low Priority**: Update remaining files during normal development\n\n"
    report += "**See `src/core/TEXT_MIGRATION_GUIDE.md` for detailed migration instructions.**\n"
    
    return report


def main():
    """Main verification function"""
    print("🔍 Scanning codebase for direct text usage...")
    
    # Get project root
    project_root = Path(__file__).parent.parent.parent
    
    # Find direct text usage
    results = find_direct_text_usage(project_root)
    
    # Generate report
    report = generate_migration_report(results)
    
    # Print to console
    print("\n" + "="*60)
    print(report)
    print("="*60)
    
    # Save report to file
    report_file = project_root / "TEXT_MIGRATION_STATUS.md"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Full report saved to: {report_file}")
    
    # Return exit code
    return 0 if not results else 1


if __name__ == "__main__":
    exit(main())
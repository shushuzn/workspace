#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Workspace Path Fixer - Fix hardcoded workspace paths
Replace D:\OpenClaw\workspace with Path(__file__).parent.parent
"""

import os
import re
from pathlib import Path
import sys

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def fix_workspace_paths():
    """Fix all hardcoded workspace paths in 30-scripts-tools"""
    print("=" * 80)
    print("Workspace Path Fixer - Batch Fix D:\\OpenClaw\\workspace")
    print("=" * 80)
    
    tools_dir = Path('30-scripts-tools')
    py_files = list(tools_dir.rglob('*.py'))
    
    print(f"\nScanning {len(py_files)} Python files...")
    
    fixed_count = 0
    backup_count = 0
    
    # Patterns to match
    patterns = [
        # str(Path(__file__).parent.parent)
        (r'Path\(r["\']D:\\\\OpenClaw\\\\workspace["\']\)', 'Path(__file__).parent.parent'),
        (r'r["\']D:\\\\OpenClaw\\\\workspace["\']', 'str(Path(__file__).parent.parent)'),
        # str(Path(__file__).parent.parent)
        (r'Path\(["\']D:\\\\OpenClaw\\\\workspace["\']\)', 'Path(__file__).parent.parent'),
        (r'["\']D:\\\\OpenClaw\\\\workspace["\']', 'str(Path(__file__).parent.parent)'),
        # str(Path(__file__).parent.parent) (single backslash in raw string)
        (r'Path\(r["\']D:\\OpenClaw\\workspace["\']\)', 'Path(__file__).parent.parent'),
        (r'r["\']D:\\OpenClaw\\workspace["\']', 'str(Path(__file__).parent.parent)'),
    ]
    
    fixed_files = []
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            fixes_made = 0
            
            # Check if file contains workspace path
            if str(Path(__file__).parent.parent) not in content and 'D:\\\\OpenClaw\\\\workspace' not in content:
                continue
            
            # Apply fixes
            for pattern, replacement in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    fixes_made += len(matches)
            
            # Add pathlib import if needed
            if fixes_made > 0:
                if 'from pathlib import Path' not in content and 'import pathlib' not in content:
                    # Add at beginning
                    content = 'from pathlib import Path\n' + content
                
                # Create backup
                backup_dir = Path('security_backups')
                backup_dir.mkdir(exist_ok=True)
                backup_path = backup_dir / f"{py_file.name}.bak"
                
                import shutil
                shutil.copy2(py_file, backup_path)
                backup_count += 1
                
                # Save fixed file
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed_count += 1
                fixed_files.append((py_file, fixes_made))
                print(f"✓ {py_file} ({fixes_made} fixes)")
                
        except Exception as e:
            print(f"✗ Error fixing {py_file}: {e}")
    
    print("\n" + "=" * 80)
    print(f"Files fixed: {fixed_count}")
    print(f"Backups created: {backup_count}")
    print(f"Total path replacements: {sum(f[1] for f in fixed_files)}")
    print("=" * 80)
    
    # Generate report
    if fixed_files:
        report = f"""# Workspace Path Fix Report

Generated: {Path.cwd()}

## Summary
- Files Fixed: {fixed_count}
- Backups: security_backups/
- Pattern: D:\\OpenClaw\\workspace → Path(__file__).parent.parent

## Files Modified
"""
        for file_path, fixes in fixed_files[:50]:
            report += f"- `{file_path}` ({fixes})\n"
        if len(fixed_files) > 50:
            report += f"- ... and {len(fixed_files) - 50} more\n"
        
        report_file = Path('data/workspace_path_fix_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")

if __name__ == "__main__":
    fix_workspace_paths()

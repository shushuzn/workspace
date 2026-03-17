#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Quick Security Fix - Batch fix remaining issues
Focus on high-priority files in 30-scripts-tools
"""

import os
import re
from pathlib import Path
import sys

# UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def quick_fix_paths():
    """Quick fix for common path patterns"""
    print("=" * 80)
    print("Quick Security Fix - Remaining Path Issues")
    print("=" * 80)
    
    # Scan 30-scripts-tools directory
    tools_dir = Path('30-scripts-tools')
    py_files = list(tools_dir.rglob('*.py'))
    
    # Skip intentkit and other submodules
    skip_dirs = ['intentkit', 'github-sync', 'github_repo', 'cnt-research']
    py_files = [f for f in py_files if not any(s in str(f) for s in skip_dirs)]
    
    print(f"\nScanning {len(py_files)} Python files...")
    
    fixed = 0
    total_fixes = 0
    
    # Patterns to fix
    patterns = [
        # Workspace path variations
        (r'["\']D:\\\\OpenClaw\\\\workspace["\']', 'str(Path(__file__).parent.parent)'),
        (r'["\']D:\\OpenClaw\\workspace["\']', 'str(Path(__file__).parent.parent)'),
        (r'r["\']D:\\\\OpenClaw\\\\workspace["\']', 'str(Path(__file__).parent.parent)'),
        (r'r["\']D:\\OpenClaw\\workspace["\']', 'str(Path(__file__).parent.parent)'),
        # IP addresses (example)
        (r'["\']8\.208\.30\.28["\']', 'os.getenv("HOST_IP", os.getenv("HOST_IP", "8.208.30.28"))'),
    ]
    
    for py_file in py_files:
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            file_fixes = 0
            
            for pattern, replacement in patterns:
                if re.search(pattern, content):
                    content = re.sub(pattern, replacement, content)
                    file_fixes += len(re.findall(pattern, original))
            
            # Add imports if needed
            if file_fixes > 0:
                needs_pathlib = 'Path(__file__)' in content and 'from pathlib import Path' not in content
                needs_os = 'os.getenv' in content and 'import os' not in content
                
                if needs_pathlib or needs_os:
                    # Find import section
                    lines = content.split('\n')
                    import_lines = []
                    for i, line in enumerate(lines):
                        if line.startswith('import ') or line.startswith('from '):
                            import_lines.append(i)
                    
                    # Add imports after existing imports
                    if import_lines:
                        insert_pos = import_lines[-1] + 1
                        if needs_pathlib:
                            lines.insert(insert_pos, 'from pathlib import Path')
                            insert_pos += 1
                        if needs_os:
                            lines.insert(insert_pos, 'import os')
                        content = '\n'.join(lines)
                    else:
                        # Add at beginning
                        prefix = []
                        if needs_pathlib:
                            prefix.append('from pathlib import Path')
                        if needs_os:
                            prefix.append('import os')
                        content = '\n'.join(prefix) + '\n' + content
                
                # Save
                with open(py_file, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                fixed += 1
                total_fixes += file_fixes
                
                if fixed % 10 == 1:
                    print(f"[{fixed}] {py_file} ({file_fixes} fixes)")
                    
        except Exception as e:
            pass
    
    print("\n" + "=" * 80)
    print(f"Files Fixed: {fixed}")
    print(f"Total Fixes: {total_fixes}")
    print("=" * 80)

if __name__ == "__main__":
    quick_fix_paths()

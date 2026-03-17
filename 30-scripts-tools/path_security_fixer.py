#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Path Security Fixer - Fix hardcoded absolute paths
Specialized tool for hardcoded_path vulnerabilities (749 occurrences)
"""

import os
import re
import shutil
from datetime import datetime
from pathlib import Path
import sys

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class PathFixer:
    """Fix hardcoded absolute paths"""
    
    def __init__(self, backup_dir: str = "security_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.fix_count = 0
        
    def backup_file(self, file_path: str) -> str:
        """Create backup"""
        src = Path(file_path)
        if not src.exists():
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{src.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(src, backup_path)
        return str(backup_path)
    
    def is_safe_to_fix(self, path: str) -> bool:
        """Check if path is safe to fix"""
        # Don't fix system paths
        unsafe_patterns = [
            'python', 'program files', 'windows', 'system32',
            'appdata', 'programdata', 'users\\'
        ]
        path_lower = path.lower()
        return not any(p in path_lower for p in unsafe_patterns)
    
    def extract_relative_path(self, abs_path: str) -> str:
        """Extract filename or relative path from absolute path"""
        # Get the last meaningful part
        parts = abs_path.replace('\\', '/').split('/')
        
        # Find workspace-relative path
        for i, part in enumerate(parts):
            if part == 'OpenClaw' and i + 1 < len(parts):
                return '/'.join(parts[i+1:])
        
        # Just use filename
        return parts[-1]
    
    def fix_paths_in_file(self, file_path: str) -> int:
        """Fix all hardcoded paths in a file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            fixes_made = 0
            
            # Pattern for Windows absolute paths
            pattern = r'r?["\']([D-Z]:\\[^"\']+ )["\']'
            
            matches = list(re.finditer(pattern, content))
            
            # Add pathlib import if needed
            needs_pathlib = False
            
            for match in reversed(matches):  # Process in reverse to maintain positions
                abs_path = match.group(1)
                
                if not self.is_safe_to_fix(abs_path):
                    continue
                
                # Get relative path
                rel_path = self.extract_relative_path(abs_path)
                
                # Create replacement
                if '/' in rel_path:
                    new_code = f'Path(__file__).parent / "{rel_path}"'
                else:
                    new_code = f'Path(__file__).parent / "{rel_path}"'
                
                needs_pathlib = True
                
                # Replace (handle raw strings)
                old_match = match.group(0)
                if old_match.startswith('r'):
                    new_code = f'Path(__file__).parent / "{rel_path}"'
                
                content = content[:match.start()] + new_code + content[match.end():]
                fixes_made += 1
                self.fix_count += 1
            
            # Add pathlib import if needed and not present
            if needs_pathlib and fixes_made > 0:
                if 'from pathlib import Path' not in content and 'import pathlib' not in content:
                    # Add after existing imports
                    import_match = re.search(r'^(import .+|from .+ import .+)', content, re.MULTILINE)
                    if import_match:
                        insert_pos = import_match.end()
                        content = content[:insert_pos] + '\nfrom pathlib import Path' + content[insert_pos:]
                    else:
                        content = 'from pathlib import Path\n' + content
            
            # Save if changed
            if content != original_content:
                self.backup_file(file_path)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
            
            return fixes_made
            
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return 0
    
    def fix_directory(self, dir_path: str, max_files: int = 100):
        """Fix all Python files in directory"""
        print("=" * 80)
        print("Path Security Fixer - Hardcoded Path Remediation")
        print("=" * 80)
        
        dir_path = Path(dir_path)
        py_files = list(dir_path.rglob('*.py'))
        
        print(f"\nFound {len(py_files)} Python files")
        print(f"Processing up to {max_files} files...")
        
        fixed_files = []
        
        for i, py_file in enumerate(py_files[:max_files]):
            fixes = self.fix_paths_in_file(str(py_file))
            if fixes > 0:
                fixed_files.append((py_file, fixes))
                print(f"[{len(fixed_files)}] ✓ {py_file} ({fixes} fixes)")
        
        print("\n" + "=" * 80)
        print(f"Files fixed: {len(fixed_files)}")
        print(f"Total path fixes: {self.fix_count}")
        print("=" * 80)
        
        # Generate report
        if fixed_files:
            self.generate_report(fixed_files)
    
    def generate_report(self, fixed_files):
        """Generate fix report"""
        report = f"""# Path Security Fix Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Files Fixed:** {len(fixed_files)}
- **Total Path Fixes:** {self.fix_count}
- **Backups:** security_backups/

## Files Modified

"""
        for file_path, fixes in fixed_files:
            report += f"- `{file_path}` ({fixes} paths)\n"
        
        report += """
## Testing Required

1. Run affected scripts to ensure paths work correctly
2. Check file operations still function
3. Verify no broken imports

## Rollback

```bash
cp security_backups/<file>.bak <original_path>
```
"""
        report_file = Path('data/path_fix_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Path Security Fixer")
    parser.add_argument("--dir", type=str, default="30-scripts-tools",
                       help="Directory to fix")
    parser.add_argument("--max", type=int, default=100,
                       help="Max files to process")
    
    args = parser.parse_args()
    
    fixer = PathFixer()
    fixer.fix_directory(args.dir, args.max)

if __name__ == "__main__":
    main()

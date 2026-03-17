#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Complete Security Path Fixer - Fix all hardcoded paths in workspace
Comprehensive fix for all Python files
"""

import os
import re
import shutil
from pathlib import Path
from datetime import datetime
import sys

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class CompletePathFixer:
    """Fix all hardcoded paths in workspace"""
    
    def __init__(self, backup_dir: str = "security_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.fix_count = 0
        self.backup_count = 0
        self.files_fixed = []
        
    def backup_file(self, file_path: str) -> str:
        """Create backup"""
        src = Path(file_path)
        if not src.exists():
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{src.stem}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(src, backup_path)
        self.backup_count += 1
        return str(backup_path)
    
    def is_safe_to_fix(self, path: str) -> bool:
        """Check if path is safe to fix"""
        unsafe = ['python', 'program files', 'windows', 'system32', 'appdata']
        return not any(p in path.lower() for p in unsafe)
    
    def fix_file(self, file_path: str) -> int:
        """Fix all hardcoded paths in file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            fixes = 0
            
            # Pattern 1: D:\OpenClaw\workspace (various escaping)
            patterns = [
                (r'Path\(r["\']D:\\\\OpenClaw\\\\workspace["\']\)', 'Path(__file__).parent.parent'),
                (r'r["\']D:\\\\OpenClaw\\\\workspace["\']', 'str(Path(__file__).parent.parent)'),
                (r'Path\(r["\']D:\\OpenClaw\\workspace["\']\)', 'Path(__file__).parent.parent'),
                (r'r["\']D:\\OpenClaw\\workspace["\']', 'str(Path(__file__).parent.parent)'),
                (r'["\']D:\\\\OpenClaw\\\\workspace["\']', 'str(Path(__file__).parent.parent)'),
                (r'["\']D:\\OpenClaw\\workspace["\']', 'str(Path(__file__).parent.parent)'),
            ]
            
            for pattern, replacement in patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    fixes += len(matches)
            
            # Add pathlib import if needed
            if fixes > 0:
                if 'from pathlib import Path' not in content and 'import pathlib' not in content:
                    content = 'from pathlib import Path\n' + content
                
                # Backup and save
                self.backup_file(str(file_path))
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.fix_count += fixes
                self.files_fixed.append((file_path, fixes))
            
            return fixes
            
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return 0
    
    def fix_all(self, root_dir: str = ".", max_files: int = 500):
        """Fix all Python files in directory tree"""
        from datetime import datetime
        
        print("=" * 80)
        print("Complete Security Path Fixer - Workspace-Wide Fix")
        print("=" * 80)
        
        root = Path(root_dir)
        
        # Directories to skip
        skip_dirs = {
            'node_modules', '__pycache__', '.git', 'venv', 'env',
            'intentkit', 'github-sync', 'github_repo', 'cnt-research',
            '40-50 多媒体资源库', '06-research'
        }
        
        py_files = []
        for py_file in root.rglob('*.py'):
            # Skip certain directories
            if any(skip in str(py_file) for skip in skip_dirs):
                continue
            py_files.append(py_file)
        
        print(f"\nFound {len(py_files)} Python files to scan")
        print(f"Max files to process: {max_files}")
        
        for i, py_file in enumerate(py_files[:max_files]):
            fixes = self.fix_file(py_file)
            if fixes > 0 and len(self.files_fixed) % 20 == 1:
                print(f"[{len(self.files_fixed)}] {py_file} ({fixes} fixes)")
        
        # Summary
        print("\n" + "=" * 80)
        print(f"Files Fixed: {len(self.files_fixed)}")
        print(f"Total Path Replacements: {self.fix_count}")
        print(f"Backups Created: {self.backup_count}")
        print("=" * 80)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate comprehensive fix report"""
        from datetime import datetime
        
        report = f"""# Complete Security Path Fix Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Files Fixed:** {len(self.files_fixed)}
- **Total Path Replacements:** {self.fix_count}
- **Backups Created:** {self.backup_count}
- **Backup Location:** security_backups/

## Files Modified

"""
        for file_path, fixes in sorted(self.files_fixed, key=lambda x: x[1], reverse=True)[:50]:
            report += f"- `{file_path}` ({fixes} paths)\n"
        
        if len(self.files_fixed) > 50:
            report += f"\n... and {len(self.files_fixed) - 50} more files\n"
        
        report += """
## Rollback

```bash
cp security_backups/<backup_file> <original_path>
```

## Testing

Run affected scripts to verify paths work correctly:
```bash
python <script>.py --help
```
"""
        report_file = Path('data/complete_path_fix_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Complete Security Path Fixer")
    parser.add_argument("--dir", type=str, default=".", help="Root directory")
    parser.add_argument("--max", type=int, default=500, help="Max files")
    args = parser.parse_args()
    
    fixer = CompletePathFixer()
    fixer.fix_all(args.dir, args.max)

if __name__ == "__main__":
    main()

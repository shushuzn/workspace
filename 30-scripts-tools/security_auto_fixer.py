#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Auto-Fixer - Automated security vulnerability remediation
Part of Security Audit Automation System (BRAIN-011)

Features:
- Auto-fix hardcoded secrets → environment variables
- Auto-fix hardcoded paths → pathlib relative paths
- Auto-fix hardcoded IPs → configuration files
- Backup before fix
- Generate .env template
- Audit trail
"""

import os
import re
import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import sys

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class SecurityFixer:
    """Automated security vulnerability fixer"""
    
    def __init__(self, backup_dir: str = "security_backups"):
        self.backup_dir = Path(backup_dir)
        self.backup_dir.mkdir(exist_ok=True)
        self.fix_count = 0
        self.backup_count = 0
        self.fix_log = []
        
    def backup_file(self, file_path: str) -> str:
        """Create backup of file before fixing"""
        src = Path(file_path)
        if not src.exists():
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{src.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(src, backup_path)
        self.backup_count += 1
        return str(backup_path)
    
    def fix_hardcoded_secrets(self, content: str, file_path: str) -> Tuple[str, List[Dict]]:
        """Replace hardcoded secrets with environment variables"""
        fixes = []
        
        # Patterns for common secrets
        patterns = [
            (r'(api_key|apikey|API_KEY|api_secret)\s*=\s*["\']([^"\']{8,})["\']', 'API_KEY'),
            (r'(password|passwd|PASSWORD|pwd)\s*=\s*["\']([^"\']{4,})["\']', 'PASSWORD'),
            (r'(secret|SECRET|secret_key)\s*=\s*["\']([^"\']{8,})["\']', 'SECRET'),
            (r'(token|TOKEN|auth_token)\s*=\s*["\']([^"\']{8,})["\']', 'TOKEN'),
            (r'(private_key|PRIVATE_KEY)\s*=\s*["\']([^"\']{20,})["\']', 'PRIVATE_KEY'),
        ]
        
        for pattern, env_name in patterns:
            matches = list(re.finditer(pattern, content, re.IGNORECASE))
            for match in matches:
                old_value = match.group(0)
                # Generate env var name from file path
                file_base = Path(file_path).stem.upper().replace('-', '_').replace('.', '_')
                var_name = f"{file_base}_{env_name}"
                new_value = f'{env_name} = os.getenv("{var_name}")'
                
                content = content.replace(old_value, new_value, 1)
                fixes.append({
                    'type': 'hardcoded_secret',
                    'line': content[:match.start()].count('\n') + 1,
                    'old': old_value[:50] + '...',
                    'new': new_value
                })
                self.fix_count += 1
        
        return content, fixes
    
    def fix_hardcoded_paths(self, content: str, file_path: str) -> Tuple[str, List[Dict]]:
        """Replace hardcoded absolute paths with pathlib relative paths"""
        fixes = []
        
        # Pattern for Windows absolute paths
        path_pattern = r'["\']([D-Z]:\\[^"\']+ )["\']'
        
        matches = list(re.finditer(path_pattern, content))
        for match in matches:
            old_path = match.group(1)
            
            # Skip common non-sensitive paths
            if any(skip in old_path.lower() for skip in ['python', 'program files', 'windows']):
                continue
            
            # Convert to pathlib
            relative_path = old_path.replace('\\', '/').split('/')[-1]
            new_code = f'str(Path(__file__).parent / "{relative_path}")'
            
            # Add pathlib import if not present
            if 'from pathlib import Path' not in content and 'import pathlib' not in content:
                content = 'from pathlib import Path\n' + content
            
            old_code = f'"{old_path}"'
            content = content.replace(old_code, new_code, 1)
            
            fixes.append({
                'type': 'hardcoded_path',
                'line': content[:match.start()].count('\n') + 1,
                'old': old_path[:60] + '...',
                'new': new_code
            })
            self.fix_count += 1
        
        return content, fixes
    
    def fix_hardcoded_ips(self, content: str, file_path: str) -> Tuple[str, List[Dict]]:
        """Replace hardcoded IP addresses with config variables"""
        fixes = []
        
        # Pattern for IP addresses
        ip_pattern = r'["\'](\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})["\']'
        
        matches = list(re.finditer(ip_pattern, content))
        for match in matches:
            ip = match.group(1)
            
            # Skip localhost
            if ip.startswith('127.') or ip == '0.0.0.0':
                continue
            
            var_name = f'HOST_IP_{ip.replace(".", "_")}'
            new_code = f'os.getenv("{var_name}", "{ip}")'
            
            old_code = f'"{ip}"'
            content = content.replace(old_code, new_code, 1)
            
            fixes.append({
                'type': 'hardcoded_ip',
                'line': content[:match.start()].count('\n') + 1,
                'old': ip,
                'new': new_code
            })
            self.fix_count += 1
        
        return content, fixes
    
    def generate_env_template(self, all_fixes: Dict[str, List[Dict]]) -> str:
        """Generate .env template from all fixes"""
        env_lines = [
            "# Auto-generated .env file",
            "# DO NOT COMMIT THIS FILE TO GIT",
            "# Generated by Security Auto-Fixer",
            f"# Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "# Secrets (replace with actual values)",
        ]
        
        # Collect all unique env vars
        env_vars = set()
        for file_path, fixes in all_fixes.items():
            for fix in fixes:
                if fix['type'] == 'hardcoded_secret':
                    # Extract var name from new value
                    match = re.search(r'os\.getenv\("([^"]+)"\)', fix['new'])
                    if match:
                        env_vars.add(match.group(1))
                elif fix['type'] == 'hardcoded_ip':
                    match = re.search(r'os\.getenv\("([^"]+)"', fix['new'])
                    if match:
                        env_vars.add(f"{match.group(1)}={fix['old']}")
        
        for var in sorted(env_vars):
            if '=' in var:
                env_lines.append(var)
            else:
                env_lines.append(f"{var}=")
        
        return '\n'.join(env_lines)
    
    def fix_file(self, file_path: str, scan_data: Dict) -> Dict[str, Any]:
        """Fix all security issues in a single file"""
        result = {
            'file': file_path,
            'fixed': False,
            'backup': None,
            'fixes': [],
            'errors': []
        }
        
        try:
            # Read file
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            content = original_content
            file_fixes = []
            
            # Apply fixes
            content, secret_fixes = self.fix_hardcoded_secrets(content, file_path)
            file_fixes.extend(secret_fixes)
            
            content, path_fixes = self.fix_hardcoded_paths(content, file_path)
            file_fixes.extend(path_fixes)
            
            content, ip_fixes = self.fix_hardcoded_ips(content, file_path)
            file_fixes.extend(ip_fixes)
            
            # If changes were made, backup and save
            if content != original_content:
                # Backup
                backup_path = self.backup_file(file_path)
                result['backup'] = backup_path
                
                # Save fixed content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                result['fixed'] = True
                result['fixes'] = file_fixes
            
            self.fix_log.append(result)
            return result
            
        except Exception as e:
            result['errors'].append(str(e))
            self.fix_log.append(result)
            return result
    
    def run_batch_fix(self, scan_file: str, max_files: int = 50):
        """Run batch fix on all affected files"""
        print("=" * 80)
        print("Security Auto-Fixer - Batch Remediation")
        print("=" * 80)
        
        # Load scan data
        print(f"\nLoading scan data from: {scan_file}")
        with open(scan_file, 'r', encoding='utf-8') as f:
            scan_data = json.load(f)
        
        # Get affected files
        issues = scan_data.get('findings', []) or scan_data.get('issues', [])
        
        # Group by file
        files_to_fix = {}
        for issue in issues:
            file_path = issue.get('file', '')
            if file_path and os.path.exists(file_path):
                if file_path not in files_to_fix:
                    files_to_fix[file_path] = []
                files_to_fix[file_path].append(issue)
        
        print(f"Files to fix: {len(files_to_fix)}")
        print(f"Max files to process: {max_files}")
        
        # Fix files
        all_fixes = {}
        for i, file_path in enumerate(list(files_to_fix.keys())[:max_files]):
            print(f"\n[{i+1}/{min(len(files_to_fix), max_files)}] Fixing: {file_path}")
            result = self.fix_file(file_path, scan_data)
            all_fixes[file_path] = result['fixes']
            
            if result['fixed']:
                print(f"  ✓ Fixed {len(result['fixes'])} issues")
                print(f"  ✓ Backup: {result['backup']}")
            elif result['errors']:
                print(f"  ✗ Errors: {result['errors']}")
            else:
                print(f"  - No changes needed")
        
        # Generate .env template
        print("\nGenerating .env template...")
        env_content = self.generate_env_template(all_fixes)
        env_file = Path('.env.auto')
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(env_content)
        print(f"✓ .env template saved to: {env_file}")
        
        # Generate fix report
        print("\nGenerating fix report...")
        report = self.generate_fix_report(all_fixes)
        report_file = Path('data/security_fix_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"✓ Fix report saved to: {report_file}")
        
        # Summary
        print("\n" + "=" * 80)
        print("Fix Summary")
        print("=" * 80)
        print(f"Files processed: {len(files_to_fix)}")
        print(f"Files fixed: {sum(1 for r in self.fix_log if r['fixed'])}")
        print(f"Total fixes: {self.fix_count}")
        print(f"Backups created: {self.backup_count}")
        print("=" * 80)
    
    def generate_fix_report(self, all_fixes: Dict[str, List[Dict]]) -> str:
        """Generate comprehensive fix report"""
        report = f"""# Security Auto-Fix Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Files Processed:** {len(all_fixes)}
- **Total Fixes Applied:** {self.fix_count}
- **Backups Created:** {self.backup_count}

## Fixes by Type

"""
        # Count by type
        type_counts = {}
        for fixes in all_fixes.values():
            for fix in fixes:
                fix_type = fix.get('type', 'unknown')
                type_counts[fix_type] = type_counts.get(fix_type, 0) + 1
        
        for fix_type, count in sorted(type_counts.items(), key=lambda x: x[1], reverse=True):
            report += f"- **{fix_type}:** {count}\n"
        
        report += "\n## Files Fixed\n\n"
        
        for file_path, fixes in all_fixes.items():
            if fixes:
                report += f"### `{file_path}`\n\n"
                report += f"**Fixes:** {len(fixes)}\n\n"
                for fix in fixes[:5]:  # Show first 5
                    report += f"- Line {fix['line']}: {fix['type']} → {fix['new'][:50]}...\n"
                if len(fixes) > 5:
                    report += f"- ... and {len(fixes) - 5} more\n"
                report += "\n"
        
        report += """
## Next Steps

1. **Review all changes** - Use `git diff` to review
2. **Test thoroughly** - Run test suite
3. **Update .env** - Fill in actual secret values
4. **Add .env to .gitignore** - Prevent accidental commits
5. **Rotate exposed secrets** - Change all hardcoded secrets
6. **Commit changes** - `git commit -m "🛡️ Security fixes"`

## Rollback

If needed, restore from backups in `security_backups/` directory:
```bash
cp security_backups/<file>.bak <original_path>
```
"""
        return report

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Security Auto-Fixer")
    parser.add_argument("--scan", type=str, default="data/security_scan_report.json",
                       help="Scan results JSON file")
    parser.add_argument("--max", type=int, default=50,
                       help="Max files to fix (default: 50)")
    parser.add_argument("--dry-run", action="store_true",
                       help="Show what would be fixed without making changes")
    
    args = parser.parse_args()
    
    fixer = SecurityFixer()
    
    if args.dry_run:
        print("DRY RUN MODE - No changes will be made")
        # Just show what would be fixed
        with open(args.scan, 'r', encoding='utf-8') as f:
            scan_data = json.load(f)
        
        issues = scan_data.get('findings', [])
        files = set(i.get('file', '') for i in issues if i.get('file'))
        print(f"\nWould fix {len(files)} files:")
        for f in list(files)[:20]:
            print(f"  - {f}")
        if len(files) > 20:
            print(f"  ... and {len(files) - 20} more")
    else:
        fixer.run_batch_fix(args.scan, args.max)

if __name__ == "__main__":
    main()

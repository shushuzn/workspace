#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Batch Security Fixer - Fix top files with security issues
Priority: hardcoded_path, password, ip_address
"""

import os
import re
from pathlib import Path
from datetime import datetime
import sys

# UTF-8 encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

class BatchSecurityFixer:
    """Batch fix security issues in priority files"""
    
    def __init__(self):
        self.backup_dir = Path('security_backups')
        self.backup_dir.mkdir(exist_ok=True)
        self.files_fixed = []
        self.total_fixes = 0
        self.backup_count = 0
        
    def backup_file(self, file_path: str) -> str:
        """Create timestamped backup"""
        src = Path(file_path)
        if not src.exists():
            return None
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{src.stem}_{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        try:
            import shutil
            shutil.copy2(src, backup_path)
            self.backup_count += 1
            return str(backup_path)
        except Exception as e:
            return None
    
    def fix_file(self, file_path: str) -> int:
        """Fix all security issues in file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original = content
            fixes = 0
            needs_pathlib = False
            needs_os = False
            
            # Fix 1: Hardcoded workspace paths (various patterns)
            path_patterns = [
                # Double escaped (JSON strings in Python)
                (r'["\']D:\\\\OpenClaw\\\\workspace["\']', 'str(Path(__file__).parent.parent)'),
                (r'r["\']D:\\\\OpenClaw\\\\workspace["\']', 'str(Path(__file__).parent.parent)'),
                # Single escaped
                (r'["\']D:\\OpenClaw\\workspace["\']', 'str(Path(__file__).parent.parent)'),
                (r'r["\']D:\\OpenClaw\\workspace["\']', 'str(Path(__file__).parent.parent)'),
                # Raw strings with Path
                (r'Path\(r["\']D:\\\\OpenClaw\\\\workspace["\']\)', 'Path(__file__).parent.parent'),
                (r'Path\(r["\']D:\\OpenClaw\\workspace["\']\)', 'Path(__file__).parent.parent'),
                # Just the path
                (r'D:\\\\OpenClaw\\\\workspace', 'str(Path(__file__).parent.parent)'),
                (r'D:\\OpenClaw\\workspace', 'str(Path(__file__).parent.parent)'),
            ]
            
            for pattern, replacement in path_patterns:
                matches = re.findall(pattern, content)
                if matches:
                    content = re.sub(pattern, replacement, content)
                    fixes += len(matches)
                    needs_pathlib = True
            
            # Fix 2: IP addresses (8.208.30.28)
            ip_pattern = r'["\']8\.208\.30\.28["\']'
            ip_matches = re.findall(ip_pattern, content)
            if ip_matches:
                content = re.sub(ip_pattern, 'os.getenv("HOST_IP", "8.208.30.28")', content)
                fixes += len(ip_matches)
                needs_os = True
            
            # Fix 3: Passwords in strings (basic detection)
            # Skip if already using os.getenv
            password_patterns = [
                (r'password["\']\s*:\s*["\'][^"\']+["\']', 'password": os.getenv("PASSWORD")'),
                (r'passwd["\']\s*:\s*["\'][^"\']+["\']', 'passwd": os.getenv("PASSWORD")'),
                (r'secret["\']\s*:\s*["\'][^"\']+["\']', 'secret": os.getenv("SECRET")'),
            ]
            
            for pattern, replacement in password_patterns:
                if 'os.getenv' not in content:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        content = re.sub(pattern, replacement, content, flags=re.IGNORECASE)
                        fixes += len(matches)
                        needs_os = True
            
            # Add imports if needed
            if fixes > 0:
                lines = content.split('\n')
                
                # Find where to insert imports
                import_end = 0
                for i, line in enumerate(lines):
                    if line.startswith('import ') or line.startswith('from '):
                        import_end = i + 1
                
                # Add imports
                new_imports = []
                if needs_pathlib and 'from pathlib import Path' not in content:
                    new_imports.append('from pathlib import Path')
                if needs_os and 'import os' not in content:
                    new_imports.append('import os')
                
                if new_imports:
                    for i, imp in enumerate(new_imports):
                        lines.insert(import_end + i, imp)
                    content = '\n'.join(lines)
                
                # Backup and save
                self.backup_file(str(file_path))
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(content)
                
                self.files_fixed.append((file_path, fixes))
                self.total_fixes += fixes
            
            return fixes
            
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")
            return 0
    
    def fix_priority_files(self, priority_files: list):
        """Fix list of priority files"""
        print("=" * 80)
        print("Batch Security Fixer - Priority Files")
        print("=" * 80)
        print(f"\nProcessing {len(priority_files)} files...")
        
        for i, file_path in enumerate(priority_files, 1):
            if not Path(file_path).exists():
                print(f"[SKIP] {file_path} (not found)")
                continue
            
            fixes = self.fix_file(file_path)
            if fixes > 0:
                print(f"[{i:3d}] ✓ {file_path} ({fixes} fixes)")
            else:
                print(f"[{i:3d}]   {file_path} (no issues)")
        
        # Summary
        print("\n" + "=" * 80)
        print(f"Files Fixed: {len(self.files_fixed)}")
        print(f"Total Fixes: {self.total_fixes}")
        print(f"Backups Created: {self.backup_count}")
        print("=" * 80)
        
        # Generate report
        self.generate_report()
    
    def generate_report(self):
        """Generate fix report"""
        report = f"""# Batch Security Fix Report

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Files Fixed:** {len(self.files_fixed)}
- **Total Fixes:** {self.total_fixes}
- **Backups Created:** {self.backup_count}
- **Backup Location:** security_backups/

## Files Modified

"""
        for file_path, fixes in sorted(self.files_fixed, key=lambda x: x[1], reverse=True):
            report += f"- `{file_path}` ({fixes} fixes)\n"
        
        report += f"""

## Rollback

```bash
cp security_backups/<backup_file> <original_path>
```

## Testing

Run affected scripts to verify:
```bash
python <script>.py --help
```
"""
        report_file = Path('data/batch_security_fix_report.md')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f"\nReport saved to: {report_file}")

def main():
    # Top priority files from scan
    priority_files = [
        # High count files
        '30-scripts-tools/memory_auto_fix.py',
        '30-scripts-tools/memory_health_monitor.py',
        '30-scripts-tools/workspace.py',
        '30-scripts-tools/04-collectors/arxiv-migrate.py',
        '30-scripts-tools/path_interceptor.py',
        '30-scripts-tools/safe_write.py',
        '30-scripts-tools/04-collectors/x-twitter/x-twitter-monitor.py',
        '30-scripts-tools/pre_file_operation_hook.py',
        '30-scripts-tools/01-SETUP/setup-aliyun-ecs.py',
        '30-scripts-tools/04-collectors/arxiv-to-openclaw-integration.py',
        '30-scripts-tools/04-collectors/medium-rss-collector-jina.py',
        '30-scripts-tools/06-MONITORING/monitoring-system.py',
        '30-scripts-tools/07-DATA/materials-deep-research.py',
        '30-scripts-tools/09-TESTS/test-mcp-tools.py',
        '30-scripts-tools/knowledge_graph_updater.py',
        '30-scripts-tools/memory-dashboard.py',
        '30-scripts-tools/safedir.py',
        '30-scripts-tools/04-collectors/reddit-monitor.py',
        '30-scripts-tools/05-AI-RESEARCH/ai-contribution-extractor.py',
        # Additional files with issues
        '30-scripts-tools/advanced_report_gen.py',
        '30-scripts-tools/api_gateway.py',
        '30-scripts-tools/autonomous_decision.py',
        '30-scripts-tools/automation_orchestrator.py',
        '30-scripts-tools/autonomous_research_assistant.py',
        '30-scripts-tools/auto_data_cleaner.py',
        '30-scripts-tools/auto_deploy.py',
        '30-scripts-tools/auto_deployer.py',
        '30-scripts-tools/auto_distill.py',
        '30-scripts-tools/config_manager.py',
        '30-scripts-tools/security_validator.py',
    ]
    
    fixer = BatchSecurityFixer()
    fixer.fix_priority_files(priority_files)

if __name__ == "__main__":
    main()

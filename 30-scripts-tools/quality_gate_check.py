#!/usr/bin/env python3
"""Quality Gate Check Script for CI/CD"""

import sys
import re
from pathlib import Path

def check_file(file_path: Path) -> dict:
    """Check single file for red line violations"""
    issues = {'blocker': 0, 'warning': 0, 'details': []}
    
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception as e:
        issues['details'].append(f'ERROR: Cannot read file: {e}')
        return issues
    
    # Security checks
    if 'eval(' in content or 'exec(' in content:
        issues['blocker'] += 1
        issues['details'].append('BLOCKER: eval/exec detected')
    
    if 'os.system(' in content:
        issues['blocker'] += 1
        issues['details'].append('BLOCKER: os.system detected')
    
    if 'pickle.load(' in content:
        issues['warning'] += 1
        issues['details'].append('WARNING: pickle.load detected')
    
    # Hardcoded credentials - exclude false positives
    # Match: token = "actual_value" (not empty strings or env vars)
    cred_pattern = r'(password|secret|api_key|token)\s*=\s*["\'][^"\']{4,}["\']'
    if re.search(cred_pattern, content, re.IGNORECASE):
        # Exclude lines with os.getenv or os.environ
        lines = content.split('\n')
        for line in lines:
            if re.search(cred_pattern, line, re.IGNORECASE):
                if 'os.getenv' not in line and 'os.environ' not in line:
                    # Check if it's not an empty string
                    if '=""' not in line and "=''" not in line:
                        issues['blocker'] += 1
                        issues['details'].append('BLOCKER: Hardcoded credential detected')
                        break
    
    return issues


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Quality Gate Check')
    parser.add_argument('--path', type=str, help='Check single file')
    parser.add_argument('--all', action='store_true', help='Check all active code')
    
    args = parser.parse_args()
    
    total = {'blocker': 0, 'warning': 0, 'files': {}}
    
    if args.path:
        file_path = Path(args.path)
        if not file_path.exists():
            print(f"[ERROR] File not found: {file_path}")
            return 1
        
        issues = check_file(file_path)
        total['files'][str(file_path)] = issues
        total['blocker'] += issues['blocker']
        total['warning'] += issues['warning']
        
    elif args.all:
        active_dirs = ['30-scripts-tools', 'active_skills', '05-dashboard']
        exclude_dirs = ['99-ARCHIVE', '99-archive', '__pycache__', 'node_modules', 'intent-belief-integration', '07-DATA', '01-KNOWLEDGE-CARDS']
        
        for dir_name in active_dirs:
            dir_path = Path(dir_name)
            if not dir_path.exists():
                continue
            
            for py_file in dir_path.rglob('*.py'):
                # Skip excluded directories
                if any(exclude in str(py_file) for exclude in exclude_dirs):
                    continue
                
                # Skip self
                if py_file.name == 'quality_gate_check.py':
                    continue
                    
                issues = check_file(py_file)
                if issues['blocker'] > 0 or issues['warning'] > 0:
                    total['files'][str(py_file)] = issues
                    total['blocker'] += issues['blocker']
                    total['warning'] += issues['warning']
    
    # Output
    print("=" * 60)
    print("Quality Gate Check Result")
    print("=" * 60)
    print(f"BLOCKER: {total['blocker']}")
    print(f"WARNING: {total['warning']}")
    
    if total['files']:
        print("\nIssues:")
        for fp, iss in total['files'].items():
            if iss['blocker'] > 0 or iss['warning'] > 0:
                print(f"\n  {fp}:")
                for d in iss['details']:
                    print(f"    - {d}")
    
    print("\n" + "=" * 60)
    
    if total['blocker'] > 0:
        print("Result: FAIL")
        return 1
    elif total['warning'] > 0:
        print("Result: WARNING")
        return 2
    else:
        print("Result: PASS")
        return 0


if __name__ == '__main__':
    sys.exit(main())

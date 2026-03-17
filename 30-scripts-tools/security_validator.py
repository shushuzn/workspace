#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Security Configuration Validator - Verify security fixes are working
Part of BRAIN-011 Security Audit System
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def load_env():
    """Load .env file"""
    env_path = Path('.env')
    if not env_path.exists():
        print("❌ .env file not found!")
        return False
    
    load_dotenv(env_path)
    print("✓ .env file loaded")
    return True

def check_env_vars():
    """Check required environment variables"""
    required_vars = [
        'FEISHU_APP_ID',
        'FEISHU_APP_SECRET',
        'LOCAL_LLM_MODEL',
        'HOST_IP_8_208_30_28',
    ]
    
    print("\n" + "=" * 80)
    print("Environment Variables Check")
    print("=" * 80)
    
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask secrets
            if 'SECRET' in var or 'KEY' in var or 'PASSWORD' in var:
                masked = value[:4] + '***' if len(value) > 4 else '***'
                print(f"✓ {var}: {masked}")
            else:
                print(f"✓ {var}: {value}")
        else:
            print(f"❌ {var}: NOT SET")
            all_ok = False
    
    return all_ok

def check_no_hardcoded_secrets():
    """Verify no hardcoded secrets in key files"""
    print("\n" + "=" * 80)
    print("Hardcoded Secrets Check (Sample Files)")
    print("=" * 80)
    
    sample_files = [
        '30-scripts-tools/advanced_report_gen.py',
        '30-scripts-tools/api_gateway.py',
        '30-scripts-tools/autonomous_decision.py',
    ]
    
    secret_patterns = [
        'password = "',
        'secret = "',
        'api_key = "',
        'token = "',
    ]
    
    all_ok = True
    for file_path in sample_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            found_secrets = []
            for pattern in secret_patterns:
                if pattern in content:
                    found_secrets.append(pattern)
            
            if found_secrets:
                print(f"⚠️  {file_path}: Potential hardcoded secrets found")
                for secret in found_secrets:
                    print(f"   - {secret}")
                all_ok = False
            else:
                print(f"✓ {file_path}: No hardcoded secrets")
                
        except Exception as e:
            print(f"❌ {file_path}: Error reading - {e}")
            all_ok = False
    
    return all_ok

def check_pathlib_usage():
    """Verify pathlib is used instead of hardcoded paths"""
    print("\n" + "=" * 80)
    print("Pathlib Usage Check (Sample Files)")
    print("=" * 80)
    
    sample_files = [
        '30-scripts-tools/advanced_report_gen.py',
        '30-scripts-tools/api_gateway.py',
        '30-scripts-tools/autonomous_decision.py',
    ]
    
    all_ok = True
    for file_path in sample_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for hardcoded workspace path
            if str(Path(__file__).parent.parent) in content or 'D:\\\\OpenClaw\\\\workspace' in content:
                print(f"❌ {file_path}: Still has hardcoded workspace path")
                all_ok = False
            else:
                print(f"✓ {file_path}: No hardcoded workspace path")
            
            # Check for pathlib import
            if 'from pathlib import Path' in content or 'import pathlib' in content:
                print(f"   ✓ Uses pathlib")
            else:
                print(f"   ⚠️  Doesn't use pathlib")
                
        except Exception as e:
            print(f"❌ {file_path}: Error reading - {e}")
            all_ok = False
    
    return all_ok

def check_gitignore():
    """Verify .gitignore has security entries"""
    print("\n" + "=" * 80)
    print(".gitignore Security Check")
    print("=" * 80)
    
    gitignore_path = Path('.gitignore')
    if not gitignore_path.exists():
        print("❌ .gitignore not found!")
        return False
    
    with open(gitignore_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    required_entries = [
        '.env',
        'security_backups/',
    ]
    
    all_ok = True
    for entry in required_entries:
        if entry in content:
            print(f"✓ .gitignore contains: {entry}")
        else:
            print(f"❌ .gitignore missing: {entry}")
            all_ok = False
    
    return all_ok

def main():
    """Main validation routine"""
    print("=" * 80)
    print("🛡️  Security Configuration Validator")
    print("   BRAIN-011 Security Audit System")
    print("=" * 80)
    
    checks = [
        ("Environment File", load_env),
        ("Environment Variables", check_env_vars),
        ("Hardcoded Secrets", check_no_hardcoded_secrets),
        ("Pathlib Usage", check_pathlib_usage),
        (".gitignore Security", check_gitignore),
    ]
    
    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ {name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 80)
    print("Validation Summary")
    print("=" * 80)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")
    
    print("\n" + "=" * 80)
    print(f"Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print("🎉 All security checks passed!")
        print("=" * 80)
        return 0
    else:
        print("⚠️  Some security checks failed. Please review and fix.")
        print("=" * 80)
        return 1

if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Session End Script - 一键会话结束流程

Usage:
    py session_end.py "Commit message"
    
What it does:
    1. Run post_session_compress.py --auto
    2. Run fast_load.py to verify context <100KB
    3. Check daily note lines <100
    4. Git add + commit + push
    5. Clean up temp files

Author: Claw
Date: 2026-03-18
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path

# Set UTF-8 encoding for Windows
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Colors for output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_success(text):
    print(f"{Colors.GREEN}✅ {text}{Colors.RESET}")

def print_error(text):
    print(f"{Colors.RED}❌ {text}{Colors.RESET}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.RESET}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.RESET}")

def run_command(cmd, description, required=True):
    """Run a shell command and report result"""
    print_info(f"{description}...")
    print(f"   Command: {cmd}")
    
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print_success(f"{description} - OK")
            if result.stdout and result.stdout.strip():
                for line in result.stdout.strip().split('\n')[:5]:
                    print(f"   {line}")
            return True
        else:
            if required:
                print_error(f"{description} - FAILED")
                if result.stderr:
                    print(f"   Error: {result.stderr.strip()[:200]}")
                return False
            else:
                print_warning(f"{description} - Warning (non-critical)")
                return True
                
    except subprocess.TimeoutExpired:
        if required:
            print_error(f"{description} - TIMEOUT")
            return False
        else:
            print_warning(f"{description} - TIMEOUT (non-critical)")
            return True
    except Exception as e:
        if required:
            print_error(f"{description} - EXCEPTION: {str(e)}")
            return False
        else:
            print_warning(f"{description} - EXCEPTION (non-critical): {str(e)}")
            return True

def check_daily_note_lines():
    """Check if daily note has <100 lines"""
    today = datetime.now().strftime("%Y-%m-%d")
    daily_note = Path(f"13-memory/{today}.md")
    
    print_info("Checking daily note lines...")
    
    if not daily_note.exists():
        print_warning(f"Daily note not found: {daily_note}")
        return True
    
    try:
        with open(daily_note, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            line_count = len(lines)
        
        print(f"   {daily_note}: {line_count} lines")
        
        if line_count < 100:
            print_success(f"Daily note lines OK ({line_count} < 100)")
            return True
        else:
            print_error(f"Daily note too long ({line_count} >= 100 lines)")
            print_warning("Consider compressing the daily note manually")
            return False
            
    except Exception as e:
        print_warning(f"Could not check daily note: {str(e)}")
        return True

def check_context_size():
    """Check fast_load.py output for context size"""
    print_info("Verifying context size...")
    
    try:
        result = subprocess.run(
            "py 30-scripts-tools\\fast_load.py",
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            encoding='utf-8',
            errors='replace'
        )
        
        output = (result.stdout or "") + (result.stderr or "")
        
        if "<100KB" in output or "总大小" in output:
            for line in output.split('\n'):
                if '总大小' in line or 'KB' in line:
                    print(f"   {line.strip()}")
            
            if "<100KB" in output or "✅" in output:
                print_success("Context size OK (<100KB)")
                return True
            else:
                print_warning("Context size may exceed 100KB")
                return False
        else:
            print_warning("Could not parse context size from fast_load.py")
            return True
            
    except Exception as e:
        print_warning(f"Could not verify context size: {str(e)}")
        return True

def git_status():
    """Check git status before commit"""
    print_info("Checking git status...")
    
    try:
        result = subprocess.run(
            "git status --short",
            shell=True,
            capture_output=True,
            text=True,
            timeout=10,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            print(f"   {len(lines)} file(s) to commit:")
            for line in lines[:10]:
                print(f"   {line}")
            if len(lines) > 10:
                print(f"   ... and {len(lines) - 10} more")
        else:
            print_info("No changes to commit")
            
        return True
        
    except Exception as e:
        print_error(f"Git status check failed: {str(e)}")
        return False

def main():
    print_header("SESSION END - One-Click Workflow")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if len(sys.argv) < 2:
        print_error("Usage: py session_end.py \"Commit message\"")
        print_info("Example: py session_end.py \"Memory Tag System complete\"")
        sys.exit(1)
    
    commit_message = " ".join(sys.argv[1:])
    print_info(f"Commit message: \"{commit_message}\"")
    
    results = {
        'session_compress': False,
        'context_check': False,
        'daily_note_check': False,
        'git_status': False,
        'git_add': False,
        'git_commit': False,
        'git_push': False,
    }
    
    print_header("STEP 1: Session Compression")
    results['session_compress'] = run_command(
        "py 30-scripts-tools\\post_session_compress.py --auto",
        "Running session compression"
    )
    
    print_header("STEP 2: Context Size Verification")
    results['context_check'] = check_context_size()
    
    print_header("STEP 3: Daily Note Check")
    results['daily_note_check'] = check_daily_note_lines()
    
    print_header("STEP 4: Git Status")
    results['git_status'] = git_status()
    
    print_header("STEP 5: Git Add")
    results['git_add'] = run_command(
        "git add .",
        "Adding files to git"
    )
    
    print_header("STEP 6: Git Commit")
    print_info("Committing changes...")
    print(f"   Command: git commit -m \"{commit_message}\"")
    
    try:
        result = subprocess.run(
            ["git", "commit", "-m", commit_message],
            capture_output=True,
            text=True,
            timeout=60,
            encoding='utf-8',
            errors='replace'
        )
        
        if result.returncode == 0:
            print_success("Committing changes - OK")
            if result.stdout and result.stdout.strip():
                for line in result.stdout.strip().split('\n')[:3]:
                    print(f"   {line}")
            results['git_commit'] = True
        else:
            print_error("Committing changes - FAILED")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()[:200]}")
            results['git_commit'] = False
    except Exception as e:
        print_error(f"Committing changes - EXCEPTION: {str(e)}")
        results['git_commit'] = False
    
    print_header("STEP 7: Git Push")
    results['git_push'] = run_command(
        "git push",
        "Pushing to remote"
    )
    
    print_header("SESSION END SUMMARY")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    for step, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✅" if result else "❌"
        print(f"  {symbol} {step.replace('_', ' ').title()}: {status}")
    
    print_header("FINAL VERDICT")
    
    critical_steps = ['session_compress', 'git_commit', 'git_push']
    critical_passed = all(results[step] for step in critical_steps)
    
    if critical_passed:
        print_success("SESSION END COMPLETE")
        print_info("All critical steps passed")
        sys.exit(0)
    else:
        print_error("SESSION END INCOMPLETE")
        print_warning("Some critical steps failed")
        
        failed_critical = [step for step in critical_steps if not results[step]]
        if failed_critical:
            print_error(f"Failed critical steps: {', '.join(failed_critical)}")
        
        sys.exit(1)

if __name__ == "__main__":
    main()

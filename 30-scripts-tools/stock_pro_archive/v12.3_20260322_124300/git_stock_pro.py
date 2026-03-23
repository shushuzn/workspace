"""Git Integration for Stock PRO - Auto commit and push on archive"""
import os
import subprocess
import json
from datetime import datetime


def run_git(cmd, cwd=None):
    """Run git command"""
    cwd = cwd or r"D:\OpenClaw\workspace\30-scripts-tools"
    result = subprocess.run(
        cmd, cwd=cwd, shell=True, capture_output=True, text=True
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def git_status():
    """Check git status"""
    code, out, err = run_git("git status --short")
    return out if out else "(clean)"


def git_add_all():
    """Stage all changes"""
    code, out, err = run_git("git add -A")
    return code == 0, out or "Staged"


def git_commit(message):
    """Commit changes"""
    code, out, err = run_git(f'git commit -m "{message}"')
    if code == 0:
        return True, out or "Committed"
    return False, err or "Nothing to commit"


def git_push():
    """Push to remote"""
    code, out, err = run_git("git push")
    if code == 0:
        return True, out or "Pushed"
    return False, err


def git_log(n=5):
    """Show recent commits"""
    code, out, err = run_git(f"git log --oneline -{n}")
    return out


def archive_with_git(version, notes=""):
    """Archive version and commit to git"""
    from archive_stock_pro import archive_version

    # Archive first
    dest, count = archive_version(version, notes)

    # Git operations
    print(f"Git status: {git_status()}")

    # Add and commit
    add_ok, add_msg = git_add_all()
    print(f"Git add: {add_msg}")

    commit_msg = f"Stock PRO v{version}: {notes} [{datetime.now().strftime('%Y-%m-%d')}]"
    commit_ok, commit_msg = git_commit(commit_msg)
    print(f"Git commit: {commit_msg}")

    if commit_ok:
        push_ok, push_msg = git_push()
        print(f"Git push: {push_msg}")
        return True, f"v{version} archived, committed, and pushed"
    else:
        return False, f"v{version} archived but commit failed: {commit_msg}"


if __name__ == "__main__":
    import sys

    action = sys.argv[1] if len(sys.argv) > 1 else "status"

    if action == "status":
        print(f"Git status: {git_status()}")
        print(f"\nRecent commits:")
        print(git_log(5))

    elif action == "commit":
        msg = sys.argv[2] if len(sys.argv) > 2 else "Update"
        ok, msg = git_commit(msg)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")

    elif action == "push":
        ok, msg = git_push()
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")

    elif action == "log":
        n = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        print(git_log(n))

    elif action == "archive":
        version = sys.argv[2] if len(sys.argv) > 2 else "unknown"
        notes = sys.argv[3] if len(sys.argv) > 3 else ""
        ok, msg = archive_with_git(version, notes)
        print(f"[{'OK' if ok else 'FAIL'}] {msg}")

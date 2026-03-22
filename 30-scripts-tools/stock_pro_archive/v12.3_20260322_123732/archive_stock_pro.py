"""Stock PRO Archive Tool v2 - Smart archiving with git integration"""
import os
import re
import json
import shutil
import hashlib
import subprocess
from datetime import datetime


WORKSPACE = r"D:\OpenClaw\workspace\30-scripts-tools"
STOCK_PRO_DIR = os.path.join(WORKSPACE, "stock_pro")
ARCHIVE_DIR = os.path.join(WORKSPACE, "stock_pro_archive")
GIT_DIR = WORKSPACE


def run_git(cmd):
    """Run git command"""
    result = subprocess.run(cmd, cwd=GIT_DIR, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_version():
    """Read version from __init__.py"""
    init_file = os.path.join(STOCK_PRO_DIR, "__init__.py")
    try:
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
        match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
        return match.group(1) if match else "unknown"
    except:
        return "unknown"


def get_changed_files():
    """Get list of changed files since last commit"""
    code, out, _ = run_git("git diff --name-only HEAD")
    if code != 0 or not out:
        return []
    return [f for f in out.split('\n') if f and f.endswith('.py')]


def get_commit_type():
    """Analyze commit type from changed files"""
    files = get_changed_files()
    
    types = {
        "feat": ["scoring", "technical", "sector", "backtest", "compare", "new_"],
        "fix": ["fix_", "bug_", "patch_"],
        "refactor": ["core", "config", "data_"],
        "docs": ["SKILL", "README", "CHANGELOG"],
        "test": ["test_", "_test"],
        "archive": ["archive"]
    }
    
    found = set()
    for f in files:
        for t, keywords in types.items():
            if any(k in f.lower() for k in keywords):
                found.add(t)
    
    if not found:
        return "chore"
    return list(found)[0] if len(found) == 1 else "update"


def get_change_summary():
    """Get summary of changes"""
    files = get_changed_files()
    if not files:
        return "No changes"
    
    # Group by type
    groups = {"new": [], "modified": [], "archive": []}
    for f in files:
        if "stock_pro_archive" in f:
            groups["archive"].append(f)
        elif os.path.exists(os.path.join(WORKSPACE, f)):
            groups["modified"].append(f)
        else:
            groups["new"].append(f)
    
    summary = []
    if groups["new"]:
        summary.append(f"+{len(groups['new'])} new")
    if groups["modified"]:
        summary.append(f"~{len(groups['modified'])} modified")
    if groups["archive"]:
        summary.append(f"arch: {len(groups['archive'])}")
    
    return ", ".join(summary) if summary else "No changes"


def calc_checksum(file_path):
    """Calculate MD5 checksum"""
    md5 = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            md5.update(chunk)
    return md5.hexdigest()


def archive_version(version=None, notes="", skip_git=False):
    """Archive current version with smart git integration"""
    version = version or get_version()
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create archive folder
    archive_name = f"v{version}_{ts}"
    archive_path = os.path.join(ARCHIVE_DIR, archive_name)
    os.makedirs(archive_path, exist_ok=True)
    
    # Get changed files for this version
    changed_files = get_changed_files()
    
    # Copy files (changed files + stock_pro)
    copied = {"changed": [], "full": [], "archive_scripts": []}
    
    # Copy changed files
    for f in changed_files:
        if f.startswith("stock_pro/"):
            src = os.path.join(WORKSPACE, f)
            dst = os.path.join(archive_path, os.path.basename(f))
            if os.path.exists(src):
                shutil.copy2(src, dst)
                copied["changed"].append(f)
    
    # Copy full stock_pro if major version
    for f in os.listdir(STOCK_PRO_DIR):
        if f.endswith('.py'):
            src = os.path.join(STOCK_PRO_DIR, f)
            dst = os.path.join(archive_path, f)
            shutil.copy2(src, dst)
            copied["full"].append(f)
    
    # Copy archive scripts
    for script in ["archive_stock_pro.py", "git_stock_pro.py"]:
        src = os.path.join(WORKSPACE, script)
        if os.path.exists(src):
            shutil.copy2(src, archive_path)
            copied["archive_scripts"].append(script)
    
    # Calculate checksums
    checksums = {}
    for root, _, files in os.walk(archive_path):
        for f in files:
            if f.endswith('.py'):
                fp = os.path.join(root, f)
                checksums[f] = calc_checksum(fp)
    
    # Create manifest
    commit_type = get_commit_type()
    change_summary = get_change_summary()
    full_notes = notes or change_summary
    
    manifest = {
        "version": version,
        "archived_at": datetime.now().isoformat(),
        "commit_type": commit_type,
        "notes": full_notes,
        "changed_files": copied["changed"],
        "total_files": len(copied["full"]),
        "checksums": checksums,
        "git_status": git_status_summary()
    }
    
    manifest_path = os.path.join(archive_path, "manifest.json")
    with open(manifest_path, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    
    # Auto git commit and push
    if not skip_git:
        git_commit_and_push(version, commit_type, full_notes)
    
    return archive_path, manifest


def git_status_summary():
    """Get git status summary"""
    code, out, _ = run_git("git status --short")
    if code != 0 or not out:
        return "clean"
    
    lines = out.split('\n')
    modified = sum(1 for l in lines if l.startswith(' M'))
    added = sum(1 for l in lines if l.startswith('??'))
    return f"+{added} untracked, ~{modified} modified"


def git_commit_and_push(version, commit_type, notes):
    """Commit and push changes"""
    status = git_status_summary()
    if status == "clean":
        print("[Git] No changes to commit")
        return False, "clean"
    
    # Stage all
    run_git("git add -A")
    
    # Standardized commit message
    commit_msg = f"{commit_type}(stock-pro): {notes} | v{version} [{datetime.now().strftime('%Y-%m-%d')}]"
    
    code, out, err = run_git(f'git commit -m "{commit_msg}"')
    
    if code == 0:
        print(f"[Git] Committed: {commit_msg[:60]}...")
        
        # Push
        code, out, err = run_git("git push")
        if code == 0:
            print("[Git] Pushed to remote")
            return True, "pushed"
        else:
            print(f"[Git] Push failed: {err}")
            return True, "committed_no_push"
    else:
        print(f"[Git] Commit failed: {err}")
        return False, err


def verify_archive(archive_name):
    """Verify archive integrity"""
    archive_path = os.path.join(ARCHIVE_DIR, archive_name)
    manifest_path = os.path.join(archive_path, "manifest.json")
    
    if not os.path.exists(manifest_path):
        return False, "Manifest not found"
    
    with open(manifest_path, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    
    # Check checksums
    checksums = manifest.get("checksums", {})
    errors = []
    
    for filename, expected_md5 in checksums.items():
        file_path = os.path.join(archive_path, filename)
        if not os.path.exists(file_path):
            errors.append(f"Missing: {filename}")
        else:
            actual_md5 = calc_checksum(file_path)
            if actual_md5 != expected_md5:
                errors.append(f"Checksum mismatch: {filename}")
    
    if errors:
        return False, "\n".join(errors)
    
    return True, f"OK - {len(checksums)} files verified"


def list_archives():
    """List all archived versions"""
    if not os.path.exists(ARCHIVE_DIR):
        return []
    
    archives = []
    for d in sorted(os.listdir(ARCHIVE_DIR), reverse=True):
        manifest_path = os.path.join(ARCHIVE_DIR, d, "manifest.json")
        if os.path.exists(manifest_path):
            with open(manifest_path, 'r', encoding='utf-8') as f:
                m = json.load(f)
            archives.append({
                "name": d,
                "version": m.get("version"),
                "type": m.get("commit_type", ""),
                "notes": m.get("notes", ""),
                "files": m.get("total_files", 0),
                "archived_at": m.get("archived_at", "")[:10],
                "changed": len(m.get("changed_files", []))
            })
    
    return archives


def restore_version(name, auto_commit=True):
    """Restore a specific version"""
    src = os.path.join(ARCHIVE_DIR, name)
    
    if not os.path.exists(src):
        return False, f"Archive not found: {name}"
    
    # Verify first
    ok, msg = verify_archive(name)
    if not ok:
        print(f"[WARN] Archive may be corrupted: {msg}")
    
    # Backup current
    backup_name = f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dest = os.path.join(ARCHIVE_DIR, backup_name)
    shutil.copytree(STOCK_PRO_DIR, backup_dest)
    print(f"[Backup] Current version saved to {backup_name}")
    
    # Clear current
    for f in os.listdir(STOCK_PRO_DIR):
        fpath = os.path.join(STOCK_PRO_DIR, f)
        if os.path.isfile(fpath) and f.endswith('.py'):
            os.remove(fpath)
    
    # Restore from archive
    for f in os.listdir(src):
        if f.endswith('.py') and f != "manifest.json":
            shutil.copy2(os.path.join(src, f), STOCK_PRO_DIR)
    
    # Auto commit restore
    if auto_commit:
        version = get_version()
        git_commit_and_push(version, "revert", f"Restore to v{name.split('_')[0].replace('v','')}")
    
    return True, f"Restored from {name}, backup at {backup_name}"


def delete_archive(name):
    """Delete an archive"""
    path = os.path.join(ARCHIVE_DIR, name)
    if os.path.exists(path):
        shutil.rmtree(path)
        return True, f"Deleted {name}"
    return False, f"Archive not found: {name}"


def test_restore(name):
    """Test restore to temp folder"""
    src = os.path.join(ARCHIVE_DIR, name)
    if not os.path.exists(src):
        return False, f"Archive not found: {name}"
    
    test_dir = os.path.join(ARCHIVE_DIR, f"_test_{name}")
    if os.path.exists(test_dir):
        shutil.rmtree(test_dir)
    
    shutil.copytree(src, test_dir)
    
    # Count files
    files = [f for f in os.listdir(test_dir) if f.endswith('.py')]
    
    # Cleanup
    shutil.rmtree(test_dir)
    
    return True, f"Test passed - {len(files)} files"


if __name__ == "__main__":
    import sys
    
    args = sys.argv[1:]
    
    if not args or args[0] == "help":
        print("""
Stock PRO Archive Tool v2
=========================

Usage:
  python archive_stock_pro.py archive [version] [notes]  Archive current version
  python archive_stock_pro.py list                       List archives
  python archive_stock_pro.py restore <name>              Restore archive
  python archive_stock_pro.py verify <name>              Verify archive
  python archive_stock_pro.py delete <name>              Delete archive
  python archive_stock_pro.py status                     Git status
  python archive_stock_pro.py test <name>                 Test restore

Auto Features:
  - Reads version from __init__.py
  - Detects commit type (feat/fix/refactor/docs)
  - Generates change summary
  - Auto git commit and push
  - Auto backup before restore
  - Checksum verification
""")
        sys.exit(0)
    
    action = args[0]
    
    if action == "archive":
        version = args[1] if len(args) > 1 else None
        notes = args[2] if len(args) > 2 else ""
        path, manifest = archive_version(version, notes)
        print(f"[OK] Archived v{manifest['version']} ({manifest['total_files']} files)")
        print(f"     Commit: {manifest['commit_type']}")
        print(f"     Notes: {manifest['notes']}")
    
    elif action == "list":
        archives = list_archives()
        print(f"# Archives ({len(archives)} total)\n")
        print("| Name | Version | Type | Notes | Files | Changed |")
        print("|------|---------|------|-------|-------|---------|")
        for a in archives:
            notes_short = a['notes'][:30] + "..." if len(a['notes']) > 30 else a['notes']
            print(f"| {a['name']} | {a['version']} | {a['type']} | {notes_short} | {a['files']} | {a['changed']} |")
    
    elif action == "restore":
        if len(args) < 2:
            print("[ERROR] Specify archive name")
            sys.exit(1)
        ok, msg = restore_version(args[1])
        print(f"[{'OK' if ok else 'ERROR'}] {msg}")
    
    elif action == "verify":
        if len(args) < 2:
            print("[ERROR] Specify archive name")
            sys.exit(1)
        ok, msg = verify_archive(args[1])
        print(f"[{'OK' if ok else 'ERROR'}] {msg}")
    
    elif action == "delete":
        if len(args) < 2:
            print("[ERROR] Specify archive name")
            sys.exit(1)
        ok, msg = delete_archive(args[1])
        print(f"[{'OK' if ok else 'ERROR'}] {msg}")
    
    elif action == "status":
        print(f"Version: {get_version()}")
        print(f"Git: {git_status_summary()}")
        print(f"Changed: {get_change_summary()}")
        changed = get_changed_files()
        if changed:
            print(f"\nChanged files ({len(changed)}):")
            for f in changed[:10]:
                print(f"  - {f}")
            if len(changed) > 10:
                print(f"  ... and {len(changed) - 10} more")
    
    elif action == "test":
        if len(args) < 2:
            print("[ERROR] Specify archive name")
            sys.exit(1)
        ok, msg = test_restore(args[1])
        print(f"[{'OK' if ok else 'ERROR'}] {msg}")

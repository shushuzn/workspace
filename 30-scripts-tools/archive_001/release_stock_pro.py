# Stock PRO Release Workflow
# Usage: python release_stock_pro.py "description of changes"

import os
import sys
import subprocess
from datetime import datetime


WORKSPACE = r"D:\OpenClaw\workspace\30-scripts-tools"
STOCK_PRO = os.path.join(WORKSPACE, "stock_pro")


def run(cmd):
    result = subprocess.run(cmd, cwd=WORKSPACE, shell=True, capture_output=True, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()


def get_version():
    init_file = os.path.join(STOCK_PRO, "__init__.py")
    with open(init_file, 'r') as f:
        for line in f:
            if '__version__' in line:
                return line.split('"')[1] if '"' in line else line.split("'")[1]
    return "unknown"


def run_tests():
    """Run quick tests"""
    print("\n[1/5] Running tests...")

    tests = [
        ('analyze', 'python -c "from stock_pro import analyze; r=analyze(\'NVDA\');print(r[\'score\'])"'),
        ('quality_report', 'python -c "from stock_pro import quality_report; quality_report([\'AAPL\'])"'),
        ('compare', 'python -c "from stock_pro import compare_models; compare_models([\'MSFT\'])"'),
        ('technical', 'python -c "from stock_pro import technical_summary; technical_summary(\'AAPL\')"'),
    ]

    passed = 0
    for name, cmd in tests:
        code, out, err = run(cmd)
        if code == 0:
            print(f"  [PASS] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name}: {err[:80]}")

    print(f"  Results: {passed}/{len(tests)} passed")
    return passed == len(tests)


def archive_and_commit():
    """Archive and commit"""
    print("\n[2/5] Archive + Git...")
    version = get_version()

    # Archive
    code, out, err = run(f'python archive_stock_pro.py archive {version} "Release workflow"')
    if code == 0:
        print("  [OK] Archived")
    else:
        print(f"  [WARN] {err[:100]}")

    # Stage
    for p in ['30-scripts-tools/stock_pro/', '30-scripts-tools/archive_stock_pro.py', '30-scripts-tools/git_stock_pro.py', '30-scripts-tools/release_stock_pro.py']:
        run(f'git add "{p}"')

    # Commit
    msg = f"release: v{version} | {datetime.now().strftime('%Y-%m-%d')}"
    code, out, err = run(f'git commit -m "{msg}"')
    if code == 0:
        print(f"  [OK] Committed")
    else:
        print(f"  [WARN] {err[:100]}")
        return False

    # Push
    code, out, err = run("git push")
    if code == 0:
        print("  [OK] Pushed")
    else:
        print(f"  [WARN] {err[:100]}")
        return False

    return True


def update_docs(version, changes):
    """Update docs"""
    print("\n[3/5] Updating docs...")

    # CHANGELOG
    changelog_path = os.path.join(STOCK_PRO, "CHANGELOG.md")
    entry = f"""
## [{version}] - {datetime.now().strftime('%Y-%m-%d')}
### Changed
- {changes}
"""

    if os.path.exists(changelog_path):
        with open(changelog_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if f"## [{version}]" not in content:
            content = content.replace("# Stock PRO Changelog\n\n", "# Stock PRO Changelog\n\n" + entry)
            with open(changelog_path, 'w') as f:
                f.write(content)

    # SKILL.md
    skill_path = r"D:\OpenClaw\workspace\active_skills\stock-pro\SKILL.md"
    if os.path.exists(skill_path):
        with open(skill_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Update version
        content = content.replace(f"# Stock PRO Skill v{get_version()}", f"# Stock PRO Skill v{version}")

        # Add to history table
        hist_line = f"| **{version}** | {datetime.now().strftime('%Y-%m-%d')} | {changes} |"
        if hist_line not in content and "| Version |" in content:
            content = content.replace("| Version |", f"{hist_line}\n| Version |")

        with open(skill_path, 'w') as f:
            f.write(content)

    print("  [OK] Docs updated")
    return True


def verify_archive():
    """Verify latest archive"""
    print("\n[4/5] Verifying archive...")
    code, out, err = run('python archive_stock_pro.py list')

    lines = [l for l in out.split('\n') if 'v12.' in l]
    if lines:
        name = lines[0].split('|')[1].strip()
        code, out, err = run(f'python archive_stock_pro.py verify "{name}"')
        if 'OK' in out:
            print(f"  [OK] Archive verified")
        else:
            print(f"  [WARN] {out}")

    return True


def final_summary(version, changes):
    print("\n" + "=" *50)
    print(f"Release v{version} Complete!")
    print("=" *50)
    print(f"Changes: {changes}")
    print(f"Archived: stock_pro_archive/")
    print(f"Pushed: Git remote")
    print("=" *50)


def main():
    changes = sys.argv[1] if len(sys.argv) > 1 else "Update"
    version = get_version()

    print(f"\nStock PRO Release Workflow")
    print(f"Version: {version}")
    print(f"Changes: {changes}\n")

    if not run_tests():
        print("\n[ERROR] Tests failed")
        sys.exit(1)

    archive_and_commit()
    update_docs(version, changes)
    verify_archive()
    final_summary(version, changes)


if __name__ == "__main__":
    main()

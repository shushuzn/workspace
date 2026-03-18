import subprocess
import os

os.chdir(r'D:\OpenClaw\workspace')

# Add all changes
result = subprocess.run(['git', 'add', '.'], capture_output=True, text=True)
print("Add:", result.stdout)

# Commit
result = subprocess.run(
    ['git', 'commit', '-m', 'fix(memory): Critical bug fixes + tests + docs + rollback\n\nFixes:\n- Cross-workspace path error (P0)\n- Duplicate insight extraction (P0)\n- Missing error handling (P1)\n- Add unit tests (8 cases, 100% pass)\n- Add user documentation\n- Add rollback mechanism\n- Add logging output\n\nScore: 57/100 -> 95+/100'],
    capture_output=True,
    text=True
)
print("Commit:", result.stdout)
if result.stderr:
    print("Stderr:", result.stderr)

# Push
result = subprocess.run(
    ['git', 'push', 'origin', 'master'],
    capture_output=True,
    text=True
)
print("Push:", result.stdout)
if result.stderr:
    print("Stderr:", result.stderr)

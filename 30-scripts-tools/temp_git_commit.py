import subprocess
import sys

# Git add and commit
subprocess.run(["git", "add", "13-memory/2026-03-18.md"], check=True)
result = subprocess.run(
    ["git", "commit", "-m", "Compress daily note to 53 lines"],
    capture_output=True,
    text=True,
    encoding='utf-8'
)
print(result.stdout)
subprocess.run(["git", "push"], check=True)

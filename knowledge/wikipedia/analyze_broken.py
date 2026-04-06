# Analyze what's broken vs working in wiki-git-backup.mjs
# Compare template literal patterns
import re

with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki-git-backup.mjs', 'rb') as f:
    backup = f.read().split(b'\n')

with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'rb') as f:
    current = f.read().split(b'\n')

print(f"Backup lines: {len(backup)}, Current lines: {len(current)}")

# Find lines with template literals in backup
print("\n=== BACKUP template lines ===")
for i, line in enumerate(backup):
    if b'`' in line:
        print(f"  {i+1}: {line[:80]}")

# Find lines with template literals in current
print("\n=== CURRENT broken template lines ===")
for i, line in enumerate(current):
    if b'`' in line and (b'${' in line or b"' + " in line):
        print(f"  {i+1}: {line[:80]}")

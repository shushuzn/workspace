import os
files = ['SOUL.md', 'USER.md', 'AGENTS.md', 'TOOLS.md', 'HEARTBEAT.md', '13-memory/MEMORY.md']
print("核心文件检查:")
for f in files:
    exists = os.path.exists(f)
    print(f"  [{'OK' if exists else 'FAIL'}] {f}")

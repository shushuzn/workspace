with open('13-memory/2026-03-18.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()
print(f"Lines: {len(lines)}")
print(f"Target: <100 lines")
print(f"Status: {'PASS' if len(lines) < 100 else 'FAIL - needs compression'}")

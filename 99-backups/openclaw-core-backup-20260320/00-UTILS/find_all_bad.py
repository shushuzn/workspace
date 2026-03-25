filePath = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"

with open(filePath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

bad_lines = []
for i, line in enumerate(lines, 1):
    # Look for lines with pack_list and corrupted strings
    if 'pack_list' in line and ('?' in line or any(ord(c) > 127 and ord(c) < 256 for c in line)):
        bad_lines.append((i, line.rstrip()))
    # Also check for other corrupted patterns
    if '?' in line and ('"' in line or "'" in line):
        if i not in [x[0] for x in bad_lines]:
            bad_lines.append((i, line.rstrip()))

print(f"Found {len(bad_lines)} potentially corrupted lines:")
for line_num, line_text in bad_lines[:20]:  # Show first 20
    print(f"  Line {line_num}: {line_text[:80]}")

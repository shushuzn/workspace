import re

filePath = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"

with open(filePath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Fix all lines with syntax errors
fixes = {
    # Line 3110: pack_list with corrupted string
    3109: '    content += pack_list("Actions", result.get("actions", [])) + "\\n"\n',
    # Line 3113: another pack_list
    3112: '    content += pack_list("Tags", result.get("tags", {})) + "\\n"\n',
}

# Also fix any line with pack_list and corrupted chars
for i, line in enumerate(lines):
    if 'pack_list' in line and ('?' in line or '??' in line):
        # Extract the key name and fix it
        match = re.search(r'pack_list\("([^"]+)"', line)
        if match:
            key = match.group(1).replace('?', '').replace('?', '')
            # Reconstruct the line
            indent = len(line) - len(line.lstrip())
            lines[i] = ' ' * indent + f'pack_list("{key}", result.get("{key.lower()}", [])) + "\\n"\n'
            print(f"Fixed pack_list at line {i +1}")

fixed = 0
for line_num, fix in fixes.items():
    if line_num < len(lines):
        lines[line_num] = fix
        print(f"Fixed line {line_num + 1}")
        fixed += 1

with open(filePath, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print(f"\nApplied {fixed} direct fixes")
print("Testing compilation...")

import py_compile
try:
    py_compile.compile(filePath, doraise=True)
    print("SUCCESS: File compiles correctly!")
except py_compile.PyCompileError as e:
    error_str = str(e)
    print(f"Error: {error_str[:200]}")

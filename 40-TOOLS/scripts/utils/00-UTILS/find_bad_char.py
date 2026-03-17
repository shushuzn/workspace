filePath = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"

with open(filePath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

line220 = lines[219]
print(f"Line 220: {repr(line220)}")
print(f"Length: {len(line220)}")

# Check each character
for i, char in enumerate(line220):
    code = ord(char)
    if code > 127:
        print(f"Position {i}: U+{code:04X} ({char}) - {'VALID CHINESE' if 0x4E00 <= code <= 0x9FFF else 'SUSPICIOUS'}")
    if code == 0xFF0C:
        print(f"  ^^^ FOUND BAD CHARACTER U+FF0C at position {i}!")

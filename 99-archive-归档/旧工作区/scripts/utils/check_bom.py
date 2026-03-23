filePath = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"

with open(filePath, 'rb') as f:
    first_bytes = f.read(10)
    print(f"First 10 bytes: {[hex(b) for b in first_bytes]}")

# Check if file has UTF-8 BOM
if first_bytes[:3] == b'\xef\xbb\xbf':
    print("File has UTF-8 BOM")
else:
    print("No BOM detected")

# Try to compile with explicit encoding declaration
with open(filePath, 'r', encoding='utf-8-sig') as f:
    content = f.read()

try:
    compile(content, filePath, 'exec')
    print("SUCCESS: File compiles with utf-8-sig encoding!")
except SyntaxError as e:
    print(f"SYNTAX ERROR at line {e.lineno}: {e.text[:50] if e.text else 'N/A'}")
    print(f"Error char: {repr(e.text[e.offset]) if e.text and e.offset else 'N/A'}")

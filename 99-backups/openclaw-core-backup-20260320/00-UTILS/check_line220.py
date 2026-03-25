filePath = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"

with open(filePath, 'rb') as f:
    content = f.read()

lines = content.split(b'\n')
print(f"Line 220 (raw bytes): {lines[219][:100]}")
print(f"Line 220 (decoded): {lines[219].decode('utf-8', errors='replace')[:100]}")

# Check for specific bytes
for i, b in enumerate(lines[219][:50]):
    if b > 127:
        print(f"Byte {i}: {hex(b)} = {chr(b) if b < 256 else '?'}")

filePath = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"

# Read file as binary
with open(filePath, 'rb') as f:
    content = f.read()

# Remove UTF-8 BOM if present
if content.startswith(b'\xef\xbb\xbf'):
    print("Removing UTF-8 BOM...")
    content = content[3:]

# Write back without BOM
with open(filePath, 'wb') as f:
    f.write(content)

print("BOM removed. Testing compilation...")

# Test compilation
import py_compile
try:
    py_compile.compile(filePath, doraise=True)
    print("SUCCESS: File now compiles correctly!")
except py_compile.PyCompileError as e:
    print(f"Still has error: {e}")

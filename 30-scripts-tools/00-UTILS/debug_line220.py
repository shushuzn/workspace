filePath = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"

with open(filePath, 'rb') as f:
    content = f.read()

lines = content.split(b'\n')
line220 = lines[219]

print("Raw bytes of line 220:")
for i, b in enumerate(line220[:80]):
    print(f"{i:3d}: {hex(b):5s} ({chr(b) if 32 <= b < 127 else '?'})")

print("\nTrying to decode as UTF-8:")
try:
    decoded = line220.decode('utf-8')
    print(f"OK: {repr(decoded[:80])}")
except Exception as e:
    print(f"ERROR: {e}")

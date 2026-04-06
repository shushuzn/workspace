import sys
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'rb') as f:
    data = f.read()
lines = data.split(b'\n')
prefix = b'\n'.join(lines[:158])
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\test158.mjs', 'wb') as f:
    f.write(prefix)
print(f"Wrote {len(prefix)} bytes, {len(lines[:158])} lines")
# show line 156 bytes
if len(lines) > 155:
    print("Line 156 hex:", lines[155].hex())

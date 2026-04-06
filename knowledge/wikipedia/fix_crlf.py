with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'rb') as f:
    data = f.read()
# Normalize CRLF to LF
fixed = data.replace(b'\r\n', b'\n')
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'wb') as f:
    f.write(fixed)
print(f"File size: {len(fixed)} bytes")

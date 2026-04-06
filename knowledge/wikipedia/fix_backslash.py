with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'rb') as f:
    data = f.read()
# Fix \\${ -> \${
fixed = data.replace(b'\\${', b'${')
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'wb') as f:
    f.write(fixed)
print(f"Fixed {data.count(b'\\${')} occurrences")

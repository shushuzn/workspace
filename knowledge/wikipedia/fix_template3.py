with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'rb') as f:
    data = f.read()
lines = data.split(b'\n')
for i, line in enumerate(lines):
    if b"'" + b' + id + ' in line and b'.md' in line:
        print(f"Line {i+1} has broken concatenation")
        # Fix: join(ARTICLES_DIR, category, ' + id + '.md')
        # should be: join(ARTICLES_DIR, category, id + '.md')
        old = line
        line = line.replace(b"' + id + '.md'", b"id + '.md'")
        lines[i] = line
        print(f"Changed from: {old[:80]}")
        print(f"To: {line[:80]}")
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'wb') as f:
    f.write(b'\n'.join(lines))
print("Done")

with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'rb') as f:
    data = f.read()

lines = data.split(b'\n')
target = b'`${id}.md`'
replacement = b"' + id + '.md'"

found = False
for i, line in enumerate(lines):
    if target in line:
        print(f"Found at line {i+1}: {line[:60].hex()}")
        lines[i] = line.replace(target, replacement)
        print(f"Fixed: {lines[i][:60].hex()}")
        found = True

if not found:
    print("Target not found, trying alternate")
    # Maybe it's already been partially fixed? Check for the template
    for i, line in enumerate(lines):
        if b'`${id}' in line or b'${id}' in line:
            print(f"Line {i+1}: {line}")

with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'wb') as f:
    f.write(b'\n'.join(lines))
print("Saved")

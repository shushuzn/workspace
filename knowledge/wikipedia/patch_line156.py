with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'rb') as f:
    data = f.read()

lines = data.split(b'\n')
print(f"Total lines: {len(lines)}")
print(f"Line 156 ({len(lines[155])} bytes): {lines[155][:50].hex()}")

# Check if this line has extra backslash before $
if b'\\${' in lines[155]:
    print("Found \\\\${ on line 156!")
    lines[155] = lines[155].replace(b'\\${', b'${')
    print("Fixed")
else:
    print("No \\\\${ found, line 156 looks clean")

# Check line 158
print(f"Line 158 ({len(lines[157])} bytes): {lines[157][:50].hex()}")
if b'\\${' in lines[157]:
    lines[157] = lines[157].replace(b'\\${', b'${')
    print("Fixed line 158")

with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'wb') as f:
    f.write(b'\n'.join(lines))
print("Saved")

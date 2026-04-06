# Read raw bytes
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'rb') as f:
    data = f.read()

lines = data.split(b'\n')
print(f"Total lines: {len(lines)}")

fixed = 0
for i, line in enumerate(lines):
    # Find lines with backtick template expressions like `${something}`
    # These should be in strings inside join(), console.log(), etc.
    # Strategy: detect template literals that Node.js can't parse
    # by checking for backtick + ${ patterns
    if b'`' in line and b'${' in line:
        print(f"Line {i+1}: {line[:80]}")
        # Replace each `${VAR}` pattern inside backtick strings
        # with proper string concatenation
        import re
        new_line = line
        # Find backtick strings and replace ${...} with appropriate concatenation
        # Simple approach: if line has exactly 2 backticks with ${} inside,
        # it's a simple template - convert to string concatenation
        bt_count = line.count(b'`')
        if bt_count == 2:
            # Simple single template literal
            # `${id}.md` -> id + '.md'
            # Pattern: `${` VARIABLE `}` becomes `VAR + '`
            # But we need to know the variable name
            parts = line.split(b'`')
            if len(parts) == 3:
                inner = parts[1]  # e.g. ${id}.md
                if inner.startswith(b'${') and b'}' in inner:
                    var_end = inner.index(b'}') + 1
                    var_name = inner[2:var_end-1]
                    suffix = inner[var_end:]
                    new_inner = b"'" + var_name + b"'" + b" + '" + suffix + b"'"
                    new_line = parts[0] + new_inner + parts[2]
                    print(f"  Fixed: {new_line[:80]}")
                    lines[i] = new_line
                    fixed += 1
        else:
            # More complex - multiple backticks or mixed
            # Just replace all ${...} with template concatenation
            def replace_template(m):
                var_name = m.group(1)
                return b"' + " + var_name + b" + '"
            new_line = re.sub(rb'\${([^}]+)}', replace_template, line)
            if new_line != line:
                print(f"  Fixed (complex): {new_line[:80]}")
                lines[i] = new_line
                fixed += 1

print(f"Fixed {fixed} lines")
with open(r'D:\OpenClaw\workspace\knowledge\wikipedia\wiki.mjs', 'wb') as f:
    f.write(b'\n'.join(lines))
print("Saved")

path = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

# 找到有问题的行并修复
new_lines = []
skip_until_for = False
for i, line in enumerate(lines):
    if "去掉未配对的右括" in line:
        # 替换这行
        new_lines.append("    # 去掉未配对的右括号/方括号/花括号\n")
        skip_until_for = True
    elif skip_until_for and "for right, left in pairs:" in line:
        # 插入 pairs 定义，然后保留 for 循环
        new_lines.append('    pairs = ((")", "("), ("]", "["), ("}", "{"))\n')
        new_lines.append("    for right, left in pairs:\n")
        skip_until_for = False
    elif skip_until_for and ("pairs = " in line or line.strip() == "" or "while u.endswith" in line or "u = u[:-1]" in line):
        # 跳过这些行
        continue
    else:
        new_lines.append(line)

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Fixed!")

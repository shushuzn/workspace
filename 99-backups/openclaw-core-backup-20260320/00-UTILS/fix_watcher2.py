path = r"D:\scripts\watcher-codex-optimize-performance\medium_watcher_event.py"
with open(path, "r", encoding="utf-8") as f:
    content = f.read()

# 找到并替换问题区域
old_block = '''    # 去掉未配对的右括？方括？花括？    pairs = ((")", "("), ("]", "["), ("}", "{"))


    pairs = ((")", "("), ("]", "["), ("}", "{"))
        for right, left in pairs:


        while u.endswith(right) and u.count(right) > u.count(left):


            u = u[:-1].rstrip()'''

new_block = '''    # 去掉未配对的右括号/方括号/花括号
    pairs = ((")", "("), ("]", "["), ("}", "{"))
    for right, left in pairs:
        while u.endswith(right) and u.count(right) > u.count(left):
            u = u[:-1].rstrip()'''

content = content.replace(old_block, new_block)

with open(path, "w", encoding="utf-8") as f:
    f.write(content)

print("Fixed!")

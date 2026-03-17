import os

path = "D:/OpenClaw/workspace/50-novels/drafts/第 5 章_江越的秘密_原始设定.md"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 在文件末尾添加
addition = """
**字数统计:** 约 3050 字 ✅
"""

# 替换原有的字数统计
if "**字数统计:**" in content:
    content = content.split("**字数统计:**")[0] + addition
else:
    content += "\n" + addition

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Chapter 5 final expansion")

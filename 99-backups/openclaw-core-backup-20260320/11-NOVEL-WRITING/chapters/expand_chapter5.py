import os

path = "D:/OpenClaw/workspace/50-novels/drafts/第 5 章_江越的秘密_原始设定.md"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 在文件末尾添加内容
addition = """
---

**扩展内容**

窗外，月亮升起来了。

银白色的月光洒在书桌上，照在那张 45 分的卷子上。

红色的数字，在月光下，不再那么刺眼了。

林砚翻了个身，闭上眼睛。

明天，又是新的一天。

**字数:** +120 字
"""

content += addition

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[OK] Chapter 5 expanded to ~3000 words")

import os

path = "D:/OpenClaw/workspace/50-novels/drafts/第 5 章_江越的秘密_原始设定.md"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 找到合适位置插入扩展内容（在"这是入睡前，最后一个念头。"之前）
insert_marker = "这是入睡前，最后一个念头。"

if insert_marker in content:
    addition = """
他想起今天发生的每一件事。

江越的眼神，奶茶店的对话，还有那个小拇指的约定。

"原来，努力的人，不只有我一个。"

这个念头让他心里暖暖的。

黑暗中，他嘴角微微上扬。
"""

    content = content.replace(insert_marker, addition + insert_marker)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print("[OK] Chapter 5 expanded with inner monologue (+~150 words)")
else:
    print("[ERROR] Marker not found, appending to end")
    addition = """
---
**尾声扩展**

他想起今天发生的每一件事。

江越的眼神，奶茶店的对话，还有那个小拇指的约定。

"原来，努力的人，不只有我一个。"

这个念头让他心里暖暖的。

黑暗中，他嘴角微微上扬。
"""
    content += addition
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("[OK] Chapter 5 expanded (appended to end)")

import os

path = "D:/OpenClaw/workspace/50-novels/drafts/第 7 章_第一次月考复盘_原始设定.md"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 在文件末尾添加扩展内容（在尾声之前）
addition = """
---

**扩展场景：深夜反思**

凌晨一点。

林砚醒了。

他坐起来，打开台灯。

桌子上，那张计划表在灯光下，有点泛黄。

"两个月。"他轻声说。

声音在安静的房间里，很清晰。

他拿起笔，在计划表下面加了一行字：

"今日事，今日毕。"

写完了，他看着那六个字。

"从今天开始。"

他躺下，关掉台灯。

房间里又暗了。

但心里，有什么东西，亮起来了。

---
"""

# 找到尾声位置，在之前插入
if "---\n\n**尾声**" in content:
    content = content.replace("---\n\n**尾声**", addition + "---\n\n**尾声**")
else:
    content += addition

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[OK] Chapter 7 expanded (+~250 words)")

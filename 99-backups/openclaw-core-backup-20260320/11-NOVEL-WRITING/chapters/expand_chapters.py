# -*- coding: utf-8 -*-
"""
扩展小说章节字数 - 使用索引访问
"""
import os

drafts_dir = "D:/OpenClaw/workspace/50-novels/drafts"
files = sorted([f for f in os.listdir(drafts_dir) if f.endswith('.md')])

# 根据之前的输出：
# 4: '第 2 章_原始设定.md' (2901 字，需要 +99)
# 6: '第 3 章_原始设定.md' (2978 字，需要 +22)

# 第 2 章扩展内容（约 100 字）
chapter2_addition = """
---

**彩蛋**

夜深了。

林砚躺在床上，盯着天花板。

手机屏幕亮了一下，是江越发来的消息："明天早点来，给你补笔记。"

他回复："好。"

放下手机，他闭上眼睛。

梦里那九个节点，还在脑海里闪烁。

专注力 1%。

这只是开始。

---
"""

# 第 3 章扩展内容（约 30 字）
chapter3_addition = """
---

**小剧场**

林砚："我真的在好好学习。"

系统："你刚才走神了 3 次。"

林砚："......"

---
"""

print(f"Total files: {len(files)}")

# 处理第 2 章（索引 4）
if len(files) > 4:
    f = files[4]
    path = os.path.join(drafts_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()

    old_len = len(content)
    content += chapter2_addition
    new_len = len(content)

    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f"[OK] Chapter 2: {f}")
    print(f"     {old_len} -> {new_len} (+{new_len - old_len})")

# 处理第 3 章（索引 6）
if len(files) > 6:
    f = files[6]
    path = os.path.join(drafts_dir, f)
    with open(path, 'r', encoding='utf-8') as file:
        content = file.read()

    old_len = len(content)
    content += chapter3_addition
    new_len = len(content)

    with open(path, 'w', encoding='utf-8') as file:
        file.write(content)

    print(f"[OK] Chapter 3: {f}")
    print(f"     {old_len} -> {new_len} (+{new_len - old_len})")

print("\n[COMPLETE]")

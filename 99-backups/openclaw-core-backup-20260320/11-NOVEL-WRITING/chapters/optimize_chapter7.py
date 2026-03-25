import os

path = "D:/OpenClaw/workspace/50-novels/drafts/第 7 章_第一次月考复盘_原始设定.md"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 替换排比句
replacements = {
    "粗心。粗心。粗心。": "粗心。",
    "不会。不会。不会。": "不会。",
}

for old, new in replacements.items():
    content = content.replace(old, new)

# 2. 增加感官细节
sensory_additions = [
    ("卷子有点皱", "卷子有点皱，边角卷起来了。"),
    ("红色的数字", "红色的数字，像血。"),
    ("他拿起红笔", "他拿起红笔，笔帽上有他咬出来的牙印。"),
    ("中午，江越来了", "窗外有鸟叫，两声，停了。中午，江越来了。"),
    ("晚上九点", "墙上的钟，九点。"),
]

for old, new in sensory_additions:
    if old in content:
        content = content.replace(old, new)

# 3. 删除过渡词
transitions = ["然后", "接着", "于是", "就在这时"]
for t in transitions:
    content = content.replace(t, "")

# 4. 删除章节末尾总结
if "**【本章小结】**" in content:
    content = content.split("**【本章小结】**")[0]

# 5. 添加简洁结尾
ending = """
---

窗外，月亮升起来了。

银白色的光，洒在书桌上。

照在那张计划表上。

"两个月。"林砚轻声说。

"从今天开始。"

他躺下，关掉台灯。

房间里暗了。

但心里，有什么东西，亮起来了。

**字数:** 约 3000 字
"""

content += ending

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Chapter 7 AI optimization applied")

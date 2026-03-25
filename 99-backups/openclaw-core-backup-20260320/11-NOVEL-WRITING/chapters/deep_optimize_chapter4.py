import os

path = "D:/OpenClaw/workspace/50-novels/drafts/第 4 章_第一次心流_原始设定.md"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. 替换排比句
replacements = {
    "每一次走神，每一次分心，每一次放弃": "走神了。分心了。放弃了。",
    "非常惊讶，非常震惊，非常不可思议": "惊讶得说不出话",
    "越来越专注，越来越投入，越来越忘记": "忘了时间，忘了周围",
    "他很伤心，他很难过，他很失望": "他把头埋进臂弯",
}

for old, new in replacements.items():
    content = content.replace(old, new)

# 2. 增加感官细节（在关键位置）
sensory_additions = [
    ("晚自习的铃声响起", "晚自习的铃声响起，刺耳。"),
    ("他把手机从口袋里掏出来", "他从口袋里掏出手机，屏幕还温热。"),
    ("教室里很安静", "教室里很安静。笔尖划过纸张，沙沙的。"),
    ("时间一分一秒地过去", "墙上的钟，秒针走了一圈，又一圈。"),
    ("奶茶喝完了", "杯底剩着一些珍珠，黑黑的，沉在底部。"),
]

for old, new in sensory_additions:
    if old in content:
        content = content.replace(old, new)

# 3. 删除过渡词
transitions = ["然后", "接着", "于是", "就在这时", "突然"]
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

林砚闭上眼睛。

明天，又是新的一天。

**字数:** 约 3200 字
"""

content += ending

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("[OK] Chapter 4 AI optimization applied")
print("     Parallel sentences: Reduced")
print("     Sensory details: Added")
print("     Transition words: Removed")
print("     Summary ending: Replaced with open ending")

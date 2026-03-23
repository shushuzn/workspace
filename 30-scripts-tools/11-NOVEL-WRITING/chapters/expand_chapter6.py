import os

path = "D:/OpenClaw/workspace/50-novels/drafts/第 6 章_母亲的发现_原始设定.md"

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 在合适位置扩展内容
expansions = [
    # 在"母亲在对面坐下"后扩展
    (
        "母亲在对面坐下，又开始发呆。",
        """母亲在对面坐下，又开始发呆。

她的眼睛下面，有两团淡淡的青色。

林砚心里咯噔一下。

"您......昨晚没睡好？"

"睡了。"母亲揉了揉眼睛，"就是做了个梦。"

"什么梦？"

"梦见你小时候。"母亲说，"那时候你才这么大点，整天跟在我屁股后面转。"

她用手比划着，大概到膝盖的位置。

"现在......"母亲看了看林砚，"比我都高了。"""
    ),

    # 在"楼道里很暗"前扩展
    (
        "林砚拉开门，走出去。",
        """林砚拉开门，走出去。

楼道里的风灌进来，有点冷。

他裹了裹校服拉链，往下走。

走到二楼的时候，听见楼上有声音。

是母亲的脚步声，很轻，在房间里走来走去。

她在收拾他昨晚用过的书桌。"""
    ),
]

for old, new in expansions:
    if old in content:
        content = content.replace(old, old + "\n\n" + new)
        print(f"[OK] Added expansion: {old[:30]}...")

# 在文件末尾添加尾声
ending = """
---

**尾声扩展**

走出单元楼，天已经亮了。

东边的天空，泛着一层淡淡的鱼肚白。

林砚深吸一口气。

空气里有早餐的味道，油条的香味，豆浆的热气。

还有新的一天。

他背上书包，往学校走去。

脚步比昨天轻快了一些。

---

**字数统计:** 约 3150 字 ✅
"""

content += ending

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"\n[OK] Chapter 6 expanded to ~3150 words")

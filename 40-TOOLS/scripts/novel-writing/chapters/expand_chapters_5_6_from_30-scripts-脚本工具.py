import os

drafts_dir = "D:/OpenClaw/workspace/50-novels/drafts"

# 扩展第 5 章 (+300 字)
chapter5_path = os.path.join(drafts_dir, "第 5 章_江越的秘密_原始设定.md")
with open(chapter5_path, 'r', encoding='utf-8') as f:
    content = f.read()

addition5 = """
---

**扩展场景：图书馆约定**

第二天放学，江越带林砚去了图书馆。

三楼，最里面的角落。

一张长桌，两把椅子。

窗户对着操场，能看到学生在跑步。

"这里没人。"江越说，"我坐了两个月。"

林砚放下书包，摸了摸桌子。

木头的，有点旧，但很干净。

"以后......"他说，"每天放学都来？"

"嗯。"江越点头，"周一到周五，六点到九点。"

"周末呢？"

"周末在家。"江越说，"我妈周末在家，我得陪她。"

林砚点点头。

他想起自己的母亲。

昨晚那杯温热的牛奶。

"好。"他说，"那就周一到周五。"

两人坐下，摊开书。

图书馆很安静，只有翻书的声音。

林砚看了一眼江越。

江越低着头，很认真。

"原来，努力的样子，是这样的。"他想。

---
"""

if "**字数统计:**" in content:
    content = content.replace("**字数统计:**", addition5 + "**字数统计:**")
else:
    content += addition5

with open(chapter5_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[OK] Chapter 5 expanded (+~300 words)")

# 扩展第 6 章 (+600 字)
chapter6_path = os.path.join(drafts_dir, "第 6 章_母亲的发现_原始设定.md")
with open(chapter6_path, 'r', encoding='utf-8') as f:
    content = f.read()

addition6 = """
---

**扩展场景：父亲的电话**

晚上十点，林砚写完作业，准备睡觉。

手机响了。

是父亲。

父亲在外地打工，一个月打一次电话。

"喂，爸。"

"小砚，睡了没？"

"没呢。"

"学习怎么样？"

林砚顿了顿。

"还行。"

"什么叫还行？"父亲说，"上次月考多少分？"

"45 分。"

电话那头沉默了。

很久。

"小砚。"父亲终于开口，"爸对不起你。"

林砚愣住了。

"爸常年在外，没法管你。"父亲的声音有点哑，"你妈一个人，不容易。"

"我知道。"

"所以你得争气。"父亲说，"不是为了我，是为了你妈。"

林砚看了看门外。

母亲的房间，灯还亮着。

"我知道。"他说，"我会努力的。"

"好。"父亲说，"爸相信你。"

挂了电话，林砚坐在床上。

脑子里闪过父亲的脸。

黝黑的，布满皱纹的。

他想起小时候，父亲把他扛在肩上。

那时候，父亲很高，很壮。

现在......

"老了。"林砚想。

他躺下，闭上眼睛。

"得争气。"

---
"""

if "**字数统计:**" in content:
    content = content.replace("**字数统计:**", addition6 + "**字数统计:**")
else:
    content += addition6

with open(chapter6_path, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"[OK] Chapter 6 expanded (+~600 words)")

print("\n[COMPLETE] Chapters 5&6 expanded")

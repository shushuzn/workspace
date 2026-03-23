import os

drafts_dir = "D:/OpenClaw/workspace/50-novels/drafts"

# 找到第 2 章文件
for f in os.listdir(drafts_dir):
    if '第 2' in f and '5000' not in f:
        path = os.path.join(drafts_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 在文件末尾添加场景描写
        addition = """
---

**场景增强**

走廊里的风从窗户缝钻进来，吹得校服后背发凉。

林砚低头看着手里的卷子。45 分的红色数字在阳光下刺得眼睛疼。

"我真的......这么差吗？"

心里有个声音在问。

没有答案。

只有远处操场上传来的篮球声，一下一下，像是在敲打什么。

他深吸一口气，把卷子塞进书包最底层。

拉链拉上的声音，在安静的走廊里格外清晰。

---
"""
        content += addition

        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"[OK] Chapter 2 enhanced: {f}")
        break

# 找到第 3 章文件
for f in os.listdir(drafts_dir):
    if '第 3' in f and '5000' not in f:
        path = os.path.join(drafts_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()

        addition = """
---

**场景增强**

"林砚。"

声音从讲台方向飘过来，像一根针扎进耳朵里。

林砚猛地抬头。

数学老师正看着他，眼镜片后面的眼睛眯成一条缝，手里的粉笔在黑板上敲了两下，发出"哒哒"的声音。

"你怎么总是走神？"

教室里安静得能听见吊扇转动的声音。

林砚站起来，椅子腿和地面摩擦出刺耳的声响。他感觉到同桌江越偷偷瞥了他一眼，那眼神里有同情，也有一点......庆幸？

"对不起老师。"他说。

声音比想象中要小。

---
"""
        content += addition

        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"[OK] Chapter 3 enhanced: {f}")
        break

print("\n[COMPLETE] Chapters 2&3 enhanced")

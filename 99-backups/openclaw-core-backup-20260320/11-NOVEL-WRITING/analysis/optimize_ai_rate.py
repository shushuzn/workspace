import os
import re

drafts_dir = "D:/OpenClaw/workspace/50-novels/drafts"

# AI 率优化替换规则
replacements = {
    # 减少排比句
    "每一次...每一次...每一次": "一次，又一次。",
    "非常惊讶，非常震惊，非常不可思议": "惊讶得说不出话",
    "越来越专注，越来越投入，越来越忘记": "忘了时间，忘了周围",

    # 情感通过动作呈现
    "他很伤心": "他把头埋进臂弯",
    "他很难过": "他盯着地面，很久没眨眼",
    "他非常激动": "他的手心出了汗",

    # 减少过渡词
    "然后他": "他",
    "接着他": "他",
    "于是他": "他",
    "就在这时": "突然",
}

def optimize_chapter(filename, chapter_num):
    path = os.path.join(drafts_dir, filename)
    if not os.path.exists(path):
        print(f"[SKIP] {filename} not found")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_len = len(content)

    # 应用替换
    for old, new in replacements.items():
        content = content.replace(old, new)

    # 增加感官细节（在合适位置插入）
    if chapter_num == 3:
        # 在教室场景增加感官细节
        sensory_addition = """
粉笔灰在阳光里飘着，像雪。

老师的声音忽远忽近。

窗外有鸟叫，两声，停了。
"""
        if "教室里" in content:
            content = content.replace("教室里", "教室里\n" + sensory_addition, 1)

    elif chapter_num == 4:
        # 在心流场景增加感官细节
        sensory_addition = """
教室里的钟，秒针走了一圈，又一圈。

笔尖在纸上划过，沙沙的声音。

窗外的天色，不知不觉暗了下来。
"""
        if "晚自习" in content:
            content = content.replace("晚自习", "晚自习\n" + sensory_addition, 1)

    elif chapter_num == 5:
        # 在奶茶店场景增加感官细节
        sensory_addition = """
塑料杯壁上凝着一层水珠，顺着杯身往下滑。

奶茶的甜味在嘴里化开，珍珠软软的。

空调的嗡嗡声，很轻，但一直在。
"""
        if "奶茶店" in content:
            content = content.replace("奶茶店", "奶茶店\n" + sensory_addition, 1)

    new_len = len(content)

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] Chapter {chapter_num} optimized: {original_len} → {new_len} chars (+{new_len - original_len})")

# 优化第 3/4/5 章
chapters = [
    ("第 3 章_原始设定.md", 3),
    ("第 4 章_第一次心流_原始设定.md", 4),
    ("第 5 章_江越的秘密_原始设定.md", 5),
]

for filename, chapter_num in chapters:
    optimize_chapter(filename, chapter_num)

print("\n[COMPLETE] AI optimization applied to chapters 3/4/5")

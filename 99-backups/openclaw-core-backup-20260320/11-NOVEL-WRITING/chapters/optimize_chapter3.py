import os

drafts_dir = "D:/OpenClaw/workspace/50-novels/drafts"

# 找到第 3 章文件
for f in os.listdir(drafts_dir):
    if '第 3' in f and '5000' not in f:
        path = os.path.join(drafts_dir, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()

        # 增加感官细节
        sensory_addition = """
粉笔灰在阳光里飘着，像雪。

老师的声音忽远忽近。

窗外有鸟叫，两声，停了。
"""
        if "教室" in content:
            content = content.replace("教室", "教室\n" + sensory_addition, 1)

        # 减少直白情感
        content = content.replace("他很伤心", "他把头埋进臂弯")
        content = content.replace("他很难过", "他盯着地面，很久没眨眼")

        with open(path, 'w', encoding='utf-8') as file:
            file.write(content)

        print(f"[OK] Chapter 3 optimized: {f}")
        break

print("\n[COMPLETE] Chapter 3 AI optimization")

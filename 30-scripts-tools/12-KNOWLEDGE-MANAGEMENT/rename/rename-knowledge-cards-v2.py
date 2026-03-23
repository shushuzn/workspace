#!/usr/bin/env python3
"""60-knowledge-cards 文件夹规范化 - 按序号重命名"""

import os

BASE_DIR = "D:/OpenClaw/workspace/60-knowledge-cards"

# 按序号映射
SUBJECTS = {
    1: "chinese-lang",
    2: "chinese-lit",
    3: "english",
    4: "physics",
    5: "chemistry",
    6: "biology",
    7: "history",
    8: "geography",
    9: "physics-theory",
    10: "inorganic-chem",
    11: "organic-chem",
    12: "analytical-chem",
    13: "vocabulary",
    14: "grammar",
    15: "reading",
    16: "writing",
    17: "genetics",
    18: "modern-chem",
    19: "experimental",
    20: "mathematics",
    21: "chinese-history",
    22: "international",
    99: "comprehensive",
}

def main():
    folders = [f for f in os.listdir(BASE_DIR) if os.path.isdir(os.path.join(BASE_DIR, f))]
    print(f"找到 {len(folders)} 个文件夹")

    for folder in sorted(folders):
        # 提取序号
        try:
            num = int(folder.split("-")[0])
            if num in SUBJECTS:
                new_name = f"{num:02d}-{SUBJECTS[num]}"
                old_path = os.path.join(BASE_DIR, folder)
                new_path = os.path.join(BASE_DIR, new_name)

                if old_path != new_path:
                    print(f"{folder} → {new_name}")
                    os.rename(old_path, new_path)
        except (ValueError, IndexError):
            print(f"跳过：{folder}")

    print("\n完成！")

if __name__ == "__main__":
    main()

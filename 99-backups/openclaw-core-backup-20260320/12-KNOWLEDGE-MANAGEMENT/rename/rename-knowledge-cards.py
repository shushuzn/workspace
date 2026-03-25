#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
60-knowledge-cards 文件夹规范化 - 中文→英文
"""

import os

BASE_DIR = "D:/OpenClaw/workspace/60-knowledge-cards"

# 学科分类映射 (中文→英文)
MAPPING = {
    "01-语文": "01-chinese",
    "02-数学": "02-mathematics",
    "03-英语": "03-english",
    "04-物理": "04-physics",
    "05-化学": "05-chemistry",
    "06-生物": "06-biology",
    "07-历史": "07-history",
    "08-地理": "08-geography",
    "09-政治": "09-politics",
    "10-音乐": "10-music",
    "11-美术": "11-art",
    "12-体育": "12-physical-education",
    "13-信息技术": "13-information-technology",
    "14-通用技术": "14-general-technology",
    "15-心理健康": "15-mental-health",
    "16-职业生涯": "16-career-planning",
    "17-国防教育": "17-national-defense",
    "18-劳动技术": "18-labor-technology",
    "19-社会实践": "19-social-practice",
    "20-研究性学习": "20-research-learning",
    "21-中国传统文化": "21-chinese-traditional-culture",
    "22-国际理解": "22-international-understanding",
    "99-综合": "99-comprehensive",
}

def main():
    folders = os.listdir(BASE_DIR)
    print(f"找到 {len(folders)} 个文件夹")

    renamed = 0
    for folder in folders:
        # 尝试匹配中文文件夹
        for cn, en in MAPPING.items():
            if folder.startswith(cn) or cn in folder:
                old_path = os.path.join(BASE_DIR, folder)
                new_name = folder.replace(cn, en)
                new_path = os.path.join(BASE_DIR, new_name)

                if old_path != new_path and os.path.exists(old_path):
                    print(f"重命名：{folder} → {new_name}")
                    os.rename(old_path, new_path)
                    renamed += 1
                break

    print(f"\n完成！重命名 {renamed} 个文件夹")

if __name__ == "__main__":
    main()

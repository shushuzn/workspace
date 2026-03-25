#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Foreshadowing Tracker
Track foreshadowing planting and recovery status
"""

import os
import re
import json
from datetime import datetime

# Config
DRAFTS_FOLDER = r"D:\OpenClaw\workspace\50-novels\drafts"
SETTING_FILE = r"D:\OpenClaw\workspace\50-novels\15-docs\伏笔追踪设定.json"

# Default foreshadowing settings
DEFAULT_FORESHADOWING = [
    {"id": 1, "name": "游戏手柄肌肉记忆", "plant_chapters": [3, 50, 150], "recover_chapters": [300, 500, 700, 850, 900]},
    {"id": 2, "name": "炸串味道", "plant_chapters": [5, 25, 100], "recover_chapters": [300, 500, 700, 850, 900]},
    {"id": 3, "name": "茶杯缺口", "plant_chapters": [10, 59, 95], "recover_chapters": [200, 400, 600, 820, 900]},
    {"id": 4, "name": "父亲沉默", "plant_chapters": [14, 46, 200], "recover_chapters": [400, 600, 700, 800, 900]},
    {"id": 5, "name": "周越疏远", "plant_chapters": [2, 35, 100], "recover_chapters": [300, 500, 700, 750, 900]},
    {"id": 6, "name": "小数点后两位", "plant_chapters": [7, 100, 300], "recover_chapters": [500, 700, 850, 900]},
    {"id": 7, "name": "口头禅演变", "plant_chapters": [1, 50, 200], "recover_chapters": [400, 600, 800, 900]},
    {"id": 8, "name": "未发出的消息", "plant_chapters": [9, 100, 300], "recover_chapters": [700, 850, 900]},
    {"id": 9, "name": "眼镜度数", "plant_chapters": [105, 200, 400], "recover_chapters": [600, 700, 800, 900]},
    {"id": 10, "name": "自行车", "plant_chapters": [14, 100, 200], "recover_chapters": [400, 600, 700, 900]},
    {"id": 11, "name": "闹钟时间", "plant_chapters": [51, 200, 400], "recover_chapters": [600, 700, 800, 900]},
    {"id": 12, "name": "书架位置", "plant_chapters": [70, 200, 400], "recover_chapters": [600, 800, 850, 900]},
    {"id": 13, "name": "签名变化", "plant_chapters": [50, 200, 400], "recover_chapters": [600, 700, 900]},
    {"id": 14, "name": "咖啡/茶偏好", "plant_chapters": [150, 300, 400], "recover_chapters": [500, 600, 900]},
    {"id": 15, "name": "照片墙", "plant_chapters": [100, 300, 500], "recover_chapters": [700, 800, 850, 900]},
]

def load_foreshadowing_settings():
    """Load foreshadowing settings"""
    if os.path.exists(SETTING_FILE):
        with open(SETTING_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return DEFAULT_FORESHADOWING

def scan_chapter_for_foreshadowing(chapter_num, content):
    """Scan single chapter for foreshadowing"""
    found = []

    # Simple keyword matching (can be enhanced)
    keywords = {
        1: ['拇指', '滑动', '游戏', '肌肉记忆'],
        2: ['炸串', '味道', '巷口'],
        3: ['茶杯', '缺口', '苏师'],
        4: ['父亲', '沉默', '叹气'],
        5: ['周越', '疏远', '背影'],
        6: ['小数点', '两位', '精确'],
        7: ['口头禅', '随便', '知道了'],
        8: ['消息', '未发出', '草稿箱'],
        9: ['眼镜', '度数', '视力'],
        10: ['自行车', '车链', '骑车'],
        11: ['闹钟', '时间', '起床'],
        12: ['书架', '位置', '书'],
        13: ['签名', 'QQ', '状态'],
        14: ['咖啡', '茶', '饮料'],
        15: ['照片', '墙', '回忆'],
    }

    for f_id, words in keywords.items():
        for word in words:
            if word in content:
                found.append(f_id)
                break

    return list(set(found))

def track_foreshadowing():
    """Track all foreshadowing"""
    print("=" * 60)
    print("Foreshadowing Tracker Report")
    print("=" * 60)
    print(f"Folder: {DRAFTS_FOLDER}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    print()

    foreshadowing_settings = load_foreshadowing_settings()

    # Scan all chapters
    draft_files = []
    for file in os.listdir(DRAFTS_FOLDER):
        if file.endswith('.md') and file.startswith('第'):
            match = re.search(r'第 (\d+) 章', file)
            if match:
                chapter_num = int(match.group(1))
                draft_files.append((chapter_num, os.path.join(DRAFTS_FOLDER, file)))

    draft_files.sort(key=lambda x: x[0])

    # Track foreshadowing
    tracking_results = {}
    for f in foreshadowing_settings:
        tracking_results[f['id']] = {
            'name': f['name'],
            'plant_status': [],
            'recover_status': [],
        }

    for chapter_num, file_path in draft_files:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        found = scan_chapter_for_foreshadowing(chapter_num, content)

        for f_id in found:
            if f_id in tracking_results:
                if chapter_num in foreshadowing_settings[f_id -1]['plant_chapters']:
                    tracking_results[f_id]['plant_status'].append(chapter_num)
                if chapter_num in foreshadowing_settings[f_id -1]['recover_chapters']:
                    tracking_results[f_id]['recover_status'].append(chapter_num)

    # Print report
    print("Foreshadowing Status:")
    print("-" * 60)
    print(f"{'ID':<5} {'Name':<20} {'Planted':<15} {'Recovered':<15} {'Status':<10}")
    print("-" * 60)

    for f in foreshadowing_settings:
        f_id = f['id']
        name = f['name'][:18].ljust(20)

        planted = tracking_results[f_id]['plant_status']
        recovered = tracking_results[f_id]['recover_status']

        planted_str = ','.join(map(str, planted)) if planted else 'None'
        recovered_str = ','.join(map(str, recovered)) if recovered else 'None'

        # Determine status
        expected_plant = len(f['plant_chapters'])
        expected_recover = len(f['recover_chapters'])

        if len(planted) == expected_plant and len(recovered) == expected_recover:
            status = '✅ Complete'
        elif len(planted) > 0:
            status = '⏳ In Progress'
        else:
            status = '❌ Not Started'

        print(f"{f_id:<5} {name} {planted_str:<15} {recovered_str:<15} {status}")

    print("-" * 60)
    print()

    # Save report
    report_file = os.path.join(DRAFTS_FOLDER, "foreshadowing_report.json")
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(tracking_results, f, ensure_ascii=False, indent=2)

    print(f"Report saved to: {report_file}")
    print()
    print("=" * 60)

if __name__ == "__main__":
    track_foreshadowing()

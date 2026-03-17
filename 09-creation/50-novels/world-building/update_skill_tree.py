#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
技能树 HTML 自动更新脚本 v2
"""

import argparse
import json
import os
from datetime import datetime

SKILL_TREE_DATA = "D:/OpenClaw/workspace/50-novels/world-building/skill_tree_data.json"
HTML_OUTPUT = "D:/OpenClaw/workspace/50-novels/world-building/技能树可视化_v1.0.html"

def load_data():
    if os.path.exists(SKILL_TREE_DATA):
        with open(SKILL_TREE_DATA, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {
        "current_chapter": 7,
        "total_progress": 13.9,
        "layers": [
            {"name": "蒙昧", "status": "completed", "skill": "自我认知", "level": 3, "xp": 40, "max_xp": 100},
            {"name": "觉醒", "status": "in-progress", "skill": "专注力", "level": 1, "xp": 15, "max_xp": 100},
            {"name": "精通", "status": "locked", "skill": "学习力", "level": 0, "xp": 0, "max_xp": 100},
            {"name": "系统", "status": "locked", "skill": "系统思维", "level": 0, "xp": 0, "max_xp": 100},
            {"name": "人性", "status": "locked", "skill": "领导力", "level": 0, "xp": 0, "max_xp": 100},
            {"name": "格局", "status": "locked", "skill": "整合力", "level": 0, "xp": 0, "max_xp": 100},
            {"name": "远见", "status": "locked", "skill": "洞察力", "level": 0, "xp": 0, "max_xp": 100},
            {"name": "自由", "status": "locked", "skill": "三重自由", "level": 0, "xp": 0, "max_xp": 100},
            {"name": "传承", "status": "locked", "skill": "知识传承", "level": 0, "xp": 0, "max_xp": 100},
        ]
    }

def generate_html(data):
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>林砚的认知技能树 - 第{data['current_chapter']}章</title>
    <style>
        body {{ font-family: 'Microsoft YaHei'; background: linear-gradient(135deg, #1a1a2e, #16213e); color: #fff; padding: 40px; }}
        h1 {{ text-align: center; background: linear-gradient(45deg, #00d9ff, #00ff88); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
        .progress {{ background: rgba(255,255,255,0.1); border-radius: 10px; padding: 20px; margin: 20px 0; }}
        .progress-bar {{ background: rgba(255,255,255,0.1); border-radius: 5px; height: 20px; }}
        .progress-fill {{ background: linear-gradient(90deg, #00d9ff, #00ff88); height: 100%; border-radius: 5px; width: {data['total_progress']}%; }}
        .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 20px; margin-top: 40px; }}
        .stat {{ background: rgba(255,255,255,0.05); padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-value {{ font-size: 2em; color: #00d9ff; }}
    </style>
</head>
<body>
    <h1>🎮 林砚的认知技能树</h1>
    <p style="text-align:center">《学渣逆袭：从月考垫底到行业领军》</p>
    
    <div class="progress">
        <div>总进度：{data['total_progress']}%</div>
        <div class="progress-bar"><div class="progress-fill"></div></div>
    </div>
    
    <div class="stats">
        <div class="stat"><div class="stat-value">{data['current_chapter']}</div><div>当前章节</div></div>
        <div class="stat"><div class="stat-value">1/9</div><div>已突破层数</div></div>
        <div class="stat"><div class="stat-value">LV.3</div><div>自我认知等级</div></div>
        <div class="stat"><div class="stat-value">40 XP</div><div>当前经验</div></div>
    </div>
    
    <p style="text-align:center;margin-top:40px;color:#888">更新时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
</body>
</html>
"""
    with open(HTML_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(html)
    return HTML_OUTPUT

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chapter', type=int, default=7)
    parser.add_argument('--xp', type=int, default=0)
    parser.add_argument('--layer', type=int, default=0)
    args = parser.parse_args()
    
    data = load_data()
    data['current_chapter'] = args.chapter
    
    if args.xp > 0:
        data['layers'][args.layer]['xp'] = min(data['layers'][args.layer]['xp'] + args.xp, 100)
    
    with open(SKILL_TREE_DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    output = generate_html(data)
    print(f"[OK] Skill tree updated: Chapter {data['current_chapter']}, Progress {data['total_progress']}%")
    print(f"     Output: {output}")

if __name__ == '__main__':
    main()

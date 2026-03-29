#!/usr/bin/env python3
"""分批下载 OpenClaw 技能 - 使用并行下载和重试机制"""

import os
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import quote

# 配置
RAW_GITHUB = "https://raw.githubusercontent.com/openclaw/skills/main"
OUTPUT_DIR = "D:/OpenClaw/workspace/active_skills"
SKILLS_LIST_FILE = "all-skills-list.txt"

# 请求头
HEADERS = {
    "User-Agent": "OpenClaw-Skill-Installer/1.0",
    "Accept": "*/*"
}

def load_skills_list():
    """加载技能列表"""
    skills = []
    with open(SKILLS_LIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]
        for line in lines:
            parts = line.strip().split('|')
            if len(parts) >= 2:
                skills.append({
                    'slug': parts[0],
                    'name': parts[1],
                    'category': parts[2] if len(parts) > 2 else 'unknown'
                })
    return skills

def download_file(url, output_path, retries=3):
    """下载文件，带重试"""
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=30)
            if resp.status_code == 200:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(resp.text)
                return True
            elif resp.status_code == 404:
                return False  # 文件不存在，不需要重试
            else:
                time.sleep(1)  # 等待后重试
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
    return False

def install_skill(skill):
    """安装单个技能"""
    slug = skill['slug']
    output_dir = os.path.join(OUTPUT_DIR, slug)
    
    # 如果已存在且有内容，跳过
    if os.path.exists(output_dir):
        files = [f for f in os.listdir(output_dir) if os.path.isfile(os.path.join(output_dir, f))]
        if len(files) > 0:
            return {'slug': slug, 'status': 'skipped', 'files': len(files)}
    else:
        os.makedirs(output_dir, exist_ok=True)
    
    # 下载核心文件
    files_to_download = ['SKILL.md', 'skill.json', 'README.md', 'package.json']
    downloaded = 0
    
    for filename in files_to_download:
        url = f"{RAW_GITHUB}/skills/{slug}/{filename}"
        output_path = os.path.join(output_dir, filename)
        if download_file(url, output_path):
            downloaded += 1
    
    if downloaded > 0:
        return {'slug': slug, 'status': 'success', 'files': downloaded}
    else:
        # 没有下载到任何文件，可能是空的或不存在
        return {'slug': slug, 'status': 'empty', 'files': 0}

def main():
    """主函数"""
    print("🚀 开始分批安装 OpenClaw 技能...")
    
    # 加载技能列表
    skills = load_skills_list()
    print(f"📋 共 {len(skills)} 个技能待处理")
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 统计
    stats = {
        'success': 0,
        'skipped': 0,
        'empty': 0,
        'error': 0
    }
    
    # 分批安装
    batch_size = 100
    total_batches = (len(skills) + batch_size - 1) // batch_size
    
    for batch_num in range(total_batches):
        start_idx = batch_num * batch_size
        end_idx = min(start_idx + batch_size, len(skills))
        batch = skills[start_idx:end_idx]
        
        print(f"\n📦 批次 {batch_num + 1}/{total_batches} ({start_idx + 1}-{end_idx}/{len(skills)})")
        
        # 并行安装
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = {executor.submit(install_skill, skill): skill for skill in batch}
            for future in as_completed(futures):
                skill = futures[future]
                try:
                    result = future.result()
                    stats[result['status']] += 1
                    
                    # 每 50 个输出一次进度
                    total = sum(stats.values())
                    if total % 50 == 0:
                        print(f"  📊 进度: {total}/{len(skills)} | ✅ 成功: {stats['success']} | ⏭️ 跳过: {stats['skipped']} | ⚠️ 空: {stats['empty']}")
                except Exception as e:
                    stats['error'] += 1
        
        # 批次间等待
        if batch_num < total_batches - 1:
            print(f"  ⏳ 等待 3 秒...")
            time.sleep(3)
    
    # 最终报告
    print(f"\n{'='*60}")
    print(f"📊 安装完成!")
    print(f"  ✅ 成功安装: {stats['success']}")
    print(f"  ⏭️ 已存在跳过: {stats['skipped']}")
    print(f"  ⚠️ 空技能: {stats['empty']}")
    print(f"  ❌ 错误: {stats['error']}")
    print(f"  📁 目录: {OUTPUT_DIR}")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
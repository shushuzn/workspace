#!/usr/bin/env python3
"""批量安装 OpenClaw 技能"""

import os
import requests
import time
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
GITHUB_API = "https://api.github.com/repos/openclaw/skills"
RAW_GITHUB = "https://raw.githubusercontent.com/openclaw/skills/main"
OUTPUT_DIR = "D:/OpenClaw/workspace/active_skills"
SKILLS_LIST_FILE = "all-skills-list.txt"

# 请求头（避免速率限制）
HEADERS = {
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "OpenClaw-Skill-Installer"
}

def load_skills_list():
    """加载技能列表"""
    skills = []
    with open(SKILLS_LIST_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()[1:]  # 跳过标题行
        for line in lines:
            parts = line.strip().split('|')
            if len(parts) >= 2:
                skills.append({
                    'slug': parts[0],
                    'name': parts[1],
                    'category': parts[2] if len(parts) > 2 else 'unknown'
                })
    return skills

def get_skill_contents(skill_slug):
    """获取技能目录内容"""
    url = f"{GITHUB_API}/contents/skills/{skill_slug}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            return resp.json()
        elif resp.status_code == 404:
            print(f"  ⚠️ 技能不存在: {skill_slug}")
            return None
        else:
            print(f"  ❌ API 错误 {resp.status_code}: {skill_slug}")
            return None
    except Exception as e:
        print(f"  ❌ 网络错误: {skill_slug} - {e}")
        return None

def download_file(skill_slug, filename, output_dir):
    """下载单个文件"""
    url = f"{RAW_GITHUB}/skills/{skill_slug}/{filename}"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        if resp.status_code == 200:
            filepath = os.path.join(output_dir, filename)
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(resp.text)
            return True
        return False
    except:
        return False

def install_skill(skill):
    """安装单个技能"""
    slug = skill['slug']
    output_dir = os.path.join(OUTPUT_DIR, slug)
    
    # 创建目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 获取技能内容
    contents = get_skill_contents(slug)
    if not contents:
        return False
    
    # 下载所有文件
    success = 0
    for item in contents:
        if item['type'] == 'file':
            if download_file(slug, item['name'], output_dir):
                success += 1
    
    return success > 0

def main():
    """主函数"""
    print("🚀 开始批量安装 OpenClaw 技能...")
    
    # 加载技能列表
    skills = load_skills_list()
    print(f"📋 共 {len(skills)} 个技能待安装")
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # 统计
    installed = 0
    failed = 0
    
    # 分批安装（避免 API 速率限制）
    batch_size = 50
    for i in range(0, len(skills), batch_size):
        batch = skills[i:i+batch_size]
        print(f"\n📦 安装批次 {i//batch_size + 1}/{(len(skills)-1)//batch_size + 1}")
        
        # 并行安装
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(install_skill, skill): skill for skill in batch}
            for future in as_completed(futures):
                skill = futures[future]
                try:
                    if future.result():
                        installed += 1
                        if installed % 10 == 0:
                            print(f"  ✅ 已安装: {installed}/{len(skills)}")
                    else:
                        failed += 1
                except Exception as e:
                    failed += 1
                    print(f"  ❌ 安装失败: {skill['slug']} - {e}")
        
        # 避免速率限制
        if i + batch_size < len(skills):
            print("  ⏳ 等待 2 秒...")
            time.sleep(2)
    
    # 最终报告
    print(f"\n{'='*50}")
    print(f"📊 安装完成!")
    print(f"  ✅ 成功: {installed}")
    print(f"  ❌ 失败: {failed}")
    print(f"  📁 目录: {OUTPUT_DIR}")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
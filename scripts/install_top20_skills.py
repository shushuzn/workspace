#!/usr/bin/env python3
"""安装 awesome-openclaw-skills 前20个 Coding Agents & IDEs 技能"""

import os
import subprocess
import time

# 前20个技能的 GitHub 仓库 URL (openclaw/skills 仓库的子目录)
SKILLS = [
    ("0g-compute", "https://github.com/openclaw/skills/tree/main/skills/in-liberty420/0g-compute"),
    ("0protocol", "https://github.com/openclaw/skills/tree/main/skills/0isone/0protocol"),
    ("2nd-brain", "https://github.com/openclaw/skills/tree/main/skills/coderaven/2nd-brain"),
    ("2slides-skills", "https://github.com/openclaw/skills/tree/main/skills/javainthinking/2slides-skills"),
    ("3d-cog", "https://github.com/openclaw/skills/tree/main/skills/nitishgargiitd/3d-cog"),
    ("3d-model-generation", "https://github.com/openclaw/skills/tree/main/skills/eftalyurtseven/3d-model-generation"),
    ("a", "https://github.com/openclaw/skills/tree/main/skills/ricketh137/a"),
    ("aade-api-monitor", "https://github.com/openclaw/skills/tree/main/skills/satoshistackalotto/aade-api-monitor"),
    ("abaddon", "https://github.com/openclaw/skills/tree/main/skills/enochosbot-bot/abaddon"),
    ("academic-research", "https://github.com/openclaw/skills/tree/main/skills/rogersuperbuilderalpha/academic-research"),
    ("academic-research-hub", "https://github.com/openclaw/skills/tree/main/skills/anisafifi/academic-research-hub"),
    ("acestep-simplemv", "https://github.com/openclaw/skills/tree/main/skills/dumoedss/acestep-simplemv"),
    ("acestep-songwriting", "https://github.com/openclaw/skills/tree/main/skills/dumoedss/acestep-songwriting"),
    ("achurch", "https://github.com/openclaw/skills/tree/main/skills/lucasgeeksinthewood/achurch"),
    ("active-maintenance", "https://github.com/openclaw/skills/tree/main/skills/xiaowenzhou/active-maintenance"),
    ("adblock-dns", "https://github.com/openclaw/skills/tree/main/skills/picaye/adblock-dns"),
    ("add-top-openrouter-models", "https://github.com/openclaw/skills/tree/main/skills/chunhualiao/add-top-openrouter-models"),
    ("adhd-founder-planner", "https://github.com/openclaw/skills/tree/main/skills/jankutschera/adhd-founder-planner"),
    ("adwhiz", "https://github.com/openclaw/skills/tree/main/skills/iamzifei/adwhiz"),
    ("aeo-prompt-question-finder", "https://github.com/openclaw/skills/tree/main/skills/psyduckler/aeo-prompt-question-finder"),
]

OUTPUT_DIR = "D:/OpenClaw/workspace/active_skills"

def download_skill(name, repo_url):
    """下载技能文件夹"""
    skill_dir = os.path.join(OUTPUT_DIR, name)
    
    # 如果已存在，跳过
    if os.path.exists(skill_dir):
        print(f"⏭️  跳过 {name} (已存在)")
        return True
    
    print(f"📦 正在安装: {name}...")
    
    # 从 GitHub URL 提取仓库和路径
    # URL 格式: https://github.com/openclaw/skills/tree/main/skills/author/skill-name
    parts = repo_url.replace("https://github.com/", "").split("/")
    # parts = ['openclaw', 'skills', 'tree', 'main', 'skills', 'author', 'skill-name']
    author = parts[5]
    repo_path = f"skills/{author}/{name}"
    
    raw_url = f"https://raw.githubusercontent.com/openclaw/skills/main/{repo_path}/SKILL.md"
    
    print(f"   检查: {raw_url}")
    
    try:
        # 检查 SKILL.md 是否存在
        result = subprocess.run(
            ["curl", "-s", "-o", "NUL", "-w", "%{http_code}", raw_url],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0 and result.stdout.strip() == "200":
            # 使用 git sparse-checkout 只克隆特定目录
            print(f"   ✅ 技能存在: {name}")
            
            # 创建技能目录
            os.makedirs(skill_dir, exist_ok=True)
            
            # 下载 SKILL.md
            subprocess.run(
                ["curl", "-s", "-o", f"{skill_dir}/SKILL.md", raw_url],
                capture_output=True,
                timeout=30
            )
            
            # 下载其他文件
            for filename in ["README.md", "install.sh", "requirements.txt"]:
                file_url = f"https://raw.githubusercontent.com/openclaw/skills/main/{repo_path}/{filename}"
                result = subprocess.run(
                    ["curl", "-s", "-o", "NUL", "-w", "%{http_code}", file_url],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode == 0 and result.stdout.strip() == "200":
                    subprocess.run(
                        ["curl", "-s", "-o", f"{skill_dir}/{filename}", file_url],
                        capture_output=True,
                        timeout=30
                    )
            
            print(f"   ✅ 成功安装: {name}")
            return True
        else:
            print(f"   ❌ 技能不存在: {name} (HTTP {result.stdout.strip()})")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"   ❌ 超时: {name}")
        return False
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return False

def main():
    print("=" * 60)
    print("安装 awesome-openclaw-skills 前20个 Coding Agents & IDEs 技能")
    print("=" * 60)
    print()
    
    # 确保输出目录存在
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    success_count = 0
    fail_count = 0
    
    for i, (name, url) in enumerate(SKILLS, 1):
        print(f"[{i}/20] ", end="")
        if download_skill(name, url):
            success_count += 1
        else:
            fail_count += 1
        print()
        time.sleep(0.5)  # 避免过快请求
    
    print("=" * 60)
    print(f"安装完成! 成功: {success_count}, 失败: {fail_count}")
    print("=" * 60)

if __name__ == "__main__":
    main()
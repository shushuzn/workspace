#!/usr/bin/env python3
"""
Research Report Generator
自动生成周报/月报，汇总 Arxiv、Medium、Twitter、Reddit 等来源
输出到 Obsidian vault
"""

import sys
import os
import re
import json
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from pathlib import Path

# Windows UTF-8 编码支持
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ============ 配置 ============
WORKSPACE = str(Path(__file__).parent.parent)
OUTPUT_DIR = os.path.join(WORKSPACE, "reports")

# 数据源目录
SOURCES = {
    "arxiv": os.path.join(WORKSPACE, "Arxiv"),
    "medium": os.path.join(WORKSPACE, "Medium"),
    "twitter": os.path.join(WORKSPACE, "X-Twitter"),
    "reddit": os.path.join(WORKSPACE, "Reddit"),
    "hackernews": os.path.join(WORKSPACE, "HackerNews")
}

# ============ 工具函数 ============
def log(msg: str):
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def get_date_range(report_type: str) -> Tuple[datetime, datetime]:
    """获取报告日期范围"""
    today = datetime.now()

    if report_type == "weekly":
        # 本周一到周日
        start = today - timedelta(days=today.weekday())
        end = start + timedelta(days=6)
    elif report_type == "monthly":
        # 本月 1 号到月末
        start = today.replace(day=1)
        if today.month == 12:
            end = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            end = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
    else:
        # 默认最近 7 天
        start = today - timedelta(days=7)
        end = today

    return start, end

def find_markdown_files(directory: str, start: datetime, end: datetime) -> List[str]:
    """查找指定日期范围内的 Markdown 文件"""
    files = []

    if not os.path.exists(directory):
        return files

    # 遍历目录
    for root, dirs, filenames in os.walk(directory):
        # 跳过 archive 目录
        if '_archive' in root or 'archive' in root:
            continue

        for filename in filenames:
            if not filename.endswith('.md'):
                continue

            filepath = os.path.join(root, filename)

            # 检查文件日期
            try:
                # 从文件名提取日期
                date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filename)
                if date_match:
                    file_date = datetime.strptime(date_match.group(1), '%Y-%m-%d')
                    if start <= file_date <= end:
                        files.append(filepath)
                else:
                    # 使用文件修改时间
                    mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                    if start <= mtime <= end:
                        files.append(filepath)
            except Exception as e:
                log(f"⚠️ 解析 {filename} 失败：{e}")

    return sorted(files, reverse=True)

def extract_frontmatter(filepath: str) -> Dict:
    """提取 Markdown 文件的 YAML frontmatter"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                frontmatter = content[4:end].strip()
                metadata = {}
                for line in frontmatter.split('\n'):
                    if ':' in line:
                        key, value = line.split(':', 1)
                        metadata[key.strip()] = value.strip()
                return metadata
    except Exception as e:
        log(f"⚠️ 读取 frontmatter 失败 {filepath}: {e}")

    return {}

def extract_content(filepath: str, max_lines: int = 50) -> str:
    """提取 Markdown 文件内容（前 N 行）"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # 跳过 frontmatter
        content_lines = []
        in_frontmatter = False
        for line in lines:
            if line.strip() == '---':
                in_frontmatter = not in_frontmatter
                continue
            if not in_frontmatter:
                content_lines.append(line)

        return ''.join(content_lines[:max_lines])
    except Exception as e:
        log(f"⚠️ 读取内容失败 {filepath}: {e}")
        return ""

# ============ 报告生成 ============
def generate_weekly_report(start: datetime, end: datetime) -> str:
    """生成周报"""
    report_date = datetime.now().strftime("%Y-%m-%d")
    week_num = start.isocalendar()[1]

    report = f"""# 研究周报 - 第{week_num}周 ({start.strftime('%Y-%m-%d')} ~ {end.strftime('%Y-%m-%d')})

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**报告周期:** {start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}

---

## 📊 概览

"""

    stats = {}
    for source_name, source_dir in SOURCES.items():
        files = find_markdown_files(source_dir, start, end)
        stats[source_name] = len(files)
        report += f"- **{source_name.capitalize()}:** {len(files)} 篇\n"

    total = sum(stats.values())
    report += f"\n**总计:** {total} 篇内容\n\n---\n\n"

    # 各来源详情
    for source_name, source_dir in SOURCES.items():
        files = find_markdown_files(source_dir, start, end)

        if not files:
            continue

        report += f"## 📚 {source_name.capitalize()}\n\n"

        for filepath in files[:10]:  # 最多 10 篇
            filename = os.path.basename(filepath)
            metadata = extract_frontmatter(filepath)

            title = metadata.get('title', filename.replace('.md', ''))
            tags = metadata.get('tags', '')
            date = metadata.get('date', '')

            report += f"### {title}\n\n"
            if tags:
                report += f"🏷️ {tags}\n\n"
            if date:
                report += f"📅 {date}\n\n"
            report += f"📁 `{filename}`\n\n"
            report += "---\n\n"

    # 关键洞察
    report += """## 💡 关键洞察

（此处手动填写本周最重要的发现/趋势/思考）

### 技术趋势
- 

### 值得关注
- 

### 待深入研究
- 

---

## 📋 下周计划

- [ ] 
- [ ] 
- [ ] 

---

**报告结束时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
""".replace('{datetime.now().strftime(\'%Y-%m-%d %H:%M:%S\')}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))

    return report

def generate_monthly_report(start: datetime, end: datetime) -> str:
    """生成月报"""
    report_date = datetime.now().strftime("%Y-%m-%d")
    month_name = start.strftime("%Y年%m月")

    report = f"""# 研究月报 - {month_name}

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**报告周期:** {start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}

---

## 📊 月度概览

"""

    stats = {}
    for source_name, source_dir in SOURCES.items():
        files = find_markdown_files(source_dir, start, end)
        stats[source_name] = len(files)
        report += f"- **{source_name.capitalize()}:** {len(files)} 篇\n"

    total = sum(stats.values())
    report += f"\n**月度总计:** {total} 篇内容\n\n---\n\n"

    # 每周汇总
    report += "## 📅 周度分解\n\n"
    current = start
    week_num = 1
    while current <= end:
        week_end = min(current + timedelta(days=6), end)
        week_files = []
        for source_dir in SOURCES.values():
            week_files.extend(find_markdown_files(source_dir, current, week_end))
        report += f"- **第{week_num}周** ({current.strftime('%m-%d')} ~ {week_end.strftime('%m-%d')}): {len(week_files)} 篇\n"
        current = week_end + timedelta(days=1)
        week_num += 1

    report += "\n---\n\n"

    # 热点话题
    report += """## 🔥 热点话题

（基于标签/关键词统计）

### 高频关键词
- 
- 
- 

---

## 📈 趋势分析

### 技术趋势
- 

### 研究方向
- 

---

## 💡 月度洞察

### 最重要的发现
1. 
2. 
3. 

### 值得关注的进展
- 

### 下月重点
- 

---

**报告结束时间:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return report

# ============ 主流程 ============
def main():
    import sys

    report_type = sys.argv[1] if len(sys.argv) > 1 else "weekly"

    log(f"🚀 生成{report_type}报告")

    start, end = get_date_range(report_type)
    log(f"📅 日期范围：{start.strftime('%Y-%m-%d')} - {end.strftime('%Y-%m-%d')}")

    # 创建输出目录
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # 生成报告
    if report_type == "monthly":
        report = generate_monthly_report(start, end)
        filename = f"monthly-report-{datetime.now().strftime('%Y-%m')}.md"
    else:
        report = generate_weekly_report(start, end)
        week_num = start.isocalendar()[1]
        filename = f"weekly-report-{start.strftime('%Y')}-w{week_num:02d}.md"

    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    log(f"💾 报告已保存到 {filepath}")
    log("✅ 完成")

if __name__ == "__main__":
    main()

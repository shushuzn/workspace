#!/usr/bin/env python3
# daily-brief.py - 每日简报自动生成
# 用法：py daily-brief.py [--date YYYY-MM-DD] [--send]

import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

import argparse
import subprocess
import os
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("D:/OpenClaw/workspace")
BRIEF_DIR = WORKSPACE / "21-reports/daily-briefs"
MEMORY_DIR = WORKSPACE / "13-memory"

def get_date(args_date):
    if args_date:
        return args_date
    return (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

def count_files(directory, pattern="*.md"):
    """统计目录中文件数量"""
    if not os.path.exists(directory):
        return 0, []
    files = list(Path(directory).glob(pattern))
    # 过滤临时文件
    files = [f for f in files if not f.name.endswith("~")]
    return len(files), files

def get_arxiv_data(date):
    """收集 arXiv 数据"""
    arxiv_dir = WORKSPACE / "40-arxiv/papers" / date
    count, files = count_files(arxiv_dir)
    high_priority = len([f for f in files if "high" in f.name.lower() or "priority" in f.name.lower()])
    return count, high_priority, files[:5]  # 返回前 5 个文件

def get_medium_data(date):
    """收集 Medium 数据"""
    medium_dir = WORKSPACE / "41-medium/analyzed" / date
    count, files = count_files(medium_dir)
    # 深度解析 = 包含 "## Core question" 的文章
    deep_count = 0
    for f in files:
        try:
            content = f.read_text(encoding="utf-8")
            if "## Core question" in content or "## 1. Core question" in content:
                deep_count += 1
        except Exception:
            pass
    return count, deep_count

def get_github_status():
    """检查 GitHub 状态"""
    try:
        os.chdir(WORKSPACE)

        # 检查是否为 git 仓库
        result = subprocess.run(
            ["git", "rev-parse", "--git-dir"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            return 0, "⚠️ 非 Git 仓库"

        # 获取今日提交数
        result = subprocess.run(
            ["git", "log", "--since=yesterday", "--oneline"],
            capture_output=True, text=True, timeout=10
        )
        commits = 0
        if result.stdout and result.stdout.strip():
            commits = len(result.stdout.strip().split("\n"))

        # 检查未推送提交 (需要 upstream 分支)
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "@{u}"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode != 0:
            # 无 upstream 分支
            return commits, "⚠️ 无 upstream"

        # 检查未推送提交数
        result = subprocess.run(
            ["git", "rev-list", "--count", "@{u}..HEAD"],
            capture_output=True, text=True, timeout=10
        )
        unpushed = 0
        if result.stdout and result.stdout.strip():
            try:
                unpushed = int(result.stdout.strip())
            except ValueError:
                unpushed = 0

        status = "✅" if unpushed == 0 else f"⚠️ 待推送 ({unpushed})"
        return commits, status
    except FileNotFoundError:
        return 0, "❌ Git 未安装"
    except Exception as e:
        return 0, f"❌ 检查失败：{type(e).__name__}"

def get_domain_rankings():
    """获取领域排名"""
    try:
        os.chdir(WORKSPACE)
        result = subprocess.run(
            ["py", "30-scripts/domain_ranker_v2.py", "--compare"],
            capture_output=True, text=True, timeout=30, encoding="utf-8"
        )
        top_domains = []
        for line in result.stdout.split("\n"):
            # 解析格式：1    DeepLearning         [IRON] 黑铁 717
            if "[IRON]" in line and "黑铁" in line:
                parts = line.split()
                if len(parts) >= 5:
                    rank = parts[0]
                    domain = parts[1]
                    level = parts[4]  # 黑铁后面的数字
                    top_domains.append((rank, domain, level))
                    if len(top_domains) >= 3:
                        break
        return top_domains
    except Exception as e:
        return []

def get_pending_items():
    """获取待处理事项"""
    pending = {}

    # 待解析论文
    queued_dir = WORKSPACE / "40-arxiv/queued"
    pending["parse"] = count_files(queued_dir)[0]

    # Git 待提交
    try:
        os.chdir(WORKSPACE)
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True, text=True, timeout=10
        )
        pending["git"] = len([l for l in result.stdout.split("\n") if l.strip()])
    except Exception:
        pending["git"] = 0

    return pending

def get_hackernews():
    """获取 HackerNews 热门讨论"""
    import requests

    try:
        # 获取 Top 20 故事
        response = requests.get("https://hacker-news.firebaseio.com/v0/topstories.json", timeout=30)
        story_ids = response.json()[:20]

        stories = []
        for story_id in story_ids[:10]:  # 取前 10 个
            story_resp = requests.get(f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json", timeout=15)
            story = story_resp.json()
            if story and story.get("title"):
                stories.append({
                    "title": story["title"],
                    "url": story.get("url", f"https://news.ycombinator.com/item?id={story_id}"),
                    "score": story.get("score", 0),
                    "comments": story.get("descendants", 0)
                })

        return stories[:5]  # 返回前 5 个
    except Exception as e:
        return []

def get_weather():
    """获取香港天气 (多源备份)"""
    import requests

    # 源 1: wttr.in (主源)
    try:
        response = requests.get(
            "http://wttr.in/HongKong?format=%C+%t+%h",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0 (OpenClaw Weather Bot)"},
            proxies=None  # 不使用代理
        )
        if response.status_code == 200 and response.text.strip():
            weather_text = response.text.strip()
            # 检查是否返回了有效数据 (不是错误信息)
            if "Unknown location" not in weather_text and "Error" not in weather_text:
                return weather_text
    except Exception as e:
        pass

    # 源 2: wttr.in 中文版本
    try:
        response = requests.get(
            "http://wttr.in/香港？format=%C+%t+%h",
            timeout=15,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        if response.status_code == 200 and response.text.strip():
            return response.text.strip()
    except Exception:
        pass

    # 源 3: Open-Meteo (备用)
    try:
        response = requests.get(
            "https://api.open-meteo.com/v1/forecast?latitude=22.3193&longitude=114.1694&current_weather=true",
            timeout=15
        )
        if response.status_code == 200:
            data = response.json()
            current = data.get("current_weather", {})
            temp = current.get("temperature", "N/A")
            wind = current.get("windspeed", "N/A")
            code = current.get("weathercode", 0)

            # 简单天气代码转换
            weather_map = {
                0: "☀️ 晴", 1: "🌤️ 多云", 2: "⛅ 阴", 3: "☁️ 多云",
                45: "🌫️ 雾", 48: "🌫️ 雾凇",
                51: "🌧️ 毛毛雨", 53: "🌧️ 小雨", 55: "🌧️ 大雨",
                61: "🌧️ 小雨", 63: "🌧️ 中雨", 65: "🌧️ 大雨",
                80: "🌦️ 阵雨", 81: "🌦️ 中阵雨", 82: "⛈️ 大阵雨",
                95: "⛈️ 雷雨", 96: "⛈️ 雷阵雨", 99: "⛈️ 大雷阵雨"
            }
            weather_desc = weather_map.get(code, f"代码{code}")

            return f"{weather_desc} {temp}°C 风{wind}km/h"
    except Exception:
        pass

    # 所有源都失败
    return "⚠️ 天气数据暂不可用"

def get_calendar_events():
    """获取今日日历事件 (多源支持)"""
    events = []
    today = datetime.now().strftime("%Y-%m-%d")
    today_display = datetime.now().strftime("%m 月%d 日")

    # 源 1: 本地 Markdown 日历文件
    calendar_file = WORKSPACE / "13-memory" / "calendar.md"
    if calendar_file.exists():
        try:
            lines = calendar_file.read_text(encoding="utf-8").split("\n")
            in_today_section = False

            for line in lines:
                # 检查是否进入今日 section
                if line.strip().startswith(f"## {today}"):
                    in_today_section = True
                    continue

                # 检查是否进入下一天 section
                if in_today_section and line.strip().startswith("## "):
                    break

                # 提取事件
                if in_today_section and line.strip().startswith("- ["):
                    # 解析：- [ ] 事件名 @时间 #标签
                    event_text = line.strip()[5:].strip()  # 移除 "- [ ] " (5 字符)

                    # 提取标签 (先提取，避免被时间分割影响)
                    category = "other"
                    if " #" in event_text:
                        parts = event_text.split(" #")
                        event_text = parts[0].strip()
                        category = parts[1].strip().split()[0] if parts[1] else "other"

                    # 提取时间
                    time = ""
                    if " @" in event_text:
                        parts = event_text.split(" @")
                        event_text = parts[0].strip()
                        time = parts[1].strip().split()[0] if parts[1] else ""

                    # 分类图标
                    icons = {
                        "meeting": "👥", "deadline": "⏰", "personal": "🏠",
                        "work": "💼", "research": "🔬", "other": "📅"
                    }
                    icon = icons.get(category.lower(), "📅")

                    event_str = f"{icon} {event_text}"
                    if time:
                        event_str = f"{time} {event_str}"
                    events.append(event_str)
        except Exception as e:
            pass

    # 源 2: Google Calendar API (预留)
    # 源 3: Outlook Calendar API (预留)

    # 格式化输出
    if not events:
        return [f"📅 {today_display} - 无日程安排"]

    # 添加明日预告
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        tomorrow_file = WORKSPACE / "13-memory" / "calendar.md"
        if tomorrow_file.exists():
            content = tomorrow_file.read_text(encoding="utf-8")
            tomorrow_section = f"## {tomorrow}"
            if tomorrow_section in content:
                event_count = content.split(tomorrow_section)[1].split("\n## ")[0].count("- [")
                if event_count > 0:
                    events.append(f"\n📌 明日预告：{event_count} 个事件")
    except Exception:
        pass

    return events

def get_historical_comparison(date):
    """获取历史对比数据"""
    try:
        from datetime import datetime, timedelta
        current_date = datetime.strptime(date, "%Y-%m-%d")
        yesterday = (current_date - timedelta(days=1)).strftime("%Y-%m-%d")
        last_week = (current_date - timedelta(days=7)).strftime("%Y-%m-%d")

        # 读取昨日简报
        yesterday_brief = BRIEF_DIR / f"brief-{yesterday}.md"
        last_week_brief = BRIEF_DIR / f"brief-{last_week}.md"

        comparison = {
            "yesterday": None,
            "last_week": None
        }

        if yesterday_brief.exists():
            content = yesterday_brief.read_text(encoding="utf-8")
            # 简单解析 arXiv 数量
            import re
            match = re.search(r"\| arXiv 收集 \| (\d+) 篇", content)
            if match:
                comparison["yesterday"] = int(match.group(1))

        if last_week_brief.exists():
            content = last_week_brief.read_text(encoding="utf-8")
            import re
            match = re.search(r"\| arXiv 收集 \| (\d+) 篇", content)
            if match:
                comparison["last_week"] = int(match.group(1))

        return comparison
    except Exception as e:
        return {"yesterday": None, "last_week": None}

def get_trend_data(days=7):
    """获取最近 N 天的趋势数据"""
    from datetime import datetime, timedelta

    trend = []
    current_date = datetime.now()

    for i in range(days - 1, -1, -1):
        date = (current_date - timedelta(days=i)).strftime("%Y-%m-%d")
        brief_file = BRIEF_DIR / f"brief-{date}.md"

        arxiv_count = 0
        medium_count = 0

        if brief_file.exists():
            try:
                content = brief_file.read_text(encoding="utf-8")
                import re

                # 解析 arXiv 数量
                match = re.search(r"\| arXiv 收集 \| (\d+) 篇", content)
                if match:
                    arxiv_count = int(match.group(1))

                # 解析 Medium 数量
                match = re.search(r"\| Medium 分析 \| (\d+) 篇", content)
                if match:
                    medium_count = int(match.group(1))
            except Exception:
                pass

        trend.append({
            "date": date,
            "day": date.split("-")[2],  # 只显示日期
            "arxiv": arxiv_count,
            "medium": medium_count
        })

    return trend

def generate_trend_chart(trend_data):
    """生成 ASCII 趋势图"""
    if not trend_data:
        return "暂无趋势数据"

    # 找到最大值用于缩放
    max_arxiv = max(d["arxiv"] for d in trend_data) or 1
    max_medium = max(d["medium"] for d in trend_data) or 1
    max_val = max(max_arxiv, max_medium)

    # 生成图表 (最高 10 行)
    chart_height = 8
    chart = []

    for row in range(chart_height, 0, -1):
        threshold = (row / chart_height) * max_val
        line = f"{int(threshold):3d} │"

        for day in trend_data:
            if day["arxiv"] >= threshold:
                line += " 📊"
            elif day["medium"] >= threshold:
                line += " 📰"
            else:
                line += "  ·"

        chart.append(line)

    # X 轴
    x_axis = "    └─" + "".join(f" {d['day'][-2:]} " for d in trend_data)
    chart.append(x_axis)

    # 图例
    legend = "    图例：📊 arXiv  📰 Medium"
    chart.append(legend)

    return "\n".join(chart)

def generate_brief(date):
    """生成简报内容"""
    print(f"📊 生成每日简报 | 日期：{date}")

    # 收集数据
    print("\n📥 收集 arXiv 数据...")
    arxiv_count, arxiv_high, arxiv_files = get_arxiv_data(date)
    print(f"  ├─ 收集：{arxiv_count} 篇")
    print(f"  └─ 高优先级：{arxiv_high} 篇")

    print("\n📰 收集 Medium 数据...")
    medium_count, medium_deep = get_medium_data(date)
    print(f"  ├─ 分析：{medium_count} 篇")
    print(f"  └─ 深度解析：{medium_deep} 篇")

    print("\n🐙 检查 GitHub 状态...")
    git_commits, git_status = get_github_status()
    print(f"  ├─ 提交：{git_commits} 次")
    print(f"  └─ 同步：{git_status}")

    print("\n🏆 计算领域排名...")
    top_domains = get_domain_rankings()

    print("\n🌐 获取 HackerNews...")
    hn_stories = get_hackernews()
    print(f"  └─ 热门：{len(hn_stories)} 条")

    print("\n🌤️ 获取天气...")
    weather = get_weather()
    print(f"  └─ {weather}")

    print("\n📅 获取日历...")
    calendar = get_calendar_events()

    print("\n📊 获取历史对比...")
    history = get_historical_comparison(date)

    print("\n📈 生成趋势数据...")
    trend_data = get_trend_data(7)
    trend_chart = generate_trend_chart(trend_data)

    print("\n📝 生成简报...")

    # 生成内容
    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    # 构建历史对比文本
    history_text = ""
    if history["yesterday"] is not None:
        diff = arxiv_count - history["yesterday"]
        history_text += f"- 较昨日：{diff:+d} 篇 ({'↑' if diff > 0 else '↓' if diff < 0 else '→'})\n"
    if history["last_week"] is not None:
        diff = arxiv_count - history["last_week"]
        history_text += f"- 较上周：{diff:+d} 篇 ({'↑' if diff > 0 else '↓' if diff < 0 else '→'})\n"
    if not history_text:
        history_text = "- 无历史数据 (首次运行)\n"

    content = f"""# 📊 每日简报 | {date}

**生成时间:** {now}  
**数据周期:** {date} 00:00 - {date} 23:59  
**天气:** {weather}

---

## 🎯 核心指标

| 指标 | 数值 | 状态 |
|------|------|------|
| arXiv 收集 | {arxiv_count} 篇 | {"✅" if arxiv_count > 0 else "⚠️"} |
| 高优先级论文 | {arxiv_high} 篇 | {"🔥" if arxiv_high > 0 else "- "} |
| Medium 分析 | {medium_count} 篇 | {"✅" if medium_count > 0 else "⚠️"} |
| 深度解析 | {medium_deep} 篇 | {"🧠" if medium_deep > 0 else "- "} |
| GitHub 提交 | {git_commits} 次 | {"✅" if git_commits > 0 else "⚠️"} |
| 同步状态 | {git_status} | {"✅" if git_status == "✅" else "⚠️"} |

### 📈 历史对比
{history_text}

---

## 📊 7 天趋势

```
{trend_chart}
```

---

## 🏆 领域段位 Top 3

"""

    if top_domains:
        for rank, domain, level in top_domains:
            content += f"- **#{rank} {domain}:** 黑铁 {level} 级\n"
    else:
        content += "- 暂无排名数据\n"

    content += "\n---\n\n## 🔥 高优先级内容\n\n"

    if arxiv_files:
        for i, paper in enumerate(arxiv_files, 1):
            try:
                first_line = paper.read_text(encoding="utf-8").split("\n")[0]
                title = first_line.replace("# ", "").strip()
                content += f"{i}. **{title}**\n"
            except Exception:
                content += f"{i}. **{paper.name}**\n"
    else:
        content += "- 无高优先级内容\n"

    # 待处理事项
    pending = get_pending_items()
    content += f"""
---

## ⚠️ 待处理事项

- 待解析论文：{pending['parse']} 篇
- Git 待提交：{pending['git']} 个文件

---

## 🌐 HackerNews 热门

"""

    if hn_stories:
        for i, story in enumerate(hn_stories, 1):
            content += f"{i}. **{story['title']}** (👍{story['score']} 💬{story['comments']})\n"
    else:
        content += "- 暂无数据\n"

    content += f"""
---

## 📅 今日日历

"""

    for event in calendar:
        content += f"- {event}\n"

    content += f"""
---

## 📋 详细数据

- arXiv 目录：`{WORKSPACE}/40-arxiv/papers/{date}`
- Medium 目录：`{WORKSPACE}/41-medium/analyzed/{date}`
- 简报存档：`{BRIEF_DIR}`

---

*自动生成 by daily-brief.py | OpenClaw Workspace*
"""

    return content

def send_to_feishu(content, brief_file):
    """发送到 Feishu (通过 OpenClaw CLI)"""
    import subprocess
    import tempfile

    print("\n📤 发送到 Feishu...")

    try:
        # 方法 1: 使用 openclaw CLI 发送
        # 注意：需要 OpenClaw 支持 CLI 消息发送
        cmd = ["openclaw", "message", "send", "--channel", "feishu", "--file", str(brief_file)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

        if result.returncode == 0:
            print("  └─ ✅ 发送成功")
            return True
        else:
            print(f"  └─ ⚠️ CLI 发送失败：{result.stderr}")
    except FileNotFoundError:
        print("  └─ ⚠️ openclaw CLI 未找到")
    except Exception as e:
        print(f"  └─ ⚠️ 发送异常：{e}")

    # 方法 2: 写入发送队列文件，由 heartbeat 处理
    queue_file = WORKSPACE / "13-memory" / "feishu-queue.json"
    import json
    try:
        queue = []
        if queue_file.exists():
            queue = json.loads(queue_file.read_text(encoding="utf-8"))

        queue.append({
            "type": "daily_brief",
            "content": content,
            "file": str(brief_file),
            "queued_at": datetime.now().isoformat()
        })

        queue_file.write_text(json.dumps(queue, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  └─ ✅ 已加入发送队列：{queue_file}")
        return True
    except Exception as e:
        print(f"  └─ ❌ 队列写入失败：{e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="每日简报自动生成")
    parser.add_argument("--date", type=str, help="日期 (YYYY-MM-DD)，默认昨天")
    parser.add_argument("--send", action="store_true", help="发送到 Feishu")
    args = parser.parse_args()

    date = get_date(args.date)

    # 确保输出目录存在
    BRIEF_DIR.mkdir(parents=True, exist_ok=True)

    # 生成简报
    content = generate_brief(date)

    # 保存文件
    brief_file = BRIEF_DIR / f"brief-{date}.md"
    brief_file.write_text(content, encoding="utf-8")

    print(f"\n✅ 简报生成完成！")
    print(f"📁 文件位置：{brief_file}")

    if args.send:
        send_to_feishu(content, brief_file)

if __name__ == "__main__":
    main()

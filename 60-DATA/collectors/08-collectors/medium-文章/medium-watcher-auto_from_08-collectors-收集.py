"""
Medium Watcher v2.2 - 增加 GitHub 支持
"""

import sys
import json
import re
import time
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from xml.etree import ElementTree

OUTPUT_DIR = Path("D:/obsidian/Vault/Medium")
LOG_FILE = OUTPUT_DIR / "watcher-log.md"
SEEN_FILE = OUTPUT_DIR / ".seen-urls.json"
STATUS_FILE = OUTPUT_DIR / "Medium-Watcher-Status.md"
STATS_FILE = OUTPUT_DIR / ".watcher-stats.json"
REPORTS_DIR = OUTPUT_DIR / "Reports"

# 调试输出
print("[DEBUG] Script starting...", file=sys.stderr)
print(f"[DEBUG] Python version: {sys.version}", file=sys.stderr)
print(f"[DEBUG] Output dir: {OUTPUT_DIR}", file=sys.stderr)
print(f"[DEBUG] Output dir exists: {OUTPUT_DIR.exists()}", file=sys.stderr)

REPORTS_DIR.mkdir(exist_ok=True)

# ==================== 源配置 ====================

SOURCES = {
    "medium": {
        "tags": [
            "artificial-intelligence", "machine-learning", "data-science",
            "startup", "entrepreneurship", "mental-health", 
            "psychology", "productivity", "programming",
        ],
        "enabled": True,
        "priority_keywords": ["breakthrough", "new", "first", "revolutionary", "critical"],
    },
    "arxiv": {
        "categories": [
            "cs.AI", "cs.LG", "cs.CL", "cs.CV", "cs.NE", "stat.ML",
        ],
        "enabled": True,
        "max_results": 5,
        "priority_keywords": ["novel", "state-of-the-art", "SOTA", "breakthrough", "first"],
    },
    "github": {
        "topics": [
            "machine-learning",
            "deep-learning",
            "artificial-intelligence",
            "natural-language-processing",
            "computer-vision",
            "data-science",
            "mcp",
            "llm",
        ],
        "enabled": True,
        "max_repos": 10,  # 每个 topic 最多抓取仓库数
        "min_stars": 50,  # 最小 star 数
        "priority_keywords": ["framework", "library", "toolkit", "platform", "sdk"],
    }
}

# 标签分类规则
TAG_CATEGORIES = {
    "AI/ML": ["artificial-intelligence", "machine-learning", "cs.AI", "cs.LG", "stat.ML", "machine-learning", "deep-learning", "artificial-intelligence"],
    "NLP": ["natural-language-processing", "cs.CL", "nlp", "llm", "language-model"],
    "Vision": ["computer-vision", "cs.CV", "image-processing", "object-detection"],
    "Data": ["data-science", "analytics", "visualization", "data-analysis"],
    "Business": ["startup", "entrepreneurship", "venture-capital"],
    "Psychology": ["mental-health", "psychology", "neuroscience"],
    "Tech": ["programming", "software-engineering", "web-dev", "mcp", "api"],
    "Productivity": ["productivity", "time-management", "habits", "automation"],
}

# 优先级规则
PRIORITY_RULES = {
    "high": {"keywords": ["breakthrough", "critical", "novel", "SOTA", "state-of-the-art", "framework", "official"], "min_score": 8},
    "medium": {"keywords": ["survey", "review", "tutorial", "guide", "library", "toolkit"], "min_score": 5},
    "low": {"keywords": [], "min_score": 0}
}

# ==================== 数据加载 ====================

seen_urls = set()
if SEEN_FILE.exists():
    try:
        seen_urls = set(json.load(open(SEEN_FILE, "r", encoding="utf-8")))
    except:
        seen_urls = set()

stats = {
    "total_runs": 0,
    "total_articles": 0,
    "total_notes": 0,
    "by_source": {"medium": 0, "arxiv": 0, "github": 0},
    "by_category": {},
    "by_priority": {"high": 0, "medium": 0, "low": 0},
    "last_run": None,
    "errors": [],
    "weekly_reports": 0,
    "monthly_reports": 0,
}

def load_stats():
    global stats
    if STATS_FILE.exists():
        try:
            stats = json.load(open(STATS_FILE, "r", encoding="utf-8"))
        except:
            pass

def save_stats():
    with open(STATS_FILE, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)

# ==================== GitHub API ====================

def fetch_github_trending(topic: str, max_repos: int = 10, min_stars: int = 50):
    """从 GitHub 搜索仓库"""
    base_url = "https://api.github.com/search/repositories"
    query = f"topic:{topic}+stars:>={min_stars}"
    url = f"{base_url}?q={query}&sort=stars&order=desc&per_page={max_repos}"
    
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "MediumWatcher/2.2",
                "Accept": "application/vnd.github.v3+json",
            }
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        
        return parse_github_response(data, topic)
    except Exception as e:
        log_message(f"GitHub 搜索失败 {topic}: {e}")
        return []

def parse_github_response(data: dict, topic: str):
    """解析 GitHub API 响应"""
    repos = []
    
    for item in data.get("items", []):
        repo = {
            "source": "github",
            "full_name": item.get("full_name", ""),
            "name": item.get("name", ""),
            "owner": item.get("owner", {}).get("login", ""),
            "description": item.get("description", "") or "No description",
            "html_url": item.get("html_url", ""),
            "stars": item.get("stargazers_count", 0),
            "forks": item.get("forks_count", 0),
            "watchers": item.get("watchers_count", 0),
            "language": item.get("language", ""),
            "topics": item.get("topics", []),
            "created_at": item.get("created_at", "")[:10],
            "updated_at": item.get("updated_at", "")[:10],
            "homepage": item.get("homepage", ""),
            "license": item.get("license", {}).get("name", "") if item.get("license") else "",
        }
        
        if repo["full_name"] and repo["name"]:
            repos.append(repo)
    
    return repos

def fetch_github_readme(owner: str, repo: str):
    """获取 README 内容"""
    url = f"https://raw.githubusercontent.com/{owner}/{repo}/main/README.md"
    alt_url = f"https://raw.githubusercontent.com/{owner}/{repo}/master/README.md"
    
    for try_url in [url, alt_url]:
        try:
            req = urllib.request.Request(try_url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return resp.read().decode("utf-8")[:5000]  # 限制长度
        except:
            continue
    
    return None

def generate_github_note(repo: dict, category: str, priority: str, score: int, readme: str = None):
    """生成 GitHub 仓库笔记"""
    tags = ["github", "repository", datetime.now().strftime("%Y-%m"), category.lower().replace("/", "-")]
    if priority == "high":
        tags.append("high-priority")
    
    # 生成文件名
    safe_name = re.sub(r'[^\w\s-]', '', repo["name"])[:30].strip()
    safe_owner = re.sub(r'[^\w\s-]', '', repo["owner"])[:20].strip()
    filename = f"{repo['updated_at']}_gh_{safe_owner}_{safe_name}.md"
    
    priority_badge = {"high": "🔥 高优先级", "medium": "📌 中优先级", "low": "普通"}[priority]
    
    # 构建相关链接
    related_links = []
    if repo["homepage"]:
        related_links.append(f"- [🏠 官方网站]({repo['homepage']})")
    related_links.append(f"- [📦 PyPI](https://pypi.org/search/?q={repo['name']})")
    related_links.append(f"- [📊 Google Trends](https://trends.google.com/trends/explore?q={repo['name']})")
    
    note = f"""---
created: {datetime.now().strftime("%Y-%m-%d")}
source: {repo['html_url']}
repo: {repo['full_name']}
name: {repo['name']}
owner: {repo['owner']}
updated: {repo['updated_at']}
stars: {repo['stars']}
language: {repo['language'] or 'Unknown'}
tags: {tags}
category: {category}
priority: {priority}
score: {score}
status: raw
---

# {repo['name']}

> {priority_badge} | GitHub 仓库自动搜集

## 📊 仓库统计

| 指标 | 值 |
|------|-----|
| 完整名称 | {repo['full_name']} |
| 所有者 | [{repo['owner']}](https://github.com/{repo['owner']}) |
| Stars | ⭐ {repo['stars']} |
| Forks | 🍴 {repo['forks']} |
| 语言 | {repo['language'] or 'Unknown'} |
| 许可 | {repo['license'] or 'Unknown'} |
| 更新 | {repo['updated_at']} |

## 🔗 相关链接

- [📦 GitHub]({repo['html_url']})
{chr(10).join(related_links)}

## 📝 描述

{repo['description']}

## 📄 README

{readme[:2000] if readme else "*(README 获取失败或未提供)*"}

## 💡 核心功能

*(待分析)*

## 🚀 使用场景

*(待补充)*

## ✅ 行动项

- [ ] 阅读完整 README
- [ ] 尝试安装和使用
- [ ] 评估是否适合项目
- [ ] 更新笔记状态为 `analyzed`

## 🔗 相关资源

- [GitHub Issues]({repo['html_url']}/issues)
- [GitHub Pulls]({repo['html_url']}/pulls)
- [GitHub Releases]({repo['html_url']}/releases)

---

*Generated by Medium Watcher v2.2 (GitHub)*
"""
    return filename, note

# ==================== arXiv API ====================

def fetch_arxiv_category(category: str, max_results: int = 5):
    base_url = "http://export.arxiv.org/api/query"
    query = f"cat:{category}"
    url = f"{base_url}?search_query={query}&start=0&max_results={max_results}&sortBy=submittedDate&sortOrder=descending"
    
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            xml_data = resp.read().decode("utf-8")
        return parse_arxiv_xml(xml_data, category)
    except Exception as e:
        log_message(f"arXiv 抓取失败 {category}: {e}")
        return []

def parse_arxiv_xml(xml_data: str, category: str):
    papers = []
    ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
    
    try:
        root = ElementTree.fromstring(xml_data)
        entries = root.findall("atom:entry", ns)
        
        for entry in entries:
            paper = {
                "source": "arxiv",
                "arxiv_id": None,
                "title": None,
                "authors": [],
                "published": None,
                "abstract": None,
                "categories": [],
                "pdf_url": None,
                "abs_url": None,
            }
            
            id_elem = entry.find("atom:id", ns)
            if id_elem is not None:
                paper["arxiv_id"] = id_elem.text.split("/")[-1]
                paper["abs_url"] = f"https://arxiv.org/abs/{paper['arxiv_id']}"
                paper["pdf_url"] = f"https://arxiv.org/pdf/{paper['arxiv_id']}.pdf"
            
            title_elem = entry.find("atom:title", ns)
            if title_elem is not None:
                paper["title"] = " ".join(title_elem.text.split())
            
            for author in entry.findall("atom:author", ns):
                name_elem = author.find("atom:name", ns)
                if name_elem is not None:
                    paper["authors"].append(name_elem.text)
            
            published_elem = entry.find("atom:published", ns)
            if published_elem is not None:
                paper["published"] = published_elem.text[:10]
            
            summary_elem = entry.find("atom:summary", ns)
            if summary_elem is not None:
                paper["abstract"] = " ".join(summary_elem.text.split())[:2000]
            
            for cat in entry.findall("atom:category", ns):
                term = cat.get("term")
                if term:
                    paper["categories"].append(term)
            
            if paper["arxiv_id"] and paper["title"]:
                papers.append(paper)
    except Exception as e:
        log_message(f"arXiv XML 解析失败：{e}")
    
    return papers

def generate_arxiv_note(paper: dict, category: str, priority: str, score: int):
    tags = ["arxiv", "academic-paper", datetime.now().strftime("%Y-%m"), category.lower().replace("/", "-")]
    if priority == "high":
        tags.append("high-priority")
    
    safe_title = re.sub(r'[^\w\s-]', '', paper["title"])[:50].strip()
    safe_title = re.sub(r'\s+', '-', safe_title)
    filename = f"{paper['published']}_{paper['arxiv_id']}_{safe_title}.md"
    
    priority_badge = {"high": "🔥 高优先级", "medium": "📌 中优先级", "low": "普通"}[priority]
    authors_str = ", ".join(paper["authors"][:3])
    if len(paper["authors"]) > 3:
        authors_str += f" et al. ({len(paper['authors'])} authors)"
    
    note = f"""---
created: {datetime.now().strftime("%Y-%m-%d")}
source: {paper['abs_url']}
arxiv_id: {paper['arxiv_id']}
title: {paper['title']}
authors: {authors_str}
published: {paper['published']}
def run_collection():
    import os
    source_filter = os.environ.get('MW_SOURCE', 'all')
tags: {tags}
category: {category}
priority: {priority}
score: {score}
status: raw
---

# {paper['title']}

> {priority_badge} | arXiv 论文自动搜集

## 📄 元数据

| 字段 | 值 |
|------|-----|
| arXiv ID | {paper['arxiv_id']} |
| 作者 | {authors_str} |
| 发布 | {paper['published']} |
| 分类 | {", ".join(paper['categories'])} |
| 优先级 | {priority} ({score}/10) |
| PDF | [下载]({paper['pdf_url']}) |
| 摘要页 | [查看]({paper['abs_url']}) |

## 📝 摘要

{paper['abstract'] or "*(摘要获取失败)*"}

## 💡 核心贡献

*(待分析)*

## 🔍 研究方法

*(待补充)*

## 📊 实验结果

*(待补充)*

## ✅ 行动项

- [ ] 阅读完整论文
- [ ] 提取核心贡献
- [ ] 关联现有知识
- [ ] 更新笔记状态为 `analyzed`

## 🔗 相关链接

- [arXiv 摘要]({paper['abs_url']})
- [PDF 下载]({paper['pdf_url']})
- [Semantic Scholar](https://www.semanticscholar.org/search?q={paper['title']})
- [Google Scholar](https://scholar.google.com/scholar?q={paper['title']})

---

*Generated by Medium Watcher v2.2 (arXiv)*
"""
    return filename, note

# ==================== Medium 抓取 ====================

def fetch_medium_tag(tag: str, max_articles: int = 3):
    print(f"[DEBUG] fetch_medium_tag called with tag: {tag}", file=sys.stderr)
    url = f"https://r.jina.ai/https://medium.com/tag/{tag}"
    print(f"[DEBUG] URL: {url}", file=sys.stderr)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        print(f"[DEBUG] Before urlopen", file=sys.stderr)
        with urllib.request.urlopen(req, timeout=30) as resp:
            print(f"[DEBUG] After urlopen", file=sys.stderr)
            content = resp.read().decode("utf-8")
        
        articles = []
        print(f"[DEBUG] Content length: {len(content)}", file=sys.stderr)
        # jina.ai 返回 Markdown 格式，使用正则匹配 Markdown 链接
        matches = re.findall(r'\[([^\]]+)\]\((https://medium\.com/[^\)]+)\)', content)
        print(f"[DEBUG] Found {len(matches)} markdown links", file=sys.stderr)
        for title, url in matches:
            clean_url = url.rstrip(')"\'')
            # 调试：打印前 10 个 URL
            if len(articles) < 10:
                print(f"[DEBUG] Checking URL: {clean_url}", file=sys.stderr)
            if (clean_url not in seen_urls and 
                clean_url.count('/') >= 4 and  # 文章 URL 至少有 4 个/
                "/m/signin" not in clean_url and
                "/sitemap" not in clean_url):
                articles.append(clean_url)
                print(f"[DEBUG] ✓ Found article: {clean_url}", file=sys.stderr)
                if len(articles) >= max_articles:
                    break
        print(f"[DEBUG] Total articles found: {len(articles)}", file=sys.stderr)
        return articles[:max_articles]
    except Exception as e:
        return []

def fetch_article_content(url: str):
    jina_url = f"https://r.jina.ai/{url}"
    try:
        req = urllib.request.Request(jina_url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        return None

# ==================== 通用工具 ====================

def categorize_article(title: str, tags: list, source: str = "medium") -> str:
    text = (title + " " + " ".join(tags)).lower()
    for category, category_tags in TAG_CATEGORIES.items():
        for tag in category_tags:
            if tag.lower() in text:
                return category
    return "General"

def calculate_priority(title: str, content: str = "", source: str = "medium") -> tuple:
    text = (title + " " + content).lower()
    score = 5
    for kw in PRIORITY_RULES["high"]["keywords"]:
        if kw.lower() in text:
            score += 3
    for kw in PRIORITY_RULES["medium"]["keywords"]:
        if kw.lower() in text:
            score += 1
    if source == "arxiv":
        score += 1
    priority = "high" if score >= 8 else ("medium" if score >= 5 else "low")
    return priority, min(score, 10)

def save_note(filename: str, note: str):
    print(f"[DEBUG] save_note called with filename: {filename}", file=sys.stderr)
    filepath = OUTPUT_DIR / filename
    print(f"[DEBUG] filepath: {filepath}", file=sys.stderr)
    counter = 1
    while filepath.exists():
        stem = filename.replace('.md', '')
        filepath = OUTPUT_DIR / f"{stem}-{counter}.md"
        counter += 1
    print(f"[DEBUG] Writing to {filepath}", file=sys.stderr)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(note)
    print(f"[DEBUG] File saved successfully", file=sys.stderr)
    return filepath

def log_message(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"- [{timestamp}] {msg}\n"
    if not LOG_FILE.exists():
        with open(LOG_FILE, "w", encoding="utf-8") as f:
            f.write("# Medium Watcher 日志\n\n")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(entry)

def update_seen_urls():
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen_urls), f, indent=2, ensure_ascii=False)

def update_status():
    status_content = f"""---
created: 2026-03-01
type: system-status
tags: [medium-watcher, automation, status]
---

# Medium Watcher 自动搜集状态

## 📊 实时状态

| 指标 | 数值 |
|------|------|
| **运行状态** | ✅ 后台运行中 |
| **搜集间隔** | ⏱️ 5 分钟 |
| **总运行次数** | {stats['total_runs']} |
| **总搜集文章** | {stats['total_articles']} |
| **总生成笔记** | {stats['total_notes']} |
| **Medium 文章** | {stats['by_source'].get('medium', 0)} |
| **arXiv 论文** | {stats['by_source'].get('arxiv', 0)} |
| **GitHub 仓库** | {stats['by_source'].get('github', 0)} |
| **高优先级** | 🔥 {stats['by_priority']['high']} |
| **最后运行** | {stats['last_run'] or '从未'} |

## 📑 监控源

| 源 | 状态 | 配置 |
|---|------|------|
| Medium | {"✅ 运行中" if SOURCES['medium']['enabled'] else "⏸️ 禁用"} | {len(SOURCES['medium']['tags'])} 标签 |
| arXiv | {"✅ 运行中" if SOURCES['arxiv']['enabled'] else "⏸️ 禁用"} | {len(SOURCES['arxiv']['categories'])} 类别 |
| GitHub | {"✅ 运行中" if SOURCES['github']['enabled'] else "⏸️ 禁用"} | {len(SOURCES['github']['topics'])} 主题 |

## 📁 分类统计

"""
    for category, count in stats.get("by_category", {}).items():
        status_content += f"| {category} | {count} |\n"
    if not stats.get("by_category"):
        status_content += "| *(暂无数据)* | - |\n"
    
    status_content += f"""
## 📈 优先级分布

| 优先级 | 数量 | 图标 |
|--------|------|------|
| 高 | {stats['by_priority']['high']} | 🔥 |
| 中 | {stats['by_priority']['medium']} | 📌 |
| 低 | {stats['by_priority']['low']} | - |

---

*Last updated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        f.write(status_content)

# ==================== 主流程 ====================

def run_collection():
    import os
    print("[DEBUG] run_collection() called", file=sys.stderr)
    source_filter = os.environ.get("MW_SOURCE", "all")
    print(f"[DEBUG] source_filter: {source_filter}", file=sys.stderr)
    start_time = datetime.now()
    stats["total_runs"] += 1
    stats["last_run"] = start_time.strftime("%Y-%m-%d %H:%M:%S")
    errors = []
    
    new_articles = 0
    new_notes = 0
    categories = {}
    top_priority = "low"
    
    # 1. Medium 搜集 (source_filter check)
    if SOURCES["medium"]["enabled"] and (source_filter == "all" or source_filter == "medium"):
        print("[DEBUG] Starting Medium collection", file=sys.stderr)
        log_message("开始 Medium 搜集")
        print("[DEBUG] After first log_message", file=sys.stderr)
        for tag in SOURCES["medium"]["tags"]:
            print(f"[DEBUG] Processing tag: {tag}", file=sys.stderr)
            articles = fetch_medium_tag(tag, max_articles=2)
            print(f"[DEBUG] Got {len(articles)} articles for tag {tag}", file=sys.stderr)
            for url in articles:
                print(f"[DEBUG] Processing URL: {url[:50]}...", file=sys.stderr)
                if url in seen_urls:
                    print(f"[DEBUG] URL already seen, skipping", file=sys.stderr)
                    continue
                new_articles += 1
                print(f"[DEBUG] Before fetch_article_content", file=sys.stderr)
                content = fetch_article_content(url)
                print(f"[DEBUG] After fetch_article_content, content length: {len(content) if content else 0}", file=sys.stderr)
                if not content:
                    errors.append(f"Medium 抓取失败：{url[:50]}")
                    continue
                category = categorize_article(url, [tag], "medium")
                priority, score = calculate_priority(url, content, "medium")
                categories[category] = categories.get(category, 0) + 1
                stats["by_category"][category] = stats["by_category"].get(category, 0) + 1
                stats["by_priority"][priority] += 1
                stats["by_source"]["medium"] = stats["by_source"].get("medium", 0) + 1
                if priority == "high":
                    top_priority = "high"
                elif priority == "medium" and top_priority == "low":
                    top_priority = "medium"
                title = content.split("Title:")[1].split("\n")[0].strip() if "Title:" in content else url
                published = content.split("Published Time:")[1].split("\n")[0].strip()[:10] if "Published Time:" in content else datetime.now().strftime("%Y-%m-%d")
                safe_title = re.sub(r'[^\w\s-]', '', title)[:50].strip()
                safe_title = re.sub(r'\s+', '-', safe_title)
                priority_marker = {"high": "🔥", "medium": "📌", "low": ""}[priority]
                filename = f"{published}_{priority_marker}_{safe_title}.md" if priority_marker else f"{published}_{safe_title}.md"
                note = f"""---
created: {datetime.now().strftime("%Y-%m-%d")}
source: {url}
title: {title}
published: {published}
tags: ["medium", "auto-collected", "{category.lower()}"]
category: {category}
priority: {priority}
score: {score}
status: raw
---

# {title}

> {{"🔥 高优先级" if priority == "high" else "📌 中优先级" if priority == "medium" else "普通"}} | Medium 文章自动搜集

## 📄 元数据
| 字段 | 值 |
|------|-----|
| 发布 | {published} |
| 分类 | {category} |
| 优先级 | {priority} ({score}/10) |
| 来源 | [{url}]({url}) |

## 📝 内容摘要
*(待分析)*

## 💡 核心洞见
*(待补充)*

## ✅ 行动项
- [ ] 阅读并分析本文
- [ ] 提取关键概念
- [ ] 关联现有知识

---
*Generated by Medium Watcher v2.2*
"""
                save_note(filename, note)
                new_notes += 1
                seen_urls.add(url)
            time.sleep(2)
    
    # 2. arXiv 搜集 (source_filter check)
    if SOURCES["arxiv"]["enabled"] and (source_filter == "all" or source_filter == "arxiv"):
        log_message("开始 arXiv 搜集")
        for category in SOURCES["arxiv"]["categories"]:
            papers = fetch_arxiv_category(category, SOURCES["arxiv"]["max_results"])
            for paper in papers:
                if paper["abs_url"] in seen_urls:
                    continue
                new_articles += 1
                cat_name = category.split(".")[-1] if "." in category else category
                category_mapped = categorize_article(paper["title"], paper["categories"], "arxiv")
                priority, score = calculate_priority(paper["title"], paper["abstract"], "arxiv")
                categories[category_mapped] = categories.get(category_mapped, 0) + 1
                stats["by_category"][category_mapped] = stats["by_category"].get(category_mapped, 0) + 1
                stats["by_priority"][priority] += 1
                stats["by_source"]["arxiv"] = stats["by_source"].get("arxiv", 0) + 1
                if priority == "high":
                    top_priority = "high"
                elif priority == "medium" and top_priority == "low":
                    top_priority = "medium"
                filename, note = generate_arxiv_note(paper, category_mapped, priority, score)
                save_note(filename, note)
                new_notes += 1
                seen_urls.add(paper["abs_url"])
                log_message(f"arXiv: {paper['arxiv_id']} - {paper['title'][:50]}")
            time.sleep(3)
    
    # 3. GitHub 搜集 (source_filter check) - 暂时禁用调试
    print("[DEBUG] Skipping GitHub collection for now", file=sys.stderr)
    if False and SOURCES["github"]["enabled"] and (source_filter == "all" or source_filter == "github"):
        log_message("开始 GitHub 搜集")
        for topic in SOURCES["github"]["topics"]:
            repos = fetch_github_trending(topic, SOURCES["github"]["max_repos"], SOURCES["github"]["min_stars"])
            for repo in repos:
                if repo["html_url"] in seen_urls:
                    continue
                new_articles += 1
                category_mapped = categorize_article(repo["name"], repo["topics"] + [topic], "github")
                priority, score = calculate_priority(repo["name"] + " " + repo["description"], "", "github")
                categories[category_mapped] = categories.get(category_mapped, 0) + 1
                stats["by_category"][category_mapped] = stats["by_category"].get(category_mapped, 0) + 1
                stats["by_priority"][priority] += 1
                stats["by_source"]["github"] = stats["by_source"].get("github", 0) + 1
                if priority == "high":
                    top_priority = "high"
                elif priority == "medium" and top_priority == "low":
                    top_priority = "medium"
                # 尝试获取 README
                readme = fetch_github_readme(repo["owner"], repo["name"])
                filename, note = generate_github_note(repo, category_mapped, priority, score, readme)
                save_note(filename, note)
                new_notes += 1
                seen_urls.add(repo["html_url"])
                log_message(f"GitHub: {repo['full_name']} - ⭐{repo['stars']}")
            time.sleep(2)  # GitHub API 限制
    
    stats["total_articles"] += new_articles
    stats["total_notes"] += new_notes
    update_seen_urls()
    save_stats()
    update_status()
    log_message(f"搜集完成：{new_articles} 篇，{new_notes} 篇笔记")
    return new_articles, new_notes, errors

# ==================== 主程序 ====================

if __name__ == "__main__":
    print("[DEBUG] Before load_stats()", file=sys.stderr)
    load_stats()
    print("[DEBUG] After load_stats()", file=sys.stderr)
    try:
        print("[DEBUG] Before run_collection()", file=sys.stderr)
        articles, notes, errors = run_collection()
        status = "[OK]" if not errors else "[WARN]"
        print(f"{status} Done: {articles} articles, {notes} notes")
    except Exception as e:
        stats["errors"].append(str(e))
        save_stats()
        print(f"[ERROR] {e}")

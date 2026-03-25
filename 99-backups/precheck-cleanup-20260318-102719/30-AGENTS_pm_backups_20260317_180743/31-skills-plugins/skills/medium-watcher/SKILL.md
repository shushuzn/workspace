---
name: medium-watcher
description: Medium 技术文章监听工具。按作者/标签/出版物自动收集 Medium 文章，提取正文内容，归档原始文件，筛选高质内容。使用场景：(1) 补充非论文信息源，(2) 工业界动态追踪，(3) 专家观点收集。
---

# Medium Watcher — Medium 文章监听

## 核心功能

1. **多源监听** — 按作者/标签/出版物订阅
2. **内容提取** — 提取正文、图片、代码块
3. **原始归档** — 保存 HTML/Markdown 原始文件
4. **质量筛选** — 基于阅读数/点赞数/评论数评分
5. **定期清理** — 归档过期文件，保持仓库整洁

## 监听配置

### 按作者订阅

```yaml
authors:
  - "https://medium.com/@author1"
  - "https://medium.com/@author2"
  - "Andrej Karpathy"
  - "Simon Willison"
```

### 按标签订阅

```yaml
tags:
  - "artificial-intelligence"
  - "machine-learning"
  - "llm"
  - "agentic-ai"
  - "mcp"
  - "software-architecture"
```

### 按出版物订阅

```yaml
publications:
  - "Towards Data Science"
  - "Better Programming"
  - "The Startup"
  - "Level Up Coding"
```

## 工作流程

```
1. 遍历订阅源 (作者/标签/出版物)
   ↓
2. 获取最新文章列表 (RSS/API)
   ↓
3. 去重检查 (URL/标题相似度)
   ↓
4. 提取正文内容 (标题/作者/日期/正文)
   ↓
5. 质量评分 (阅读数/点赞/评论)
   ↓
6. 保存原始文件 + 元数据
   ↓
7. (可选) 筛选高质文章深度分析
```

## 输出格式

### 原始 Markdown

```markdown
---
source: medium
url: https://medium.com/@author/article-title
author: Author Name
date: 2026-03-03
tags: [ai, llm]
claps: 1200
responses: 45
reading_time: 8 min
---

# 文章标题

[正文内容，含图片/代码块]

---

*原始文件，待处理*
```

### 元数据 JSON

```json
{
  "collected_date": "2026-03-03",
  "source": "medium",
  "url": "https://medium.com/@author/article-title",
  "title": "文章标题",
  "author": "Author Name",
  "published_date": "2026-03-02",
  "tags": ["ai", "llm"],
  "claps": 1200,
  "responses": 45,
  "reading_time": 8,
  "quality_score": 4.2,
  "file_path": "Medium/Raw/medium-2026-03-03-article.md"
}
```

### 质量评分规则

| 指标 | 权重 | 评分 |
|------|------|------|
| 点赞数 (Claps) | 40% | >1000: 5 分, >500: 4 分, >100: 3 分 |
| 评论数 (Responses) | 30% | >50: 5 分, >20: 4 分, >5: 3 分 |
| 阅读时间 | 15% | >10min: 5 分, >5min: 4 分 |
| 作者影响力 | 15% | 知名专家：5 分 |

**阈值:** ≥4 分标记为"高质"，可深度分析

## 文件管理

### 目录结构

```
Medium/
├── Raw/                    # 原始文件 (待处理)
│   ├── medium-2026-03-03-article1.md
│   └── medium-2026-03-03-article2.md
├── Processed/              # 已处理 (生成 P-Note/M-Note)
│   └── P-2026-ArticleTitle.md
└── Archive/                # 归档 (30 天后)
    └── 2026-03/
        └── medium-*.md
```

### 清理策略

```yaml
# 每日清理 (执行时间：每日 4am)
- 移动 30 天前的 Raw 文件 → Archive/日期/
- 压缩 Archive/ 目录 (可选)
- 删除 >90 天的压缩文件 (可选)

# 保留规则
- 已处理文件 (Processed/) 永久保留
- 高质文章 (≥4 分) 永久保留
- 低质文章 (<3 分) 30 天后删除
```

## 使用方式

### 命令行

```bash
python medium-watcher.py \
  --authors author1,author2 \
  --tags ai,llm,agentic-ai \
  --output Medium/Raw/ \
  --min-score 3 \
  --format md,json
```

### 定时任务

```powershell
# 每日 4am 执行
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "medium-watcher.py --tags ai,llm --output Medium/Raw/"
$trigger = New-ScheduledTaskTrigger -Daily -At 4am
Register-ScheduledTask -TaskName "medium-watcher" -Action $action -Trigger $trigger

# 每日 5am 清理归档
$action = New-ScheduledTaskAction -Execute "python" `
  -Argument "medium-watcher.py --cleanup --archive-after-days 30"
$trigger = New-ScheduledTaskTrigger -Daily -At 5am
Register-ScheduledTask -TaskName "medium-watcher-cleanup" -Action $action -Trigger $trigger
```

### 与 AI Research OS 集成

```python
# Medium 文章 → AI Research OS 分析

def process_high_quality_articles():
    # 加载高质文章
    articles = load_articles(min_score=4)
    
    for article in articles[:3]:  # 限制每日处理数量
        # 提取核心观点
        views = extract_views(article["content"])
        
        # 补充到 P-Note 或 C-Note
        if is_technical_deep_dive(article):
            create_p_note(article)
        else:
            append_to_memory(views)
```

## 文件结构

```
medium-watcher/
├── SKILL.md
├── scripts/
│   ├── medium-watcher.py     # 主脚本
│   ├── content-extractor.py  # 内容提取器
│   └── cleanup-archiver.py   # 清理归档
├── references/
│   ├── rss-feeds.md        # RSS 源列表
│   └── quality-rules.md    # 质量评分规则
└── assets/
    └── templates/
        └── article-md-template.md
```

## 输出路径

- **原始文件:** `Medium/Raw/medium-YYYY-MM-DD-article.md`
- **元数据:** `Medium/Raw/medium-YYYY-MM-DD.meta.json`
- **归档:** `Medium/Archive/YYYY-MM/`

## API 限制

- Medium 无官方 API，使用 RSS/网页抓取
- 建议：添加请求延迟 (1-2 秒)
- 错误处理：重试机制 (3 次)

## 已知局限

1. **付费墙** — 部分文章无法访问
2. **动态内容** — JavaScript 渲染内容需浏览器
3. **反爬虫** — 可能触发速率限制
4. **格式变化** — Medium 改版可能影响提取

## 依赖

```
feedparser>=6.0.0
beautifulsoup4>=4.12.0
requests>=2.31.0
```

## 参考

- Medium RSS: `https://medium.com/feed/@username`
- Medium 标签 RSS: `https://medium.com/feed/tag/{tag}`

---

*补充非论文信息源，追踪工业界动态*

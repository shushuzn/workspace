# 04-COLLECTORS - 数据收集器

**用途:** 自动收集 arXiv/Medium/Reddit/Twitter/HackerNews 数据

---

## 📁 目录结构

```
04-COLLECTORS/
├── arxiv/                     # arXiv 收集
│   ├── arxiv-research-orchestrator.ps1
│   └── arxiv_ops_cli.py
├── medium/                    # Medium 监控
├── reddit/                    # Reddit 监控
│   ├── reddit-monitor.log
│   └── reddit-seen.db
├── x-twitter/                 # Twitter 监控
│   ├── x-twitter-monitor.py
│   ├── x-twitter.log
│   └── x-twitter-seen.db
├── hn/                        # HackerNews
│   └── hn-comment-analyzer.py
├── collectors/                # 收集器核心
└── README.md
```

---

## 🚀 快速开始

### arXiv 收集
```powershell
# 运行收集器
.\arxiv\arxiv-research-orchestrator.ps1

# CLI 操作
py arxiv\arxiv_ops_cli.py --help
```

### Twitter 监控
```bash
# 运行监控
py x-twitter\x-twitter-monitor.py
```

---

## ✨ 功能特性

- ✅ **arXiv** - 38 领域自动收集
- ✅ **Medium** - RSS 订阅监控
- ✅ **Reddit** - 技术板块追踪
- ✅ **Twitter/X** - 专家观点收集
- ✅ **HackerNews** - 评论分析

---

## 📊 统计信息

| 类别 | 数量 | 大小 |
|------|------|------|
| arXiv 脚本 | 2 | 16KB |
| Reddit 数据 | 2 | 40KB |
| Twitter 脚本 | 3 | 25KB |
| HN 分析 | 1 | 4KB |
| **总计** | **27** | **~85KB** |

---

*最后更新：2026-03-11 | 版本 v1.0*

# 🛠️ 技能快速参考

**最后更新:** 2026-03-04 15:10  
**技能目录:** `D:\npm-global\node_modules\openclaw\skills\`

---

## 📚 AI 研究技能 (核心)

| 技能 | 用途 | 命令/触发 |
|------|------|----------|
| **ai-research-os** | 论文深度解析 → P-Note/C-Note/M-Note | `分析论文 arXiv:xxxx.xxxxx` |
| **arxiv-daily** | 每日 arXiv 论文收集 + 优先级评分 | 定时任务 2am |
| **pdf-extractor** | PDF → 结构化 Markdown | `python pdf-extractor.py --input paper.pdf` |
| **batch-processor** | 批量论文并行解析 | 定时任务 2:30am |
| **citation-tracker** | 引用关系追踪 + 图谱生成 | 定时任务 周日 6am |

---

## 📰 信息收集技能

| 技能 | 用途 | 配置 |
|------|------|------|
| **medium-watcher** | Medium 技术文章收集 | 定时任务 4am |
| **arxiv-collector** | arXiv 论文收集 (内置) | 定时任务 2am |

---

## 🧠 知识管理技能

| 技能 | 用途 | 输出 |
|------|------|------|
| **memory-distiller** | 每日笔记 → MEMORY.md 蒸馏 | 定时任务 周日 5am |
| **knowledge-graph** | 实体/关系抽取 + 图谱构建 | GraphML/JSON |
| **knowledge-graph-builder** | 增强版图谱 (D3.js 可视化) | HTML/GraphML |

---

## 🔧 系统工具技能

| 技能 | 用途 | 命令 |
|------|------|------|
| **github-sync** | Git 自动同步 | 定时任务 6am |
| **github** | 手动 gh CLI 操作 | `gh issue list` 等 |
| **gh-issues** | GitHub issues → PR 自动修复 | `/gh-issues owner/repo` |
| **healthcheck** | 系统安全审计 | `openclaw healthcheck` |
| **mcporter** | MCP 服务器调用 | `mcporter list` |

---

## 📊 其他实用技能

| 技能 | 用途 |
|------|------|
| **weather** | 天气预报 (wttr.in) |
| **openai-whisper-api** | 语音转文字 |
| **skill-creator** | 创建新技能 |
| **evermemos** | EverMemOS 记忆系统集成 |

---

## 📋 常用工作流

### 单篇论文解析
```
1. 收集：arxiv-daily (自动) 或 手动提供 arXiv ID
2. 解析：ai-research-os → P-Note
3. 同步：github-sync (自动)
```

### 批量论文解析
```
1. 收集：arxiv-collector → high-priority.json
2. 解析：batch-processor (并行 4 个)
3. 蒸馏：memory-distiller (周日)
4. 图谱：citation-tracker (周日)
```

### 知识蒸馏
```
1. 输入：memory/YYYY-MM-DD.md (每日笔记)
2. 处理：memory-distiller --period weekly
3. 输出：MEMORY.md (长期记忆)
```

---

## 🔑 关键文件

| 文件 | 用途 |
|------|------|
| `MEMORY.md` | 长期记忆 (核心观点/趋势/决策) |
| `HEARTBEAT.md` | 心跳任务清单 |
| `SYSTEM-DASHBOARD.md` | 系统状态仪表盘 |
| `memory/YYYY-MM-DD.md` | 每日笔记 |

---

## 📅 定时任务时间表

| 时间 | 任务 | 说明 |
|------|------|------|
| 2:00 AM | arxiv-collector | 收集论文 |
| 2:30 AM | batch-processor | 解析论文 |
| 3:00 AM | nightly-security-audit | 安全审计 |
| 4:00 AM | medium-watcher | 收集文章 |
| 5:00 AM | memory-distiller | 知识蒸馏 (周日) |
| 6:00 AM | github-sync | Git 同步 |
| 6:00 AM | citation-tracker | 引用追踪 (周日) |

---

*此文档由 AI 维护，技能更新时自动同步*

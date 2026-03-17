# 技能使用示例集

**创建时间:** 2026-03-04 15:10  
**目的:** 为常用技能提供实际使用案例

---

## 📚 AI 研究技能

### 1. ai-research-os (论文深度解析)

**场景:** 需要深度分析一篇 AI 研究论文

**示例 1 - 单篇论文解析:**
```
分析论文 arXiv:2602.23681
```

**输出:**
- P-Note 格式笔记 (`P-2026-ODAR-AdaptiveRouting.md`)
- 10 维度信息抽取
- 对抗式审稿 (6 大类问题)
- Decision (是/否/观望)

**示例 2 - 多篇对比分析:**
```
对比分析这 3 篇效率优化论文：2602.23668, 2602.23681, 2602.23701
```

**输出:**
- M-Note 跨论文分析 (`M-20260303-Efficiency Optimization.md`)
- 量化对比表
- 综合设计建议

**实际案例:**
- 2026-03-03: 批量解析 5 篇论文 (~6 分钟，效率 +76%)
- 输出：5 篇 P-Note + 1 篇 M-Note
- 已同步至 obsidian-sync 仓库

---

### 2. batch-processor (批量论文解析)

**场景:** 需要并行处理多篇论文

**示例 1 - CLI 调用:**
```bash
python batch-processor.py --papers 2602.23668,2602.23681,2602.23701 --max-concurrent 4
```

**示例 2 - 从文件读取:**
```bash
python batch-processor.py --input papers.txt --output Medium/P-Note/
```

**示例 3 - DryRun 测试:**
```bash
python batch-processor.py --papers 2602.23668 --dry-run --verbose
```

**输出:**
- 进度追踪 (`progress.json`)
- 汇总报告 (`batch-summary-YYYY-MM-DD.md`)
- P-Note 文件 (输出目录)

**性能指标:**
- 4 篇论文：~6 分钟 (vs 串行~20 分钟)
- 效率提升：+70%

---

### 3. arxiv-daily (每日论文收集)

**场景:** 自动收集指定领域的每日新论文

**配置:**
```yaml
categories: cs.AI, cs.LG, cs.CL
min_score: 3
output: Medium/Raw/
```

**输出:**
- JSON 元数据 (`arxiv-YYYY-MM-DD.json`)
- Markdown 索引 (`arxiv-YYYY-MM-DD-index.md`)
- 优先级评分

**集成:**
- 定时任务：每日 2:00 AM
- 与 batch-processor 联动

---

## 📰 信息收集技能

### 4. medium-watcher (Medium 文章收集)

**场景:** 按标签/作者收集中文/英文技术文章

**示例:**
```bash
python medium-watcher.py --tags ai,llm,agentic --output Medium/Raw/ --min-score 3
```

**输出:**
- 原始 Markdown 文件
- 质量评分 (1-5 分)
- 自动归档 (30 天保留期)

**定时任务:** 每日 4:00 AM

---

## 🧠 知识管理技能

### 5. memory-distiller (知识蒸馏)

**场景:** 将每日笔记提炼为长期记忆

**示例 1 - 每周蒸馏:**
```bash
python memory-distiller.py --input memory/ --output MEMORY.md --period weekly
```

**示例 2 - 指定日期范围:**
```bash
python memory-distiller.py --input memory/ --output MEMORY.md --start 2026-03-01 --end 2026-03-07
```

**输出:**
- 核心观点 (去重 + 置信度评估)
- 趋势追踪更新
- 交叉引用

**实际案例:**
- 2026-03-03: 蒸馏 14 个核心观点
- MEMORY.md 从 8KB 增长至 24KB

---

### 6. knowledge-graph-builder (知识图谱)

**场景:** 从论文/笔记构建可查询的知识网络

**示例 1 - 单文件:**
```bash
python build-graph.py --input "P-20260302-The Auton Agentic AI Framework.md" --output knowledge-graph/ --source markdown --format json
```

**示例 2 - 目录扫描:**
```bash
python build-graph.py --input Medium/P-Note/ --output knowledge-graph/ --source markdown --format all --analyze
```

**输出:**
- GraphML (Gephi 可视化)
- JSON (程序查询)
- HTML (D3.js 交互式)
- 分析报告

**测试结果 (2026-03-04):**
```
输入：P-20260302-The Auton Agentic AI Framework.md
输出：
  - graph.json (818 B)
  - analysis.json (301 B)
实体：2 个，关系：1 个
```

---

### 7. citation-tracker (引用追踪)

**场景:** 追踪论文的引用关系和影响力

**示例 1 - 单篇分析:**
```bash
python citation-tracker.py --paper 2602.23681
```

**示例 2 - 批量分析:**
```bash
python citation-tracker.py --input Medium/P-Note/ --output knowledge-graph/
```

**示例 3 - 离线模式:**
```bash
python citation-tracker.py --paper 2602.23681 --offline
```

**输出:**
- 引用图谱 (`kg-citations.graphml`)
- 影响力评分 (PageRank)
- JSON 元数据

**数据源:**
- 本地 P-Note 参考文献
- Semantic Scholar API (被引查询)
- arXiv API (元数据)

---

## 🔧 系统工具技能

### 8. github-sync (Git 自动同步)

**场景:** 自动提交工作区变更到 GitHub

**示例 1 - 手动同步:**
```bash
python github-sync.py --sync
```

**示例 2 - 监听模式:**
```bash
python github-sync.py --watch --interval 900
```

**示例 3 - 查看状态:**
```bash
python github-sync.py --status
```

**配置:**
```yaml
watch_dirs:
  - Medium/P-Note/
  - memory/
  - MEMORY.md
commit_prefix: "[auto-sync]"
push_interval: 1800
```

**实际案例:**
- 2026-03-03: 提交 5 篇 P-Note + 1 篇 M-Note
- Commit: `9fd9740 [auto-sync] 2026-03-03 系统维护`

---

### 9. evermemos (EverMemOS 集成)

**场景:** 为 OpenClaw 提供长期记忆存储/检索

**示例 1 - 存储记忆:**
```bash
node evermemos.js store --message "用户偏好使用 Python 进行数据分析" --sender "user_001" --sender-name "华为"
```

**示例 2 - 检索记忆:**
```bash
node evermemos.js search --query "Python 数据分析" --method hybrid --top-k 10
```

**示例 3 - 获取特定类型:**
```bash
node evermemos.js get --type "foresight" --user-id "user_001"
```

**API 测试 (2026-03-04):**
```bash
POST http://localhost:1995/api/v1/memories
Body: {"message_id": "msg_test", "sender": "test_user", "content": "测试记忆"}
Response: {"status": "ok", "message": "Message queued, awaiting boundary detection"}
```

**验证状态:** ✅ 通过 (存储/检索/获取)

---

## 📊 其他实用技能

### 10. weather (天气预报)

**示例:**
```
北京天气怎么样？
周末香港会下雨吗？
```

**数据源:** wttr.in (无需 API Key)

---

### 11. openai-whisper-api (语音转文字)

**示例:**
```
转录这个音频文件：meeting-recording.mp3
```

**输出:** Markdown 格式文字稿

---

### 12. healthcheck (系统安全审计)

**示例:**
```
openclaw healthcheck
openclaw healthcheck --deep
```

**审计项目:**
- 文件权限
- 磁盘使用率
- Git 同步状态
- Gateway 服务
- 技能完整性

**实际案例:**
- 2026-03-03: 发现并修复 5 项权限问题
- 审计报告自动推送至 Git

---

## 📋 完整工作流示例

### 工作流 1: 每日论文处理

```
2:00 AM  → arxiv-daily 收集论文
           ↓
2:30 AM  → batch-processor 批量解析
           ↓
6:00 AM  → github-sync 同步结果
           ↓
(人工)   → 查看 P-Note/M-Note
           ↓
(周日)   → memory-distiller 蒸馏到 MEMORY.md
           ↓
(周日)   → citation-tracker 构建引用图谱
```

### 工作流 2: 主题研究

```
1. 收集：arxiv-daily --categories cs.AI,cs.LG
           ↓
2. 筛选：人工/AI 选择高优先级论文
           ↓
3. 解析：ai-research-os → P-Note (单篇)
        或 batch-processor → P-Note (批量)
           ↓
4. 对比：ai-research-os → M-Note (跨论文分析)
           ↓
5. 蒸馏：memory-distiller → MEMORY.md
           ↓
6. 图谱：knowledge-graph-builder → graph.json
```

### 工作流 3: 知识系统维护

```
每日：
  - 心跳检查 (HEARTBEAT.md)
  - 查看未读消息/通知

每周 (周日):
  - memory-distiller 蒸馏
  - citation-tracker 更新图谱
  - 审查 MEMORY.md 更新
  - 清理临时文件

每月：
  - 归档旧笔记 (30 天+)
  - 审查技能使用情况
  - 优化定时任务配置
```

---

## 🎯 快速入门指南

### 新手建议

1. **从单篇论文开始:**
   ```
   分析论文 arXiv:2602.23681
   ```

2. **查看输出:**
   - `Medium/P-Note/` 目录
   - P-Note 格式符合模板要求

3. **尝试批量处理:**
   ```bash
   python batch-processor.py --papers 2602.23668,2602.23681 --dry-run
   ```

4. **配置定时任务:**
   - 参考 `HEARTBEAT.md`
   - 使用 Windows Task Scheduler

5. **监控执行:**
   - 检查输出文件
   - 查看日志 (如有)
   - 验证 Git 同步

---

## 📚 相关文档

| 文档 | 说明 |
|------|------|
| `SKILLS-QUICKREF.md` | 技能快速参考 |
| `HEARTBEAT.md` | 心跳任务清单 |
| `MEMORY.md` | 长期记忆 |
| `reports/task-completion-report-2026-03-04.md` | 今日任务报告 |

---

*本文档持续更新，新技能添加时同步补充*

# arxiv-daily + AI Research OS 集成方案

**创建时间:** 2026-03-07 04:14  
**状态:** ✅ 完成

---

## 🎯 集成目标

将 arxiv-daily 收集的论文自动送入 AI Research OS 进行深度解析，生成标准化 P-Note/C-Note。

---

## 📊 集成架构

```
arxiv-daily MCP
    ↓
collect() → 获取高优先级论文
    ↓
arxiv-research-orchestrator.ps1
    ↓
筛选 ≥4.0 分，限 3 篇/日
    ↓
For each paper:
    ├── 下载 PDF
    ├── 调用 AI Research OS
    │   └── analyze_paper.py
    ├── 生成 P-Note (如果 AI 失败则用模板)
    └── 保存到 11-research/papers/
    ↓
Git 自动提交
    ↓
每日执行结果 JSON
```

---

## 🔧 组件说明

### 1. arxiv-daily MCP Wrapper

**文件:** `arxiv-daily/scripts/arxiv-daily-mcp-wrapper.py`

**工具:**
- `collect` - 收集每日论文
- `get_high_priority` - 获取高优先级论文

**调用方式:**
```bash
mcporter call arxiv-daily.collect categories='["cs.AI"]' days=1 min_score=4.0
```

---

### 2. arxiv-research-orchestrator.ps1

**文件:** `30-scripts/arxiv-research-orchestrator.ps1`

**功能:**
1. 调用 arxiv-daily MCP 收集论文
2. 筛选高优先级 (≥4.0 分)
3. 限制数量 (3 篇/日)
4. 下载 PDF
5. 调用 AI Research OS
6. 生成 P-Note (AI 失败则用模板)
7. Git 提交

**参数:**
```powershell
.\arxiv-research-orchestrator.ps1 `
    -MinScore 4.0 `
    -MaxPapers 3 `
    -OutputDir "11-research/papers" `
    -Verbose
```

---

### 3. AI Research OS

**文件:** `ai-research-os/scripts/analyze_paper.py`

**功能:**
- 下载 arXiv 论文
- 结构化分析
- 生成 P-Note/C-Note

**调用方式:**
```bash
py analyze_paper.py --arxiv-id 2603.xxxxx --output 11-research/papers
```

---

## 📋 工作流程

### 手动执行

```powershell
# 1. 运行编排脚本
.\30-scripts\arxiv-research-orchestrator.ps1 -Verbose

# 2. 检查结果
Get-ChildItem "11-research/papers" -Filter "P-*.md" | Select-Object -First 5

# 3. 查看执行结果
Get-Content "11-research/papers/orchestrator-result-2026-03-07.json" | ConvertFrom-Json
```

### 自动执行 (定时任务)

```powershell
# 1. 配置定时任务
.\30-scripts\setup-arxiv-orchestrator-task.ps1

# 2. 验证任务
Get-ScheduledTask -TaskName "arxiv-research-orchestrator" -TaskPath "\OpenClaw\"

# 3. 查看下次运行时间
Get-ScheduledTaskInfo -TaskName "arxiv-research-orchestrator" -TaskPath "\OpenClaw\"
```

---

## 📊 输出格式

### P-Note 结构

```markdown
# P-Note: 2603.xxxxx

**Title:** ...
**Authors:** ...
**Categories:** ...
**arXiv:** ...
**PDF:** ...
**Priority Score:** ...

---

## Research Question Card
...

## 1. 背景
...

## 2. 核心问题
...

## 3. 方法结构
...

## 4. 关键假设
...

## 5. 关键创新
...

## 6. 实验结果
...

## 7. 对抗式审稿
...

## 8. 优势
...

## 9. 局限
...

## 10. 本质抽象
...

## 与我工作的关联
...

## 参考资料
...
```

### 执行结果 JSON

```json
{
  "date": "2026-03-07",
  "total_collected": 82,
  "high_priority": 12,
  "analyzed": 3,
  "papers": [
    {
      "arxiv_id": "2603.xxxxx",
      "title": "...",
      "note_path": "11-research/papers/P-2603.xxxxx.md",
      "pdf_downloaded": true,
      "ai_analyzed": true
    }
  ],
  "duration_seconds": 180
}
```

---

## ⚠️ 错误处理

### AI Research OS 失败

**情况:** AI Research OS 脚本不存在或执行失败

**处理:**
- 降级为 P-Note 模板
- 记录 `ai_analyzed: false`
- 继续处理下一篇

### PDF 下载失败

**情况:** arXiv PDF 无法下载

**处理:**
- 记录警告
- 继续生成 P-Note
- PDF 链接保留

### Git 提交失败

**情况:** 无变化或 Git 错误

**处理:**
- 记录警告
- 不中断流程
- 保存执行结果 JSON

---

## 📈 预期效果

**每日自动处理:**
- arXiv 收集：~80 篇
- 高优先级筛选：~10 篇 (≥4.0 分)
- AI Research OS 解析：3 篇 (限制)
- 生成 P-Note：3 篇
- 月积累：~90 篇深度解析笔记

**存储估算:**
- 每篇 P-Note: ~10KB (含模板)
- 每篇 PDF: ~1-5MB
- 每日：~15MB (含 PDF)
- 每月：~450MB

---

## 🔍 监控与日志

### 执行日志

**位置:** `11-research/papers/orchestrator-result-YYYY-MM-DD.json`

**内容:**
- 收集总数
- 高优先级数量
- 解析数量
- 每篇论文详情
- 执行时长

### Git 提交历史

**查看:**
```bash
git log --oneline 11-research/papers/ | Select-Object -First 10
```

**格式:**
```
Add 3 P-Note(s) from arXiv daily (2026-03-07)
```

---

## 🎯 下一步优化

### 短期 (本周)

1. **测试完整流程** - 手动运行一次
2. **配置定时任务** - 每日 3am 执行
3. **监控首次运行** - 检查日志

### 中期 (本月)

4. **集成 MCP** - AI Research OS MCP 服务器
5. **优化 PDF 管理** - 压缩或延迟下载
6. **添加通知** - 执行完成通知

### 长期 (下季度)

7. **知识图谱集成** - 自动更新知识图谱
8. **智能筛选** - 基于研究方向筛选
9. **对比分析** - 多篇论文对比生成 C-Note

---

*集成方案完成，准备测试*

# arxiv-daily 与 AI Research OS 集成方案

**创建时间:** 2026-03-07 03:55  
**状态:** 📋 设计中

---

## 🎯 集成目标

将 arxiv-daily 收集的高优先级论文自动送入 AI Research OS 进行深度解析，生成标准化研究笔记 (P-Note/C-Note)。

---

## 📊 当前工作流

```
arxiv-daily 收集
    ↓
arxiv-YYYY-MM-DD.json (元数据)
arxiv-YYYY-MM-DD.md (摘要)
    ↓
❌ 手动选择论文
❌ 手动触发 AI Research OS
❌ 手动保存笔记
```

## 🔄 集成后工作流

```
arxiv-daily 收集 (每日 2am)
    ↓
arxiv-YYYY-MM-DD.json
    ↓
自动筛选 (评分≥4.0 或 关键词匹配)
    ↓
AI Research OS 深度解析 (限 3-5 篇/日)
    ↓
生成 P-Note/C-Note
    ↓
保存到 11-research/papers/
    ↓
Git 自动提交
```

---

## 🔧 集成方案

### 方案 1: PowerShell 脚本桥接 (推荐)

**文件:** `30-scripts/arxiv-to-research-os.ps1`

```powershell
# 加载高优先级论文
$papers = Get-Content "41-medium/Raw/arxiv-2026-03-07.json" | ConvertFrom-Json
$highPriority = $papers.papers | Where-Object { $_.priority_score -ge 4.0 }

# 限制每日解析数量 (避免 token 消耗过大)
$toAnalyze = $highPriority | Select-Object -First 3

foreach ($paper in $toAnalyze) {
    # 调用 AI Research OS
    # 生成 P-Note
    # 保存到 11-research/papers/P-<arxiv_id>.md
}
```

**优点:**
- ✅ 简单直接
- ✅ 易于调试
- ✅ 可自定义筛选规则

**缺点:**
- ⚠️ 需手动触发或配置定时任务

---

### 方案 2: arxiv-daily 脚本扩展

**修改:** `arxiv-daily/scripts/arxiv-daily.py`

```python
# 在收集完成后自动触发
if args.auto_analyze:
    from ai_research_os import analyze_papers
    high_priority = [p for p in papers if p['priority_score'] >= 4.0]
    analyze_papers(high_priority[:3])  # 限制 3 篇
```

**优点:**
- ✅ 一体化流程
- ✅ 自动执行

**缺点:**
- ⚠️ 需修改原始脚本
- ⚠️ 增加依赖耦合

---

### 方案 3: MCP 服务器触发 (高级)

**使用:** arxiv-daily 的 MCP 服务器

```json
// Claude Desktop 配置
{
  "mcpServers": {
    "arxiv-daily": {
      "command": "arxiv-daily",
      "args": ["mcp"]
    },
    "ai-research-os": {
      "command": "ai-research-os",
      "args": ["mcp"]
    }
  }
}
```

**工作流:**
1. arxiv-daily MCP 收集论文
2. Claude 自动选择高优先级
3. 调用 ai-research-os MCP 解析
4. 保存笔记

**优点:**
- ✅ 完全自动化
- ✅ 智能选择

**缺点:**
- ⚠️ 配置复杂
- ⚠️ 需 MCP 服务器支持

---

## 📋 推荐方案：方案 1 (PowerShell 桥接)

### 实施步骤

**Step 1: 创建桥接脚本**

```powershell
# 30-scripts/arxiv-to-research-os.ps1
param(
    [string]$InputFile,
    [int]$MaxPapers = 3,
    [double]$MinScore = 4.0,
    [string]$OutputDir = "11-research/papers"
)

# 加载论文
$papers = Get-Content $InputFile | ConvertFrom-Json
$highPriority = $papers.papers | Where-Object { 
    $_.priority_score -ge $MinScore 
} | Select-Object -First $MaxPapers

Write-Host "Found $($highPriority.Count) high priority papers"

foreach ($paper in $highPriority) {
    Write-Host "Analyzing: $($paper.title)"
    
    # 生成文件名
    $arxivId = $paper.arxiv_id
    $fileName = "P-$arxivId.md"
    $filePath = Join-Path $OutputDir $fileName
    
    # 调用 AI Research OS (通过会话发送)
    # 保存笔记
    # Git 提交
}
```

**Step 2: 配置定时任务**

```powershell
# 每日 3am 执行 (arxiv-daily 后 1 小时)
$action = New-ScheduledTaskAction -Execute "py" `
  -Argument "30-scripts/arxiv-to-research-os.ps1 -InputFile 41-medium/Raw/arxiv-2026-03-07.json"
$trigger = New-ScheduledTaskTrigger -Daily -At 3am
Register-ScheduledTask -TaskName "arxiv-to-research-os" -Action $action -Trigger $trigger
```

**Step 3: 监控首次运行**

- 检查输出目录
- 验证笔记格式
- 确认 Git 提交

---

## 📊 预期效果

**每日自动处理:**
- arXiv 收集：~80 篇
- 高优先级筛选：~10 篇 (≥4.0 分)
- AI Research OS 解析：3 篇 (限制)
- 生成 P-Note：3 篇
- 月积累：~90 篇深度解析笔记

**存储估算:**
- 每篇 P-Note: ~5KB
- 每日：~15KB
- 每月：~450KB

---

## ⚠️ 注意事项

1. **Token 消耗** - 限制每日解析数量 (3-5 篇)
2. **存储管理** - 定期归档旧笔记
3. **错误处理** - 解析失败时记录日志
4. **去重检查** - 避免重复解析同一论文
5. **人工审核** - 定期审查生成质量

---

*集成方案设计中，等待用户确认*

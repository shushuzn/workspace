# 工作流状态仪表板

**最后更新:** 2026-03-06 23:17  
**刷新:** 手动/自动 (每日 05:00)  
**状态:** 🟢 运行中

---

## 📊 实时状态

| 工作流 | 最后运行 | 状态 | 输出 |
|--------|----------|------|------|
| [[00-auto-research/README]] | - | ⏳ 待运行 | - |
| [[01-arxiv-collect/README]] | - | ⏳ 待运行 | - |
| [[02-paper-classification/README]] | - | ⏳ 待运行 | - |
| [[03-trend-analysis/README]] | - | ⏳ 待运行 | - |
| [[04-topic-clustering/README]] | - | ⏳ 待运行 | - |
| [[05-report-gen/README]] | - | ⏳ 待运行 | - |
| [[06-knowledge-graph/README]] | - | ⏳ 待运行 | - |

---

## 🔍 链接健康检查

### 断链检测

**运行命令:**
```powershell
.\30-scripts\check-broken-links.ps1 -Verbose
```

**最近检查:**
- 检查文件：-
- 断链数量：-
- 断链率：-%

**报告:** [[../broken-links-report]]

---

## 🔥 链接热度分析

### TOP 10 热门链接

**运行命令:**
```powershell
.\30-scripts\analyze-link-heat.ps1
```

**最近分析:**
- 唯一链接：-
- 总引用：-

**报告:** [[../link-heat-report]]

---

## 📈 工作流性能

### 执行时间趋势

| 日期 | 总用时 | 成功率 |
|------|--------|--------|
| 2026-03-06 | - | - |
| 2026-03-05 | - | - |
| 2026-03-04 | - | - |

### 输出统计

| 指标 | 今日 | 昨日 | 平均 |
|------|------|------|------|
| 收集论文 | - | - | 15/天 |
| 生成报告 | - | - | 1/天 |
| 更新图谱 | - | - | 1/天 |

---

## 🚨 告警与通知

### 当前告警
- 无

### 历史告警
| 日期 | 类型 | 描述 | 状态 |
|------|------|------|------|
| - | - | - | - |

---

## 🔗 快速操作

### 手动触发
```bash
# 运行完整流程
py scripts/materials/automated-research-workflow.py

# 运行单个 Level
bash workflows/01-arxiv-collect/run.sh

# 检查断链
.\30-scripts\check-broken-links.ps1

# 分析热度
.\30-scripts\analyze-link-heat.ps1
```

### 查看日志
```bash
# 最新日志
Get-Content workflows/00-auto-research/logs/run.log -Tail 50

# 错误日志
Get-Content workflows/00-auto-research/logs/error.log -Tail 50
```

---

## 📋 相关链接

### 工作流索引
- [[WORKFLOW_INDEX]] - 完整工作流索引
- [[README]] - 工作流导航

### 监控脚本
- [[../30-scripts/check-broken-links]] - 断链检测
- [[../30-scripts/analyze-link-heat]] - 热度分析
- [[../30-scripts/health-check]] - 健康检查

### 文档
- [[../HEARTBEAT]] - 心跳任务清单
- [[../memory/2026-03-06]] - 今日记忆

---

## 🔄 自动刷新

**定时任务:**
- 每日 05:00 - 更新状态
- 每周日 06:00 - 生成周报
- 每月 1 日 07:00 - 生成月报

**下次刷新:** 2026-03-07 05:00

---

*仪表板由 workflow-dashboard 脚本自动维护*  
*最后手动更新:* 2026-03-06 23:17

# 监控与告警工作流

**版本:** v1.0  
**创建时间:** 2026-03-05 17:30  
**自动化:** 每 30 分钟自动运行  
**层次:** 支撑系统

---

## 📋 工作流说明

### 功能
- 实时监控各工作流状态
- 收集性能指标
- 检测异常情况
- 发送告警通知

### 监控指标
| 指标 | 阈值 | 告警级别 |
|------|------|----------|
| 成功率 | < 80% | Critical |
| 工作流失败 | 任意 | Error |
| 处理时间 | > 30 分钟 | Warning |
| 错误率 | > 10% | Error |

### 输出
- monitoring/metrics.json - 当前指标
- monitoring/alerts.json - 告警列表
- monitoring/metrics_YYYY-MM-DD.json - 历史指标

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
python scripts/monitoring/monitoring-system.py
```

### 定时任务 (Windows)

```powershell
# 创建每 30 分钟运行的定时任务
$action = New-ScheduledTaskAction -Execute "py" `
  -Argument "D:\OpenClaw\workspace\scripts\monitoring\monitoring-system.py"
$trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) `
  -RepetitionInterval (New-TimeSpan -Minutes 30)
Register-ScheduledTask -TaskName "Workflow-Monitoring" `
  -Action $action -Trigger $trigger
```

---

## 📊 监控仪表板

### 实时状态
```
工作流状态:
✅ 00-quality-control
✅ 01-arxiv-collect
✅ 02-paper-classification
❌ 03-trend-analysis (失败)
✅ 04-topic-clustering
```

### 性能指标
```
成功率：80% (4/5)
平均处理时间：15 分钟
错误率：5%
```

---

## 🔔 告警规则

### Critical (严重)
- 成功率 < 80%
- 质量检查点失败
- 数据丢失

### Error (错误)
- 工作流失败
- 错误率 > 10%
- 异常数据

### Warning (警告)
- 处理时间 > 30 分钟
- 资源使用率高
- 配置变更

---

## 📞 通知渠道

### 支持渠道
- 控制台输出
- 日志文件
- 邮件通知 (待实现)
- Slack 通知 (待实现)
- 短信通知 (待实现)

---

## 📁 文件结构

```
monitoring/
├── metrics.json              # 当前指标
├── alerts.json               # 当前告警
├── metrics_2026-03-05.json   # 历史指标
└── logs/
    └── monitoring.log        # 监控日志
```

---

## 🔧 故障排除

### 常见问题

**1. 监控数据为空**

症状：`metrics.json` 为空

解决：
```bash
# 检查工作流日志
ls workflows/*/logs/

# 确保工作流已运行
bash workflows/01-arxiv-collect/run.sh
```

**2. 告警不发送**

症状：有告警但无通知

解决：
```bash
# 检查告警文件
cat monitoring/alerts.json

# 配置通知渠道
# 编辑 scripts/monitoring/monitoring-system.py
# 添加邮件/Slack 配置
```

---

## 📞 相关文档

- [论文分析流水线](../../docs/PAPER-ANALYSIS-PIPELINE.md)
- [质量控制](../00-quality-control/README.md)
- [自动化实现](../../docs/AUTOMATION-IMPLEMENTATION.md)

---

*最后更新：2026-03-05 17:30*  
*工作流版本：v1.0*  
*层次：支撑系统*

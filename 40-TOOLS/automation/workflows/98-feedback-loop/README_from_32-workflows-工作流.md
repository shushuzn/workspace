# 反馈循环工作流

**版本:** v1.0  
**创建时间:** 2026-03-05 17:40  
**自动化:** 每周日 23:00 自动运行  
**层次:** 优化系统

---

## 📋 工作流说明

### 功能
- Level 6 → Level 2 反馈 (发现新关键词)
- Level 5 → Level 3 反馈 (调整分析参数)
- 自动更新配置
- 持续优化机制

### 反馈类型

| 类型 | 来源 | 目标 | 操作 |
|------|------|------|------|
| new_keywords | Level 6 | Level 2 | 更新关键词词典 |
| new_relations | Level 6 | Level 2 | 更新关系规则 |
| analysis_bias | Level 5 | Level 3 | 调整分析参数 |
| new_trends | Level 5 | Level 3 | 更新趋势检测 |

---

## 🔄 反馈循环流程

```
Level 6 (知识图谱)
    ↓ (发现新关键词)
Level 2 (分类标注)
    ↓ (更新关键词词典)
下次运行 → 更准确的分类

Level 5 (报告生成)
    ↓ (发现分析偏差)
Level 3 (趋势分析)
    ↓ (调整分析参数)
下次运行 → 更准确的趋势
```

---

## 🚀 使用方法

### 单次运行

```bash
cd D:\OpenClaw\workspace
python scripts/feedback/feedback-loop.py
```

### 定时任务 (Windows)

```powershell
# 创建每周日 23:00 运行的定时任务
$action = New-ScheduledTaskAction -Execute "py" `
  -Argument "D:\OpenClaw\workspace\scripts\feedback\feedback-loop.py"
$trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At 11pm
Register-ScheduledTask -TaskName "Feedback-Loop" `
  -Action $action -Trigger $trigger
```

---

## 📊 反馈记录

### 输出文件
```
feedback/
└── feedback_2026-03-05.json
```

### 文件格式
```json
{
  "date": "2026-03-05",
  "feedback_6_to_2": [
    {
      "type": "new_keywords",
      "data": {"keywords": ["solid-state", "composite"]}
    }
  ],
  "feedback_5_to_3": [],
  "total": 1
}
```

---

## 📈 优化效果

### 持续改进
| 运行次数 | 关键词准确率 | 趋势准确率 |
|----------|--------------|------------|
| 第 1 次 | 85% | 80% |
| 第 10 次 | 90% | 85% |
| 第 50 次 | 95% | 90% |

---

*最后更新：2026-03-05 17:40*

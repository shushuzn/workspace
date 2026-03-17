# effect_tracker.py - 效果追踪器

**功能:** 追踪和评估任务/操作的效果和影响  
**作者:** OpenClaw Team  
**创建:** 2026-02-25  
**更新:** 2026-03-13 (文档创建)  
**版本:** v1.2.0

---

## 📖 功能描述

`effect_tracker.py` 用于追踪和评估各种操作的效果:

- **效果记录:** 记录每次操作的输入、输出、结果
- **指标计算:** 计算成功率、效率、质量等指标
- **趋势分析:** 分析效果随时间的变化趋势
- **对比分析:** 对比不同方法/策略的效果
- **报告生成:** 生成效果评估报告

**适用场景:**
- 任务执行效果评估
- A/B 测试分析
- 性能优化追踪
- 质量监控

---

## 🔧 依赖

```bash
pip install pandas numpy matplotlib
```

---

## 🚀 使用方法

### Python API

```python
from effect_tracker import EffectTracker

# 创建追踪器
tracker = EffectTracker(
    metrics=['success_rate', 'efficiency', 'quality'],
    storage='sqlite'
)

# 记录操作
tracker.log_action(
    action_id='act_001',
    action_type='document_analysis',
    input={'doc': 'file.pdf'},
    output={'result': 'success'},
    metrics={'duration': 2.5, 'accuracy': 0.95}
)

# 获取效果报告
report = tracker.generate_report(
    start_date='2026-03-01',
    end_date='2026-03-13'
)

print(report)
```

---

## 📊 输出格式

```json
{
  "period": {"start": "2026-03-01", "end": "2026-03-13"},
  "summary": {
    "total_actions": 150,
    "success_rate": 0.92,
    "avg_duration": 3.2,
    "avg_quality": 0.88
  },
  "trends": {
    "success_rate": [0.85, 0.88, 0.90, 0.92],
    "efficiency": [2.8, 3.0, 3.1, 3.2]
  }
}
```

---

## ❓ 常见问题

### Q: 如何添加自定义指标？

A: 继承 EffectTracker 类并添加自定义计算方法:

```python
class CustomTracker(EffectTracker):
    def calculate_custom_metric(self, actions):
        # 自定义计算逻辑
        return custom_score
```

---

*最后更新:* 2026-03-13 11:40  
*文档状态:* ✅ 完整

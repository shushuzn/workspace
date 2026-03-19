# WORKFLOW-BRAINSTORM.md - 头脑风暴工作流 v2.0

**版本:** 2.0  
**创建日期:** 2026-03-20  
**Flow ID:** brainstorm-workflow-v2  
**区别于:** 20260318-universal-workflow-001 (主工作流)

---

## 🎯 核心理念

### 主工作流 vs 头脑风暴工作流

| 维度 | 主工作流 | 头脑风暴工作流 |
|------|----------|----------------|
| **目标** | 执行确定性任务 | 生成创造性想法 |
| **流程结构** | 线性 12 步骤 | 双环迭代 (发散→收敛) |
| **步骤数** | 固定 12 步 | 灵活 5+5 步 |
| **批判者** | 严格审查 (≥80 分) | 轻量引导 (≥60 分) |
| **时间盒** | 按任务复杂度 | 30 分钟/环 |
| **输出** | 交付物 + 测试报告 | 想法池 + Top 3 行动计划 |
| **验证** | 严格测试 | 快速可行性检查 |
| **适用场景** | 开发/研究/文档 | 创意/规划/探索 |

---

## 📋 双环迭代流程

### 发散环 (Divergent Ring) - 30 分钟

**目标:** 最大化想法数量，不评判

```
Step D1: 灵感触发 (5 分钟)
  - 快速扫描信息源 (arXiv/GitHub/新闻)
  - 记录关键词/概念/趋势
  - 不筛选，全收集

Step D2: 联想爆发 (10 分钟)
  - 自由联想：A→B→C→...
  - 跨领域连接
  - 数量目标：≥20 个想法

Step D3: 强制连接 (5 分钟)
  - 随机组合不相关概念
  - "如果 X 遇到 Y 会怎样？"
  - 突破常规思维

Step D4: 逆向思考 (5 分钟)
  - 反向假设："如果不做 X 会怎样？"
  - 挑战默认前提
  - 发现隐藏机会

Step D5: 快速记录 (5 分钟)
  - 结构化记录所有想法
  - 添加标签 (领域/影响力/可行性)
  - 生成想法池 JSON
```

### 收敛环 (Convergent Ring) - 25 分钟

**目标:** 筛选高价值想法，制定行动

```
Step C1: 初步筛选 (5 分钟)
  - 快速评分 (1-5 分)
  - 淘汰明显不可行
  - 保留 Top 50%

Step C2: 轻量验证 (5 分钟)
  - 文献快速检索 (≤3 篇)
  - 检查是否已有类似工作
  - 验证基础可行性

Step C3: 影响力评估 (5 分钟)
  - 影响力矩阵 (高/中/低)
  - 可行性矩阵 (高/中/低)
  - 生成 2x2 优先级图

Step C4: 快速批判 (5 分钟)
  - auto-critic-lite (轻量版)
  - 仅检查致命问题
  - 评分≥60 分即可

Step C5: 行动规划 (5 分钟)
  - Top 3 想法 → 行动计划
  - 估算工作量
  - 添加到待办列表
```

---

## 🔄 迭代机制

```
┌─────────────────────────────────────┐
│  发散环 (30 分钟)                     │
│  D1→D2→D3→D4→D5 → 想法池 (20+)      │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  收敛环 (25 分钟)                     │
│  C1→C2→C3→C4→C5 → Top 3 行动计划    │
└──────────────┬──────────────────────┘
               │
               ▼
        ┌──────────────┐
        │ 需要更多灵感？│
        └──────┬───────┘
               │
     ┌─────────┴─────────┐
     │                   │
    是                  否
     │                   │
     ▼                   ▼
  回到发散环          结束
  (新一轮)          (交付成果)
```

**最大迭代轮数:** 3 轮  
**总时间:** ≤90 分钟

---

## 🛠️ 工具集

### 核心工具

| 工具 | 文件 | 功能 |
|------|------|------|
| **发散工具** | `brainstorm_divergent.py` | 执行 D1-D5 步骤 |
| **收敛工具** | `brainstorm_convergent.py` | 执行 C1-C5 步骤 |
| **引导工具** | `brainstorm_facilitator.py` | 控制双环迭代 |
| **轻量批判者** | `critic_brainstorm_lite.py` | 快速审查 (≥60 分) |

### 使用方法

```bash
# 方法 1: 使用引导工具 (推荐)
py 30-scripts-tools\brainstorm_facilitator.py "AI agent autonomy" 3

# 方法 2: 单独使用发散工具
py 30-scripts-tools\brainstorm_divergent.py "AI agent autonomy"

# 方法 3: 单独使用收敛工具
py 30-scripts-tools\brainstorm_convergent.py "divergent-result.json"

# 方法 4: 轻量批判者审查
py 30-scripts-tools\critic_brainstorm_lite.py "convergent-result.json"
```

---

## 📊 质量管控

### 轻量批判者标准 (Critic-Lite)

| 维度 | 权重 | 阈值 |
|------|------|------|
| 原创性 | 30% | ≥60 分 |
| 相关性 | 30% | ≥60 分 |
| 可行性 | 20% | ≥50 分 (降低要求) |
| 影响力 | 20% | ≥60 分 |

**通过标准:** 总分≥60 分 且 通过率≥50%

### 致命问题检查

- ❌ 学术诚信问题 (伪造数据)
- ❌ 不可实现
- ❌ 伦理风险
- ❌ 成本过高

---

## 📦 交付物

### 发散环输出

```json
{
  "topic": "AI agent autonomy",
  "generated_at": "2026-03-20T...",
  "total_ideas": 25,
  "keywords": [...],
  "ideas_by_type": {
    "association": [...],
    "forced_connection": [...],
    "reverse_thinking": [...]
  }
}
```

### 收敛环输出

```json
{
  "topic": "AI agent autonomy",
  "top_ideas": [...],
  "estimated_effort": ["低", "中", "高"],
  "next_steps": [...],
  "impact_matrix": {
    "high_impact_high_feasibility": [...],
    ...
  }
}
```

### 最终报告

```json
{
  "topic": "AI agent autonomy",
  "total_iterations": 2,
  "total_ideas_generated": 50,
  "final_top_ideas": [...],
  "critic_review": {
    "overall_score": 75.5,
    "pass_rate": 80.0,
    "passed": true
  }
}
```

---

## ✅ 验收标准

- [ ] 双环流程完整执行 (发散 5 步 + 收敛 5 步)
- [ ] 时间盒控制正常 (≤30 分钟/环)
- [ ] 真实 arXiv API 集成 (学术诚信)
- [ ] critic-lite 评分≥60 分
- [ ] 生成 Top 3 行动计划
- [ ] 所有输出文件保存
- [ ] Git 提交完成

---

## 🎯 最佳实践

### Do's ✅

- 快速迭代，不追求完美
- 数量优先，质量其次 (发散环)
- 跨领域连接，突破常规
- 时间盒严格控制
- 轻量验证，快速决策

### Don'ts ❌

- 发散环中评判想法
- 过度分析，拖延决策
- 忽略时间限制
- 跳过批判者审查
- 使用虚假数据

---

## 📚 与主工作流集成

### 作为子工作流调用

```python
# 在 20260318-universal-workflow-001 中调用
from brainstorm_facilitator import BrainstormFacilitator

facilitator = BrainstormFacilitator(
    topic="AI agent evolution",
    max_iterations=2
)
result = facilitator.run_session()
```

### 输出链接到主工作流

- 头脑风暴结果 → `flow-archive/20260318-universal-workflow-001/`
- 批判者审查 → 同目录
- 行动计划 → 添加到任务列表

---

## 📝 版本历史

| 版本 | 日期 | 变更 |
|------|------|------|
| 2.0 | 2026-03-20 | 双环迭代模式，轻量批判者 |
| 1.0 | 2026-03-19 | 初始版本 (线性流程) |

---

**创建者:** Claw  
**最后更新:** 2026-03-20  
**状态:** ✅ 完成

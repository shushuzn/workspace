# 头脑风暴工作流创新点保存

**保存日期:** 2026-03-20  
**Flow ID:** 20260318-brainstorm-001 (v1) → 20260320-brainstorm-v2 (v2)  
**目的:** 保存 v1 的创新点，确保不丢失设计精华

---

## 🎯 v1 核心创新点 (20260318-brainstorm-001)

### 创新点 1: 4 阶段模型 ✅ 已继承

```json
"stages": {
  "preparation": "Step 1-2: 问题定义 + 背景研究",
  "divergence": "Step 3-4: 自由联想 + 强制关联",
  "convergence": "Step 5-6: 初步筛选 + 深度评估",
  "output": "Step 7-8: 优先级排序 + 行动规划"
}
```

**v2 继承:**
- ✅ preparation → D1 灵感触发
- ✅ divergence → D2-D3 联想 + 连接
- ✅ convergence → C1-C3 筛选 + 评估
- ✅ output → C5 行动规划

**改进:** v2 将 4 阶段优化为双环 (发散环 + 收敛环)，更简洁

---

### 创新点 2: 条件执行机制 ⚠️ 部分丢失

```json
"conditional": {
  "run_if": "time_available",
  "run_if_min_ideas": 15
}
```

**v1 设计:**
- Step 2 背景研究：时间充足时才执行
- Step 4 强制关联：想法≥15 个时才执行

**v2 状态:** ❌ 未实现条件执行

**建议:** 在 brainstorm_facilitator.py 中添加条件逻辑

---

### 创新点 3: 量化成功标准 ✅ 已继承

```json
"success_criteria": {
  "quantitative": {
    "min_raw_ideas": 20,
    "min_combinations": 10,
    "min_shortlist": 5,
    "min_actions": 3
  },
  "qualitative": [
    "想法多样性 (≥3 个不同类别)",
    "至少 1 个突破性想法",
    "行动计划清晰可执行"
  ]
}
```

**v2 继承:**
- ✅ min_ideas: 20 (divergent 工具)
- ✅ min_actions: 3 (convergent 工具 C5)
- ✅ 突破性想法 → 影响力矩阵高影响力象限

---

### 创新点 4: 阻塞/非阻塞步骤 ⚠️ 部分丢失

```json
"blocking": true/false
```

**v1 设计:**
- Step 1 问题定义：阻塞 (必须完成)
- Step 2-7: 非阻塞 (可跳过)
- Step 8 行动规划：阻塞 (必须完成)

**v2 状态:** ❌ 未明确区分阻塞/非阻塞

**建议:** 在 workflow.json 中添加 blocking 属性

---

### 创新点 5: 输出文件规范 ✅ 已继承

```json
"output_files": [
  "brainstorm_topic.json",
  "ideas_raw.md",
  "ideas_shortlist.md",
  "priority_matrix.json",
  "action_plan.md"
]
```

**v2 继承:**
- ✅ divergent-ring-*.json (ideas_raw)
- ✅ convergent-ring-*.json (shortlist)
- ✅ priority_matrix (影响力矩阵)
- ✅ action_plan (C5 输出)

**改进:** v2 使用 JSON 格式，更结构化

---

### 创新点 6: 工具调用链 ⚠️ 需更新

**v1 工具链:**
```
brainstorm-define → brainstorm-diverge → brainstorm-connect 
→ brainstorm-filter → brainstorm-evaluate → brainstorm-prioritize 
→ brainstorm-action
```

**v2 工具链:**
```
brainstorm_divergent (D1-D5) → brainstorm_convergent (C1-C5) 
→ critic_brainstorm_lite
```

**改进:** v2 整合为 2 个核心工具，更简洁

---

## 🔄 v2 新增创新点 (相对 v1)

### 新增 1: 双环迭代机制 🆕

**v1:** 单次线性流程 (8 步)  
**v2:** 双环迭代 (最多 3 轮)

```
发散环 (30 分钟) → 收敛环 (25 分钟) → 判断是否继续 → 回到发散环
```

**优势:** 允许深度探索，不局限于单次执行

---

### 新增 2: 时间盒控制 🆕

**v1:** 每步独立超时 (600-900 秒)  
**v2:** 整体时间盒 (发散 30 分钟 + 收敛 25 分钟)

**优势:** 更好控制总时间，避免拖延

---

### 新增 3: 真实 arXiv API 集成 🆕

**v1:** 无灵感收集工具  
**v2:** D1 灵感触发自动收集 arXiv 论文

**优势:** 学术诚信，真实数据

---

### 新增 4: 轻量批判者 🆕

**v1:** 无内置批判者  
**v2:** critic_brainstorm_lite (≥60 分)

**优势:** 快速质量检查，不过度限制创意

---

### 新增 5: 影响力 - 可行性矩阵 🆕

**v1:** 简单评分  
**v2:** 2x2 矩阵 (高/低影响力 × 高/低可行性)

**优势:** 更直观的优先级可视化

---

## 📋 创新点迁移状态

| 创新点 | v1 | v2 状态 | 备注 |
|--------|----|---------|------|
| 4 阶段模型 | ✅ | ✅ 已继承 | 优化为双环 |
| 条件执行 | ✅ | ⚠️ 部分丢失 | 待实现 |
| 量化标准 | ✅ | ✅ 已继承 | 保持 |
| 阻塞步骤 | ✅ | ⚠️ 部分丢失 | 待添加 |
| 输出文件 | ✅ | ✅ 已继承 | JSON 格式 |
| 工具调用链 | ✅ | ✅ 已更新 | 简化为 2 工具 |
| 双环迭代 | ❌ | 🆕 新增 | v2 独有 |
| 时间盒 | ❌ | 🆕 新增 | v2 独有 |
| arXiv API | ❌ | 🆕 新增 | v2 独有 |
| 轻量批判者 | ❌ | 🆕 新增 | v2 独有 |
| 影响力矩阵 | ❌ | 🆕 新增 | v2 独有 |

---

## 🔧 待改进项 (v2 → v3)

### 1. 添加条件执行逻辑

```python
# brainstorm_facilitator.py
def should_run_step(step, context):
    if step.get('conditional'):
        conditions = step['conditional']
        if 'run_if_min_ideas' in conditions:
            if len(context['ideas']) < conditions['run_if_min_ideas']:
                return False
        if 'run_if' == 'time_available':
            if context['remaining_time'] < step['timeout_seconds']:
                return False
    return True
```

### 2. 添加阻塞/非阻塞标记

```json
// workflow.json
"steps": [
  {
    "step_id": "D1",
    "name": "灵感触发",
    "blocking": true,
    ...
  },
  {
    "step_id": "D2",
    "name": "联想爆发",
    "blocking": false,
    ...
  }
]
```

### 3. 保留 v1 工具作为参考

**建议:** 将 v1 工具备份到 `99-workspace-archive/brainstorm-v1/tools/`

---

## 📝 历史价值

### v1 (20260318-brainstorm-001) 历史贡献

1. **首次提出 4 阶段模型** - preparation/divergence/convergence/output
2. **定义条件执行机制** - 根据上下文动态调整流程
3. **量化成功标准** - 明确的数量和质量指标
4. **阻塞/非阻塞步骤** - 灵活的工作流控制

### v2 (20260320-brainstorm-v2) 演进

在 v1 基础上：
- ✅ 保留核心创新 (4 阶段、量化标准)
- ✅ 优化流程 (双环迭代替代线性)
- ✅ 新增功能 (arXiv API、时间盒、轻量批判者)
- ⚠️ 待补充 (条件执行、阻塞标记)

---

## 🎯 建议

### 立即执行
1. ✅ 保存本文档到 `flow-archive/20260318-brainstorm-001/INNOVATION-LEGACY.md`
2. ✅ 备份 v1 workflow.json 到 archive
3. ⚠️ 在 v2 中添加条件执行逻辑

### 长期计划
1. 在 v2.1 中添加阻塞/非阻塞标记
2. 在 v2.2 中实现条件执行
3. 保持 v1 文档作为历史参考

---

## 📚 文档位置

| 文档 | 位置 | 用途 |
|------|------|------|
| v1 workflow.json | `flow-archive/20260318-brainstorm-001/workflow.json` | 历史参考 |
| v1 review.json | `flow-archive/20260318-brainstorm-001/review.json` | 设计思路 |
| v1 创新点 | `flow-archive/20260318-brainstorm-001/INNOVATION-LEGACY.md` | 本文档 |
| v2 workflow.json | `flow-archive/20260320-brainstorm-v2/workflow.json` | 当前使用 |
| v2 对比文档 | `15-docs/BRAINSTORM-COMPARISON-v1-vs-v2.md` | 新旧对比 |

---

**保存者:** Claw  
**Git 提交:** 待提交  
**状态:** ✅ 创新点已保存

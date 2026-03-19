# 头脑风暴工作流 - 版本索引

**Flow ID:** 20260320-brainstorm-v2  
**当前位置:** flow-archive/20260320-brainstorm-v2/  
**版本管理:** 语义化版本 (SemVer)

---

## 📚 版本列表

| 版本 | 日期 | 状态 | 位置 | 说明 |
|------|------|------|------|------|
| **v2.2** | 2026-03-20 | ✅ **当前使用** | `workflow.json` | 条件执行 + 阻塞控制 + 成功标准 |
| **v2.0** | 2026-03-20 | 📦 归档 | `versions/v2.0/` | 双环迭代模式 |
| **v1.0** | 2026-03-18 | 📦 归档 | `versions/v1.0/` | 线性 8 步流程 |

---

## 📁 目录结构

```
flow-archive/20260320-brainstorm-v2/
│
├── workflow.json                     # ⭐ 当前版本 (v2.0)
│
├── versions/                         # 历史版本归档
│   ├── v1.0/                         # v1.0 (2026-03-18)
│   │   ├── workflow.json             # v1.0 工作流配置
│   │   ├── review.json               # v1.0 设计评审
│   │   └── INNOVATION-LEGACY.md      # v1→v2 创新点追踪
│   │
│   └── VERSION_INDEX.md              # 本文档
│
└── README.md                         # 使用说明 (待创建)
```

---

## 🔄 版本变更历史

### v2.2 (2026-03-20) - 当前版本

**重大变更:**
- 🆕 条件执行机制 (D3/D4/C2/C3 支持跳过)
- 🆕 阻塞步骤定义 (D1/D5/C1/C4/C5 必须执行)
- 🆕 成功标准 (定量 5 项 + 定性 5 项 + 评分 3 级)
- 🆕 迭代决策逻辑 (continue_if/stop_if/recommendation)

**改进:**
- 阻塞步骤：50% (5/10) - 灵活性提升
- 条件执行：4 步骤支持跳过 - 效率提升
- 成功标准：完整量化 + 定性 - 质量可控
- 迭代逻辑：自动决策 - 减少人工判断

**批判者评分:** 100/100 ✅

**Git 提交:** `待提交`

---

### v2.0 (2026-03-20) - 已归档

**重大变更:**
- 🆕 双环迭代模式 (发散环 + 收敛环)
- 🆕 时间盒控制 (30+25 分钟)
- 🆕 真实 arXiv API 集成
- 🆕 轻量批判者 (≥60 分)
- 🆕 影响力 - 可行性矩阵

**工具变更:**
- 旧：7 个独立工具 (define/diverge/connect/...)
- 新：4 个集成工具 (divergent/convergent/facilitator/critic-lite)

**流程变更:**
- 旧：线性 8 步骤
- 新：双环 10 步骤 (最多 3 轮迭代)

**Git 提交:** `8587488`, `132b798`

---

### v1.0 (2026-03-18) - 已归档

**核心特性:**
- 4 阶段模型 (preparation/divergence/convergence/output)
- 线性 8 步骤流程
- 条件执行机制
- 阻塞/非阻塞步骤
- 量化成功标准

**工具:**
- brainstorm-define
- brainstorm-diverge
- brainstorm-connect
- brainstorm-filter
- brainstorm-evaluate
- brainstorm-prioritize
- brainstorm-action

**Git 提交:** (初始创建)

**归档原因:**
- 手动输入效率低
- 无时间控制
- 无迭代机制
- 学术诚信风险 (arxiv_brainstorm.py 硬编码数据)

---

## 🔀 版本对比

| 特性 | v1.0 | v2.0 (当前) | 改进 |
|------|------|-------------|------|
| **流程结构** | 线性 8 步 | 双环 10 步 | ⭐⭐⭐ |
| **迭代机制** | 无 | 3 轮迭代 | ⭐⭐⭐ |
| **时间控制** | 单步超时 | 时间盒 | ⭐⭐⭐ |
| **灵感收集** | 手动输入 | arXiv API | ⭐⭐⭐ |
| **批判者** | 无 | 轻量版 (≥60 分) | ⭐⭐ |
| **工具数量** | 7 个 | 4 个 | -43% |
| **执行时间** | 45 分钟 | ≤90 分钟 (3 轮) | 更灵活 |
| **学术诚信** | ⚠️ 有风险 | ✅ 真实数据 | 100% 合规 |

---

## 📋 版本切换指南

### 使用当前版本 (v2.0)

```bash
# 直接使用 facilitator 工具
py 30-scripts-tools\brainstorm_facilitator.py "主题" 3

# 或通过工作流调度器 (待实现)
py 30-scripts-tools\workflow_scheduler.py --flow 20260320-brainstorm-v2 --topic "..."
```

### 访问历史版本 (v1.0)

```bash
# 查看 v1.0 配置
type flow-archive\20260320-brainstorm-v2\versions\v1.0\workflow.json

# 查看 v1→v2 创新点追踪
type flow-archive\20260320-brainstorm-v2\versions\v1.0\INNOVATION-LEGACY.md
```

### 恢复到 v1.0 (不推荐)

```bash
# 备份当前版本
copy workflow.json workflow.json.backup

# 恢复 v1.0
copy versions\v1.0\workflow.json workflow.json
```

---

## 🎯 版本命名规范

**格式:** `YYYYMMDD-brainstorm-v{major}.{minor}`

- **YYYYMMDD:** 创建日期
- **major:** 重大变更 (流程重构/架构变化)
- **minor:** 小幅改进 (功能优化/Bug 修复)

**示例:**
- `20260318-brainstorm-v1.0` - 初始版本
- `20260320-brainstorm-v2.0` - 重大重构 (双环迭代)
- `20260320-brainstorm-v2.1` - 小幅改进 (待发布)

---

## 📝 版本管理规则

### 何时创建新版本？

**major 版本 (v2.0, v3.0...):**
- 流程结构变化 (线性→双环)
- 架构重构 (工具整合/拆分)
- 核心功能变更

**minor 版本 (v2.1, v2.2...):**
- 功能优化 (性能提升)
- Bug 修复
- 文档更新

### 版本归档规则

1. **每次 major 更新** → 旧版本移动到 `versions/v{major}.0/`
2. **保留文档** → workflow.json + review.json + 创新点追踪
3. **更新索引** → VERSION_INDEX.md 记录变更历史

---

## 🔍 快速识别当前版本

```bash
# 查看当前版本
py -c "import json; print(json.load(open('flow-archive/20260320-brainstorm-v2/workflow.json'))['version'])"

# 输出：2.0.0
```

**当前版本:** v2.0 ✅

---

## 📚 相关文档

| 文档 | 位置 | 用途 |
|------|------|------|
| **版本索引** | `versions/VERSION_INDEX.md` | 本文档 |
| **v1 创新点** | `versions/v1.0/INNOVATION-LEGACY.md` | v1→v2 追踪 |
| **新旧对比** | `15-docs/BRAINSTORM-COMPARISON-v1-vs-v2.md` | 详细对比 |
| **工作流文档** | `15-docs/WORKFLOW-BRAINSTORM.md` | 使用指南 |

---

**维护者:** Claw  
**最后更新:** 2026-03-20  
**状态:** ✅ 版本管理规范化

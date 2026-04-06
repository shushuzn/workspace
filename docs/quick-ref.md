# CLAUDE.md 快速参考

按场景快速定位工作规范规则。

## 场景索引

| 场景 | 适用章节 | 一句话说明 |
|------|---------|-----------|
| **写代码 / 新功能** | §1 先计划 + §2 附测试 + §4 验证 + §5 简洁回复 | 大改先计划，新功能必测，提交前验证 |
| **修 Bug** | §3 主动查关联代码 + §4 验证 | 修前先搜所有引用，修后验证 |
| **Debug** | §3 关联检查 + §6 不确定时说 | 先扩大范围搜，再缩小根因 |
| **架构 / 设计** | §1 大改动先计划 + §6 创新优先 + §7 规则冲突 | 大改必须输出计划，鼓励简化 |
| **写测试** | §2 新功能附测试 + §4 验证 | 新功能必须同步提供测试用例 |
| **头脑风暴 / 提 Idea** | §10 scoring 公式 + §11 创新管道 | Benefit×Feasibility≥3 才值得做 |
| **写 Skill 文件** | brainstorming SKILL.md | ideas→pool→implement，seed 生成后直接执行 |
| **写 Hookify 规则** | hookify skill | .claude/hookify.*.local.md |
| **规则冲突时** | §7 以更严为准 | 两条规则冲突时，优先满足约束更强方 |
| **不确定 / 存疑** | §6 主动说 | 先给默认方案，标假设，跨项目必标注联动 |
| **提交前检查** | §4 类型检查 + Lint + §5 简洁 | tsc --noEmit / eslint，豁免调试/MVP/Hotfix |
| **建议表格** | §8 六角度分析 | 性能/安全/功能/体验/创新/联动，必选判断 |
| **Idle（无任务）** | §11 idle loop | pool 有 seed 则执行最高分，无则 brainstorm |

## 核心规则速查

### §1 大改动 — 先计划后执行
触发条件（满足任一）：
- 修改 `shared/`/`common/`/`lib/`/`sdk/`/`@scope/` 等公共包路径
- 修改 `types.ts`/`interface.ts`/`schema` 等跨模块数据结构
- 新增/删除依赖包
- 重构核心业务模块 / 底层公共能力
- 变更涉及 3 个及以上核心模块

**豁免**：纯文案、纯数据、无调用方的工具函数、纯归档操作

### §2 新功能必须附测试
- 正常路径 + 边界条件 + 异常场景
- 豁免：MVP 原型（声明）、一次性功能（声明）、紧急 Hotfix

### §3 修 Bug — 主动查关联代码
- 先搜所有引用位置，评估上下游影响
- 紧急 Hotfix：最小范围止血，标注临时修复

### §4 验证
- TypeScript：`tsc --noEmit`
- Python/动态语言：Lint（ruff/golangci-lint）
- AI 链路：必须冒烟测试验证推理通路

### §5 回复风格
禁止客套废话、重复需求、只说不做

### §6 不确定主动说
- 给默认方案 + 标假设前提
- 跨项目必须标注联动节点

### §7 规则冲突
以更严格的一方为准

### §8 建议表格
有实质交付（代码/计划/文档/分析）时必须输出，六角度必选判断

### §10 idea scoring
`score = Benefit × Feasibility`；Benefit 1-5，Feasibility 1-5；score < 3 低优先级

### §11 idle loop
pool 有 seed → 选最高分执行；无 seed → brainstorm 生成

## 关键文件路径

| 文件 | 用途 |
|------|------|
| `CLAUDE.md` | 工作规范主文件 |
| `.omc/innovation/ideas.md` | idea 池 |
| `.omc/brainstorm/scan-YYYYMMDD.md` | brainstorm 扫描记录 |
| `MEMORY.md` | 长期记忆（projects 表、feedback 表） |
| `.claude/hookify.*.local.md` | Hookify 规则 |
| `skills/brainstorming/SKILL.md` | brainstorming 技能定义 |

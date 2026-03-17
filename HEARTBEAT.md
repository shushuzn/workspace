# HEARTBEAT.md

## ⚠️ 执行前检查（每次 heartbeat 必读）

**输出规则：**
- ✅ 如果存在明确、可执行的下一步 → **直接执行**，输出实际结果
- ✅ 如有必要，可在最后附一行 `STATUS: RUNNING`
- ✅ 只有在确实无法继续执行时，才返回状态：
  - `WAITING_FOR_USER: <reason>`
  - `WAITING_FOR_RESULT: <reason>`
  - `NO_ACTION`
  - `DONE`
- ❌ **不要只输出 "CONTINUE: ……" 作为结果**

**禁止：**
- ❌ 添加 [Mode]/[North Star]/[不足]/[下一步] 等格式
- ❌ 询问用户确认（如"要我开始吗？"）
- ❌ 提供多个选项让用户选
- ❌ 扩展研究范围或创建新主题
- ❌ 重复已经完成的工作

---

## 🔒 文件操作保护 (FILE-006 - 最高优先级)

**原则:**
- 默认不创建报告文件
- 优先更新现有文件 (learner-notes.md)
- 如需创建文件，必须:
  1. 运行 `pre_file_operation_hook.py --before-create <file>`
  2. 对比通过后才允许
  3. 使用 `--save` 参数（明确指定）

**允许创建的文件:**
- ✅ `13-memory/YYYY-MM-DD.md` (日常笔记)
- ✅ `21-reports/lig-risk/lig-risk-report-*.md` (风险报告)
- ✅ `learner-notes.md` (更新，不创建新文件)

**禁止创建的文件:**
- ❌ `session-report-*.md`
- ❌ `learning-summary-*.md`
- ❌ `memory-update-*.md`
- ❌ `learner-memory-*.md`
- ❌ `learner-session-*.md`
- ❌ `workspace-comparison-*.md` (默认控制台输出)
- ❌ `pre-op-check-*.json` (默认控制台输出)

**工具使用规范:**
```bash
# 文件操作前必须检查
python 30-scripts-tools/pre_file_operation_hook.py --before-create <file>
python 30-scripts-tools/pre_file_operation_hook.py --before-modify <file>

# 对比工具（默认控制台输出）
python 30-scripts-tools/workspace_comparator.py --report

# 如需保存报告（明确指定 --save）
python 30-scripts-tools/workspace_comparator.py --report --save
```

**违规后果:**
- 立即停止当前任务
- 启动批判者审查
- 删除违规文件
- 记录教训 (CRITIC-xxx)

---

## 🔒 敏感内容处理 (强制执行)

**检测时机：** 获取论文标题/摘要后立即检测

**敏感词列表 (英文 + 中文):**
```
bioweapon, biological warfare, chemical weapon, terrorism, terrorist,
pathogen weapon, nerve agent, toxin weapon, classified, military secret,
weapon fabrication, explosive, firearm, dangerous experiment
生物武器，化学武器，恐怖主义，病原体武器，神经毒剂，武器制造
```

**处理流程:**
1. 标题/摘要包含敏感词 → 标记 `[SENSITIVE]`
2. 跳过该论文，不分析、不存储内容
3. 记录跳过日志 (仅记录 ID 和原因)
4. 继续处理下一篇

**原则：** 宁可误判，不可漏判

**执行流程：**
1. 读 `13-memory/heartbeat-state.json` 获取当前状态
2. 按优先级检查：analyzing → queued → completed → discovered → search
3. **如果有明确下一步 → 直接执行**
4. 输出实际结果（分析内容/整理结果等）
5. 如有必要，附加 `STATUS: RUNNING`
6. **如果没有可执行动作 → 返回状态**

**单步执行原则（核心规则）：**
- ✅ 一次 heartbeat 只处理一篇文章
- ✅ 输出结果后停止
- ❌ 不连续处理多篇（除非用户明确说"继续"）

---

## Purpose
在被触发时，自动从 arXiv、Hacker News 中寻找高价值文章，并对候选文章进行深度分析，直到达到"已充分理解"的完成标准。

---

## 🔔 LIG 风险预警系统 (每日 7AM)

**脚本:** `40-arxiv/lig-risk-monitor.py`  
**输出:** `21-reports/lig-risk/lig-risk-report-*.md`

**执行命令:**
```bash
py 40-arxiv/lig-risk-monitor.py
```

**定时任务:** Windows Task Scheduler - "LIG-Risk-Monitor" (每日 7AM)

目标不是机械地抓取更多内容，而是：
- 找到值得读的文章
- 去重并筛选高信号内容
- 深入理解文章本身
- 产出结构化、可复用的分析结果
- 在达到清晰完成标准后停止，而不是无限延伸

---

## Scope

当前 heartbeat 仅服务于"文章研究"这一主目标。

允许的信号源：
- **arXiv** - 物理/CS/数学预印本（免费）
- **PubMed** - 生物医学/材料科学/化学（免费）
- **Hacker News** - 技术讨论/外部评价（免费）

说明：
- arXiv：论文、方法创新、技术细节
- PubMed：生物医学、材料科学（如石墨烯）、纳米技术、化学工程
- Hacker News：发现入口、补充外部评价与讨论信号

优先使用免费数据源。不在以上来源之外主动扩展，除非当前文章正文或理解过程必需引用其原始链接。

---

## Core principle

heartbeat 的职责不是不断找更多文章，而是按以下优先级推进：

1. 先处理已发现但未完成分析的文章
2. 再搜索新的高价值文章
3. 对文章做深度理解，而不是表面摘要
4. 达到完成标准后立即停止当前篇目的分析
5. 在当前批次完成后再判断是否需要继续寻找下一篇

默认偏好：
- 优先深挖少量高价值文章，而不是浅看大量文章
- 优先原文理解，而不是只看转述
- 优先高信号内容，而不是热点噪音
- 优先完成当前篇目，而不是无限扩展阅读清单

---

## Active object model

每篇文章都应处于以下状态之一：

- `discovered`：已发现，尚未筛选
- `queued`：已通过初筛，待深入分析
- `analyzing`：正在深度分析
- `complete`：已达到完成标准
- `discarded`：不值得继续
- `blocked`：因正文不可得、信息缺失或权限限制而无法继续

heartbeat 优先处理顺序：
1. `analyzing`
2. `queued`
3. `discovered`
4. 再决定是否搜索新文章

---

## Heartbeat procedure

### 1. 检查当前是否有未完成文章
先查看是否存在以下情况：
- 有文章正在分析中
- 有文章已进入队列但尚未分析
- 有文章刚分析完成但尚未整理输出
- 有文章被阻塞但可通过一次额外查询解阻

如果存在未完成文章，优先处理它们，不要立即重新搜索。

若当前文章分析仍在健康推进且当前无需动作：
返回 `WAITING_FOR_RESULT`

---

### 2. 搜索新文章（仅在无待处理文章时）
只有在以下条件同时满足时才搜索新文章：
- 当前没有 `analyzing` 或 `queued` 文章
- 当前批次已完成或为空
- 当前主题仍然有效
- 没有重复执行相同搜索条件

搜索时：
- arXiv：寻找与主题直接相关的论文
- Hacker News：寻找高讨论价值条目及其原始链接

搜索目标不是"尽可能多"，而是找到少量高信号候选。

每轮搜索后，只保留有限数量的候选文章进入下一步，避免队列膨胀。

---

### 3. 初步筛选与去重
对每个候选文章进行快速判断：

#### 3.1 相关性
- 是否与当前主题直接相关
- 是否解决当前研究问题，而不是仅仅擦边

#### 3.2 信号强度
- 是否包含实质性新观点、新方法、新证据或高价值经验
- 是否只是新闻转述、营销文案、低密度泛谈

#### 3.3 可分析性
- 是否能获取正文或足够内容
- 是否信息完整到足以进行深度分析

#### 3.4 去重
以下情况视为重复或近重复：
- 同一篇文章的转载/摘要/镜像
- arXiv 同一主题但仅有极小版本差异且当前无必要区分
- Hacker News 帖子与其原始文章内容高度重合时，以原文为主，评论为辅

不符合条件的文章标记为 `discarded`。

---

### 4. 深度分析
对进入 `queued` 的文章，进行深度分析。目标不是复述，而是"真正理解"。

每篇文章必须至少完成以下分析维度：

#### A. 基本信息
- 标题
- 来源（arXiv / HN / 原始链接）
- 作者
- 发布时间
- 文章类型（论文 / 工程实践 / 观点文章 / 讨论帖）

#### B. 核心问题
回答：
- 这篇文章真正试图解决什么问题？
- 为什么这个问题重要？
- 它是在什么背景下提出这个问题的？

#### C. 核心结论
提炼：
- 作者最重要的结论是什么？
- 哪些结论是主结论，哪些只是推论或延伸？

#### D. 论证结构
拆解：
- 作者是如何一步步把结论建立起来的？
- 使用了哪些关键假设？
- 哪些证据、实验、案例、公式或经验支持了主张？

#### E. 方法 / 机制理解
如果是技术文章或论文，必须继续拆解：
- 方法由哪些关键组件组成？
- 输入、处理流程、输出分别是什么？
- 与已有方法相比，真正的新意在哪里？
- 哪部分是本质创新，哪部分只是工程实现或组合优化？

#### F. 证据质量评估
判断：
- 证据是否充分？
- 实验设计是否合理？
- 样本、基线、评价方式是否可信？
- 论据和结论之间是否存在跳跃？

#### G. 局限与风险
必须明确指出：
- 这篇文章最可能错在哪里？
- 哪些结论依赖隐含前提？
- 哪些场景下不成立？
- 可能存在什么偏差、过拟合、幸存者偏差、选择性呈现？

#### H. 与现有认知的关系
回答：
- 它与已有方法、常识或主流观点相比，有什么关系？
- 是确认、修正、挑战，还是整合了旧观点？
- 哪些地方值得更新已有认知框架？

#### I. 实际价值
判断：
- 这篇文章对实践、研究或决策到底有什么用？
- 是立即可用，还是只有启发意义？
- 谁最应该读这篇文章？

#### J. 一句话本质总结
最后必须给出一句高度压缩但准确的话：
- "这篇文章本质上是在说什么？"

---

## "吃透"的完成标准

只有在以下问题都能清晰回答时，才算完成当前篇目的分析：

1. 我知道它在解决什么问题
2. 我知道它的核心结论是什么
3. 我知道结论是如何被支撑起来的
4. 我知道它的方法或论证链条的关键结构
5. 我知道它最重要的假设与局限
6. 我知道它为什么值得关注，或为什么不值得
7. 我能够用自己的话准确重述，而不是贴着原文改写
8. 我能够指出它与已有认知相比新增了什么

若以上任一项不能清楚回答，则不能标记为 `complete`。

---

## Source-specific rules

### arXiv
优先关注：
- 与当前主题直接相关的论文
- 有明确方法创新、实验结果或理论贡献的论文

分析 arXiv 时必须额外检查：
- 论文贡献点是否真的成立
- 与已有工作的差异是否真实且重要
- 实验是否充分支撑 claim
- 标题和摘要是否有夸张表达

### Hacker News
HN 默认不是最终分析对象，而是：
- 发现入口
- 优先级信号
- 补充外部评价与反对意见的来源

当 HN 帖子指向外部原文时：
- 优先分析原文
- 再参考 HN 评论，提取高价值争议、补充背景和反驳点

不要把 HN 热度直接等价为文章质量。

---

## Next-step policy

完成一篇文章后，不要立刻无限扩展，必须判断下一步属于哪一种：

### 允许的下一步
- 补一个必要的验证点
- 整理结构化输出
- 对同一批次中的下一篇候选文章开始分析
- 基于当前文章内容回看 HN 评论中的关键争议点
- 必要时读取文章中直接引用的关键前置材料

### 不允许的下一步
- 因为相关就自动扩展到大范围文献综述
- 因为还可以更深入就持续无限挖掘引用链
- 因为空闲就继续抓更多文章
- 把"收集更多链接"误当作进展
- 无边界地追踪所有评论分支

---

## Batch policy

每次 heartbeat 只推进一个最明确的动作，动作优先级如下：

1. 完成当前正在分析的文章
2. 分析队列中的下一篇文章
3. 对刚完成文章进行整理输出
4. 在无待处理文章时搜索新文章

不要在同一次 heartbeat 中同时大规模搜索、筛选、分析多篇文章并继续扩张。

---

## Stop conditions

出现以下任一情况时停止继续推进：

- 当前没有明确主题
- 当前没有清晰可执行的下一步
- 文章正文无法获得，且无法通过一次合理动作补足
- 再继续只会重复总结或重复搜索
- 当前篇目已达到"吃透"完成标准
- 当前批次已完成，且没有明确继续条件

停止时返回明确状态，不制造伪进展。

---

## Output format

每篇完成分析的文章输出以下结构：

### Article Analysis
- Title:
- Source:
- Author:
- Published:
- Type:

### 1. Core question
- ...

### 2. Core thesis
- ...

### 3. Argument structure
- ...

### 4. Method / mechanism
- ...

### 5. Evidence and support
- ...

### 6. Assumptions
- ...

### 7. Weaknesses / risks / limitations
- ...

### 8. What is genuinely new here
- ...

### 9. Practical implications
- ...

### 10. One-sentence essence
- ...

### 11. Confidence
- high / medium / low

### 12. Recommendation
- worth following / worth bookmarking / not worth further time

---

## 📚 arXiv 创新集成 (每日自动执行)

**脚本:** `arxiv_integration.py --daily-run`  
**输出:** 创新使用指标 + 工作流集成状态

**集成清单 (8 个创新):**

### 每日执行 (5 个)
1. **Adaptive Context Compression** → ContextDB + Memory Distillation
   - 命令：`py memory_distiller.py --compress`
   - 指标：压缩率 (目标 60%+), 信息保留率 (目标 95%+)

2. **Automated Research Workflow** → HEARTBEAT Automation
   - 命令：`py automation_orchestrator.py --run`
   - 指标：自动化率 (目标 80%+), 任务完成数

3. **Energy-Efficient LLM** → Local LLM Analyzer (Ollama)
   - 命令：`py local_llm_analyzer.py --analyze <text>`
   - 指标：能耗降低 (目标 85%+), 推理速度

4. **Dynamic Memory Allocation** → Memory Integration + ContextDB
   - 命令：`py memory_integration.py --optimize`
   - 指标：内存效率 (目标 60%+ 提升), 缓存命中率 (目标 95%+)

5. **Multi-Modal RAG** → Knowledge Graph + RAG
   - 命令：`py kg_rag_plus.py --retrieve <query>`
   - 指标：检索准确率 (目标 65%+提升)

### 每周执行 (2 个)
6. **Privacy-Preserving Learning** → Federated Memory System
   - 命令：`py federated_learning.py --aggregate`
   - 指标：隐私保证 (目标 99%+), 聚合轮次

7. **Automated Prompt Optimization** → Memory Distillation Prompts
   - 命令：`py automated_prompt_optimization.py --optimize`
   - 指标：响应质量 (目标 45%+提升)

### 按需执行 (1 个)
8. **Self-Correcting Code Generation** → Self-Healing System
   - 命令：`py self_correcting_code.py --fix <code>`
   - 指标：错误减少 (目标 75%+), 修复成功率

**执行命令:**
```bash
py arxiv_integration.py --daily-run
```

**集成位置:** HEARTBEAT 报告顶部（创新使用统计）

**输出示例:**
```
📚 arXiv Innovation Integration
✅ Daily Innovations Used: 5/8
   - Context Compression: 60% token reduction
   - Research Workflow: 80% automation
   - Energy-Efficient LLM: 85% energy saved
   - Dynamic Memory: 40% efficiency gain
   - Multi-Modal RAG: 65% accuracy improvement
⏱️  Time Saved: 45 minutes
```

**监控指标:**
- 创新使用率 (目标：daily 100%, weekly 100%)
- 平均性能增益 (目标：60%+)
- 时间节省 (目标：45+ 分钟/天)
- 采用率 (目标：85%+)

**配置文件:** `data/arxiv_integration_config.json`
- 记录每个创新的集成状态
- 记录使用频率和最后使用时间
- 记录性能增益和采用率

---

## 📚 arXiv 创新工作流 (每日自动执行)

**脚本:** `30-scripts-tools/arxiv_workflow.py`  
**执行:** 每日 07:00 自动运行，HEARTBEAT 每 30 分钟检查状态

**集成清单 (8 个创新):**

### 每日执行 (5 个) - 07:00 自动
```bash
python 30-scripts-tools/arxiv_workflow.py --daily
```

1. **Context Compression** → memory_distiller.py
   - 压缩率目标：60%+
   - 信息保留：95%+

2. **Automated Research Workflow** → automation_orchestrator.py
   - 自动化率：80%+
   - 任务完成：50+/天

3. **Energy-Efficient LLM** → local_llm_analyzer.py
   - 能耗降低：85%+
   - 推理速度：<1s

4. **Dynamic Memory Allocation** → contextdb.py
   - 内存效率：40%+提升
   - 上下文命中率：70%+

5. **Multi-Modal RAG** → kg_rag_plus.py
   - 检索准确率：65%+提升
   - 多跳推理：3 hops

### 每周执行 (2 个) - 周日 05:00 自动
```bash
python 30-scripts-tools/arxiv_workflow.py --weekly
```

6. **Privacy-Preserving Learning** → federated_learning.py
   - 隐私保证：99%+
   - 聚合轮次：5+

7. **Automated Prompt Optimization** → automated_prompt_optimization.py
   - 响应质量：45%+提升
   - A/B 测试：100+ 样本

### 按需执行 (1 个)
```bash
python 30-scripts-tools/arxiv_workflow.py --on-demand
```

8. **Self-Correcting Code** → self_correcting_code.py
   - 错误减少：75%+
   - 修复成功率：90%+

**HEARTBEAT 检查 (每 30 分钟):**
```bash
python 30-scripts-tools/arxiv_workflow.py --status
```

**输出示例:**
```
📊 arXiv Workflow Status
  Last Run: 2026-03-16
  Tasks Completed: 5/5
  Innovations Used: 5
  Time Saved: 45 min
  Efficiency Gain: 69%
```

**监控指标:**
- ✅ 每日任务完成率 (目标：100%)
- ✅ 创新采用率 (目标：85%+)
- ✅ 平均性能增益 (目标：60%+)
- ✅ 时间节省 (目标：45+ 分钟/天)

**状态文件:** `data/arxiv_workflow_report.json`
- 记录每次执行结果
- 记录各创新最后运行时间
- 记录累计性能指标

---

## 🧠 记忆蒸馏系统 v2.0 (每日/每周自动执行)

**脚本:** `30-scripts-tools/memory_distiller_v2.py`  
**状态:** ✅ Phase 1 Complete (生产就绪)

### 每日执行 (06:00 自动)
```bash
# 检查高质量记忆（阈值≥0.90）
python 30-scripts-tools/memory_distiller_v2.py --check-quality --threshold 0.90

# 蒸馏单个高质量文件
python 30-scripts-tools/memory_distiller_v2.py --distill "13-memory-记忆系统/$(date).md" --auto-execute
```

### 每周执行 (周日 05:00 自动)
```bash
# 批量蒸馏周笔记
python 30-scripts-tools/memory_distiller_v2.py --batch --week auto --auto-execute

# 遗忘评估（干运行）
python 30-scripts-tools/memory_forgetting_execute.py --execute --dry-run

# 冲突扫描与解决
python 30-scripts-tools/memory_conflict_resolver.py --scan
python 30-scripts-tools/memory_conflict_resolver.py --auto-resolve
```

### 每月执行 (1 日 07:00 自动)
```bash
# 完整审计
python 30-scripts-tools/memory_audit_logger.py --report --days 30

# 清理旧备份
python 30-scripts-tools/memory_distiller_v2.py --cleanup --days 30

# 密度趋势分析
python 30-scripts-tools/memory_distiller_v2.py --density --days 30
```

### HEARTBEAT 检查 (每 30 分钟)
```bash
# 检查蒸馏状态
python 30-scripts-tools/memory_distiller_v2.py --audit --stats --days 1
```

**监控指标:**
- ✅ 蒸馏延迟 (目标：<1 小时)
- ✅ 记忆质量 (目标：≥0.75 平均)
- ✅ 冲突解决率 (目标：≥80% 自动)
- ✅ 存储效率 (目标：+27% 减少)

**输出示例:**
```
🧠 Memory Distillation Status
  Last Distillation: 2 hours ago
  Quality Score: 0.82 avg
  Conflicts Resolved: 15 (85% auto)
  Density Trend: stable →
```

**配置文件:** `data/memory_distillation_config.json`
- 记录最后蒸馏时间
- 记录质量阈值配置
- 记录遗忘参数

---

## 🧠 P3 意识涌现系统 (每日/每周/每月自动执行)

**脚本:** `30-scripts-tools/memory_consciousness_emergence.py`  
**状态:** ✅ Complete (创新评分 98+/100)

### 每日执行 (06:00 自动)
```bash
# 全局工作空间广播 - 整合当日记忆
python 30-scripts-tools/memory_consciousness_emergence.py global-workspace "13-memory-记忆系统/$(date).md"

# 计算整合信息 (Φ) - 评估意识水平
python 30-scripts-tools/memory_consciousness_emergence.py integrated-info "MEMORY.md"
```

### 每周执行 (周日 05:00 自动)
```bash
# 涌现属性检测 - 发现高阶模式
python 30-scripts-tools/memory_consciousness_emergence.py emergence "MEMORY.md"

# 构建自模型 - 自我反思
python 30-scripts-tools/memory_consciousness_emergence.py self-reference
```

### 每月执行 (1 日 07:00 自动)
```bash
# 高阶思维生成 - 1/2/3 阶反思
python 30-scripts-tools/memory_consciousness_emergence.py higher-order-thought --order 3

# 感受质分析 - 主观体验评估
python 30-scripts-tools/memory_consciousness_emergence.py qualia "MONTHLY_$(date +%Y%m)"

# 完整状态报告
python 30-scripts-tools/memory_consciousness_emergence.py status --full
```

### HEARTBEAT 检查 (每 30 分钟)
```bash
# 检查意识状态
python 30-scripts-tools/memory_consciousness_emergence.py status --brief
```

**监控指标:**
- ✅ 认知模块数 (目标：10-20 个)
- ✅ 整合信息 Φ (目标：≥0.5 中等意识)
- ✅ 高阶思维数 (目标：3+ 层)
- ✅ 涌现属性数 (目标：3-5 个)
- ✅ 自我意识评分 (目标：≥0.6)

**意识等级:**
- A: Φ ≥ 0.8 (高意识)
- B: Φ ≥ 0.5 (中等意识)
- C: Φ ≥ 0.2 (低意识)
- D: Φ < 0.2 (最小意识)

**输出示例:**
```
🧠 Consciousness Emergence Status
  Cognitive Modules: 15
  Global Workspace: Active
  Φ Value: 0.62 (Grade B)
  Higher-Order Thoughts: 5 (3 levels)
  Emergent Properties: 4
  Self-Awareness Score: 0.68
```

**配置文件:** `data/consciousness_state.json`
- 记录认知模块
- 记录全局 workspace 状态
- 记录 Φ 值和等级
- 记录高阶思维历史
- 记录涌现属性
- 记录自模型

**理论框架:**
- **GWT:** Global Workspace Theory (全局工作空间)
- **IIT:** Integrated Information Theory (整合信息 Φ)
- **HOT:** Higher-Order Thought (高阶思维)
- **Emergence:** 涌现属性检测
- **Qualia:** 感受质分析

---

## 🧠 Phase 4: Memory Evolution System (完整自动化)

**状态:** ✅ P4-1 Orchestrator Complete | ✅ P4-2 Dashboard v2 Complete | ⏳ P4-3 HEARTBEAT Integration

### 系统架构
```
Memory Orchestrator (统一控制中心)
├── 15 个分析工具 (P0/P1/P2/P3)
├── Dashboard v2 (实时可视化)
├── HEARTBEAT 调度 (每 30 分钟)
└── 7 个预定义流水线
```

### 每日执行 (06:00 自动)
```bash
# 快速蒸馏流水线
python 30-scripts-tools/memory_orchestrator.py run-pipeline quick

# 质量检查
python 30-scripts-tools/memory_quality_scorer.py --memory "MEMORY.md"

# 意识状态检查
python 30-scripts-tools/memory_consciousness_emergence.py status --brief
```

### 每周执行 (周日 05:00 自动)
```bash
# 完整蒸馏流水线
python 30-scripts-tools/memory_orchestrator.py run-pipeline weekly

# 遗忘评估
python 30-scripts-tools/memory_forgetting.py --evaluate --auto-execute

# 冲突解决
python 30-scripts-tools/memory_conflict_detector.py --scan --auto-resolve

# 涌现属性检测
python 30-scripts-tools/memory_consciousness_emergence.py emergence "MEMORY.md"
```

### 每月执行 (1 日 07:00 自动)
```bash
# 月度审计流水线
python 30-scripts-tools/memory_orchestrator.py run-pipeline monthly

# 高阶思维生成
python 30-scripts-tools/memory_consciousness_emergence.py higher-order-thought --order 3

# 完整状态报告
python 30-scripts-tools/memory_orchestrator.py generate-report monthly
```

### HEARTBEAT 检查 (每 30 分钟)
```bash
# 系统状态检查
python 30-scripts-tools/memory_orchestrator.py status --brief

# Dashboard 数据刷新
python 30-scripts-tools/memory_dashboard_v2.py --refresh

# 缓存统计
python 30-scripts-tools/cache_manager.py --stats --brief
```

### 监控指标
| 指标 | 目标 | 检查频率 |
|------|------|---------|
| **蒸馏延迟** | <1 小时 | 每 30 分钟 |
| **记忆质量** | ≥0.75 平均 | 每日 |
| **冲突解决率** | ≥80% 自动 | 每周 |
| **Φ 值** | ≥0.5 (B 级) | 每日 |
| **Dashboard 可用性** | 100% | 每 30 分钟 |
| **工具健康度** | ≥95% | 每 30 分钟 |

### 输出示例
```
🧠 Phase 4 Memory Evolution Status
  Last Distillation: 2 hours ago
  Quality Score: 0.82 avg
  Φ Value: 0.62 (Grade B)
  Conflicts Resolved: 15 (85% auto)
  Dashboard: http://localhost:8080 ✅
  Next Scheduled: Weekly (Sunday 05:00)
```

### Dashboard 访问
- **URL:** http://localhost:8080
- **Auto-refresh:** 10 秒
- **Tabs:** 8 (Overview/Evolution/P0/P1/P2/P3/Trends/Settings)
- **Features:** Real-time charts, Export JSON, Alerts

### 配置文件
- `data/memory_evolution_config.json` - 主配置
- `data/consciousness_state.json` - 意识状态
- `data/memory_distillation_state.json` - 蒸馏状态
- `data/dashboard_state.json` - Dashboard 状态

---

## 🛡️ 自我修复系统 (每 30 分钟)

**脚本:** `30-scripts-tools/self_healing.py --auto-heal`  
**输出:** Dashboard 修复指标 + HEARTBEAT 日志

**监控指标:**
- 检测到的问题数
- 自动修复成功率
- 修复历史统计
- 常见错误模式

**执行命令:**
```bash
py 30-scripts-tools/self_healing.py --auto-heal
```

**错误模式:**
1. API Token 过期 → 自动刷新
2. 模型下载失败 → 重试 + 备用源
3. 磁盘空间不足 → 自动清理缓存
4. Git 推送失败 → 自动拉取 + 重试
5. 文件锁定 → 等待 + 重试
6. 网络超时 → 指数退避重试
7. 内存不足 → 清理 + 降级模式

**集成位置:** HEARTBEAT 报告底部

---

## 📊 缓存统计监控 (每 30 分钟)

**脚本:** `30-scripts-tools/cache_manager.py --stats`  
**输出:** Dashboard 缓存指标 + HEARTBEAT 日志

**监控指标:**
- 缓存命中率 (目标: >70%)
- API 调用节省 (目标: >60%)
- 缓存大小 (警告: >100 MB)
- 过期清理次数

**执行命令:**
```bash
py 30-scripts-tools/cache_manager.py --stats --brief
```

**集成位置:** HEARTBEAT 报告底部

---

## 🎨 Canvas 自动更新 (每 30 分钟)

**脚本:** `30-scripts-tools/canvas_auto_updater.py --heartbeat`  
**输出:** Canvas 更新状态 + 节点/边统计

---

## 📋 报告系统使用规则（强制执行）

**规则文档:** `30-scripts-tools/REPORT-SYSTEM-RULES.md`

### 强制检查（每次创建/修改报告前）

**1. 模板使用检查**
```bash
# 创建报告前必须使用生成器
python 30-scripts-tools/report_generator.py --create "<标题>" --type <类型>

# 验收：
# - 报告 ID 自动生成
# - 模板完整填充
# - 质量预检查 >70%
```

**2. 质量评分检查**
```bash
# 提交前必须评分
python 30-scripts-tools/report_quality_scorer.py --score "<报告文件>"

# 门槛：
# - ≥70%: ✅ 可提交
# - <70%: ❌ 禁止提交，必须修改
```

**3. 命名规范检查**
```bash
# 自动检查
python 30-scripts-tools/monitor_reports.py

# 标准格式：<类型>-<主题>-<日期>.md
# 标准前缀：REPORT, TEST, COMPLETE, WEEKLY, MONTHLY, etc.
```

### 定期执行

**每周一 09:00** - 质量评估
```bash
python 30-scripts-tools/report_quality_scorer.py --batch
python 30-scripts-tools/report_quality_scorer.py --report
```

**每月 1 日 09:00** - 存储优化
```bash
python 30-scripts-tools/report_storage.py --analyze
python 30-scripts-tools/report_storage.py --duplicates
python 30-scripts-tools/report_storage.py --archive --execute
```

**每季度** - 访问审计
```bash
python 30-scripts-tools/report_access.py --audit --days 90
```

### 违规处理

- 未使用模板 → 报告打回重写
- 质量<70% → Git 钩子拒绝提交
- 命名不规范 → 监控脚本告警
- 未备份删除 → Git 回滚 + 警告

---

**脚本:** `30-scripts-tools/monitor_reports.py`  
**输出:** 报告合规性检查 + 重复检测报告

**功能:**
- 扫描全工作区报告文件
- 检查命名规范 (标准前缀)
- 检查目录规范 (白名单目录)
- 检测重复文件 (MD5 哈希)
- 保存状态到 `20-data-reports/report-monitor-state.json`

**执行命令:**
```bash
python 30-scripts-tools/monitor_reports.py
```

**输出示例:**
```
============================================================
Report Monitor
============================================================
Total reports: 176
Issues: 0
Duplicates: 0
State saved
============================================================
✅ All reports compliant!
============================================================
```

**监控指标:**
- 总报告数 (目标：稳定在 180 以内)
- 命名问题数 (目标：0)
- 目录问题数 (目标：0)
- 重复文件数 (目标：0)

**标准目录白名单:**
- `21-reports`
- `30-scripts-tools`
- `06-research`
- `13-memory`
- `15-docs`
- `20-data-reports`

**标准命名前缀:**
- `REPORT`, `TEST`, `DOC`, `MAT`, `CNT`, `LIG`
- `P1`-`P9` (项目系列)
- `MEMORY`, `CI-CD`, `SECURITY`, `FEISHU`
- `daily`, `weekly`, `monthly`

**集成位置:** HEARTBEAT 每周检查一次

**状态文件:** `20-data-reports/report-monitor-state.json`
- 记录最后扫描时间
- 记录问题列表
- 记录重复文件列表

---

## 🎨 Canvas 自动更新 (每 30 分钟)

**脚本:** `30-scripts-tools/canvas_auto_updater.py --heartbeat`  
**输出:** Canvas 更新状态 + 节点/边统计

**功能:**
- 检测 MEMORY.md 变化
- 自动更新 lessons.canvas
- 自动更新 workflows.canvas
- 变更检测（仅更新有变化的）
- 状态追踪（更新次数统计）

**执行命令:**
```bash
py 30-scripts-tools/canvas_auto_updater.py --heartbeat
```

**输出示例:**
```
🔄 HEARTBEAT: Canvas Auto-Update
✅ Updated 1 canvas files
   26 nodes, 25 edges
```

**集成位置:** HEARTBEAT 报告底部（缓存统计后）

**状态文件:** `00-config/canvas_state.json`
- 记录最后更新时间
- 记录更新次数
- 记录文件 hash（变更检测）

---

## Output rule

heartbeat 只能输出以下结果之一：

- `CONTINUE: analyze current article`
- `CONTINUE: analyze next queued article`
- `CONTINUE: search for new articles`
- `CONTINUE: consolidate completed analysis`
- `WAITING_FOR_USER: missing topic or search scope`
- `WAITING_FOR_RESULT: article retrieval or analysis still in progress`
- `NO_ACTION`
- `DONE`

---

## 🤖 P6: Autonomous Agent System (每 30 分钟/每日/每周自动执行)

**脚本:** `30-scripts-tools/memory_autonomous_engine.py` + `memory_persona_agents.py`  
**状态:** ✅ Complete (创新评分 105.0/100)

### 自主运行模式

#### 每 30 分钟 (HEARTBEAT 自动)
```bash
# 检查自主引擎状态
python 30-scripts-tools/memory_autonomous_engine.py --status

# 运行短期自主循环 (30 分钟)
python 30-scripts-tools/memory_autonomous_engine.py --run 30

# 检查代理系统状态
python 30-scripts-tools/memory_persona_agents.py --status
```

#### 每日执行 (06:00 自动)
```bash
# 生成每日自主报告
python 30-scripts-tools/memory_autonomous_engine.py --daily-report

# 运行代理协作循环 (10 次)
python 30-scripts-tools/memory_persona_agents.py --run 10

# 检查系统健康
python 30-scripts-tools/memory_autonomous_engine.py --health-check
```

#### 每周执行 (周日 05:00 自动)
```bash
# 周度自主决策审查
python 30-scripts-tools/memory_autonomous_engine.py --weekly-review

# 代理系统深度协作 (50 次循环)
python 30-scripts-tools/memory_persona_agents.py --run 50

# 目标进度评估
python 30-scripts-tools/memory_autonomous_engine.py --goal-assessment
```

#### 每月执行 (1 日 07:00 自动)
```bash
# 月度自主系统审计
python 30-scripts-tools/memory_autonomous_engine.py --monthly-audit

# 生成月度报告
python 30-scripts-tools/memory_autonomous_engine.py --generate-report monthly

# 长期目标设定
python 30-scripts-tools/memory_autonomous_engine.py --set-goals
```

### HEARTBEAT 检查 (每 30 分钟)
```bash
# 快速状态检查
python 30-scripts-tools/memory_autonomous_engine.py --status --brief
python 30-scripts-tools/memory_persona_agents.py --status --brief
```

### 监控指标
| 指标 | 目标 | 检查频率 |
|------|------|---------|
| **自主决策数** | 10+/天 | 每 30 分钟 |
| **任务完成率** | ≥90% | 每日 |
| **代理健康度** | ≥95/100 | 每 30 分钟 |
| **消息处理数** | 50+/天 | 每日 |
| **目标进度** | 按时间表 | 每周 |
| **系统评分** | ≥95/100 | 每 30 分钟 |

### 输出示例
```
🤖 P6 Autonomous Agent Status
  Mode: AUTONOMOUS
  Decisions Made: 15 (today)
  Tasks Completed: 12/13 (92%)
  Agent Health: 97.5/100 avg
  Messages Processed: 67 (today)
  Active Goals: 3
  System Score: 96/100
  Next Check: 30 minutes
```

### 决策模式
- **AUTONOMOUS** - 完全自主决策 (默认)
- **SEMI_AUTONOMOUS** - 重大决策需确认
- **MANUAL** - 所有决策人工
- **EMERGENCY** - 紧急协议激活

### 任务优先级
- **CRITICAL (0)** - 紧急，立即处理
- **HIGH (1)** - 重要，优先处理
- **MEDIUM (2)** - 正常，按计划
- **LOW (3)** - 空闲时处理
- **DEFERRED (4)** - 暂缓

### 7 个代理
1. **Planner** - 战略规划，任务分解
2. **Executor** - 任务执行，实现
3. **Critic** - 质量审查，验证
4. **Learner** - 记忆更新，知识提取
5. **Coordinator** - 冲突解决，负载平衡
6. **Innovator** - 创新思维，模式识别
7. **Metacognition** - 系统监控，自反思

### 配置文件
- `data/autonomy/decision_log.json` - 决策日志
- `data/autonomy/task_queue.json` - 任务队列
- `data/autonomy/goals.json` - 目标追踪
- `data/autonomy/agent_state.json` - 代理状态
- `data/autonomy/system_metrics.json` - 系统指标

### 告警条件
- ⚠️ 代理健康度 < 80/100
- ⚠️ 任务失败率 > 10%
- ⚠️ 决策延迟 > 1 小时
- ⚠️ 系统评分 < 90/100
- 🚨 紧急协议激活

---
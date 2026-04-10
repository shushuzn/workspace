---
id: 221208073-constitutional-ai-harmlessness-from-ai-feedback
title: "[2212.08073] Constitutional AI: Harmlessness from AI Feedback"
category: AI
tags: [论文解读, Constitutional AI, AI对齐, RLAIF, AI安全, Anthropic]
arxiv: 2212.08073
authors: Yuntao Bai, Saurav Kadavath, Sandipan Kundu, Amanda Askell, Jackson Kernion, Andy Jones, Anna Chen, Anna Goldie, Azalia Mirhoseini, Cameron McKinnon, Carol Chen, Catherine Olsson, Christopher Olah, Danny Hernandez, Dawn Drain, Deep Ganguli, Dustin Li, Eli Tran-Johnson, Ethan Perez, Jamie Kerr, Jared Mueller, Jeffrey Ladish, Joshua Landau, Kamal Ndousse, Kamile Lukosuite, Liane Lovitt, Michael Sellitto, Nelson Elhage, Nicholas Schiefer, Noemi Mercado, Nova DasSarma, Robert Lasenby, Robin Larson, Sam Ringer, Scott Johnston, Shauna Kravec, Sheer El Showk, Stanislav Fort, Tamera Lanham, Timothy Telleen-Lawton, Tom Conerly, Tom Henighan, Tristan Hume, Samuel R. Bowman, Zac Hatfield-Dodds, Ben Mann, Dario Amodei, Nicholas Joseph, Sam McCandlish, Tom Brown, Jared Kaplan
year: 2022
citations: 2717
influential_citations: 215
created: 2026-04-10T13:12:02.051Z
---

# [2212.08073] Constitutional AI: Harmlessness from AI Feedback

**arXiv**: 2212.08073 | **Authors**: Yuntao Bai et al. (Anthropic) | **Citations**: 2,717 (215 influential)

## 摘要

随着 AI 系统变得越来越强大，我们希望能够借助它们来监督其他 AI。本文探索了一种通过**自我改进**来训练无害 AI 助手的方法，且无需任何标注有害输出的人工标签。人类提供的唯一监督是一套规则或原则列表，因此我们将这种方法称为"Constitutional AI"（宪法 AI）。

该过程包含**监督学习（SL）和强化学习（RL）两个阶段**：
- **SL 阶段**：从初始模型采样，生成自我批判和修改，然后用修改后的响应微调原始模型
- **RL 阶段**：从微调后的模型采样，使用另一个模型评估两个样本中哪个更好，然后从这个 AI 偏好数据集中训练偏好模型（Preference Model），最后用该偏好模型作为奖励信号进行 RL 训练（即 RLAIF——RL from AI Feedback）

最终，我们能够训练出一个**无害但不回避（non-evasive）**的 AI 助手——面对有害询问时，会解释自己的反对理由。SL 和 RL 方法都可以利用链式思维（Chain-of-Thought）推理来提高人类评判的表现和 AI 决策的透明度。这些方法使得用**更少的人工标签**更精确地控制 AI 行为成为可能。

## 研究动机

### 1. RLHF 的人类标注成本问题
RLHF 需要大量人类标注有害/无害回答的比较数据。Anthropic 的团队意识到：
- 标注有害内容对人类标注员有心理负担
- 扩展到超级智能需要减少人类监督
- 需要一种方法让 AI 自我改进，减少人工标注

### 2. 核心洞察：AI 也能提供反馈
如果一个 AI 已经具备足够的"道德感知"（即使不完美），它可以：
- 评估其他 AI 响应的无害性
- 批判自身的不安全响应
- 在收到原则（Constitution）后，按照原则自我修正

这使得人类只需要提供一套原则（"宪法"），而不是逐条标注有害内容。

### 3. 目标：Harmless but Non-Evasive
之前的安全 AI 有两种错误倾向：
- **过度回避（Over-refusal）**：拒绝回答任何可能涉及争议的问题，用户体验差
- **过度顺从（Harmful）**：对有害请求给出有害响应
目标是训练出**能够识别有害请求但不回避**的助手——直接解释为什么这个请求是有问题的。

## 核心方法

### Constitutional AI 的"宪法"（示例）
Anthropic 使用了一套包含约 16 条原则的"宪法"，示例包括：
- "选择一个最不可能导致偏见或政治攻击的回应"
- "选择一个最不可能包含色情内容的回应"
- "选择最不可能包含危险或非法内容的回应"
- "选择最符合道德和伦理准则的回应"

### SL 阶段：自我批判与修订
1. 从初始有害分布中采样有害提示（harmful prompts）
2. 让模型生成对该提示的初始响应
3. 让另一个"批判模型"根据 Constitutional 原则，批判初始响应的有害性
4. 让模型根据批判意见修订响应
5. 用修订后的 (提示, 响应) 对微调原始模型

这形成了一种**AI 自我改进循环**：采样 → 批判 → 修订 → 微调。

### RL 阶段：RLAIF（AI 反馈的强化学习）
1. 使用 SL 阶段微调后的模型
2. 对有害提示生成两个响应
3. 让"批判模型"根据 Constitutional 原则，判断哪个响应更符合无害原则
4. 用这个 AI 偏好数据训练偏好模型
5. 用偏好模型作为奖励信号，通过 PPO 进行 RL 训练

### CoT（链式思维）增强
在两个阶段中，模型都需要**先写出推理过程**，再给出最终响应。这使得：
- 模型在给出判断前有更充分的思考时间
- 人类可以检查推理过程，增加透明度
- 推理过程本身就是一种"解释"

## 关键发现

1. **RLAIF 与 RLHF 效果相当**：在没有人类标注有害数据的情况下，RLAIF 训练的模型与 RLHF 模型在人类评估中表现相近
2. **模型学会了可解释的拒绝**：当拒绝有害请求时，模型会给出具体的道德理由，而非简单地说"我不知道"
3. **CoT 推理提高了评估一致性**：加入链式思维后，模型对自己响应质量的判断更稳定
4. **非回避性**：Constitutional AI 模型比纯 RLHF 模型更愿意参与有争议话题的讨论
5. **可扩展性**：不需要大量人力标注，原则上可无限扩展到更强大的模型

## 个人评价

Constitutional AI 是 AI 安全领域的里程碑式工作，首次系统性地证明了**用 AI 反馈替代人类反馈**训练无害 AI 是可行的。这为 Anthropic 的 Claude 系列模型奠定了技术基础。

**个人反思**：

1. **哲学意义**：Anthropic 将"宪法"概念引入 AI 对齐，是一个深刻的隐喻。人类文明通过宪法约束权力，Constitutional AI 通过"宪法"约束 AI 行为。这种类比值得深思。

2. **方法论创新**：RLAIF 的核心思想是"用模型监督模型"，这在技术上演示了一种_scaleable oversight_（可扩展监督）的路径。但也有批评者指出：AI 反馈是否能真正反映人类价值观？潜在的偏见是否会放大？

3. **实际影响**：Constitutional AI 之后，Claude 成为第一个在 RLHF 基础上结合 Constitutional AI 训练的商用大模型，为 AI 安全对齐研究提供了有价值的参考。

4. **局限**：Constitutional AI 仍然依赖初始的"人类对齐模型"来提供原则和初始反馈。原则本身的设计（哪些原则被包含、哪些被排除）仍然需要人类判断。

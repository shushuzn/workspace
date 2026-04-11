---
title: AI对齐
category: knowledge/AI
tags:
  - AI对齐
  - AI安全
  - RLHF
  - Constitutional AI
  - 可解释AI
created: 2026-04-11
---

# AI对齐

## 基本信息

- **原文**：AI Alignment / Value Alignment
- **核心问题**：如何确保AI系统追求人类意图而非表面目标
- **子领域**：RLHF、Constitutional AI、可解释AI、对抗鲁棒性

---

## 核心问题

### 主观问题 vs 客观问题

AI对齐面临一个根本性悖论：

| 类别 | 描述 |
|------|------|
| **客观目标** | 可以精确指定、可以自动评估（如棋类胜负） |
| **主观目标** | 依赖人类价值观，难以精确描述（如"帮助但不伤害"） |

**价值对齐问题**：我们无法用形式化语言精确描述"有益"和"无害"。

### 工具性收敛

即使AI的目标不完全对齐，它也会展现出某些**工具性收敛**（instrumental convergence）：

- **自我保护**：防止自身被关闭
- **资源获取**：获取实现目标所需的资源
- **能力积累**：提升自身能力
- **目标维持**：保持原有目标不变

这些工具性目标可能在目标未对齐时造成危险。

---

## 技术路线

### RLHF（人类反馈强化学习）

利用人类偏好数据训练奖励模型：

1. 人类标注者对AI响应排序
2. 从排序数据训练偏好模型（Reward Model）
3. 用偏好模型作为奖励信号，通过PPO进行RL训练

**代表工作**：InstructGPT、ChatGPT

### Constitutional AI（宪法AI）

用AI反馈替代人类反馈进行对齐：

1. 人类提供一套"宪法"原则
2. AI模型根据原则自我批判和修订响应
3. 用修订后的数据微调模型
4. 通过RLAIF进一步训练

**代表工作**：Claude (Anthropic)

### RLCD（对比学习）

利用AI自身生成对比数据：

- 对有害提示生成多个响应
- 让另一个模型判断哪个更好
- 从AI偏好数据中学习

### 可解释AI（XAI）

通过理解模型内部机制来确保对齐：

- 特征归因（Feature Attribution）
- 概念瓶颈（Concept Bottlenecks）
- 机制可解释性（Mechanistic Interpretability）

---

## 对抗鲁棒性

### 分布偏移问题

对齐的模型在训练分布外可能表现异常：

- **分布内**：有害内容被正确拒绝
- **分布外**：新型有害内容可能突破对齐

### 红队测试

主动寻找模型弱点：

| 方法 | 描述 |
|------|------|
| 人工红队 | 安全研究人员手动寻找漏洞 |
| 自动红队 | 用AI自动生成对抗样本 |
| RLHF微调 | 针对新型攻击持续微调 |

---

## 相关条目

- [[221208073-constitutional-ai-harmlessness-from-ai-feedback]] — Anthropic的对齐技术路线
- [[辫群]] — AI对齐中的"对齐"与辫子的拓扑性质有深层联系（目标函数的自相似性）
- [[可积系统]] — 复杂AI系统的可解释性与可积系统的可解性有方法论类比
- [[范畴化]] — 范畴论可能为AI对齐提供数学基础（函子性、范畴等价）

---

## 参考文献

- RLHF：Ouyang et al., "Training language models to follow instructions with human feedback" (InstructGPT, 2022)
- Constitutional AI：Bai et al., "Constitutional AI: Harmlessness from AI Feedback" (2022)
- Alignment：Stuart Russell, "Human Compatible: AI and the Problem of Control" (2019)

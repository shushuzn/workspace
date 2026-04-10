---
id: 200514165-language-models-are-few-shot-learners
title: "[2005.14165] Language Models are Few-Shot Learners"
category: AI
tags: [论文解读, GPT-3, 大语言模型, In-Context Learning, 少样本学习]
arxiv: 2005.14165
authors: Tom B. Brown, Benjamin Mann, Nick Ryder, Melanie Subbiah, Jared Kaplan, Prafulla Dhariwal, Arvind Neelakantan, Pranav Shyam, Girish Sastry, Amanda Askell, Sandhini Agarwal, Ariel Herbert-Voss, Gretchen Krueger, Tom Henighan, Rewon Child, Aditya Ramesh, Daniel M. Ziegler, Jeffrey Wu, Clemens Winter, Christopher Hesse, Mark Chen, Eric Sigler, Mateusz Litwin, Scott Gray, Benjamin Chess, Jack Clark, Christopher Berner, Sam McCandlish, Alec Radford, Ilya Sutskever, Dario Amodei
year: 2020
references:
  - "Brown et al., GPT-3, 2020"
cross-references:
  - "[[170603762-attention-is-all-you-need]]"
  - "[[181004805-bert-pre-training-of-deep-bidirectional-transformers-for-language-understanding]]"
  - "[[200901325-learning-to-summarize-from-human-feedback]]"
created: 2026-04-10T13:11:56.171Z
---

# [2005.14165] Language Models are Few-Shot Learners

**arXiv**: 2005.14165 | **Authors**: Tom B. Brown et al. (OpenAI) | **Parameters**: 175B | **Citations**: ~20,000+ (estimated)

## 摘要

近期的工作通过在大规模文本语料上预训练后进行任务特定微调，在多项 NLP 任务和基准上取得了显著提升。但这种方法虽然架构上是任务无关的，仍需要数千到数万条任务特定的微调数据。相比之下，人类通常只需要几个例子或简单指令就能执行新的语言任务——这是当前 NLP 系统难以做到的。本文展示了**扩展语言模型规模**可以大幅提升任务无关的少样本（Few-Shot）性能，有时甚至能与当时的微调最佳方法竞争。

具体来说，我们训练了 GPT-3，一个拥有 **1750亿参数**的自回归语言模型（是此前任何非稀疏语言模型的10倍），并在少样本设置下测试其性能。对于所有任务，GPT-3 在不进行任何梯度更新或微调的情况下运行，任务和少样本演示完全通过纯文本交互指定。GPT-3 在多项 NLP 数据集上取得了强劲表现，包括翻译、问答、完形填空任务，以及需要即时推理或领域适应的任务（如单词乱序还原、在句子中使用新词、执行3位数算术）。同时，我们也识别出一些 GPT-3 少样本学习仍然困难的数据集，以及一些与大规模网页语料训练相关的 方法论问题。最后，我们发现人类评估者难以区分 GPT-3 生成的新闻文章样本与人类撰写的文章。

## 研究动机

### 1. 微调的局限性
GPT-1/GPT-2/BERT 确立的"预训练+微调"范式虽然成功，但存在根本缺陷：
- 每个新任务都需要大量标注数据（如情感分析需要数万条标注）
- 每个任务都需要存储和部署单独的微调模型
- 无法快速适应新任务——需要重新训练

### 2. 人类智能的启示
人类可以：
- 从**几个例子**中学习新任务（Few-Shot）
- 仅凭**简单指令**执行从未见过的任务（Zero-Shot）
- 组合已有知识**即时推理**新问题

### 3. 核心假设
OpenAI 团队提出大胆假设：**如果语言模型足够大，并且在大规模多样化文本上训练，它应该能够从少样本演示中推断任务——无需任何参数更新**。这就是"情境学习"（In-Context Learning）的核心思想。

## 核心方法

### 1. 模型规模：1750亿参数
GPT-3 是当时最大的语言模型：
| 模型 | 参数规模 |
|------|---------|
| BERT-Large | 340M |
| GPT-2 | 1.5B |
| Turing NLG | 17B |
| **GPT-3** | **175B** |

训练 GPT-3 需要约 3640 Petaflop/s-day 计算量（是 GPT-2 的 2000 倍）。

### 2. 训练数据
使用了多个大规模文本语料：
- Common Crawl（4100 亿 token，筛选后约 570B）
- WebText2（190 亿 token）
- Books1（120 亿 token）
- Books2（550 亿 token）
- Wikipedia（30 亿 token）

总训练 token 约 **3000 亿**。

### 3. In-Context Learning（情境学习）
GPT-3 在推理时不进行任何梯度更新，而是通过**在输入中提供少量示例**让模型推断任务：
```
Input:
This is great! -> positive
This is bad! -> negative
I love this movie -> [model predicts positive]
```
关键：模型参数保持冻结，任务知识完全来自情境中的示例。

### 4. Zero/Few/One-Shot 设置
- **Zero-Shot**：只提供任务描述，无示例
- **One-Shot**：提供一个示例
- **Few-Shot**：提供 k 个示例（通常 k=10-100）

### 5. 模型系列
除了 175B 主模型，还训练了多个小规模变体用于对比研究：125M, 350M, 760M, 1.3B, 2.7B, 6.7B, 13B, 175B。

## 关键发现

1. **规模定律（Scaling Law）**：性能随模型规模、数据规模、计算量的增加而平滑提升，没有出现"平台期"
2. **情境学习有效性**：在多个任务上，仅凭 10-100 个示例就能接近或达到 SOTA 微调水平
3. **突破性任务表现**：
   - 翻译（Zero-Shot 可比肩专业翻译系统）
   - 3位数算术（从未在训练语料中见过）
   - 单词去乱序（GPT-3 可以学习推理）
   - 新闻文章生成（人类无法区分）
4. **GPT-3 的局限**：
   - 在复杂推理任务（数学应用题）上仍有明显差距
   - 容易产生"幻觉"和偏见
   - 对罕见知识或小众领域理解不足
5. **社会影响**：论文首次大规模讨论了大模型的社会风险（虚假信息、偏见、权力集中）

## 个人评价

GPT-3 是大语言模型时代的真正起点。这篇论文的意义不仅是技术突破，更是**证明了"规模"本身就是一种能力**——当模型足够大、训练数据足够多样时，少样本学习和零样本任务迁移能力会自发涌现，无需任何任务特定设计。

**个人反思**：
- 论文揭示了一个深刻洞察：**情境学习（In-Context Learning）不是某种特殊技术，而是大力出奇迹的自然结果**
- GPT-3 的成功催生了 AI 领域对"涌现能力"（Emergent Abilities）的研究热潮
- 但 GPT-3 的缺陷（幻觉、偏见、推理能力弱）也预示了后来 RLHF、Constitutional AI 等对齐研究的必要性
- 从 GPT-3 到 ChatGPT 只隔了一个 RLHF——这使得 GPT-3 的影响力被进一步放大

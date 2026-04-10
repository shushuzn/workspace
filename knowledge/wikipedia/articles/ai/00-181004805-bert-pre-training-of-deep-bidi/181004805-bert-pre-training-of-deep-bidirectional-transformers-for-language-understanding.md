---
id: 181004805-bert-pre-training-of-deep-bidirectional-transformers-for-language-understanding
title: "[1810.04805] BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding"
category: AI
tags: [论文解读, BERT, Transformer, NLP, 预训练]
arxiv: 1810.04805
authors: Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova
year: 2018
references:
  - "Devlin et al., BERT, 2018"
cross-references:
  - "[[170603762-attention-is-all-you-need]]"
  - "[[200514165-language-models-are-few-shot-learners]]"
created: 2026-04-10T13:10:10.813Z
---

# [1810.04805] BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding

**arXiv**: 1810.04805 | **Authors**: Jacob Devlin, Ming-Wei Chang, Kenton Lee, Kristina Toutanova (Google AI Language) | **Citations**: ~96,000+ (estimated)

## 摘要

BERT（Bidirectional Encoder Representations from Transformers）是一种新的语言表示模型。与近期的语言表示模型不同，BERT 设计为从无标注文本中预训练深度双向表示，通过联合 conditioning 左和右上下文来实现（不是像 GPT 那样从左到右单向，也不是像 ELMo 那样简单拼接两个单向模型）。预训练的 BERT 模型只需添加一个额外的输出层，无需对任务特定的架构进行大幅修改，即可为问答、语言推理等广泛任务创建最先进模型。BERT 在 11 项 NLP 任务上取得了新的最先进结果，包括 GLUE 分数提升至 80.5%（绝对提升 7.7%）、MultiNLI 准确率提升至 86.7%（绝对提升 4.6%）、SQuAD v1.1 问答 F1 提升至 93.2（绝对提升 1.5 分）、SQuAD v2.0 F1 提升至 83.1（绝对提升 5.1 分）。

## 研究动机

### 1. 预训练模型的历史缺陷
- **GPT（单向）**：采用 Left-to-Right Transformer Decoder，只看左侧上下文，限制了可以学习的信息类型
- **ELMo（双向 LSTM 拼接）**：使用两个独立训练的单向模型，简单拼接，不是真正的双向联合训练
- **传统方法**：每个 NLP 任务都需要从零训练，数据稀缺

### 2. 关键洞察
BERT 团队提出的关键问题是：**能否同时利用好左上下文和右上下文，创建真正双向联合训练的深度表示？**

这是一个看似简单但极其重要的创新——深度双向性意味着模型在每一层都能同时看到"之前发生了什么"和"之后会发生什么"，从而学习更丰富的语义表示。

## 核心方法

### 1. 预训练任务：Masked Language Model（MLM）
随机遮盖输入中 15% 的 token，用 [MASK] 标记替代。预训练目标是预测被遮盖的词：
```
Input: The man [MASK] to the store
Target: went
```
MLM 允许深度双向表示的学习，因为遮盖词可以从左右两侧上下文推断。

### 2. 预训练任务：Next Sentence Prediction（NSP）
训练数据：50% 是真正的下一句，50% 是随机句子。判断 B 是否是 A 的下一句：
```
A: The man went to the store
B: He bought milk    → IsNext (正样本)
A: The man went to the store
B: Penguins are birds → NotNext (负样本)
```
NSP 让 BERT 学习句子间关系，对问答、自然语言推理等任务至关重要。

### 3. 模型架构
- **BERT-Base**：12 层 Transformer Encoder，隐层 768 维，12 注意力头，110M 参数
- **BERT-Large**：24 层 Transformer Encoder，隐层 1024 维，16 注意力头，340M 参数

### 4. 微调策略
预训练完成后，只需在模型顶部添加一个任务特定的输出层，所有参数在下游任务上联合微调。由于注意力机制允许模型根据特定任务灵活对齐输入和输出，因此架构改动极小。

### 5. 输入表示
Tokenization 使用 WordPiece（类似 BPE），每句开头添加 [CLS]，句子对用 [SEP] 分隔：
```
[CLS] The man went to the store [SEP] He bought milk [SEP]
```

## 关键发现

1. **11 项 SOTA**：BERT 在 GLUE（9项任务）、SQuAD v1.1/v2.0、SQuAD 全部刷新记录
2. **数据规模**：预训练语料 BooksCorpus（800M 词）+ English Wikipedia（2,500M 词）
3. **BERT-Large 的突破性**：在 SQuAD 上是首个超越人类表现的模型
4. **双向性的力量**：MLM 比 LTR（左到右）预训练更能学习上下文表示，在所有任务上均优于单向模型
5. **知识迁移的普适性**：不同任务的微调都有效，且模型同时学到了丰富的语言知识

## 个人评价

BERT 是 NLP 领域"预训练+微调"范式的标志性工作。它的伟大之处在于**简洁**：没有复杂的任务定制，只是改变了预训练目标（MLM + NSP），就解锁了 Transformer Encoder 的全部潜力。

**历史意义**：
- BERT 之后，NLP 领域几乎所有任务都开始采用"预训练语言模型 + 微调"范式
- 它开创了"大模型"时代的序幕——BERT-Large（340M）到 GPT-3（175B）再到 GPT-4/LLaMA/Claude，模型规模越来越大
- GLUE 基准在 BERT 出现后迅速被超越，导致研究者需要创建 SuperGLUE 来继续推进

**个人反思**：BERT 的成功揭示了一个深刻规律——**语言理解需要双向语境建模**。GPT 系列的单向限制在 GPT-2/3/4 中通过海量数据和巨大规模得到了一定弥补，但双向性始终是 BERT 系模型的优势。这促成了 RoBERTa、ALBERT、ELECTRA 等大量 BERT 变体的诞生。

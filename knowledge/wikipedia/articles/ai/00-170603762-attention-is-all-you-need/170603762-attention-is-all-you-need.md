---
id: 170603762-attention-is-all-you-need
title: "[1706.03762] Attention Is All You Need"
category: AI
tags: [论文解读, Transformer, 深度学习, NLP, 注意力机制]
arxiv: 1706.03762
authors: Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin
year: 2017
citations: 172323
influential_citations: 19585
created: 2026-04-10T13:11:57.771Z
---

# [1706.03762] Attention Is All You Need

**arXiv**: 1706.03762 | **Authors**: Ashish Vaswani, Noam Shazeer, et al. (Google Brain/Research) | **Citations**: 172,323 (19,585 influential)

## 摘要

当时主流的序列转导模型基于复杂的循环神经网络（RNN/LSTM/GRU）或卷积神经网络（CNN），配置为 Encoder-Decoder 架构。表现最好的模型还通过注意力机制连接 Encoder 和 Decoder。Transformer 提出了一种全新的简单网络架构——完全基于注意力机制，彻底摒弃了循环和卷积操作。在两个机器翻译任务上的实验表明，这些模型不仅质量更高，而且更具可并行化性，训练时间也显著缩短。Transformer 在 WMT 2014 英德翻译任务上达到了 28.4 BLEU，比包括集成模型在内的已有最佳结果高出 2 BLEU 以上。在 WMT 2014 英法翻译任务上，模型在 8 块 GPU 上训练 3.5 天后，建立了新的单模型最高 BLEU 分数 41.8，训练成本仅为文献中最佳模型的很小一部分。实验还证明 Transformer 能很好地泛化到其他任务——在数据量大和数据量有限的两种条件下，均成功应用于英语成分句法分析任务。

## 研究动机

### 1. RNN 的根本缺陷
循环神经网络存在两个核心问题：
- **顺序计算本质**：必须逐token处理，无法并行，限制了长序列的训练效率
- **长期依赖问题**：信息在序列中传播路径过长，梯度消失/爆炸使得学习远距离依赖困难

### 2. CNN 的局限性
卷积神经网络虽然可以并行计算，但：
- 捕获长距离依赖需要多层堆叠（如 ResNet 需要 30+ 层才能捕获大范围关联）
- 感受野有限，增加卷积核大小会大幅增加计算复杂度

### 3. 注意力机制的兴起
注意力机制（Bahdanau et al., 2014）允许序列中任意位置直接交互，但此前一直与 RNN 配合使用。Google 的研究团队问了一个关键问题：**能不能完全抛弃 RNN 和 CNN，只用注意力机制？**

这个问题意义重大：如果成功，不仅能解决并行化问题，还能让序列中任意两点之间的依赖关系学习复杂度降为 O(1)。

## 核心方法

### Transformer 架构
Transformer 采用了 **Encoder-Decoder** 结构，但完全使用 Self-Attention 和 Cross-Attention 替代了 RNN/LSTM/Conv：

```
Encoder: Input → [Self-Attention + Feed-Forward] × N → Encoder Output
Decoder: Output → [Masked Self-Attention + Cross-Attention + Feed-Forward] × N → Output
```

### 1. Scaled Dot-Product Attention
```
Attention(Q, K, V) = softmax(QK^T / √d_k) V
```
- Q（Query）、K（Keys）、V（Values）来自同一输入的线性变换
- 除以 √d_k 防止点积值过大导致 softmax 梯度消失
- 矩阵形式可一次计算所有位置的注意力权重

### 2. Multi-Head Attention（MHA）
将 Q/K/V 投影到 h 个不同的子空间（每个子空间维度 d_k/h），并行计算注意力后拼接：
```
MultiHead(Q,K,V) = Concat(head_1,...,head_h) W^O
where head_i = Attention(QW_i^Q, KW_i^K, VW_i^V)
```
- 论文使用 h=8 个头，每个头维度 64
- 多头允许模型在不同的表示子空间关注不同类型的信息（如语法关系、语义关联、指代消解）

### 3. 位置编码（Positional Encoding）
由于 Transformer 没有循环或卷积结构，无法自然获取序列位置信息。论文使用正弦/余弦函数编码位置：
```
PE(pos, 2i) = sin(pos / 10000^(2i/d_model))
PE(pos, 2i+1) = cos(pos / 10000^(2i/d_model))
```
这一选择使得模型可以学习相对位置关系（因为 sin/cos 函数具有线性可表达的周期性）。

### 4. 编码器结构
每层包含两个子层：
- **Multi-Head Self-Attention**（MHA）
- **Position-wise Feed-Forward Network**（全连接层，两层线性变换，中间 ReLU）
每个子层周围使用 **残差连接（Residual Connection）** 和 **Layer Normalization**。

### 5. 解码器结构
与编码器类似，但多了一个 Masked Multi-Head Cross-Attention 层（接受 Encoder 输出作为 K/V）：
- **Masked Self-Attention**：防止解码器在预测第 t 个 token 时看到未来位置的信息（通过将非法连接置为 -∞ 再 softmax）
- **Cross-Attention**：Query 来自解码器前一层，Keys 和 Values 来自编码器最终输出

### 6. 训练配置
- 优化器：Adam（β1=0.9, β2=0.98, ε=10^-9）
- 学习率调度：**Noam Schedule**（前 warmup_steps 线性增长，后续按步^-0.5 衰减）
- 正则化：Label Smoothing（ε=0.1）、Dropout（0.1）
- 英德翻译：BASE 模型 d_model=512, 6层, 8头, FFN=2048; BIG 模型 d_model=1024, 6层, 16头, FFN=4096
- 训练步数：英德 100K 步，3.5 天在 8 块 P100 GPU 上

## 关键发现

1. **SOTA 翻译质量**：Transformer 在 WMT 英德/英法两个翻译任务上均刷新了单模型记录（28.4 / 41.8 BLEU），大幅超越 LSTM/GRU 集成模型
2. **训练效率提升**：BIG 模型训练时间仅约 0.1 天（P100 8GPU），而之前最佳系统训练数周
3. **泛化能力**：无需修改架构，仅通过迁移学习即可应用于英语句法分析任务
4. **注意力可视化发现**：模型确实学习到了语法结构——不同注意力头关注不同的语法关系（如主语-动词、修饰语等）
5. **残差连接的关键作用**：没有残差连接，8 层模型几乎无法训练；残差连接使得深层 Transformer 稳定训练

## 个人评价

这是深度学习历史上最重大的架构突破之一。Vaswani 等人用简洁优雅的数学（缩放点积注意力 + 残差连接 + 层归一化）解决了一个困扰 NLP 领域几十年的问题——如何高效建模任意距离的依赖关系。

**为什么重要**：
- 2017年的 Transformer 论文至今被引用超 17 万次，是有史以来被引用最高的深度学习论文之一
- 它不仅是翻译模型，更是一套通用的序列建模框架：GPT 系列（单向）、BERT（双向）、T5、ChatGPT、Llama 等全部衍生自 Transformer 架构
- 直到 2024 年的最新大语言模型（GPT-4、Claude、Gemini）仍然运行在 Transformer 之上

**个人反思**：论文的创新不在于"发明"注意力机制（Bahdanau 2014 已提出），而在于**敢于完全抛弃 RNN**、**精心调优每个工程细节**（位置编码、Noam Schedule、Label Smoothing）的魄力。Google 团队用 8 块 GPU 在 3.5 天内做出的实验，证明了这一架构的工程可行性，为后续整个 AI 领域的发展指明了方向。

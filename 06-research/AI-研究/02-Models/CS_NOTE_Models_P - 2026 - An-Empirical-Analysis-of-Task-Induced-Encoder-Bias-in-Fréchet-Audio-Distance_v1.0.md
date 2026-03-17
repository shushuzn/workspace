type: paper
status: draft
date: 2026-02-27
tags: [Audio, FAD]
------------------

# An Empirical Analysis of Task-Induced Encoder Bias in Fréchet Audio Distance

**Source:** ARXIV: 2602.23958  
**Authors:** Wonwoo Jeong  
**Published:** 2026-02-27  | **Updated:** 2026-02-27  
**Landing:** https://arxiv.org/abs/2602.23958v1  
**PDF:** https://arxiv.org/pdf/2602.23958v1  
**Primary Category:** eess.AS

---

## Research Question Card

* 我想解决什么问题？
* 为什么重要？
* 我的先验判断是什么？
* 什么证据会推翻我？

---

## 1. 背景

> **Abstract（原文）**  
> Fréchet Audio Distance (FAD) is the de facto standard for evaluating text-to-audio generation, yet its scores depend on the underlying encoder's embedding space. An encoder's training task dictates which acoustic features are preserved or discarded, causing FAD to inherit systematic task-induced biases. We decompose evaluation into Recall, Precision, and Alignment (split into semantic and structural dimensions), using log-scale normalization for fair cross-encoder comparison. Controlled experiments on six encoders across two datasets reveal a four-axis trade-off: reconstruction-based AudioMAE leads precision sensitivity; ASR-trained Whisper dominates structural detection but is blind to signal degradation; classification-trained VGGish maximizes semantic detection but penalizes legitimate intra-class variation. Since no single encoder is a universal evaluator, future metrics must shift toward evaluation-native encoders intrinsically aligned with human perception.

---

## 2. 核心问题

---

## 3. 方法结构

### 架构拆解

### 算法逻辑

### 关键组件

---

## 4. 关键创新

---

## 5. 实验分析

### 数据集

### 基线对比

### 消融实验

### 成本分析

---

## 6. 对抗式审稿

* 逻辑漏洞：
* 偏置风险：
* 复现难度：
* 失败模式推测：

---

## 7. 优势

---

## 8. 局限

---

## 9. 本质抽象

---

## 10. 与其他方法对比

* vs A：
* vs B：
* vs C：

---

## 11. Decision（决策）

* 是否使用？
* 使用场景？
* 不适用边界？
* 接下来关注信号？

---

## 知识蒸馏

### Facts

1.
2.

### Principles

1.
2.

### Insights

1.
2.

---

## 认知升级

* 长期价值：
* 规模效应：
* 技术护城河：
* 是否范式转移：
* 商业潜力：

---

## 评分量表

* Novelty (1-5):
* Leverage (1-5):
* Evidence (1-5):
* Cost (1-5):
* Moat (1-5):
* Adoption Signal (1-5):

### Overall Judgment


---

## AI 自动初稿（待核验）

## 1. 背景
> AI Draft（可编辑，需人工核验）
- **【事实】** 文本到音频（TTA）生成技术随着扩散模型和语言模型架构的发展迅速进步【事实】。
- **【事实】** Fréchet Audio Distance (FAD) 已成为评估 TTA 生成的事实标准基准指标，改编自视觉领域的 FID【事实】。
- **【事实】** FAD 计算预训练编码器嵌入空间中真实音频与生成音频的分布距离（假设为高斯分布）【事实】。
- **【事实】** 现有研究指出 FAD 分数可能与人类听觉判断存在分歧，这一局限性与其视觉 counterpart FID 共享【事实】。
- **【推断】** 随着生成模型能力的提升，对评估指标可靠性的需求日益 intensifying，传统的单一指标可能无法捕捉感知细微差别【推断】。

## 2. 核心问题
> AI Draft（可编辑，需人工核验）
- **【事实】** FAD 分数依赖于底层编码器的嵌入空间，编码器的训练任务决定了哪些声学特征被保留或丢弃【事实】。
- **【事实】** 这导致 FAD 继承了系统性的“任务诱导偏差”（Task-Induced Bias）【事实】。
- **【事实】** 主导且最少被研究的感知分歧来源是编码器的训练任务，而非 FAD 的高斯假设或样本大小敏感性【事实】。
- **【推断】** 核心矛盾在于：目前缺乏一个通用的编码器能作为“ universal evaluator"，不同任务导向的编码器对同一生成结果的评价存在盲区【推断】。
- **【事实】**  distortions 若落入编码器的不变性集（Invariance Set），无论感知严重程度如何，FAD 变化均可忽略【事实】。

## 3. 方法结构
> AI Draft（可编辑，需人工核验）
- **评估维度分解（R/P/A）**
    - **【事实】** 将评估分解为三个轴：Recall（召回）、Precision（精度）、Alignment（对齐）【事实】。
    - **【事实】** Alignment 进一步细分为 Semantic（语义，如音色、声源身份）和 Structural（结构，如时间顺序、事件序列）【事实】。
    - **【事实】** 最终形成四轴评估 profile（Four-axis evaluation profile）【事实】。
- **跨编码器归一化**
    - **【事实】** 采用对数尺度自参考归一化（log-scale self-reference normalization）以实现公平的跨编码器比较【事实】。
    - **【事实】** 公式：$S_{norm}^{(e)}(\tau) = \frac{\log(1 + FAD^{(e)}(\tau))}{\log(1 + FAD^{(e)}_{max})}$，其中 $FAD_{max}$ 为该编码器在所有扰动中的最大观测值【事实】。
    - **【推断】** 此方法旨在解决不同编码器动态范围差异过大（如 EnCodec 可达 148 而 CLAP 仅 1.0）导致的“视觉压缩”问题【推断】。
- **扰动设计 suite**
    - **【事实】** 针对各轴设计特定扰动：Recall（轻微音高/时间拉伸）、Precision（噪声/低通/混响）、Semantic（大幅音高/共振峰偏移）、Structural（时间反转/片段洗牌）【事实】。

## 4. 关键创新
> AI Draft（可编辑，需人工核验）
- **【事实】** 提出了针对 FAD 的 Recall-Precision-Alignment (R/P/A) 分解分析法，而非仅依赖单一分布距离【事实】。
- **【事实】** 引入对数尺度自参考归一化，解决了不同编码器 FAD 动态范围差异导致的比较失效问题【事实】。
- **【推断】** 首次系统性地映射了主流音频编码器（ASR、分类、重建等任务）在 FAD 评估中的“不变性集”与“盲区”【推断】。
- **【事实】** 揭示了编码器训练任务与评估偏差之间的直接因果关系（如 ASR 任务导致对信号退化不敏感）【事实】。

## 5. 实验分析
> AI Draft（可编辑，需人工核验）
- **数据集**
    - **【事实】** LibriSpeech test-clean (2,620 utterances, 语音域)【事实】。
    - **【事实】** ESC-50 (2,000 environmental sounds, 通用音频域)【事实】。
- **基线编码器 (6 种)**
    - **【事实】** AudioMAE (Masked Reconstruction), EnCodec (Neural Audio Compression), Wav2Vec 2.0 (SSL), VGGish (Classification), CLAP (Cross-modal), Whisper (ASR)【事实】。
- **主要发现 (四轴权衡)**
    - **【事实】** AudioMAE  leading Precision sensitivity (对信号退化最敏感)【事实】。
    - **【事实】** Whisper dominates Structural detection (对时间顺序敏感) 但对信号退化 blind (不敏感)【事实】。
    - **【事实】** VGGish maximizes Semantic detection 但 penalizes legitimate intra-class variation (Recall 低)【事实】。
    - **【事实】** 不存在单一编码器能同时在所有轴上表现最佳【事实】。
- **消融实验**
    - **未在当前片段中找到** (文中主要对比不同编码器而非同一编码器内部组件消融)。
- **成本分析**
    - **未在当前片段中找到** (未提及具体 GPU 耗时或计算成本)。

## 6. 对抗式审稿
> AI Draft（可编辑，需人工核验）
- **逻辑漏洞**
    - **【推断】** 扰动设计基于 DSP 变换，可能与真实生成模型的伪影（Artifacts）分布不完全一致，存在生态效度风险【推断】。
    - **【推断】** 将 Alignment 强行拆分为语义和结构可能忽略了二者在人类感知中的耦合性【推断】。
- **偏置风险**
    - **【事实】** 实验仅覆盖语音和环境音，未包含音乐域（文中自述局限）【事实】。
    - **【推断】** 归一化方法依赖 $FAD_{max}$，若扰动 suite 未覆盖编码器极端敏感区，归一化结果可能失真【推断】。
- **复现难度**
    - **【推断】** 中等。需复现 6 种编码器的前向传播及特定 DSP 扰动 pipeline，归一化逻辑清晰但需确保扰动参数一致【推断】。
- **失败模式推测**
    - **【推断】** 若生成模型伪影恰好落在某编码器的不变性集内（如 Whisper 对噪声不敏感），该方法可能误判生成质量【推断】。

## 7. 优势
> AI Draft（可编辑，需人工核验）
- **【事实】** 提供了诊断编码器盲区的系统性分析透镜（Analytical Lens）【事实】。
- **【事实】** 归一化方法显著提升了低失真区域（Low-distortion regime）的区分度，符合 Weber–Fechner 定律【事实】。
- **【推断】** 促使研究者明确披露所使用的编码器，避免“黑盒”评估导致的误导【推断】。
- **【事实】** 实证了训练任务如何具体影响评估指标，为未来设计“评估原生编码器”提供方向【事实】。

## 8. 局限
> AI Draft（可编辑，需人工核验）
- **【事实】** 缺乏大规模主观测试（如 FAD-MOS 相关性）来映射分析轴与人类听觉判断的关系【事实】。
- **【事实】** 验证的架构范围有限，需在其他同类范式（如 HuBERT, AST）上验证趋势【事实】。
- **【事实】** 未涵盖音乐域，而音乐中和声、节奏与音色的交互更为复杂【事实】。
- **【事实】** 真实生成伪影高度纠缠，比 DSP 扰动更难诊断分离【事实】。

## 9. 本质抽象
> AI Draft（可编辑，需人工核验）
- **【推断】** 评估指标的本质是“感知空间在特定任务子空间上的投影”【推断】。
- **【推断】** FAD 测量的不是绝对感知距离，而是编码器训练任务所保留子空间上的发散度【推断】。
- **【事实】** 编码器的不变性集（Invariance Set）直接定义了其固有的评估偏差【事实】。
- **【推断】** 理想的评估器应拥有与人类感知内在对齐的嵌入空间几何结构，而非由单一下游任务 dictate【推断】。

## 10. 与其他方法对比
> AI Draft（可编辑，需人工核验）
- **vs FID (Fréchet Inception Distance)**
    - **【事实】** FAD 是 FID 的音频适配版，两者共享高斯假设局限【事实】。
    - **【推断】** 本文揭示了 FAD 特有的编码器任务偏差问题，这在视觉 FID 中同样存在但较少被系统性分解【推断】。
- **vs KLD / IS (KL Divergence / Inception Score)**
    - **【推断】** 传统指标同样依赖编码器特征，但缺乏本文的 R/P/A 细粒度诊断能力【推断】。
- **vs Human Eval (MOS)**
    - **【事实】** 人类评估是感知金标准，但成本高【事实】。
    - **【推断】** 本文方法旨在缩小自动指标与人类评估的差距，而非完全替代【推断】。

## 11. Decision（决策）
> AI Draft（可编辑，需人工核验）
- **是否使用**
    - **【推断】** 是，但仅作为诊断工具或多指标组合的一部分，不作为单一优化目标【推断】。
- **使用场景**
    - **【事实】** 需要分析生成模型具体缺陷类型（是结构乱了还是音质差了）时【事实】。
    - **【事实】** 对比不同编码器对同一生成模型的评价差异时【事实】。
- **不适用边界**
    - **【事实】** 音乐生成评估（文中明确未覆盖）【事实】。
    - **【推断】** 需要绝对质量排名而非相对诊断时【推断】。
- **接下来关注信号**
    - **【推断】** 关注是否有后续工作提出“评估原生编码器”（Evaluation-native encoders）【推断】。
    - **【事实】** 关注文中提到的 FAD-MOS 相关性验证后续研究【事实】。

## 知识蒸馏
> AI Draft（可编辑，需人工核验）
- **Facts**
    - FAD 分数依赖编码器嵌入空间。
    - 6 种编码器在 2 数据集上的四轴权衡实证结果。
    - 对数归一化公式及必要性。
- **Principles**
    - 训练任务决定特征保留/丢弃（Task dictates feature preservation）。
    - 不变性集导致评估盲区（Invariance set creates blind spots）。
    - 低失真区域的区分度对评估至关重要（Discriminative resolution in low-distortion regime）。
- **Insights**
    - 没有通用的评估编码器（No universal evaluator）。
    - 评估指标设计需从“任务迁移”转向“感知对齐”（Shift from task-transfer to perception-aligned）。
    - 单一指标会混淆 Recall/Precision/Alignment 维度。

## 认知升级
> AI Draft（可编辑，需人工核验）
- **长期价值**
    - **【推断】** 推动音频评估从“黑盒打分”向“白盒诊断”转型，提升生成模型迭代效率【推断】。
- **规模效应**
    - **【推断】** 若建立标准化的 R/P/A 评估基准，可促进社区对编码器选择的共识【推断】。
- **技术护城河**
    - **【推断】** 提出“评估原生编码器”概念，可能成为未来评估指标设计的新范式【推断】。
- **是否范式转移**
    - **【推断】** 是评估方法论的转移（从单一分数到多维 Profile），而非生成模型本身的转移【推断】。
- **商业潜力**
    - **【推断】** 适用于音频生成平台的质量监控模块，帮助客户理解生成内容的具体缺陷【推断】。

## 评分量表
> AI Draft（可编辑，需人工核验）
- **Novelty: 8/10** (系统性分解 FAD 偏差并提出归一化方法，视角独特)
- **Leverage: 7/10** (对现有 FAD 使用者有直接指导意义，但需额外计算成本)
- **Evidence: 8/10** (6 编码器 x 2 数据集 x 多扰动，实证充分)
- **Cost: 6/10** (需运行多个编码器及扰动测试，比单跑 FAD 成本高)
- **Moat: 7/10** (方法论清晰，但容易被跟进，核心护城河在于后续“评估原生编码器”的实现)
- **Adoption Signal: 8/10** (解决了社区痛点，即 FAD 与人类感知不一致的问题)
- **Overall Judgment: 8/10** (一篇高质量的实证分析论文，虽未提出新生成模型，但对评估领域有重要修正意义)

---

## 附：PDF 章节粗拆（自动抽取 · 供快速定位）

### BODY

> An Empirical Analysis of Task-Induced Encoder Bias
> in Fr´echet Audio Distance
> Wonwoo Jeong
> Department of Computer Science and Engineering, Sogang University, Seoul, Republic of Korea
> jeongwonwoo@sogang.ac.kr

### Abstract

> Fr´echet Audio Distance (FAD) is the de facto standard for eval-
> uating text-to-audio generation, yet its scores depend on the
> underlying encoder’s embedding space. An encoder’s training
> task dictates which acoustic features are preserved or discarded,
> causing FAD to inherit systematic task-induced biases. We de-
> compose evaluation into Recall, Precision, and Alignment (split
> into semantic and structural dimensions), using log-scale nor-
> malization for fair cross-encoder comparison. Controlled ex-
> periments on six encoders across two datasets reveal a four-axis
> trade-off: reconstruction-based AudioMAE leads precision sen-
> sitivity; ASR-trained Whisper dominates structural detection
> but is blind to signal degradation; classification-trained VGGish
> maximizes semantic detection but penalizes legitimate intra-
> class variation. Since no single encoder is a universal evalua-
> tor, future metrics must shift toward evaluation-native encoders
> intrinsically aligned with human perception.
> Index Terms: audio evaluation, Fr´echet Audio Distance, text-
> to-audio generation, audio encoders, evaluation metrics
> 1. Introduction
> Text-to-audio (TTA) generation has advanced rapidly with
> diffusion-based and language-model-based architectures [1, 2,
> 3, 4, 5, 6], intensifying the need for reliable automatic evalua-
> tion. Fr´echet Audio Distance (FAD) [7], adapted from FID [8],
> computes distributional distance between real and generated au-
> dio in a pretrained encoder’s embedding space and has become
> the standard benchmark metric [4, 9, 10, 11]. However, FAD
> scores can diverge from human auditory judgments [12, 13]—a
> limitation shared with its visual counterpart FID [14] and one
> that undermines its reliability as a perceptual proxy.
> While FAD’s Gaussian assumption [15] and sample size
> sensitivity
> …

### CLAP

> Whisper
> Figure 1: Four-axis trade-off (Outermost is better). AudioMAE
> leads Precision; Whisper captures Structural but is invariant to
> signal degradation; VGGish leads Semantic but limits Recall.
> reveal a four-axis trade-off (Figure 1): AudioMAE achieves the
> highest precision sensitivity; Whisper dominates structural de-
> tection but exhibits marginal sensitivity to signal degradation;
> VGGish leads semantic alignment but disproportionately pe-
> nalizes recall. Because every encoder’s training task induces
> a distinct invariance set, no single tested encoder functions as
> a universal evaluator—a finding that underscores the need for
> evaluation-native encoders whose embedding spaces are intrin-
> sically aligned with human perception.
> 2. Analytical Methodology
> 2.1. Fr´echet Audio Distance and Encoder Projection
> Let X be the input audio space and Φ : X →Z ⊂Rd be a
> pretrained encoder, where Z denotes the d-dimensional embed-
> ding space induced by the training task. FAD measures the 2-
> Wasserstein distance between reference and generated embed-
> ding distributions in Z, modeled as Gaussians N(µr, Σr) and
> N(µg, Σg) estimated from the reference set R and generated
> set G, respectively:
> FAD = ∥µr−µg∥2 + tr
>  Σr+Σg−2(ΣrΣg)1/2
> (1)
> While FAD constitutes a valid distributional metric within Z, its
> capacity to represent perceptual distance in X is fundamentally
> constrained by the structure of Φ. To analyze this limitation, let
> Gpert be a perturbed set where each reference sample x ∈R is
> replaced by its transformed counterpart ˜x ∈X subjected to a
> specific perceptual perturbation (e.g., temporal shuffling, addi-
> tive noise). If the encoder is invariant to this perturbation such
> that Φ(˜x) ≈Φ(x) for all x ∈R, the embedding distributions
> arXiv:2602.23958v1  [eess.AS]  27 Feb 2026
> in Z become
> …

### CLAP

> Whisper
> Figure 2: Precision response to white noise. (a) Raw FAD (lin-
> ear scale): dynamic-range disparity compresses low-sensitivity
> encoders into a visually indistinguishable baseline—this “vi-
> sual squashing” motivates our normalization. (b) After log-
> scale normalization (Snorm), all six trajectories separate, re-
> vealing each encoder’s distinct precision profile.
> FAD(e)(τ) ≡FAD(R, Gτ) denote the FAD computed via en-
> coder e between the clean reference set and the set perturbed
> by τ:
> S(e)
> norm(τ) = log(1 + FAD(e)(τ))
> log(1 + FAD(e)
> max)
> (3)
> where FAD(e)
> max is the maximum FAD observed for encoder e
> across our fixed perturbation suite, rendering the normalization
> deterministic. Since every encoder is exposed to identical per-
> turbations, FAD(e)
> max reflects each encoder’s intrinsic dynamic
> range. The log(1+·) transform provides a monotonic compres-
> sive mapping; our goal is comparative profiling of task-induced
> sensitivities, not absolute cross-encoder ranking. Using the 95th
> percentile instead of the maximum yields identical qualitative
> conclusions.
> Figure 2 illustrates the necessity of this normalization. On
> a linear scale (a), the broad dynamic range of EnCodec (reach-
> ing 148.8 at SNR −5 dB) compresses the response trajectories
> of less sensitive encoders (e.g., VGGish, Whisper, and CLAP)
> into a visually indistinguishable baseline. After log-scale nor-
> malization (b), the variations among all six encoders become
> distinctly observable. This transformation is justified on two
> grounds:
> Mitigation of scale-disparity compression. FAD is un-
> bounded; as Figure 2(a) shows, dynamic ranges differ by over
> two orders of magnitude (EnCodec exceeds 148 while CLAP
> barely reaches 1.0). Linear normalization bounded by these ex-
> tremes would compress the low-distortion regime (FAD
> …

### CLAP

> Cross-modal Contrastive Learning 48k
> 512
> Whisper
> Automatic Speech Recognition
> 16k 1280
> 3. Experimental Setup
> 3.1. Datasets and Preprocessing
> We utilize LibriSpeech test-clean [26] (2,620 utterances, vari-
> able length) and ESC-50 [27] (2,000 environmental sounds, 5 s
> each) to span the speech and general audio domains.
> Clips
> retain their original duration without padding or truncation:
> because FAD aggregates per-clip embeddings into set-level
> Gaussian statistics, duration variability is inherently neutral-
> ized between paired reference and perturbed sets. All audio
> is loudness-normalized to −23 LUFS (ITU-R BS.1770-4) and
> resampled to each encoder’s native rate.
> 3.2. Encoders
> We evaluate six encoders spanning five training paradigms (Ta-
> ble 1), carefully chosen to probe complementary regions of the
> invariance–sensitivity landscape:
> Semantic encoders. Whisper [17] (ASR) represents lin-
> guistic structure preservation and provides an empirical ceiling
> for temporal sensitivity. CLAP [28] maps audio into a shared
> text–audio space to probe cross-modal alignment transfer. VG-
> Gish [18] provides a baseline for spectral template sensitivity.
> Acoustic encoders. AudioMAE [29] (masked reconstruc-
> tion) establishes the empirical ceiling for signal-level preci-
> sion sensitivity.
> EnCodec [19] (neural codec) tests whether
> compression-oriented training introduces systematic frequency-
> band biases. Wav2Vec 2.0 [30] (self-supervised, related to Hu-
> BERT [31] and BEATs [32]) serves as a task-agnostic base-
> line. For transformer-based encoders (Whisper, AudioMAE,
> Wav2Vec 2.0), we extract the final hidden state; for EnCodec,
> we utilize the continuous encoder output prior to the residual
> vector quantizer. FAD requires a single clip-level embedding
> per sample. Following standard practice [7], we
> …

### evaluation axis:

> Recall.
> Mild pitch shift (±1, ±2 st) and time stretch
> (0.9×, 1.1×) represent intra-class stylistic variations that
> should not trigger significant distributional shifts.
> Precision.
> Signal-level
> degradations
> include
> addi-
> tive white noise at SNR ∈
> {60, 40, 20, 10, 0, −5} dB,
> low-pass
> biquad
> filtering
> with
> cutoffs
> at
> -8
> -4
> -2
> -1
> 1
> 2
> 4
> 8
> Pitch shift (semitones)
> 0.0
> 0.2
> 0.4
> 0.6
> 0.8
> 1.0
> Snorm
> Recall
> Zone
> AudioMAE
> EnCodec
> Wav2Vec 2.0
> VGGish

### CLAP

> Whisper
> Figure 3: Pitch-shift trajectory (−8 to +8 st).
> Shaded: re-
> call zone (±1–2 st). VGGish shows inflexible sensitivity at mild
> shifts; Whisper maintains the lowest recall-zone response.
> {8000, 6000, 4000, 2000, 1000}
> Hz,
> and
> reverberation
> with RT60 ∈{0.1, 0.2, 0.25, 0.4, 0.5, 0.6, 0.8, 1.0, 2.0} s.
> Semantic Alignment. Severe distortions include pitch shift
> at ±4, ±8 st and spectral envelope manipulation (“formant
> shift”) at 1.3×, 1.4× with F0 preserved. While originating in
> speech processing, this reshaping modifies the perceived phys-
> ical dimensions and resonance of general audio sources, effec-
> tively inducing a categorical shift in source identity.
> Structural Alignment. Macroscopic temporal disruptions
> are evaluated via time reversal and chunk shuffling at durations
> of {1000, 500, 250, 100} ms. We apply 10 ms cross-fades to
> eliminate click artifacts and isolate structural effects.
> All transformations are executed via standard DSP libraries.
> The demarcation between Recall and Semantic Alignment is
> operationally defined by general perceptual tendencies: mild
> ±1–2 st shifts typically represent natural expressive variation,
> whereas larger ±4–8 st shifts tend to alter the perceived source
> identity.
> 4. Results and Discussion
> 4.1. The Four-Axis Trade-off
> As detailed in Table 2 and Figure 1, AudioMAE demonstrates
> the highest Precision, closely followed by EnCodec. Whisper
> exhibits an orthogonal profile, maximizing Structural Align-
> ment and Recall while minimizing Precision. Conversely, VG-
> Gish maximizes Semantic Alignment at the expense of Re-
> call. CLAP remains balanced but achieves no peak sensitivities.
> Two distinct mechanisms underlie this trade-off: the Semantic–
> Recall opposition is fundamental, as classification training col-
> lapses features onto tight class-
> …

### 2 st, shaded), VGGish registers Snorm=0.36 at +1 st—9×

> Whisper’s 0.04—because classification training interprets even
> minor spectral displacements as categorical deviations: a re-
> call trap. The contrast between near-uniform responses within
> ±2 st and divergent, asymmetric profiles at ±4–8 st empirically
> validates the perceptual-magnitude demarcation between Recall
> and Semantic Alignment (Section 3.3). This rigid sensitivity ex-
> tends to the temporal domain: under mild time stretch (0.9×–
> 1.1×), all encoders show disproportionately higher sensitivity
> than under comparable pitch shifts. Consequently, optimizing
> for single-encoder FAD risks constraining generative models to
> narrow spectral and temporal templates, actively penalizing nat-
> ural variations that listeners typically accept [34, 35].
> 4.3. Precision: Threshold Behavior and Codec Blind Spots
> Whisper’s suppressed precision sensitivity ( ¯Snorm=0.23 for
> noise, 0.14 for reverberation) is consistent with ASR training
> that incentivizes noise-robust representations to maintain tran-
> scription accuracy. In contrast, VGGish (0.46 noise, 0.44 rever-
> beration) and AudioMAE saturate rapidly, reflecting their acute
> sensitivity to signal-level degradation. EnCodec’s low-pass re-
> sponse on LibriSpeech reveals a distinct anomaly: FAD jumps
> 32× between 6 kHz and 8 kHz, as RVQ capacity concentrates
> sub-8 kHz [19]—this discontinuity does not manifest on ESC-
> 50, indicating a speech-specific bandwidth bias.
> 4.4. Alignment: Content vs. Order
> A Pearson correlation analysis between the Structural and Se-
> mantic scores (Table 2) across all six encoders reveals a strong
> anti-correlation (r=−0.67).
> Figure 4 illustrates this inverse
> relationship. Under identical mean-pooling, Whisper demon-
> strates pronounced sensitivity to structural disruptions while re-
> maining largely invariant to semanti
> …

### CLAP

> Whisper
>  Structural Alignment
> Semantic Alignment
> Reversal / Pitch +8 st
> Shuffle 100 ms / Formant 1.4×
> Figure 4: Diverging bar chart of Structural (left) vs. Semantic
> (right) sensitivity. Solid bars: Reversal / Pitch +8 st; hatched
> bars:
> Shuffle 100 ms / Formant 1.4×.
> Whisper extends far
> left (structural-dominant); VGGish extends far right (semantic-
> dominant)—visually capturing the anti-correlation (r=−0.67).
> based encoders largely fail to detect structural violations. Al-
> though multi-encoder aggregation might appear as a poten-
> tial solution, the principled fusion of heterogeneous embedding
> spaces—differing in sample rate, dimensionality, and dynamic
> range—constitutes an open problem. Practitioners should there-
> fore transition away from monolithic FAD reporting, explicitly
> disclosing the chosen encoder and selecting one aligned with
> their specific evaluation goals.
> More fundamentally, relying on task-specific encoders lim-
> its FAD by design; their invariance sets are immutable artifacts
> of their training tasks. Unlike these models, human auditory
> perception integrates semantic identity and structural flow with-
> out mutually exclusive trade-offs. Overcoming this limitation
> requires shifting toward representations intrinsically aligned
> with human perception. Rather than serving as a direct opti-
> mization target, the presented R/P/A decomposition functions
> as an analytical lens to diagnose these blind spots and audit fu-
> ture metrics for balanced sensitivities.
> While our approach effectively isolates task-induced biases,
> several limitations remain. First, mapping the analytical R/P/A
> axes to human auditory judgments necessitates large-scale sub-
> jective testing (e.g., FAD–MOS correlation). Second, to avoid
> over-generalization, the observed trends should be verified
> acro
> …

### evaluation metric for image generation,” in Proc. IEEE/CVF

> Conference on Computer Vision and Pattern Recognition (CVPR),
> 2024, pp. 9307–9315.
> [15] S. Chung, S. Jung, S. Mun, H.-j. Song, and J.-H. Kim, “KAD: No
> more FAD! an effective and efficient evaluation metric for audio
> generation,” in Proc. International Conference on Learning Rep-
> resentations (ICLR), 2025.
> [16] G. Parmar, R. Zhang, and J.-Y. Zhu, “On aliased resizing and sur-
> prising subtleties in GAN evaluation,” in Proc. IEEE/CVF Confer-
> ence on Computer Vision and Pattern Recognition (CVPR), 2022,
> pp. 11 410–11 420.
> [17] A. Radford, J. W. Kim, T. Xu, G. Brockman, C. McLeavey, and

### I. Sutskever, “Robust speech recognition via large-scale weak su-

> pervision,” in Proc. International Conference on Machine Learn-
> ing (ICML), 2023, pp. 28 492–28 518.
> [18] S. Hershey, S. Chaudhuri, D. P. W. Ellis, J. F. Gemmeke,
> A. Jansen, R. C. Moore, M. Plakal, D. Platt, R. A. Sauber,
> B. Seybold et al., “CNN architectures for large-scale audio clas-
> sification,” in Proc. IEEE International Conference on Acoustics,
> Speech and Signal Processing (ICASSP), 2017, pp. 131–135.
> [19] A. D´efossez, J. Copet, G. Synnaeve, and Y. Adi, “High fidelity
> neural audio compression,” Transactions on Machine Learning
> Research, 2023.
> [20] M. S. M. Sajjadi, O. Bachem, M. Lucic, O. Bousquet, and
> S. Gelly, “Assessing generative models via precision and recall,”
> in Advances in Neural Information Processing Systems, vol. 31,
> 2018.
> [21] T. Kynk¨a¨anniemi, T. Karras, S. Laine, J. Lehtinen, and T. Aila,
> “Improved precision and recall metric for assessing generative
> models,” in Advances in Neural Information Processing Systems,
> vol. 32, 2019.
> [22] M. F. Naeem, S. J. Oh, Y. Uh, Y. Choi, and J. Yoo, “Reliable
> fidelity and diversity metrics for generative models,” in Proc. In-
> ternational Conference on Machine Learning (ICML), 2020, pp.
> 7176–7185.
> [23] D. Friedman and A. B. Dieng, “The vendi score: A diversity eval-
> uation metric for machine learning,” Transactions on Machine
> Learning Research, 2023.
> [24] E. H. Weber, De Pulsu, Resorptione, Auditu et Tactu: Annota-
> tiones Anatomicae et Physiologicae.
> Koehler, Leipzig, 1834.
> [25] G. T. Fechner, Elemente der Psychophysik. Breitkopf und H¨artel,
> Leipzig, 1860.
> [26] V. Panayotov, G. Chen, D. Povey, and S. Khudanpur, “Lib-
> riSpeech: An ASR corpus based on public domain audio books,”
> in Proc. IEEE International Conference on Acoustics, Speech and
> Signal Processing (ICASSP), 2015, pp. 5206–5210.
> [27] K. J. Piczak, “ESC: D
> …

### X. Yu, and F. Wei, “BEATs: Audio pre-training with acoustic tok-

> enizers,” in Proc. International Conference on Machine Learning
> (ICML), 2023, pp. 5178–5193.
> [33] V. Papyan, X. Y. Han, and D. L. Donoho, “Prevalence of neural
> collapse during the terminal phase of deep learning training,” Pro-
> ceedings of the National Academy of Sciences, vol. 117, no. 40,
> pp. 24 652–24 663, 2020.
> [34] K. Kumar, R. Kumar, T. de Boissiere, L. Gestin, W. Z. Teoh,
> J. Sotelo, A. de Br´ebisson, Y. Bengio, and A. Courville, “Mel-
> GAN: Generative adversarial networks for conditional waveform
> synthesis,” in Advances in Neural Information Processing Sys-
> tems, vol. 32, 2019.
> [35] Z. Kong, W. Ping, J. Huang, K. Zhao, and B. Catanzaro, “Dif-
> fWave: A versatile diffusion model for audio synthesis,” in Proc.
> International Conference on Learning Representations (ICLR),
> 2021.
> [36] Y. Gong, Y.-A. Chung, and J. Glass, “AST: Audio spectrogram
> transformer,” in Proc. Interspeech, 2021, pp. 571–575.

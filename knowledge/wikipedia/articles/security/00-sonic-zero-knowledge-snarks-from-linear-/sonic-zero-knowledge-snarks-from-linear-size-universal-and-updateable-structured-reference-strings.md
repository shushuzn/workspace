---
id: sonic-zero-knowledge-snarks-from-linear-size-universal-and-updateable-structured-reference-strings
title: Sonic: Zero-Knowledge SNARKs from Linear-Size Universal and Updateable Structured Reference Strings
category: security
tags: [论文解读, ePrint:2019/099]
eprint: 2019/099
source: IACR ePrint
url: https://eprint.iacr.org/2019/099
created: 2026-04-10T14:11:28.285Z
---

# Sonic: Zero-Knowledge SNARKs from Linear-Size Universal and Updateable Structured Reference Strings

**IACR ePrint** | ePrint: 2019/099 | **Author**: Mary Maller, Sean Bowe, Markulf Kohlweiss, Sarah Meiklejohn

## 摘要

Zero-knowledge proofs have become an important tool for addressing privacy and scalability concerns in cryptocurrencies and other applications. In many systems each client downloads and verifies every new proof, and so proofs must be small and cheap to verify. The most practical schemes require either a trusted setup, as in (pre-processing) zk-SNARKs, or verification complexity that scales linearly with the complexity of the relation, as in Bulletproofs. The structured reference strings required by most zk-SNARK schemes can be constructed with multi-party computation protocols, but the resulting parameters are specific to an individual relation. Groth et al. discovered a zk-SNARK protocol with a universal and updateable structured reference string, however the string scales quadratically in the size of the supported relations. Here we describe a zero-knowledge SNARK, Sonic, which supports a universal and continually updateable structured reference string that scales linearly in size. Sonic proofs are constant size, and in the batch verification context the marginal cost of verification is comparable with the most efficient SNARKs in the literature. We also describe a generally useful technique in which untrusted ``helpers&#39;&#39; can compute advice which allows batches of proofs to be verified more efficiently. Note: Batching arguments updated.

## 研究动机

零知识证明在区块链隐私和扩容中至关重要，但现有方案面临两难：

- **Groth16**：需可信Setup、电路专用，不同电路不同Setup
- **Bulletproofs**：无需可信Setup，但验证线性增长

Sonic的目标：首次实现**通用可更新的SRS**（Universal & Updateable SRS），同时保证：
- SRS大小与电路规模**线性**相关（非二次）
- 证明大小**常数**
- 验证**批量高效**

## 核心方法

### 1. 线性大小SRS

早期通用SNARK（如Groth16改进版）的SRS大小为O(n²)，Sonic通过新的多项式承诺方案将SRS降到O(n)。

关键创新：**Sally（Sonic Linear-sized Lagrange basis）**承诺方案，使得承诺大小与电路规模线性相关。

### 2. 可更新SRS

SRS可以持续更新，任何人都可以添加随机性来"破坏"之前的密钥，无需重新进行可信 Setup仪式。

### 3. 常数证明大小

无论电路多大，Sonic的证明总是常数大小（几个群元素），适合链上存储。

### 4. 批量验证优化

Sonic引入了"helper"概念：不可信的第三方可以预计算advice，使批量验证更高效。

## 关键发现

1. **线性SRS**：首次实现与电路规模线性相关的通用SRS
2. **常数证明**：证明大小与电路规模无关
3. **可更新安全**：SRS可无限期更新，数学上可证明安全性
4. **批量验证高效**：批量验证时， marginal cost与最高效SNARK可比
5. **奠基者角色**：Sonic开创了通用可更新SRS范式，PLONK/Marlin都建立在其基础上

## 个人评价

Sonic是"通用可更新SRS"领域的开创者。虽然后来被PLONK/Marlin超越（证明速度更快），但Sonic的核心思想——用线性SRS实现通用SNARK——是革命性的。

**深层跨域联系**：

1. **通用性 ↔ 拓扑通用性**：Sonic的"一个SRS适用所有电路"与拓扑中的"通用不变量"概念有深刻共鸣——都是寻找在广泛对象类上保持一致性的结构

2. **更新机制 ↔ 同调论**：SRS的"更新"操作与拓扑同调论中的边界算子有相似性——都是通过局部修正保持全局一致性

3. **批量验证 ↔ 范畴化**：Sonic的helper机制本质上是将计算任务"范畴化"——将多个相关证明组织成结构化的整体

## 相关条目

- [[plonk-permutations-over-lagrange-bases-for-oecumenical-noninteractive-arguments-of-knowledge|PLONK]] — PLONK继承Sonic的SRS思想并大幅优化证明速度
- [[marlin-preprocessing-zksnarks-with-universal-and-updatable-srs|Marlin]] — Marlin同样基于Sonic的通用SRS范式
- [[辫群]] — SRS的多项式承诺结构与辫群的多项式表示有代数同构性

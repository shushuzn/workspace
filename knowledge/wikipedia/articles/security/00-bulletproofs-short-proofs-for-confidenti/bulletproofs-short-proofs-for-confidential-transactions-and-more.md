---
id: bulletproofs-short-proofs-for-confidential-transactions-and-more
title: Bulletproofs: Short Proofs for Confidential Transactions and More
category: security
tags: [论文解读, ePrint:2017/1066]
eprint: 2017/1066
source: IACR ePrint
url: https://eprint.iacr.org/2017/1066
created: 2026-04-10T14:08:35.424Z
---

# Bulletproofs: Short Proofs for Confidential Transactions and More

**IACR ePrint** | ePrint: 2017/1066 | **Author**: Benedikt Bünz, Jonathan Bootle, Dan Boneh, Andrew Poelstra, Pieter Wuille, Greg Maxwell

## 摘要

We propose Bulletproofs, a new non-interactive zero-knowledge proof protocol with very short proofs and without a trusted setup; the proof size is only logarithmic in the witness size. Bulletproofs are especially well suited for efficient range proofs on committed values: they enable proving that a committed value is in a range using only $2\log_2(n)+9$ group and field elements, where $n$ is the bit length of the range. Proof generation and verification times are linear in $n$. Bulletproofs greatly improve on the linear (in $n$) sized range proofs in existing proposals for confidential transactions in Bitcoin and other cryptocurrencies. Moreover, Bulletproofs supports aggregation of range proofs, so that a party can prove that $m$ commitments lie in a given range by providing only an additive $O(\log(m))$ group elements over the length of a single proof. To aggregate proofs from multiple parties, we enable the parties to generate a single proof without revealing their inputs to each other via a simple multi-party computation (MPC) protocol for constructing Bulletproofs. This MPC protocol uses either a constant number of rounds and linear communication, or a logarithmic number of rounds and logarithmic communication. We show that verification time, while asymptotically linear, is very efficient in practice. Moreover, the verification of multiple Bulletproofs can be batched for further speed-up. Concretely, the marginal time to verify an aggregation of 16 range proofs is about the same as the time to verify 16 ECDSA signatures. Bulletproofs build on the techniques of Bootle et al. (EUROCRYPT 2016). Beyond range proofs, Bulletproofs provide short zero-knowledge proofs for general arithmetic circuits while only relying on the discrete logarithm assumption and without requiring a trusted setup. We discuss many applications that would benefit from Bulletproofs, primarily in the area of cryptocurrencies. The efficiency of Bulletproofs is particularly well suited for the distributed and trustless nature of blockchains. Note: This version fixes an earlier mistake in the Fiat-Shamir section (Section 4.4) reported by TrailOfBits.

## 研究动机

零知识证明（ZKP）是隐私保护的核心技术。传统方案面临三个根本问题：

1. **可信 Setup 问题**：Groth16等SNARK需要可信的多方计算仪式，密钥泄露风险高
2. **证明长度**：早期方案证明长度线性增长，链上存储成本高昂
3. **聚合效率**：多笔交易需要分别验证，无法批量处理

Bulletproofs的作者们（来自Stanford/Blockstream/Microsoft等）希望解决这三个问题，提出一种无需可信Setup、证明长度对数增长、支持高效聚合的零知识证明方案。

## 核心方法

### 1. 简短范围证明（Range Proof）

传统方案：证明范围需要 O(n) 复杂度（n=比特长度）

Bulletproofs创新：利用**内积论证**（Inner Product Argument），将复杂度降为 O(log n)：

$$\text{证明大小} = 2\log_2(n) + 9 \text{ 个群元素}$$

关键技巧：将Pedersen承诺表示为椭圆曲线点的线性组合，然后对内积关系递归证明。

### 2. 聚合协议（Aggregation Protocol）

多个证明方可以联合生成一个聚合证明，而无需暴露各自的私密输入：

- **常数轮数协议**：O(1)轮通信，但线性通信复杂度
- **对数轮数协议**：O(log m)轮通信，对数通信复杂度

### 3. 无需可信Setup

不依赖CRS（Common Reference String），只需离散对数假设。这比Groth16/Sonic等通用SNARK更安全——不存在密钥泄露风险。

### 4. 批量验证（Batched Verification）

多个Bulletproof可以批量验证，验证时间与单独验证相近：验证16个聚合范围证明的时间≈验证16个ECDSA签名。

## 关键发现

1. **对数级证明大小**：2log₂(n)+9个群元素，比早期方案小1-2个数量级
2. **线性验证时间**：验证复杂度O(n)，但常数很小，实际很快
3. **天然聚合**：多方无需透露私密输入即可聚合证明
4. **通用性**：不仅用于范围证明，还可证明任意算术电路
5. **适用场景**：区块链机密交易、分布式隐私计算、链上隐私保护

## 个人评价

Bulletproofs是零知识证明领域的重要里程碑。它证明了"简短证明"和"无需可信Setup"可以兼得，为隐私保护提供了实用工具。

**与拓扑数学的深层联系**：

Bulletproofs的代数结构（椭圆曲线群、内积论证）与拓扑数学存在意想不到的联系：

1. **辫群结构**：椭圆曲线点加法构成阿贝尔群，与辫群的交换关系（σᵢσⱼ=σⱼσᵢ, |i-j|>1）有结构相似性——两者都是"编织"代数

2. **拓扑量子计算**：Anyon的编织统计同样基于群结构，Bulletproofs的承诺聚合与拓扑量子比特的融合（fusion）操作有概念同构性——都是"组合多个组件产生新信息"

3. **数学统一性**：数论（椭圆曲线）、代数（辫群）、拓扑（Anyon统计）三个看似无关的领域，在"交换结构"这一核心概念下统一

这种跨领域类比揭示了数学的深层统一性：无论是有趣的物理系统、安全的密码协议，还是高效的证明系统，都可能共享相同的基本数学结构。

## 相关条目

- [[IAM 云身份与访问管理]] — Bulletproofs的隐私保护可用于IAM审计日志的零知识证明
- [[辫群]] — 辫群的阿贝尔结构与椭圆曲线群有代数同构性（交换性）
- [[拓扑量子计算]] — Anyon编织与Bulletproofs聚合都体现了"组合产生新信息"的数学原理

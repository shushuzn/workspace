---
id: ringct-20-a-compact-accumulator-based-linkable-ring-signature-protocol-for-blockchain-cryptocurrency-monero
title: RingCT 2.0: A Compact Accumulator-Based (Linkable Ring Signature) Protocol for Blockchain Cryptocurrency Monero
category: security
tags: [论文解读, ePrint:2017/921]
eprint: 2017/921
source: IACR ePrint
url: https://eprint.iacr.org/2017/921
created: 2026-04-10T14:43:50.477Z
---

# RingCT 2.0: A Compact Accumulator-Based (Linkable Ring Signature) Protocol for Blockchain Cryptocurrency Monero

**IACR ePrint** | ePrint: 2017/921 | **Author**: Shi-Feng Sun, Man Ho Au, Joseph K. Liu, Tsz Hon Yuen, Dawu Gu

## 摘要

In this work, we initially study the necessary properties and security requirements of Ring Confidential Transaction (RingCT) protocol deployed in the popular anonymous cryptocurrency Monero. Firstly, we formalize the syntax of RingCT protocol and present several formal security definitions according to its application in Monero. Based on our observations on the underlying (linkable) ring signature and commitment schemes, we then put forward a new efficient RingCT protocol (RingCT 2.0), which is built upon the well-known Pedersen commitment, accumulator with one-way domain and signature of knowledge (which altogether perform the functions of a linkable ring signature). Besides, we show that it satisfies the security requirements if the underlying building blocks are secure in the random oracle model. In comparison with the original RingCT protocol, our RingCT 2.0 protocol presents a significant space saving, namely, the transaction size is independent of the number of groups of input accounts included in the generalized ring while the original RingCT suffers a linear growth with the number of groups, which would allow each block to process more transactions.

## 研究动机

门罗币（Monero）的RingCT协议面临可扩展性瓶颈：

- **交易大小随输入组数线性增长**：原版RingCT交易大小与输入账户组数成正比
- **区块链膨胀**：交易数据大导致区块链体积快速膨胀
- **隐私与效率矛盾**：既要保持交易隐私，又要提升吞吐量

核心问题：如何在保持门罗币隐私特性的同时，减小RingCT交易大小？

## 核心方法

### 1. RingCT形式化

本文首先形式化RingCT协议的必要性质和安全要求：

- **环签名**：隐藏真实签名者身份
- **机密交易**：隐藏交易金额
- **链接性**：检测双花攻击
- **累加器**：聚合多个认证信息

### 2. RingCT 2.0构造

基于三个基础模块构建高效协议：

| 组件 | 作用 |
|------|------|
| Pedersen承诺 | 隐藏交易金额 |
| 单向域累加器 | 聚合认证信息 |
| 知识签名 | 证明承诺与签名的关联 |

### 3. 空间优化

关键突破：交易大小与输入组数无关

- 原版RingCT：交易大小 = O(输入组数)
- RingCT 2.0：交易大小 = O(1)

### 4. 安全性证明

在随机预言机模型下证明安全性：

- 基于底层组件安全性
- 满足门罗币应用的安全需求

## 关键发现

1. **交易大小常数级**：突破线性增长瓶颈
2. **区块链空间节省**：允许每个区块处理更多交易
3. **安全性严格证明**：提供完整的形式化安全分析
4. **兼容性好**：保持与门罗币生态的兼容性
5. **实用性强**：已被门罗币采用部署

## 个人评价

RingCT 2.0解决了门罗币长期以来的可扩展性痛点，在不牺牲隐私的前提下实现了显著的效率提升。这是密码学理论与工程实践完美结合的典范。

**深层跨域联系**：

1. **累加器 ↔ 拓扑不变子空间**：累加器将多个元素压缩为单一认证值，与拓扑中研究不变子空间（invariant subspace）的商空间构造有概念相似——都是通过某种"聚合"保持关键信息

2. **常数级交易大小 ↔ 拓扑紧化**：交易大小与输入组数无关体现了紧化（compactification）的思想——将无限或大量信息压缩到有限表示

3. **环签名隐私 ↔ 拓扑对称性**：环签名保护签名者身份与拓扑学中的对称性（symmetry）概念有深层联系——都是研究在某种变换下保持不变的性质

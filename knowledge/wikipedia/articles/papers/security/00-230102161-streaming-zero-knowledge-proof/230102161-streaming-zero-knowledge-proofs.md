---
id: 230102161-streaming-zero-knowledge-proofs
title: [2301.02161] Streaming Zero-Knowledge Proofs
category: security
tags: [论文解读, 2301.02161]
arxiv: 2301.02161
created: 2026-04-10T13:51:19.238Z
---

# [2301.02161] Streaming Zero-Knowledge Proofs

**arXiv**: 2301.02161 | **Author**: 

## 摘要

Streaming interactive proofs (SIPs) enable a space-bounded algorithm with one-pass access to a massive stream of data to verify a computation that requires large space, by communicating with a powerful but untrusted prover. This work initiates the study of zero-knowledge proofs for data streams. We define the notion of zero-knowledge in the streaming setting and construct zero-knowledge SIPs for the two main algorithmic building blocks in the streaming interactive proofs literature: the sumcheck and polynomial evaluation protocols. To the best of our knowledge all known streaming interactive proofs are based on either of these tools, and indeed, this allows us to obtain zero-knowledge SIPs for central streaming problems such as index, point and range queries, median, frequency moments, and inner product. Our protocols are efficient in terms of time and space, as well as communication: the verifier algorithm&#39;s space complexity is $\mathrm{polylog}(n)$ and, after a non-interactive setup that uses a random string of near-linear length, the remaining parameters are $n^{o(1)}$. En route, we develop an algorithmic toolkit for designing zero-knowledge data stream protocols, consisting of an algebraic streaming commitment protocol and a temporal commitment protocol.Our analyses rely on delicate algebraic and information-theoretic arguments and reductions from average-case communication complexity.

## 研究动机

流数据上的验证是云计算和区块链的核心问题：

- **海量数据**：现代数据流规模巨大（TB/PB级），无法全部存入内存
- **空间受限算法**：验证者只有多对数空间（polylog），无法存储整个数据流
- **流证明（SIP）**：允许空间受限的验证者与强大的证明者交互，验证流数据上的计算

核心问题：如何让流证明也具有**零知识性质**——不泄露证明者数据的同时验证正确性？

## 核心方法

### 1. 流零知识定义

零知识流证明需要满足：
- **完备性**：正确计算时验证者总是接受
- **可靠性**：错误计算时验证者以高概率拒绝
- **零知识性**：验证者无法从交互中学到关于数据的任何信息

### 2. 两大基础构建

本文基于两个核心协议：
- **Sumcheck协议**：验证多项式和的正确性
- **多项式求值协议**：验证在特定点的多项式值

### 3. 应用场景

基于以上构建，本文给出以下流问题的零知识证明：
- **索引查询**：数据流第i个元素
- **点查询**：元素是否在集合中
- **范围查询**：元素是否在给定范围内
- **中位数**：数据流的统计量
- **频率矩**：F₀, F₁, F₂等
- **内积**：两向量点积

### 4. 效率分析

| 参数 | 复杂度 |
|------|--------|
| 验证者空间 | polylog(n) |
| 通信 | n^{o(1)} |
| 预处理 | 近线性随机串 |

## 关键发现

1. **首个流零知识证明**：首次系统研究数据流上的零知识证明
2. **通用框架**：基于sumcheck和多项式求值，覆盖主要流问题
3. **高效验证**：验证者空间仅为polylog(n)，适合资源受限场景
4. **零知识保留**：在保持零知识的同时不显著增加通信开销
5. **工具包**：开发了代数流承诺协议和临时承诺协议

## 个人评价

 Streaming Zero-Knowledge Proofs是零知识证明与流算法交叉领域的重要突破。它为零知识证明在云计算和区块链中的应用提供了新的可能性。

**深层跨域联系**：

1. **流算法 ↔ 拓扑流**：数据流的"时间性"与拓扑中的流（flow）有概念相似性——都是沿时间/空间维度的信息传递

2. **多对数空间 ↔ 拓扑维度**：验证者的polylog空间复杂度与拓扑中的维度降低（dimension reduction）有深层联系——都涉及信息在减少表示维度时的保持

3. **信息理论 ↔ 范畴化**：零知识的"信息隐藏"与范畴化中的自然变换（natural transformation）有概念同构性——都研究结构保持的信息隐藏机制

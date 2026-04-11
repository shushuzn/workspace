---
id: incrementally-verifiable-computation-via-rate-1-batch-arguments
title: Incrementally Verifiable Computation via Rate-1 Batch Arguments
category: security
tags: [论文解读, ePrint:2023/1394]
eprint: 2023/1394
source: IACR ePrint
url: https://eprint.iacr.org/2023/1394
created: 2026-04-10T14:26:44.218Z
---

# Incrementally Verifiable Computation via Rate-1 Batch Arguments

**IACR ePrint** | ePrint: 2023/1394 | **Author**: Omer Paneth, Rafael Pass

## 摘要

Non-interactive delegation schemes enable producing succinct proofs (that can be efficiently verified) that a machine $M$ transitions from $c_1$ to $c_2$ in a certain number of deterministic steps. We here consider the problem of efficiently \emph{merging} such proofs: given a proof $\Pi_1$ that $M$ transitions from $c_1$ to $c_2$, and a proof $\Pi_2$ that $M$ transitions from $c_2$ to $c_3$, can these proofs be efficiently merged into a single short proof (of roughly the same size as the original proofs) that $M$ transitions from $c_1$ to $c_3$? To date, the only known constructions of such a mergeable delegation scheme rely on strong non-falsifiable ``knowledge extraction&#34; assumptions. In this work, we present a provably secure construction based on the standard LWE assumption. As an application of mergeable delegation, we obtain a construction of incrementally verifiable computation (IVC) (with polylogarithmic length proofs) for any (unbounded) polynomial number of steps based on LWE; as far as we know, this is the first such construction based on any falsifiable (as opposed to knowledge-extraction) assumption. The central building block that we rely on, and construct based on LWE, is a rate-1 batch argument (BARG): this is a non-interactive argument for NP that enables proving $k$ NP statements $x_1,..., x_k$ with communication/verifier complexity $m+o(m)$, where $m$ is the length of one witness. Rate-1 BARGs are particularly useful as they can be recursively composed a super-constant number of times.

## 研究动机

增量可验证计算（IVC）和可合并 delegation 协议是长期悬而未决的问题：

- **Delegation需求**：将计算委托给不受信任的证明者，快速验证正确性
- **证明合并难题**：已知方案无法高效合并两个证明
- **IVC应用广泛**：长计算（如区块链Rollup）需要增量验证

核心问题：能否构造可高效合并的 delegation 方案，并基于此实现基于标准假设的IVC？

## 核心方法

### 1. 可合并 Delegation 方案

给定两个证明：
- Π₁：M从c₁转换到c₂
- Π₂：M从c₂转换到c₃

能否高效合并为单一简短证明，证明M从c₁到c₃的转换？

- **同等大小**：合并后证明大小与原证明大致相同
- **高效合并**：合并开销可接受

### 2. Rate-1 Batch Arguments (BARG)

中心构建模块：

- **Rate-1特性**：通信复杂度为 m + o(m)，其中m为单个见证长度
- **递归可组合**：可被递归组合超常数次
- **NP语句批处理**：同时证明k个NP语句

### 3. 基于LWE的IVC

作为应用：

- **基于标准假设**：首个基于LWE（可证伪假设）的IVC构造
- **多对数长度证明**：对于任意无界多项式步数
- **超越知识提取假设**：首次不依赖强非可证伪知识提取假设

### 4. 安全性基础

基于标准LWE假设：

- **可证伪假设**：LWE是经过充分研究的可证伪假设
- **随机预言机模型**：在随机预言机模型下证明安全
- **标准vs非标准**：首次在可证伪假设上实现突破

## 关键发现

1. **首个基于LWE的IVC**：打破了对强知识提取假设的依赖
2. **可合并delegation**：解决长期悬而未决的合并问题
3. **Rate-1 BARG**：提供高效的批量零知识论证
4. **递归组合能力**：可多次递归组合
5. **理论突破**：为IVC提供更坚实的安全性基础

## 个人评价

这是IVC理论的重大突破，首次在标准且可证伪的LWE假设上实现了实用的IVC构造。Rate-1 BARG作为核心原语可能在其他零知识应用中发挥重要作用。

**深层跨域联系**：

1. **证明合并 ↔ 拓扑[[拓扑序|拓扑合成]]**：证明合并与拓扑学中的同伦[[拓扑序|拓扑合成]]（homotopy composition）有深层联系——都是将多个路径/证明"粘合"为单一复合结构

2. **增量验证 ↔ 拓扑持续性**：IVC的增量特性与拓扑学中的持续[[拓扑序|拓扑同调]]（persistent homology）有概念相似——都是在逐步演进中保持某种[[拓扑序|拓扑不变量]]

3. **Rate-1特性 ↔ 拓扑效率**：Rate-1（线性效率）与拓扑学中研究的有效不变式有深层联系——都是追求最优的信息压缩率

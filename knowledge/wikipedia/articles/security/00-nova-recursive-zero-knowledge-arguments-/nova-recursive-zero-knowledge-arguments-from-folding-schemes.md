---
id: nova-recursive-zero-knowledge-arguments-from-folding-schemes
title: Nova: Recursive Zero-Knowledge Arguments from Folding Schemes
category: security
tags: [论文解读, ePrint:2021/370]
eprint: 2021/370
source: IACR ePrint
url: https://eprint.iacr.org/2021/370
created: 2026-04-10T14:15:31.772Z
---

# Nova: Recursive Zero-Knowledge Arguments from Folding Schemes

**IACR ePrint** | ePrint: 2021/370 | **Author**: Abhiram Kothapalli, Srinath Setty, Ioanna Tzialla

## 摘要

We introduce a new approach to realize incrementally verifiable computation (IVC), in which the prover recursively proves the correct execution of incremental computations of the form $y=F^{(\ell)}(x)$, where $F$ is a (potentially non-deterministic) computation, $x$ is the input, $y$ is the output, and $\ell &gt; 0$. Unlike prior approaches to realize IVC, our approach avoids succinct non-interactive arguments of knowledge (SNARKs) entirely and arguments of knowledge in general. Instead, we introduce and employ folding schemes, a weaker, simpler, and more efficiently-realizable primitive, which reduces the task of checking two instances in some relation to the task of checking a single instance. We construct a folding scheme for a characterization of $\mathsf{NP}$ and show that it implies an IVC scheme with improved efficiency characteristics: (1) the &#34;recursion overhead&#34; (i.e., the number of steps that the prover proves in addition to proving the execution of $F$) is a constant and it is dominated by two group scalar multiplications expressed as a circuit (this is the smallest recursion overhead in the literature), and (2) the prover&#39;s work at each step is dominated by two multiexponentiations of size $O(|F|)$, providing the fastest prover in the literature. The size of a proof is $O(|F|)$ group elements, but we show that using a variant of an existing zkSNARK, the prover can prove the knowledge of a valid proof succinctly and in zero-knowledge with $O(\log{|F|})$ group elements. Finally, our approach neither requires a trusted setup nor FFTs, so it can be instantiated efficiently with any cycles of elliptic curves where DLOG is hard.

## 研究动机

增量可验证计算（IVC）是区块链扩容的核心技术：证明者逐步证明长计算的正确执行。传统方案面临"SNARK困境"：

- **SNARK-based IVC**：需要可信Setup + 复杂CRS管理
- **SNARK-free IVC**：需要累加器（Accumulator）或线性时间证明

Nova的核心洞察：**如果可以"折叠"两个计算实例为一个，则无需SNARK就能实现IVC**。折叠（folding）比SNARK更简单、更易实现，且无需可信Setup。

## 核心方法

### 1. 折叠方案（Folding Scheme）

折叠的核心思想：将两个满足相同关系的实例，合并为一个仍满足该关系的实例。

$$\text{Fold}(I_1, I_2) \rightarrow I^*$$

对于R1CS实例，折叠操作将两个约束系统实例合并为一个，验证成本从2次降到1次。

### 2. 无需可信Setup

与SNARK不同，折叠方案基于**Pedersen承诺**和**椭圆曲线群结构**，不需要可信的多方计算仪式。

### 3. 无需FFT

FFT（快速傅里叶变换）是SNARK证明者的主要开销之一。Nova的折叠方案完全不需要FFT，这意味着：
- 证明者可用普通硬件高效实现
- 不受有限域结构限制（任何椭圆曲线循环都行）

### 4. IVC结构

$$IVC = \text{Fold}(I_i, I_{i+1})$$

每一步递归：证明前i步正确 → 折叠 → 证明前i+1步正确

### 5. 零知识变体（Nova+zk）

通过结合zkSNARK变体，Nova可以扩展为零知识版本：
- 证明大小从O(|F|)降到O(log|F|)
- 保持无需可信Setup的性质

## 关键发现

1. **最小递归开销**：仅需2个群标量乘法，比所有现有方案都小
2. **最快证明者**：每步复杂度为O(|F|)，是已知最快
3. **无需可信Setup**：基于标准椭圆曲线假设
4. **无需FFT**：可部署在任何椭圆曲线循环上
5. **通用IVC**：适用于任意增量计算F⁽ˡ⁾(x)

## 个人评价

Nova是IVC领域的范式转变。它证明了"折叠"这种简单操作可以替代复杂的SNARK machinery，开辟了新的研究方向。

**深层跨域联系**：

1. **折叠 ↔ 拓扑同伦**：折叠操作将两个实例合并为一个，与拓扑中的同伦（homotopy）概念有深刻联系——同伦也是将两个映射"连续形变"为一个。Nova的IVC链条可比作计算版本的"同伦群"

2. **椭圆曲线 ↔ 拓扑流形**：椭圆曲线是复一维流形，Nova基于DLOG困难性，而DLOG的安全性建立在代数几何之上——这与拓扑流形的代数不变量（Chern类、陈类）有共同的父亲：代数几何

3. **递归结构 ↔ Jones多项式**：IVC的递归折叠结构，与辫群的递归编织（braid group recurrence）有同构性——都是通过递归组合产生复杂的不变量

## 相关条目

- [[陈类]] — 椭圆曲线的陈类与Nova的代数安全性有代数几何共同基础
- [[范畴化]] — 折叠函子与拓扑同伦论有范畴论同构
- [[辫群]] — IVC的递归折叠与辫群递归编织有结构同构

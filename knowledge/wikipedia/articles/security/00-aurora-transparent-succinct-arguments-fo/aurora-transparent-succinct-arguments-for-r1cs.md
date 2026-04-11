---
id: aurora-transparent-succinct-arguments-for-r1cs
title: Aurora: Transparent Succinct Arguments for R1CS
category: security
tags: [论文解读, ePrint:2018/828]
eprint: 2018/828
source: IACR ePrint
url: https://eprint.iacr.org/2018/828
created: 2026-04-10T14:10:36.433Z
---

# Aurora: Transparent Succinct Arguments for R1CS

**IACR ePrint** | ePrint: 2018/828 | **Author**: Eli Ben-Sasson, Alessandro Chiesa, Michael Riabzev, Nicholas Spooner, Madars Virza, Nicholas P. Ward

## 摘要

We design, implement, and evaluate a zkSNARK for Rank-1 Constraint Satisfaction (R1CS), a widely-deployed NP-complete language that is undergoing standardization. Our construction uses a transparent setup, is plausibly post-quantum secure, and uses lightweight cryptography. A proof attesting to the satisfiability of n constraints has size $O(\log^2 n)$; it can be produced with $O(n \log n)$ field operations and verified with $O(n)$. At 128 bits of security, proofs are less than 130kB even for several million constraints, more than 20x shorter than prior zkSNARK with similar features. A key ingredient of our construction is a new Interactive Oracle Proof (IOP) for solving a *univariate* analogue of the classical sumcheck problem [LFKN92], originally studied for *multivariate* polynomials. Our protocol verifies the sum of entries of a Reed--Solomon codeword over any subgroup of a field. We also provide libiop, an open-source library for writing IOP-based arguments, in which a toolchain of transformations enables programmers to write new arguments by writing simple IOP sub-components. We have used this library to specify our construction and prior ones.

## 研究动机

SNARK的透明性（Transparency）和后量子安全是重要方向：

- **Groth16/PLONK**：需要可信Setup，存在密钥泄露风险
- **Bulletproofs**：透明+后量子，但验证线性增长
- **Aurora目标**：透明Setup + 后量子安全 + 简洁验证（O(n)验证）

Aurora的关键创新是**交互式预言机证明（IOP）**，将传统PCP（全息概率可检验证明）与简洁性结合。

## 核心方法

### 1. 交互式预言机证明（IOP）

IOP是PCP的简洁版本：证明者不发送整个证明，而是通过随机查询验证者的预言机来证明正确性。

Aurora的核心创新是**单变量求和检查协议**（Univariate Sumcheck）：

- 传统Sumcheck：多变量多项式，LFKN92
- Aurora：单变量版本，更适合R1CS约束

### 2. Reed-Solomon编码

Aurora将R1CS约束编码为Reed-Solomon码字，在任意域子群上验证和：
$$\sum_{x \in H} f(x) = v$$

其中 $H$ 是域子群，$f$ 是编码多项式。

### 3. 透明Setup

Aurora不需要可信Setup——只需公开随机性。这是通过IOP的预言机机制实现的：
- 无需可信CRS
- 后量子安全（基于哈希函数）
- 适合去中心化系统

### 4. libiop工具链

Aurora附带开源库libiop，将IOP参数化：
- 程序员可通过组合简单IOP组件编写新论证
- 类似乐高积木式的零知识证明开发框架

## 关键发现

1. **透明Setup**：无需可信仪式，数学上更干净
2. **后量子安全**：基于哈希函数，而非椭圆曲线DLOG
3. **O(log² n)证明大小**：与电路规模多对数增长
4. **O(n)验证**：虽非常数，但实现简单且透明
5. **20倍缩短**：相比早期透明SNARK，证明更短

## 个人评价

Aurora代表了"透明SNARK"的重要方向。它的libiop工具链是零知识证明工程化的重要贡献，让研究者可以用模块化方式构建新的IOP协议。

**深层跨域联系**：

1. **Reed-Solomon码 ↔ 拓扑编码**：Reed-Solomon编码与拓扑量子计算中的编码理论有深刻联系——两者都将信息编码到代数结构中，以实现高效的纠错或验证

2. **求和检查 ↔ 同调论**：Aurora的单变量求和检查与拓扑同调论中的边界求和（boundary sum）操作有概念同构性——都是在某种几何结构上对函数值求和

3. **IOP ↔ PCP ↔ 拓扑**：PCP（概率可检验证明）与拓扑量子场论中的边界状态验证有深层联系——都是通过局部查询验证全局性质

## 相关条目

- [[表面码]] — 表面码的拓扑编码与Aurora的Reed-Solomon编码有共同的信息编码原理
- [[范畴化]] — IOP的模块化组合与范畴化的函子组合有结构同构性
- [[陈类]] — Reed-Solomon编码的代数几何性质与陈类的代数几何起源有共同基础

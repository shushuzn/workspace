---
id: caulk-lookup-arguments-in-sublinear-time
title: Caulk: Lookup Arguments in Sublinear Time
category: security
tags: [论文解读, ePrint:2022/621]
eprint: 2022/621
source: IACR ePrint
url: https://eprint.iacr.org/2022/621
created: 2026-04-10T14:15:35.360Z
---

# Caulk: Lookup Arguments in Sublinear Time

**IACR ePrint** | ePrint: 2022/621 | **Author**: Arantxa Zapico, Vitalik Buterin, Dmitry Khovratovich, Mary Maller, Anca Nitulescu, Mark Simkin

## 摘要

We present position-hiding linkability for vector commitment schemes: one can prove in zero knowledge that one or $m$ values that comprise commitment cm all belong to the vector of size $N$ committed to in C. Our construction Caulk can be used for membership proofs and lookup arguments and outperforms all existing alternatives in prover time by orders of magnitude. For both single- and multi-membership proofs Caulk beats SNARKed Merkle proofs by the factor of 100 even if the latter instantiated with Poseidon hash. Asymptotically our prover needs $O(m^2 + m\log N)$ time to prove a batch of $m$ openings, whereas proof size is $O(1)$ and verifier time is $O(\log(\log N))$. As a lookup argument, Caulk is the first scheme with prover time sublinear in the table size, assuming $O(N\log N)$ preprocessing time and $O(N)$ storage. It can be used as a subprimitive in verifiable computation schemes in order to drastically decrease the lookup overhead. Our scheme comes with a reference implementation and benchmarks.

## 研究动机

查找论证（Lookup Argument）是零知识证明中的基础原语：证明某个值属于一个已知集合。在以太坊等区块链中，这是隐私保护计算的关键。

传统方案的困境：
- **Merkle树+SNARK**：O(log N)验证，但证明者是O(N)的
- **多项式承诺**：需要将查找表编码为多项式，开销大
- **Caulk目标**： prover time亚线性 + O(1)证明大小 + O(log log N)验证

## 核心方法

### 1. 向量承诺方案

Caulk基于**向量承诺**（Vector Commitment）：可以承诺一个向量V，长度为N，然后以O(1)大小证明任意位置的值。

关键性质：**位置隐藏链接性**（position-hiding linkability）：可以证明m个值都属于承诺向量，而不暴露它们的位置或彼此关系。

### 2. 查找论证的亚线性证明

传统方法：证明者需要处理整个表（O(N)）

Caulk的创新：通过预处理将表编码为多项式，然后：
- **预处理**：O(N log N)时间 + O(N)存储
- **证明时间**：O(m² + m log N)（m=查找值数量）
- **证明大小**：O(1)
- **验证时间**：O(log log N)

### 3. 与SNARKed Merkle对比

Caulk在性能上碾压SNARKed Merkle：
- 证明时间快**100倍**（即使Poseidon哈希优化后）
- 单成员和多成员证明都大幅领先

### 4. 应用场景

- **隐私保护**：证明某个值在许可列表中而不暴露具体值
- **Verifiable Computation**：在可验证计算中作为子模块降低查找开销
- **以太坊无状态客户端**：证明状态访问的正确性

## 关键发现

1. **首个亚线性查找论证**：证明时间sublinear in table size
2. **100倍提速**：相比SNARKed Merkle
3. **O(1)证明大小**：与表大小无关
4. **O(log log N)验证**：极快的验证速度
5. **零知识位置隐藏**：可证明成员关系而不暴露位置

## 个人评价

Caulk是零知识证明工程化的重要进步。它将查找论证从"实用但慢"带入"高效亚线性"时代，对以太坊无状态客户端和隐私保护应用有重要意义。

**深层跨域联系**：

1. **向量承诺 ↔ 拓扑不变性**：向量承诺将信息绑定到位置，与拓扑中的不变量有相似性——都是通过某种"编码"将语义信息与具体表示分离

2. **亚线性算法 ↔ 计算复杂性**：Caulk的亚线性证明与拓扑量子计算中的快速算法有共同关注点——都是在资源受限下寻找高效方案

3. **零知识 ↔ 范畴化**：零知识证明的"知识隐藏"与范畴化中的函子性有深层联系——都是研究结构如何在变换中保持信息

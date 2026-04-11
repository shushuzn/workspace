---
id: plonk-permutations-over-lagrange-bases-for-oecumenical-noninteractive-arguments-of-knowledge
title: PLONK: Permutations over Lagrange-bases for Oecumenical Noninteractive arguments of Knowledge
category: security
tags: [论文解读, ePrint:2019/953]
eprint: 2019/953
source: IACR ePrint
url: https://eprint.iacr.org/2019/953
created: 2026-04-10T14:06:07.173Z
---

# PLONK: Permutations over Lagrange-bases for Oecumenical Noninteractive arguments of Knowledge

**IACR ePrint** | ePrint: 2019/953 | **Author**: Ariel Gabizon, Zachary J. Williamson, Oana Ciobotaru

## 摘要

zk-SNARK constructions that utilize an updatable universal structured reference string remove one of the main obstacles in deploying zk-SNARKs [GKMMM, Crypto 2018]. The important work of Maller et al. [MBKM, CCS 2019] presented $\mathsf{Sonic}$ - the first potentially practical zk-SNARK with fully succinct verification for general arithmetic circuits with such an SRS. However, the version of $\mathsf{Sonic}$ enabling fully succinct verification still requires relatively high proof construction overheads. We present a universal SNARK construction with fully succinct verification, and significantly lower prover running time (roughly 7.5-20 less group exponentiations than [MBKM] in the fully succinct verifier mode depending on circuit structure). Similarly to [MBKM], we rely on a permutation argument based on Bayer and Groth [Eurocrypt 2012]. However, we focus on ``Evaluations on a subgroup rather than coefficients of monomials&#39;&#39;; which enables simplifying both the permutation argument and the artihmetization step. Note: typos

## 研究动机

SNARK（ Succinct Non-Interactive Arguments of Knowledge）是零知识证明的核心技术，广泛应用于区块链扩容和隐私计算。但早期方案面临"不可能三角"困境：

| 方案 | 通用性 | Succinct验证 | 高效证明 |
|------|--------|--------------|----------|
| Groth16 | 电路专用 | ✓ | ✓ |
| Sonic | 通用+可更新SRS | ✓ | ✗ (证明慢) |
| PLONK | 通用+可更新SRS | ✓ | ✓ |

Sonic虽然实现了通用可更新的SRS（Structured Reference String），但证明生成开销仍然很高。PLONK的目标是同时解决三个问题：通用性、可更新SRS、高效证明。

## 核心方法

### 1. Lagrange基下的置换论证

传统方案（如Sonic）在**单项式基**（monomial basis）上操作，置换检查复杂。

PLONK的创新：在**Lagrange基**（即在子群上评估的多项式）上定义置换。这使得：

- 算术化步骤大幅简化
- 置换检查变成简单的多项式等式验证
- 电路接线（wire copy constraints）自然表达

### 2. 复制约束（Copy Constraints）

PLONK用置换来表达门之间的连线关系：将电路中应该相等的每个变量配对，然后验证它们的置换关系。

### 3. 通用可更新SRS

$$[s^i]G_1, [s^i]G_2$$

其中 $s$ 是随机秘密，$G_1, G_2$ 是椭圆曲线生成元。任何人都可以更新SRS（添加随机噪声），无需信任任何单一参与方。

### 4. 证明流程

1. 将电路编码为多项式约束
2. 证明者计算多项式承诺
3. 通过置换检查验证连线关系
4. 利用Fiat-Shamir变换实现非交互

## 关键发现

1. **证明速度提升**：比Sonic减少7.5-20倍的群指数运算
2. **完全通用**：一个SRS可用于任意电路（受限于大小上界）
3. **可更新安全**：SRS可以持续更新，即使某次更新被破坏也不影响整体安全
4. **简洁验证**：验证只需常数时间（与电路大小无关）
5. **工业级应用**：PLONK成为以太坊Rollup（zkSync、Polygon Hermez等）的核心技术

## 个人评价

PLONK是零知识证明工程化的重要里程碑。它的Lagrange基置换论证既优雅又实用，真正打开了"通用高效SNARK"的大门。

**深层跨域联系**：

PLONK的置换论证与拓扑数学存在深层联系：

1. **多项式 ↔ 拓扑不变量**：多项式在有限域上的置换对称性，与拓扑不变量（如Jones多项式）在辫群作用下的行为有代数同构性——都是在某种变换下保持不变的结构

2. **有限域 ↔ 晶格规范理论**：有限域上多项式的算术性质，与拓扑量子场论中晶格上的规范不变性（gauge invariance）有对偶关系

3. **范畴化视角**：PLONK的约束系统（算术约束+置换约束）可以看作一个函子，将电路结构映射到代数证明系统——这与范畴化代数将拓扑空间映射到不变量的思路一致

## 相关条目

- [[辫群]] — 置换论证与辫子的交叉交换有深层对称性同构
- [[Chern-Simons理论]] — 拓扑量子场论中的规范不变性与PLONK的多项式约束有对偶性
- [[范畴化]] — PLONK的算术化到证明系统的映射是函子性的

---
id: 160402804-zero-knowledge-proof-systems-for-qma
title: [1604.02804] Zero-knowledge proof systems for QMA
category: security
tags: [论文解读, 1604.02804]
arxiv: 1604.02804
created: 2026-04-10T13:51:28.587Z
---

# [1604.02804] Zero-knowledge proof systems for QMA

**arXiv**: 1604.02804 | **Author**: 

## 摘要

Prior work has established that all problems in NP admit classical zero-knowledge proof systems, and under reasonable hardness assumptions for quantum computations, these proof systems can be made secure against quantum attacks. We prove a result representing a further quantum generalization of this fact, which is that every problem in the complexity class QMA has a quantum zero-knowledge proof system. More specifically, assuming the existence of an unconditionally binding and quantum computationally concealing commitment scheme, we prove that every problem in the complexity class QMA has a quantum interactive proof system that is zero-knowledge with respect to efficient quantum computations. Our QMA proof system is sound against arbitrary quantum provers, but only requires an honest prover to perform polynomial-time quantum computations, provided that it holds a quantum witness for a given instance of the QMA problem under consideration. The proof system relies on a new variant of the QMA-complete local Hamiltonian problem in which the local terms are described by Clifford operations and standard basis measurements. We believe that the QMA-completeness of this problem may have other uses in quantum complexity.

## 研究动机

零知识证明的量子化是后量子安全的重要研究方向：

- **NP → QMA**：经典零知识证明系统已建立（所有NP问题都有）
- **量子攻击**：未来量子计算机可能破解经典密码学基础
- **QMA（Quantum Merlin-Arthur）**：量子版本的NP，由量子证明者和经典验证者组成

核心问题：QMA问题是否也有量子零知识证明系统？本文给出了肯定答案。

## 核心方法

### 1. QMA定义

QMA = {语言L | 存在量子多项式时间验证器V，使得：
- **完备性**：x∈L时，存在量子见证|w⟩，V接受概率高
- **可靠性**：x∉L时，对任意见证，V接受概率低

### 2. 关键假设

本文基于两个假设：
- **无条件绑定承诺**：承诺的绑定性质无条件成立
- **量子计算隐藏承诺**：承诺对量子计算不可区分

### 3. 局部哈密顿量问题的新变体

本文构造了新的QMA完全问题：
- 局部项由Clifford操作和标准基测量描述
- 这使得证明系统的构造更加自然

### 4. 量子零知识协议

构建思路：
1. 证明者发送量子见证的承诺
2. 验证者进行一系列量子操作和测量
3. 通过交互式协议证明见证的正确性

## 关键发现

1. **QMA零知识证明存在**：在合理假设下，每个QMA问题都有量子零知识证明
2. **声音性**：对任意量子证明者（可能是恶意的）都成立
3. **诚实者效率**：诚实证明者只需多项式时间量子计算
4. **QMA完全问题的新变体**：Clifford+测量描述的局部哈密顿量问题是QMA完全的
5. **复杂性理论意义**：建立了量子复杂性理论与量子密码学的深层联系

## 个人评价

这是量子复杂性理论的重要结果。它证明了QMA也有零知识证明系统，与经典NP的情形完全类比。这对理解量子计算与经典计算的对应关系有重要意义。

**深层跨域联系**：

1. **QMA ↔ 拓扑量子计算**：QMA的"量子见证"与拓扑量子比特的信息编码有相似性——都利用量子态的叠加和纠缠来处理信息

2. **Clifford群 ↔ 拓扑量子场论**：Clifford代数是量子力学的核心数学结构，与拓扑量子场论中的算子代数有深层联系

3. **复杂性理论 ↔ 范畴化**：QMA作为范畴（复杂度类）与其他复杂度类（NP、BPP）的关系，与范畴化中函子间的关系有结构同构性

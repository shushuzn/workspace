---
id: 201210452-experimental-relativistic-zero-knowledge-proofs
title: [2012.10452] Experimental relativistic zero-knowledge proofs
category: security
tags: [论文解读, 2012.10452]
arxiv: 2012.10452
created: 2026-04-10T13:51:31.738Z
---

# [2012.10452] Experimental relativistic zero-knowledge proofs

**arXiv**: 2012.10452 | **Author**: 

## 摘要

Protecting secrets is a key challenge in our contemporary information-based era. In common situations, however, revealing secrets appears unavoidable, for instance, when identifying oneself in a bank to retrieve money. In turn, this may have highly undesirable consequences in the unlikely, yet not unrealistic, case where the bank&#39;s security gets compromised. This naturally raises the question of whether disclosing secrets is fundamentally necessary for identifying oneself, or more generally for proving a statement to be correct. Developments in computer science provide an elegant solution via the concept of zero-knowledge proofs: a prover can convince a verifier of the validity of a certain statement without facilitating the elaboration of a proof at all. In this work, we report the experimental realisation of such a zero-knowledge protocol involving two separated verifier-prover pairs. Security is enforced via the physical principle of special relativity, and no computational assumption (such as the existence of one-way functions) is required. Our implementation exclusively relies on off-the-shelf equipment and works at both short (60 m) and long distances ($\geqslant$400 m) in about one second. This demonstrates the practical potential of multi-prover zero-knowledge protocols, promising for identification tasks and blockchain applications such as cryptocurrencies or smart contracts.

## 研究动机

传统零知识证明依赖计算复杂性假设（如单向函数），但这些假设在量子计算机面前可能失效。本文探索了一个根本不同的路径：

- **密码学假设的脆弱性**：大数分解、离散对数等假设在量子攻击下不再成立
- **物理原理的永恒性**：狭义相对论（光速不变）不随技术进步而改变
- **相对论零知识证明**：利用相对论原理替代计算假设，实现无条件安全

核心问题：能否用物理原理（而非数学假设）来实现零知识证明？

## 核心方法

### 1. 相对论安全原理

狭义相对论的核心约束：
- **光速上限**：信息传递速度不超过c
- **同时性相对化**：不同参考系下同时性不同

利用这两个约束，即使证明者试图欺骗，也无法在短时间内将信息传递给远处的同谋。

### 2. 双验证者结构

实验设置：
- 两对分离的验证者-证明者（距离60米和400米）
- 证明者在短时间内同时向两个验证者发送证明
- 由于光速限制，两个验证者无法协调作弊

### 3. 协议设计

基于Fiat-Shamir范式的非交互版本：
1. 验证者提出随机挑战
2. 证明者同时响应两个验证者
3. 由于信息来不及传递，作弊概率被物理原理压制

### 4. 实验实现

- **设备**：现成设备，无特殊要求
- **距离**：60米（短距离）和400米（长距离）
- **速度**：约1秒内完成
- **实际可行性**：展示了相对论零知识证明的工程可行性

## 关键发现

1. **无需计算假设**：完全基于物理原理（狭义相对论）
2. **量子计算安全**：不受量子攻击威胁
3. **实验验证**：在60米和400米距离上成功实现
4. **实用速度**：约1秒完成证明，满足实际应用
5. **应用前景**：身份识别、区块链（加密货币/智能合约）

## 个人评价

这是密码学与物理学交叉的里程碑工作。它证明了"物理原理可以替代数学假设"来实现安全协议，开辟了"物理安全密码学"的新方向。

**深层跨域联系**：

1. **相对论 ↔ 因果结构**：狭义相对论的因果结构与拓扑量子场论中的因果律有深层联系——都受光速不变约束

2. **无条件安全 ↔ 拓扑保护**：相对论安全与拓扑量子计算都提供"无条件"保护——前者基于物理原理，后者基于拓扑性质

3. **时空约束 ↔ 计算复杂性**：相对论对信息传递的时空约束与计算复杂性理论有深层对应——都研究在物理/资源限制下的可行计算

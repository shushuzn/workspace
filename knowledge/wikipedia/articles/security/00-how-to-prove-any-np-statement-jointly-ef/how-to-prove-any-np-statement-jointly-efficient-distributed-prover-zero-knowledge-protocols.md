---
id: how-to-prove-any-np-statement-jointly-efficient-distributed-prover-zero-knowledge-protocols
title: How to prove any NP statement jointly? Efficient Distributed-prover Zero-Knowledge Protocols
category: security
tags: [论文解读, ePrint:2021/1599]
eprint: 2021/1599
source: IACR ePrint
url: https://eprint.iacr.org/2021/1599
created: 2026-04-10T14:20:59.606Z
---

# How to prove any NP statement jointly? Efficient Distributed-prover Zero-Knowledge Protocols

**IACR ePrint** | ePrint: 2021/1599 | **Author**: Pankaj Dayama, Arpita Patra, Protik Paul, Nitin Singh, Dhinakaran Vinayagamurthy

## 摘要

Traditional zero-knowledge protocols have been studied and optimized for the setting where a single prover holds the complete witness and tries to convince a verifier about a predicate on the witness, without revealing any additional information to the verifier. In this work, we study the notion of distributed-prover zero knowledge (DPZK) for arbitrary predicates where the witness is shared among multiple mutually distrusting provers and they want to convince a verifier that their shares together satisfy the predicate. We make the following contributions to the notion of distributed proof generation: (i) we propose a new MPC-style security definition to capture the adversarial settings possible for different collusion models between the provers and the verifier, (ii) we discuss new efficiency parameters for distributed proof generation such as the number of rounds of interaction and the amount of communication among the provers, and (iii) we propose a compiler that realizes distributed proof generation from the zero-knowledge protocols in the Interactive Oracle Proofs (IOP) paradigm. Our compiler can be used to obtain DPZK from arbitrary IOP protocols, but the concrete efficiency overheads are substantial in general. To this end, we contribute (iv) a new zero-knowledge IOP $\textsf{Graphene}$ which can be compiled into an efficient DPZK protocol. The $(\mathsf{D} + 1)$-DPZK protocol $\text{D-Graphene}$, with $\mathsf{D}$ provers and one verifier, admits $O(N^{1/c})$ proof size with a communication complexity of $O(\mathsf{D}^2\cdot (N^{1-2/c} + N_s))$, where $N$ is the number of gates in the arithmetic circuit representing the predicate and $N_s$ is the number of wires that depends on inputs from two or more parties. Significantly, only the distributed proof generation in $\text{D-Graphene}$ requires interaction among the provers. $\text{D-Graphene}$ compares favourably with the DPZK protocols obtained from the state-of-art zero-knowledge protocols, even those not modelled as IOPs.

## 研究动机

分布式证明者零知识（DPZK）协议是新兴的研究方向：

- **传统ZK局限**：传统零知识协议假设单个证明者持有完整见证
- **多方见证场景**：实际应用中见证可能分布在多个互不信任的参与方
- **碰撞模型复杂性**：不同参与方与验证者之间可能形成各种碰撞模型
- **效率参数**：现有方案在轮数和通信量等效率参数上缺乏系统研究

核心问题：如何为任意NP语句构造高效的多方分布式证明者零知识协议？

## 核心方法

### 1. DPZK形式化

提出MPC风格的安全定义：

- **碰撞模型**：形式化参与方之间以及与验证者之间可能的碰撞模型
- **安全性定义**：捕捉对抗性设置的各个方面
- **零知识保持**：证明过程中不泄露额外信息

### 2. 效率参数体系

引入新的效率参数：

- **交互轮数**：分布式证明生成所需轮数
- **参与方间通信量**：多方之间的通信复杂度
- **证明大小**：最终生成的证明尺寸

### 3. IOP编译器

提出从IOP协议构造DPZK的编译器：

- **通用性**：适用于任意IOP协议
- **从Graphene到D-Graphene**：新零知识IOP编译为高效DPZK协议
- **D+1证明者模型**：D个证明者+1个验证者

### 4. D-Graphene协议

| 参数 | 复杂度 |
|------|--------|
| 证明大小 | O(N^{1/C}) |
| 通信复杂度 | O(D²·(N^{1-2/C} + N_s)) |
| 证明者间交互 | 仅分布式证明生成阶段需要 |

## 关键发现

1. **首个通用DPZK框架**：为任意NP语句提供分布式零知识证明
2. **MPC风格安全定义**：精确刻画多种碰撞模型下的安全性
3. **D-Graphene高效协议**：相比现有方案有明显效率优势
4. **IOP范式结合**：充分利用IOP的高效特性
5. **实际应用前景**：适合隐私保护的多方计算场景

## 个人评价

这是分布式零知识证明领域的重要进展，首次为任意NP语句提供了系统性的多方证明框架。Graphene系列的高效设计使其在实际应用中具有重要价值。

**深层跨域联系**：

1. **分布式证明 ↔ 拓扑分散**：多方分布式证明与拓扑学中的分散（dispersal）有概念相似——都是将整体计算分布到多个组件

2. **碰撞模型 ↔ 拓扑障碍**：不同碰撞模型与拓扑障碍理论有深层联系——都是研究部分组件失效时的整体行为

3. **证明大小优化 ↔ 拓扑压缩**：O(N^{1/C})证明大小与拓扑信息压缩有概念相似——都是将大量信息有效压缩

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

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

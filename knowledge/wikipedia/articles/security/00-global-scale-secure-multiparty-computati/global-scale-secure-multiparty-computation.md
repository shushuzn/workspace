---
id: global-scale-secure-multiparty-computation
title: Global-Scale Secure Multiparty Computation
category: security
tags: [论文解读, ePrint:2017/189]
eprint: 2017/189
source: IACR ePrint
url: https://eprint.iacr.org/2017/189
created: 2026-04-10T14:31:08.063Z
---

# Global-Scale Secure Multiparty Computation

**IACR ePrint** | ePrint: 2017/189 | **Author**: Xiao Wang, Samuel Ranellucci, Jonathan Katz

## 摘要

We propose a new, constant-round protocol for multi-party computation of boolean circuits that is secure against an arbitrary number of malicious corruptions. At a high level, we extend and generalize recent work of Wang et al. in the two-party setting and design an efficient preprocessing phase that allows the parties to generate authenticated information; we then show how to use this information to distributively construct a single ``authenticated&#39;&#39; garbled circuit that is evaluated by one party. Our resulting protocol improves upon the state-of-the-art both asymptotically and concretely. We validate these claims via several experiments demonstrating both the efficiency and scalability of our protocol: - Efficiency: For three-party computation over a LAN, our protocol requires only 95 ms to evaluate AES. This is roughly a 700$\times$ improvement over the best prior work, and only 2.5$\times$ slower than the best known result in the two-party setting. In general, for $n$ parties our protocol improves upon prior work (which was never implemented) by a factor of more than $230n$, e.g., an improvement of 3 orders of magnitude for 5-party computation. - Scalability: We successfully executed our protocol with a large number of parties located all over the world, computing (for example) AES with 128 parties across 5 continents in under 3 minutes. Our work represents the largest-scale demonstration of secure computation to date.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

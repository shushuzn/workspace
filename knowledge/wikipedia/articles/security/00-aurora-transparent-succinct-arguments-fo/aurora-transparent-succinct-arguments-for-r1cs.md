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

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

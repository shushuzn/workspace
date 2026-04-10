---
id: simple-verifiable-delay-functions
title: Simple Verifiable Delay Functions
category: security
tags: [论文解读, ePrint:2018/627]
eprint: 2018/627
source: IACR ePrint
url: https://eprint.iacr.org/2018/627
created: 2026-04-10T14:41:47.305Z
---

# Simple Verifiable Delay Functions

**IACR ePrint** | ePrint: 2018/627 | **Author**: Krzysztof Pietrzak

## 摘要

We construct a verifable delay function (VDF) by showing how the Rivest-Shamir-Wagner time-lock puzzle can be made publicly verifiable. Concretely, we give a statistically sound public-coin protocol to prove that a tuple $(N,x,T,y)$ satisfies $y=x^{2^T}\pmod N$ where the prover doesn&#39;t know the factorization of $N$ and its running time is dominated by solving the puzzle, that is, compute $x^{2^T}$, which is conjectured to require $T$ sequential squarings. To get a VDF we make this protocol non-interactive using the Fiat-Shamir heuristic. The motivation for this work comes from the Chia blockchain design, which uses a VDF as a key ingredient. For typical parameters ($T\le 2^{40},N=2048$), our proofs are of size around $10KB$, verification cost around three RSA exponentiations and computing the proof is $8000$ times faster than solving the puzzle even without any parallelism.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

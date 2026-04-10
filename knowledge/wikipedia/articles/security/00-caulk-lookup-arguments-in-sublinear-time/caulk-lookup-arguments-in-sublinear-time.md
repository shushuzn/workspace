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

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

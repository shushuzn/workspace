---
id: nova-recursive-zero-knowledge-arguments-from-folding-schemes
title: Nova: Recursive Zero-Knowledge Arguments from Folding Schemes
category: security
tags: [论文解读, ePrint:2021/370]
eprint: 2021/370
source: IACR ePrint
url: https://eprint.iacr.org/2021/370
created: 2026-04-10T14:15:31.772Z
---

# Nova: Recursive Zero-Knowledge Arguments from Folding Schemes

**IACR ePrint** | ePrint: 2021/370 | **Author**: Abhiram Kothapalli, Srinath Setty, Ioanna Tzialla

## 摘要

We introduce a new approach to realize incrementally verifiable computation (IVC), in which the prover recursively proves the correct execution of incremental computations of the form $y=F^{(\ell)}(x)$, where $F$ is a (potentially non-deterministic) computation, $x$ is the input, $y$ is the output, and $\ell &gt; 0$. Unlike prior approaches to realize IVC, our approach avoids succinct non-interactive arguments of knowledge (SNARKs) entirely and arguments of knowledge in general. Instead, we introduce and employ folding schemes, a weaker, simpler, and more efficiently-realizable primitive, which reduces the task of checking two instances in some relation to the task of checking a single instance. We construct a folding scheme for a characterization of $\mathsf{NP}$ and show that it implies an IVC scheme with improved efficiency characteristics: (1) the &#34;recursion overhead&#34; (i.e., the number of steps that the prover proves in addition to proving the execution of $F$) is a constant and it is dominated by two group scalar multiplications expressed as a circuit (this is the smallest recursion overhead in the literature), and (2) the prover&#39;s work at each step is dominated by two multiexponentiations of size $O(|F|)$, providing the fastest prover in the literature. The size of a proof is $O(|F|)$ group elements, but we show that using a variant of an existing zkSNARK, the prover can prove the knowledge of a valid proof succinctly and in zero-knowledge with $O(\log{|F|})$ group elements. Finally, our approach neither requires a trusted setup nor FFTs, so it can be instantiated efficiently with any cycles of elliptic curves where DLOG is hard.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

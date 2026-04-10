---
id: incrementally-verifiable-computation-via-rate-1-batch-arguments
title: Incrementally Verifiable Computation via Rate-1 Batch Arguments
category: security
tags: [论文解读, ePrint:2023/1394]
eprint: 2023/1394
source: IACR ePrint
url: https://eprint.iacr.org/2023/1394
created: 2026-04-10T14:26:44.218Z
---

# Incrementally Verifiable Computation via Rate-1 Batch Arguments

**IACR ePrint** | ePrint: 2023/1394 | **Author**: Omer Paneth, Rafael Pass

## 摘要

Non-interactive delegation schemes enable producing succinct proofs (that can be efficiently verified) that a machine $M$ transitions from $c_1$ to $c_2$ in a certain number of deterministic steps. We here consider the problem of efficiently \emph{merging} such proofs: given a proof $\Pi_1$ that $M$ transitions from $c_1$ to $c_2$, and a proof $\Pi_2$ that $M$ transitions from $c_2$ to $c_3$, can these proofs be efficiently merged into a single short proof (of roughly the same size as the original proofs) that $M$ transitions from $c_1$ to $c_3$? To date, the only known constructions of such a mergeable delegation scheme rely on strong non-falsifiable ``knowledge extraction&#34; assumptions. In this work, we present a provably secure construction based on the standard LWE assumption. As an application of mergeable delegation, we obtain a construction of incrementally verifiable computation (IVC) (with polylogarithmic length proofs) for any (unbounded) polynomial number of steps based on LWE; as far as we know, this is the first such construction based on any falsifiable (as opposed to knowledge-extraction) assumption. The central building block that we rely on, and construct based on LWE, is a rate-1 batch argument (BARG): this is a non-interactive argument for NP that enables proving $k$ NP statements $x_1,..., x_k$ with communication/verifier complexity $m+o(m)$, where $m$ is the length of one witness. Rate-1 BARGs are particularly useful as they can be recursively composed a super-constant number of times.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

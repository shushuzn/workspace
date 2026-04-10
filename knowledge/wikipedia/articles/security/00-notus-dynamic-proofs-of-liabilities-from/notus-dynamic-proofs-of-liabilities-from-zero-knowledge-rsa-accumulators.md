---
id: notus-dynamic-proofs-of-liabilities-from-zero-knowledge-rsa-accumulators
title: Notus: Dynamic Proofs of Liabilities from Zero-knowledge RSA Accumulators
category: security
tags: [论文解读, ePrint:2024/395]
eprint: 2024/395
source: IACR ePrint
url: https://eprint.iacr.org/2024/395
created: 2026-04-10T14:26:48.294Z
---

# Notus: Dynamic Proofs of Liabilities from Zero-knowledge RSA Accumulators

**IACR ePrint** | ePrint: 2024/395 | **Author**: Jiajun Xin, Arman Haghighi, Xiangan Tian, Dimitrios Papadopoulos

## 摘要

Proofs of Liabilities (PoL) allow an untrusted prover to commit to its liabilities towards a set of users and then prove independent users&#39; amounts or the total sum of liabilities, upon queries by users or third-party auditors. This application setting is highly dynamic. User liabilities may increase/decrease arbitrarily and the prover needs to update proofs in epoch increments (e.g., once a day for a crypto-asset exchange platform). However, prior works mostly focus on the static case and trivial extensions to the dynamic setting open the system to windows of opportunity for the prover to under-report its liabilities and rectify its books in time for the next check, unless all users check their liabilities at all epochs. In this work, we develop Notus, the first dynamic PoL system for general liability updates that avoids this issue. Moreover, it achieves $O(1)$ query proof size, verification time, and auditor overhead-per-epoch. The core building blocks underlying Notus are a novel zero-knowledge (and SNARK-friendly) RSA accumulator and a corresponding zero-knowledge MultiSwap protocol, which may be of independent interest. We then propose optimizations to reduce the prover&#39;s update overhead and make Notus scale to large numbers of users ($10^6$ in our experiments). Our results are very encouraging, e.g., it takes less than $2$ms to verify a user&#39;s liability and the proof size is $256$ Bytes. On the prover side, deploying Notus on a cloud-based testbed with eight 32-core machines and exploiting parallelism, it takes ${\sim}3$ minutes to perform the complete epoch update, after which all proofs have already been computed. Note: This is the full version of our publication. We made minor modifications to the security definitions.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

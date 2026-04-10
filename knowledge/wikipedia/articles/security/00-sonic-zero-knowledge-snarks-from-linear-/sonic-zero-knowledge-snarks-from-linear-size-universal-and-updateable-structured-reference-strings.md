---
id: sonic-zero-knowledge-snarks-from-linear-size-universal-and-updateable-structured-reference-strings
title: Sonic: Zero-Knowledge SNARKs from Linear-Size Universal and Updateable Structured Reference Strings
category: security
tags: [论文解读, ePrint:2019/099]
eprint: 2019/099
source: IACR ePrint
url: https://eprint.iacr.org/2019/099
created: 2026-04-10T14:11:28.285Z
---

# Sonic: Zero-Knowledge SNARKs from Linear-Size Universal and Updateable Structured Reference Strings

**IACR ePrint** | ePrint: 2019/099 | **Author**: Mary Maller, Sean Bowe, Markulf Kohlweiss, Sarah Meiklejohn

## 摘要

Zero-knowledge proofs have become an important tool for addressing privacy and scalability concerns in cryptocurrencies and other applications. In many systems each client downloads and verifies every new proof, and so proofs must be small and cheap to verify. The most practical schemes require either a trusted setup, as in (pre-processing) zk-SNARKs, or verification complexity that scales linearly with the complexity of the relation, as in Bulletproofs. The structured reference strings required by most zk-SNARK schemes can be constructed with multi-party computation protocols, but the resulting parameters are specific to an individual relation. Groth et al. discovered a zk-SNARK protocol with a universal and updateable structured reference string, however the string scales quadratically in the size of the supported relations. Here we describe a zero-knowledge SNARK, Sonic, which supports a universal and continually updateable structured reference string that scales linearly in size. Sonic proofs are constant size, and in the batch verification context the marginal cost of verification is comparable with the most efficient SNARKs in the literature. We also describe a generally useful technique in which untrusted ``helpers&#39;&#39; can compute advice which allows batches of proofs to be verified more efficiently. Note: Batching arguments updated.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

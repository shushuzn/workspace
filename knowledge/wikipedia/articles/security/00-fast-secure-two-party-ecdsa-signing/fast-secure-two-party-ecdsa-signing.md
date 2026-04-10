---
id: fast-secure-two-party-ecdsa-signing
title: Fast Secure Two-Party ECDSA Signing
category: security
tags: [论文解读, ePrint:2017/552]
eprint: 2017/552
source: IACR ePrint
url: https://eprint.iacr.org/2017/552
created: 2026-04-10T14:43:52.778Z
---

# Fast Secure Two-Party ECDSA Signing

**IACR ePrint** | ePrint: 2017/552 | **Author**: Yehuda Lindell

## 摘要

ECDSA is a standard digital signature schemes that is widely used in TLS, Bitcoin and elsewhere. Unlike other schemes like RSA, Schnorr signatures and more, it is particularly hard to construct efficient threshold signature protocols for ECDSA (and DSA). As a result, the best-known protocols today for secure distributed ECDSA require running heavy zero-knowledge proofs and computing many large-modulus exponentiations for every signing operation. In this paper, we consider the specific case of two parties (and thus no honest majority) and construct a protocol that is approximately two orders of magnitude faster than the previous best. Concretely, our protocol achieves good performance, with a single signing operation for curve P-256 taking approximately 37ms between two standard machine types in Azure (utilizing a single core only). Our protocol is proven secure for sequential composition under standard assumptions using a game-based definition. In addition, we prove security by simulation under a plausible yet non-standard assumption regarding Paillier. We show that partial concurrency (where if one execution aborts then all need to abort) can also be achieved. Note: In the Journal of Cryptology, 34:44, 2021. This is the full version of the paper at CRYPTO 2017.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

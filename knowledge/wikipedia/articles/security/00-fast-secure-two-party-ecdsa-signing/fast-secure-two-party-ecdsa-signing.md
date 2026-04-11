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

ECDSA是互联网和区块链的核心签名算法，但构建高效的阈值签名协议极其困难：

- **ECDSA广泛应用**：TLS、比特币等无数系统使用ECDSA
- **阈值签名需求**：多方共同签名需要保护私钥不泄露
- **现有方案效率低下**：需要运行大量零知识证明，每次签名都极慢

核心问题：两方ECDSA签名能否在不泄露私钥的前提下达到实用性能？

## 核心方法

### 1. 困境分析

ECDSA的代数结构使得：
- 无法像Schnorr签名那样简单分解
- 需要复杂的零知识证明来证明关系
- 每次签名都要计算大量模指数

### 2. Lindell的解决方案

本文构造了两方ECDSA的高效协议：

关键思想：利用**加法秘密分享**和**伪签名分享**：

1. 将私钥d分享为d = d₁ + d₂
2. 双方各持有一个分享
3. 签名时通过安全协议计算(d₁, d₂)的函数

### 3. 核心优化

- **减少零知识证明调用**：从每次签名多次降到仅一次
- **预计算优化**：离线预计算降低在线阶段开销
- **Paillier加密**：基于Paillier同态加密实现安全计算

### 4. 性能数据

| 指标 | 数值 |
|------|------|
| 单次签名时间 | ~37ms（P-256曲线）|
| 机器配置 | Azure标准机器，单核 |
| 相比前作 | 快约100倍 |

## 关键发现

1. **两方阈值ECDSA首个实用方案**：性能达到可接受范围
2. **100倍加速**：相比之前最好的方案
3. **标准假设下安全**：基于游戏定义的证明，标准假设
4. **顺序合成安全**：通过顺序合成框架证明
5. **部分并发可行**：可实现"一方中止则全部中止"

## 个人评价

这篇论文解决了ECDSA阈值签名的效率问题，使得分布式密钥管理在实践中可行。

**深层跨域联系**：

1. **秘密分享 ↔ 拓扑分裂**：ECDSA的加法秘密分享与拓扑中的流形分裂有概念相似性——都是将整体"分裂"为部分

2. **顺序合成 ↔ 拓扑序**：协议的安全性通过顺序合成框架证明，这与拓扑学中研究序列结构（topological order）的方法有相似性

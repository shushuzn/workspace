---
id: ouroboros-chronos-permissionless-clock-synchronization-via-proof-of-stake
title: Ouroboros Chronos: Permissionless Clock Synchronization via Proof-of-Stake
category: security
tags: [论文解读, ePrint:2019/838]
eprint: 2019/838
source: IACR ePrint
url: https://eprint.iacr.org/2019/838
created: 2026-04-10T14:40:00.076Z
---

# Ouroboros Chronos: Permissionless Clock Synchronization via Proof-of-Stake

**IACR ePrint** | ePrint: 2019/838 | **Author**: Christian Badertscher, Peter Gaži, Aggelos Kiayias, Alexander Russell, Vassilis Zikas

## 摘要

Clock synchronization allows parties to establish a common notion of global time by leveraging a weaker synchrony assumption, i.e., local clocks with approximately the same speed. The problem has long been a prominent goal for fault-tolerant distributed computing with a number of ingenious solutions in various settings. However, despite intensive investigation, the existing solutions do not apply to common blockchain protocols, which are designed to tolerate variable---and potentially adversarial---participation patterns, e.g., sleepiness and dynamic availability. Furthermore, because such blockchain protocols rely on freshly joining (or re-joining) parties to have a common notion of time, e.g., a global clock which allows knowledge of the current protocol round, it is not clear if or how they can operate without such a strong synchrony assumption. In this work, we show how to solve the global synchronization problem by leveraging proof of stake (PoS). Concretely, we design and analyze a PoS blockchain protocol in the above dynamic-participation setting, that does not require a global clock but merely assumes that parties have local clocks advancing at approximately the same speed. Central to our construction is a novel synchronization mechanism that can be thought as the blockchain-era analogue of classical synchronizers: It enables joining parties---even if upon joining their local time is off by an arbitrary amount---to quickly calibrate their local clocks so that they all show approximately the same time. As a direct implication of our blockchain construction---since the blockchain can be joined and observed by any interested party---we obtain a permissionless PoS implementation of a global clock that may be used by higher level protocols that need access to global time. Note: Revised overall structure of the paper and improved presentation of the results.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

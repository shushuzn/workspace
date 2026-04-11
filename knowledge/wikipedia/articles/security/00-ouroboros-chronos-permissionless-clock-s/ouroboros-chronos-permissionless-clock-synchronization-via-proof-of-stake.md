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

区块链协议中的全局时钟同步是长期困扰学术界和工业界的难题：

- **区块链本质**：区块链协议设计为容忍动态且可能对抗性的参与模式
- **强同步假设困境**：现有解决方案依赖全局时钟或强同步假设
- **新加入方问题**：新加入或重新加入的参与方需要与全局时钟同步

核心问题：如何在无需全局时钟的情况下，实现区块链协议的全局同步？

## 核心方法

### 1. 利用PoS解决全局同步

本文利用权益证明（Proof of Stake）解决区块链中的全局同步问题：

- **本地时钟假设**：仅需参与方拥有近似相同速度的本地时钟
- **无需全局时钟**：不依赖全局时钟或强同步假设
- **容忍动态参与**：支持参与方的动态加入和离开

### 2. 区块链时代同步器

构造可视为经典同步器的区块链时代版本：

- **校准机制**：即使加入时本地时间偏差任意大，也能快速校准
- **无需中心协调**：通过区块链本身实现去中心化同步
- **无权限**：任何有兴趣的参与方都可以加入和观察区块链

### 3. 动态参与设置

针对动态参与设置设计区块链协议：

- **容忍睡眠**：节点可以休眠后重新加入
- **动态可用性**：支持参与方的动态可用性变化
- **对抗性参与**：容忍潜在对抗性的参与模式

### 4. 全局时钟实现

作为直接推论：

- **无权限PoS全局时钟**：获得可被更高级协议使用的全局时钟实现
- **可被任何人观察**：区块链可被任何有兴趣的参与方观察
- **上层协议基础**：为需要全局时间的上层协议提供基础设施

## 关键发现

1. **无需全局时钟**：首次实现无全局时钟假设的区块链同步
2. **区块链时代同步器**：提出经典同步器的区块链版本
3. **动态参与支持**：完整支持动态参与模式
4. **无权限全局时钟**：实现可被上层协议使用的全局时钟
5. **理论基础**：为区块链时间同步提供严格理论基础

## 个人评价

Ouroboros Chronos解决了区块链领域的根本性问题——如何在去中心化、无权限的环境中实现可信的时间同步。这为所有依赖时间感知的区块链上层协议提供了基础设施级贡献。

**深层跨域联系**：

1. **时钟同步 ↔ 拓扑联络**：全局时钟同步与拓扑学中的平坦联络（flat connection）有深层结构相似——都是建立局部与整体一致性的机制

2. **校准机制 ↔ 拓扑适配**：局部时钟校准与拓扑适配性（topological adaptation）有概念相似——都是让不同组件协调到一致状态

3. **动态参与 ↔ 拓扑变体**：动态参与模式与拓扑学中的变分（variation）研究有深层联系——都涉及在变化中保持某种整体一致性

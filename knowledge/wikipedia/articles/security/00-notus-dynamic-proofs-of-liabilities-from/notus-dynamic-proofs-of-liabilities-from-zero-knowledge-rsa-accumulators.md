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

负债证明（PoL）是加密资产交易平台监管合规的核心技术：

- **动态负债场景**：用户负债随时增减，交易所需要定期更新证明
- **静态方案局限**：现有PoL方案大多针对静态场景，动态扩展存在"窗口机会"漏洞
- **证明人欺骗风险**：如果并非所有用户都在所有时期检查，不诚信的证明人可以在检查窗口期伪造账目

核心问题：如何在动态负债更新场景下，实现无可信第三方的负债证明？

## 核心方法

### 1. 首个动态PoL系统

Notus是首个避免窗口机会漏洞的动态PoL系统：

- **一般性负债更新**：支持任意增删改的负债操作
- **每时期O(1)开销**：查询证明大小、验证时间、审计者开销均为常数级
- **Epoch增量更新**：设计为每天或每epoch更新一次

### 2. 零知识RSA累加器

构造了新型零知识且SNARK友好的RSA累加器：

- **零知识特性**：不泄露额外信息
- **SNARK友好**：便于与递归零知识证明组合
- **MultiSwap协议**：相应的零知识多交换协议

### 3. 窗口机会漏洞防御

解决了动态设置中的核心安全问题：

- **持续可验证性**：即使只有部分用户检查，证明人仍无法欺骗
- **无窗口期**：消除证明人可乘之机的时间窗口
- **安全性与效率兼得**：不牺牲效率前提下保证安全

### 4. 性能数据

| 指标 | 数值 |
|------|------|
| 验证时间 | < 2ms |
| 证明大小 | 256 Bytes |
| 用户规模 | 支持10⁶用户 |
| 完整epoch更新 | ~3分钟（8×32核云服务器）|

## 关键发现

1. **首个实用动态PoL**：解决窗口机会漏洞的里程碑方案
2. **常数级效率**：查询和验证均达到O(1)
3. **大规模可扩展**：支持百万级用户规模
4. **零知识RSA累加器**：新型原语可独立应用于其他场景
5. **已实际部署**：云端测试平台验证了实用性

## 个人评价

Notus解决了负债证明从静态到动态的关键跨越，为加密资产交易平台的合规监管提供了实用工具。其零知识RSA累加器作为核心组件可能在其他零知识应用中发挥重要作用。

**深层跨域联系**：

1. **累加器聚合 ↔ 拓扑商空间**：RSA累加器将多个负债聚合为单一承诺，与拓扑学中的商空间（quotient space）有概念相似——都是通过某种等价关系将多重信息压缩到单一表示

2. **动态更新 ↔ 拓扑变分**：动态负债更新与拓扑学中的变分（variation）研究有深层联系——都是研究在连续变化中保持某种不变量

3. **常数级证明 ↔ 拓扑紧化**：O(1)证明大小与拓扑紧化（compactification）思想相通——将大量信息压缩到有限的表示中

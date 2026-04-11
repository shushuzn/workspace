---
id: global-scale-secure-multiparty-computation
title: Global-Scale Secure Multiparty Computation
category: security
tags: [论文解读, ePrint:2017/189]
eprint: 2017/189
source: IACR ePrint
url: https://eprint.iacr.org/2017/189
created: 2026-04-10T14:31:08.063Z
---

# Global-Scale Secure Multiparty Computation

**IACR ePrint** | ePrint: 2017/189 | **Author**: Xiao Wang, Samuel Ranellucci, Jonathan Katz

## 摘要

We propose a new, constant-round protocol for multi-party computation of boolean circuits that is secure against an arbitrary number of malicious corruptions. At a high level, we extend and generalize recent work of Wang et al. in the two-party setting and design an efficient preprocessing phase that allows the parties to generate authenticated information; we then show how to use this information to distributively construct a single ``authenticated&#39;&#39; garbled circuit that is evaluated by one party. Our resulting protocol improves upon the state-of-the-art both asymptotically and concretely. We validate these claims via several experiments demonstrating both the efficiency and scalability of our protocol: - Efficiency: For three-party computation over a LAN, our protocol requires only 95 ms to evaluate AES. This is roughly a 700$\times$ improvement over the best prior work, and only 2.5$\times$ slower than the best known result in the two-party setting. In general, for $n$ parties our protocol improves upon prior work (which was never implemented) by a factor of more than $230n$, e.g., an improvement of 3 orders of magnitude for 5-party computation. - Scalability: We successfully executed our protocol with a large number of parties located all over the world, computing (for example) AES with 128 parties across 5 continents in under 3 minutes. Our work represents the largest-scale demonstration of secure computation to date.

## 研究动机

安全多方计算（MPC）在全球规模部署面临根本性挑战：

- **常数轮协议需求**：现有方案通信轮数随参与方数量增长
- **大规模实验缺失**：此前工作从未实现真正的大规模部署测试
- **横跨全球的信任**：需要验证在全球分布的参与方之间MPC的可行性
- **效率瓶颈**：即使是最先进的方案，对于大量参与方仍效率低下

核心问题：能否构造常数轮且真正可扩展到全球规模的MPC协议？

## 核心方法

### 1. 高效预处理阶段

扩展和改进Wang等人两方设置的工作：

- **认证信息生成**：参与方生成认证信息
- **分布式构造**：利用认证信息分布式构造单个"认证"混淆电路
- **单方评估**：仅需一方评估混淆电路
- **常数轮特性**：协议轮数与参与方数量无关

### 2. 认证混淆电路

核心构造：

- **认证结构**：将标准混淆电路扩展为支持多方认证
- **分布式生成**：认证电路由所有参与方分布式生成
- **单方评估**：评估由单个参与方完成，无需各方参与

### 3. 性能优化

相较于前作的理论与实践双重改进：

- **渐近改进**：协议复杂度优于前人工作
- **具体改进**：实验验证了效率和可扩展性

### 4. 性能数据

| 场景 | 性能 |
|------|------|
| 3方LAN计算AES | 仅需95ms |
| vs前最佳工作 | ~700倍提升 |
| vs两方最佳结果 | 仅慢2.5倍 |
| n方改进 | 超过230n倍改进 |
| 128方跨5洲计算AES | 3分钟内完成 |

## 关键发现

1. **首个大规模演示**：史上最大规模的MPC实际部署演示
2. **常数轮协议**：轮数与参与方数量无关
3. **700倍效率提升**：3方计算相比前最佳工作改进700倍
4. **全球横跨测试**：128方跨5大洲成功执行MPC
5. **实用里程碑**：证明MPC可在全球规模部署

## 个人评价

这是MPC领域的里程碑工作，首次通过大规模实验证明了全球尺度安全计算的可行性。常数轮协议设计和700倍的效率提升使MPC从理论走向实践。

**深层跨域联系**：

1. **常数轮特性 ↔ 拓扑刚性**：常数轮与拓扑学中的刚性（rigidity）有深层联系——都是某种不随规模变化的性质

2. **全球分布 ↔ 拓扑流行**：跨5大洲的MPC与拓扑流行（topological manifold）有概念相似——都是研究跨越广大空间的整体结构

3. **预处理模式 ↔ 拓扑预置**：预处理阶段与拓扑学中的预置结构有相似性——都是为后续计算预先准备某种不变结构

---
id: non-interactive-universal-arguments
title: Non-interactive Universal Arguments
category: security
tags: [论文解读, ePrint:2023/458]
eprint: 2023/458
source: IACR ePrint
url: https://eprint.iacr.org/2023/458
created: 2026-04-10T14:24:51.391Z
---

# Non-interactive Universal Arguments

**IACR ePrint** | ePrint: 2023/458 | **Author**: Nir Bitansky, Omer Paneth, Dana Shamir, Tomer Solomon

## 摘要

In 2002, Barak and Goldreich introduced the notion of a universal argument and constructed an interactive universal argument for non-deterministic computations based on polynomially hard collision-resistant hash functions. Since then, and especially in recent years, there have been tremendous developments in the construction of non-interactive succinct arguments for deterministic computations under standard hardness assumptions. However, the constructed succinct arguments can be proven universal only under sub-exponential assumptions. Assuming polynomially hard fully homomorphic encryption and a widely believed worst-case complexity assumption, we prove a general lifting theorem showing that all existing non-interactive succinct arguments can be made universal. The required complexity assumption is that non-uniformity does not allow arbitrary polynomial speedup. In the setting of uniform adversaries, this extra assumption is not needed.

## 研究动机

通用参数（Universal Arguments）是密码学证明系统的核心概念：

- **Barak-Goldreich开创性工作**：2002年提出通用参数概念，基于多项式硬度的碰撞电阻哈希函数构造
- **非确定性计算支持**：已有方案支持非确定性计算
- **最新进展**：近年来在标准硬度假设下为确定性计算构造非交互简洁证明取得巨大进展
- **通用性瓶颈**：现有构造只能在亚指数假设下被证明通用

核心问题：能否在标准多项式硬度假设下，将所有现有非交互简洁参数改造为通用的？

## 核心方法

### 1. 通用性提升定理

本文证明了一般性的提升定理：

- **FHE假设**：基于多项式硬度的全同态加密
- **复杂性假设**：基于广泛相信的最坏情况复杂性假设
- **所有现有方案可升级**：证明所有现有非交互简洁参数都可以被改造为通用的

### 2. 非一致性限制

核心假设：

- **非一致性不允许任意多项式加速**：非均匀性不能提供任意多项式加速
- **均匀对手不需要此假设**：在均匀对手设置下不需要额外假设
- **与P≠NP相关**：此假设与复杂性理论中的核心问题相关

### 3. 现有方案的通用化

将以下方案的通用性进行提升：

- **确定性计算参数**：已有的各种非交互简洁证明
- **标准假设下安全**：在多项式硬度假设下可证安全
- **实际应用价值**：提高现有方案的适用范围

### 4. 理论意义

统一了多种现有方案：

- **通用框架**：提供了将特定方案通用化的通用方法
- **假设简化**：将亚指数假设替换为标准多项式假设
- **理论与实践结合**：为实际部署的方案提供更强安全性保证

## 关键发现

1. **通用性突破**：首次在标准多项式假设下实现通用性证明
2. **FHE驱动方法**：利用全同态加密作为桥梁实现通用性提升
3. **复杂性理论连接**：与非一致性限制假设有深层联系
4. **实际影响广泛**：可直接应用于现有多种非交互证明系统
5. **均匀vs非均匀**：明确区分了均匀和非均匀设置下的不同要求

## 个人评价

这是通用参数领域的理论突破，通过巧妙的提升定理将亚指数假设下的安全性结果迁移到标准多项式假设。为实际部署的零知识证明系统提供了更坚实的安全性基础。

**深层跨域联系**：

1. **通用性 ↔ 拓扑[[拓扑序|拓扑万有性]]**：通用参数（universal argument）与拓扑学中的[[拓扑序|拓扑万有性]]质（universal property）有深层结构相似——都是某种"能够表示所有其他同类对象"的最高级形式

2. **非一致性限制 ↔ 拓扑障碍**：非一致性不允许任意加速与拓扑障碍理论有概念相似——都是研究某种"不可逾越"的界限

3. **FHE同态性 ↔ 拓扑函子性**：FHE的同态性质与拓扑学中的函子性（functoriality）有深层联系——都是保持结构的映射

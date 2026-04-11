---
id: proof-carrying-data-from-accumulation-schemes
title: Proof-Carrying Data from Accumulation Schemes
category: security
tags: [论文解读, ePrint:2020/499]
eprint: 2020/499
source: IACR ePrint
url: https://eprint.iacr.org/2020/499
created: 2026-04-10T14:15:25.718Z
---

# Proof-Carrying Data from Accumulation Schemes

**IACR ePrint** | ePrint: 2020/499 | **Author**: Benedikt Bünz, Alessandro Chiesa, Pratyush Mishra, Nicholas Spooner

## 摘要

Recursive proof composition has been shown to lead to powerful primitives such as incrementally-verifiable computation (IVC) and proof-carrying data (PCD). All existing approaches to recursive composition take a succinct non-interactive argument of knowledge (SNARK) and use it to prove a statement about its own verifier. This technique requires that the verifier run in time sublinear in the size of the statement it is checking, a strong requirement that restricts the class of SNARKs from which PCD can be built. This in turn restricts the efficiency and security properties of the resulting scheme. Bowe, Grigg, and Hopwood (ePrint 2019/1021) outlined a novel approach to recursive composition, and applied it to a particular SNARK construction which does *not* have a sublinear-time verifier. However, they omit details about this approach and do not prove that it satisfies any security property. Nonetheless, schemes based on their ideas have already been implemented in software. In this work we present a collection of results that establish the theoretical foundations for a generalization of the above approach. We define an *accumulation scheme* for a non-interactive argument, and show that this suffices to construct PCD, even if the argument itself does not have a sublinear-time verifier. Moreover we give constructions of accumulation schemes for SNARKs, which yield PCD schemes with novel efficiency and security features.

## 研究动机

递归证明组合是构造IVC和PCD的核心技术：

- **现有递归组合局限**：所有现有递归组合方法都要求SNARK的验证者亚线性运行
- **强限制条件**：这个要求限制了可构建PCD的SNARK类别
- **Bowe等人突破**：Bowe、Grigg、Hopwood提出了无需亚线性验证者的递归组合方法
- **缺乏理论证明**：虽然已有软件实现，但缺乏安全性证明

核心问题：如何为Bowe等人的方法建立严格的理论基础，并一般化此方法？

## 核心方法

### 1. 积累方案定义

形式化积累方案的概念：

- **对非交互论证的积累**：为非交互论证定义积累方案
- **不要求亚线性验证**：即使论证本身没有亚线性时间验证者也足够
- **充分性证明**：证明积累方案足以构造PCD

### 2. PCD构造新条件

将构造条件从"亚线性验证"弱化为"积累方案"：

- **更广泛适用**：允许使用更多类型的底层论证系统
- **安全性保持**：不因条件弱化而牺牲安全性
- **效率特征新颖**：可获得具有新颖效率和安全特性的PCD方案

### 3. SNARK积累方案构造

为多种SNARK构造积累方案：

- **通用构造方法**：不依赖特定SNARK结构
- **效率优化**：可获得新颖效率特征的PCD
- **安全增强**：可获得新颖安全特性的PCD

### 4. 理论基础建立

建立递归组合方法的理论框架：

- **安全性证明**：为Bowe等人的方法提供安全性证明
- **一般化框架**：将特殊构造推广为一般性理论
- **软件实现支撑**：为已有软件实现提供理论支撑

## 关键发现

1. **积累方案形式化**：首次形式化积累方案概念
2. **条件弱化突破**：将PCD构造条件从SNARK亚线性验证弱化为积累方案
3. **理论完整性**：为Bowe等人的方法建立严格理论基础
4. **新颖效率特征**：可构造具有新颖效率的PCD
5. **安全性证明**：为实用方案提供安全性保证

## 个人评价

这篇论文填补了递归证明组合理论的重要空白。通过积累方案这一新概念，将实践中有效的构造方法纳入严格理论框架，为PCD和IVC的发展奠定了更坚实基础。

**深层跨域联系**：

1. **积累方案 ↔ 拓扑累积**：积累方案与拓扑学中的累积（accumulation）有深层结构相似——都是将增量信息逐步合并为整体

2. **递归组合 ↔ 拓扑复合**：递归证明组合与拓扑学中的复合（composition）有概念相似——都是通过组合构建更复杂的结构

3. **亚线性要求 ↔ 拓扑效率**：从亚线性到积累方案的弱化与拓扑学中从强条件到弱条件的最优化有相似性——都是追求在最弱假设下达到目标

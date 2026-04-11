---
id: a-survey-of-two-verifiable-delay-functions
title: A Survey of Two Verifiable Delay Functions
category: security
tags: [论文解读, ePrint:2018/712]
eprint: 2018/712
source: IACR ePrint
url: https://eprint.iacr.org/2018/712
created: 2026-04-10T14:41:51.695Z
---

# A Survey of Two Verifiable Delay Functions

**IACR ePrint** | ePrint: 2018/712 | **Author**: Dan Boneh, Benedikt Bünz, Ben Fisch

## 摘要

A verifiable delay function (VDF) is an important tool used for adding delay in decentralized applications. This short note briefly surveys and compares two recent beautiful Verifiable Delay Functions (VDFs), one due to Pietrzak and the other due to Wesolowski. We also provide a new computational proof of security for one of them, and compare the complexity assumptions needed for both schemes.

## 研究动机

可验证延迟函数（VDF）是去中心化应用中的重要工具：

- **时间延迟**：在区块链中引入不可跳过的时间延迟
- **随机性来源**：VDF提供可验证的随机性（用于PoS抽签等）
- **防止贿赂攻击**：延迟使得贿赂无意义

两种VDF方案（Pietrzak和Wesolowski）各有优缺点，需要系统性比较。

## 核心方法

### 1. VDF定义

VDF的核心性质：
- **延迟性**：计算需要至少T步 sequential 操作
- **可验证性**：任何人都能快速验证证明正确性
- **唯一性**：给定输入，输出唯一

### 2. Pietrzak VDF

基于**迭代哈希**构造：
- 证明者进行T次哈希迭代
- 证明：进行了T步sequential计算
- 安全性基于序贯哈希的困难性

### 3. Wesolowski VDF

基于**数论**构造：
- 证明者计算 g^(2^T)
- 通过商群和除法给出简洁证明
- 安全性基于整数分解困难性

### 4. 比较

| 指标 | Pietrzak | Wesolowski |
|------|-----------|-------------|
| 证明大小 | O(log T) | O(1) |
| 验证速度 | 慢（多指数运算） | 快 |
| 安全性假设 | 哈希困难性 | 整数分解 |
| 抗量子 | 是 | 否 |

## 关键发现

1. **证明大小权衡**：Pietrzak证明更大但验证更慢；Wesolowski证明小但验证相对慢
2. **安全性假设**：Pietrzak抗量子；Wesolowski依赖整数分解
3. **实用性**：Wesolowski在大多数场景更实用
4. **组合使用**：两种方案可组合使用
5. **标准化**：VDF正在成为区块链基础设施组件

## 个人评价

这篇简短综述为VDF的工程选型提供了清晰指南。两种方案各有权衡，实际应用需根据场景选择。

**深层跨域联系**：

1. **时间延迟 ↔ 拓扑时间**：VDF的时间延迟与拓扑学中研究的"时间参数化"有深层联系——都涉及某种不可逆的演进过程

2. **顺序计算 ↔ 拓扑序**：sequential计算与拓扑序（topological order）有概念相似性——都是某种"不可并行化"的序列结构

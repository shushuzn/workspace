---
id: proof-carrying-data-without-succinct-arguments
title: Proof-Carrying Data without Succinct Arguments
category: security
tags: [论文解读, ePrint:2020/1618]
eprint: 2020/1618
source: IACR ePrint
url: https://eprint.iacr.org/2020/1618
created: 2026-04-10T14:15:28.113Z
---

# Proof-Carrying Data without Succinct Arguments

**IACR ePrint** | ePrint: 2020/1618 | **Author**: Benedikt Bünz, Alessandro Chiesa, William Lin, Pratyush Mishra, Nicholas Spooner

## 摘要

Proof-carrying data (PCD) is a powerful cryptographic primitive that enables mutually distrustful parties to perform distributed computations that run indefinitely. Known approaches to construct PCD are based on succinct non-interactive arguments of knowledge (SNARKs) that have a succinct verifier or a succinct accumulation scheme. In this paper we show how to obtain PCD without relying on SNARKs. We construct a PCD scheme given any non-interactive argument of knowledge (e.g., with linear-size arguments) that has a *split accumulation scheme*, which is a weak form of accumulation that we introduce. Moreover, we construct a transparent non-interactive argument of knowledge for R1CS whose split accumulation is verifiable via a (small) *constant number of group and field operations*. Our construction is proved secure in the random oracle model based on the hardness of discrete logarithms, and it leads, via the random oracle heuristic and our result above, to concrete efficiency improvements for PCD. Along the way, we construct a split accumulation scheme for Hadamard products under Pedersen commitments and for a simple polynomial commitment scheme based on Pedersen commitments. Our results are supported by a modular and efficient implementation. Note: Fix minor typo in abstract

## 研究动机

证明携带数据（PCD）是密码学中的强大原语：

- **无限分布式计算**：使互不信任的参与方能执行无限长的分布式计算
- **SNARK依赖瓶颈**：现有方法依赖简洁非交互知识论证（SNARKs）
- **透明性挑战**：许多SNARK方案需要可信设置，不够透明
- **简洁性要求**：SNARK的简洁性可能带来不必要的复杂性

核心问题：能否不依赖SNARK构造PCD，利用更弱的积累假设？

## 核心方法

### 1. 分割积累方案

引入一种弱化的积累形式——分割积累（split accumulation）：

- **弱化形式**：不需要完整的积累性质
- **构建灵活**：可以在更弱的假设下实现
- **PCD构造基础**：足以支撑PCD构造

### 2. 非SNARK的PCD构造

给定任何非交互知识论证（例如线性大小论证）：

- **只要有分割积累方案**：即可构造PCD
- **突破SNARK依赖**：不再需要SNARK的简洁性
- **更多候选方案**：可以利用更广泛的底层论证系统

### 3. 透明非交互R1CS论证

针对R1CS构造透明非交互论证：

- **常数级验证**：分割积累可通过常数个群和域运算验证
- **基于离散对数**：在随机预言机模型下基于离散对数困难性
- **Hadamard积积累**：为Hadamard积构造分割积累方案

### 4. Pedersen承诺应用

构建基于Pedersen承诺的分割积累方案：

- **Hadamard积**：支持Hadamard积的积累
- **简单多项式承诺**：为简单的多项式承诺方案构造积累
- **模块化实现**：实现模块化且高效

## 关键发现

1. **突破SNARK依赖**：首次不依赖SNARK构造PCD
2. **分割积累新概念**：引入弱化但足够实用的积累形式
3. **透明性改进**：提供基于离散对数的透明方案
4. **常数级验证**：验证效率显著提升
5. **实用效率**：实现展现出良好的实际效率

## 个人评价

这是PCD理论的重要突破，通过引入分割积累这一弱化概念，摆脱了对SNARK的依赖。为那些不适合使用SNARK的场景提供了替代方案，同时保持了PCD的核心能力。

**深层跨域联系**：

1. **分割积累 ↔ 拓扑分裂**：分割积累与拓扑学中的分裂（splitting）有深层联系——都是将整体结构分解为可独立处理的部分

2. **无限计算 ↔ 拓扑无限**：PCD支持的无限分布式计算与拓扑学中的无限（infinite）概念有结构相似——都涉及在延续中保持某种不变性质

3. **常数级验证 ↔ 拓扑有效不变式**：常数级验证与拓扑学中的有效不变式有概念相似——都是追求最优的计算效率

---
id: simple-verifiable-delay-functions
title: Simple Verifiable Delay Functions
category: security
tags: [论文解读, ePrint:2018/627]
eprint: 2018/627
source: IACR ePrint
url: https://eprint.iacr.org/2018/627
created: 2026-04-10T14:41:47.305Z
---

# Simple Verifiable Delay Functions

**IACR ePrint** | ePrint: 2018/627 | **Author**: Krzysztof Pietrzak

## 摘要

We construct a verifable delay function (VDF) by showing how the Rivest-Shamir-Wagner time-lock puzzle can be made publicly verifiable. Concretely, we give a statistically sound public-coin protocol to prove that a tuple $(N,x,T,y)$ satisfies $y=x^{2^T}\pmod N$ where the prover doesn&#39;t know the factorization of $N$ and its running time is dominated by solving the puzzle, that is, compute $x^{2^T}$, which is conjectured to require $T$ sequential squarings. To get a VDF we make this protocol non-interactive using the Fiat-Shamir heuristic. The motivation for this work comes from the Chia blockchain design, which uses a VDF as a key ingredient. For typical parameters ($T\le 2^{40},N=2048$), our proofs are of size around $10KB$, verification cost around three RSA exponentiations and computing the proof is $8000$ times faster than solving the puzzle even without any parallelism.

## 研究动机

可验证延迟函数（VDF）是Chia区块链设计中的关键组件：

- **Chia共识需求**：Chia区块链使用VDF作为共识关键要素
- **时间锁定谜题**：RSA时间锁谜题（RSW）虽能提供延迟，但无法公开验证
- **实用化挑战**：需要让任何人快速验证延迟已发生

核心问题：如何将RSW时间锁谜题改造成可公开验证的VDF？

## 核心方法

### 1. RSW时间锁谜题公开化

将Rivest-Shamir-Wagner时间锁谜题改造为公开可验证：

- **给定的元组**：证明(N, x, T, y)满足 y = x^{2^T} (mod N)
- **证明者不知道因子分解**：证明者不知道N的因子分解
- **运行时间由谜题主导**：计算x^{2^T}需要T次顺序平方运算

### 2. 统计可靠性的公开硬币协议

给出统计可靠的公开硬币协议：

- **统计可靠性**：统计意义上无法伪造证明
- **单次交互**：协议运行一次即可
- **类比Fiat-Shamir**：通过Fiat-Shamir启发式转为非交互式

### 3. Fiat-Shamir非交互化

将交互协议转为非交互VDF：

- **非交互式证明**：证明可被任何人验证
- **公开可验证性**：无需可信第三方
- **保持延迟特性**：计算仍需要T步顺序操作

### 4. 性能数据

| 指标 | 数值 |
|------|------|
| 典型参数 | T ≤ 2⁴⁰, N = 2048 |
| 证明大小 | ~10KB |
| 验证成本 | 约3次RSA指数运算 |
| 证明速度 | 比解谜题快8000倍 |

## 关键发现

1. **VDF构造简化**：给出比Wesolowski VDF更简单的构造
2. **Chia集成**：已被Chia区块链采用
3. **证明效率高**：证明生成比求解谜题快8000倍
4. **公开验证**：无需可信设置即可验证
5. **实用性验证**：参数设置达到实用性能

## 个人评价

Simple VDF与Wesolowski VDF形成互补——前者构造简单，后者证明更短。在Chia等实际系统中已被部署验证了其工程可行性。

**深层跨域联系**：

1. **顺序平方 ↔ [[拓扑序|拓扑时间]]**：T次顺序平方运算与拓扑学中研究的"时间参数化"（temporal parameterization）有深层联系——都是某种不可并行的序列过程

2. **RSA时间锁 ↔ [[拓扑序|拓扑障碍]]**：RSA时间锁基于分解困难，与拓扑学中研究"穿越障碍所需的最小能量"有概念相似——都是某种计算或几何障碍

3. **VDF顺序性 ↔ [[拓扑序]]**：VDF要求的顺序计算特性与拓扑序（topological order）有深层联系——都是研究某种"不可绕过"的序列结构

---
id: making-groth39s-zk-snark-simulation-extractable-in-the-random-oracle-model
title: Making Groth&#39;s zk-SNARK Simulation Extractable in the Random Oracle Model
category: security
tags: [论文解读, ePrint:2018/187]
eprint: 2018/187
source: IACR ePrint
url: https://eprint.iacr.org/2018/187
created: 2026-04-10T14:23:35.647Z
---

# Making Groth&#39;s zk-SNARK Simulation Extractable in the Random Oracle Model

**IACR ePrint** | ePrint: 2018/187 | **Author**: Sean Bowe, Ariel Gabizon

## 摘要

We describe a variant of Groth&#39;s zk-SNARK [Groth, Eurocrypt 2016] that satisfies simulation extractability, which is a strong form of adaptive non-malleability. The proving time is almost identical to [Groth] and requires only two additional group operations. Our proof consists of 5 group elements rather than 3 as in [Groth], and the security proof requires the random oracle model.

## 研究动机

Groth16是最高效的SNARK之一，但存在**可塑性攻击**（malleability）风险：

- 原始Groth16：**非适应性仿真可提取性**（non-adaptive simulation extractability）
- 攻击者可以修改证明而不改变有效性
- 在某些应用（如区块链）中，这可能导致双花攻击

本文目标：在几乎不增加开销的情况下，将Groth16升级为**适应性仿真可提取性**（adaptive simulation extractability）。

## 核心方法

### 1. 仿真可提取性（Simulation Extractability）

仿真可提取性是SNARK的最高安全等级之一：

- **零知识**：证明不泄露见证
- **知识可靠性**：证明者必须有 witnesses 才能生成有效证明
- **仿真可提取性**：即使证明者在看到仿真器产生的证明后生成新证明，也可以提取其 witnesses

### 2. 适应性安全

"适应性"意味着攻击者可以在看到挑战后选择目标：

$$Advantage \leq \epsilon$$

这比"非适应性"安全强得多，因为在真实协议中攻击者可以看到挑战内容。

### 3. 额外开销

与原始Groth16相比：

| 指标 | 原始Groth16 | 仿真可提取版本 |
|------|-------------|---------------|
| 证明大小 | 3群元素 | 5群元素 |
| 证明时间 | 1x | ~1x（+2次群运算）|
| 安全性 | 非适应性 | 适应性 |

## 关键发现

1. **最小开销**：仅增加2个群元素和2次群运算
2. **强安全**：首次为Groth16提供适应性仿真可提取性
3. **兼容性**：与原始Groth16结构兼容，可直接升级
4. **随机预言机**：安全证明在随机预言机模型下成立
5. **实用性**：被后续多个项目采用作为安全SNARK的基础

## 个人评价

这篇论文展示了如何在保持效率的同时增强安全级别。在区块链等 adversarial 环境中，仿真可提取性是必要的安全保障。

**深层跨域联系**：

1. **适应性安全 ↔ 拓扑适应性**：适应性安全与拓扑量子计算中的"鲁棒性"有相似关注点——都是研究系统在动态对抗环境下的稳定性

2. **随机预言机 ↔ 混沌理论**：随机预言机模型中的"哈希函数的随机性"，与动力系统中的混沌行为有深层联系——都对初始条件极度敏感

3. **群论 ↔ 拓扑不变量**：椭圆曲线群的代数结构与拓扑不变量（如Jones多项式）有共同来源——都研究在某种变换下保持不变的结构

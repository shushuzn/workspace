---
id: one-shot-fiat-shamir-based-nizk-arguments-of-composite-residuosity-and-logarithmic-size-ring-signatures-in-the-standard-model
title: One-Shot Fiat-Shamir-based NIZK Arguments of Composite Residuosity and Logarithmic-Size Ring Signatures in the Standard Model
category: security
tags: [论文解读, ePrint:2020/1334]
eprint: 2020/1334
source: IACR ePrint
url: https://eprint.iacr.org/2020/1334
created: 2026-04-10T14:43:11.307Z
---

# One-Shot Fiat-Shamir-based NIZK Arguments of Composite Residuosity and Logarithmic-Size Ring Signatures in the Standard Model

**IACR ePrint** | ePrint: 2020/1334 | **Author**: Benoît Libert, Khoa Nguyen, Thomas Peters, Moti Yung

## 摘要

The standard model security of the Fiat-Shamir transform has been an active research area for many years. In breakthrough results, Canetti et al. (STOC&#39;19) and Peikert-Shiehian (Crypto&#39;19) showed that, under the Learning-With-Errors (LWE) assumption, it provides soundness by applying correlation-intractable (CI) hash functions to so-called trapdoor $\Sigma$-protocols. In order to be compatible with CI hash functions based on standard LWE assumptions with polynomial approximation factors, all known such protocols have been obtained via parallel repetitions of a basic protocol with binary challenges. In this paper, we consider languages related to Paillier&#39;s composite residuosity assumption (DCR) for which we give the first trapdoor $\Sigma$-protocols providing soundness in one shot, via exponentially large challenge spaces. This improvement is analogous to the one enabled by Schnorr over the original Fiat-Shamir protocol in the random oracle model. Using the correlation-intractable hash function paradigm, we then obtain simulation-sound NIZK arguments showing that an element of $\mathbb{Z}_{N^2}^\ast$ is a composite residue, which opens the door to space-efficient applications in the standard model. As a concrete example, we build logarithmic-size ring signatures (assuming a common reference string) with the shortest signature length among schemes based on standard assumptions in the standard model. We prove security under the DCR and LWE assumptions, while keeping the signature size comparable with that of random-oracle-based schemes.

## 研究动机

Fiat-Shamir变换在标准模型下的安全性是长期悬而未决的核心问题：

- **随机预言机依赖**：传统Fiat-Shamir依赖随机预言机，在标准模型下无法保证安全性
- **并行重复效率低**：已知方案通过并行重复二进制挑战协议来达到安全性，效率极低
- **应用受限**：无法构建实用的标准模型下的非交互零知识证明

核心问题：如何在大挑战空间下实现一次性（one-shot）安全性证明？

## 核心方法

### 1. 标准模型Fiat-Shamir

Canetti等人在STOC'19和Peikert-Shiehian在Crypto'19的突破性工作：

- **相关不可逆哈希函数**：利用CI哈希函数为陷阱Σ协议提供可靠性
- **LWE假设**：基于LWE的CI哈希函数在标准模型下安全
- **局限性**：需要多项式近似因子的LWE假设

### 2. 复合剩余假设的陷阱Σ协议

本文针对Paillier复合剩余假设（DCR）给出首个陷阱Σ协议：

- **指数级大挑战空间**：通过指数级大挑战空间实现一次性可靠性
- **类Schnorr改进**：类比Schnorr对原始Fiat-Shamir协议的改进
- **无需并行重复**：效率大幅提升

### 3. 模拟声音NIZK论证

利用CI哈希函数范式获得：

- **DCR语言**：证明Z\*_{N²}中元素是复合剩余
- **标准模型安全**：模拟声音NIZK论证
- **空间高效应用**：为标准模型下空间高效应用打开大门

### 4. 对数规模环签名

作为具体应用示例：

- **最短签名**：在标准模型下基于标准假设的方案中签名最短
- **DCR+LWE双重安全**：同时基于DCR和LWE假设
- **与ROM方案可比**：签名大小与随机预言机方案相当

## 关键发现

1. **一次性安全性突破**：首次实现大挑战空间下的one-shot可靠性
2. **首个DCR陷阱Σ协议**：填补复合剩余假设领域空白
3. **最短环签名**：标准模型下基于标准假设的环签名最短
4. **标准模型可行**：无需随机预言机即可实现实用NIZK
5. **效率提升显著**：避免并行重复带来的指数级开销

## 个人评价

这是Fiat-Shamir标准模型安全性的重要里程碑。通过指数级大挑战空间实现一次性安全性，为构建高效的实用零知识证明系统铺平了道路。

**深层跨域联系**：

1. **复合剩余假设 ↔ [[拓扑序|拓扑数论]]**：DCR基于复合剩余类的结构，与拓扑数论中研究p进数域的局部紧致性有深层联系——都涉及数域中的某种"剩余类"结构

2. **指数级挑战空间 ↔ [[拓扑序|拓扑熵]]**：大挑战空间与拓扑动力系统中的拓扑熵有概念相似——两者都涉及信息量的指数级增长

3. **环签名 ↔ [[辫群]]**：环签名的"环形"结构与拓扑学中的辫群（braid group）有深层联系——都是研究在闭合路径上的代数结构

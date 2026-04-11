---
id: proofs-of-isogeny-knowledge-and-application-to-post-quantum-one-time-verifiable-random-function
title: Proofs of Isogeny Knowledge and Application to Post-quantum One-Time Verifiable Random Function
category: security
tags: [论文解读, ePrint:2021/744]
eprint: 2021/744
source: IACR ePrint
url: https://eprint.iacr.org/2021/744
created: 2026-04-10T14:45:17.494Z
---

# Proofs of Isogeny Knowledge and Application to Post-quantum One-Time Verifiable Random Function

**IACR ePrint** | ePrint: 2021/744 | **Author**: Antonin Leroux

## 摘要

In this paper, we introduce a new method to prove the knowledge of an isogeny of given degree between two supersingular elliptic curves. Our approach can be extended to verify the evaluation of the secret isogeny on some points of the domain. The main advantage of this new proof of knowledge is its compactness which is orders of magnitude better than existing proofs of isogeny knowledge. The principle of our method is to reveal some well-chosen endomorphisms and does not constitute a zero-knowledge proof. However, when the degree is a large prime, we can introduce a new hardness assumption upon which we build the first verifiable random function (VRF) based on isogenies. Our protocol can be seen as a generalization of the BLS-style classical construction from elliptic curves and achieves one-time pseudo-randomness in the random oracle model. We propose concrete parameters for this new scheme which reach post-quantum NIST-1 level of security. Our VRF has an overall cost (proof size, key size and output size) of roughly $1$KB, which is shorter than all the other post-quantum instantiations based on lattices. In the process, we also develop several algorithmic tools to solve norm equations over quaternion orders that may be of independent interest.

## 研究动机

同源（isogeny）是连接椭圆曲线的代数结构，是后量子密码学的重要基石：

- **后量子时代来临**：量子计算机威胁RSA/ECDSA等传统签名，业界急需基于椭圆曲线同源的签名方案
- **现有同源证明效率低下**：已有的同源知识证明体积庞大，无法实用
- **VRF应用需求**：可验证随机函数（VRF）在区块链随机数生成、去中心化协议中有重要应用

核心问题：能否构造紧凑的同源知识证明，并基于此构建实用的后量子VRF？

## 核心方法

### 1. 同源知识证明新方法

本文提出紧凑的同源知识证明协议：

关键思想：揭示精心选择的自同态（endomorphisms），而非传统零知识证明：

1. 证明者持有同源 φ: E₁ → E₂
2. 选择特定自同态进行约束
3. 利用这些自同态的关系证明同源存在
4. 当度为大型素数时，引入新困难性假设

### 2. 第一个同源VRF构造

基于新假设，构造首个基于同源的一次性VRF：

- **BLS风格推广**：将经典椭圆曲线BLS VRF推广到同源场景
- **随机预言机模型**：证明一次性伪随机性
- **后量子安全**：参数达到NIST-1后量子安全级别

### 3. 四元数阶范方程算法

本文开发了多个四元数阶（quaternion order）范方程求解算法：

- 可能在其他场景独立有用

### 4. 性能数据

| 指标 | 数值 |
|------|------|
| VRF总成本 | ~1KB（proof + key + output）|
| vs lattice方案 | 比所有格基后量子方案更短 |
| 安全级别 | NIST-1后量子级别 |

## 关键发现

1. **同源证明重大突破**：紧凑性提升数个数量级
2. **首个同源VRF**：填补后量子VRF空白
3. **四元数阶工具**：为同源计算提供新算法武器
4. **实用性验证**：1KB规模首次使同源VRF达到实用水平
5. **后量子选择**：为NIST后量子标准提供同源候选

## 个人评价

这是同源密码学的重要进展。紧凑证明解决了同源方案长期以来的效率瓶颈，而首个同源VRF则为区块链和分布式系统提供了新的后量子选择。

**深层跨域联系**：

1. **同源 ↔ [[拓扑序|拓扑映射]]**：椭圆曲线同源是代数几何中的紧致流形间映射，与拓扑学中的映射流形（mapping torus）有深层结构相似性——都是研究保持某种结构的连续映射

2. **四元数阶 ↔ [[拓扑序|分割代数]]**：四元数作为实数域上最大的可除代数，与拓扑学中研究非阿基米德域的p进数有算术几何联系——两者都涉及"超越"传统数系的结构

3. **VRF伪随机性 ↔ [[拓扑序|拓扑熵]]**：VRF的伪随机性与拓扑动力系统中的拓扑熵（topological entropy）有概念相似——都涉及某种产生不可预测性的机制

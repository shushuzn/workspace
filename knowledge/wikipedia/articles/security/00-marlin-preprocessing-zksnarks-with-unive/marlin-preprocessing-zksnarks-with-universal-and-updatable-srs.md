---
id: marlin-preprocessing-zksnarks-with-universal-and-updatable-srs
title: Marlin: Preprocessing zkSNARKs with Universal and Updatable SRS
category: security
tags: [论文解读, ePrint:2019/1047]
eprint: 2019/1047
source: IACR ePrint
url: https://eprint.iacr.org/2019/1047
created: 2026-04-10T14:10:29.207Z
---

# Marlin: Preprocessing zkSNARKs with Universal and Updatable SRS

**IACR ePrint** | ePrint: 2019/1047 | **Author**: Alessandro Chiesa, Yuncong Hu, Mary Maller, Pratyush Mishra, Psi Vesely, Nicholas Ward

## 摘要

We present a methodology to construct preprocessing zkSNARKs where the structured reference string (SRS) is universal and updatable. This exploits a novel use of *holography* [Babai et al., STOC 1991], where fast verification is achieved provided the statement being checked is given in encoded form. We use our methodology to obtain a preprocessing zkSNARK where the SRS has linear size and arguments have constant size. Our construction improves on Sonic [Maller et al., CCS 2019], the prior state of the art in this setting, in all efficiency parameters: proving is an order of magnitude faster and verification is thrice as fast, even with smaller SRS size and argument size. Our construction is most efficient when instantiated in the algebraic group model (also used by Sonic), but we also demonstrate how to realize it under concrete knowledge assumptions. We implement and evaluate our construction. The core of our preprocessing zkSNARK is an efficient *algebraic holographic proof* (AHP) for rank-1 constraint satisfiability (R1CS) that achieves linear proof length and constant query complexity. Note: The updated version includes further optimizations to both the AHP and the compiler.

## 研究动机

SNARK的预处理（Preprocessing）问题是实用化的关键瓶颈：

- **Groth16**：电路专用，不同电路需不同可信Setup
- **Sonic**：通用+可更新SRS，但验证慢10倍于Groth16
- **Marlin目标**：在保持通用性的同时，将Sonic的验证速度提升3倍，证明速度提升10倍

核心挑战是如何让快速验证（需要某种编码形式）和通用性兼容——Marlin通过"全息证明"（Holography）技术解决。

## 核心方法

### 1. 代数全息证明（AHP）

Babai等人的全息证明（PCP）思想：验证者无需读取整个证明，只需查询编码证明的少量位置。

Marlin的核心创新是**代数全息证明（AHP）** for R1CS：

- 将约束满足问题编码为代数编码
- 验证者只需查询常数个编码位置
- 证明长度线性，查询复杂度常数

### 2. 线性大小SRS

与Sonic相同，Marlin的SRS大小与电路规模线性相关：

$$\text{SRS size} = O(|C|)$$

但Marlin的编码效率更高，相同安全级别下SRS更小。

### 3. 通用电路编译器

Marlin的AHP → SNARK编译器：

1. 用AHP生成全息证明
2. 用Fiat-Shamir变换实现非交互
3. 通过代数群承诺绑定证明

关键性质：同一SRS可用于任意电路（受限于最大电路规模）。

### 4. 与Sonic的对比

| 指标 | Sonic | Marlin |
|------|-------|--------|
| 证明时间 | 1x | 10x faster |
| 验证时间 | 3x | 1x |
| SRS大小 | 1x | 更小 |

## 关键发现

1. **数量级提速**：证明时间比Sonic快10倍
2. **3倍验证加速**：验证时间比Sonic快3倍
3. **线性SRS**：SRS大小与电路线性相关，但常数更小
4. **常数查询复杂度**：全息性质使得验证只需查询少量位置
5. **工业采用**：Marlin被多个零知识证明项目采用作为基础协议

## 个人评价

Marlin是SNARK效率进化史上的重要一步。它与PLONK同年出现（2019年），两者都解决了Sonic的效率问题，但技术路线不同：PLONK用Lagrange基，Marlin用代数全息证明。两者共同奠定了现代zkEVM的技术基础。

**深层跨域联系**：

1. **全息 ↔ 拓扑对偶**：全息原理（holography）将n维体上的信息编码到n-1维边界上，与拓扑量子场论中的边界-体对偶（bulk-boundary duality）有深刻类比——都是信息编码的几何化

2. **线性码 ↔ 拓扑码**：Marlin的线性大小SRS和常数查询，与拓扑量子计算中的表面码（surface code）有结构相似性——都通过几何编码实现高效的局部操作+全局验证

3. **范畴化**：Marlin的AHP→SNARK编译器是函子性的——将R1CS范畴映射到SNARK范畴，保持了约束结构

## 相关条目

- [[表面码]] — 表面码的拓扑编码与Marlin的代数全息证明有几何类比
- [[Chern-Simons理论]] — 边界-体对偶的全息原理是Chern-Simons理论的核心
- [[范畴化]] — Marlin的AHP编译器是R1CS→SNARK的函子

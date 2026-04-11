---
id: 230505904-revisiting-fully-homomorphic-encryption-schemes
title: [2305.05904] Revisiting Fully Homomorphic Encryption Schemes
category: security
tags: [论文解读, arXiv:2305.05904]
arxiv: 2305.05904
source: arXiv
url: https://arxiv.org/abs/2305.05904
created: 2026-04-10T14:34:31.468Z
---

# [2305.05904] Revisiting Fully Homomorphic Encryption Schemes

**arXiv** | arXiv: 2305.05904 | **Author**: 

## 摘要

Homomorphic encryption is a sophisticated encryption technique that allows computations on encrypted data to be done without the requirement for decryption. This trait makes homomorphic encryption appropriate for safe computation in sensitive data scenarios, such as cloud computing, medical data exchange, and financial transactions. The data is encrypted using a public key in homomorphic encryption, and the calculation is conducted on the encrypted data using an algorithm that retains the encryption. The computed result is then decrypted with a private key to acquire the final output. This abstract notion protects data while allowing complicated computations to be done on the encrypted data, resulting in a secure and efficient approach to analysing sensitive information. This article is intended to give a clear idea about the various fully Homomorphic Encryption Schemes present in the literature and analyse and compare the results of each of these schemes. Further, we also provide applications and open-source tools of homomorphic encryption schemes.

## 研究动机

同态加密（FHE）是隐私保护计算的核心技术，但仍缺乏系统性理解：

- **FHE发展迅速**：从2009年Gentry的开创性工作到如今多种实用方案
- **方案多样性**：FHE方案各有权衡（效率、安全性、密钥大小）
- **应用场景复杂**：云计算、医疗数据交换、金融交易各有不同需求
- **缺乏系统性比较**：开发者难以选择适合自己场景的方案

核心问题：各种FHE方案有什么异同？各有什么优缺点？如何选择？

## 核心方法

### 1. FHE方案分类

本文系统梳理了主要FHE方案：

| 方案 | 开创者 | 基础假设 | 特点 |
|------|--------|----------|------|
| **Gentry** | Craig Gentry (2009) | 格困难问题 | 首个完整FHE |
| **BGV** | Brakerski/Gentry/Vaikuntanathan | LWE/RLWE | 打包编码高效 |
| **BFV** | Fan-Vercauteren | RLWE | 整数算术友好 |
| **CKKS** | Cheon-Kim-Kim-Song | RLWE | 实数近似计算 |
| **TFHE** | Tartarus/FHEW | GSW | 快速比特操作 |
| **FHEW** | Ducas-Micciancio | GSW | 快速[[拓扑序|拓扑自举]] |

### 2. 性能比较

| 指标 | BGV/BFV | CKKS | TFHE/FHEW |
|------|---------|------|------------|
| 密文大小 | 中 | 中 | 大 |
| 计算速度 | 快（打包） | 快（打包） | 慢（逐比特） |
| 精度 | 精确 | 近似 | 精确 |
| [[拓扑序|拓扑自举]]速度 | 中 | 中 | 快 |

### 3. 应用场景映射

不同场景适合不同方案：
- **云隐私计算**：BGV/BFV（高效打包）
- **机器学习推理**：CKKS（实数近似）
- **安全比特协议**：TFHE（快速布尔操作）

### 4. 开源工具

| 工具 | 支持方案 | 语言 |
|------|---------|------|
| SEAL | BFV, CKKS, BGV | C++ |
| PALISADE | 多种 | C++ |
| HELib | BGV, CKKS | C++ |
| tfhe-rs | TFHE | Rust |

## 关键发现

1. **没有最优方案**：各方案有权衡，需根据场景选择
2. **打包编码是关键**：能显著提升批处理效率
3. **[[拓扑序|拓扑自举]]是瓶颈**：[[拓扑序|拓扑自举]]速度决定了FHE的实用边界
4. **硬件加速前景**：GPU/FPGA加速有潜力
5. **标准化进行中**：行业正在推动FHE标准化

## 个人评价

这篇综述为FHE的工程化应用提供了实用指南。它清晰地比较了各种方案的权衡，帮助开发者做出明智的选择。

**深层跨域联系**：

1. **格密码学 ↔ 拓扑学**：FHE基于格困难问题，而格在拓扑学中有深刻应用——[[辫群]]、晶体结构、拓扑[[拓扑序|拓扑不变量]]都与格有关

2. **打包编码 ↔ 拓扑[[拓扑序|拓扑紧化]]**：FHE的打包编码将多个值压缩到单个密文中，与拓扑[[拓扑序|拓扑紧化]]（compactification）有概念相似——都是信息的"压缩表示"

3. **[[拓扑序|拓扑自举]] ↔ 拓扑[[拓扑序|拓扑自举]]**：FHE的[[拓扑序|拓扑自举]]（bootstrapping）刷新密文，与拓扑学中的[[拓扑序|拓扑自举]]（bootstrap）有语义相似——都是某种"重新初始化"操作

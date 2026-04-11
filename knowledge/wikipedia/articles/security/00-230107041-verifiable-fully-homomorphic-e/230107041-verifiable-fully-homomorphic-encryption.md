---
id: 230107041-verifiable-fully-homomorphic-encryption
title: [2301.07041] Verifiable Fully Homomorphic Encryption
category: security
tags: [论文解读, arXiv:2301.07041]
arxiv: 2301.07041
source: arXiv
url: https://arxiv.org/abs/2301.07041
created: 2026-04-10T14:34:29.965Z
---

# [2301.07041] Verifiable Fully Homomorphic Encryption

**arXiv** | arXiv: 2301.07041 | **Author**: 

## 摘要

Fully Homomorphic Encryption (FHE) is seeing increasing real-world deployment to protect data in use by allowing computation over encrypted data. However, the same malleability that enables homomorphic computations also raises integrity issues, which have so far been mostly overlooked. While FHEs lack of integrity has obvious implications for correctness, it also has severe implications for confidentiality: a malicious server can leverage the lack of integrity to carry out interactive key-recovery attacks. As a result, virtually all FHE schemes and applications assume an honest-but-curious server who does not deviate from the protocol. In practice, however, this assumption is insufficient for a wide range of deployment scenarios. While there has been work that aims to address this gap, these have remained isolated efforts considering only aspects of the overall problem and fail to fully address the needs and characteristics of modern FHE schemes and applications. In this paper, we analyze existing FHE integrity approaches, present attacks that exploit gaps in prior work, and propose a new notion for maliciously-secure verifiable FHE. We then instantiate this new notion with a range of techniques, analyzing them and evaluating their performance in a range of different settings. We highlight their potential but also show where future work on tailored integrity solutions for FHE is still required.

## 研究动机

同态加密（FHE）面临一个被忽视的根本问题：**完整性缺失**：

- **FHE的可塑性**：同态计算能力来源于密文的数学结构，这本身也意味着可以被篡改
- **诚实但好奇假设**：现有FHE应用都假设服务器"诚实但好奇"——不偏离协议
- **恶意服务器攻击**：恶意服务器可以利用完整性缺失进行交互式密钥恢复攻击

核心问题：如何在FHE中实现可验证性，防御恶意服务器？

## 核心方法

### 1. FHE完整性分析

本文系统分析了FHE完整性的漏洞：

- **密文篡改**：攻击者修改密文导致错误计算结果
- **密钥恢复攻击**：恶意服务器利用完整性缺失进行密钥恢复
- **现有方案的局限**：之前的工作都是孤立尝试，未全面覆盖

### 2. 可验证FHE的新定义

提出**恶意安全可验证FHE**的形式化定义：

- **正确性**：密文正确对应明文
- **声音性**：无法伪造有效的计算结果
- **零知识性**：不泄露明文信息

### 3. 实现技术

本文给出多种可验证FHE实例化方案：

| 技术 | 效率 | 安全性 |
|------|------|--------|
| 承诺方案组合 | 高 | 强 |
| SNARK集成 | 中 | 强 |
| 交互式验证 | 低 | 最强 |

### 4. 性能评估

在多种场景下评估：
- 单服务器场景
- 多服务器场景
- 云外包场景

## 关键发现

1. **FHE完整性漏洞被低估**：之前的工作未充分重视此问题
2. **密钥恢复攻击可行**：恶意服务器可利用完整性缺失
3. **可验证FHE可行**：多种技术可实现恶意安全可验证FHE
4. **效率权衡**：更强的安全性带来更高的计算开销
5. **开放问题**：仍需针对现代FHE方案的定制化完整性方案

## 个人评价

这是FHE安全领域的重要突破，首次系统性地揭示了FHE完整性缺失的严重后果，并提出可行的解决方案。

**深层跨域联系**：

1. **可验证性 ↔ 拓扑不变量**：可验证FHE的"完整性验证"与拓扑不变量的"不变量检测"有方法论相似性——都是验证某种数学对象的性质是否保持不变

2. **恶意安全 ↔ 对抗鲁棒性**：恶意服务器攻击与AI对抗鲁棒性有深层联系——都研究在恶意参与者存在时的系统安全性

3. **承诺方案 ↔ 拓扑约束**：密文承诺与拓扑约束有概念相似性——都通过某种"绑定"机制保证信息的完整性

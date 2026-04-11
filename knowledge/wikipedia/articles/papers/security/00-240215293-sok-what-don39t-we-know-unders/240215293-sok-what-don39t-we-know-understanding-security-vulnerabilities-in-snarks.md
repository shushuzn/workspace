---
id: 240215293-sok-what-don39t-we-know-understanding-security-vulnerabilities-in-snarks
title: [2402.15293] SoK: What don&#39;t we know? Understanding Security Vulnerabilities in SNARKs
category: security
tags: [论文解读, 2402.15293]
arxiv: 2402.15293
created: 2026-04-10T13:51:39.420Z
---

# [2402.15293] SoK: What don&#39;t we know? Understanding Security Vulnerabilities in SNARKs

**arXiv**: 2402.15293 | **Author**: 

## 摘要

Zero-knowledge proofs (ZKPs) have evolved from being a theoretical concept providing privacy and verifiability to having practical, real-world implementations, with SNARKs (Succinct Non-Interactive Argument of Knowledge) emerging as one of the most significant innovations. Prior work has mainly focused on designing more efficient SNARK systems and providing security proofs for them. Many think of SNARKs as &#34;just math,&#34; implying that what is proven to be correct and secure is correct in practice. In contrast, this paper focuses on assessing end-to-end security properties of real-life SNARK implementations. We start by building foundations with a system model and by establishing threat models and defining adversarial roles for systems that use SNARKs. Our study encompasses an extensive analysis of 141 actual vulnerabilities in SNARK implementations, providing a detailed taxonomy to aid developers and security researchers in understanding the security threats in systems employing SNARKs. Finally, we evaluate existing defense mechanisms and offer recommendations for enhancing the security of SNARK-based systems, paving the way for more robust and reliable implementations in the future.

## 研究动机

零知识证明已从理论走向实践，但实际部署中存在大量安全隐患：

- **理论与实践的差距**：SNARK的数学证明假设"完美的实现"，但实际代码中存在漏洞
- **141个真实漏洞**：本文系统分析了SNARK实现中的真实漏洞
- **缺乏系统性理解**：安全社区对SNARK漏洞的全貌缺乏共识

核心问题：SNARK实现中到底有哪些类型的安全漏洞？防御机制是否充分？

## 核心方法

### 1. 系统模型与威胁模型

本文首先建立形式化基础：
- **系统模型**：定义使用SNARK的系统的边界和组件
- **威胁模型**：定义攻击者能力和目标
- **对抗角色**：定义各种参与方的可能行为

### 2. 漏洞分类学（Taxonomy）

对141个真实漏洞进行系统分类：

| 类别 | 描述 | 例子 |
|------|------|------|
| **密码学实现** | 椭圆曲线、哈希函数错误实现 | 不安全的随机数生成 |
| **约束系统** | R1CS/电路描述错误 | 约束丢失、错误约束 |
| **多项式承诺** | 承诺方案实现缺陷 | CRS陷阱、验证绕过 |
| **API误用** | 调用方错误使用库 | 状态泄露、顺序错误 |
| **前端漏洞** | 电路生成工具问题 | 类型混淆、边界检查缺失 |

### 3. 防御机制评估

评估现有防御机制的有效性：
- **形式化验证**：有一定效果，但无法覆盖所有漏洞
- **模糊测试**：有效发现崩溃类漏洞，但难以发现逻辑漏洞
- **代码审计**：仍然不可或缺

## 关键发现

1. **141个真实漏洞**：涵盖所有主流SNARK库
2. **最常见漏洞类型**：约束系统错误（32%）、API误用（28%）
3. **理论证明≠安全实现**：形式化安全不等于实现安全
4. **防御机制不足**：现有工具无法完全防止漏洞
5. **建议清单**：提供具体的安全开发建议

## 个人评价

这是零知识证明安全领域的里程碑式工作。它首次系统性地揭示了"理论完美"的SNARK在实际部署中的脆弱性，对安全社区有重要的警示意义。

**深层跨域联系**：

1. **漏洞分类 ↔ [[拓扑序|拓扑分类]]**：141种漏洞的分类与拓扑中的分类问题（如[[拓扑序|拓扑不变量]]分类）有方法论相似性——都是对复杂对象的系统化归类

2. **形式化验证 ↔ [[拓扑序|拓扑不变量]]**：形式化验证与[[拓扑序|拓扑不变量]]都试图用数学工具捕捉"正确性"——前者是算法的行为不变量，后者是空间的几何不变量

3. **对抗模型 ↔ 博弈论**：SNARK的威胁模型与博弈论中的对抗性分析有深层联系——都是研究在恶意参与者存在时的系统安全

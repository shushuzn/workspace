---
id: iam-te-quan-sheng-ji
title: IAM 特权升级
category: security
tags:
  - IAM
  - 特权升级
  - 云安全
  - Burau-Lyapunov
created: 2026-04-07
references: []
cross-references: []
---

# IAM 特权升级

**Privilege Escalation** — 攻击者通过一系列合法 IAM 操作，逐步提升自身权限，最终获得管理员或 root 级别访问权限的攻击路径。

## 攻击原理

云 IAM 系统（如 AWS IAM、Azure AD）中，权限以有向图形式组织：
- **节点**：用户、服务账号、角色
- **边**：权限委托（assume role、pass role）
- **边权重**：操作复杂度或时间成本

攻击者从低权限账号出发，通过图中可达路径逐步提升权限。每一步都是合法操作，但整体路径构成攻击。

```
普通用户 → ReadS3 → ListEC2 → DescribeInstance → CreateAccessKey → AdminUser
```

## 传统检测方法

| 方法 | 原理 | 局限性 |
|------|------|--------|
| 规则引擎 | 匹配已知攻击链 | 无法检测未知路径 |
| 行为异常 | 基线偏差告警 | 误报率高，无法量化潜力 |
| 图遍历 | 手工定义传递规则 | 无法捕捉系统性特征 |

## 关键发现

论文证明：**没有任何阿贝尔统计量能够替代 Burau-Lyapunov 指数（LE）**，即传统统计方法在根本上无法捕捉特权升级的结构性特征。这是因为特权升级路径具有非阿贝尔（non-abelian）性质——路径的"长度"不仅与中间节点有关，还与节点的**顺序**有关。

## 相关条目

- [[IAM 云身份与访问管理]] — 特权升级发生的系统环境
- [[辫群]] — LE 指数的数学基础，描述权限路径的非阿贝尔组合结构
- [[Burau-Lyapunov 指数]] — 量化特权升级潜力的核心指标

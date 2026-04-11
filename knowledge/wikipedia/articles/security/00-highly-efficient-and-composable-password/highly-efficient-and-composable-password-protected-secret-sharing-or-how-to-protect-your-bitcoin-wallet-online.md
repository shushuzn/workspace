---
id: highly-efficient-and-composable-password-protected-secret-sharing-or-how-to-protect-your-bitcoin-wallet-online
title: Highly-Efficient and Composable Password-Protected Secret Sharing (Or: How to Protect Your Bitcoin Wallet Online)
category: security
tags: [论文解读, ePrint:2016/144]
eprint: 2016/144
source: IACR ePrint
url: https://eprint.iacr.org/2016/144
created: 2026-04-10T14:45:15.349Z
---

# Highly-Efficient and Composable Password-Protected Secret Sharing (Or: How to Protect Your Bitcoin Wallet Online)

**IACR ePrint** | ePrint: 2016/144 | **Author**: Stanislaw Jarecki, Aggelos Kiayias, Hugo Krawczyk, Jiayu Xu

## 摘要

PPSS is a central primitive introduced by Bagherzandi et al [BJSL10] which allows a user to store a secret among n servers such that the user can later reconstruct the secret with the sole possession of a single password by contacting t+1 servers for t&lt;n. At the same time, an attacker breaking into t of these servers - and controlling all communication channels - learns nothing about the secret (or the password). Thus, PPSS schemes are ideal for on-line storing of valuable secrets when retrieval solely relies on a memorizable password. We show the most efficient Password-Protected Secret Sharing (PPSS) to date (and its implied Threshold-PAKE scheme), which is optimal in round communication as in Jarecki et al [JKK14] but which improves computation and communication complexity over that scheme requiring a single per-server exponentiation for the client and a single exponentiation for the server. As with the schemes from [JKK14] and Camenisch et al [CLLN14], we do not require secure channels or PKI other than in the initialization stage. We prove the security of our PPSS scheme in the Universally Composable (UC) model. For this we present a UC definition of PPSS that relaxes the UC formalism of [CLLN14] in a way that enables more efficient PPSS schemes (by dispensing with the need to extract the user&#39;s password in the simulation) and present a UC-based definition of Oblivious PRF (OPRF) that is more general than the (Verifiable) OPRF definition from [JKK14] and is also crucial for enabling our performance optimization.

## 研究动机

密码保护秘密分享（PPSS）是保护在线高价值资产的理想原语：

- **比特币钱包风险**：用户私钥一旦丢失无法恢复，被盗则资产全失
- **单点登录困境**：传统方案依赖单一密码，容易被钓鱼攻击
- **现有方案效率低下**：已有PPSS方案计算和通信开销过大

核心问题：如何在仅靠记忆密码的情况下，安全高效地存储和恢复高价值秘密？

## 核心方法

### 1. PPSS形式化定义

Bagherzandi等人引入的PPSS允许：
- 将秘密分布在n台服务器上
- 用户仅凭密码联系t+1台服务器即可恢复
- 攻击者即使攻陷t台服务器且控制所有通信，也完全无法获取秘密

### 2. 最优效率方案

本文构造了迄今最高效的PPSS方案：

关键优化：
- **单次指数运算**：客户端每服务器仅需一次指数运算
- **服务器单次运算**：服务器端仅需一次指数运算
- **无需安全信道**：初始化阶段外不需要PKI或安全信道

### 3. UC安全框架

在通用可组合（UC）模型中证明安全性：

- **UC-PPSS定义**：放松Camenisch等人在CLLN14中的定义
- **去除密码提取**：仿真器无需提取用户密码即可证明安全
- **通用OPRF定义**：提出比JKK14更通用的不经意PRF定义

### 4. 性能数据

| 指标 | 数值 |
|------|------|
| 客户端每服务器 | 单次指数运算 |
| 服务器端 | 单次指数运算 |
| 轮数 | 最优（与JKK14相同）|
| 信道要求 | 无需安全信道 |

## 关键发现

1. **效率重大突破**：相比前作计算和通信均大幅优化
2. **阈值PAKE方案**：隐含构造了高效的阈值PAKE协议
3. **UC安全证明**：首个在UC框架下证明安全的高效PPSS
4. **实用性验证**：适合保护比特币钱包等高价值在线资产
5. **无PKI需求**：初始化后可完全脱离PKI运行

## 个人评价

这是秘密分享工程化的里程碑工作。将学术上优美的PPSS方案变成真正可部署的实用协议，对保护加密货币钱包等高价值资产具有重要意义。

**深层跨域联系**：

1. **秘密分享 ↔ 拓扑分裂**：PPSS将秘密分布到多方，与拓扑中的流形分裂（manifold splitting）有概念相似——都是将整体信息分布到多个组件并通过某种方式重组

2. **阈值访问结构 ↔ 拓扑障碍**：t+1恢复门槛与拓扑中研究"跨越障碍所需的最小通道数"有结构相似性——都是某种临界条件

3. **不经意PRF ↔ 拓扑嵌入**：OPRF的"不经意性"（只知道输出而不知道函数）与拓扑嵌入（topological embedding）有概念相似——都是某种保持结构的映射

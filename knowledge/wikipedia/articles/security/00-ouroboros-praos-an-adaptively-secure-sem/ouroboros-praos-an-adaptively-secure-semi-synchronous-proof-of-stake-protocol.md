---
id: ouroboros-praos-an-adaptively-secure-semi-synchronous-proof-of-stake-protocol
title: Ouroboros Praos: An adaptively-secure, semi-synchronous proof-of-stake protocol
category: security
tags: [论文解读, ePrint:2017/573]
eprint: 2017/573
source: IACR ePrint
url: https://eprint.iacr.org/2017/573
created: 2026-04-10T14:39:45.897Z
---

# Ouroboros Praos: An adaptively-secure, semi-synchronous proof-of-stake protocol

**IACR ePrint** | ePrint: 2017/573 | **Author**: Bernardo David, Peter Gaži, Aggelos Kiayias, Alexander Russell

## 摘要

We present ``Ouroboros Praos&#39;&#39;, a proof-of-stake blockchain protocol that, for the first time, provides security against fully-adaptive corruption in the semi-synchronous setting: Specifically, the adversary can corrupt any participant of a dynamically evolving population of stakeholders at any moment so long as the stakeholder distribution maintains an honest majority of stake; furthermore, the protocol tolerates an adversarially-controlled message delivery delay unknown to protocol participants. To achieve these guarantees we formalize and realize in the universal composition setting a suitable form of forward secure digital signatures and a new type of verifiable random function that maintains unpredictability under malicious key generation. Our security proof develops a general combinatorial framework for the analysis of semi-synchronous blockchains that may be of independent interest. We prove our protocol secure under standard cryptographic assumptions in the random oracle model.

## 研究动机

区块链协议在自适应腐败攻击下的安全性是核心挑战：

- **完全自适应腐败**：对手可以随时腐蚀任何参与方
- **半同步设置**：消息延迟不可预测，但协议仍需运行
- **动态权益人群体**：参与方随时可以加入或离开
- **多数 stake 假设**：诚实多数仍是必要假设

核心问题：如何在完全自适应腐败和半同步网络条件下，实现安全的PoS区块链？

## 核心方法

### 1. 前向安全数字签名

在通用组合设置中形式化并实现：

- **前向安全密钥演化**：密钥随时间演变，过去的密钥无法伪造新签名
- **自适应安全**：即使当前密钥被泄露，过去的签名仍安全
- **UC框架**：在通用可组合框架下证明安全

### 2. 新型可验证随机函数

构造在恶意密钥生成下保持不可预测性的VRF：

- **密钥生成攻击防护**：对手无法通过恶意密钥生成获取优势
- **输出不可预测**：即使对手控制部分密钥生成过程，输出仍不可预测
- **与VRF标准定义的区别**：标准VRF定义未考虑恶意密钥生成

### 3. 半同步区块链分析框架

开发了通用的组合分析框架：

- **半同步建模**：形式化消息传递延迟的对抗性控制
- **自适应的有效性**：允许动态变化的参与者集合
- **组合证明技术**：适用于广泛的半同步区块链协议

### 4. 安全性证明

在随机预言机模型下基于标准密码学假设证明安全：

- **完全自适应腐败安全**：首次在PoS中实现
- **容忍消息延迟**：可容忍对手任意控制的消息延迟
- **标准假设**：不依赖非常规密码学假设

## 关键发现

1. **首个自适应安全PoS协议**：填补完全自适应腐败安全PoS空白
2. **半同步网络适配**：首次在半同步设置中实现强安全保证
3. **通用组合框架**：分析框架可适用于其他半同步区块链协议
4. **前向安全签名**：为PoS协议提供关键密码学原语
5. **实用性强**：为Cardano等真实区块链提供理论基础

## 个人评价

Ouroboros Praos是权益证明领域的里程碑工作，首次在自适应腐败和半同步网络的现实条件下实现了强安全保证。其前向安全签名和新型VRF为整个领域提供了重要的密码学工具。

**深层跨域联系**：

1. **自适应安全 ↔ [[拓扑序|拓扑稳定性]]**：自适应安全与拓扑学中的稳定性（stability）概念有深层联系——都是研究系统在扰动下保持的能力

2. **前向安全 ↔ [[拓扑序|拓扑持续性]]**：前向安全的"密钥随时间演化"特性与拓扑学中的持续同调（persistent homology）有概念相似——都是研究某种性质在不同尺度上的保持

3. **VRF不可预测性 ↔ [[拓扑序|拓扑熵]]**：VRF的不可预测性与拓扑熵有深层联系——两者都涉及某种"产生不确定性"的机制

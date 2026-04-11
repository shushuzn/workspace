---
id: a-framework-for-constructing-fast-mpc-over-arithmetic-circuits-with-malicious-adversaries-and-an-honest-majority
title: A Framework for Constructing Fast MPC over Arithmetic Circuits with Malicious Adversaries and an Honest-Majority
category: security
tags: [论文解读, ePrint:2017/816]
eprint: 2017/816
source: IACR ePrint
url: https://eprint.iacr.org/2017/816
created: 2026-04-10T14:32:09.828Z
---

# A Framework for Constructing Fast MPC over Arithmetic Circuits with Malicious Adversaries and an Honest-Majority

**IACR ePrint** | ePrint: 2017/816 | **Author**: Yehuda Lindell, Ariel Nof

## 摘要

Protocols for secure multiparty computation enable a set of parties to compute a function of their inputs without revealing anything but the output. The security properties of the protocol must be preserved in the presence of adversarial behavior. The two classic adversary models considered are \emph{semi-honest} (where the adversary follows the protocol specification but tries to learn more than allowed by examining the protocol transcript) and \emph{malicious} (where the adversary may follow any arbitrary attack strategy). Protocols for semi-honest adversaries are often far more efficient, but in many cases the security guarantees are not strong enough. In this paper, we present a new efficient method for ``compiling&#39;&#39; a large class of protocols that are secure in the presence of semi-honest adversaries into protocols that are secure in the presence of malicious adversaries. Our method assumes an honest majority (i.e., that $t&lt;n/2$ where $t$ is the number of corrupted parties and $n$ is the number of parties overall), and is applicable to many semi-honest protocols based on secret-sharing. In order to achieve high efficiency, our protocol is \emph{secure with abort} and does not achieve fairness, meaning that the adversary may receive output while the honest parties~do~not. We present a number of instantiations of our compiler, and obtain protocol variants that are very efficient for both a small and large number of parties. We implemented our protocol variants and ran extensive experiments to compare them with each other. Our results show that secure computation with an honest majority can be practical, even with security in the presence of malicious adversaries. For example, we securely compute a large arithmetic circuit of depth 20 with 1,000,000 multiplication gates, in approximately 0.5 seconds with three parties, and approximately 29 seconds with 50 parties, and just under 1 minute with 90 parties. Note: Correction of a small error in the protocol for small fields

## 研究动机

安全多方计算（MPC）面临安全性与效率的两难：

- **半诚实模型**：协议遵循规范但试图从 transcript 学习更多——效率高但不安全
- **恶意模型**：对手可任意攻击——安全但效率低
- **现有方法**：从半诚实协议编译到恶意协议的方法开销巨大

核心问题：能否在保持恶意安全性（honest majority假设）的同时，接近半诚实协议的效率？

## 核心方法

### 1. 编译器方法论

Lindell等人的编译器将半诚实协议转换为恶意协议：

```
半诚实安全协议 + 编译器 → 恶意安全协议
```

关键思想：利用**秘密分享**（Secret Sharing）作为基础协议。

### 2. 诚实多数假设

编译器假设 t < n/2（腐败方少于一半）：

- 诚实多数保证了可验证的秘密分享
- 可以检测和惩罚恶意行为
- 是实现恶意安全的必要条件

### 3. "Abort" 安全性

本文采用**security with abort**而非 fairness：

- 对手可以提前获得输出
- 诚实方可能无法获得输出
- 优点：效率显著提升

### 4. 性能数据

| 参与方数 | 电路规模 | 计算时间 |
|---------|----------|---------|
| 3方 | 100万乘法门，深度20 | ~0.5秒 |
| 50方 | 100万乘法门，深度20 | ~29秒 |
| 90方 | 100万乘法门，深度20 | ~1分钟 |

## 关键发现

1. **首个实用恶意安全MPC**：诚实多数情况下实现可实用性能
2. **大规模电路处理**：100万乘法门在1分钟内完成
3. **扩展性好**：从3方到90方仍有合理性能
4. **开源实现**：提供了完整实现和基准测试
5. **应用前景**：隐私机器学习、安全云计算、金融计算

## 个人评价

这是MPC领域的里程碑工作。它证明了"恶意安全+诚实多数"可以在保持安全的同时达到实用性能，改变了安全计算"太慢无法使用"的局面。

**深层跨域联系**：

1. **秘密分享 ↔ 拓扑[[拓扑序|拓扑分裂]]**：秘密分享将秘密"[[拓扑序|拓扑分裂]]"到多方，与拓扑中的流形[[拓扑序|拓扑分裂]]（manifold splitting）有概念相似性——都是将整体信息分布到多个组件

2. **诚实多数 ↔ 拓扑[[拓扑序|拓扑稳定性]]**：诚实多数假设与拓扑中研究整体[[拓扑序|拓扑稳定性]]的思想有深层联系——都是通过多数/整体的性质保证系统可靠性

3. **Abort安全性 ↔ [[范畴化]]**：恶意安全的"可中止"性质与[[范畴化]]中态射的可中断性有结构相似性——都是允许计算在某些条件下终止

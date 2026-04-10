---
id: burau-lyapunov-zhi-shu
title: Burau-Lyapunov 指数
category: math
tags:
  - Burau
  - Lyapunov
  - 辫群
  - 特权升级
  - 数学物理
created: 2026-04-07
references: []
cross-references: []
---

# Burau-Lyapunov 指数

**Burau-Lyapunov Exponent (LE)** — 论文提出的核心指标，用于量化 IAM 权限图中的特权升级潜力。名字来源于两个数学概念的神秘融合。

## 数学背景

### Burau 表示

Burau 表示是辫群（Braid Group）到矩阵群的一种同态映射。给定辫群的生成元 $\sigma_1, \sigma_2, \ldots, \sigma_{n-1}$，Burau 表示将每个生成元映射为一个 $n \times n$ 上三角矩阵，其迹（trace）包含辫的拓扑不变量。

### Lyapunov 指数

Lyapunov 指数来自混沌理论，衡量动力系统中相邻轨道的指数发散速率。正的 Lyapunov 指数表明系统具有敏感依赖性——初始条件的微小差异导致轨道的指数级偏离。

## 论文的核心创新

论文将两者结合，提出 **Burau-Lyapunov 指数（LE）** 作为 IAM 权限图的谱分析工具：

$$LE(\mathcal{G}) = \lambda_{max}(B(\mathcal{G}))$$

其中 $B(\mathcal{G})$ 是权限图 $\mathcal{G}$ 的 Burau 表示矩阵，$\lambda_{max}$ 是其最大特征值。

### 为什么 LE 能检测特权升级

特权升级路径具有**非阿贝尔**性质：
- 路径 A → B 与路径 B → A 的效果不同（矩阵乘法不交换）
- 路径的"复杂度"不仅与中间节点数量有关，还与节点的**排列顺序**有关

论文的关键定理：没有**任何阿贝尔统计量**（入度、出度、PageRank 等）能够复制 LE 的检测能力。这意味着传统的图分析方法在根本上无法捕捉特权升级的结构性特征。

## 在云安全中的应用

在真实 IAM 图（如 Solar、Stard Astrophysics 云环境）上，LE 指数的检测性能：
- **泛化能力强**：无需在目标环境上重新训练或调参
- **对阿贝尔方法免疫的攻击仍然可被检测**：如仅改变路径顺序的隐蔽攻击
- **可解释**：最大特征值对应的特征向量指出图中哪些节点是关键的"放大器"

## 相关条目

- [[辫群]] — LE 的数学基础
- [[IAM 特权升级]] — LE 的安全应用场景
- [[IAM 云身份与访问管理]] — LE 分析的权限图来源

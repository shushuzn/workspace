---
title: Chern-Simons理论
category: knowledge/physics
tags:
  - Chern-Simons理论
  - 拓扑量子场论
  - 纽结理论
created: 2026-04-07
---

# Chern-Simons理论

## 基本信息

- **原文**：Chern-Simons theory
- **类型**：三维拓扑场论
- **提出者**：Chern（1974），Simons（1970年代）
- **物理应用**：Witten（1989）用CS理论导出联络目不变量，获Fields奖

---

## 核心概念

### 拉格朗日量

$$L = \frac{k}{4\pi} \int Tr(A \wedge dA + \frac{2}{3} A \wedge A \wedge A)$$

其中：
- $A$：规范场（gauge field）
- $k$：拓扑荷（level，整数）
- $Tr$：矩阵迹

### 关键性质

1. **拓扑 Lagrangian**：只依赖于场的拓扑性质，不依赖于度规
2. **路径积分可计算**：虽然在三维度，但路径积分有明确定义
3. **不变量**：配分函数和算符期待值都是拓扑不变量

---

## 与联络目理论的关系

| 维度 | 理论 | 不变量 |
|------|------|--------|
| 3维 | Chern-Simons | 联络目不变量（linking number） |
| 3维 | Jones多项式 | 联络目的量子不变量 |

**Witten 1989**：CS路径积分自然给出Jones多项式

---

## 物理应用

1. **拓扑量子计算机**：Anyon编织实现拓扑保护的量子门
2. **拓扑相物质**：分数量子霍尔效应
3. **量子引力**：AdS/CFT对偶中的引力解
4. **拓扑绝缘体**：表面态的拓扑保护

---

## 数学延伸

- **三维流形不变量**：CS路径积分定义流形的不变量
- **几何Langlands对偶**：数论与物理的对偶
- **杨-巴克斯特方程**：可从CS理论导出

---

## 相关条目

- [[量子场论的数学物理]] — 山崎雅人演讲，包含CS理论与联络目的完整推导
- [[联络目不变量]] — CS理论的主要应用
- [[Yang-Baxter方程]] — CS理论中Wilson线的代数结构
- [[可积系统]] — CS理论与可积系统的关系
- [[Khovanov同调]] — CS理论高维推广的范畴化视角（Witten conjecture）
- [[拓扑量子计算]] — CS理论是Anyon统计的物理基础

---

## 参考文献

- Witten 1989 — "Quantum field theory and the Jones polynomial" (Communications in Mathematical Physics)
- Chern, Simons — 原始定义

---
title: Jones多项式
category: math
tags:
  - Jones多项式
  - 纽结不变量
  - 拓扑数学
created: 2026-04-07
---

# Jones多项式

## 基本信息

- **原文**：Jones polynomial
- **发现者**：Vaughan Jones (1984)
- **类型**：联络目不变量（knot invariant）
- **数学分支**：低维拓扑学 / 算子代数

---

## 定义

### skein关系

Jones多项式 $V(L)(t)$ 由以下关系定义：

$$t^{-1} V(L_+) - t V(L_-) = (t^{1/2} - t^{-1/2}) V(L_0)$$

其中 $L_+, L_-, L_0$ 在交叉处相同，仅交叉方向不同。

### 归一化

$$V(\text{平凡纽结}) = 1$$

---

## 与Yang-Baxter方程的关系

### 辫群表示

Jones多项式来自辫群 $B_n$ 的表示：

- 生成元 $\sigma_i$ 对应辫子交叉
- 表示矩阵 $R_i$ 满足 Yang-Baxter 方程
- Jones多项式 = 辫群表示的踪迹（trace）

### 统计力学连接

**Witten (1989)** 指出：Jones多项式可从Chern-Simons路径积分自然导出。

---

## 历史

| 年份 | 事件 |
|------|------|
| 1984 | Jones发现多项式不变量 |
| 1985 | HOMFLY-PT多项式（与Jones相关） |
| 1989 | Witten用Chern-Simons理论解释（Fields奖工作） |
| 1990 | Jones获Fields奖 |

---

## 应用

1. **拓扑量子计算**：Anyon编织实现量子门
2. **分子生物学**：DNA打结结构分析
3. **拓扑相分类**：物质相的拓扑分类
4. **低维拓扑**：四维流形的分类

---

## 相关条目

- [[联络目不变量]] — Jones是其中最重要的
- [[Chern-Simons理论]] — 物理上产生Jones多项式
- [[Yang-Baxter方程]] — Jones多项式的代数基础
- [[可积系统]] — Jones多项式与可积系统的深层联系
- [[拓扑量子计算]] — Jones多项式来自Anyon编织
- [[量子场论的数学物理]] — 山崎雅人演讲，包含Jones多项式的完整背景（Chern-Simons→Jones多项式的完整链条）

---

## 参考文献

- Jones 1985 — "A polynomial invariant of knots and links via braids"
- Witten 1989 — "Quantum field theory and the Jones polynomial"

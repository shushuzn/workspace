# Anyon

## 基本信息

- **原文**：Anyon
- **类型**：准粒子激发（quasiparticle）
- **特性**：二维系统中满足任意子统计（anyonic statistics）

---

## 统计类型

| 类型 | 维度 | 交换行为 | 例子 |
|------|------|----------|------|
| 玻色子 | 任意 | $\psi_1 \psi_2 = \psi_2 \psi_1$ | 光子 |
| 费米子 | 任意 | $\psi_1 \psi_2 = -\psi_2 \psi_1$ | 电子 |
| **Anyon** | **二维** | $\psi_1 \psi_2 = e^{i\theta} \psi_2 \psi_1$ | 分数量子霍尔态 |

---

## 核心特性

### 相位因子 $\theta$

- ** bosons**: $\theta = 0$
- ** fermions**: $\theta = \pi$
- ** Anyon**: $0 < \theta < \pi$（任意相位）

###编织（Braiding）

二维系统中，粒子交换产生拓扑相位：

$$|\psi\rangle \rightarrow e^{i\theta} |\psi\rangle$$

相位只依赖于拓扑路径，不依赖于交换速度。

---

## 物理实现

### 分数量子霍尔效应

| 系统 | Anyon类型 | 电荷 |
|------|-----------|------|
| $\nu = 1/3$ | Quasihole | $e/3$ |
| $\nu = 5/2$ | Pfaffian (Ising anyon) | $e/4$ |
| $\nu = 7/2$ | Fibonacci anyon | $e/4$ |

### Ising anyon vs Fibonacci anyon

| 性质 | Ising anyon | Fibonacci anyon |
|------|-------------|-----------------|
| 对应共形场论 | $SU(2)_2$ | $SU(2)_3$ |
| 基线融合域 | $\mathbf{1}, \sigma, \psi$ | $\mathbf{1}, \tau$ |
| 编织能力 | 子集（非通用） | **通用** |
| 实现难度 | 已观测 | 尚未确定性实现 |
| 典型平台 | $\nu = 5/2$ FQHE | $\nu = 7/2$ FQHE |

### 拓扑量子计算

**编织门**：
- Anyon编织实现量子门
- 拓扑保护（不受环境噪声影响）
- **Fibonacci anyon 可实现通用量子计算**（任意幺正门）
- 微软/Google等在研发

---

## 与辫群的关系

Anyon的统计由辫群 $B_n$ 的表示描述：

- 编织动作 = 辫群生成元 $\sigma_i$
- 任意子交换 = 辫群元素的乘积
- **拓扑量子计算** = 辫群表示的物理实现

---

## 相关条目

- [[Jones多项式]] — Anyon编织给出Jones多项式
- [[Chern-Simons理论]] — Anyon是CS理论的低能激发
- [[拓扑量子计算]] — Anyon编织实现量子门
- [[量子场论的数学物理]] — 山崎雅人演讲提到Anyon与拓扑量子计算

---

## 参考文献

- Wilczek 1982 — Anyon的提出
- Moore & Read 1991 — 非阿贝尔Anyon
- Freedman & Larsen & Wang 2002 — Anyon与拓扑量子计算

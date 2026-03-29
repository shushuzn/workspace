# A Universal Identity for Powers in Quadratic Algebras and a Matrix Derivation of a Fibonacci Identity

**arXiv**: [2603.19343v1](https://arxiv.org/abs/2603.19343)
**Author**: Marco Mantovanelli
**Date**: March 2026

---

## 1. Overview

The paper proves a **universal identity** for powers of elements in quadratic algebras, expressing $x^m$ in terms of $x$ and the identity. As an application, a general formula for powers of $2 \times 2$ matrices depending only on **trace** and **determinant** is derived. Applying this to the Fibonacci matrix yields a binomial expansion formula for $F_{nm}$.

Key insight: such Fibonacci identities arise from **general algebraic principles** rather than specific properties of Fibonacci numbers.

---

## 2. Core Theorem: Universal Quadratic Reduction

### Setup

Let $x$ be an element in an $R$-algebra satisfying a quadratic relation:

$$x^2 - tx + d = 0 \quad \text{for some } t, d \in R$$

Define the polynomials $P_m(t, d)$ recursively:

- $P_0(t, d) = 0$
- $P_1(t, d) = 1$
- $P_{m+1}(t, d) = t P_m(t, d) - d P_{m-1}(t, d)$ for $m \geq 1$

### Theorem (Universal Identity)

For all integers $m \geq 1$:

$$x^m = P_m(t, d) x - d P_{m-1}(t, d)$$

### Explicit Binomial Form

$$P_m(t, d) = \sum_{i=0}^{\lfloor (m-1)/2 \rfloor} \binom{m-1-i}{i} t^{m-1-2i} (-d)^i$$

---

## 3. Corollary: Matrix Formulation

For $M \in M_2(R)$ with $t = \operatorname{tr}(M)$ and $d = \det(M)$:

$$M^2 - tM + dI = 0 \quad \text{(Cayley-Hamilton)}$$

$$M^m = P_m(t, d) M - d P_{m-1}(t, d) I$$

This expresses any power of a $2 \times 2$ matrix purely in terms of its trace, determinant, and itself.

---

## 4. Application to Fibonacci Numbers

### Fibonacci Matrix

$$A = \begin{pmatrix} 1 & 1 \\ 1 & 0 \end{pmatrix}$$

Properties:
- $A^n = \begin{pmatrix} F_{n+1} & F_n \\ F_n & F_{n-1} \end{pmatrix}$
- $\operatorname{tr}(A^n) = L_n$ (Lucas number)
- $\det(A^n) = (-1)^n$

### Corollary 2 (Fibonacci Binomial Identity)

For all integers $m, n \geq 1$:

$$F_{nm} = F_n \sum_{i=0}^{\lfloor (m-1)/2 \rfloor} \binom{m-1-i}{i} L_n^{\,m-1-2i} (-1)^{i(n+1)}$$

### Chebyshev Connection

When $\sqrt{d}$ exists:

$$P_m(t, d) = d^{(m-1)/2} U_{m-1}\!\left(\frac{t}{2\sqrt{d}}\right)$$

where $U_k$ are Chebyshev polynomials of the second kind. This recovers **Vorobtsov's identity** as a special case.

---

## 5. Mathematical Significance

| Aspect | Significance |
|--------|-------------|
| **Universality** | The identity holds for ANY quadratic algebra, not just matrices |
| **Minimality** | Only requires trace ($t$) and determinant ($d$) — two invariants |
| **Systematic** | Fibonacci and Lucas identities are not coincidences — they follow from general algebraic structure |
| **Binomial Structure** | The formula is a binomial expansion with alternating signs and combinatorial coefficients |
| **Chebyshev Link** | Connects to classical orthogonal polynomials when $\sqrt{d}$ exists |

---

## 6. Related Work

- **Vorobtsov's identity** — recovered as a corollary of the universal formula

---

## 7. Files in This Directory

- `arxiv-2603.19343-quadratic-algebra-fibonacci.md` — this document
- `README.md` — overview

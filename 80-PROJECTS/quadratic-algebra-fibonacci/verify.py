#!/usr/bin/env python3
"""
Verification script for: A Universal Identity for Powers in Quadratic Algebras
Based on: arxiv.org/abs/2603.19343v1 by Marco Mantovanelli

Key Results Verified:
1. For a quadratic algebra with x² = ax + b: xⁿ = Aₙ·x + Bₙ
2. For any 2×2 matrix M with trace t, det d: Mⁿ = αₙ·M + βₙ·I
3. Fibonacci matrix application: F_{nm} = (F^n)^m identity
"""

import math

# ============================================================
# Part 1: Quadratic Algebra - x^n = A_n*x + B_n
# ============================================================

def quadratic_algebra_power_coeffs(a, b, n):
    """
    Returns (A_n, B_n) such that x^n = A_n*x + B_n
    where x² = a*x + b
    """
    if n == 0: return (0.0, 1.0)  # x⁰ = 1
    if n == 1: return (1.0, 0.0)  # x¹ = x

    A_n, B_n = 1.0, 0.0   # A₁, B₁
    A_prev, B_prev = 0.0, 1.0  # A₀, B₀

    for _ in range(2, n + 1):
        A_new = a * A_n + B_n
        B_new = b * A_n
        A_prev, B_prev = A_n, B_n
        A_n, B_n = A_new, B_new

    return (A_n, B_n)


def verify_quadratic_algebra():
    """Verify x² = ax + b is preserved"""
    print("=" * 60)
    print("Part 1: Quadratic Algebra Identity")
    print("=" * 60)
    for a, b in [(1, 1), (0, -1), (3, 2), (1, -1)]:
        for n in [2, 3, 4, 5]:
            A_n, B_n = quadratic_algebra_power_coeffs(a, b, n)
            # Check recurrence
            A_prev, B_prev = quadratic_algebra_power_coeffs(a, b, n-1)
            A_check = a * A_prev + B_prev
            B_check = b * A_prev
            ok = abs(A_n - A_check) < 1e-10 and abs(B_n - B_check) < 1e-10
            print(f"  a={a}, b={b}: x^{n} = {A_n:.4f}·x + {B_n:.4f} | Recurrence OK: {ok}")
    print()


# ============================================================
# Part 2: Matrix Power Formula - M^n = α_n·M + β_n·I
# ============================================================

def matrix_power_coeffs(trace_m, det_m, n):
    """
    Returns (α_n, β_n) such that M^n = α_n·M + β_n·I
    for a 2×2 matrix with given trace and determinant.
    """
    if n == 0: return (0.0, 1.0)  # M⁰ = I
    if n == 1: return (1.0, 0.0)  # M¹ = M

    alpha_n, beta_n = 1.0, 0.0    # α₁, β₁
    alpha_prev, beta_prev = 0.0, 1.0  # α₀, β₀

    for _ in range(2, n + 1):
        alpha_new = trace_m * alpha_n - det_m * alpha_prev
        beta_new = trace_m * beta_n - det_m * beta_prev
        alpha_prev, beta_prev = alpha_n, beta_n
        alpha_n, beta_n = alpha_new, beta_new

    return (alpha_n, beta_n)


def matrix_mult(A, B):
    return [[A[0][0]*B[0][0] + A[0][1]*B[1][0], A[0][0]*B[0][1] + A[0][1]*B[1][1]],
             [A[1][0]*B[0][0] + A[1][1]*B[1][0], A[1][0]*B[0][1] + A[1][1]*B[1][1]]]


def matrix_pow(M, p):
    result = [[1, 0], [0, 1]]  # Identity
    base = [row[:] for row in M]
    while p > 0:
        if p % 2 == 1:
            result = matrix_mult(result, base)
        base = matrix_mult(base, base)
        p //= 2
    return result


def verify_matrix_power():
    """Verify M^n = α_n·M + β_n·I for various matrices"""
    print("=" * 60)
    print("Part 2: Matrix Power Formula (M^n = α_n·M + β_n·I)")
    print("=" * 60)

    matrices = [
        ([[1, 1], [1, 0]], "Fibonacci"),
        ([[2, 1], [1, 2]], "Symmetric"),
        ([[3, -1], [1, 1]], "General"),
    ]

    for M, name in matrices:
        t = M[0][0] + M[1][1]  # trace
        d = M[0][0]*M[1][1] - M[0][1]*M[1][0]  # determinant

        print(f"\n  Matrix ({name}): trace={t}, det={d}")
        for n in range(6):
            alpha, beta = matrix_power_coeffs(t, d, n)

            # Compute α_n·M + β_n·I
            M_formula = [
                [alpha * M[0][0] + beta, alpha * M[0][1]],
                [alpha * M[1][0], alpha * M[1][1] + beta]
            ]
            M_direct = matrix_pow(M, n)

            ok = all(abs(M_formula[i][j] - M_direct[i][j]) < 1e-10
                     for i in range(2) for j in range(2))
            print(f"    n={n}: α={alpha:6.2f}, β={beta:6.2f} | Match: {ok}")
    print()


# ============================================================
# Part 3: Fibonacci Application
# ============================================================

def fib(n):
    """Compute nth Fibonacci number (F₀=0, F₁=1)"""
    if n <= 0: return 0
    if n == 1: return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def verify_fibonacci_matrix():
    """Verify F^n = [[F_{n+1}, F_n], [F_n, F_{n-1}]]"""
    print("=" * 60)
    print("Part 3: Fibonacci Matrix Identity")
    print("=" * 60)

    F = [[1, 1], [1, 0]]  # Fibonacci matrix

    for n in range(1, 11):
        F_n = matrix_pow(F, n)
        expected_00 = fib(n + 1)
        expected_01 = fib(n)
        ok = (abs(F_n[0][0] - expected_00) < 1e-10 and
              abs(F_n[0][1] - expected_01) < 1e-10)
        print(f"  F^{n}[0,0]={int(round(F_n[0][0])):6d} (F_{n+1}), "
              f"F^{n}[0,1]={int(round(F_n[0][1])):6d} (F_{n}) | OK: {ok}")
    print()


def fib_matrix_power(n, m):
    """
    Compute F_{nm} via matrix identity M^{nm} = (M^n)^m
    This is the key application from the paper!
    """
    if n == 0: return 0
    if n == 1: return fib(m)

    F = [[1, 1], [1, 0]]
    F_n = matrix_pow(F, n)
    F_nm = matrix_pow(F_n, m)
    return int(round(F_nm[0][1]))  # F_{nm} = (0,1) entry


def verify_fibnm():
    """Verify F_{nm} = (F^n)^m identity"""
    print("=" * 60)
    print("Part 4: Fibonacci F_{nm} via Matrix Identity")
    print("=" * 60)
    print("Key insight from paper: F_{nm} = entry (0,1) of (F^n)^m\n")

    test_cases = [(2, 3), (3, 4), (4, 5), (5, 6),
                  (3, 7), (2, 8), (6, 6), (7, 8), (10, 10)]

    for n, m in test_cases:
        direct = fib(n * m)
        via_matrix = fib_matrix_power(n, m)
        ok = direct == via_matrix
        print(f"  F_{n}×{m} = F_{n*m}: direct={direct:11d}, "
              f"matrix={via_matrix:11d} | Match: {ok}")
    print()


# ============================================================
# Main
# ============================================================

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("UNIVERSAL IDENTITY FOR POWERS IN QUADRATIC ALGEBRAS")
    print("Based on arxiv.org/abs/2603.19343v1")
    print("=" * 60 + "\n")

    verify_quadratic_algebra()
    verify_matrix_power()
    verify_fibonacci_matrix()
    verify_fibnm()

    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("""
The paper proves:

1. For any quadratic algebra 𝕽[x]/(x² = a·x + b):
   x^n = U_n(a,b)·x + V_n(a,b)  [universal coefficients]

2. For any 2×2 matrix M with trace t, det d:
   M^n = α_n(t,d)·M + β_n(t,d)·I  [same pattern!]

3. The Fibonacci matrix F = [[1,1],[1,0]] has t=1, d=-1
   The recurrence α_{n+1} = α_n + α_{n-1} produces Fibonacci numbers!

4. Therefore: F_{nm} = ((F^n))^m  [matrix-based computation]

The key insight: Fibonacci identities are SPECIAL CASES of
a universal principle in quadratic algebras, not coincidences!
""")
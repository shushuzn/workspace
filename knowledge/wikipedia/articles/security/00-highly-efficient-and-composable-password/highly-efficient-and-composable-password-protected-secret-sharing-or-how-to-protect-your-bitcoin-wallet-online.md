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

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

---
id: proof-carrying-data-without-succinct-arguments
title: Proof-Carrying Data without Succinct Arguments
category: security
tags: [论文解读, ePrint:2020/1618]
eprint: 2020/1618
source: IACR ePrint
url: https://eprint.iacr.org/2020/1618
created: 2026-04-10T14:15:28.113Z
---

# Proof-Carrying Data without Succinct Arguments

**IACR ePrint** | ePrint: 2020/1618 | **Author**: Benedikt Bünz, Alessandro Chiesa, William Lin, Pratyush Mishra, Nicholas Spooner

## 摘要

Proof-carrying data (PCD) is a powerful cryptographic primitive that enables mutually distrustful parties to perform distributed computations that run indefinitely. Known approaches to construct PCD are based on succinct non-interactive arguments of knowledge (SNARKs) that have a succinct verifier or a succinct accumulation scheme. In this paper we show how to obtain PCD without relying on SNARKs. We construct a PCD scheme given any non-interactive argument of knowledge (e.g., with linear-size arguments) that has a *split accumulation scheme*, which is a weak form of accumulation that we introduce. Moreover, we construct a transparent non-interactive argument of knowledge for R1CS whose split accumulation is verifiable via a (small) *constant number of group and field operations*. Our construction is proved secure in the random oracle model based on the hardness of discrete logarithms, and it leads, via the random oracle heuristic and our result above, to concrete efficiency improvements for PCD. Along the way, we construct a split accumulation scheme for Hadamard products under Pedersen commitments and for a simple polynomial commitment scheme based on Pedersen commitments. Our results are supported by a modular and efficient implementation. Note: Fix minor typo in abstract

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

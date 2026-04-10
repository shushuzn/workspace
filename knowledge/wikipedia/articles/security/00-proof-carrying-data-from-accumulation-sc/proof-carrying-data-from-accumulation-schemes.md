---
id: proof-carrying-data-from-accumulation-schemes
title: Proof-Carrying Data from Accumulation Schemes
category: security
tags: [论文解读, ePrint:2020/499]
eprint: 2020/499
source: IACR ePrint
url: https://eprint.iacr.org/2020/499
created: 2026-04-10T14:15:25.718Z
---

# Proof-Carrying Data from Accumulation Schemes

**IACR ePrint** | ePrint: 2020/499 | **Author**: Benedikt Bünz, Alessandro Chiesa, Pratyush Mishra, Nicholas Spooner

## 摘要

Recursive proof composition has been shown to lead to powerful primitives such as incrementally-verifiable computation (IVC) and proof-carrying data (PCD). All existing approaches to recursive composition take a succinct non-interactive argument of knowledge (SNARK) and use it to prove a statement about its own verifier. This technique requires that the verifier run in time sublinear in the size of the statement it is checking, a strong requirement that restricts the class of SNARKs from which PCD can be built. This in turn restricts the efficiency and security properties of the resulting scheme. Bowe, Grigg, and Hopwood (ePrint 2019/1021) outlined a novel approach to recursive composition, and applied it to a particular SNARK construction which does *not* have a sublinear-time verifier. However, they omit details about this approach and do not prove that it satisfies any security property. Nonetheless, schemes based on their ideas have already been implemented in software. In this work we present a collection of results that establish the theoretical foundations for a generalization of the above approach. We define an *accumulation scheme* for a non-interactive argument, and show that this suffices to construct PCD, even if the argument itself does not have a sublinear-time verifier. Moreover we give constructions of accumulation schemes for SNARKs, which yield PCD schemes with novel efficiency and security features.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

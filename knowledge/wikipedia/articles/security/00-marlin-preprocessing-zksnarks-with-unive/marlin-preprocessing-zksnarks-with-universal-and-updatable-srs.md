---
id: marlin-preprocessing-zksnarks-with-universal-and-updatable-srs
title: Marlin: Preprocessing zkSNARKs with Universal and Updatable SRS
category: security
tags: [论文解读, ePrint:2019/1047]
eprint: 2019/1047
source: IACR ePrint
url: https://eprint.iacr.org/2019/1047
created: 2026-04-10T14:10:29.207Z
---

# Marlin: Preprocessing zkSNARKs with Universal and Updatable SRS

**IACR ePrint** | ePrint: 2019/1047 | **Author**: Alessandro Chiesa, Yuncong Hu, Mary Maller, Pratyush Mishra, Psi Vesely, Nicholas Ward

## 摘要

We present a methodology to construct preprocessing zkSNARKs where the structured reference string (SRS) is universal and updatable. This exploits a novel use of *holography* [Babai et al., STOC 1991], where fast verification is achieved provided the statement being checked is given in encoded form. We use our methodology to obtain a preprocessing zkSNARK where the SRS has linear size and arguments have constant size. Our construction improves on Sonic [Maller et al., CCS 2019], the prior state of the art in this setting, in all efficiency parameters: proving is an order of magnitude faster and verification is thrice as fast, even with smaller SRS size and argument size. Our construction is most efficient when instantiated in the algebraic group model (also used by Sonic), but we also demonstrate how to realize it under concrete knowledge assumptions. We implement and evaluate our construction. The core of our preprocessing zkSNARK is an efficient *algebraic holographic proof* (AHP) for rank-1 constraint satisfiability (R1CS) that achieves linear proof length and constant query complexity. Note: The updated version includes further optimizations to both the AHP and the compiler.

## 研究动机

（人工填写）

## 核心方法

（人工填写）

## 关键发现

（人工填写）

## 个人评价

（人工填写）

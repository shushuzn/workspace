---
created: 2026-03-03 12:52:06
tags: [arxiv, csdc]
source: arxiv
category: cs.CR, cs.DC, cs.DS
---

# 2G2T: Constant-Size, Statistically Sound MSM Outsourcing

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23464
- **Authors:** Majid Khabbazian
- **Categories:** cs.CR, cs.DC, cs.DS
- **Original:** cs.DC
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csDC

## Abstract

Multi-scalar multiplication (MSM), defined as MSM(P, x) = sum_{i=1}^n x_i P_i, is a dominant computational kernel in discrete-logarithm-based cryptography and often becomes a bottleneck for verifiers and other resource-constrained clients. We present 2G2T, a simple protocol for verifiably outsourcing MSM to an untrusted server. After a one-time keyed setup for fixed bases P = (P1, ..., Pn) that produces a public merged-bases vector T and client secret state, the server answers each query x = (x1, ..., xn) with only two group elements: A claimed to equal MSM(P, x) and an auxiliary value B claimed to equal MSM(T, x). Verification requires a single length-n field inner product and a constant number of group operations (two scalar multiplications and one addition), while the server performs two MSMs. In our Ristretto255 implementation, verification is up to ~300x faster than computing the MSM locally using a highly optimized MSM routine for n up to 2^18, and the server-to-client response is constant-size (two compressed group elements, 64 bytes on Ristretto255). Despite its simplicity and efficiency, 2G2T achieves statistical soundness: for any (even computationally unbounded) adversarial server, the probability of accepting an incorrect result is at most 1/q per query, and at most e/q over e adaptive executions, in a prime-order group of size q.

## Notes

<!-- Add your notes here -->

## Tags

#csDC #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

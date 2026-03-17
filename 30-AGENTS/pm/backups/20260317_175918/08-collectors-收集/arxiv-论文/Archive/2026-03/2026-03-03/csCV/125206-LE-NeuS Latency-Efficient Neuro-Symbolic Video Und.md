---
created: 2026-03-03 12:52:06
tags: [arxiv, cscv]
source: arxiv
category: cs.CV
---

# LE-NeuS: Latency-Efficient Neuro-Symbolic Video Understanding via Adaptive Temporal Verification

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23553
- **Authors:** Shawn Liang, Sahil Shah, Chengwei Zhou, SP Sharan, Harsh Goel, Arnab Sanyal, Sandeep Chinchali, Gourav Datta
- **Categories:** cs.CV
- **Original:** cs.CV
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csCV

## Abstract

Neuro-symbolic approaches to long-form video question answering (LVQA) have demonstrated significant accuracy improvements by grounding temporal reasoning in formal verification. However, existing methods incur prohibitive latency overheads, up to 90x slower than base VLM prompting, rendering them impractical for latency-sensitive edge deployments. We present LE-NeuS, a latency-efficient neuro-symbolic framework that preserves the accuracy benefits of temporal logic-guided video understanding while drastically reducing inference latency. Our key insight is that the dominant computational bottleneck arises from sequential and dense proposition detection across video frames during automaton construction. We address this through two principled optimizations: (1) CLIP guided two-stage adaptive sampling that exploits visual redundancy to skip semantically similar frames while preserving temporal boundaries, and (2) batched proposition detection that parallelizes VLM inference across temporal windows. Theoretically, we derive latency bounds as a function of video length, proposition complexity, and sampling density, establishing conditions under which latency efficiency is achievable. Empirically, on LongVideoBench and Video-MME benchmarks deployed on NVIDIA H100 GPUs, LE-NeuS reduces the latency gap from 90x to approximately 10x while maintaining >10% accuracy gains on temporally complex queries.

## Notes

<!-- Add your notes here -->

## Tags

#csCV #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

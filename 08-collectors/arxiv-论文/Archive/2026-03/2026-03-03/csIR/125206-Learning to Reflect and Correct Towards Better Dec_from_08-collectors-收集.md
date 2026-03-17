---
created: 2026-03-03 12:52:06
tags: [arxiv, csir]
source: arxiv
category: cs.IR
---

# Learning to Reflect and Correct: Towards Better Decoding Trajectories for Large-Scale Generative Recommendation

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23639
- **Authors:** Haibo Xing, Hao Deng, Lingyu Mu, Jinxin Hu, Yu Zhang, Xiaoyi Zeng, Jing Zhang
- **Categories:** cs.IR
- **Original:** cs.IR
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csIR

## Abstract

Generative Recommendation (GR) has become a promising paradigm for large-scale recommendation systems. However, existing GR models typically perform single-pass decoding without explicit refinement, causing early deviations to accumulate and ultimately degrade recommendation quality. To tackle this problem, we propose GRC, which is, to our knowledge, the first structured reflection-correction framework for GR that extends standard decoding into a Generation-Reflection-Correction (GRC) process. Concretely, GRC introduces a supervised reflection-correction template that decomposes the decoding process into initial draft generation, multi-granular reflection, and reflection-guided correction, thereby enabling structured reflection and correction in the semantic token space. To further explore the enlarged refinement space introduced by the GRC process, we optimize the entire GRC trajectory with GRPO-based reinforcement learning, under a carefully designed reward function with token-level and trajectory-level signals. For efficient online serving, we propose an Entropy-Guided Reflection Scheduling (EGRS) strategy that dynamically allocates more correction budget to high-uncertainty decoding trajectories during beam search. Extensive experiments on real-world datasets show that GRC consistently outperforms six state-of-the-art baselines by up to 15.74%, and online A/B tests demonstrate its substantial practical value in large-scale industrial recommendation, delivering a 1.79% lift in advertising revenue with only modest latency overhead.

## Notes

<!-- Add your notes here -->

## Tags

#csIR #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

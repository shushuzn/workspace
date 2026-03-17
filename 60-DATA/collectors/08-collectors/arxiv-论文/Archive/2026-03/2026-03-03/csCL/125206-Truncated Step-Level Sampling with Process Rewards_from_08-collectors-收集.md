---
created: 2026-03-03 12:52:06
tags: [arxiv, cscl]
source: arxiv
category: cs.CL, cs.IR
---

# Truncated Step-Level Sampling with Process Rewards for Retrieval-Augmented Reasoning

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23440
- **Authors:** Chris Samarinas, Haw-Shiuan Chang, Hamed Zamani
- **Categories:** cs.CL, cs.IR
- **Original:** cs.CL
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csCL

## Abstract

Training large language models to reason with search engines via reinforcement learning is hindered by a fundamental credit assignment problem: existing methods such as Search-R1 provide only a sparse outcome reward after an entire multi-step trajectory, making it infeasible to attribute success or failure to individual reasoning and retrieval decisions. Process-reward methods like StepSearch alleviate this by introducing step-level supervision, but rely on heuristic rewards such as TF-IDF overlap with gold documents, and still sample k complete trajectories per example, retaining high gradient variance. We propose SLATE, a framework built on two complementary ideas: (1) truncated step-level sampling, which generates k trajectories that share a common prefix and differ only at the next step, and (2) dense LLM-as-judge rewards, which replace heuristic scoring with a capable LLM evaluator that assesses the quality of each reasoning step, search query, and answer, providing richer and more reliable supervision. We theoretically prove that under the same dense reward structure, truncated sampling reduces the variance of advantage estimates by up to a factor of T compared to full-trajectory sampling for T-step trajectories, yielding lower-variance, better-targeted policy gradients. Experiments on seven QA benchmarks confirm that SLATE consistently outperforms both sparse-reward and process-reward baselines, with the largest gains on harder multi-hop tasks and smaller models.

## Notes

<!-- Add your notes here -->

## Tags

#csCL #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

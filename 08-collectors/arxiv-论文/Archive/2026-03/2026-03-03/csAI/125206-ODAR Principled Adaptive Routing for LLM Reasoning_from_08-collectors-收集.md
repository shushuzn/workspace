---
created: 2026-03-03 12:52:06
tags: [arxiv, csai]
source: arxiv
category: cs.AI
---

# ODAR: Principled Adaptive Routing for LLM Reasoning via Active Inference

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23681
- **Authors:** Siyuan Ma, Bo Gao, Xiaojun Jia, Simeng Qin, Tianlin Li, Ke Ma, Xiaoshuang Jia, Wenqi Ren, Yang Liu
- **Categories:** cs.AI
- **Original:** cs.AI
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csAI

## Abstract

The paradigm of large language model (LLM) reasoning is shifting from parameter scaling to test-time compute scaling, yet many existing approaches still rely on uniform brute-force sampling (for example, fixed best-of-N or self-consistency) that is costly, hard to attribute, and can trigger overthinking with diminishing returns. We propose ODAR-Expert, an adaptive routing framework that optimizes the accuracy-efficiency trade-off via principled resource allocation. ODAR uses a difficulty estimator grounded in amortized active inference to dynamically route queries between a heuristic Fast Agent and a deliberative Slow Agent. We further introduce a free-energy-principled, risk-sensitive fusion mechanism that selects answers by minimizing a variational free energy objective, balancing log-likelihood with epistemic uncertainty (varentropy) as a principled alternative to ad hoc voting over heterogeneous candidates. Extensive evaluation across 23 benchmarks shows strong and consistent gains, including 98.2% accuracy on MATH and 54.8% on Humanity's Last Exam (HLE), while improving the compute-accuracy frontier under compute-matched settings. We also validate reproducibility on a fully open-source stack (Llama 4 + DeepSeek), where ODAR surpasses homogeneous sampling strategies while reducing computational costs by 82%. Overall, our results suggest that thinking-optimal scaling requires adaptive resource allocation with free-energy-based decision-making rather than simply increasing test-time compute.

## Notes

<!-- Add your notes here -->

## Tags

#csAI #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

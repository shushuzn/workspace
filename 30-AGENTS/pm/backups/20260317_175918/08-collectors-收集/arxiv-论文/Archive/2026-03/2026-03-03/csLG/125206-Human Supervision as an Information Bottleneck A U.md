---
created: 2026-03-03 12:52:06
tags: [arxiv, cslg]
source: arxiv
category: cs.LG, cs.AI
---

# Human Supervision as an Information Bottleneck: A Unified Theory of Error Floors in Human-Guided Learning

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23446
- **Authors:** Alejandro Rodriguez Dominguez
- **Categories:** cs.LG, cs.AI
- **Original:** cs.LG
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csLG

## Abstract

Large language models are trained primarily on human-generated data and feedback, yet they exhibit persistent errors arising from annotation noise, subjective preferences, and the limited expressive bandwidth of natural language. We argue that these limitations reflect structural properties of the supervision channel rather than model scale or optimization. We develop a unified theory showing that whenever the human supervision channel is not sufficient for a latent evaluation target, it acts as an information-reducing channel that induces a strictly positive excess-risk floor for any learner dominated by it. We formalize this Human-Bounded Intelligence limit and show that across six complementary frameworks (operator theory, PAC-Bayes, information theory, causal inference, category theory, and game-theoretic analyses of reinforcement learning from human feedback), non-sufficiency yields strictly positive lower bounds arising from the same structural decomposition into annotation noise, preference distortion, and semantic compression. The theory explains why scaling alone cannot eliminate persistent human-aligned errors and characterizes conditions under which auxiliary non-human signals (e.g., retrieval, program execution, tools) increase effective supervision capacity and collapse the floor by restoring information about the latent target. Experiments on real preference data, synthetic known-target tasks, and externally verifiable benchmarks confirm the predicted structural signatures: human-only supervision exhibits a persistent floor, while sufficiently informative auxiliary channels strictly reduce or eliminate excess error.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

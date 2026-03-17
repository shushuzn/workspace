---
created: 2026-03-03 12:52:06
tags: [arxiv, csai]
source: arxiv
category: cs.AI, cs.LG
---

# Construct, Merge, Solve & Adapt with Reinforcement Learning for the min-max Multiple Traveling Salesman Problem

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23579
- **Authors:** Guillem Rodr\'iguez-Corominas, Maria J. Blesa, Christian Blum
- **Categories:** cs.AI, cs.LG
- **Original:** cs.AI
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csAI

## Abstract

The Multiple Traveling Salesman Problem (mTSP) extends the Traveling Salesman Problem to m tours that start and end at a common depot and jointly visit all customers exactly once. In the min-max variant, the objective is to minimize the longest tour, reflecting workload balance. We propose a hybrid approach, Construct, Merge, Solve & Adapt with Reinforcement Learning (RL-CMSA), for the symmetric single-depot min-max mTSP. The method iteratively constructs diverse solutions using probabilistic clustering guided by learned pairwise q-values, merges routes into a compact pool, solves a restricted set-covering MILP, and refines solutions via inter-route remove, shift, and swap moves. The q-values are updated by reinforcing city-pair co-occurrences in high-quality solutions, while the pool is adapted through ageing and pruning. This combination of exact optimization and reinforcement-guided construction balances exploration and exploitation. Computational results on random and TSPLIB instances show that RL-CMSA consistently finds (near-)best solutions and outperforms a state-of-the-art hybrid genetic algorithm under comparable time limits, especially as instance size and the number of salesmen increase.

## Notes

<!-- Add your notes here -->

## Tags

#csAI #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

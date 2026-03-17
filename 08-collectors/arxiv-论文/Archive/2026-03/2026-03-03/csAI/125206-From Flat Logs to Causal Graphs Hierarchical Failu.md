---
created: 2026-03-03 12:52:06
tags: [arxiv, csai]
source: arxiv
category: cs.AI, cs.SE
---

# From Flat Logs to Causal Graphs: Hierarchical Failure Attribution for LLM-based Multi-Agent Systems

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23701
- **Authors:** Yawen Wang, Wenjie Wu, Junjie Wang, Qing Wang
- **Categories:** cs.AI, cs.SE
- **Original:** cs.SE
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csAI

## Abstract

LLM-powered Multi-Agent Systems (MAS) have demonstrated remarkable capabilities in complex domains but suffer from inherent fragility and opaque failure mechanisms. Existing failure attribution methods, whether relying on direct prompting, costly replays, or supervised fine-tuning, typically treat execution logs as flat sequences. This linear perspective fails to disentangle the intricate causal links inherent to MAS, leading to weak observability and ambiguous responsibility boundaries. To address these challenges, we propose CHIEF, a novel framework that transforms chaotic trajectories into a structured hierarchical causal graph. It then employs hierarchical oracle-guided backtracking to efficiently prune the search space via sybthesized virtual oracles. Finally, it implements counterfactual attribution via a progressive causal screening strategy to rigorously distinguish true root causes from propagated symptoms. Experiments on Who&amp;When benchmark show that CHIEF outperforms eight strong and state-of-the-art baselines on both agent- and step-level accuracy. Ablation studies further confirm the critical role of each proposed module.

## Notes

<!-- Add your notes here -->

## Tags

#csAI #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

---
created: 2026-03-03 12:52:06
tags: [arxiv, csdc]
source: arxiv
category: cs.DC, cs.AI, cs.PF
---

# Green or Fast? Learning to Balance Cold Starts and Idle Carbon in Serverless Computing

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23935
- **Authors:** Bowen Sun, Christos D. Antonopoulos, Evgenia Smirni, Bin Ren, Nikolaos Bellas, Spyros Lalis
- **Categories:** cs.DC, cs.AI, cs.PF
- **Original:** cs.DC
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csDC

## Abstract

Serverless computing simplifies cloud deployment but introduces new challenges in managing service latency and carbon emissions. Reducing cold-start latency requires retaining warm function instances, while minimizing carbon emissions favors reclaiming idle resources. This balance is further complicated by time-varying grid carbon intensity and varying workload patterns, under which static keep-alive policies are inefficient. We present LACE-RL, a latency-aware and carbon-efficient management framework that formulates serverless pod retention as a sequential decision problem. LACE-RL uses deep reinforcement learning to dynamically tune keep-alive durations, jointly modeling cold-start probability, function-specific latency costs, and real-time carbon intensity. Using the Huawei Public Cloud Trace, we show that LACE-RL reduces cold starts by 51.69% and idle keep-alive carbon emissions by 77.08% compared to Huawei's static policy, while achieving better latency-carbon trade-offs than state-of-the-art heuristic and single-objective baselines, approaching Oracle performance.

## Notes

<!-- Add your notes here -->

## Tags

#csDC #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

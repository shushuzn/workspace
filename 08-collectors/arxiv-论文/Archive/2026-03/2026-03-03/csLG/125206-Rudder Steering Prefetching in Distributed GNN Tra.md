---
created: 2026-03-03 12:52:06
tags: [arxiv, cslg]
source: arxiv
category: cs.LG, cs.AI, cs.DC, cs.MA, cs.PF
---

# Rudder: Steering Prefetching in Distributed GNN Training using LLM Agents

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23556
- **Authors:** Aishwarya Sarkar, Sayan Ghosh, Nathan Tallent, Aman Chadha, Tanya Roosta, Ali Jannesari
- **Categories:** cs.LG, cs.AI, cs.DC, cs.MA, cs.PF
- **Original:** cs.DC
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csLG

## Abstract

Large-scale Graph Neural Networks (GNNs) are typically trained by sampling a vertex's neighbors to a fixed distance. Because large input graphs are distributed, training requires frequent irregular communication that stalls forward progress. Moreover, fetched data changes with graph, graph distribution, sample and batch parameters, and caching polices. Consequently, any static prefetching method will miss crucial opportunities to adapt to different dynamic conditions. In this paper, we introduce Rudder, a software module embedded in the state-of-the-art AWS DistDGL framework, to autonomously prefetch remote nodes and minimize communication. Rudder's adaptation contrasts with both standard heuristics and traditional ML classifiers. We observe that the generative AI found in contemporary Large Language Models (LLMs) exhibits emergent properties like In-Context Learning (ICL) for zero-shot tasks, with logical multi-step reasoning. We find this behavior well-suited for adaptive control even with substantial undertraining. Evaluations using standard datasets and unseen configurations on the NERSC Perlmutter supercomputer show up to 91% improvement in end-to-end training performance over baseline DistDGL (no prefetching), and an 82% improvement over static prefetching, reducing communication by over 50%. Our code is available at https://github.com/aishwaryyasarkar/rudder-llm-agent.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

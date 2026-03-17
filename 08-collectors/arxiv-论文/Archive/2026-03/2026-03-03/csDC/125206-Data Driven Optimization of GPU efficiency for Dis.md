---
created: 2026-03-03 12:52:06
tags: [arxiv, csdc]
source: arxiv
category: cs.DC, cs.AI, cs.CL, cs.LG
---

# Data Driven Optimization of GPU efficiency for Distributed LLM Adapter Serving

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.24044
- **Authors:** Ferran Agullo, Joan Oliveras, Chen Wang, Alberto Gutierrez-Torre, Olivier Tardieu, Alaa Youssef, Jordi Torres, Josep Ll. Berral
- **Categories:** cs.DC, cs.AI, cs.CL, cs.LG
- **Original:** cs.DC
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csDC

## Abstract

Large Language Model (LLM) adapters enable low-cost model specialization, but introduce complex caching and scheduling challenges in distributed serving systems where hundreds of adapters must be hosted concurrently. While prior work has largely focused on latency minimization, resource efficiency through throughput maximization remains underexplored. This paper presents a data-driven pipeline that, for a given workload, computes an adapter placement that serves the workload with the minimum number of GPUs while avoiding request starvation and GPU memory errors. To that end, the approach identifies the maximum feasible throughput attainable on each GPU by leveraging accurate performance predictions learned from real serving behavior. The proposed pipeline integrates three components: (i) a Digital Twin (DT) tailored to LLM-adapter serving, (ii) a distilled machine learning (ML) model trained on DT-generated data, and (iii) a greedy placement algorithm that exploits ML-based performance estimates to maximize GPU efficiency. The DT emulates real system dynamics with high fidelity, achieving below 5% throughput estimation error while executing up to 90 times faster than full LLM benchmarking across both predictable and unpredictable workloads. The learned ML models further accelerate performance estimation with marginal accuracy degradation, enabling scalable optimization. Experimental results demonstrate that the pipeline substantially improves GPU efficiency by reducing the number of GPUs required to sustain target workloads. Beyond GPU efficiency, the pipeline can be adapted to alternative objectives, such as latency minimization, highlighting its versatility for future large-scale LLM serving infrastructures.

## Notes

<!-- Add your notes here -->

## Tags

#csDC #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

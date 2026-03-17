---
created: 2026-03-03 12:52:06
tags: [arxiv, csdc]
source: arxiv
category: cs.DC
---

# Hestia: Hyperthread-Level Scheduling for Cloud Microservices with Interference-Aware Attention

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23758
- **Authors:** Dingyu Yang, Fanyong Kong, Jie Dai, Shiyou Qian, Shuangwei Li, Jian Cao, Guangtao Xue, Gang Chen
- **Categories:** cs.DC
- **Original:** cs.DC
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csDC

## Abstract

Modern cloud servers routinely co-locate multiple latency-sensitive microservice instances to improve resource efficiency. However, the diversity of microservice behaviors, coupled with mutual performance interference under simultaneous multithreading (SMT), makes large-scale placement increasingly complex. Existing interference aware schedulers and isolation techniques rely on coarse core-level profiling or static resource partitioning, leaving asymmetric hyperthread-level heterogeneity and SMT contention dynamics largely unmodeled. We present Hestia, a hyperthread-level, interference-aware scheduling framework powered by self-attention. Through an extensive analysis of production traces encompassing 32,408 instances across 3,132 servers, we identify two dominant contention patterns -- sharing-core (SC) and sharing-socket (SS) -- and reveal strong asymmetry in their impact. Guided by these insights, Hestia incorporates (1) a self-attention-based CPU usage predictor that models SC/SS contention and hardware heterogeneity, and (2) an interference scoring model that estimates pairwise contention risks to guide scheduling decisions. We evaluate Hestia through large-scale simulation and a real production deployment. Hestia reduces the 95th-percentile service latency by up to 80\%, lowers overall CPU consumption by 2.3\% under the same workload, and surpasses five state-of-the-art schedulers by up to 30.65\% across diverse contention scenarios.

## Notes

<!-- Add your notes here -->

## Tags

#csDC #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

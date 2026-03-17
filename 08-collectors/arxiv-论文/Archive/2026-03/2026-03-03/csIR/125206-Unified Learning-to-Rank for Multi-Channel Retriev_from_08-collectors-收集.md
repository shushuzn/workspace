---
created: 2026-03-03 12:52:06
tags: [arxiv, csir]
source: arxiv
category: cs.IR
---

# Unified Learning-to-Rank for Multi-Channel Retrieval in Large-Scale E-Commerce Search

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23530
- **Authors:** Aditya Gaydhani, Guangyue Xu, Dhanush Kamath, Ankit Singh, Alex Li
- **Categories:** cs.IR
- **Original:** cs.IR
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csIR

## Abstract

Large-scale e-commerce search must surface a broad set of items from a vast catalog, ranging from bestselling products to new, trending, or seasonal items. Modern systems therefore rely on multiple specialized retrieval channels to surface products, each designed to satisfy a specific objective. A key challenge is how to effectively merge documents from these heterogeneous channels into a single ranked list under strict latency constraints while optimizing for business KPIs such as user conversion. Rank-based fusion methods such as Reciprocal Rank Fusion (RRF) and Weighted Interleaving rely on fixed global channel weights and treat channels independently, failing to account for query-specific channel utility and cross-channel interactions. We observe that multi-channel fusion can be reformulated as a query-dependent learning-to-rank problem over heterogeneous candidate sources. In this paper, we propose a unified ranking model that learns to merge and rank documents from multiple retrieval channels. We formulate the problem as a channel-aware learning-to-rank task that jointly optimizes clicks, add-to-carts, and purchases while incorporating channel-specific objectives. We further incorporate recent user behavioral signals to capture short-term intent shifts that are critical for improving conversion in multi-channel ranking. Our online A/B experiments show that the proposed approach outperforms rank-based fusion methods, leading to a +2.85\% improvement in user conversion. The model satisfies production latency requirements, achieving a p95 latency of under 50\,ms, and is deployed on Target.com.

## Notes

<!-- Add your notes here -->

## Tags

#csIR #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

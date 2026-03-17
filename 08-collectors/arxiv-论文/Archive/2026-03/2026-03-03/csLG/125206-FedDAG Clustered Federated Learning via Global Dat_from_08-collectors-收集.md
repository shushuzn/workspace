---
created: 2026-03-03 12:52:06
tags: [arxiv, cslg]
source: arxiv
category: cs.LG, cs.AI, cs.DC
---

# FedDAG: Clustered Federated Learning via Global Data and Gradient Integration for Heterogeneous Environments

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23504
- **Authors:** Anik Pramanik, Murat Kantarcioglu, Vincent Oria, Shantanu Sharma
- **Categories:** cs.LG, cs.AI, cs.DC
- **Original:** cs.LG
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csLG

## Abstract

Federated Learning (FL) enables a group of clients to collaboratively train a model without sharing individual data, but its performance drops when client data are heterogeneous. Clustered FL tackles this by grouping similar clients. However, existing clustered FL approaches rely solely on either data similarity or gradient similarity; however, this results in an incomplete assessment of client similarities. Prior clustered FL approaches also restrict knowledge and representation sharing to clients within the same cluster. This prevents cluster models from benefiting from the diverse client population across clusters. To address these limitations, FedDAG introduces a clustered FL framework, FedDAG, that employs a weighted, class-wise similarity metric that integrates both data and gradient information, providing a more holistic measure of similarity during clustering. In addition, FedDAG adopts a dual-encoder architecture for cluster models, comprising a primary encoder trained on its own clients' data and a secondary encoder refined using gradients from complementary clusters. This enables cross-cluster feature transfer while preserving cluster-specific specialization. Experiments on diverse benchmarks and data heterogeneity settings show that FedDAG consistently outperforms state-of-the-art clustered FL baselines in accuracy.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

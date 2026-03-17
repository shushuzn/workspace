---
created: 2026-03-03 12:52:06
tags: [arxiv, csir]
source: arxiv
category: cs.IR, cs.LG, cs.SI
---

# Geodesic Semantic Search: Learning Local Riemannian Metrics for Citation Graph Retrieval

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23665
- **Authors:** Brandon Yee, Lucas Wang, Kundana Kommini, Krishna Sharma
- **Categories:** cs.IR, cs.LG, cs.SI
- **Original:** cs.IR
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csIR

## Abstract

We present Geodesic Semantic Search (GSS), a retrieval system that learns node-specific Riemannian metrics on citation graphs to enable geometry-aware semantic search. Unlike standard embedding-based retrieval that relies on fixed Euclidean distances, \gss{} learns a low-rank metric tensor $\mL_i \in \R^{d \times r}$ at each node, inducing a local positive semi-definite metric $\mG_i = \mL_i \mL_i^\top + \eps \mI$. This parameterization guarantees valid metrics while keeping the model tractable. Retrieval proceeds via multi-source Dijkstra on the learned geodesic distances, followed by Maximal Marginal Relevance reranking and path coherence filtering. On citation prediction benchmarks with 169K papers, \gss{} achieves 23\% relative improvement in Recall@20 over SPECTER+FAISS baselines while providing interpretable citation paths. Our hierarchical coarse-to-fine search with k-means pooling reduces computational cost by 4$\times$ compared to flat geodesic search while maintaining 97\% retrieval quality. We provide theoretical analysis of when geodesic distances outperform direct similarity, characterize the approximation quality of low-rank metrics, and validate predictions empirically. Code and trained models are available at https://github.com/YCRG-Labs/geodesic-search.

## Notes

<!-- Add your notes here -->

## Tags

#csIR #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

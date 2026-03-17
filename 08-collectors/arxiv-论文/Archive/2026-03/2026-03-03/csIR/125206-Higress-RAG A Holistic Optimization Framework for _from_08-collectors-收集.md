---
created: 2026-03-03 12:52:06
tags: [arxiv, csir]
source: arxiv
category: cs.IR, cs.AI, cs.CL
---

# Higress-RAG: A Holistic Optimization Framework for Enterprise Retrieval-Augmented Generation via Dual Hybrid Retrieval, Adaptive Routing, and CRAG

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23374
- **Authors:** Weixi Lin
- **Categories:** cs.IR, cs.AI, cs.CL
- **Original:** cs.IR
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csIR

## Abstract

The integration of Large Language Models (LLMs) into enterprise knowledge management systems has been catalyzed by the Retrieval-Augmented Generation (RAG) paradigm, which augments parametric memory with non-parametric external data. However, the transition from proof-of-concept to production-grade RAG systems is hindered by three persistent challenges: low retrieval precision for complex queries, high rates of hallucination in the generation phase, and unacceptable latency for real-time applications. This paper presents a comprehensive analysis of the Higress RAG MCP Server, a novel, enterprise-centric architecture designed to resolve these bottlenecks through a "Full-Link Optimization" strategy. Built upon the Model Context Protocol (MCP), the system introduces a layered architecture that orchestrates a sophisticated pipeline of Adaptive Routing, Semantic Caching, Hybrid Retrieval, and Corrective RAG (CRAG). We detail the technical implementation of key innovations, including the Higress-Native Splitter for structure-aware data ingestion, the application of Reciprocal Rank Fusion (RRF) for merging dense and sparse retrieval signals, and a 50ms-latency Semantic Caching mechanism with dynamic thresholding. Experimental evaluations on domain-specific Higress technical documentation and blogs verify the system's architectural robustness. The results demonstrate that by optimizing the entire retrieval lifecycle - from pre-retrieval query rewriting to post-retrieval corrective evaluation - the Higress RAG system offers a scalable, hallucination-resistant solution for enterprise AI deployment.

## Notes

<!-- Add your notes here -->

## Tags

#csIR #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

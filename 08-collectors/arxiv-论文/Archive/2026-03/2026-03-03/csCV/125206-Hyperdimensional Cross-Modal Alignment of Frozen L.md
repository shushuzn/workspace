---
created: 2026-03-03 12:52:06
tags: [arxiv, cscv]
source: arxiv
category: cs.CV, cs.AI, cs.LG
---

# Hyperdimensional Cross-Modal Alignment of Frozen Language and Image Models for Efficient Image Captioning

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23588
- **Authors:** Abhishek Dalvi, Vasant Honavar
- **Categories:** cs.CV, cs.AI, cs.LG
- **Original:** cs.CV
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csCV

## Abstract

Large unimodal foundation models for vision and language encode rich semantic structures, yet aligning them typically requires computationally intensive multimodal fine-tuning. Such approaches depend on large-scale parameter updates, are resource intensive, and can perturb pretrained representations. Emerging evidence suggests, however, that independently trained foundation models may already exhibit latent semantic compatibility, reflecting shared structures in the data they model. This raises a fundamental question: can cross-modal alignment be achieved without modifying the models themselves? Here we introduce HDFLIM (HyperDimensional computing with Frozen Language and Image Models), a framework that establishes cross-modal mappings while keeping pretrained vision and language models fully frozen. HDFLIM projects unimodal embeddings into a shared hyperdimensional space and leverages lightweight symbolic operations -- binding, bundling, and similarity-based retrieval to construct associative cross-modal representations in a single pass over the data. Caption generation emerges from high-dimensional memory retrieval rather than iterative gradient-based optimization. We show that HDFLIM achieves performance comparable to end-to-end vision-language training methods and produces captions that are more semantically grounded than zero-shot baselines. By decoupling alignment from parameter tuning, our results suggest that semantic mapping across foundation models can be realized through symbolic operations on hyperdimensional encodings of the respective embeddings. More broadly, this work points toward an alternative paradigm for foundation model alignment in which frozen models are integrated through structured representational mappings rather than through large-scale retraining. The codebase for our implementation can be found at https://github.com/Abhishek-Dalvi410/HDFLIM.

## Notes

<!-- Add your notes here -->

## Tags

#csCV #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

---
created: 2026-03-03 12:52:06
tags: [arxiv, cscl]
source: arxiv
category: cs.CL, cs.AI, cs.IR
---

# Toward General Semantic Chunking: A Discriminative Framework for Ultra-Long Documents

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23370
- **Authors:** Kaifeng Wu, Junyan Wu, Qiang Liu, Jiarui Zhang, Wen Xu
- **Categories:** cs.CL, cs.AI, cs.IR
- **Original:** cs.CL
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csCL

## Abstract

Long-document topic segmentation plays an important role in information retrieval and document understanding, yet existing methods still show clear shortcomings in ultra-long text settings. Traditional discriminative models are constrained by fixed windows and cannot model document-level semantics; generative large language models can output paragraph boundaries, but inference is expensive and long inputs are difficult to support. To address these issues, we propose a discriminative segmentation model based on Qwen3-0.6B. On top of the backbone network, we add a cross-window context fusion layer and a boundary classification head, and combine them with an overlapping sliding-window strategy. Our model supports single-pass inputs of up to 13k tokens and can be extended to ultra-long documents for paragraph boundary detection. To further enhance downstream retrieval efficiency, we derive a vector fusion method with scalar correction, which compresses the representation of ultra-long segments into a single vector without semantic loss. Experiments on the Wikipedia long-document topic segmentation dataset WIKI-727K show that, compared with three generative models based on Qwen2-0.5B released by Jina, our method achieves a better macro-averaged F1 and delivers two orders of magnitude faster inference, substantially improving the practicality and scalability of long-document processing.

## Notes

<!-- Add your notes here -->

## Tags

#csCL #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

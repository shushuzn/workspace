---
created: 2026-03-03 12:52:06
tags: [arxiv, cslg]
source: arxiv
category: cs.LG
---

# Uncertainty-aware Language Guidance for Concept Bottleneck Models

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23495
- **Authors:** Yangyi Li, Mengdi Huai
- **Categories:** cs.LG
- **Original:** cs.LG
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csLG

## Abstract

Concept Bottleneck Models (CBMs) provide inherent interpretability by first mapping input samples to high-level semantic concepts, followed by a combination of these concepts for the final classification. However, the annotation of human-understandable concepts requires extensive expert knowledge and labor, constraining the broad adoption of CBMs. On the other hand, there are a few works that leverage the knowledge of large language models (LLMs) to construct concept bottlenecks. Nevertheless, they face two essential limitations: First, they overlook the uncertainty associated with the concepts annotated by LLMs and lack a valid mechanism to quantify uncertainty about the annotated concepts, increasing the risk of errors due to hallucinations from LLMs. Additionally, they fail to incorporate the uncertainty associated with these annotations into the learning process for concept bottleneck models. To address these limitations, we propose a novel uncertainty-aware CBM method, which not only rigorously quantifies the uncertainty of LLM-annotated concept labels with valid and distribution-free guarantees, but also incorporates quantified concept uncertainty into the CBM training procedure to account for varying levels of reliability across LLM-annotated concepts. We also provide the theoretical analysis for our proposed method. Extensive experiments on the real-world datasets validate the desired properties of our proposed methods.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

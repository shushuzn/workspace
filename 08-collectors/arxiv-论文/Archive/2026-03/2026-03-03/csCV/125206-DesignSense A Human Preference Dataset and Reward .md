---
created: 2026-03-03 12:52:06
tags: [arxiv, cscv]
source: arxiv
category: cs.CV, cs.AI
---

# DesignSense: A Human Preference Dataset and Reward Modeling Framework for Graphic Layout Generation

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23438
- **Authors:** Varun Gopal, Rishabh Jain, Aradhya Mathur, Nikitha SR, Sohan Patnaik, Sudhir Yarram, Mayur Hemani, Balaji Krishnamurthy, Mausoom Sarkar
- **Categories:** cs.CV, cs.AI
- **Original:** cs.CV
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csCV

## Abstract

Graphic layouts serve as an important and engaging medium for visual communication across different channels. While recent layout generation models have demonstrated impressive capabilities, they frequently fail to align with nuanced human aesthetic judgment. Existing preference datasets and reward models trained on text-to-image generation do not generalize to layout evaluation, where the spatial arrangement of identical elements determines quality. To address this critical gap, we introduce DesignSense-10k, a large-scale dataset of 10,235 human-annotated preference pairs for graphic layout evaluation. We propose a five-stage curation pipeline that generates visually coherent layout transformations across diverse aspect ratios, using semantic grouping, layout prediction, filtering, clustering, and VLM-based refinement to produce high-quality comparison pairs. Human preferences are annotated using a 4-class scheme (left, right, both good, both bad) to capture subjective ambiguity. Leveraging this dataset, we train DesignSense, a vision-language model-based classifier that substantially outperforms existing open-source and proprietary models across comprehensive evaluation metrics (54.6% improvement in Macro F1 over the strongest proprietary baseline). Our analysis shows that frontier VLMs remain unreliable overall and fail catastrophically on the full four-class task, underscoring the need for specialized, preference-aware models. Beyond the dataset, our reward model DesignSense yields tangible downstream gains in layout generation. Using our judge during RL based training improves generator win rate by about 3%, while inference-time scaling, which involves generating multiple candidates and selecting the best one, provides a 3.6% improvement. These results highlight the practical impact of specialized, layout-aware preference modeling on real-world layout generation quality.

## Notes

<!-- Add your notes here -->

## Tags

#csCV #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

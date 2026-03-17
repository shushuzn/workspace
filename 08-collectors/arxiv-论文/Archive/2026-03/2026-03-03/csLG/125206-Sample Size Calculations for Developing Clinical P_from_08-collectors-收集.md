---
created: 2026-03-03 12:52:06
tags: [arxiv, cslg]
source: arxiv
category: cs.LG, stat.AP, stat.ME
---

# Sample Size Calculations for Developing Clinical Prediction Models: Overview and pmsims R package

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23507
- **Authors:** Diana Shamsutdinova, Felix Zimmer, Oyebayo Ridwan Olaniran, Sarah Markham, Daniel Stahl, Gordon Forbes, Ewan Carr
- **Categories:** cs.LG, stat.AP, stat.ME
- **Original:** cs.LG
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csLG

## Abstract

Background: Clinical prediction models are increasingly used to inform healthcare decisions, but determining the minimum sample size for their development remains a critical and unresolved challenge. Inadequate sample sizes can lead to overfitting, poor generalisability, and biased predictions. Existing approaches, such as heuristic rules, closed-form formulas, and simulation-based methods, vary in flexibility and accuracy, particularly for complex data structures and machine learning models. Methods: We review current methodologies for sample size estimation in prediction modelling and introduce a conceptual framework that distinguishes between mean-based and assurance-based criteria. Building on this, we propose a novel simulation-based approach that integrates learning curves, Gaussian Process optimisation, and assurance principles to identify sample sizes that achieve target performance with high probability. This approach is implemented in pmsims, an open-source, model-agnostic R package. Results: Through case studies, we demonstrate that sample size estimates vary substantially across methods, performance metrics, and modelling strategies. Compared to existing tools, pmsims provides flexible, efficient, and interpretable solutions that accommodate diverse models and user-defined metrics while explicitly accounting for variability in model performance. Conclusions: Our framework and software advance sample size methodology for clinical prediction modelling by combining flexibility with computational efficiency. Future work should extend these methods to hierarchical and multimodal data, incorporate fairness and stability metrics, and address challenges such as missing data and complex dependency structures.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

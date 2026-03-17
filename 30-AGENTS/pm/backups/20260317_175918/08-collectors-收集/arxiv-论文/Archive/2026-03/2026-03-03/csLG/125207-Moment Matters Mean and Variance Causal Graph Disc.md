---
created: 2026-03-03 12:52:07
tags: [arxiv, cslg]
source: arxiv
category: stat.ML, cs.LG
---

# Moment Matters: Mean and Variance Causal Graph Discovery from Heteroscedastic Observational Data

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23602
- **Authors:** Yoichi Chikahara
- **Categories:** stat.ML, cs.LG
- **Original:** stat.ML
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:07
- **Domain:** csLG

## Abstract

Heteroscedasticity -- where the variance of a variable changes with other variables -- is pervasive in real data, and elucidating why it arises from the perspective of statistical moments is crucial in scientific knowledge discovery and decision-making. However, standard causal discovery does not reveal which causes act on the mean versus the variance, as it returns a single moment-agnostic graph, limiting interpretability and downstream intervention design. We propose a Bayesian, moment-driven causal discovery framework that infers separate \textit{mean} and \textit{variance} causal graphs from observational heteroscedastic data. We first derive the identification results by establishing sufficient conditions under which these two graphs are separately identifiable. Building on this theory, we develop a variational inference method that learns a posterior distribution over both graphs, enabling principled uncertainty quantification of structural features (e.g., edges, paths, and subgraphs). To address the challenges of parameter optimization in heteroscedastic models with two graph structures, we take a curvature-aware optimization approach and develop a prior incorporation technique that leverages domain knowledge on node orderings, improving sample efficiency. Experiments on synthetic, semi-synthetic, and real data show that our approach accurately recovers mean and variance structures and outperforms state-of-the-art baselines.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

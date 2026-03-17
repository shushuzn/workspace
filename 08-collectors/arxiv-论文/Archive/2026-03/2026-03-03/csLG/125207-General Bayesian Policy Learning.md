---
created: 2026-03-03 12:52:07
tags: [arxiv, cslg]
source: arxiv
category: stat.ML, cs.LG, econ.EM, math.ST, stat.ME, stat.TH
---

# General Bayesian Policy Learning

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23672
- **Authors:** Masahiro Kato
- **Categories:** stat.ML, cs.LG, econ.EM, math.ST, stat.ME, stat.TH
- **Original:** stat.ML
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:07
- **Domain:** csLG

## Abstract

This study proposes the General Bayes framework for policy learning. We consider decision problems in which a decision-maker chooses an action from an action set to maximize its expected welfare. Typical examples include treatment choice and portfolio selection. In such problems, the statistical target is a decision rule, and the prediction of each outcome $Y(a)$ is not necessarily of primary interest. We formulate this policy learning problem by loss-based Bayesian updating. Our main technical device is a squared-loss surrogate for welfare maximization. We show that maximizing empirical welfare over a policy class is equivalent to minimizing a scaled squared error in the outcome difference, up to a quadratic regularization controlled by a tuning parameter $\zeta>0$. This rewriting yields a General Bayes posterior over decision rules that admits a Gaussian pseudo-likelihood interpretation. We clarify two Bayesian interpretations of the resulting generalized posterior, a working Gaussian view and a decision-theoretic loss-based view. As one implementation example, we introduce neural networks with tanh-squashed outputs. Finally, we provide theoretical guarantees in a PAC-Bayes style.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

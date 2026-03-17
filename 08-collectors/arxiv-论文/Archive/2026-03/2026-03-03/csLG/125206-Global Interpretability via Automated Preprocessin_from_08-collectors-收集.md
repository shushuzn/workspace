---
created: 2026-03-03 12:52:06
tags: [arxiv, cslg]
source: arxiv
category: cs.LG, q-bio.QM, stat.ML
---

# Global Interpretability via Automated Preprocessing: A Framework Inspired by Psychiatric Questionnaires

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23459
- **Authors:** Eric V. Strobl
- **Categories:** cs.LG, q-bio.QM, stat.ML
- **Original:** cs.LG
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csLG

## Abstract

Psychiatric questionnaires are highly context sensitive and often only weakly predict subsequent symptom severity, which makes the prognostic relationship difficult to learn. Although flexible nonlinear models can improve predictive accuracy, their limited interpretability can erode clinical trust. In fields such as imaging and omics, investigators commonly address visit- and instrument-specific artifacts by extracting stable signal through preprocessing and then fitting an interpretable linear model. We adopt the same strategy for questionnaire data by decoupling preprocessing from prediction: we restrict nonlinear capacity to a baseline preprocessing module that estimates stable item values, and then learn a linear mapping from these stabilized baseline items to future severity. We refer to this two-stage method as REFINE (Redundancy-Exploiting Follow-up-Informed Nonlinear Enhancement), which concentrates nonlinearity in preprocessing while keeping the prognostic relationship transparently linear and therefore globally interpretable through a coefficient matrix, rather than through post hoc local attributions. In experiments, REFINE outperforms other interpretable approaches while preserving clear global attribution of prognostic factors across psychiatric and non-psychiatric longitudinal prediction tasks.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

---
created: 2026-03-03 12:52:06
tags: [arxiv, cslg]
source: arxiv
category: cs.LG
---

# Detoxifying LLMs via Representation Erasure-Based Preference Optimization

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23391
- **Authors:** Nazanin Mohammadi Sepahvand, Eleni Triantafillou, Hugo Larochelle, Doina Precup, Daniel M. Roy, Gintare Karolina Dziugaite
- **Categories:** cs.LG
- **Original:** cs.LG
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csLG

## Abstract

Large language models (LLMs) trained on webscale data can produce toxic outputs, raising concerns for safe deployment. Prior defenses, based on applications of DPO, NPO, and similar algorithms, reduce the likelihood of harmful continuations, but not robustly so: they are vulnerable to adversarial prompting and easily undone by fine-tuning-based relearning attacks. Indeed, research has shown that these edits to the model are superficial: linear probing reveals that harmful "directions" remain present in representations. To address this, we propose Representation Erasure-based Preference Optimization (REPO), reformulating detoxification as a token-level preference problem. Using a novel objective with preference data, we force the representations of toxic continuations to converge toward their benign counterparts. Our mechanistic analysis reveals that this granular approach is critical: unlike baselines, REPO induces deep, localized edits to toxicity-encoding neurons while preserving general model utility. Exhaustive evaluations show that REPO achieves state-of-the-art robustness, stopping sophisticated threats-including relearning attacks and enhanced GCG jailbreaks-where existing representation- and output-based methods fail.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

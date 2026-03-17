---
created: 2026-03-03 12:52:06
tags: [arxiv, cscl]
source: arxiv
category: cs.CL, cs.AI
---

# BRIDGE the Gap: Mitigating Bias Amplification in Automated Scoring of English Language Learners via Inter-group Data Augmentation

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23580
- **Authors:** Yun Wang, Xuansheng Wu, Jingyuan Huang, Lei Liu, Xiaoming Zhai, Ninghao Liu
- **Categories:** cs.CL, cs.AI
- **Original:** cs.CL
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csCL

## Abstract

In the field of educational assessment, automated scoring systems increasingly rely on deep learning and large language models (LLMs). However, these systems face significant risks of bias amplification, where model prediction gaps between student groups become larger than those observed in training data. This issue is especially severe for underrepresented groups such as English Language Learners (ELLs), as models may inherit and further magnify existing disparities in the data. We identify that this issue is closely tied to representation bias: the scarcity of minority (high-scoring ELL) samples makes models trained with empirical risk minimization favor majority (non-ELL) linguistic patterns. Consequently, models tend to under-predict ELL students who even demonstrate comparable domain knowledge but use different linguistic patterns, thereby undermining the fairness of automated scoring outcomes. To mitigate this, we propose BRIDGE, a Bias-Reducing Inter-group Data GEneration framework designed for low-resource assessment settings. Instead of relying on the limited minority samples, BRIDGE synthesizes high-scoring ELL samples by "pasting" construct-relevant (i.e., rubric-aligned knowledge and evidence) content from abundant high-scoring non-ELL samples into authentic ELL linguistic patterns. We further introduce a discriminator model to ensure the quality of synthetic samples. Experiments on California Science Test (CAST) datasets demonstrate that BRIDGE effectively reduces prediction bias for high-scoring ELL students while maintaining overall scoring performance. Notably, our method achieves fairness gains comparable to using additional real human data, offering a cost-effective solution for ensuring equitable scoring in large-scale assessments.

## Notes

<!-- Add your notes here -->

## Tags

#csCL #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

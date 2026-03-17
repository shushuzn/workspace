---
created: 2026-03-03 12:52:06
tags: [arxiv, cslg]
source: arxiv
category: cs.LG
---

# U-CAN: Utility-Aware Contrastive Attenuation for Efficient Unlearning in Generative Recommendation

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23400
- **Authors:** Zezheng Wu, Rui Wang, Xinghe Cheng, Yang Shao, Qing Yang, Jiapu Wang, Jingwei Zhang
- **Categories:** cs.LG
- **Original:** cs.LG
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csLG

## Abstract

Generative Recommendation (GenRec) typically leverages Large Language Models (LLMs) to redefine personalization as an instruction-driven sequence generation task. However, fine-tuning on user logs inadvertently encodes sensitive attributes into model parameters, raising critical privacy concerns. Existing Machine Unlearning (MU) techniques struggle to navigate this tension due to the Polysemy Dilemma, where neurons superimpose sensitive data with general reasoning patterns, leading to catastrophic utility loss under traditional gradient or pruning methods. To address this, we propose Utility-aware Contrastive AttenuatioN (U-CAN), a precision unlearning framework that operates on low-rank adapters. U-CAN quantifies risk by contrasting activations and focuses on neurons with asymmetric responses that are highly sensitive to the forgetting set but suppressed on the retention set. To safeguard performance, we introduce a utility-aware calibration mechanism that combines weight magnitudes with retention-set activation norms, assigning higher utility scores to dimensions that contribute strongly to retention performance. Unlike binary pruning, which often fragments network structure, U-CAN develop adaptive soft attenuation with a differentiable decay function to selectively down-scale high-risk parameters on LoRA adapters, suppressing sensitive retrieval pathways and preserving the topological connectivity of reasoning circuits. Experiments on two public datasets across seven metrics demonstrate that U-CAN achieves strong privacy forgetting, utility retention, and computational efficiency.

## Notes

<!-- Add your notes here -->

## Tags

#csLG #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

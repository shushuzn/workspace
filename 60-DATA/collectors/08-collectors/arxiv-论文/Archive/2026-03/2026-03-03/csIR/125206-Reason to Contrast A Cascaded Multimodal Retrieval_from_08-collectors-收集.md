---
created: 2026-03-03 12:52:06
tags: [arxiv, csir]
source: arxiv
category: cs.IR, cs.AI, cs.CL
---

# Reason to Contrast: A Cascaded Multimodal Retrieval Framework

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23369
- **Authors:** Xuanming Cui, Hong-You Chen, Hao Yu, Hao Yuan, Zihao Wang, Shlok Kumar Mishra, Hanchao Yu, Yonghuan Yang, Jun Xiao, Ser-Nam Lim, Jianpeng Cheng, Qi Guo, Xiangjun Fan
- **Categories:** cs.IR, cs.AI, cs.CL
- **Original:** cs.IR
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csIR

## Abstract

Traditional multimodal retrieval systems rely primarily on bi-encoder architectures, where performance is closely tied to embedding dimensionality. Recent work, Think-Then-Embed (TTE), shows that incorporating multimodal reasoning to elicit additional informative tokens before embedding can further improve retrieval. In this paper, we extend this paradigm with TTE-v2, a hybrid multimodal retrieval framework that introduces reasoning-driven performance scaling based on additional input token budget rather than model or embedding size. Our approach augments the initial multimodal retrieval with additional reasoning steps for reranking, enabling more expressive query-candidate interactions at test time. The reranking stage further provides fine-grained supervision for hard negative mining and false negative filtering, creating a feedback loop that effectively strengthens the upstream retriever. This cascaded design delivers substantial test-time improvements based on intermediate reasoning token scaling. Experiments on the MMEB-V2 benchmark demonstrate that TTE-v2-7B achieves a new state-of-the-art accuracy of 75.7%, and that TTE-v2-2B matches or surpasses leading 7B models trained with significantly larger external data. Our results highlight the promise of token-wise scaling as an alternative scaling paradigm for multimodal retrieval.

## Notes

<!-- Add your notes here -->

## Tags

#csIR #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

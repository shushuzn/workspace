---
created: 2026-03-03 12:52:06
tags: [arxiv, csai]
source: arxiv
category: cs.CR, cs.AI, cs.SE
---

# Learning to Generate Secure Code via Token-Level Rewards

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23407
- **Authors:** Jiazheng Quan, Xiaodong Li, Bin Wang, Guo An, Like Liu, Degen Huang, Lin Liu, Chengbin Hou
- **Categories:** cs.CR, cs.AI, cs.SE
- **Original:** cs.SE
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csAI

## Abstract

Large language models (LLMs) have demonstrated strong capabilities in code generation, yet they remain prone to producing security vulnerabilities. Existing approaches commonly suffer from two key limitations: the scarcity of high-quality security data and coarse-grained reinforcement learning reward signals. To address these challenges, we propose Vul2Safe, a new secure code generation framework that leverages LLM self-reflection to construct high-confidence repair pairs from real-world vulnerabilities, and further generates diverse implicit prompts to build the PrimeVul+ dataset. Meanwhile, we introduce SRCode, a novel training framework that pioneers the use of token-level rewards in reinforcement learning for code security, which enables the model to continuously attend to and reinforce critical fine-grained security patterns during training. Compared with traditional instance-level reward schemes, our approach allows for more precise optimization of local security implementations. Extensive experiments show that PrimeVul+ and SRCode substantially reduce security vulnerabilities in generated code while improving overall code quality across multiple benchmarks.

## Notes

<!-- Add your notes here -->

## Tags

#csAI #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

---
created: 2026-03-03 12:52:06
tags: [arxiv, csai]
source: arxiv
category: cs.AI, cs.SY, eess.SY
---

# PseudoAct: Leveraging Pseudocode Synthesis for Flexible Planning and Action Control in Large Language Model Agents

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23668
- **Authors:** Yihan (Logon),  Wen, Xin Chen
- **Categories:** cs.AI, cs.SY, eess.SY
- **Original:** cs.AI
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csAI

## Abstract

Large language model (LLM) agents typically rely on reactive decision-making paradigms such as ReAct, selecting actions conditioned on growing execution histories. While effective for short tasks, these approaches often lead to redundant tool usage, unstable reasoning, and high token consumption in complex long-horizon tasks involving branching, iteration, or multi-tool coordination. To address these limitations, this paper introduces PseudoAct, a novel framework for flexible planning and action control in LLM agents through pseudocode synthesis. Leveraging the ability of LLMs to express task-solving strategies as code, PseudoAct synthesizes a structured pseudocode plan that decomposes a task into subtasks and explicitly encodes control flow, including sequencing, conditionals, loops, parallel composition, and combinations of these logic primitives. Actions are then executed by following this global plan, making the decision logic explicit and temporally coherent. This design reduces redundant actions, prevents infinite loops, and avoids uninformative alternative exploration, enabling consistent and efficient long-horizon decision-making. Experiments on benchmark datasets show that our method significantly outperforms existing reactive agent approaches, achieving a 20.93% absolute gain in success rate on FEVER and setting a new state-of-the-art on HotpotQA.

## Notes

<!-- Add your notes here -->

## Tags

#csAI #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

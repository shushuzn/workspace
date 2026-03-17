---
created: 2026-03-03 12:52:06
tags: [arxiv, csse]
source: arxiv
category: cs.SE
---

# SGAgent: Suggestion-Guided LLM-Based Multi-Agent Framework for Repository-Level Software Repair

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23647
- **Authors:** Quanjun Zhang, Chengyu Gao, Yu Han, Ye Shang, Chunrong Fang, Zhenyu Chen, Liang Xiao
- **Categories:** cs.SE
- **Original:** cs.SE
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csSE

## Abstract

The rapid advancement of Large Language Models (LLMs) has led to the emergence of intelligent agents capable of autonomously interacting with environments and invoking external tools. Recently, agent-based software repair approaches have received widespread attention, as repair agents can automatically analyze and localize bugs, generate patches, and achieve state-of-the-art performance on repository-level benchmarks. However, existing approaches usually adopt a localize-then-fix paradigm, jumping directly from "where the bug is" to "how to fix it", leaving a fundamental reasoning gap. To this end, we propose SGAgent, a Suggestion-Guided multi-Agent framework for repository-level software repair, which follows a localize-suggest-fix paradigm. SGAgent introduces a suggestion phase to strengthen the transition from localization to repair. The suggester starts from the buggy locations and incrementally retrieves relevant context until it fully understands the bug, and then provides actionable repair suggestions. Moreover, we construct a Knowledge Graph from the target repository and develop a KG-based toolkit to enhance SGAgent's global contextual awareness and repository-level reasoning. Three specialized sub-agents (i.e., localizer, suggester, and fixer) collaborate to achieve automated end-to-end software repair. Experimental results on SWE-Bench show that SGAgent with Claude-3.5 achieves 51.3% repair accuracy, 81.2% file-level and 52.4% function-level localization accuracy with an average cost of $1.48 per instance, outperforming all baselines using the same base model. Furthermore, SGAgent attains 48% accuracy on VUL4J and VJBench for vulnerability repair, demonstrating strong generalization across tasks and programming languages.

## Notes

<!-- Add your notes here -->

## Tags

#csSE #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

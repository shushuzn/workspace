---
created: 2026-03-03 12:52:06
tags: [arxiv, csse]
source: arxiv
category: cs.SE, cs.CL
---

# SWE-rebench V2: Language-Agnostic SWE Task Collection at Scale

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23866
- **Authors:** Ibragim Badertdinov, Maksim Nekrashevich, Anton Shevtsov, Alexander Golubev
- **Categories:** cs.SE, cs.CL
- **Original:** cs.SE
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csSE

## Abstract

Software engineering agents (SWE) are improving rapidly, with recent gains largely driven by reinforcement learning (RL). However, RL training is constrained by the scarcity of large-scale task collections with reproducible execution environments and reliable test suites. Although a growing number of benchmarks have emerged, datasets suitable for training remain limited in scale and diversity or often target a limited set of high-resource language ecosystems. We introduce SWE-rebench V2, a language-agnostic automated pipeline for harvesting executable real-world SWE tasks and constructing RL training environments at scale. The pipeline synthesizes repository-specific installation and test procedures via an interactive setup agent, and filters unsound instances using an ensemble of LLM judges, validated against human-verified SWE-bench annotations. Using this pipeline, we construct a dataset of 32,000+ tasks spanning 20 languages and 3,600+ repositories, with pre-built images for reproducible execution. To further scale training data, we additionally release 120,000+ tasks with installation instructions, fail-to-pass tests and rich metadata, where the problem statement is generated based on the original pull request description. We validate the collected instances through a diagnostic study that covers a subset of tasks in five programming languages across seven popular models, and provide instance-level metadata that flags common confounders such as overly restrictive tests and underspecified descriptions. We release the datasets, the collection and execution code, and associated artifacts to enable large-scale training of SWE agents across diverse languages and repositories.

## Notes

<!-- Add your notes here -->

## Tags

#csSE #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

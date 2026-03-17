---
created: 2026-03-03 12:52:07
tags: [arxiv, csro]
source: arxiv
category: cs.RO, cs.SY, eess.SY
---

# MicroPush: A Simulator and Benchmark for Contact-Rich Cell Pushing and Assembly with a Magnetic Rolling Microrobot

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23607
- **Authors:** Yanda Yang, Sambeeta Das
- **Categories:** cs.RO, cs.SY, eess.SY
- **Original:** cs.RO
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:07
- **Domain:** csRO

## Abstract

Magnetic rolling microrobots enable gentle manipulation in confined microfluidic environments, yet autonomy for contact-rich behaviors such as cell pushing and multi-target assembly remains difficult to develop and evaluate reproducibly. We present MicroPush, an open-source simulator and benchmark suite for magnetic rolling microrobots in cluttered 2D scenes. MicroPush combines an overdamped interaction model with contact-aware stick--slip effects, lightweight near-field damping, optional Poiseuille background flow, and a calibrated mapping from actuation frequency to free-space rolling speed. On top of the simulator core, we provide a modular planning--control stack with a two-phase strategy for contact establishment and goal-directed pushing, together with a deterministic benchmark protocol with fixed tasks, staged execution, and unified CSV logging for single-object transport and hexagonal assembly. We report success, time, and tracking metrics, and an actuation-variation measure $E_{\Delta\omega}$. Results show that controller stability dominates performance under flow disturbances, while planner choice can influence command smoothness over long-horizon sequences via waypoint progression. MicroPush enables reproducible comparison and ablation of planning, control, and learning methods for microscale contact-rich micromanipulation.

## Notes

<!-- Add your notes here -->

## Tags

#csRO #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

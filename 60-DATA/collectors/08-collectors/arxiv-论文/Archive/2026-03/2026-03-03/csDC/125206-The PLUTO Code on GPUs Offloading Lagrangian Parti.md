---
created: 2026-03-03 12:52:06
tags: [arxiv, csdc]
source: arxiv
category: astro-ph.HE, astro-ph.IM, cs.DC
---

# The PLUTO Code on GPUs: Offloading Lagrangian Particle Methods

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23434
- **Authors:** Alessio Suriano, Stefano Truzzi, Agnese Costa, Marco Rossazza, Nitin Shukla, Andrea Mignone, Vittoria Berta, Claudio Zanni
- **Categories:** astro-ph.HE, astro-ph.IM, cs.DC
- **Original:** cs.DC
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csDC

## Abstract

The Lagrangian Particles (LP) module of the PLUTO code offers a powerful simulation tool to predict the non-thermal emission produced by shock accelerated particles in large-scale relativistic magnetized astrophysics flows. The LPs represent ensembles of relativistic particles with a given energy distribution which is updated by solving the relativistic cosmic ray transport equation. The approach consistently includes the effects of adiabatic expansion, synchrotron and inverse Compton emission. The large scale nature of such systems creates boundless computational demand which can only be satisfied by targeting modern computing hardware such as Graphic Processing Units (GPUs). In this work we presents the GPU-compatible C++ re-design of the LP module, that, by means of the programming model OpenACC and the Message Passing Interface library, is capable of targeting both single commercial GPUs as well as multi-node (pre-)exascale computing facilities. The code has been benchmarked up to 28672 parallel CPUs cores and 1024 parallel GPUs demonstrating $\sim(80-90)\%$ weak scaling parallel efficiency and good strong scaling capabilities. Our results demonstrated a speedup of $6$ times when solving that same benchmark test with 128 full GPU nodes (4GPUs per node) against the same amount of full high-end CPU nodes (112 cores per node). Furthermore, we conducted a code verification by comparing its prediction to corresponding analytical solutions for two test cases. We note that this work is part of broader project that aims at developing gPLUTO, the novel and revised GPU-ready implementation of its legacy.

## Notes

<!-- Add your notes here -->

## Tags

#csDC #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

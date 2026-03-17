---
created: 2026-03-03 12:52:06
tags: [arxiv, csro]
source: arxiv
category: cs.RO, cs.SY, eess.SY
---

# Refining Almost-Safe Value Functions on the Fly

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23478
- **Authors:** Sander Tonkens, Sosuke Kojima, Chenhao Liu, Judy Masri, Sylvia Herbert
- **Categories:** cs.RO, cs.SY, eess.SY
- **Original:** cs.RO
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csRO

## Abstract

Control Barrier Functions (CBFs) are a powerful tool for ensuring robotic safety, but designing or learning valid CBFs for complex systems is a significant challenge. While Hamilton-Jacobi Reachability provides a formal method for synthesizing safe value functions, it scales poorly and is typically performed offline, limiting its applicability in dynamic environments. This paper bridges the gap between offline synthesis and online adaptation. We introduce refineCBF for refining an approximate CBF - whether analytically derived, learned, or even unsafe - via warm-started HJ reachability. We then present its computationally efficient successor, HJ-Patch, which accelerates this process through localized updates. Both methods guarantee the recovery of a safe value function and can ensure monotonic safety improvements during adaptation. Our experiments validate our framework's primary contribution: in-the-loop, real-time adaptation, in simulation (with detailed value function analysis) and on physical hardware. Our experiments on ground vehicles and quadcopters show that our framework can successfully adapt to sudden environmental changes, such as new obstacles and unmodeled wind disturbances, providing a practical path toward deploying formally guaranteed safety in real-world settings.

## Notes

<!-- Add your notes here -->

## Tags

#csRO #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

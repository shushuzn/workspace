---
created: 2026-03-03 12:52:07
tags: [arxiv, cssy]
source: arxiv
category: eess.SY, cs.SY
---

# Neural Luenberger state observer for nonautonomous nonlinear systems

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.24252
- **Authors:** Moritz Woelk, Jarod Morris, Wentao Tang
- **Categories:** eess.SY, cs.SY
- **Original:** cs.SY
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:07
- **Domain:** csSY

## Abstract

This work proposes a method for model-free synthesis of a state observer for nonlinear systems with manipulated inputs, where the observer is trained offline using a historical or simulation dataset of state measurements. We use the structure of the Kazantzis-Kravaris/Luenberger (KKL) observer, extended to nonautonomous systems by adding an additional input-affine term to the linear time-invariant (LTI) observer-state dynamics, which determines a nonlinear injective mapping of the true states. Both this input-affine term and the nonlinear mapping from the observer states to the system states are learned from data using fully connected feedforward multi-layer perceptron neural networks. Furthermore, we theoretically prove that trained neural networks, when given new input-output data, can be used to observe the states with a guaranteed error bound. To validate the proposed observer synthesis method, case studies are performed on a bioreactor and a Williams-Otto reactor.

## Notes

<!-- Add your notes here -->

## Tags

#csSY #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

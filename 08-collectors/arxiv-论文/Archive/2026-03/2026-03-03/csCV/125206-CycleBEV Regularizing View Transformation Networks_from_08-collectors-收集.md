---
created: 2026-03-03 12:52:06
tags: [arxiv, cscv]
source: arxiv
category: cs.CV, cs.AI
---

# CycleBEV: Regularizing View Transformation Networks via View Cycle Consistency for Bird's-Eye-View Semantic Segmentation

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23575
- **Authors:** Jeongbin Hong, Dooseop Choi, Taeg-Hyun An, Kyounghwan An, Kyoung-Wook Min
- **Categories:** cs.CV, cs.AI
- **Original:** cs.CV
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csCV

## Abstract

Transforming image features from perspective view (PV) space to bird's-eye-view (BEV) space remains challenging in autonomous driving due to depth ambiguity and occlusion. Although several view transformation (VT) paradigms have been proposed, the challenge still remains. In this paper, we propose a new regularization framework, dubbed CycleBEV, that enhances existing VT models for BEV semantic segmentation. Inspired by cycle consistency, widely used in image distribution modeling, we devise an inverse view transformation (IVT) network that maps BEV segmentation maps back to PV segmentation maps and use it to regularize VT networks during training through cycle consistency losses, enabling them to capture richer semantic and geometric information from input PV images. To further exploit the capacity of the IVT network, we introduce two novel ideas that extend cycle consistency into geometric and representation spaces. We evaluate CycleBEV on four representative VT models covering three major paradigms using the large-scale nuScenes dataset. Experimental results show consistent improvements -- with gains of up to 0.74, 4.86, and 3.74 mIoU for drivable area, vehicle, and pedestrian classes, respectively -- without increasing inference complexity, since the IVT network is used only during training. The implementation code is available at https://github.com/JeongbinHong/CycleBEV.

## Notes

<!-- Add your notes here -->

## Tags

#csCV #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

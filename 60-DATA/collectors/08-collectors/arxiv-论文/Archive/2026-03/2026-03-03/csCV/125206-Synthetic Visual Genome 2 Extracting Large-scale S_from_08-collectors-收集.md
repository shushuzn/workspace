---
created: 2026-03-03 12:52:06
tags: [arxiv, cscv]
source: arxiv
category: cs.CV
---

# Synthetic Visual Genome 2: Extracting Large-scale Spatio-Temporal Scene Graphs from Videos

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23543
- **Authors:** Ziqi Gao, Jieyu Zhang, Wisdom Oluchi Ikezogwo, Jae Sung Park, Tario G. You, Daniel Ogbu, Chenhao Zheng, Weikai Huang, Yinuo Yang, Winson Han, Quan Kong, Rajat Saini, Ranjay Krishna
- **Categories:** cs.CV
- **Original:** cs.CV
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csCV

## Abstract

We introduce Synthetic Visual Genome 2 (SVG2), a large-scale panoptic video scene graph dataset. SVG2 contains over 636K videos with 6.6M objects, 52.0M attributes, and 6.7M relations, providing an order-of-magnitude increase in scale and diversity over prior spatio-temporal scene graph datasets. To create SVG2, we design a fully automated pipeline that combines multi-scale panoptic segmentation, online-offline trajectory tracking with automatic new-object discovery, per-trajectory semantic parsing, and GPT-5-based spatio-temporal relation inference. Building on this resource, we train TRaSER, a video scene graph generation model. TRaSER augments VLMs with a trajectory-aligned token arrangement mechanism and new modules: an object-trajectory resampler and a temporal-window resampler to convert raw videos and panoptic trajectories into compact spatio-temporal scene graphs in a single forward pass. The temporal-window resampler binds visual tokens to short trajectory segments to preserve local motion and temporal semantics, while the object-trajectory resampler aggregates entire trajectories to maintain global context for objects. On the PVSG, VIPSeg, VidOR and SVG2 test datasets, TRaSER improves relation detection by +15 to 20%, object prediction by +30 to 40% over the strongest open-source baselines and by +13% over GPT-5, and attribute prediction by +15%. When TRaSER's generated scene graphs are sent to a VLM for video question answering, it delivers a +1.5 to 4.6% absolute accuracy gain over using video only or video augmented with Qwen2.5-VL's generated scene graphs, demonstrating the utility of explicit spatio-temporal scene graphs as an intermediate representation.

## Notes

<!-- Add your notes here -->

## Tags

#csCV #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

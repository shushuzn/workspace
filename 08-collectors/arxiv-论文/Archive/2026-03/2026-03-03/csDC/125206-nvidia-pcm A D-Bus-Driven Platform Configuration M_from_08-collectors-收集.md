---
created: 2026-03-03 12:52:06
tags: [arxiv, csdc]
source: arxiv
category: cs.DC
---

# nvidia-pcm: A D-Bus-Driven Platform Configuration Manager for OpenBMC Environments

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.24237
- **Authors:** Harinder Singh
- **Categories:** cs.DC
- **Original:** cs.DC
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csDC

## Abstract

GPU-accelerated server platforms that share most of their hardware architecture often require separate firmware images due to minor hardware differences--different component identifiers, thermal profiles, or interconnect topologies. I built nvidia-pcm to eliminate that overhead. nvidia-pcm is a platform configuration manager for NVBMC, NVIDIA's OpenBMC-based firmware distribution, that enables a single firmware image to serve multiple platform variants. At boot, nvidia-pcm queries hardware identity data over D-Bus and exports the correct platform-specific configuration as environment variables. Downstream services read those variables without knowing or caring which hardware variant they are running on. The result is that platform differences are captured entirely in declarative JSON files, not in separate build artifacts. This paper describes the architecture, implementation, and deployment impact of nvidia-pcm, and shares lessons learned from solving the platform-identity problem at a deliberately minimal level of abstraction--prioritizing adoption simplicity over comprehensive hardware modeling.

## Notes

<!-- Add your notes here -->

## Tags

#csDC #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

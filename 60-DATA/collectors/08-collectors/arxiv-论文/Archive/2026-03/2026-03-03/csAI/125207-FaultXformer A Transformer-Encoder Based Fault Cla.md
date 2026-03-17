---
created: 2026-03-03 12:52:07
tags: [arxiv, csai]
source: arxiv
category: eess.SY, cs.AI, cs.LG, cs.SY
---

# FaultXformer: A Transformer-Encoder Based Fault Classification and Location Identification model in PMU-Integrated Active Electrical Distribution System

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.24254
- **Authors:** Kriti Thakur, Alivelu Manga Parimi, Mayukha Pal
- **Categories:** eess.SY, cs.AI, cs.LG, cs.SY
- **Original:** cs.SY
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:07
- **Domain:** csAI

## Abstract

Accurate fault detection and localization in electrical distribution systems is crucial, especially with the increasing integration of distributed energy resources (DERs), which inject greater variability and complexity into grid operations. In this study, FaultXformer is proposed, a Transformer encoder-based architecture developed for automatic fault analysis using real-time current data obtained from phasor measurement unit (PMU). The approach utilizes time-series current data to initially extract rich temporal information in stage 1, which is crucial for identifying the fault type and precisely determining its location across multiple nodes. In Stage 2, these extracted features are processed to differentiate among distinct fault types and identify the respective fault location within the distribution system. Thus, this dual-stage transformer encoder pipeline enables high-fidelity representation learning, considerably boosting the performance of the work. The model was validated on a dataset generated from the IEEE 13-node test feeder, simulated with 20 separate fault locations and several DER integration scenarios, utilizing current measurements from four strategically located PMUs. To demonstrate robust performance evaluation, stratified 10-fold cross-validation is performed. FaultXformer achieved average accuracies of 98.76% in fault type classification and 98.92% in fault location identification across cross-validation, consistently surpassing conventional deep learning baselines convolutional neural network (CNN), recurrent neural network (RNN). long short-term memory (LSTM) by 1.70%, 34.95%, and 2.04% in classification accuracy and by 10.82%, 40.89%, and 6.27% in location accuracy, respectively. These results demonstrate the efficacy of the proposed model with significant DER penetration.

## Notes

<!-- Add your notes here -->

## Tags

#csAI #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

---
created: 2026-03-03 12:52:06
tags: [arxiv, cscl]
source: arxiv
category: cs.CL
---

# FHIRPath-QA: Executable Question Answering over FHIR Electronic Health Records

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23479
- **Authors:** Michael Frew, Nishit Bheda, Bryan Tripp
- **Categories:** cs.CL
- **Original:** cs.CL
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csCL

## Abstract

Though patients are increasingly granted digital access to their electronic health records (EHRs), existing interfaces may not support precise, trustworthy answers to patient-specific questions. Large language models (LLM) show promise in clinical question answering (QA), but retrieval-based approaches are computationally inefficient, prone to hallucination, and difficult to deploy over real-life EHRs. In this work, we introduce FHIRPath-QA, the first open dataset and benchmark for patient-specific QA that includes open-standard FHIRPath queries over real-world clinical data. We propose a text-to-FHIRPath QA paradigm that shifts reasoning from free-text generation to FHIRPath query synthesis, significantly reducing LLM usage. Built on MIMIC-IV on FHIR Demo, the dataset pairs over 14k natural language questions in patient and clinician phrasing with validated FHIRPath queries and answers. Further, we demonstrate that state-of-the-art LLMs struggle to deal with ambiguity in patient language and perform poorly in FHIRPath query synthesis. However, they benefit strongly from supervised fine-tuning. Our results highlight that text-to-FHIRPath synthesis has the potential to serve as a practical foundation for safe, efficient, and interoperable consumer health applications, and our dataset and benchmark serve as a starting point for future research on the topic. The full dataset and generation code is available at: https://github.com/mooshifrew/fhirpath-qa.

## Notes

<!-- Add your notes here -->

## Tags

#csCL #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

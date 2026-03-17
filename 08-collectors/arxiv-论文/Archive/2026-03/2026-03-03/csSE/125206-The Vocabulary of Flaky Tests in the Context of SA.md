---
created: 2026-03-03 12:52:06
tags: [arxiv, csse]
source: arxiv
category: cs.SE
---

# The Vocabulary of Flaky Tests in the Context of SAP HANA

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23957
- **Authors:** Alexander Berndt, Zolt\'an Nochta, Thomas Bach
- **Categories:** cs.SE
- **Original:** cs.SE
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csSE

## Abstract

Background. Automated test execution is an important activity to gather information about the quality of a software project. So-called flaky tests, however, negatively affect this process. Such tests fail seemingly at random without changes to the code and thus do not provide a clear signal. Previous work proposed to identify flaky tests based on the source code identifiers in the test code. So far, these approaches have not been evaluated in a large-scale industrial setting. Aims. We evaluate approaches to identify flaky tests and their root causes based on source code identifiers in the test code in a large-scale industrial project. Method. First, we replicate previous work by Pinto et al. in the context of SAP HANA. Second, we assess different feature extraction techniques, namely TF-IDF and TF-IDFC-RF. Third, we evaluate CodeBERT and XGBoost as classification models. For a sound comparison, we utilize both the data set from previous work and two data sets from SAP HANA. Results. Our replication shows similar results on the original data set and on one of the SAP HANA data sets. While the original approach yielded an F1-Score of 0.94 on the original data set and 0.92 on the SAP HANA data set, our extensions achieve F1-Scores of 0.96 and 0.99, respectively. The reliance on external data sources is a common root cause for test flakiness in the context of SAP HANA. Conclusions. The vocabulary of a large industrial project seems to be slightly different with respect to the exact terms, but the categories for the terms, such as remote dependencies, are similar to previous empirical findings. However, even with rather large F1-Scores, both finding source code identifiers for flakiness and a black box prediction have limited use in practice as the results are not actionable for developers.

## Notes

<!-- Add your notes here -->

## Tags

#csSE #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

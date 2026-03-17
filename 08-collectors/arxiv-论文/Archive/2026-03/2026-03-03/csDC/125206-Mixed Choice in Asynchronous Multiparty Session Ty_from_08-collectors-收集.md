---
created: 2026-03-03 12:52:06
tags: [arxiv, csdc]
source: arxiv
category: cs.DC, cs.FL, cs.MA, cs.PL, cs.SE
---

# Mixed Choice in Asynchronous Multiparty Session Types

## Metadata
- **Source:** Arxiv
- **Link:** https://arxiv.org/abs/2602.23927
- **Authors:** Laura Bocchi, Raymond Hu, Adriana Laura Voinea, Simon Thompson
- **Categories:** cs.DC, cs.FL, cs.MA, cs.PL, cs.SE
- **Original:** cs.DC
- **Published:** Mon, 02 Mar 2026 00:00:00 -0500
- **Collected:** 2026-03-03 12:52:06
- **Domain:** csDC

## Abstract

We present a multiparty session type (MST) framework with asynchronous mixed choice (MC). We propose a core construct for MC that allows transient inconsistencies in protocol state between distributed participants, but ensures all participants can always eventually reach a mutually consistent state. We prove the correctness of our system by establishing a progress property and an operational correspondence between global types and distributed local type projections. Based on our theory, we implement a practical toolchain for specifying and validating asynchronous MST protocols featuring MC, and programming compliant gen_statem processes in Erlang/OTP. We test our framework by using our toolchain to specify and reimplement part of the amqp_client of the RabbitMQ broker for Erlang.

## Notes

<!-- Add your notes here -->

## Tags

#csDC #Arxiv #Research

---
*Auto-collected by arxiv-collector v2*

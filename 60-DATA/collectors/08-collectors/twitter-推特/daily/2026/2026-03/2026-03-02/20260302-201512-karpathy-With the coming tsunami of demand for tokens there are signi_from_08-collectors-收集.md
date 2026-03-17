---
title: "With the coming tsunami of demand for tokens, there are significant opportunities to orchestrate the underlying memory+compute *just right* for LLMs.

The fundamental and non-obvious constraint is that due to the chip fabrication process, you get two completely distinct pools of memory (of different physical implementations too): 1) on-chip SRAM that is immediately next to the compute units that is incredibly fast but of very of low capacity, and 2) off-chip DRAM which has extremely high capacity, but the contents of which you can only suck through a long straw. On top of this, there are many details of the architecture (e.g. systolic arrays), numerics, etc.

The design of the optimal physical substrate and then the orchestration of memory+compute across the top volume workflows of LLMs (inference prefill/decode, training/finetuning, etc.) with the best throughput/latency/$ is probably today's most interesting intellectual puzzle with the highest rewards (\cite 4.6T of NVDA). All of it to get many tokens, fast and cheap. Arguably, the workflow that may matter the most (inference decode *and* over long token contexts in tight agentic loops) is the one hardest to achieve simultaneously by the ~both camps of what exists today (HBM-first NVIDIA adjacent and SRAM-first Cerebras adjacent). Anyway the MatX team is A++ grade so it's my pleasure to have a small involvement and congratulations on the raise!"
source: X (Twitter)
account: @karpathy
url: https://nitter.net/karpathy/status/2026452488434651264#m
fetched: 2026-03-02T20:15:12.803118
tags: [twitter, x, karpathy]
---

# With the coming tsunami of demand for tokens, there are significant opportunities to orchestrate the underlying memory+compute *just right* for LLMs.

The fundamental and non-obvious constraint is that due to the chip fabrication process, you get two completely distinct pools of memory (of different physical implementations too): 1) on-chip SRAM that is immediately next to the compute units that is incredibly fast but of very of low capacity, and 2) off-chip DRAM which has extremely high capacity, but the contents of which you can only suck through a long straw. On top of this, there are many details of the architecture (e.g. systolic arrays), numerics, etc.

The design of the optimal physical substrate and then the orchestration of memory+compute across the top volume workflows of LLMs (inference prefill/decode, training/finetuning, etc.) with the best throughput/latency/$ is probably today's most interesting intellectual puzzle with the highest rewards (\cite 4.6T of NVDA). All of it to get many tokens, fast and cheap. Arguably, the workflow that may matter the most (inference decode *and* over long token contexts in tight agentic loops) is the one hardest to achieve simultaneously by the ~both camps of what exists today (HBM-first NVIDIA adjacent and SRAM-first Cerebras adjacent). Anyway the MatX team is A++ grade so it's my pleasure to have a small involvement and congratulations on the raise!

**Account:** @karpathy  
**Posted:** Wed, 25 Feb 2026 00:21:37 GMT  
**Link:** [https://nitter.net/karpathy/status/2026452488434651264#m](https://nitter.net/karpathy/status/2026452488434651264#m)

---

## Tweet Content

<p>With the coming tsunami of demand for tokens, there are significant opportunities to orchestrate the underlying memory+compute *just right* for LLMs.<br />
<br />
The fundamental and non-obvious constraint is that due to the chip fabrication process, you get two completely distinct pools of memory (of different physical implementations too): 1) on-chip SRAM that is immediately next to the compute units that is incredibly fast but of very of low capacity, and 2) off-chip DRAM which has extremely high capacity, but the contents of which you can only suck through a long straw. On top of this, there are many details of the architecture (e.g. systolic arrays), numerics, etc.<br />
<br />
The design of the optimal physical substrate and then the orchestration of memory+compute across the top volume workflows of LLMs (inference prefill/decode, training/finetuning, etc.) with the best throughput/latency/$ is probably today's most interesting intellectual puzzle with the highest rewards (\cite 4.6T of NVDA). All of it to get many tokens, fast and cheap. Arguably, the workflow that may matter the most (inference decode *and* over long token contexts in tight agentic loops) is the one hardest to achieve simultaneously by the ~both camps of what exists today (HBM-first NVIDIA adjacent and SRAM-first Cerebras adjacent). Anyway the MatX team is A++ grade so it's my pleasure to have a small involvement and congratulations on the raise!</p>
<hr />
<blockquote>
<b>Reiner Pope (@reinerpope)</b>
<p>
<p>We’re building an LLM chip that delivers much higher throughput than any other chip while also achieving the lowest latency. We call it the MatX One.<br />
<br />
The MatX One chip is based on a splittable systolic array, which has the energy and area efficiency that large systolic arrays are famous for, while also getting high utilization on smaller matrices with flexible shapes. The chip combines the low latency of SRAM-first designs with the long-context support of HBM. These elements, plus a fresh take on numerics, deliver higher throughput on LLMs than any announced system, while simultaneously matching the latency of SRAM-first designs. Higher throughput and lower latency give you smarter and faster models for your subscription dollar.<br />
<br />
We’ve raised a $500M Series B to wrap up development and quickly scale manufacturing, with tapeout in under a year. The round was led by Jane Street, one of the most tech-savvy Wall Street firms, and Situational Awareness LP, whose founder <a href="https://nitter.net/leopoldasch" title="Leopold Aschenbrenner">@leopoldasch</a> wrote the definitive memo on AGI. Participants include <a href="https://nitter.net/sparkcapital" title="Spark Capital">@sparkcapital</a>, <a href="https://nitter.net/danielgross" title="Daniel Gross">@danielgross</a> and <a href="https://nitter.net/natfriedman" title="Nat Friedman">@natfriedman</a>’s fund, <a href="https://nitter.net/patrickc" title="Patrick Collison">@patrickc</a> and <a href="https://nitter.net/collision" title="John Collison">@collision</a>, <a href="https://nitter.net/TriatomicCap" title="Triatomic Capital">@TriatomicCap</a>, <a href="https://nitter.net/HarpoonVentures" title="Harpoon Ventures">@HarpoonVentures</a>, <a href="https://nitter.net/karpathy" title="Andrej Karpathy">@karpathy</a>, <a href="https://nitter.net/dwarkesh_sp" title="Dwarkesh Patel">@dwarkesh_sp</a>, and others. We’re also welcoming investors across the supply chain, including Marvell and Alchip.<br />
<br />
<a href="https://nitter.net/MikeGunter_" title="Mike Gunter">@MikeGunter_</a> and I started MatX because we felt that the best chip for LLMs should be designed from first principles with a deep understanding of what LLMs need and how they will evolve. We are willing to give up on small-model performance, low-volume workloads, and even ease of programming to deliver on such a chip.<br />
<br />
We’re now a 100-person team with people who think about everything from learning rate schedules, to Swing Modulo Scheduling, to guard/round/sticky bits, to blind-mated connections—all in the same building. If you’d like to help us architect, design, and deploy many generations of chips in large volume, consider joining us.</p>

</p>
<footer>
— <cite><a href="https://nitter.net/reinerpope/status/2026351870852358492#m">https://nitter.net/reinerpope/status/2026351870852358492#m</a>
</footer>
</blockquote>

---
*Auto-collected by X Collector on 2026-03-02 20:15:12*

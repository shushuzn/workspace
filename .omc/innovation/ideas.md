# Idea Pool

- [2026-04-07] STAGE [manual] [score:4×3=12] [f:3] wikipedia T2I混合路由迁移 | benefit: SD替代9个matplotlib场景，质量提升+推理可控 | reason: Stable Diffusion 2.1 FP16在RTX3060可跑，diffusers库成熟 | approach: T2I路由层(9艺术场景SD2.1+自动回退matplotlib) | shipped:2026-04-07
- [2026-04-07] STAGE [brainstorm] [score:3×4=12] [f:4] wikipedia arXiv自动化流水线 | benefit: 人工步骤从6步→1步 | reason: wiki.mjs ingest已稳定运行 | approach: pipeline.py批量自动化+质量门禁+断点续传 | shipped:2026-04-07
- [2026-04-08] STAGE [AUTO:auto-seed-generator] [score:3×4=12] [f:4] 自动化工具调用模式识别 | benefit: 从5次调用中提取工作流模式并固化 | reason: 工具调用已达5次，存在可复用的工作流 | approach: 分析调用链→识别高频模式→生成可复用skill或adapter | shipped:2026-04-08
- [2026-04-08] STAGE [AUTO:auto-seed-generator] [score:3×4=12] [f:4] 自动化工具调用模式识别 | benefit: 从5次调用中提取工作流模式并固化 | reason: 工具调用已达5次，存在可复用的工作流 | approach: 分析调用链→识别高频模式→生成可复用skill或adapter | killed:2026-04-08 DUPLICATE of shipped:2026-04-08

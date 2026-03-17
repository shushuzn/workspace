# Show HN: Omni – Open-source workplace search and chat, built on Postgres

## 元数据
- **来源:** Hacker News
- **链接:** https://github.com/getomnico/omni
- **作者:** prvnsmpth
- **发布时间:** Mon, 02 Mar 2026 08:58:14 +0000
- **抓取时间:** 2026-03-02 21:17:44
- **AI 相关:** 否

## 内容

<p>Hey HN!<p>Over the past few months, I've been working on building Omni - a workplace search and chat platform that connects to apps like Google Drive/Gmail, Slack, Confluence, etc. Essentially an open-source alternative to Glean, fully self-hosted.<p>I noticed that some orgs find Glean to be expensive and not very extensible. I wanted to build something that small to mid-size teams could run themselves, so I decided to build it all on Postgres (ParadeDB to be precise) and pgvector. No Elasticsearch, or dedicated vector databases. I figured Postgres is more than capable of handling the level of scale required.<p>To bring up Omni on your own infra, all it takes is a single `docker compose up`, and some basic configuration to connect your apps and LLMs.<p>What it does:<p>- Syncs data from all connected apps and builds a BM25 index (ParadeDB) and HNSW vector index (pgvector)
- Hybrid search combines results from both
- Chat UI where the LLM has tools to search the index - not just basic RAG
- Traditional search UI
- Users bring their own LLM provider (OpenAI/Anthropic/Gemini)
- Connectors for Google Workspace, Slack, Confluence, Jira, HubSpot, and more
- Connector SDK to build your own custom connectors<p>Omni is in beta right now, and I'd love your feedback, especially on the following:<p>- Has anyone tried self-hosting workplace search and/or AI tools, and what was your experience like?
- Any concerns with the Postgres-only approach at larger scales?<p>Happy to answer any questions!<p>The code: <a href="https://github.com/getomnico/omni" rel="nofollow">https://github.com/getomnico/omni</a> (Apache 2.0 licensed)</p>
<hr />
<p>Comments URL: <a href="https://news.ycombinator.com/item?id=47215427">https://news.ycombinator.com/item?id=47215427</a></p>
<p>Points: 70</p>
<p># Comments: 23</p>

## 标签

#HackerNews #Tech

---
*自动收集*

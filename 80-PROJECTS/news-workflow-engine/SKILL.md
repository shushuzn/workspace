# news-workflow-engine API

## Type
REST API + Python CLI

## Description
News sentiment analysis engine with OpenAI-compatible endpoints. Crawls news, analyzes sentiment/category/importance, matches workflow templates, and outputs trading signals for rl-trading.

## Capabilities
- News sentiment analysis (AI-powered via Ollama/OpenAI)
- Workflow template matching
- Price alert webhook (material-price-tracker Chrome extension → news trigger)
- **Trading signals**: convert news sentiment into buy/sell/hold signals for rl-trading

## Endpoint Reference

### `POST /trading-signals`
Convert news into trading signals for rl-trading integration.
```
POST /trading-signals
{
  "title": "国际油价上涨突破80美元",
  "content": "WTI原油价格...",
  "source": "oil_news"
}
```
Response:
```json
{
  "topic": "finance",
  "sentiment": "positive",
  "signal": "buy",
  "confidence": 0.72,
  "sources": ["oil_news"],
  "importance": 0.8,
  "summary": "...",
  "keywords": ["原油", "WTI", "价格上涨"]
}
```

### `POST /v1/analyze/news`
Native news analysis endpoint.
```json
{
  "title": "...",
  "content": "...",
  "source": "..."
}
```

### `POST /v1/chat/completions`
OpenAI Chat Completions compatible.
```json
{
  "model": "news-analyzer",
  "messages": [{"role": "user", "content": "标题:...\n内容:..."}]
}
```

### `POST /v1/workflow/match`
Match analysis to workflow templates.

### `POST /webhook`
material-price-tracker price alert webhook.

### `GET /health`
Health check.

## Start
```bash
cd 80-PROJECTS/news-workflow-engine
python -m news_workflow.api.openai_compat --port 8080
```

## Environment
- `OLLAMA_HOST` — Ollama endpoint (default: http://localhost:11434)
- `OLLAMA_MODEL` — model (default: llama3)
- `OPENAI_API_KEY` — OpenAI key (optional, overrides Ollama)

## Signal Logic
| Sentiment | Normal Market | Policy/Regulatory |
|-----------|--------------|-------------------|
| positive | buy | sell |
| negative | sell | buy |
| neutral | hold | hold |

Confidence = importance × 0.9

## Tech Stack
Python · FastAPI · uvicorn · loguru

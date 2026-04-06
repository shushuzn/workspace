"""
OpenAI Chat Completions Compatible API

Wraps news-workflow-engine's NewsAnalyzer as an OpenAI-compatible
/v1/chat/completions endpoint so opencli and other agents can call it
with the standard OpenAI SDK.

Run: python -m news_workflow.api.openai_compat [--port 8080]
"""

import asyncio
import argparse
import sys
from pathlib import Path
from typing import Any

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import uvicorn

from news_workflow.analyzer.analyzer import NewsAnalyzer
from news_workflow.workflow.manager import WorkflowManager

app = FastAPI(title="News Workflow Engine — OpenAI Compatible API")

# Global analyzer instance (lazy init)
_analyzer: NewsAnalyzer | None = None
_workflow_manager: WorkflowManager | None = None


def get_analyzer() -> NewsAnalyzer:
    global _analyzer
    if _analyzer is None:
        _analyzer = NewsAnalyzer({"model": "ollama/llama3"})
    return _analyzer


def get_workflow_manager() -> WorkflowManager:
    global _workflow_manager
    if _workflow_manager is None:
        _workflow_manager = WorkflowManager({})
        # Load templates synchronously for simplicity
        asyncio.get_event_loop().run_until_complete(_workflow_manager.load_templates())
    return _workflow_manager


# ─── OpenAI Request/Response Models ───────────────────────────────────────────

class Message(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "news-analyzer"
    messages: list[Message]
    stream: bool = False
    temperature: float = 0.7
    max_tokens: int | None = None


class Usage(BaseModel):
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0


class ChatMessage(BaseModel):
    role: str
    content: str


class Choice(BaseModel):
    index: int
    message: ChatMessage
    finish_reason: str = "stop"


class ChatCompletionResponse(BaseModel):
    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: list[Choice]
    usage: Usage


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
async def health():
    return {"status": "ok", "service": "news-workflow-engine-openai"}


@app.post("/v1/chat/completions")
async def chat_completions(req: ChatCompletionRequest):
    """
    OpenAI Chat Completions compatible endpoint.

    Accepts messages with news content and returns AI analysis.

    Example:
        POST /v1/chat/completions
        {
          "model": "news-analyzer",
          "messages": [
            {"role": "user", "content": "AI大模型新突破\n标题:某公司发布新一代AI\n内容:性能提升10倍..."}
          ]
        }
    """
    try:
        # Extract news content from messages
        user_message = next(
            (m.content for m in reversed(req.messages) if m.role == "user"),
            ""
        )

        # Parse news item from message content
        # Support two formats:
        # 1. Plain text: "标题: xxx\n内容: xxx"
        # 2. Structured: already parsed fields
        news_item = _parse_news_item(user_message)

        # Run analysis
        analyzer = get_analyzer()
        result = await analyzer.analyze(news_item)

        # Format as OpenAI-style response
        response_text = _format_analysis_as_text(result)

        import time
        return ChatCompletionResponse(
            id=f"chatcmpl-{int(time.time()*1000)}",
            created=int(time.time()),
            model=req.model,
            choices=[Choice(
                index=0,
                message=ChatMessage(role="assistant", content=response_text),
                finish_reason="stop"
            )],
            usage=Usage(prompt_tokens=len(user_message) // 4, completion_tokens=len(response_text) // 4, total_tokens=(len(user_message) + len(response_text)) // 4)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/v1/analyze/news")
async def analyze_news(news_item: dict):
    """
    Direct news analysis endpoint (native format).

    POST /v1/analyze/news
    {
      "title": "AI大模型新突破",
      "content": "某公司发布...",
      "source": "tech_news",
      "url": "https://..."
    }
    """
    analyzer = get_analyzer()
    result = await analyzer.analyze(news_item)
    return result


@app.post("/v1/workflow/match")
async def match_workflow(analysis: dict):
    """
    Match analysis result to workflow templates.
    """
    manager = get_workflow_manager()
    matched = await manager.match_templates(analysis)
    return {"count": len(matched), "workflows": matched}


@app.post("/trading-signals")
async def trading_signals(news_item: dict):
    """
    Convert news analysis into trading signals for rl-trading.

    POST /trading-signals
    {
      "title": "国际油价上涨",
      "content": "WTI原油价格突破80美元/桶...",
      "source": "oil_news"
    }

    Returns:
    {
      "topic": "oil",
      "sentiment": "positive",
      "signal": "buy",
      "confidence": 0.75,
      "sources": ["oil_news"],
      "importance": 0.8
    }
    """
    analyzer = get_analyzer()
    result = await analyzer.analyze(news_item)

    sentiment = result.get("sentiment", "neutral")
    importance = result.get("importance", 0.5)
    category = result.get("category", "other")

    # Sentiment → signal mapping
    # Markets: positive=buy, negative=sell, neutral=hold
    # Policy/regulatory news: inverse signal
    signal_map = {
        "positive": "buy",
        "negative": "sell",
        "neutral": "hold",
    }

    # Adjust signal based on category
    if category == "policy":
        # Policy news inverts the signal (tight regulation = negative for markets)
        signal_map = {
            "positive": "sell",
            "negative": "buy",
            "neutral": "hold",
        }

    signal = signal_map.get(sentiment, "hold")

    # Confidence = importance weighted by sentiment clarity
    confidence = round(importance * 0.9, 2)

    return {
        "topic": category,
        "sentiment": sentiment,
        "signal": signal,
        "confidence": confidence,
        "sources": [news_item.get("source", "unknown")],
        "importance": importance,
        "summary": result.get("summary", ""),
        "keywords": result.get("keywords", []),
    }


class PriceAlertPayload(BaseModel):
    source: str = "material-price-tracker"
    timestamp: str
    alerts: list[dict]


@app.post("/webhook")
async def price_alert_webhook(payload: PriceAlertPayload):
    """
    Receive price threshold alerts from material-price-tracker Chrome extension.

    POST /webhook
    {
      "source": "material-price-tracker",
      "timestamp": "2026-04-06T12:00:00.000Z",
      "alerts": [
        {"type": "PE", "currentPrice": 8500, "threshold": 8600, "triggered": true},
        {"type": "PP", "currentPrice": 7800, "threshold": 7900, "triggered": true}
      ]
    }
    """
    from loguru import logger
    logger.info(f"📦 Price alert webhook received: {payload.source}")
    for alert in payload.alerts:
        logger.info(f"  🚨 {alert['type']} 现货价 {alert['currentPrice']} <= 阈值 {alert['threshold']}")
    # Optionally trigger news workflow based on price drop
    if payload.alerts:
        try:
            analyzer = get_analyzer()
            alert = payload.alerts[0]
            news_item = {
                "title": f"【价格预警】{alert['type']}现货价格突破阈值",
                "content": f"{alert['type']}当前现货价格{alert['currentPrice']}元/吨，已触发告警阈值{alert['threshold']}元/吨，请关注市场变化。",
                "source": "material-price-tracker-webhook",
                "url": "",
            }
            result = await analyzer.analyze(news_item)
            logger.info(f"  📊 Analysis: importance={result.get('importance', 0):.2f}, sentiment={result.get('sentiment', 'unknown')}")
            return {"received": True, "alerts_count": len(payload.alerts), "analysis": result}
        except Exception as e:
            logger.error(f"  ⚠️ Analysis failed: {e}")
            return {"received": True, "alerts_count": len(payload.alerts), "analysis_error": str(e)}
    return {"received": True, "alerts_count": 0}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def _parse_news_item(content: str) -> dict:
    """Parse user message into a news_item dict."""
    lines = content.strip().split("\n")
    item = {"source": "api", "url": ""}

    for line in lines:
        line = line.strip()
        if line.startswith("标题:") or line.startswith("title:"):
            item["title"] = line.split(":", 1)[1].strip()
        elif line.startswith("内容:") or line.startswith("content:"):
            item["content"] = line.split(":", 1)[1].strip()
        elif line.startswith("来源:") or line.startswith("source:"):
            item["source"] = line.split(":", 1)[1].strip()
        elif line.startswith("链接:") or line.startswith("url:"):
            item["url"] = line.split(":", 1)[1].strip()

    # If no structured format, use entire content as title
    if "title" not in item and "content" not in item:
        item["title"] = content[:200]
        item["content"] = content

    return item


def _format_analysis_as_text(result: dict) -> str:
    """Format analysis result as readable text."""
    lines = []
    if result.get("importance"):
        lines.append(f"📊 重要性: {result['importance']}/5")
    if result.get("category"):
        lines.append(f"🏷️ 分类: {result['category']}")
    if result.get("sentiment"):
        lines.append(f"💬 情感: {result['sentiment']}")
    if result.get("summary"):
        lines.append(f"\n📝 摘要: {result['summary']}")
    if result.get("keywords"):
        kw = result["keywords"]
        if isinstance(kw, list):
            kw = ", ".join(kw[:10])
        lines.append(f"🔑 关键词: {kw}")
    return "\n".join(lines) if lines else str(result)


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="News Workflow Engine — OpenAI Compatible API")
    parser.add_argument("--port", type=int, default=8080, help="Port to listen on")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    args = parser.parse_args()

    print(f"🚀 News Workflow Engine OpenAI API starting on http://{args.host}:{args.port}")
    print(f"   POST /v1/chat/completions  — OpenAI Chat Completions compatible")
    print(f"   POST /v1/analyze/news      — Native news analysis")
    print(f"   POST /v1/workflow/match    — Workflow matching")
    print(f"   POST /trading-signals      — News → trading signal (buy/sell/hold) for rl-trading")
    print(f"   POST /webhook              — material-price-tracker price alert webhook")
    print(f"   GET  /health              — Health check")

    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()

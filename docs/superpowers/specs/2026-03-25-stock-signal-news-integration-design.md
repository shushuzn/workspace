# Stock Signal + News Integration Design

**Date:** 2026-03-25
**Status:** Draft
**Project:** newshub-observability + stock-analysis-mcp-test integration

---

## 1. Overview

**Goal:** Bidirectional enhancement between news and stock signals

- News events trigger stock technical indicator recalculation (event-driven)
- Stock trend signals annotate news cards (signal labeling)

**Architecture:** API call (MCP JSON-RPC over HTTP)

---

## 2. Data Flow

```
News Entry
    ↓
Classification + Deduplication
    ↓
[Signal Annotation Step] ← new integration point
    ↓
MCP: get_summary(symbol) for each related stock
    ↓
Render trend tag on card: "AAPL: ↑强势" / "腾讯: ↓弱势"
    ↓
Card Output to channels (Feishu/Telegram/etc.)
```

---

## 3. Symbol Resolution (Priority Order)

| Priority | Source | Description |
|----------|--------|-------------|
| 1 | News metadata | `stock_codes` field from source |
| 2 | SignalLinker | Existing symbol association logic |
| 3 | Keyword map | Manual mapping for common stocks |

Fallback: If no symbol resolved → card rendered without stock annotation.

---

## 4. Integration Points

### 4.1 card_builder.py
**Change:** Add `annotate_with_stock_signals()` method

```python
async def annotate_with_stock_signals(card, news_item):
    """Add stock trend tags to news card."""
    symbols = resolve_symbols(news_item)  # Priority 1→2→3

    for symbol in symbols[:3]:  # Max 3 symbols per card
        try:
            summary = await mcp_client.call("get_summary", {"symbol": symbol, "period": "1d"})
            trend = summarize_trend(summary)  # "↑强势" / "↓弱势" / "→盘整"
            card.add_tag(f"{symbol}: {trend}")
        except Exception:
            card.add_tag(f"{symbol}: 信号待更新")
```

### 4.2 mcp_client.py (NEW)
**Purpose:** HTTP client for MCP JSON-RPC calls

```python
class MCPClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url

    async def call(self, tool: str, arguments: dict) -> dict:
        # JSON-RPC 2.0 request over HTTP
        # Timeout: 3s
        # On failure: raise MCPError (caller handles degradation)
```

### 4.3 Keyword Fallback Map
**File:** `config/stock_keyword_map.json`

```json
{
  "腾讯": "00700.HK",
  "阿里": "09988.HK",
  "茅台": "600519.SS",
  "苹果": "AAPL",
  "英伟达": "NVDA"
}
```

---

## 5. Error Handling & Degradation

| Failure Scenario | Handling |
|-----------------|----------|
| MCP service unavailable | Card shows "信号待更新" |
| Symbol resolution failed | Skip annotation, card renders normally |
| MCP call timeout (3s) | Skip annotation, no error shown |
| Invalid symbol | Log warning, skip |

**Principle:** Never block card rendering due to stock signals.

---

## 6. Performance

- **Max symbols per card:** 3 (prevents card overflow)
- **MCP timeout:** 3 seconds
- **Parallel calls:** Fire all symbol calls concurrently, render when all resolve or timeout
- **No caching in v1** (accept slight staleness for simplicity)

---

## 7. Configuration

**File:** `config/mcp_integration.json`

```json
{
  "mcp_server_url": "http://localhost:8000",
  "timeout_seconds": 3,
  "max_symbols_per_card": 3,
  "enabled": true
}
```

---

## 8. Testing

1. Unit test: `resolve_symbols()` with mock news item
2. Integration test: MCP client calls against live stock-analysis-mcp
3. E2E test: Render card with known stock-related news, verify tag appears

---

## 9. Out of Scope (v1)

- News sentiment scoring into stock analysis
- Event-driven technical indicator recalculation
- Real-time streaming / WebSocket
- Caching layer

---

## 10. File Changes

| File | Action |
|------|--------|
| `card_builder.py` | Modify - add annotation method |
| `mcp_client.py` | New - MCP HTTP client |
| `config/mcp_integration.json` | New - integration config |
| `config/stock_keyword_map.json` | New - symbol keyword mapping |

---

## 11. Dependencies

- `aiohttp` (already in newshub-observability)
- `stock-analysis-mcp-test` running on localhost:8000

---

## 12. Open Questions

1. **MCP transport:** Is stdin/stdout or HTTP? (HTTP assumed for network calls)
2. **Service discovery:** How does newshub find stock-analysis-mcp? localhost:8000 hardcoded for now
3. **Authentication:** Any auth needed for MCP calls? (Assumed no for v1)

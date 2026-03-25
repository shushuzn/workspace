# Stock Signal + News Integration Design

**Date:** 2026-03-25
**Status:** Draft → Revised after review
**Project:** newshub-observability + stock-analysis-mcp-test integration

---

## 1. Overview

**Goal:** Unidirectional stock signal annotation of news cards (Phase 1)

- Stock trend signals annotate news cards (signal labeling)
- News → MCP → Card annotation (one direction only)

**Future Phase 2 (out of scope):**
- News events trigger stock technical indicator recalculation

**Architecture:** MCP JSON-RPC over stdio (subprocess)

---

## 2. Data Flow

```
News Entry
    ↓
Classification + Deduplication
    ↓
[Signal Annotation Step] ← new integration point
    ↓
MCP: get_summary(symbol) via subprocess stdio
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

    # Fire all MCP calls concurrently
    tasks = [
        mcp_client.call("get_summary", {"symbol": sym, "period": "1d"})
        for sym in symbols[:3]  # Max 3 symbols per card
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for sym, result in zip(symbols[:3], results):
        if isinstance(result, Exception):
            card.add_tag(f"{sym}: 信号待更新")
        else:
            trend = summarize_trend(result)  # Defined in Section 4.3
            card.add_tag(f"{sym}: {trend}")
```

### 4.2 mcp_client.py (NEW)
**Purpose:** Subprocess-based MCP client using stdio transport

```python
import asyncio
import json
import subprocess
import sys
from pathlib import Path

class MCPClient:
    """MCP client using subprocess + stdio transport."""

    def __init__(self, mcp_server_path: str = None, timeout: float = 3.0):
        self.mcp_server_path = mcp_server_path or self._find_mcp_server()
        self.timeout = timeout

    def _find_mcp_server(self) -> str:
        # Search for stock-analysis-mcp-test/src/server.py
        candidates = [
            Path(__file__).parent.parent / "stock-analysis-mcp-test" / "src" / "server.py",
            Path.home() / "stock-analysis-mcp-test" / "src" / "server.py",
        ]
        for p in candidates:
            if p.exists():
                return f"python {p}"
        raise FileNotFoundError("stock-analysis-mcp-test server.py not found")

    async def call(self, tool: str, arguments: dict) -> dict:
        """Call MCP tool via subprocess stdin/stdout."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": arguments
            }
        }

        proc = await asyncio.create_subprocess_exec(
            *self.mcp_server_path.split(),
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=json.dumps(request).encode()),
                timeout=self.timeout
            )
        except asyncio.TimeoutError:
            proc.kill()
            raise MCPError(f"Timeout calling {tool}") from None

        if proc.returncode != 0:
            raise MCPError(f"MCP server error: {stderr.decode()}")

        response = json.loads(stdout.decode())
        if "error" in response:
            raise MCPError(f"MCP tool error: {response['error']}")

        # Parse MCP response content wrapper
        content = response.get("result", {}).get("content", [])
        if not content:
            raise MCPError("Empty response from MCP")

        return json.loads(content[0]["text"])


class MCPError(Exception):
    """MCP client error for degradation handling."""
    pass
```

### 4.3 summarize_trend() Definition

**Purpose:** Map `get_summary` output to Chinese trend labels.

```python
TREND_MAP = {
    "uptrend": "↑强势",
    "downtrend": "↓弱势",
    "sideways": "→盘整",
}

def summarize_trend(summary: dict) -> str:
    """
    Convert get_summary response to trend label.

    Input: get_summary returns dict with:
        - symbol: str
        - trend.direction: "uptrend" | "downtrend" | "sideways"
        - trend.signal: "buy" | "sell" | "hold"
        - rsi: float (optional)

    Output: Chinese trend label, e.g. "↑强势"
    """
    direction = summary.get("trend", {}).get("direction", "sideways")
    return TREND_MAP.get(direction, "→盘整")
```

### 4.4 Keyword Fallback Map
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
| Application-level error in response | Check `summary.get("error")`, show "信号待更新" |

**Principle:** Never block card rendering due to stock signals.

---

## 6. Performance

- **Max symbols per card:** 3 (prevents card overflow)
- **MCP timeout:** 3 seconds per call
- **Parallel calls:** `asyncio.gather()` fires all calls concurrently
- **No caching in v1** (accept slight staleness for simplicity)

---

## 7. Configuration

**File:** `config/mcp_integration.json`

```json
{
  "mcp_server_command": "python /path/to/stock-analysis-mcp-test/src/server.py",
  "timeout_seconds": 3,
  "max_symbols_per_card": 3,
  "enabled": true
}
```

---

## 8. Testing

1. Unit test: `resolve_symbols()` with mock news item
2. Unit test: `summarize_trend()` with mock summary dicts
3. Integration test: MCP client calls against live stock-analysis-mcp
4. E2E test: Render card with known stock-related news, verify tag appears

---

## 9. Out of Scope (v1)

- News sentiment scoring into stock analysis
- Event-driven technical indicator recalculation
- Real-time streaming / WebSocket
- Caching layer
- Bidirectional enhancement (Phase 2)

---

## 10. File Changes

| File | Action |
|------|--------|
| `card_builder.py` | Modify - add annotation method |
| `mcp_client.py` | New - MCP subprocess/stdio client |
| `config/mcp_integration.json` | New - integration config |
| `config/stock_keyword_map.json` | New - symbol keyword mapping |

---

## 11. Dependencies

- `asyncio` (stdlib)
- `subprocess` (stdlib)
- `json` (stdlib)
- `pathlib` (stdlib)
- No new external dependencies required

---

## 12. Open Questions - RESOLVED

1. ~~**MCP transport:** Is stdin/stdout or HTTP?~~ → **Resolved: stdio/subprocess**
2. **Service discovery:** How does newshub find stock-analysis-mcp? → Config file path, no auto-discovery
3. **Authentication:** Not needed for v1 (localhost only)

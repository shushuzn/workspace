# Stock Signal + News Integration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add stock trend annotation to news cards by calling stock-analysis-mcp via MCP subprocess/stdio.

**Architecture:** Add `mcp_client.py` (subprocess MCP client) + modify `card_builder.py` to call it. New config files for integration settings and keyword mapping.

**Tech Stack:** Python stdlib only (asyncio, subprocess, json, pathlib) — no new external deps.

---

## File Structure

```
newshub-observability/
├── mcp_client.py                              # NEW: MCP subprocess client
├── card_builder.py                             # MODIFY: add annotation method
├── config/
│   ├── mcp_integration.json                   # NEW: MCP server config
│   └── stock_keyword_map.json                 # NEW: keyword → symbol mapping
└── tests/
    ├── test_mcp_client.py                    # NEW: unit tests for MCP client
    └── test_card_builder_annotation.py        # NEW: unit tests for annotation
```

---

## Task 1: Create MCP Subprocess Client

**Files:**
- Create: `newshub-observability/mcp_client.py`
- Test: `newshub-observability/tests/test_mcp_client.py`

- [ ] **Step 1: Write failing test for MCPClient initialization and call**

Create `newshub-observability/tests/test_mcp_client.py`:

```python
import pytest
import asyncio
from mcp_client import MCPClient, MCPError


def test_mcp_client_initialization():
    """Test MCPClient can be initialized with default path."""
    client = MCPClient()
    # Should not raise


def test_mcp_client_with_explicit_path():
    """Test MCPClient accepts explicit server path."""
    client = MCPClient(mcp_server_command="python /fake/path.py")
    assert client.mcp_server_command == "python /fake/path.py"


def test_mcp_error_is_exception():
    """Test MCPError is a proper Exception subclass."""
    with pytest.raises(MCPError):
        raise MCPError("test error")
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_mcp_client.py -v`
Expected: FAIL — module not found

- [ ] **Step 3: Write minimal MCPClient implementation**

Create `newshub-observability/mcp_client.py`:

```python
"""MCP client using subprocess + stdio transport."""
import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Optional


class MCPError(Exception):
    """MCP client error for degradation handling."""
    pass


class MCPClient:
    """MCP client using subprocess + stdio transport."""

    def __init__(
        self,
        mcp_server_command: Optional[str] = None,
        timeout: float = 3.0,
        mcp_server_search_paths: Optional[list] = None,
    ):
        self.timeout = timeout
        self.mcp_server_search_paths = mcp_server_search_paths or self._default_search_paths()
        if mcp_server_command:
            self.mcp_server_command = mcp_server_command
        else:
            self.mcp_server_command = self._find_mcp_server()

    def _default_search_paths(self) -> list:
        """Return default search paths for MCP server."""
        return [
            Path(__file__).parent.parent / "stock-analysis-mcp-test" / "src" / "server.py",
            Path.home() / "stock-analysis-mcp-test" / "src" / "server.py",
        ]

    def _find_mcp_server(self) -> str:
        """Find MCP server.py in search paths."""
        for p in self.mcp_server_search_paths:
            if p.exists():
                return f"python {p}"
        raise FileNotFoundError(
            f"MCP server not found in search paths: {[str(p) for p in self.mcp_server_search_paths]}"
        )

    async def call(self, tool: str, arguments: dict) -> dict:
        """Call MCP tool via subprocess stdin/stdout."""
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool,
                "arguments": arguments,
            },
        }

        cmd_parts = self.mcp_server_command.split()
        proc = await asyncio.create_subprocess_exec(
            *cmd_parts,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                proc.communicate(input=json.dumps(request).encode()),
                timeout=self.timeout,
            )
        except asyncio.TimeoutError:
            proc.kill()
            await proc.wait()
            raise MCPError(f"Timeout calling {tool}") from None

        if proc.returncode != 0:
            stderr_text = stderr.decode() if stderr else ""
            raise MCPError(f"MCP server error: {stderr_text}")

        try:
            response = json.loads(stdout.decode())
        except json.JSONDecodeError as e:
            raise MCPError(f"Invalid JSON from MCP server: {e}") from e

        if "error" in response:
            raise MCPError(f"MCP tool error: {response['error']}")

        # Parse MCP response content wrapper
        content = response.get("result", {}).get("content", [])
        if not content:
            raise MCPError("Empty response from MCP")

        try:
            return json.loads(content[0]["text"])
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            raise MCPError(f"Invalid response format from MCP: {e}") from e
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_mcp_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add mcp_client.py tests/test_mcp_client.py
git commit -m "feat: add MCP subprocess client for stock-analysis-mcp integration"
```

---

## Task 2: Add summarize_trend() and resolve_symbols()

**Files:**
- Modify: `newshub-observability/mcp_client.py` — add helper functions
- Test: `newshub-observability/tests/test_mcp_client.py` — add tests for helpers

- [ ] **Step 1: Write failing tests for summarize_trend() and resolve_symbols()**

Add to `tests/test_mcp_client.py`:

```python
def test_summarize_trend_uptrend():
    """Test uptrend maps to upward arrow + strong."""
    from mcp_client import summarize_trend
    summary = {"trend": {"direction": "uptrend"}}
    assert summarize_trend(summary) == "↑强势"


def test_summarize_trend_downtrend():
    """Test downtrend maps to downward arrow + weak."""
    from mcp_client import summarize_trend
    summary = {"trend": {"direction": "downtrend"}}
    assert summarize_trend(summary) == "↓弱势"


def test_summarize_trend_sideways():
    """Test sideways maps to horizontal arrow + consolidating."""
    from mcp_client import summarize_trend
    summary = {"trend": {"direction": "sideways"}}
    assert summarize_trend(summary) == "→盘整"


def test_summarize_trend_unknown():
    """Test unknown direction defaults to sideways."""
    from mcp_client import summarize_trend
    summary = {"trend": {"direction": "unknown"}}
    assert summarize_trend(summary) == "→盘整"


def test_summarize_trend_missing_trend():
    """Test missing trend key defaults to sideways."""
    from mcp_client import summarize_trend
    summary = {}
    assert summarize_trend(summary) == "→盘整"


def test_resolve_symbols_from_metadata():
    """Test resolve_symbols extracts from news metadata."""
    from mcp_client import resolve_symbols
    news_item = type("NewsItem", (), {"stock_codes": ["AAPL", "NVDA"]})()
    symbols = resolve_symbols(news_item)
    assert "AAPL" in symbols
    assert "NVDA" in symbols


def test_resolve_symbols_fallback_to_keywords():
    """Test resolve_symbols falls back to keyword map."""
    from mcp_client import resolve_symbols
    news_item = type("NewsItem", (), {"title": "腾讯发布新产品", "stock_codes": []})()
    symbols = resolve_symbols(news_item)
    assert "00700.HK" in symbols
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_mcp_client.py -v`
Expected: FAIL — function not defined

- [ ] **Step 3: Add helper functions to mcp_client.py**

Add at end of `mcp_client.py`:

```python
# Trend label mapping
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


def resolve_symbols(news_item) -> list:
    """
    Resolve stock symbols from a news item.

    Priority:
    1. news_item.stock_codes (metadata from source)
    2. news_item.symbols (SignalLinker output)
    3. Keyword matching on title/content

    Returns:
        List of symbol strings, e.g. ["AAPL", "00700.HK"]
    """
    symbols = []

    # Priority 1: stock_codes metadata
    if hasattr(news_item, "stock_codes") and news_item.stock_codes:
        symbols.extend(news_item.stock_codes)

    # Priority 2: SignalLinker symbols
    if hasattr(news_item, "symbols") and news_item.symbols:
        for sym in news_item.symbols:
            if sym not in symbols:
                symbols.append(sym)

    # Priority 3: Keyword matching (loaded from config)
    keyword_map = _load_keyword_map()
    text = ""
    if hasattr(news_item, "title"):
        text += news_item.title + " "
    if hasattr(news_item, "content"):
        text += news_item.content

    for keyword, symbol in keyword_map.items():
        if keyword in text and symbol not in symbols:
            symbols.append(symbol)

    return symbols


def _load_keyword_map() -> dict:
    """Load keyword → symbol mapping from config file."""
    config_paths = [
        Path(__file__).parent / "config" / "stock_keyword_map.json",
        Path(__file__).parent.parent / "config" / "stock_keyword_map.json",
    ]
    for p in config_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {}
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `pytest tests/test_mcp_client.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add mcp_client.py tests/test_mcp_client.py
git commit -m "feat: add summarize_trend and resolve_symbols helpers"
```

---

## Task 3: Create config files

**Files:**
- Create: `newshub-observability/config/mcp_integration.json`
- Create: `newshub-observability/config/stock_keyword_map.json`

- [ ] **Step 1: Create mcp_integration.json**

```json
{
  "enabled": true,
  "mcp_server_command": "python /path/to/stock-analysis-mcp-test/src/server.py",
  "timeout_seconds": 3,
  "max_symbols_per_card": 3
}
```

- [ ] **Step 2: Create stock_keyword_map.json**

```json
{
  "腾讯": "00700.HK",
  "阿里": "09988.HK",
  "茅台": "600519.SS",
  "苹果": "AAPL",
  "英伟达": "NVDA",
  "谷歌": "GOOGL",
  "特斯拉": "TSLA",
  "亚马逊": "AMZN"
}
```

- [ ] **Step 3: Commit**

```bash
git add config/mcp_integration.json config/stock_keyword_map.json
git commit -m "feat: add MCP integration config and stock keyword map"
```

---

## Task 4: Add annotation to card_builder

**Files:**
- Modify: `newshub-observability/card_builder.py`
- Test: `newshub-observability/tests/test_card_builder_annotation.py`

- [ ] **Step 1: Write failing test for annotate_with_stock_signals**

Create `tests/test_card_builder_annotation.py`:

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from card_builder import CardBuilder, Card


@pytest.fixture
def mock_news_item():
    """Create a mock news item with stock_codes."""
    item = Mock()
    item.stock_codes = ["AAPL"]
    item.title = "Apple releases new product"
    item.content = "Apple Inc announced"
    item.symbols = []
    return item


@pytest.fixture
def mock_mcp_client():
    """Create a mock MCP client."""
    client = Mock()
    client.call = AsyncMock(return_value={"trend": {"direction": "uptrend"}})
    return client


def test_card_has_tags_after_annotation():
    """Test card gets stock trend tag after annotation."""
    card = Card()
    card.tags = []

    # Mock resolve_symbols to return AAPL
    with patch("card_builder.resolve_symbols", return_value=["AAPL"]):
        with patch("card_builder.MCPClient", return_value=mock_mcp_client()):
            # This would need the actual function to be added
            pass  # Will be implemented


def test_annotation_degrades_gracefully_on_error():
    """Test annotation shows '信号待更新' on MCP error."""
    # Will be implemented with actual function
    pass


def test_max_3_symbols_per_card():
    """Test annotation limits to 3 symbols."""
    # Will be implemented with actual function
    pass
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `pytest tests/test_card_builder_annotation.py -v`
Expected: FAIL — function not defined

- [ ] **Step 3: Add annotate_with_stock_signals to card_builder.py**

First, read existing `card_builder.py` to find the right place to add the method:

```bash
head -100 card_builder.py
```

Then add method to `CardBuilder` class:

```python
async def annotate_with_stock_signals(self, card, news_item):
    """Add stock trend tags to news card.

    Calls stock-analysis-mcp via MCP subprocess to get real-time
    trend data for related stocks and annotates the card.
    """
    from mcp_client import MCPClient, resolve_symbols, summarize_trend

    # Load config
    config = self._load_mcp_config()
    if not config.get("enabled", False):
        return card

    symbols = resolve_symbols(news_item)
    symbols = symbols[: config.get("max_symbols_per_card", 3)]

    if not symbols:
        return card

    mcp_client = MCPClient(timeout=config.get("timeout_seconds", 3.0))

    # Fire all MCP calls concurrently
    tasks = [
        mcp_client.call("get_summary", {"symbol": sym, "period": "1d"})
        for sym in symbols
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    for sym, result in zip(symbols, results):
        if isinstance(result, Exception) or (
            isinstance(result, dict) and "error" in result
        ):
            card.add_tag(f"{sym}: 信号待更新")
        else:
            trend = summarize_trend(result)
            card.add_tag(f"{sym}: {trend}")

    return card


def _load_mcp_config(self) -> dict:
    """Load MCP integration config."""
    import json
    from pathlib import Path

    config_paths = [
        Path(__file__).parent / "config" / "mcp_integration.json",
        Path(__file__).parent.parent / "config" / "mcp_integration.json",
    ]
    for p in config_paths:
        if p.exists():
            with open(p, "r", encoding="utf-8") as f:
                return json.load(f)
    return {"enabled": False}
```

- [ ] **Step 4: Write comprehensive tests**

Update `tests/test_card_builder_annotation.py` with full tests:

```python
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from card_builder import CardBuilder


@pytest.fixture
def mock_news_item():
    item = Mock()
    item.stock_codes = ["AAPL"]
    item.title = "Apple news"
    item.content = ""
    item.symbols = []
    return item


@pytest.fixture
def mock_card():
    card = Mock()
    card.tags = []
    card.add_tag = Mock()
    return card


def test_annotate_adds_trend_tag(mock_card, mock_news_item):
    """Test annotation adds stock trend tag to card."""
    builder = CardBuilder()

    mock_client = Mock()
    mock_client.call = AsyncMock(
        return_value={"trend": {"direction": "uptrend"}}
    )

    with patch("card_builder.resolve_symbols", return_value=["AAPL"]):
        with patch("card_builder.MCPClient", return_value=mock_client):
            result_card = asyncio.run(
                builder.annotate_with_stock_signals(mock_card, mock_news_item)
            )

    mock_card.add_tag.assert_called_with("AAPL: ↑强势")


def test_annotate_degrades_on_mcp_error(mock_card, mock_news_item):
    """Test annotation shows '信号待更新' on MCP error."""
    builder = CardBuilder()

    mock_client = Mock()
    mock_client.call = AsyncMock(reraises=Exception("MCP failed"))

    with patch("card_builder.resolve_symbols", return_value=["AAPL"]):
        with patch("card_builder.MCPClient", return_value=mock_client):
            result_card = asyncio.run(
                builder.annotate_with_stock_signals(mock_card, mock_news_item)
            )

    mock_card.add_tag.assert_called_with("AAPL: 信号待更新")


def test_annotate_max_3_symbols(mock_card):
    """Test annotation limits to 3 symbols."""
    builder = CardBuilder()

    item = Mock()
    item.stock_codes = ["A", "B", "C", "D", "E"]  # 5 symbols
    item.symbols = []
    item.title = ""
    item.content = ""

    mock_client = Mock()
    mock_client.call = AsyncMock(
        return_value={"trend": {"direction": "uptrend"}}
    )

    with patch("card_builder.resolve_symbols", return_value=["A", "B", "C", "D", "E"]):
        with patch("card_builder.MCPClient", return_value=mock_client):
            result_card = asyncio.run(
                builder.annotate_with_stock_signals(mock_card, item)
            )

    # Only 3 calls should be made
    assert mock_client.call.call_count == 3


def test_annotate_skips_when_disabled(mock_card, mock_news_item):
    """Test annotation skipped when disabled in config."""
    builder = CardBuilder()

    with patch("card_builder.CardBuilder._load_mcp_config", return_value={"enabled": False}):
        result_card = asyncio.run(
            builder.annotate_with_stock_signals(mock_card, mock_news_item)
        )

    mock_card.add_tag.assert_not_called()


def test_annotate_skips_when_no_symbols(mock_card):
    """Test annotation skipped when no symbols resolved."""
    builder = CardBuilder()

    item = Mock()
    item.stock_codes = []
    item.symbols = []
    item.title = ""
    item.content = ""

    result_card = asyncio.run(
        builder.annotate_with_stock_signals(mock_card, item)
    )

    mock_card.add_tag.assert_not_called()
```

- [ ] **Step 5: Run tests to verify they pass**

Run: `pytest tests/test_card_builder_annotation.py -v`
Expected: PASS

- [ ] **Step 6: Commit**

```bash
git add card_builder.py tests/test_card_builder_annotation.py
git commit -m "feat: add stock signal annotation to news cards"
```

---

## Task 5: Integration Test

**Files:**
- Test: `newshub-observability/tests/test_integration_mcp.py`

- [ ] **Step 1: Write integration test**

```python
"""
Integration test: Verify MCP client can call stock-analysis-mcp server.

Requires stock-analysis-mcp-test to be installed:
    pip install -e /path/to/stock-analysis-mcp-test
"""
import pytest
import asyncio


@pytest.fixture
def mcp_server_command():
    """Path to stock-analysis-mcp server."""
    from pathlib import Path
    candidates = [
        Path(__file__).parent.parent.parent / "stock-analysis-mcp-test" / "src" / "server.py",
    ]
    for p in candidates:
        if p.exists():
            return f"python {p}"
    pytest.skip("stock-analysis-mcp-test not found")


@pytest.mark.integration
def test_mcp_client_calls_get_quote(mcp_server_command):
    """Test MCP client can call get_quote tool."""
    from mcp_client import MCPClient

    client = MCPClient(mcp_server_command=mcp_server_command, timeout=5.0)

    async def run():
        result = await client.call("get_quote", {"symbol": "AAPL"})
        return result

    result = asyncio.run(run())

    assert "symbol" in result or "price" in result or "error" not in result


@pytest.mark.integration
def test_mcp_client_handles_invalid_symbol(mcp_server_command):
    """Test MCP client handles invalid symbol gracefully."""
    from mcp_client import MCPClient, MCPError

    client = MCPClient(mcp_server_command=mcp_server_command, timeout=5.0)

    async def run():
        try:
            result = await client.call("get_quote", {"symbol": "INVALID_SYMBOL_XYZ"})
            return result
        except MCPError:
            return {"error": "MCPError raised as expected"}

    result = asyncio.run(run())
    assert "error" in result
```

- [ ] **Step 2: Run integration test (requires stock-analysis-mcp running)**

Run: `pytest tests/test_integration_mcp.py -v -m integration`
Expected: SKIP if server not found, or PASS if server is running

- [ ] **Step 3: Commit**

```bash
git add tests/test_integration_mcp.py
git commit -m "test: add MCP integration tests"
```

---

## Task 6: End-to-End Card Rendering Test

**Files:**
- Test: `newshub-observability/tests/test_e2e_card_with_stock_annotation.py`

- [ ] **Step 1: Write E2E test**

```python
"""
E2E test: Render a news card with stock annotation.

This test verifies the full flow from news item to annotated card.
"""
import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from card_builder import CardBuilder


@pytest.fixture
def stock_news_item():
    """Create a news item about Apple."""
    item = Mock()
    item.stock_codes = ["AAPL"]
    item.symbols = []
    item.title = "Apple announces new iPhone"
    item.content = "Apple Inc revealed"
    return item


@pytest.mark.e2e
def test_card_renders_with_stock_annotation(stock_news_item):
    """Test news card includes stock trend annotation."""
    builder = CardBuilder()

    mock_client = Mock()
    mock_client.call = AsyncMock(
        return_value={
            "symbol": "AAPL",
            "trend": {"direction": "uptrend"},
            "price": 175.50,
            "change_percent": 2.3,
        }
    )

    card = Mock()
    card.tags = []
    card.add_tag = Mock()

    with patch("card_builder.resolve_symbols", return_value=["AAPL"]):
        with patch("card_builder.MCPClient", return_value=mock_client):
            result = asyncio.run(
                builder.annotate_with_stock_signals(card, stock_news_item)
            )

    # Verify tag was added
    assert card.add_tag.called
    tags_added = [call[0][0] for call in card.add_tag.call_args_list]
    assert any("AAPL" in tag for tag in tags_added)
    assert any("↑强势" in tag for tag in tags_added)
```

- [ ] **Step 2: Run E2E test**

Run: `pytest tests/test_e2e_card_with_stock_annotation.py -v -m e2e`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add tests/test_e2e_card_with_stock_annotation.py
git commit -m "test: add E2E test for stock annotation in card rendering"
```

---

## Summary

| Task | Description |
|------|-------------|
| 1 | MCP subprocess client (`mcp_client.py`) |
| 2 | Helper functions (`summarize_trend`, `resolve_symbols`) |
| 3 | Config files (`mcp_integration.json`, `stock_keyword_map.json`) |
| 4 | Card annotation integration (`card_builder.py`) |
| 5 | Integration tests |
| 6 | E2E card rendering test |

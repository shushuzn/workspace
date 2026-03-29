"""Context tools for OpenViking MCP via curl."""

import json
import logging
import os
import subprocess
import urllib.parse
from typing import Optional

log = logging.getLogger("openviking-mcp.context")

OV_BASE = os.environ.get("VIKING_BASE_URL", "http://127.0.0.1:1933")
OV_API_KEY = os.environ.get("VIKING_API_KEY", "")
OV_ACCOUNT = os.environ.get("VIKING_ACCOUNT", "default")
OV_USER = os.environ.get("VIKING_USER", "default")


def _get_headers():
    headers = ["Content-Type: application/json"]
    if OV_API_KEY:
        headers.append(f"X-API-Key: {OV_API_KEY}")
    headers.extend([f"X-OpenViking-Account: {OV_ACCOUNT}", f"X-OpenViking-User: {OV_USER}"])
    return headers


def _curl_get(path: str, params: dict = None) -> dict:
    url = f"{OV_BASE}{path}"
    if params:
        url += "?" + "&".join(f"{k}={urllib.parse.quote(str(v), safe='')}" for k, v in params.items())
    cmd = ["curl", "-s", "--noproxy", "*", "-X", "GET", url]
    for h in _get_headers():
        cmd.extend(["-H", h])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not r.stdout.strip():
        return {}
    return json.loads(r.stdout)


def _curl_post(path: str, data: dict) -> dict:
    url = f"{OV_BASE}{path}"
    cmd = ["curl", "-s", "--noproxy", "*", "-X", "POST", url]
    for h in _get_headers():
        cmd.extend(["-H", h])
    cmd.extend(["-d", json.dumps(data)])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not r.stdout.strip():
        return {}
    return json.loads(r.stdout)


def search(query: str, limit: int = 10, project: Optional[str] = None) -> str:
    """Search across all context."""
    try:
        result = _curl_post("/api/v1/search/search", {"query": query, "limit": limit})
        memories = result.get("result", {}).get("memories", []) if isinstance(result.get("result"), dict) else result.get("result", [])
        return json.dumps({"success": True, "query": query, "results": memories, "count": len(memories)}, ensure_ascii=False)
    except Exception as e:
        log.exception("search failed")
        return json.dumps({"success": False, "error": str(e)})


def context_abstract(path: str) -> str:
    """L0: Get one-sentence abstract."""
    try:
        uri = f"viking://{path}" if not path.startswith("viking://") else path
        result = _curl_get("/api/v1/content/abstract", {"uri": uri})
        return json.dumps({"success": True, "path": path, "level": "L0", "abstract": result.get("result", "")}, ensure_ascii=False)
    except Exception as e:
        log.exception("context_abstract failed")
        return json.dumps({"success": False, "error": str(e)})


def context_overview(path: str) -> str:
    """L1: Get overview."""
    try:
        uri = f"viking://{path}" if not path.startswith("viking://") else path
        result = _curl_get("/api/v1/content/overview", {"uri": uri})
        return json.dumps({"success": True, "path": path, "level": "L1", "overview": result.get("result", "")}, ensure_ascii=False)
    except Exception as e:
        log.exception("context_overview failed")
        return json.dumps({"success": False, "error": str(e)})


def context_read(path: str, offset: int = 0, limit: int = -1) -> str:
    """L2: Get full content."""
    try:
        uri = f"viking://{path}" if not path.startswith("viking://") else path
        result = _curl_get("/api/v1/content/read", {"uri": uri, "offset": offset, "limit": limit})
        return json.dumps({"success": True, "path": path, "level": "L2", "content": result.get("result", "")}, ensure_ascii=False)
    except Exception as e:
        log.exception("context_read failed")
        return json.dumps({"success": False, "error": str(e)})


def context_write(path: str, content: str, metadata: Optional[dict] = None) -> str:
    """Write/store context."""
    try:
        uri = f"viking://{path}" if not path.startswith("viking://") else path
        result = _curl_post("/api/v1/resources", {"path": path, "instruction": content, "reason": metadata.get("reason", "MCP write") if metadata else "MCP write", "wait": True})
        return json.dumps({"success": True, "path": path, "result": result}, ensure_ascii=False)
    except Exception as e:
        log.exception("context_write failed")
        return json.dumps({"success": False, "error": str(e)})

"""Resource and relation tools for OpenViking MCP via curl."""

import json
import logging
import os
import subprocess
import urllib.parse
from typing import Optional

log = logging.getLogger("openviking-mcp.resources")

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


def resource_ls(path: Optional[str] = None) -> str:
    """List resources at a path."""
    try:
        uri = f"viking://{path}" if path else "viking://"
        result = _curl_get("/api/v1/fs/ls", {"path": uri})
        items = result.get("result", {}).get("items", []) if isinstance(result.get("result"), dict) else result.get("result", [])
        return json.dumps({"success": True, "path": path or "/", "items": items}, ensure_ascii=False)
    except Exception as e:
        log.exception("resource_ls failed")
        return json.dumps({"success": False, "error": str(e)})


def resource_tree(path: Optional[str] = None, depth: int = 3) -> str:
    """Get tree view of resources."""
    try:
        uri = f"viking://{path}" if path else "viking://"
        result = _curl_get("/api/v1/fs/tree", {"path": uri, "depth": depth})
        return json.dumps({"success": True, "path": path or "/", "tree": result.get("result", {})}, ensure_ascii=False)
    except Exception as e:
        log.exception("resource_tree failed")
        return json.dumps({"success": False, "error": str(e)})


def relation_link(from_path: str, to_path: str, relation_type: Optional[str] = None) -> str:
    """Create a relation between two contexts."""
    try:
        from_uri = f"viking://{from_path}" if not from_path.startswith("viking://") else from_path
        to_uri = f"viking://{to_path}" if not to_path.startswith("viking://") else to_path
        result = _curl_post("/api/v1/relations/link", {"from_uri": from_uri, "to_uri": to_uri, "reason": relation_type or ""})
        return json.dumps({"success": True, "from": from_path, "to": to_path, "relation_type": relation_type, "result": result}, ensure_ascii=False)
    except Exception as e:
        log.exception("relation_link failed")
        return json.dumps({"success": False, "error": str(e)})


def relation_list(path: str) -> str:
    """Get relations for a context."""
    try:
        uri = f"viking://{path}" if not path.startswith("viking://") else path
        result = _curl_get("/api/v1/relations", {"uri": uri})
        return json.dumps({"success": True, "path": path, "relations": result.get("result", [])}, ensure_ascii=False)
    except Exception as e:
        log.exception("relation_list failed")
        return json.dumps({"success": False, "error": str(e)})

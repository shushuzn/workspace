"""Session management tools for OpenViking MCP via curl."""

import json
import logging
import os
import subprocess
from typing import Optional

log = logging.getLogger("openviking-mcp.session")

OV_BASE = os.environ.get("VIKING_BASE_URL", "http://127.0.0.1:1933")
OV_API_KEY = os.environ.get("VIKING_API_KEY", "")
OV_ACCOUNT = os.environ.get("VIKING_ACCOUNT", "default")
OV_USER = os.environ.get("VIKING_USER", "default")

_current_session_id: Optional[str] = None


def _curl(method: str, path: str, data: dict = None) -> dict:
    url = f"{OV_BASE}{path}"
    cmd = ["curl", "-s", "--noproxy", "*", "-X", method, url,
           "-H", "Content-Type: application/json"]
    if OV_API_KEY:
        cmd.extend(["-H", f"X-API-Key: {OV_API_KEY}"])
    cmd.extend([
        "-H", f"X-OpenViking-Account: {OV_ACCOUNT}",
        "-H", f"X-OpenViking-User: {OV_USER}"
    ])
    if data:
        cmd.extend(["-d", json.dumps(data)])
    r = subprocess.run(cmd, capture_output=True, text=True)
    if not r.stdout.strip():
        return {}
    return json.loads(r.stdout)


def session_create(project: Optional[str] = None, metadata: Optional[dict] = None) -> str:
    """Create a new session."""
    try:
        result = _curl("POST", "/api/v1/sessions", {"account_id": OV_ACCOUNT, "user_id": OV_USER})
        result_data = result.get("result", result)
        global _current_session_id
        _current_session_id = result_data.get("session_id")
        return json.dumps({"success": True, "session_id": _current_session_id, "project": project, "metadata": metadata or {}}, ensure_ascii=False)
    except Exception as e:
        log.exception("session_create failed")
        return json.dumps({"success": False, "error": str(e)})


def session_info(session_id: Optional[str] = None) -> str:
    """Get session details."""
    try:
        sid = session_id or _current_session_id
        if not sid:
            return json.dumps({"success": False, "error": "No session ID"})
        info = _curl("GET", f"/api/v1/sessions/{sid}")
        return json.dumps({"success": True, "session": info.get("result", info), "current": sid == _current_session_id}, ensure_ascii=False)
    except Exception as e:
        log.exception("session_info failed")
        return json.dumps({"success": False, "error": str(e)})


def session_add_message(session_id: str, role: str, content: str) -> str:
    """Add a message to a session."""
    try:
        if role not in ("user", "assistant"):
            return json.dumps({"success": False, "error": "role must be 'user' or 'assistant'"})
        result = _curl("POST", f"/api/v1/sessions/{session_id}/messages", {"role": role, "content": content})
        return json.dumps({"success": True, "result": result}, ensure_ascii=False)
    except Exception as e:
        log.exception("session_add_message failed")
        return json.dumps({"success": False, "error": str(e)})


def session_commit(session_id: str) -> str:
    """Commit (persist) a session."""
    try:
        result = _curl("POST", f"/api/v1/sessions/{session_id}/commit", {})
        return json.dumps({"success": True, "result": result}, ensure_ascii=False)
    except Exception as e:
        log.exception("session_commit failed")
        return json.dumps({"success": False, "error": str(e)})


def session_export(session_id: Optional[str] = None, output_path: Optional[str] = None) -> str:
    """Export session state to a portable JSON file."""
    try:
        import os as _os
        sid = session_id or _current_session_id
        if not sid:
            return json.dumps({"success": False, "error": "No session ID"})
        info = _curl("GET", f"/api/v1/sessions/{sid}")
        messages_resp = _curl("GET", f"/api/v1/sessions/{sid}/messages")
        messages = messages_resp.get("result", messages_resp) if isinstance(messages_resp, dict) else []
        export_data = {
            "session_id": sid,
            "info": info.get("result", info) if isinstance(info, dict) else info,
            "messages": messages,
            "exported_at": str(__import__("datetime").datetime.now()),
        }
        path = output_path or f"session_backup_{sid[:8]}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(export_data, f, ensure_ascii=False, indent=2)
        return json.dumps({"success": True, "path": _os.path.abspath(path)}, ensure_ascii=False)
    except Exception as e:
        log.exception("session_export failed")
        return json.dumps({"success": False, "error": str(e)})


def session_import(input_path: str, project: Optional[str] = None, metadata: Optional[dict] = None) -> str:
    """Import session state from a portable JSON file."""
    try:
        import os as _os
        if not _os.path.exists(input_path):
            return json.dumps({"success": False, "error": f"File not found: {input_path}"})
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        messages = data.get("messages", [])
        # create new session
        create_result = session_create(project=project, metadata=metadata)
        create_parsed = json.loads(create_result)
        if not create_parsed.get("success"):
            return create_result
        new_sid = create_parsed.get("session_id")
        # replay messages
        for msg in messages:
            role = msg.get("role")
            content = msg.get("content", "")
            if role in ("user", "assistant") and content:
                session_add_message(new_sid, role, content)
        return json.dumps({"success": True, "session_id": new_sid, "messages_restored": len(messages)}, ensure_ascii=False)
    except Exception as e:
        log.exception("session_import failed")
        return json.dumps({"success": False, "error": str(e)})


def session_list() -> str:
    """List all sessions."""
    try:
        sessions = _curl("GET", "/api/v1/sessions")
        return json.dumps({"success": True, "sessions": sessions.get("result", []), "current": _current_session_id}, ensure_ascii=False)
    except Exception as e:
        log.exception("session_list failed")
        return json.dumps({"success": False, "error": str(e)})

"""OpenViking MCP Server.

Provides context management, session persistence, and knowledge sharing
via the Model Context Protocol (JSON-RPC 2.0 over stdio).
"""

from __future__ import annotations

import asyncio
import json
import logging
import sys
from typing import Any, Optional

try:
    from .tools import (
        session_create,
        session_info,
        session_add_message,
        session_commit,
        session_list,
        search,
        context_abstract,
        context_overview,
        context_read,
        context_write,
        resource_ls,
        resource_tree,
        relation_link,
        relation_list,
    )
except ImportError:
    from tools import (
        session_create,
        session_info,
        session_add_message,
        session_commit,
        session_list,
        search,
        context_abstract,
        context_overview,
        context_read,
        context_write,
        resource_ls,
        resource_tree,
        relation_link,
        relation_list,
    )

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger("openviking-mcp")


# ─────────────────────────────────────────────────────────────
# MCP Protocol (JSON-RPC 2.0)
# ─────────────────────────────────────────────────────────────


class MCPResponse:
    """Encapsulates an MCP JSON-RPC response or notification."""

    def __init__(
        self,
        jsonrpc: str = "2.0",
        id: Optional[int | str] = None,
        result: Any = None,
        error: Optional[dict] = None,
    ):
        self.jsonrpc = jsonrpc
        self.id = id
        self.result = result
        self.error = error

    def to_dict(self) -> dict:
        d = {"jsonrpc": self.jsonrpc}
        if self.id is not None:
            d["id"] = self.id
        if self.error is not None:
            d["error"] = self.error
        elif self.result is not None:
            d["result"] = self.result
        return d

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


# ─────────────────────────────────────────────────────────────
# Tool Registry
# ─────────────────────────────────────────────────────────────


TOOL_FUNCTIONS = {
    # Session tools
    "session_create": session_create,
    "session_info": session_info,
    "session_add_message": session_add_message,
    "session_commit": session_commit,
    "session_list": session_list,
    # Context tools
    "search": search,
    "context_abstract": context_abstract,
    "context_overview": context_overview,
    "context_read": context_read,
    "context_write": context_write,
    # Resource tools
    "resource_ls": resource_ls,
    "resource_tree": resource_tree,
    "relation_link": relation_link,
    "relation_list": relation_list,
}


# ─────────────────────────────────────────────────────────────
# MCP Handlers
# ─────────────────────────────────────────────────────────────


def handle_initialize(params: dict) -> dict:
    """Handle MCP initialize request."""
    return {
        "protocolVersion": "2024-11-05",
        "capabilities": {
            "tools": {
                "listChanged": True,
            },
        },
        "serverInfo": {
            "name": "openviking-mcp",
            "version": "0.1.0",
        },
    }


def handle_tools_list() -> dict:
    """Handle tools/list request - return all available tools."""
    tools = [
        # ── Session Tools ──
        {
            "name": "session_create",
            "description": "Create a new session for storing conversation context.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "project": {"type": "string", "description": "Optional project name"},
                    "metadata": {"type": "object", "description": "Optional metadata"},
                },
            },
        },
        {
            "name": "session_info",
            "description": "Get details about a session.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID (uses current if not provided)"},
                },
            },
        },
        {
            "name": "session_add_message",
            "description": "Add a message to a session.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID"},
                    "role": {"type": "string", "enum": ["user", "assistant"], "description": "Message role"},
                    "content": {"type": "string", "description": "Message content"},
                },
                "required": ["session_id", "role", "content"],
            },
        },
        {
            "name": "session_commit",
            "description": "Persist/commit a session to storage.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "session_id": {"type": "string", "description": "Session ID to commit"},
                },
                "required": ["session_id"],
            },
        },
        {
            "name": "session_list",
            "description": "List all sessions.",
            "inputSchema": {
                "type": "object",
                "properties": {},
            },
        },
        # ── Context Tools ──
        {
            "name": "search",
            "description": "Search across all context stored in OpenViking.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query string"},
                    "limit": {"type": "integer", "description": "Max results (default 10)"},
                    "project": {"type": "string", "description": "Filter by project name"},
                },
                "required": ["query"],
            },
        },
        {
            "name": "context_abstract",
            "description": "L0: Get one-sentence abstract/summary (~100 tokens).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Context path"},
                },
                "required": ["path"],
            },
        },
        {
            "name": "context_overview",
            "description": "L1: Get overview with core info (~2k tokens).",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Context path"},
                },
                "required": ["path"],
            },
        },
        {
            "name": "context_read",
            "description": "L2: Get full content of a context path.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Context path"},
                    "offset": {"type": "integer", "description": "Read offset (default 0)"},
                    "limit": {"type": "integer", "description": "Max bytes (default -1 = all)"},
                },
                "required": ["path"],
            },
        },
        {
            "name": "context_write",
            "description": "Write/store context at a path.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Context path"},
                    "content": {"type": "string", "description": "Content to store"},
                    "metadata": {"type": "object", "description": "Optional metadata"},
                },
                "required": ["path", "content"],
            },
        },
        # ── Resource Tools ──
        {
            "name": "resource_ls",
            "description": "List resources at a path.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path (defaults to root)"},
                },
            },
        },
        {
            "name": "resource_tree",
            "description": "Get tree view of resources.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Path (defaults to root)"},
                    "depth": {"type": "integer", "description": "Max depth (default 3)"},
                },
            },
        },
        {
            "name": "relation_link",
            "description": "Create a relation between two contexts.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "from_path": {"type": "string", "description": "Source context path"},
                    "to_path": {"type": "string", "description": "Target context path"},
                    "relation_type": {"type": "string", "description": "Relation type (e.g. 'related')"},
                },
                "required": ["from_path", "to_path"],
            },
        },
        {
            "name": "relation_list",
            "description": "Get relations for a context.",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "path": {"type": "string", "description": "Context path"},
                },
                "required": ["path"],
            },
        },
    ]

    return {"tools": tools}


def handle_tools_call(params: dict) -> dict:
    """Handle tools/call request - execute a tool function."""
    name = params.get("name", "")
    arguments = params.get("arguments", {})

    if name not in TOOL_FUNCTIONS:
        return {"content": [{"type": "text", "text": json.dumps({"error": f"Unknown tool: {name}"})}]}

    try:
        func = TOOL_FUNCTIONS[name]
        result = func(**arguments)

        # Try to parse result as JSON for better display
        try:
            parsed = json.loads(result)
            text = json.dumps(parsed, indent=2, ensure_ascii=False)
        except Exception:
            text = str(result)

        return {
            "content": [
                {
                    "type": "text",
                    "text": text,
                }
            ]
        }
    except TypeError as e:
        # Missing or invalid argument
        return {"content": [{"type": "text", "text": json.dumps({"error": f"Invalid arguments: {e}", "tool": name, "provided": arguments})}]}
    except Exception as e:
        log.exception("Tool %s failed", name)
        return {"content": [{"type": "text", "text": json.dumps({"error": str(e), "tool": name})}]}


def handle_request(method: str, params: dict, req_id: Any) -> MCPResponse:
    """Route MCP requests to handlers."""
    if method == "initialize":
        return MCPResponse(id=req_id, result=handle_initialize(params))
    elif method == "tools/list":
        return MCPResponse(id=req_id, result=handle_tools_list())
    elif method == "tools/call":
        return MCPResponse(id=req_id, result=handle_tools_call(params))
    elif method in ("initialized", "shutdown"):
        # Notifications - no response needed
        return MCPResponse(id=None, result=None)
    else:
        return MCPResponse(
            id=req_id,
            error={"code": -32601, "message": f"Method not found: {method}"},
        )


async def read_message() -> Optional[dict]:
    """Read one JSON-RPC message from stdin."""
    try:
        line = sys.stdin.readline()
        if not line:
            return None
        return json.loads(line.strip())
    except Exception:
        return None


async def write_message(msg: MCPResponse) -> None:
    """Write one JSON-RPC message to stdout."""
    try:
        sys.stdout.write(msg.to_json() + "\n")
        sys.stdout.flush()
    except Exception:
        log.exception("Failed to write message")


async def run_server() -> None:
    """Run the MCP server main loop."""
    log.info("OpenViking MCP Server starting...")

    while True:
        message = await read_message()
        if message is None:
            log.info("Stdin closed, shutting down.")
            break

        method = message.get("method", "")
        params = message.get("params", {})
        req_id = message.get("id")

        try:
            response = handle_request(method, params, req_id)
            if response.id is not None:
                await write_message(response)
        except Exception:
            log.exception("Error handling %s", method)
            error_resp = MCPResponse(
                id=req_id,
                error={"code": -32603, "message": "Internal error"},
            )
            await write_message(error_resp)


def main() -> None:
    """Entry point."""
    try:
        asyncio.run(run_server())
    except KeyboardInterrupt:
        log.info("Server stopped.")


if __name__ == "__main__":
    main()

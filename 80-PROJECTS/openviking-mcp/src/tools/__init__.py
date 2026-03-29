"""OpenViking MCP Tools."""

try:
    from openviking_mcp.tools.session import (
        session_create,
        session_info,
        session_add_message,
        session_commit,
        session_list,
    )
    from openviking_mcp.tools.context import (
        search,
        context_abstract,
        context_overview,
        context_read,
        context_write,
    )
    from openviking_mcp.tools.resources import (
        resource_ls,
        resource_tree,
        relation_link,
        relation_list,
    )
except ImportError:
    from tools.session import (
        session_create,
        session_info,
        session_add_message,
        session_commit,
        session_list,
    )
    from tools.context import (
        search,
        context_abstract,
        context_overview,
        context_read,
        context_write,
    )
    from tools.resources import (
        resource_ls,
        resource_tree,
        relation_link,
        relation_list,
    )

__all__ = [
    "session_create",
    "session_info",
    "session_add_message",
    "session_commit",
    "session_list",
    "search",
    "context_abstract",
    "context_overview",
    "context_read",
    "context_write",
    "resource_ls",
    "resource_tree",
    "relation_link",
    "relation_list",
]

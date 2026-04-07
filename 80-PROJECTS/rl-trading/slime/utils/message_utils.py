"""Shared message processing utilities for OpenClaw RL."""
from typing import Any


def _flatten_message_content(content: str | list | Any) -> str:
    """Extract plain text from multimodal content lists."""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict):
                if item.get("type") == "text":
                    parts.append(item.get("text", ""))
        return " ".join(parts) if parts else ""
    return str(content) if content is not None else ""


def _normalize_messages_for_template(messages: list[dict]) -> list[dict]:
    """Make messages compatible with the chat template.

    - developer → system (templates only know 'system')
    - multimodal content lists → plain text strings
    """
    out = []
    for msg in messages:
        m = dict(msg)
        if m.get("role") == "developer":
            m["role"] = "system"
        raw = m.get("content")
        if not isinstance(raw, str) and raw is not None:
            m["content"] = _flatten_message_content(raw)
        out.append(m)
    return out

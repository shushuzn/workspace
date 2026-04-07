#!/usr/bin/env python3
"""Smoke test: verify shared utils work without GPU or external dependencies."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent / "slime"))

from utils.message_utils import _flatten_message_content, _normalize_messages_for_template

print("=== OpenClaw-RL Smoke Test (no GPU required) ===\n")


def test_flatten_message_content():
    assert _flatten_message_content("hello") == "hello"
    assert _flatten_message_content([{"type": "text", "text": "hi"}]) == "hi"
    assert _flatten_message_content([{"type": "text", "text": "a"}, {"type": "image"}]) == "a"
    assert _flatten_message_content([]) == ""
    assert _flatten_message_content(None) == ""
    print("✓ _flatten_message_content OK")


def test_normalize_messages():
    msgs = [{"role": "developer", "content": "hello"}, {"role": "user", "content": "world"}]
    result = _normalize_messages_for_template(msgs)
    assert result[0]["role"] == "system"
    assert result[1]["role"] == "user"
    assert result[0]["content"] == "hello"
    print("✓ _normalize_messages_for_template OK")


if __name__ == "__main__":
    test_flatten_message_content()
    test_normalize_messages()
    print("\nAll smoke tests passed.")

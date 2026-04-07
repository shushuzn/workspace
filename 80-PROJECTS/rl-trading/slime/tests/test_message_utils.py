"""Tests for slime.utils.message_utils."""
import pytest
from slime.utils.message_utils import _flatten_message_content, _normalize_messages_for_template


class TestFlattenMessageContent:
    def test_string_passthrough(self):
        assert _flatten_message_content("hello world") == "hello world"

    def test_plain_text_in_list(self):
        content = [{"type": "text", "text": "hello"}, {"type": "text", "text": "world"}]
        assert _flatten_message_content(content) == "hello world"

    def test_mixed_list_with_text(self):
        content = [{"type": "text", "text": "hello"}, {"type": "image", "url": "http://..."}]
        assert _flatten_message_content(content) == "hello"

    def test_empty_list(self):
        assert _flatten_message_content([]) == ""

    def test_none(self):
        assert _flatten_message_content(None) == ""

    def test_non_dict_list_item(self):
        content = [{"type": "text", "text": "valid"}, "not a dict", 123]
        assert _flatten_message_content(content) == "valid"

    def test_arbitrary_object(self):
        assert _flatten_message_content(42) == "42"


class TestNormalizeMessagesForTemplate:
    def test_developer_to_system(self):
        messages = [{"role": "developer", "content": "you are a helpful assistant"}]
        result = _normalize_messages_for_template(messages)
        assert result[0]["role"] == "system"

    def test_preserves_user_role(self):
        messages = [{"role": "user", "content": "hello"}]
        result = _normalize_messages_for_template(messages)
        assert result[0]["role"] == "user"

    def test_flattens_multimodal_content(self):
        messages = [{"role": "user", "content": [{"type": "text", "text": "hello world"}]}]
        result = _normalize_messages_for_template(messages)
        assert result[0]["content"] == "hello world"

    def test_string_content_unchanged(self):
        messages = [{"role": "user", "content": "plain string"}]
        result = _normalize_messages_for_template(messages)
        assert result[0]["content"] == "plain string"

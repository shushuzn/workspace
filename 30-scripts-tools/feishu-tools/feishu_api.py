#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu API Client - OpenClaw Integration
=========================================
Features:
- Auto token refresh with caching
- Multiple message types (text, card, image, file)
- Rate limiting and retry logic
- Comprehensive error handling

Usage:
    python feishu-api.py send_text "Hello World"
    python feishu-api.py send_card card.json
    python feishu-api.py send_image image.png
    python feishu-api.py send_file document.pdf

Author: OpenClaw Team
Date: 2026-03-14
"""

import json
import os
import sys
import time
import hashlib
import requests
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union

# Import event filter
try:
    from feishu_webhook_filter import FeishuEventFilter, patch_lark_oapi_logger
    EVENT_FILTER_ENABLED = True
except ImportError:
    EVENT_FILTER_ENABLED = False
    FeishuEventFilter = None
    patch_lark_oapi_logger = None

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "feishu-config.json"
TOKEN_CACHE_FILE = SCRIPT_DIR / "feishu-token-cache.json"

# API Endpoints
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"
AUTH_ENDPOINT = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
MESSAGE_ENDPOINT = f"{FEISHU_API_BASE}/im/v1/messages"
IMAGE_ENDPOINT = f"{FEISHU_API_BASE}/im/v1/images"
FILE_ENDPOINT = f"{FEISHU_API_BASE}/im/v1/files"


class FeishuTokenManager:
    """Manages Feishu tenant access token with automatic refresh and caching."""

    def __init__(self, app_id: str, app_secret: str, cache_file: str,
                 refresh_before_expiry: int = 300):
        self.app_id = app_id
        self.app_secret = app_secret
        self.cache_file = Path(cache_file)
        self.refresh_before_expiry = refresh_before_expiry  # seconds
        self._token: Optional[str] = None
        self._expires_at: Optional[datetime] = None

    def load_from_cache(self) -> bool:
        """Load token from cache file if valid."""
        if not self.cache_file.exists():
            return False

        try:
            with open(self.cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            expires_at = datetime.fromisoformat(data['expires_at'])
            # Refresh if expires within refresh_before_expiry seconds
            if datetime.now() + timedelta(seconds=self.refresh_before_expiry) < expires_at:
                self._token = data['token']
                self._expires_at = expires_at
                print(f"[Token] Loaded from cache (expires: {expires_at.strftime('%Y-%m-%d %H:%M:%S')})")
                return True
            else:
                print(f"[Token] Cache expired, will refresh")
                return False
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"[Token] Cache load error: {e}")
            return False

    def save_to_cache(self, token: str, expires_in: int):
        """Save token to cache file."""
        self._expires_at = datetime.now() + timedelta(seconds=expires_in)
        self._token = token

        try:
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'token': token,
                    'expires_at': self._expires_at.isoformat(),
                    'app_id': self.app_id
                }, f, indent=2)
            print(f"[Token] Saved to cache (expires: {self._expires_at.strftime('%Y-%m-%d %H:%M:%S')})")
        except Exception as e:
            print(f"[Token] Cache save error: {e}")

    def refresh(self) -> str:
        """Request new token from Feishu API."""
        print(f"[Token] Requesting new token from Feishu API...")

        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }

        try:
            response = requests.post(AUTH_ENDPOINT, json=payload, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('code') != 0:
                raise Exception(f"API error: {data.get('msg', 'Unknown error')}")

            token = data['tenant_access_token']
            expires_in = data.get('expire', 2700)

            self.save_to_cache(token, expires_in)
            return token

        except requests.exceptions.RequestException as e:
            raise Exception(f"Token refresh failed: {e}")

    def get_token(self) -> str:
        """Get valid token, refreshing if necessary."""
        if self._token and self._expires_at:
            if datetime.now() < self._expires_at - timedelta(seconds=self.refresh_before_expiry):
                return self._token

        # Try load from cache
        if self.load_from_cache():
            return self._token

        # Refresh from API
        return self.refresh()


class FeishuAPIClient:
    """Feishu API client with support for multiple message types."""

    def __init__(self, config_file: str = str(CONFIG_FILE)):
        self.config = self._load_config(config_file)
        self.token_manager = FeishuTokenManager(
            app_id=self.config['app_id'],
            app_secret=self.config['app_secret'],
            cache_file=str(SCRIPT_DIR / self.config.get('token_cache_file', 'feishu-token-cache.json')),
            refresh_before_expiry=self.config.get('token_refresh_before_expiry', 300)
        )
        self.receive_id_type = self.config.get('receive_id_type', 'open_id')
        self.default_receive_id = self.config.get('default_receive_id')

        # Initialize event filter
        self.event_filter = None
        if EVENT_FILTER_ENABLED:
            try:
                self.event_filter = FeishuEventFilter()
                print(f"[Feishu] ✅ Event filter enabled ({len(self.event_filter.list_filters())} filters)")

                # Patch lark_oapi logger to suppress filtered event errors
                if patch_lark_oapi_logger:
                    patch_lark_oapi_logger()
            except Exception as e:
                print(f"[Feishu] ⚠️  Event filter init failed: {e}")

    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        config_path = Path(config_file)
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found: {config_file}")

        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _get_headers(self) -> Dict[str, str]:
        """Get API request headers with authentication."""
        token = self.token_manager.get_token()
        return {
            'Authorization': f'Bearer {token}',
            'Content-Type': 'application/json'
        }

    def _api_request(self, method: str, url: str,
                     params: Optional[Dict] = None,
                     data: Optional[Dict] = None,
                     files: Optional[Dict] = None,
                     retry: int = 3) -> Dict[str, Any]:
        """Make API request with retry logic."""
        last_error = None

        for attempt in range(retry):
            try:
                if method == 'GET':
                    response = requests.get(url, params=params, headers=self._get_headers(), timeout=30)
                elif method == 'POST':
                    if files:
                        response = requests.post(url, params=params, files=files, timeout=60)
                    else:
                        response = requests.post(url, params=params, json=data, headers=self._get_headers(), timeout=30)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                result = response.json()

                # Check for API-level errors
                if result.get('code') not in [0, '0']:
                    if result.get('code') == 99991663:  # Token expired
                        self.token_manager._token = None  # Force refresh
                        if attempt < retry - 1:
                            print(f"[API] Token expired, retrying with fresh token...")
                            continue
                    raise Exception(f"API error {result.get('code')}: {result.get('msg', 'Unknown error')}")

                return result

            except Exception as e:
                last_error = e
                print(f"[API] Attempt {attempt + 1}/{retry} failed: {e}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

        raise Exception(f"All {retry} attempts failed. Last error: {last_error}")

    def send_text(self, text: str, receive_id: Optional[str] = None) -> Dict[str, Any]:
        """Send text message."""
        receive_id = receive_id or self.default_receive_id
        if not receive_id:
            raise ValueError("receive_id is required")

        data = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": text})
        }

        result = self._api_request('POST', MESSAGE_ENDPOINT,
                                   params={"receive_id_type": self.receive_id_type},
                                   data=data)

        print(f"[OK] Text message sent: {result['data']['message_id']}")
        return result

    def send_poster(self, title: str, content: list, receive_id: Optional[str] = None) -> Dict[str, Any]:
        """Send interactive card message (poster template)."""
        receive_id = receive_id or self.default_receive_id
        if not receive_id:
            raise ValueError("receive_id is required")

        card_content = {
            "config": {
                "wide_screen_mode": True
            },
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": title
                },
                "template": "blue"
            },
            "elements": content
        }

        data = {
            "receive_id": receive_id,
            "msg_type": "interactive",
            "content": json.dumps(card_content)
        }

        result = self._api_request('POST', MESSAGE_ENDPOINT,
                                   params={"receive_id_type": self.receive_id_type},
                                   data=data)

        print(f"[OK] Card message sent: {result['data']['message_id']}")
        return result

    def send_image(self, image_path: str, receive_id: Optional[str] = None) -> Dict[str, Any]:
        """Send image message."""
        receive_id = receive_id or self.default_receive_id
        if not receive_id:
            raise ValueError("receive_id is required")

        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # First upload image
        with open(image_path, 'rb') as f:
            files = {
                'image': (image_path.name, f, 'image/png')
            }
            upload_result = self._api_request('POST', IMAGE_ENDPOINT,
                                              params={"image_type": "message"},
                                              files=files)

        image_key = upload_result['data']['image_key']

        # Then send message
        data = {
            "receive_id": receive_id,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key})
        }

        result = self._api_request('POST', MESSAGE_ENDPOINT,
                                   params={"receive_id_type": self.receive_id_type},
                                   data=data)

        print(f"[OK] Image message sent: {result['data']['message_id']} (key: {image_key})")
        return result

    def send_file(self, file_path: str, receive_id: Optional[str] = None) -> Dict[str, Any]:
        """Send file message."""
        receive_id = receive_id or self.default_receive_id
        if not receive_id:
            raise ValueError("receive_id is required")

        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # First upload file
        with open(file_path, 'rb') as f:
            files = {
                'file': (file_path.name, f, 'application/octet-stream')
            }
            upload_result = self._api_request('POST', FILE_ENDPOINT,
                                              params={"file_type": "stream"},
                                              files=files)

        file_key = upload_result['data']['file_key']

        # Then send message
        data = {
            "receive_id": receive_id,
            "msg_type": "file",
            "content": json.dumps({"file_key": file_key})
        }

        result = self._api_request('POST', MESSAGE_ENDPOINT,
                                   params={"receive_id_type": self.receive_id_type},
                                   data=data)

        print(f"[OK] File message sent: {result['data']['message_id']} (key: {file_key})")
        return result

    def get_token_info(self) -> Dict[str, Any]:
        """Get current token information."""
        token = self.token_manager._token
        expires_at = self.token_manager._expires_at

        if not token:
            # Try load from cache
            self.token_manager.load_from_cache()
            token = self.token_manager._token
            expires_at = self.token_manager._expires_at

        if not token:
            return {"status": "no_token", "message": "Token not yet obtained"}

        now = datetime.now()
        time_left = (expires_at - now).total_seconds() if expires_at else 0

        return {
            "status": "valid" if time_left > 0 else "expired",
            "token_preview": f"{token[:20]}...",
            "expires_at": expires_at.isoformat() if expires_at else None,
            "time_left_seconds": max(0, int(time_left)),
            "time_left_formatted": f"{int(time_left // 60)}m {int(time_left % 60)}s" if time_left > 0 else "0s"
        }


def print_usage():
    """Print usage information."""
    usage = """
Feishu API Client - OpenClaw Integration
=========================================

Usage:
    python feishu-api.py <command> [arguments]

Commands:
    send_text <message> [receive_id]     Send text message
    send_card <card.json> [receive_id]   Send interactive card message
    send_image <image.png> [receive_id]  Send image message
    send_file <document.pdf> [receive_id] Send file message
    token_info                           Show current token status
    refresh_token                        Force refresh token

Examples:
    python feishu-api.py send_text "Hello World"
    python feishu-api.py send_text "Hello" ou_xxxxx
    python feishu-api.py send_card card.json
    python feishu-api.py send_image screenshot.png
    python feishu-api.py send_file report.pdf
    python feishu-api.py token_info

Configuration:
    Edit feishu-config.json to set app credentials and defaults
"""
    print(usage)


def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    try:
        client = FeishuAPIClient()

        if command == "send_text":
            if len(sys.argv) < 3:
                print("Error: Message text required")
                print("Usage: python feishu-api.py send_text <message> [receive_id]")
                sys.exit(1)
            text = sys.argv[2]
            receive_id = sys.argv[3] if len(sys.argv) > 3 else None
            client.send_text(text, receive_id)

        elif command == "send_card":
            if len(sys.argv) < 3:
                print("Error: Card JSON file required")
                print("Usage: python feishu-api.py send_card <card.json> [receive_id]")
                sys.exit(1)
            card_file = sys.argv[2]
            receive_id = sys.argv[3] if len(sys.argv) > 3 else None

            with open(card_file, 'r', encoding='utf-8') as f:
                card_content = json.load(f)

            title = card_content.get('title', 'Notification')
            elements = card_content.get('elements', [])
            client.send_poster(title, elements, receive_id)

        elif command == "send_image":
            if len(sys.argv) < 3:
                print("Error: Image file required")
                print("Usage: python feishu-api.py send_image <image.png> [receive_id]")
                sys.exit(1)
            image_file = sys.argv[2]
            receive_id = sys.argv[3] if len(sys.argv) > 3 else None
            client.send_image(image_file, receive_id)

        elif command == "send_file":
            if len(sys.argv) < 3:
                print("Error: File required")
                print("Usage: python feishu-api.py send_file <document.pdf> [receive_id]")
                sys.exit(1)
            file_path = sys.argv[2]
            receive_id = sys.argv[3] if len(sys.argv) > 3 else None
            client.send_file(file_path, receive_id)

        elif command == "token_info":
            info = client.get_token_info()
            print("\nToken Information:")
            print(f"  Status: {info['status']}")
            if info['status'] != 'no_token':
                print(f"  Token: {info['token_preview']}")
                print(f"  Expires: {info['expires_at']}")
                print(f"  Time Left: {info['time_left_formatted']}")
            print()

        elif command == "refresh_token":
            token = client.token_manager.refresh()
            print(f"\n[OK] Token refreshed successfully")
            print(f"  Token: {token[:20]}...")
            print()

        else:
            print(f"Error: Unknown command '{command}'")
            print_usage()
            sys.exit(1)

    except Exception as e:
        print(f"\n[ERROR] Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

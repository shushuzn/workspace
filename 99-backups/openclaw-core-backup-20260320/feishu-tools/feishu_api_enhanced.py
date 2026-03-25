#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Feishu API Client - Enhanced Version
=====================================
Features:
- Auto token refresh with caching
- Multiple message types (text, card, image, file)
- Image compression (Pillow)
- Message queue (batch sending)
- Statistics tracking (success rate, latency)
- @User mention support
- Rate limiting and retry logic
- Comprehensive error handling

Usage:
    python feishu_api_enhanced.py send_text "Hello" --mention user1,user2
    python feishu_api_enhanced.py send_image photo.png --compress
    python feishu_api_enhanced.py queue_add "Message 1"
    python feishu_api_enhanced.py queue_send
    python feishu_api_enhanced.py stats

Author: OpenClaw Team
Date: 2026-03-14
Version: 2.0.0 Enhanced
"""

import json
import os
import sys
import time
import hashlib
import requests
from pathlib import Path
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, Union, List
from io import BytesIO

# Pillow for image compression
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("[Warning] Pillow not installed. Image compression disabled.")
    print("Install: pip install pillow")

# Configuration
SCRIPT_DIR = Path(__file__).parent
CONFIG_FILE = SCRIPT_DIR / "feishu-config.json"
TOKEN_CACHE_FILE = SCRIPT_DIR / "feishu-token-cache.json"
QUEUE_FILE = SCRIPT_DIR / "feishu-message-queue.json"
STATS_FILE = SCRIPT_DIR / "feishu-stats.json"

# API Endpoints
FEISHU_API_BASE = "https://open.feishu.cn/open-apis"
AUTH_ENDPOINT = f"{FEISHU_API_BASE}/auth/v3/tenant_access_token/internal"
MESSAGE_ENDPOINT = f"{FEISHU_API_BASE}/im/v1/messages"
IMAGE_ENDPOINT = f"{FEISHU_API_BASE}/im/v1/images"
FILE_ENDPOINT = f"{FEISHU_API_BASE}/im/v1/files"


class FeishuStatistics:
    """Track message sending statistics."""

    def __init__(self, stats_file: str = str(STATS_FILE)):
        self.stats_file = Path(stats_file)
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        """Load statistics from file."""
        if not self.stats_file.exists():
            return {
                "total_sent": 0,
                "total_failed": 0,
                "total_latency_ms": 0,
                "last_reset": datetime.now().isoformat(),
                "by_type": {
                    "text": {"sent": 0, "failed": 0},
                    "card": {"sent": 0, "failed": 0},
                    "image": {"sent": 0, "failed": 0},
                    "file": {"sent": 0, "failed": 0}
                },
                "hourly": {}
            }

        try:
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {
                "total_sent": 0,
                "total_failed": 0,
                "total_latency_ms": 0,
                "last_reset": datetime.now().isoformat(),
                "by_type": {
                    "text": {"sent": 0, "failed": 0},
                    "card": {"sent": 0, "failed": 0},
                    "image": {"sent": 0, "failed": 0},
                    "file": {"sent": 0, "failed": 0}
                },
                "hourly": {}
            }

    def _save_stats(self):
        """Save statistics to file."""
        try:
            with open(self.stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Warning] Failed to save stats: {e}")

    def record_success(self, msg_type: str, latency_ms: int):
        """Record successful message send."""
        self.stats["total_sent"] += 1
        self.stats["total_latency_ms"] += latency_ms

        if msg_type in self.stats["by_type"]:
            self.stats["by_type"][msg_type]["sent"] += 1

        # Hourly stats
        hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
        if hour_key not in self.stats["hourly"]:
            self.stats["hourly"][hour_key] = {"sent": 0, "failed": 0}
        self.stats["hourly"][hour_key]["sent"] += 1

        self._save_stats()

    def record_failure(self, msg_type: str):
        """Record failed message send."""
        self.stats["total_failed"] += 1

        if msg_type in self.stats["by_type"]:
            self.stats["by_type"][msg_type]["failed"] += 1

        # Hourly stats
        hour_key = datetime.now().strftime("%Y-%m-%d %H:00")
        if hour_key not in self.stats["hourly"]:
            self.stats["hourly"][hour_key] = {"sent": 0, "failed": 0}
        self.stats["hourly"][hour_key]["failed"] += 1

        self._save_stats()

    def get_summary(self) -> Dict[str, Any]:
        """Get statistics summary."""
        total = self.stats["total_sent"] + self.stats["total_failed"]
        success_rate = (self.stats["total_sent"] / total * 100) if total > 0 else 0
        avg_latency = (self.stats["total_latency_ms"] / self.stats["total_sent"]) if self.stats["total_sent"] > 0 else 0

        return {
            "total_messages": total,
            "success_rate": f"{success_rate:.2f}%",
            "avg_latency_ms": f"{avg_latency:.2f}ms",
            "by_type": self.stats["by_type"],
            "last_reset": self.stats["last_reset"]
        }

    def reset(self):
        """Reset statistics."""
        self.stats = {
            "total_sent": 0,
            "total_failed": 0,
            "total_latency_ms": 0,
            "last_reset": datetime.now().isoformat(),
            "by_type": {
                "text": {"sent": 0, "failed": 0},
                "card": {"sent": 0, "failed": 0},
                "image": {"sent": 0, "failed": 0},
                "file": {"sent": 0, "failed": 0}
            },
            "hourly": {}
        }
        self._save_stats()


class FeishuMessageQueue:
    """Message queue for batch sending."""

    def __init__(self, queue_file: str = str(QUEUE_FILE)):
        self.queue_file = Path(queue_file)
        self.queue = self._load_queue()

    def _load_queue(self) -> List[Dict[str, Any]]:
        """Load queue from file."""
        if not self.queue_file.exists():
            return []

        try:
            with open(self.queue_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return []

    def _save_queue(self):
        """Save queue to file."""
        try:
            with open(self.queue_file, 'w', encoding='utf-8') as f:
                json.dump(self.queue, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[Warning] Failed to save queue: {e}")

    def add(self, msg_type: str, content: Any, receive_id: str = None,
            mention_users: List[str] = None, priority: int = 0):
        """Add message to queue."""
        message = {
            "id": hashlib.md5(f"{time.time()}{content}".encode()).hexdigest()[:8],
            "type": msg_type,
            "content": content,
            "receive_id": receive_id,
            "mention_users": mention_users or [],
            "priority": priority,
            "created_at": datetime.now().isoformat(),
            "attempts": 0,
            "status": "pending"
        }

        self.queue.append(message)
        # Sort by priority (higher first)
        self.queue.sort(key=lambda x: x["priority"], reverse=True)
        self._save_queue()

        print(f"[OK] Message queued: {message['id']}")
        return message["id"]

    def remove(self, message_id: str):
        """Remove message from queue."""
        self.queue = [m for m in self.queue if m["id"] != message_id]
        self._save_queue()
        print(f"[OK] Message removed: {message_id}")

    def clear(self):
        """Clear all messages from queue."""
        self.queue = []
        self._save_queue()
        print("[OK] Queue cleared")

    def list_messages(self) -> List[Dict[str, Any]]:
        """List all queued messages."""
        return self.queue

    def count(self) -> int:
        """Get queue size."""
        return len(self.queue)


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


class FeishuImageCompressor:
    """Compress images before sending."""

    @staticmethod
    def compress(image_path: str, max_width: int = 1200, quality: int = 80,
                 output_path: str = None) -> str:
        """
        Compress image for sending.
        
        Args:
            image_path: Path to input image
            max_width: Maximum width (maintains aspect ratio)
            quality: JPEG quality (1-100, higher = better quality)
            output_path: Output path (default: {original}_compressed.jpg)
        
        Returns:
            Path to compressed image
        """
        if not PILLOW_AVAILABLE:
            print("[Warning] Pillow not available, returning original image")
            return image_path

        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        if output_path is None:
            output_path = image_path.parent / f"{image_path.stem}_compressed.jpg"
        else:
            output_path = Path(output_path)

        try:
            with Image.open(image_path) as img:
                # Convert to RGB if necessary (for PNG with transparency)
                if img.mode in ('RGBA', 'LA', 'P'):
                    img = img.convert('RGB')

                # Resize if too large
                if img.width > max_width:
                    ratio = max_width / img.width
                    new_height = int(img.height * ratio)
                    img = img.resize((max_width, new_height), Image.Resampling.LANCZOS)
                    print(f"[Compress] Resized from {img.width}x{img.height}")

                # Save as JPEG with quality
                img.save(output_path, 'JPEG', quality=quality, optimize=True, progressive=True)

                # Report compression ratio
                original_size = image_path.stat().st_size
                compressed_size = output_path.stat().st_size
                ratio = (1 - compressed_size / original_size) * 100

                print(f"[Compress] {image_path.name}: {original_size /1024:.1f}KB → {compressed_size /1024:.1f}KB ({ratio:.1f}% reduction)")

                return str(output_path)

        except Exception as e:
            print(f"[Warning] Compression failed: {e}, using original")
            return image_path


class FeishuAPIClient:
    """Enhanced Feishu API client with advanced features."""

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
        self.stats = FeishuStatistics()
        self.queue = FeishuMessageQueue()
        self.compressor = FeishuImageCompressor()

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
                start_time = time.time()

                # Prepare headers
                headers = self._get_headers()
                if files:
                    # Remove Content-Type for file uploads (requests will set it with boundary)
                    headers.pop('Content-Type', None)

                if method == 'GET':
                    response = requests.get(url, params=params, headers=headers, timeout=30)
                elif method == 'POST':
                    if files:
                        response = requests.post(url, params=params, files=files, timeout=60)
                    else:
                        response = requests.post(url, params=params, json=data, headers=headers, timeout=30)
                else:
                    raise ValueError(f"Unsupported method: {method}")

                response.raise_for_status()
                result = response.json()

                # Debug: Print error details if available
                if result.get('code') not in [0, '0'] and 'msg' in result:
                    print(f"[DEBUG] API Response: {json.dumps(result, indent=2)}")

                latency_ms = int((time.time() - start_time) * 1000)

                # Check for API-level errors
                if result.get('code') not in [0, '0']:
                    if result.get('code') == 99991663:  # Token expired
                        self.token_manager._token = None  # Force refresh
                        if attempt < retry - 1:
                            print(f"[API] Token expired, retrying with fresh token...")
                            continue
                    raise Exception(f"API error {result.get('code')}: {result.get('msg', 'Unknown error')}")

                return result, latency_ms

            except Exception as e:
                last_error = e
                print(f"[API] Attempt {attempt + 1}/{retry} failed: {e}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff

        raise Exception(f"All {retry} attempts failed. Last error: {last_error}")

    def _build_mention_tag(self, mention_users: List[str]) -> str:
        """Build mention tag for text messages."""
        if not mention_users:
            return ""

        mention_tags = []
        for user_id in mention_users:
            mention_tags.append(f'<at user_id="{user_id}"></at>')

        return " ".join(mention_tags)

    def send_text(self, text: str, receive_id: Optional[str] = None,
                  mention_users: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send text message with optional @mentions."""
        receive_id = receive_id or self.default_receive_id
        if not receive_id:
            raise ValueError("receive_id is required")

        # Build content with mentions
        content_text = text
        if mention_users:
            mention_tag = self._build_mention_tag(mention_users)
            content_text = f"{mention_tag}\n{text}"

        data = {
            "receive_id": receive_id,
            "msg_type": "text",
            "content": json.dumps({"text": content_text})
        }

        result, latency_ms = self._api_request('POST', MESSAGE_ENDPOINT,
                                   params={"receive_id_type": self.receive_id_type},
                                   data=data)

        self.stats.record_success("text", latency_ms)

        mention_str = f" (mentioning {len(mention_users)} users)" if mention_users else ""
        print(f"[OK] Text message sent: {result['data']['message_id']}{mention_str} ({latency_ms}ms)")
        return result

    def send_poster(self, title: str, content: list, receive_id: Optional[str] = None,
                    mention_users: Optional[List[str]] = None) -> Dict[str, Any]:
        """Send interactive card message with optional @mentions."""
        receive_id = receive_id or self.default_receive_id
        if not receive_id:
            raise ValueError("receive_id is required")

        # Add mention to content if users specified
        if mention_users:
            mention_tag = self._build_mention_tag(mention_users)
            mention_element = {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": mention_tag
                }
            }
            content = [mention_element] + content

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

        result, latency_ms = self._api_request('POST', MESSAGE_ENDPOINT,
                                   params={"receive_id_type": self.receive_id_type},
                                   data=data)

        self.stats.record_success("card", latency_ms)

        mention_str = f" (mentioning {len(mention_users)} users)" if mention_users else ""
        print(f"[OK] Card message sent: {result['data']['message_id']}{mention_str} ({latency_ms}ms)")
        return result

    def send_image(self, image_path: str, receive_id: Optional[str] = None,
                   compress: bool = False, max_width: int = 1200,
                   quality: int = 80) -> Dict[str, Any]:
        """Send image message with optional compression."""
        receive_id = receive_id or self.default_receive_id
        if not receive_id:
            raise ValueError("receive_id is required")

        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Compress if requested
        if compress:
            actual_path = self.compressor.compress(image_path, max_width, quality)
        else:
            actual_path = str(image_path)

        # First upload image
        with open(actual_path, 'rb') as f:
            files = {
                'image': (Path(actual_path).name, f, 'image/jpeg')
            }
            upload_result, latency_ms = self._api_request('POST', IMAGE_ENDPOINT,
                                              params={"image_type": "message"},
                                              files=files)

        image_key = upload_result['data']['image_key']

        # Then send message
        data = {
            "receive_id": receive_id,
            "msg_type": "image",
            "content": json.dumps({"image_key": image_key})
        }

        result, latency_ms = self._api_request('POST', MESSAGE_ENDPOINT,
                                   params={"receive_id_type": self.receive_id_type},
                                   data=data)

        self.stats.record_success("image", latency_ms)

        compress_str = " (compressed)" if compress else ""
        print(f"[OK] Image message sent: {result['data']['message_id']}{compress_str} (key: {image_key}, {latency_ms}ms)")
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
            upload_result, latency_ms = self._api_request('POST', FILE_ENDPOINT,
                                              params={"file_type": "stream"},
                                              files=files)

        file_key = upload_result['data']['file_key']

        # Then send message
        data = {
            "receive_id": receive_id,
            "msg_type": "file",
            "content": json.dumps({"file_key": file_key})
        }

        result, latency_ms = self._api_request('POST', MESSAGE_ENDPOINT,
                                   params={"receive_id_type": self.receive_id_type},
                                   data=data)

        self.stats.record_success("file", latency_ms)

        print(f"[OK] File message sent: {result['data']['message_id']} (key: {file_key}, {latency_ms}ms)")
        return result

    def send_queued_messages(self, max_count: int = 100) -> Dict[str, Any]:
        """Send all queued messages."""
        messages = self.queue.list_messages()

        if not messages:
            print("[INFO] Queue is empty")
            return {"sent": 0, "failed": 0}

        print(f"[INFO] Sending {len(messages)} queued messages...")

        results = {"sent": 0, "failed": 0}

        for i, msg in enumerate(messages[:max_count]):
            print(f"\n[{i +1}/{len(messages)}] Processing message {msg['id']}...")

            try:
                if msg["type"] == "text":
                    self.send_text(
                        msg["content"],
                        receive_id=msg.get("receive_id"),
                        mention_users=msg.get("mention_users")
                    )
                elif msg["type"] == "card":
                    self.send_poster(
                        msg["content"]["title"],
                        msg["content"]["elements"],
                        receive_id=msg.get("receive_id"),
                        mention_users=msg.get("mention_users")
                    )
                elif msg["type"] == "image":
                    self.send_image(
                        msg["content"],
                        receive_id=msg.get("receive_id"),
                        compress=msg.get("compress", False)
                    )

                results["sent"] += 1
                self.queue.remove(msg["id"])

            except Exception as e:
                results["failed"] += 1
                msg["attempts"] += 1
                msg["last_error"] = str(e)

                # Mark as failed after 3 attempts
                if msg["attempts"] >= 3:
                    msg["status"] = "failed"
                    print(f"[FAIL] Message {msg['id']} failed after 3 attempts")
                else:
                    msg["status"] = "retry"
                    print(f"[WARN] Message {msg['id']} will be retried")

                self.queue._save_queue()

        print(f"\n[OK] Queue processing complete: {results['sent']} sent, {results['failed']} failed")
        return results

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

    def get_stats(self) -> Dict[str, Any]:
        """Get message sending statistics."""
        return self.stats.get_summary()

    def reset_stats(self):
        """Reset statistics."""
        self.stats.reset()
        print("[OK] Statistics reset")


def print_usage():
    """Print usage information."""
    usage = """
Feishu API Client - Enhanced Version 2.0
=========================================

Usage:
    python feishu_api_enhanced.py <command> [arguments] [options]

Commands:
    send_text <message> [receive_id]           Send text message
    send_text <message> --mention user1,user2  Send with @mentions
    send_card <card.json> [receive_id]         Send interactive card
    send_image <image.png> [receive_id]        Send image
    send_image <image.png> --compress          Send compressed image
    send_file <document.pdf> [receive_id]      Send file
    queue_add <message> --type text            Add to queue
    queue_send                                 Send queued messages
    queue_list                                 List queued messages
    queue_clear                                Clear queue
    stats                                      Show statistics
    stats_reset                                Reset statistics
    token_info                                 Show token status
    refresh_token                              Force refresh token

Options:
    --mention user1,user2    Add @mentions (comma-separated user IDs)
    --compress               Compress image before sending
    --quality 1-100          Image quality (default: 80)
    --max-width pixels       Max image width (default: 1200)
    --type text|card|image   Message type for queue
    --priority 0-10          Queue priority (default: 0)

Examples:
    python feishu_api_enhanced.py send_text "Hello @user" --mention ou_xxxx
    python feishu_api_enhanced.py send_image photo.png --compress
    python feishu_api_enhanced.py queue_add "Batch message" --type text --priority 5
    python feishu_api_enhanced.py queue_send
    python feishu_api_enhanced.py stats

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

        # Parse options
        args = sys.argv[2:]
        mention_users = None
        compress = False
        quality = 80
        max_width = 1200
        msg_type = "text"
        priority = 0

        i = 0
        while i < len(args):
            if args[i] == "--mention" and i + 1 < len(args):
                mention_users = args[i + 1].split(",")
                i += 2
            elif args[i] == "--compress":
                compress = True
                i += 1
            elif args[i] == "--quality" and i + 1 < len(args):
                quality = int(args[i + 1])
                i += 2
            elif args[i] == "--max-width" and i + 1 < len(args):
                max_width = int(args[i + 1])
                i += 2
            elif args[i] == "--type" and i + 1 < len(args):
                msg_type = args[i + 1]
                i += 2
            elif args[i] == "--priority" and i + 1 < len(args):
                priority = int(args[i + 1])
                i += 2
            else:
                i += 1

        if command == "send_text":
            if len(args) < 1 or args[0].startswith("--"):
                print("Error: Message text required")
                print("Usage: python feishu_api_enhanced.py send_text <message> [receive_id] [--mention users]")
                sys.exit(1)
            text = args[0]
            receive_id = args[1] if len(args) > 1 and not args[1].startswith("--") else None
            client.send_text(text, receive_id, mention_users)

        elif command == "send_card":
            if len(args) < 1:
                print("Error: Card JSON file required")
                sys.exit(1)
            card_file = args[0]
            receive_id = args[1] if len(args) > 1 else None

            with open(card_file, 'r', encoding='utf-8') as f:
                card_content = json.load(f)

            title = card_content.get('title', 'Notification')
            elements = card_content.get('elements', [])
            client.send_poster(title, elements, receive_id, mention_users)

        elif command == "send_image":
            if len(args) < 1:
                print("Error: Image file required")
                sys.exit(1)
            image_file = args[0]
            receive_id = args[1] if len(args) > 1 and not args[1].startswith("--") else None
            client.send_image(image_file, receive_id, compress, max_width, quality)

        elif command == "send_file":
            if len(args) < 1:
                print("Error: File required")
                sys.exit(1)
            file_path = args[0]
            receive_id = args[1] if len(args) > 1 else None
            client.send_file(file_path, receive_id)

        elif command == "queue_add":
            if len(args) < 1:
                print("Error: Message content required")
                sys.exit(1)
            content = args[0]
            receive_id = None
            if len(args) > 1 and not args[1].startswith("--"):
                receive_id = args[1]

            client.queue.add(msg_type, content, receive_id, mention_users, priority)

        elif command == "queue_send":
            results = client.send_queued_messages()
            print(f"\nSummary: {results['sent']} sent, {results['failed']} failed")

        elif command == "queue_list":
            messages = client.queue.list_messages()
            if not messages:
                print("Queue is empty")
            else:
                print(f"Queue ({len(messages)} messages):")
                for msg in messages:
                    print(f"  [{msg['priority']}] {msg['id']}: {msg['type']} - {msg['content'][:50]}...")

        elif command == "queue_clear":
            client.queue.clear()

        elif command == "stats":
            stats = client.get_stats()
            print("\nMessage Statistics:")
            print(f"  Total Messages: {stats['total_messages']}")
            print(f"  Success Rate: {stats['success_rate']}")
            print(f"  Avg Latency: {stats['avg_latency_ms']}")
            print(f"\nBy Type:")
            for msg_type, type_stats in stats['by_type'].items():
                total = type_stats['sent'] + type_stats['failed']
                rate = (type_stats['sent'] / total * 100) if total > 0 else 0
                print(f"  {msg_type}: {type_stats['sent']}/{total} ({rate:.1f}%)")
            print(f"\nLast Reset: {stats['last_reset']}")
            print()

        elif command == "stats_reset":
            client.reset_stats()

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
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

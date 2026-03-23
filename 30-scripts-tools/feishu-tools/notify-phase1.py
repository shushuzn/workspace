#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 1 Completion Notification
"""
import json
import requests
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path(__file__).parent / "feishu-config.json"
TOKEN_CACHE = Path(__file__).parent / "feishu-token-cache.json"

def get_token():
    with open(CONFIG_FILE, encoding='utf-8') as f:
        config = json.load(f)

    app_id = config["app_id"]
    app_secret = config["app_secret"]

    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    resp = requests.post(url, json=payload, timeout=10)
    data = resp.json()

    if data.get("code") == 0:
        token = data["tenant_access_token"]
        expires = datetime.now().timestamp() + 2700
        with open(TOKEN_CACHE, "w", encoding='utf-8') as f:
            json.dump({"token": token, "expires": expires}, f)
        return token
    else:
        raise Exception(f"Token failed: {data}")

def send_message(text):
    with open(TOKEN_CACHE, encoding='utf-8') as f:
        token = json.load(f)["token"]
    with open(CONFIG_FILE, encoding='utf-8') as f:
        config = json.load(f)

    user_id = config["default_receive_id"]
    receive_id_type = config.get("receive_id_type", "open_id")
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    payload = {
        "receive_id": user_id,
        "msg_type": "text",
        "content": json.dumps({"text": text})
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    data = resp.json()

    if data.get("code") == 0:
        print(f"[OK] Message sent: {data['data']['message_id']}")
        return True
    else:
        print(f"[FAIL] Failed: {data}")
        return False

if __name__ == "__main__":
    try:
        # Check cache
        if TOKEN_CACHE.exists():
            with open(TOKEN_CACHE, encoding='utf-8') as f:
                cache = json.load(f)
            # Support both formats
            expires = cache.get("expires") or cache.get("expires_at")
            if isinstance(expires, str):
                expires = datetime.fromisoformat(expires).timestamp()
            if expires > datetime.now().timestamp() + 300:
                token = cache["token"]
                mins = (expires - datetime.now().timestamp()) / 60
                print(f"[OK] Using cached token (expires in {mins:.0f}m)")
            else:
                token = get_token()
        else:
            token = get_token()

        message = "[Phase 1 Complete!]\n\n[OK] 7-Persona System: 91/100\n[OK] Feishu Integration v2.0\n[OK] Innovator Evolution (Phase 1-3)\n[OK] Git Commit: 57 files\n\n[WARN] Rest needed (230+ min worked)\n[NEXT] Memory distillation (Mar 16, 5AM)\n\n- OpenClaw"

        send_message(message)
    except Exception as e:
        print(f"Error: {e}")

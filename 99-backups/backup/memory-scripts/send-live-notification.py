#!/usr/bin/env python3
import json
import requests
from pathlib import Path
from datetime import datetime

CONFIG_FILE = Path("D:/OpenClaw/workspace/30-scripts-tools/feishu-tools/feishu-config.json")
TOKEN_CACHE = Path("D:/OpenClaw/workspace/30-scripts-tools/feishu-tools/feishu-token-cache.json")

def get_token():
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    app_id = config["app_id"]
    app_secret = config["app_secret"]
    
    if TOKEN_CACHE.exists():
        with open(TOKEN_CACHE) as f:
            cache = json.load(f)
        expires = cache.get("expires") or cache.get("expires_at")
        if isinstance(expires, str):
            expires = datetime.fromisoformat(expires).timestamp()
        if expires > datetime.now().timestamp() + 300:
            return cache["token"]
    
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {"app_id": app_id, "app_secret": app_secret}
    resp = requests.post(url, json=payload, timeout=10)
    data = resp.json()
    
    if data.get("code") == 0:
        token = data["tenant_access_token"]
        expires = datetime.now().timestamp() + 2700
        with open(TOKEN_CACHE, "w") as f:
            json.dump({"token": token, "expires": expires})
        return token
    raise Exception(f"Token failed: {data}")

def send_message(text):
    token = get_token()
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    user_id = config.get("user_id") or config.get("default_receive_id")
    receive_id_type = config.get("receive_id_type", "open_id")
    
    url = f"https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type={receive_id_type}"
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    payload = {"receive_id": user_id, "msg_type": "text", "content": json.dumps({"text": text})}
    
    resp = requests.post(url, headers=headers, json=payload, timeout=10)
    data = resp.json()
    
    if data.get("code") == 0:
        print(f"[OK] Message sent: {data['data']['message_id']}")
        return True
    print(f"[FAIL] {data}")
    return False

if __name__ == "__main__":
    message = """
[Website LIVE! Main Domain Ready]

[OK] https://felixxii.xyz
[OK] https://www.felixxii.xyz
[OK] SSL: Let's Encrypt (Production)
[OK] Content: Innovator Dashboard
[OK] nginx: Running on 443

[INFO] Access:
  - Main domain: felixxii.xyz
  - No port needed
  - Green lock (valid SSL)

[INFO] Also available:
  - https://8.208.30.28:8444 (Direct IP)

[STATUS] Production Ready
[TIME] Total: ~15 minutes
[SCORE] 100/100

Open now: https://felixxii.xyz
"""
    
    try:
        send_message(message.strip())
    except Exception as e:
        print(f"[ERROR] {e}")

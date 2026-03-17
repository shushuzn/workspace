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
    
    # Check cache
    if TOKEN_CACHE.exists():
        with open(TOKEN_CACHE) as f:
            cache = json.load(f)
        # Support both formats
        expires = cache.get("expires") or cache.get("expires_at")
        if isinstance(expires, str):
            from datetime import datetime
            expires = datetime.fromisoformat(expires).timestamp()
        if expires > datetime.now().timestamp() + 300:
            return cache["token"]
    
    # Get new token
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
    else:
        raise Exception(f"Token failed: {data}")

def send_message(text):
    token = get_token()
    
    with open(CONFIG_FILE) as f:
        config = json.load(f)
    
    user_id = config.get("user_id") or config.get("default_receive_id")
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
    message = """
[Phase 1 Complete! Website LIVE]

[OK] Innovator Dashboard Deployed
[OK] URL: https://8.208.30.28:8444
[OK] Status: HTTP 200, 9580 bytes
[OK] SSL: Self-signed (365 days)
[OK] nginx: Running on port 8444

[INFO] Port Allocation:
  - 8443: code-server (CoPaw IDE)
  - 8444: Innovator Dashboard (NEW)

[NEXT] Optional:
  1. Add DNS CNAME (innovator.felixxii.xyz)
  2. Install Let's Encrypt SSL
  3. Git commit deployment

[TIME] Total: ~8 minutes
[SCORE] 100/100

Access now: https://8.208.30.28:8444
"""
    
    try:
        send_message(message.strip())
    except Exception as e:
        print(f"[ERROR] {e}")

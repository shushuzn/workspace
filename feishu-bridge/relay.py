"""
Telegram ↔ Feishu Message Relay
Polls both conversation logs and cross-posts new messages to the other platform.

Usage:
    python relay.py                    # relay all chats once
    python relay.py --watch           # poll every 30s
    python relay.py --chat <chat_id>   # relay specific chat only
    python relay.py --dry-run          # show what would be sent without sending
"""
import argparse
import json
import sys
import time
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("D:/OpenClaw/workspace")
CONV_DIR = WORKSPACE / "feishu-bridge" / "conversations"
STATE_FILE = WORKSPACE / "feishu-bridge" / "relay_state.json"
LOG_FILE = WORKSPACE / "feishu-bridge" / "relay.log"


def log(msg):
    ts = datetime.now().isoformat(timespec="seconds")
    line = f"{ts} {msg}"
    print(line)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {}


def save_state(state):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")


def get_history(chat_id: str) -> list:
    f = CONV_DIR / f"{chat_id}.json"
    if not f.exists():
        return []
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return []


def last_ts(msgs: list) -> str:
    if not msgs:
        return "1970-01-01T00:00:00"
    return max(m.get("timestamp", "1970-01-01T00:00:00") for m in msgs)


def relay_message(text: str, from_platform: str, to_platform: str, chat_id: str, dry_run: bool = False):
    prefix = f"[{from_platform}→{to_platform}] {chat_id}: "
    if dry_run:
        log(f"{prefix}[DRY RUN] {text[:80]}")
        return
    if to_platform == "feishu":
        _send_feishu(chat_id, text)
    else:
        _send_telegram(chat_id, text)


def _send_feishu(chat_id: str, text: str):
    # Uses lark-oapi if available, otherwise POST to feishu webhook
    try:
        from lark_oapi.adapter.向 import send
        # Imported dynamically to avoid hard dep
    except ImportError:
        pass
    # Fallback: use feishu webhook if configured
    webhook = "https://open.feishu.cn/open-apis/bot/v2/hook/REPLACE_ME"
    if "REPLACE_ME" in webhook:
        log(f"[feishu] No webhook configured for {chat_id}, skipping")
        return
    payload = json.dumps({"msg_type": "text", "content": {"text": text}}).encode()
    req = __import__("urllib.request").request.Request(
        webhook, data=payload,
        headers={"Content-Type": "application/json"},
    )
    with __import__("urllib.request").request.urlopen(req, timeout=10) as r:
        if r.status != 200:
            log(f"[feishu] Failed to send to {chat_id}: {r.status}")


def _send_telegram(chat_id: str, text: str):
    import urllib.request
    import urllib.error
    token = "8795362409:AAFO7a3nIYnkLcLeAoLN0DqkTv0aFcHiDhc"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = json.dumps({"chat_id": chat_id, "text": text}).encode()
    req = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            if r.status != 200:
                log(f"[telegram] Failed to send to {chat_id}: {r.status}")
    except Exception as e:
        log(f"[telegram] Error sending to {chat_id}: {e}")


def relay_chat(chat_id: str, state: dict, dry_run: bool = False):
    tg_msgs = get_history(f"tg_{chat_id}")
    fs_msgs = get_history(f"fs_{chat_id}")

    # relay Telegram → Feishu
    last_tg = state.get(f"tg_{chat_id}", "1970-01-01T00:00:00")
    for msg in tg_msgs:
        ts = msg.get("timestamp", "")
        if ts > last_tg and msg.get("role") == "user":
            relay_message(msg.get("content", "")[:2000], "Telegram", "Feishu", chat_id, dry_run)
        if ts > last_tg:
            last_tg = ts

    # relay Feishu → Telegram
    last_fs = state.get(f"fs_{chat_id}", "1970-01-01T00:00:00")
    for msg in fs_msgs:
        ts = msg.get("timestamp", "")
        if ts > last_fs and msg.get("role") == "user":
            relay_message(msg.get("content", "")[:2000], "Feishu", "Telegram", chat_id, dry_run)
        if ts > last_fs:
            last_fs = ts

    state[f"tg_{chat_id}"] = last_tg
    state[f"fs_{chat_id}"] = last_fs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--watch", action="store_true", help="Poll every 30 seconds")
    ap.add_argument("--chat", help="Relay specific chat_id only")
    ap.add_argument("--dry-run", action="store_true", help="Show what would be relayed")
    args = ap.parse_args()

    state = load_state()

    def tick():
        # Find all unique chat_ids from both platforms
        chat_ids = set()
        for f in CONV_DIR.glob("tg_*.json"):
            chat_ids.add(f.stem[3:])  # strip "tg_" prefix
        for f in CONV_DIR.glob("fs_*.json"):
            chat_ids.add(f.stem[3:])  # strip "fs_" prefix

        chats = [args.chat] if args.chat else sorted(chat_ids)
        for chat_id in chats:
            relay_chat(chat_id, state, args.dry_run)
        save_state(state)
        log(f"[relay] Tick done: {len(chats)} chats")

    tick()
    if args.watch:
        log("[relay] Watching every 30s...")
        while True:
            time.sleep(30)
            tick()


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Alert Bot — monitors agent logs and sends Feishu card notifications on errors.

Usage:
    python alert-bot.py                    # one-shot check
    python alert-bot.py --watch           # poll every 60s
    python alert-bot.py --watch --interval 30
    python alert-bot.py --webhook         # start webhook receiver on port 8099
    python alert-bot.py --watch --webhook  # both watch + webhook server

Requires feishu_webhook.py in the same directory (provides get_token, send_reply).
"""
import argparse
import json
import re
import sys
import time
import threading
from datetime import datetime
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

WORKSPACE = Path(__file__).parent
BRIDGE_LOG = WORKSPACE / "bridge.log"
TELEGRAM_LOG = WORKSPACE / "telegram.log"
ALERT_LOG = WORKSPACE / "alerts.log"
STATE_FILE = WORKSPACE / "alert_state.json"
WEBHOOK_PORT = 8099

# ── Billing / Metering ─────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"last_errors": {}, "last_webhook_alerts": {}, "trigger_count": 0}


def save_state(state: dict, increment_triggers: int = 0):
    if increment_triggers > 0:
        state["trigger_count"] = state.get("trigger_count", 0) + increment_triggers
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")

# ── Feishu card helpers ────────────────────────────────────────────────────────

def send_feishu_card(text: str, alert_type: str = "ERROR", project: str = "feishu-bridge"):
    """Send a rich Feishu card to the configured webhook."""
    try:
        webhook_url, chat_id = parse_feishu_webhook()
    except ValueError as e:
        print(f"[WARN] Feishu not configured: {e}")
        return

    token = get_token()
    card = {
        "msg_type": "interactive",
        "card": {
            "header": {
                "title": {"tag": "plain_text", "content": f"\u26a0\ufe0f {project.upper()} Alert — {alert_type}"},
                "template": "red" if alert_type == "ERROR" else "orange"
            },
            "elements": [
                {"tag": "div", "text": {"tag": "lark_md", "content": text}},
                {"tag": "hr"},
                {"tag": "note", "elements": [
                    {"tag": "plain_text", "content": f"\u23f0 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} · feishu-bridge"}
                ]}
            ]
        }
    }
    payload = json.dumps({"receive_id": chat_id, "msg_type": "interactive", "content": json.dumps(card, ensure_ascii=False)}).encode()
    req = urllib.request.Request(
        "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id",
        data=payload,
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            if result.get("code") != 0:
                print(f"[ERROR] Feishu send failed: {result}")
            else:
                print(f"[OK] Feishu alert sent")
    except Exception as e:
        print(f"[ERROR] Feishu request failed: {e}")


def get_token():
    from feishu_webhook import get_token as _gt
    return _gt()


def parse_feishu_webhook():
    cfg = WORKSPACE / "alert_config.json"
    if cfg.exists():
        data = json.loads(cfg.read_text(encoding="utf-8"))
        webhook = data.get("feishu_webhook_url", "")
        chat_id = data.get("feishu_chat_id", "")
    else:
        webhook = ""
        chat_id = ""
    if not webhook:
        raise ValueError("feishu_webhook_url not set in alert_config.json")
    return webhook, chat_id


# ── Log parsing ────────────────────────────────────────────────────────────────

ERROR_PATTERNS = [
    re.compile(r"\[ERROR\]", re.IGNORECASE),
    re.compile(r"\[CRITICAL\]", re.IGNORECASE),
    re.compile(r"Traceback \(most recent call last\)"),
    re.compile(r"Failed to|failed to", re.IGNORECASE),
    re.compile(r"Error:|Exception:", re.IGNORECASE),
    re.compile(r"EXIT CODE [1-9]|exit code [1-9]", re.IGNORECASE),
]


def tail_lines(path: Path, n: int = 50) -> list[str]:
    if not path.exists():
        return []
    lines = path.read_text(encoding="utf-8", errors="ignore").splitlines()
    return lines[-n:]


def extract_errors(lines: list[str]) -> list[str]:
    errors = []
    for line in lines:
        for pat in ERROR_PATTERNS:
            if pat.search(line):
                errors.append(line.strip())
                break
    return errors


# ── Alert state (dedup) ───────────────────────────────────────────────────────

def is_new(error: str, state: dict, log_name: str) -> bool:
    key = f"{log_name}:{error[-100:]}"
    return key not in state.get("last_errors", {})


def mark_seen(error: str, state: dict, log_name: str):
    key = f"{log_name}:{error[-100:]}"
    d = state.setdefault("last_errors", {})
    d[key] = datetime.now().isoformat()


def is_new_webhook(alert_id: str, state: dict) -> bool:
    """Dedup webhook alerts by alert_id within a 5-minute window."""
    if not alert_id:
        return True
    last_seen = state.get("last_webhook_alerts", {}).get(alert_id, "")
    if last_seen:
        try:
            last_time = datetime.fromisoformat(last_seen)
            if (datetime.now() - last_time).total_seconds() < 300:
                return False
        except ValueError:
            pass
    return True


def mark_webhook_seen(alert_id: str, state: dict):
    if alert_id:
        state.setdefault("last_webhook_alerts", {})[alert_id] = datetime.now().isoformat()


# ── Alert log ────────────────────────────────────────────────────────────────

def log_alert(msg: str):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"{ts} {msg}"
    print(line)
    ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(ALERT_LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")


# ── Core check ───────────────────────────────────────────────────────────────

def check_once() -> int:
    state = load_state()
    new_alerts = 0

    for log_path, log_name in [(BRIDGE_LOG, "bridge"), (TELEGRAM_LOG, "telegram")]:
        lines = tail_lines(log_path, n=100)
        errors = extract_errors(lines)
        for err in errors:
            if is_new(err, state, log_name):
                log_alert(f"[{log_name.upper()}] {err}")
                send_feishu_card(f"**[{log_name.upper()}]**\n\n```\n{err[:300]}\n```", "ERROR")
                mark_seen(err, state, log_name)
                new_alerts += 1

    save_state(state)
    return new_alerts


# ── Webhook receiver ─────────────────────────────────────────────────────────

# Supported project tags and their routing metadata
PROJECT_TAGS = {
    "material-price-tracker": {"label": "\u5395\u6599\u4ef7\u683c", "color": "blue"},
    "crucix": {"label": "Crucix OSINT", "color": "purple"},
    "stock-analysis-agent": {"label": "\u80a1\u7968\u5206\u6790", "color": "green"},
}


class WebhookHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[webhook] {args[0]}")

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok", "service": "feishu-bridge-aggregator"}).encode())
            return
        if self.path == "/billing":
            state = load_state()
            count = state.get("trigger_count", 0)
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({
                "trigger_count": count,
                "plan": "pay_per_trigger",
                "price_per_trigger": 0.01,
                "estimated_cost_usd": round(count * 0.01, 4),
            }).encode())
            return
        self.send_response(404)
        self.end_headers()
        self.wfile.write(b"Not found")

    def do_POST(self):
        if self.path != "/webhook":
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not found")
            return

        try:
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length).decode("utf-8", errors="ignore")
            payload = json.loads(body)
        except (ValueError, json.JSONDecodeError) as e:
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": "invalid json"}).encode())
            return

        project = payload.get("source", "unknown")
        alerts = payload.get("alerts", [])
        timestamp = payload.get("timestamp", datetime.now().isoformat())

        if not alerts:
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"received": True, "alerts_count": 0}).encode())
            return

        state = load_state()
        sent_count = 0

        for alert in alerts:
            alert_id = f"{project}:{alert.get('symbol', '')}:{alert.get('price', '')}:{timestamp}"
            if not is_new_webhook(alert_id, state):
                continue

            symbol = alert.get("symbol", "-")
            price = alert.get("price", "-")
            direction = alert.get("direction", "")
            tag_info = PROJECT_TAGS.get(project, {"label": project, "color": "grey"})

            lines = [
                f"\u2709 \u9879\u76ee: {tag_info['label']} (`{project}`)",
                f"  \u7b56\u7565: {symbol} @ {price} {direction}",
            ]
            if alert.get("message"):
                lines.append(f"  \u8bf0\u660e: {alert['message']}")

            text = "\n".join(lines)
            send_feishu_card(text, "ALERT", project)
            log_alert(f"[{project.upper()}] {symbol} {price} {direction}")
            mark_webhook_seen(alert_id, state)
            sent_count += 1

        save_state(state, sent_count)

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps({"received": True, "alerts_count": len(alerts), "sent": sent_count}).encode())


def run_webhook_server():
    server = HTTPServer(("0.0.0.0", WEBHOOK_PORT), WebhookHandler)
    print(f"[webhook] Aggregator listening on http://0.0.0.0:{WEBHOOK_PORT}/webhook")
    server.serve_forever()


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(description="Alert Bot — Feishu notifications for agent errors")
    ap.add_argument("--watch", action="store_true", help="Poll continuously")
    ap.add_argument("--interval", type=int, default=60, help="Poll interval in seconds (default: 60)")
    ap.add_argument("--webhook", action="store_true", help="Start webhook receiver on port 8099")
    args = ap.parse_args()

    print(f"Alert Bot starting \u2014 watching bridge.log + telegram.log")
    if args.watch:
        print(f"Poll interval: {args.interval}s")

    if args.webhook:
        t = threading.Thread(target=run_webhook_server, daemon=True)
        t.start()
        print(f"[webhook] Aggregator endpoint: POST http://localhost:{WEBHOOK_PORT}/webhook")

    count = check_once()
    print(f"Initial check: {count} new alerts")

    if args.watch:
        while True:
            time.sleep(args.interval)
            try:
                n = check_once()
                if n:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] {n} new alerts")
            except Exception as e:
                print(f"[ERROR] Check failed: {e}")
    elif not args.webhook:
        # One-shot mode — do nothing more
        pass
    else:
        # Webhook-only mode — keep alive
        while True:
            time.sleep(3600)


if __name__ == "__main__":
    import urllib.request
    main()

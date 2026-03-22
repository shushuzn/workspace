"""Webhook notifications for Stock PRO"""
import json
import urllib.request
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/OpenClaw/workspace")
WEBHOOK_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_webhooks.json"

class WebhookManager:
    def __init__(self):
        self.webhooks = {}
        self.load()
    
    def load(self):
        if WEBHOOK_FILE.exists():
            try:
                with open(WEBHOOK_FILE, 'r') as f:
                    self.webhooks = json.load(f)
            except:
                self.webhooks = {}
    
    def save(self):
        with open(WEBHOOK_FILE, 'w') as f:
            json.dump(self.webhooks, f, indent=2)
    
    def add(self, name, url, events=None):
        """Add webhook"""
        self.webhooks[name] = {
            "url": url,
            "events": events or ["alert"],
            "created": datetime.now().isoformat()
        }
        self.save()
        return f"[Webhook] Added '{name}' -> {url}"
    
    def remove(self, name):
        if name in self.webhooks:
            del self.webhooks[name]
            self.save()
            return f"[Webhook] Removed '{name}'"
        return f"[Webhook] '{name}' not found"
    
    def list_webhooks(self):
        if not self.webhooks:
            return "[Webhook] No webhooks configured. Add with: --webhook-add <name> <url>"
        
        lines = ["[Webhook] Configured Webhooks:", "-" * 50]
        for name, wh in self.webhooks.items():
            lines.append(f"  {name}: {wh['url']}")
            lines.append(f"    Events: {', '.join(wh['events'])}")
        return "\n".join(lines)
    
    def send(self, event, payload):
        """Send webhook notification"""
        results = []
        for name, wh in self.webhooks.items():
            if event in wh["events"] or "all" in wh["events"]:
                try:
                    req = urllib.request.Request(
                        wh["url"],
                        data=json.dumps(payload).encode('utf-8'),
                        headers={'Content-Type': 'application/json'}
                    )
                    with urllib.request.urlopen(req, timeout=10) as resp:
                        results.append(f"[Webhook] {name}: OK ({resp.status})")
                except Exception as e:
                    results.append(f"[Webhook] {name}: FAILED ({e})")
        return "\n".join(results) if results else "[Webhook] No matching webhooks"
    
    def notify_alert(self, results, threshold=30):
        """Send alert notification"""
        alerts = [r for r in results if r['upside'] > threshold]
        if alerts:
            payload = {
                "event": "alert",
                "timestamp": datetime.now().isoformat(),
                "alerts": [{
                    "symbol": r["symbol"],
                    "price": r["price"],
                    "target": r["target"],
                    "upside": r["upside"],
                    "score": r["score"]
                } for r in alerts]
            }
            return self.send("alert", payload)
        return None
    
    def notify_report(self, symbol, data):
        """Send report notification"""
        payload = {
            "event": "report",
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "score": data["score"],
            "rating": data["rating"],
            "upside": data["upside"]
        }
        return self.send("report", payload)

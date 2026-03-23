"""Alert management for Stock PRO"""
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path("D:/OpenClaw/workspace")
ALERTS_FILE = WORKSPACE / "30-scripts-tools" / "stock_pro_alerts.json"


class AlertManager:
    def __init__(self):
        self.alerts = {}
        self.load()

    def load(self):
        """Load alerts from file"""
        if ALERTS_FILE.exists():
            try:
                with open(ALERTS_FILE, 'r') as f:
                    self.alerts = json.load(f)
            except:
                self.alerts = {}
        else:
            self.alerts = {}

    def save(self):
        """Save alerts to file"""
        with open(ALERTS_FILE, 'w') as f:
            json.dump(self.alerts, f, indent=2)

    def add(self, symbol, alert_type, threshold, condition="above"):
        """Add an alert"""
        sym = symbol.upper()
        if sym not in self.alerts:
            self.alerts[sym] = []

        alert = {
            "type": alert_type,  # price, score, upside, peg, pe
            "threshold": threshold,
            "condition": condition,  # above, below
            "created": datetime.now().isoformat(),
            "triggered": None
        }

        self.alerts[sym].append(alert)
        self.save()
        return f"[Alert] Added {alert_type} {condition} {threshold} for {sym}"

    def remove(self, symbol, index=None):
        """Remove an alert"""
        sym = symbol.upper()
        if sym in self.alerts:
            if index is not None and index < len(self.alerts[sym]):
                removed = self.alerts[sym].pop(index)
                self.save()
                return f"[Alert] Removed {removed['type']} alert for {sym}"
            elif index is None:
                del self.alerts[sym]
                self.save()
                return f"[Alert] Removed all alerts for {sym}"
        return f"[Alert] No alerts for {sym}"

    def check(self, symbol, current_value):
        """Check if alert is triggered"""
        sym = symbol.upper()
        if sym not in self.alerts:
            return []

        triggered = []
        for i, alert in enumerate(self.alerts[sym]):
            should_trigger = False

            if alert["condition"] == "above":
                should_trigger = current_value > alert["threshold"]
            else:
                should_trigger = current_value < alert["threshold"]

            if should_trigger:
                triggered.append((i, alert))
                alert["triggered"] = datetime.now().isoformat()

        if triggered:
            self.save()

        return triggered

    def check_all(self, results):
        """Check all alerts against results"""
        triggered_alerts = []

        for r in results:
            sym = r["symbol"]

            # Check price alert
            if "price" in [a["type"] for a in self.alerts.get(sym, [])]:
                price_alerts = [a for a in self.alerts.get(sym, []) if a["type"] == "price"]
                for alert in price_alerts:
                    triggered = self.check_alert(alert, r["price"])
                    if triggered:
                        triggered_alerts.append({
                            "symbol": sym,
                            "type": "price",
                            "message": f"Price ${r['price']:.2f} {alert['condition']} ${alert['threshold']:.2f}"
                        })

            # Check score alert
            if "score" in [a["type"] for a in self.alerts.get(sym, [])]:
                score_alerts = [a for a in self.alerts.get(sym, []) if a["type"] == "score"]
                for alert in score_alerts:
                    triggered = self.check_alert(alert, r["score"])
                    if triggered:
                        triggered_alerts.append({
                            "symbol": sym,
                            "type": "score",
                            "message": f"Score {r['score']} {alert['condition']} {alert['threshold']}"
                        })

        return triggered_alerts

    def check_alert(self, alert, current_value):
        """Check single alert"""
        if alert["condition"] == "above":
            return current_value > alert["threshold"]
        else:
            return current_value < alert["threshold"]

    def list_all(self):
        """List all alerts"""
        if not self.alerts:
            return "[Alerts] No alerts configured"

        report = "# Active Alerts\n\n"
        for sym, alerts in sorted(self.alerts.items()):
            report += f"## {sym}\n"
            for i, alert in enumerate(alerts):
                triggered = " [TRIGGERED]" if alert.get("triggered") else ""
                report += f"- [{i}] {alert['type']} {alert['condition']} {alert['threshold']}{triggered}\n"
        return report


# Global instance
_alert_manager = AlertManager()


def add_alert(symbol, alert_type, threshold, condition="above"):
    """Add an alert"""
    return _alert_manager.add(symbol, alert_type, threshold, condition)


def remove_alert(symbol, index=None):
    """Remove an alert"""
    return _alert_manager.remove(symbol, index)


def check_alerts(results):
    """Check all alerts"""
    return _alert_manager.check_all(results)


def list_alerts():
    """List all alerts"""
    return _alert_manager.list_all()

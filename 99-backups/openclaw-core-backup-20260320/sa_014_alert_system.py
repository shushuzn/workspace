#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-014: Alert System
Real-time price and indicator alerts
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import time

class AlertSystem:
    """Real-time alert system for stocks"""

    def __init__(self, data_dir: str = "60-DATA/stock_alerts"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.alerts_file = self.data_dir / "alerts_log.json"
        self.config_file = self.data_dir / "alert_config.json"

        self.alerts = self._load_alerts()
        self.config = self._load_config()

    def _load_alerts(self) -> Dict:
        """Load alerts log"""
        if self.alerts_file.exists():
            with open(self.alerts_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "version": "1.0",
            "alerts": [],
            "stats": {
                "total_alerts": 0,
                "price_alerts": 0,
                "indicator_alerts": 0,
                "pattern_alerts": 0
            }
        }

    def _save_alerts(self):
        """Save alerts log"""
        with open(self.alerts_file, 'w', encoding='utf-8') as f:
            json.dump(self.alerts, f, ensure_ascii=False, indent=2)

    def _load_config(self) -> Dict:
        """Load alert configuration"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "version": "1.0",
            "alert_rules": [],
            "notification_methods": ["console"],
            "created_at": datetime.now().isoformat()
        }

    def _save_config(self):
        """Save alert configuration"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def create_price_alert(self, symbol: str, alert_type: str,
                          threshold: float, current_price: float,
                          expires_at: Optional[str] = None) -> Dict:
        """
        Create a price alert
        
        Args:
            symbol: Stock symbol
            alert_type: "above" or "below"
            threshold: Price threshold
            current_price: Current price
            expires_at: Expiration time (ISO format)
            
        Returns:
            Dict with alert details
        """
        alert = {
            "alert_id": f"price_{symbol}_{len(self.alerts['alerts']) + 1}",
            "type": "price",
            "symbol": symbol,
            "alert_type": alert_type,
            "threshold": round(threshold, 2),
            "current_price": round(current_price, 2),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "expires_at": expires_at,
            "triggered_at": None,
            "triggered_price": None
        }

        self.config["alert_rules"].append(alert)
        self._save_config()

        return alert

    def create_indicator_alert(self, symbol: str, indicator: str,
                              condition: str, value: float,
                              current_value: float) -> Dict:
        """
        Create an indicator alert
        
        Args:
            symbol: Stock symbol
            indicator: Indicator name (RSI, MACD, etc.)
            condition: Condition ("cross_above", "cross_below", "above", "below")
            value: Threshold value
            current_value: Current indicator value
            
        Returns:
            Dict with alert details
        """
        alert = {
            "alert_id": f"indicator_{symbol}_{indicator}_{len(self.config['alert_rules']) + 1}",
            "type": "indicator",
            "symbol": symbol,
            "indicator": indicator,
            "condition": condition,
            "threshold": round(value, 4),
            "current_value": round(current_value, 4),
            "status": "active",
            "created_at": datetime.now().isoformat(),
            "triggered_at": None,
            "triggered_value": None
        }

        self.config["alert_rules"].append(alert)
        self._save_config()

        return alert

    def create_pattern_alert(self, symbol: str, pattern_name: str,
                            detected: bool = False) -> Dict:
        """
        Create a pattern detection alert
        
        Args:
            symbol: Stock symbol
            pattern_name: Pattern name
            detected: Whether pattern is already detected
            
        Returns:
            Dict with alert details
        """
        alert = {
            "alert_id": f"pattern_{symbol}_{pattern_name}_{len(self.config['alert_rules']) + 1}",
            "type": "pattern",
            "symbol": symbol,
            "pattern_name": pattern_name,
            "status": "triggered" if detected else "active",
            "created_at": datetime.now().isoformat(),
            "triggered_at": datetime.now().isoformat() if detected else None
        }

        self.config["alert_rules"].append(alert)
        self._save_config()

        if detected:
            self._log_alert(alert)

        return alert

    def check_alerts(self, symbol: str, current_price: float,
                    indicators: Optional[Dict] = None) -> List[Dict]:
        """
        Check and trigger alerts
        
        Args:
            symbol: Stock symbol
            current_price: Current price
            indicators: Current indicator values
            
        Returns:
            List of triggered alerts
        """
        triggered = []

        for alert in self.config["alert_rules"]:
            if alert["status"] != "active":
                continue

            if alert["symbol"] != symbol:
                continue

            # Check expiration
            if alert.get("expires_at"):
                if datetime.fromisoformat(alert["expires_at"]) < datetime.now():
                    alert["status"] = "expired"
                    continue

            # Check price alerts
            if alert["type"] == "price":
                if alert["alert_type"] == "above" and current_price >= alert["threshold"]:
                    alert["status"] = "triggered"
                    alert["triggered_at"] = datetime.now().isoformat()
                    alert["triggered_price"] = round(current_price, 2)
                    triggered.append(alert)
                    self._log_alert(alert)

                elif alert["alert_type"] == "below" and current_price <= alert["threshold"]:
                    alert["status"] = "triggered"
                    alert["triggered_at"] = datetime.now().isoformat()
                    alert["triggered_price"] = round(current_price, 2)
                    triggered.append(alert)
                    self._log_alert(alert)

            # Check indicator alerts
            elif alert["type"] == "indicator" and indicators:
                indicator_name = alert["indicator"]
                current_value = indicators.get(indicator_name, 0)

                condition = alert["condition"]
                threshold = alert["threshold"]

                if condition == "above" and current_value > threshold:
                    alert["status"] = "triggered"
                    alert["triggered_at"] = datetime.now().isoformat()
                    alert["triggered_value"] = round(current_value, 4)
                    triggered.append(alert)
                    self._log_alert(alert)

                elif condition == "below" and current_value < threshold:
                    alert["status"] = "triggered"
                    alert["triggered_at"] = datetime.now().isoformat()
                    alert["triggered_value"] = round(current_value, 4)
                    triggered.append(alert)
                    self._log_alert(alert)

        # Save updated config
        self._save_config()

        return triggered

    def _log_alert(self, alert: Dict):
        """Log triggered alert"""
        log_entry = {
            "alert_id": alert["alert_id"],
            "type": alert["type"],
            "symbol": alert["symbol"],
            "triggered_at": alert["triggered_at"],
            "details": alert
        }

        self.alerts["alerts"].append(log_entry)
        self.alerts["stats"]["total_alerts"] += 1

        if alert["type"] == "price":
            self.alerts["stats"]["price_alerts"] += 1
        elif alert["type"] == "indicator":
            self.alerts["stats"]["indicator_alerts"] += 1
        elif alert["type"] == "pattern":
            self.alerts["stats"]["pattern_alerts"] += 1

        # Keep only last 500 alerts
        self.alerts["alerts"] = self.alerts["alerts"][-500:]

        self._save_alerts()

    def get_active_alerts(self, symbol: Optional[str] = None) -> List[Dict]:
        """Get active alerts"""
        active = []

        for alert in self.config["alert_rules"]:
            if alert["status"] != "active":
                continue

            if symbol and alert["symbol"] != symbol:
                continue

            active.append(alert)

        return active

    def delete_alert(self, alert_id: str) -> bool:
        """Delete an alert"""
        for i, alert in enumerate(self.config["alert_rules"]):
            if alert["alert_id"] == alert_id:
                self.config["alert_rules"].pop(i)
                self._save_config()
                return True

        return False

    def clear_expired_alerts(self) -> int:
        """Clear expired alerts"""
        count = 0

        for alert in self.config["alert_rules"]:
            if alert.get("expires_at"):
                if datetime.fromisoformat(alert["expires_at"]) < datetime.now():
                    alert["status"] = "expired"
                    count += 1

        self._save_config()
        return count

    def get_stats(self) -> Dict:
        """Get alert statistics"""
        return self.alerts["stats"].copy()

    def display_status(self) -> str:
        """Display system status"""
        stats = self.get_stats()
        active_count = len(self.get_active_alerts())

        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 16 + "Alert System Status")
        output.append("=" * 70)

        output.append(f"\n[Alert Types]")
        output.append("  - Price Alerts (above/below threshold)")
        output.append("  - Indicator Alerts (RSI, MACD, etc.)")
        output.append("  - Pattern Alerts (detection notifications)")

        output.append(f"\n[Statistics]")
        output.append(f"  Total Alerts:      {stats['total_alerts']}")
        output.append(f"  Price Alerts:      {stats['price_alerts']}")
        output.append(f"  Indicator Alerts:  {stats['indicator_alerts']}")
        output.append(f"  Pattern Alerts:    {stats['pattern_alerts']}")
        output.append(f"  Active Alerts:     {active_count}")

        output.append("\n" + "=" * 70 + "\n")

        return "\n".join(output)


def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 16 + "SA-014: Alert System")
    print("=" * 70)

    system = AlertSystem()

    # Test 1: Display status
    print(system.display_status())

    # Test 2: Create alerts
    print("\n[Test 1] Create Alerts")
    print("-" * 70)

    # Price alert
    price_alert = system.create_price_alert(
        symbol="TEST",
        alert_type="above",
        threshold=105.0,
        current_price=103.5,
        expires_at="2026-12-31T23:59:59"
    )
    print(f"  Created Price Alert:")
    print(f"    ID:       {price_alert['alert_id']}")
    print(f"    Symbol:   {price_alert['symbol']}")
    print(f"    Type:     {price_alert['alert_type']} ${price_alert['threshold']}")
    print(f"    Status:   {price_alert['status']}")

    # Indicator alert
    indicator_alert = system.create_indicator_alert(
        symbol="TEST",
        indicator="RSI",
        condition="below",
        value=30.0,
        current_value=35.0
    )
    print(f"\n  Created Indicator Alert:")
    print(f"    ID:       {indicator_alert['alert_id']}")
    print(f"    Symbol:   {indicator_alert['symbol']}")
    print(f"    Indicator: {indicator_alert['indicator']} {indicator_alert['condition']} {indicator_alert['threshold']}")
    print(f"    Status:   {indicator_alert['status']}")

    # Pattern alert
    pattern_alert = system.create_pattern_alert(
        symbol="TEST",
        pattern_name="double_bottom",
        detected=False
    )
    print(f"\n  Created Pattern Alert:")
    print(f"    ID:       {pattern_alert['alert_id']}")
    print(f"    Symbol:   {pattern_alert['symbol']}")
    print(f"    Pattern:  {pattern_alert['pattern_name']}")
    print(f"    Status:   {pattern_alert['status']}")

    # Test 3: Check alerts
    print("\n[Test 2] Check Alerts (Price Triggered)")
    print("-" * 70)

    triggered = system.check_alerts("TEST", current_price=106.0, indicators={"RSI": 28.0})

    if triggered:
        print(f"  Triggered {len(triggered)} alert(s):")
        for alert in triggered:
            print(f"\n    [{alert['type'].upper()}] {alert['symbol']}")
            if alert["type"] == "price":
                print(f"      Price ${alert['triggered_price']} crossed {alert['alert_type']} ${alert['threshold']}")
            elif alert["type"] == "indicator":
                print(f"      {alert['indicator']} {alert['triggered_value']} crossed {alert['condition']} {alert['threshold']}")
            print(f"      Time: {alert['triggered_at']}")
    else:
        print("  No alerts triggered")

    # Test 4: Active alerts
    print("\n[Test 3] Active Alerts")
    print("-" * 70)
    active = system.get_active_alerts()
    print(f"  Active alerts: {len(active)}")
    for alert in active:
        print(f"    - {alert['alert_id']}: {alert['symbol']} ({alert['status']})")

    # Test 5: Final stats
    print("\n[Test 4] Final Statistics")
    print("-" * 70)
    stats = system.get_stats()
    print(f"  Total Alerts:      {stats['total_alerts']}")
    print(f"  Price Alerts:      {stats['price_alerts']}")
    print(f"  Indicator Alerts:  {stats['indicator_alerts']}")
    print(f"  Pattern Alerts:    {stats['pattern_alerts']}")

    print("\n[OK] SA-014 Alert System test completed")

if __name__ == "__main__":
    main()

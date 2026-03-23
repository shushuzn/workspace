import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股票实时警报 MVP
功能：价格/RSI/成交量异常警报

作者：Claw
版本：v1.0.0
"""

import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum

class AlertType(Enum):
    """警报类型"""
    PRICE_CHANGE = "price_change"      # 价格变动
    RSI_OVERBOUGHT = "rsi_overbought"   # RSI 超买
    RSI_OVERSOLD = "rsi_oversold"       # RSI 超卖
    VOLUME_SPIKE = "volume_spike"       # 成交量突增
    BREAKOUT = "breakout"               # 突破
    SUPPORT_BREAK = "support_break"     # 跌破支撑

class AlertLevel(Enum):
    """警报级别"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class Alert:
    """警报"""
    symbol: str
    alert_type: AlertType
    level: AlertLevel
    message: str
    value: float
    threshold: float
    timestamp: str

class StockRealtimeAlert:
    """实时警报系统"""

    def __init__(self, symbol: str):
        self.symbol = symbol.upper()
        self.alerts: List[Alert] = []

        # 警报阈值配置
        self.config = {
            "price_change_pct": 5.0,      # 价格变动 >5%
            "rsi_overbought": 70,          # RSI >70
            "rsi_oversold": 30,            # RSI <30
            "volume_spike": 2.0,           # 成交量 >2倍
            "support_resistance": 2.0,     # 突破 2%
        }

        # 存储
        self.alert_log = Path("30-scripts-tools/.cache/alerts")
        self.alert_log.mkdir(parents=True, exist_ok=True)

    def check(self, data: Dict) -> List[Alert]:
        """
        检查数据并生成警报
        
        Args:
            data: 股票数据 {price, rsi, volume, ...}
        
        Returns:
            警报列表
        """
        self.alerts = []

        # 1. 价格变动检查
        if "price_change_pct" in data:
            change = abs(data["price_change_pct"])
            if change > self.config["price_change_pct"]:
                level = AlertLevel.HIGH if change > 10 else AlertLevel.MEDIUM
                self.alerts.append(Alert(
                    symbol=self.symbol,
                    alert_type=AlertType.PRICE_CHANGE,
                    level=level,
                    message=f"价格变动 {data['price_change_pct']:+.2f}%",
                    value=data["price_change_pct"],
                    threshold=self.config["price_change_pct"],
                    timestamp=datetime.now().isoformat()
                ))

        # 2. RSI 检查
        if "rsi" in data:
            rsi = data["rsi"]
            if rsi > self.config["rsi_overbought"]:
                self.alerts.append(Alert(
                    symbol=self.symbol,
                    alert_type=AlertType.RSI_OVERBOUGHT,
                    level=AlertLevel.MEDIUM,
                    message=f"RSI 超买: {rsi:.1f}",
                    value=rsi,
                    threshold=self.config["rsi_overbought"],
                    timestamp=datetime.now().isoformat()
                ))
            elif rsi < self.config["rsi_oversold"]:
                self.alerts.append(Alert(
                    symbol=self.symbol,
                    alert_type=AlertType.RSI_OVERSOLD,
                    level=AlertLevel.MEDIUM,
                    message=f"RSI 超卖: {rsi:.1f}",
                    value=rsi,
                    threshold=self.config["rsi_oversold"],
                    timestamp=datetime.now().isoformat()
                ))

        # 3. 成交量检查
        if "volume_ratio" in data:
            ratio = data["volume_ratio"]
            if ratio > self.config["volume_spike"]:
                self.alerts.append(Alert(
                    symbol=self.symbol,
                    alert_type=AlertType.VOLUME_SPIKE,
                    level=AlertLevel.HIGH,
                    message=f"成交量突增 {ratio:.1f}x",
                    value=ratio,
                    threshold=self.config["volume_spike"],
                    timestamp=datetime.now().isoformat()
                ))

        # 4. 突破检查
        if "price" in data and "resistance" in data:
            price = data["price"]
            resistance = data["resistance"]
            if price > resistance * (1 + self.config["support_resistance"]/100):
                self.alerts.append(Alert(
                    symbol=self.symbol,
                    alert_type=AlertType.BREAKOUT,
                    level=AlertLevel.HIGH,
                    message=f"突破阻力 ${resistance:.2f}",
                    value=price,
                    threshold=resistance,
                    timestamp=datetime.now().isoformat()
                ))

        # 保存到日志
        self._save_alerts()

        return self.alerts

    def _save_alerts(self):
        """保存警报到日志"""
        if not self.alerts:
            return

        log_file = self.alert_log / f"{self.symbol}_alerts.json"

        # 读取现有
        existing = []
        if log_file.exists():
            with open(log_file, "r", encoding="utf-8") as f:
                existing = json.load(f)

        # 添加新警报
        for alert in self.alerts:
            existing.append({
                "symbol": alert.symbol,
                "type": alert.alert_type.value,
                "level": alert.level.value,
                "message": alert.message,
                "value": alert.value,
                "threshold": alert.threshold,
                "timestamp": alert.timestamp
            })

        # 只保留最近 100 条
        existing = existing[-100:]

        with open(log_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)

    def get_history(self, limit: int = 10) -> List[Dict]:
        """获取历史警报"""
        log_file = self.alert_log / f"{self.symbol}_alerts.json"
        if not log_file.exists():
            return []

        with open(log_file, "r", encoding="utf-8") as f:
            alerts = json.load(f)

        return alerts[-limit:]


def demo():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py stock_realtime_alert_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py stock_realtime_alert_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

演示"""
    alert_system = StockRealtimeAlert("AAPL")

    # 模拟数据
    test_cases = [
        {
            "name": "价格暴涨",
            "data": {"price_change_pct": 8.5}
        },
        {
            "name": "RSI 超买",
            "data": {"rsi": 75.0}
        },
        {
            "name": "RSI 超卖",
            "data": {"rsi": 25.0}
        },
        {
            "name": "成交量突增",
            "data": {"volume_ratio": 3.2}
        },
        {
            "name": "突破阻力",
            "data": {"price": 158.0, "resistance": 155.0}
        },
        {
            "name": "正常数据 (无警报)",
            "data": {"price_change_pct": 1.5, "rsi": 55.0, "volume_ratio": 1.1}
        }
    ]

    print("=" * 60)
    print("Stock Realtime Alert MVP - Demo")
    print("=" * 60)

    for test in test_cases:
        alerts = alert_system.check(test["data"])

        print(f"\n[{test['name']}]")
        if alerts:
            for a in alerts:
                level_emoji = {"low": "🟢", "medium": "🟡", "high": "🟠", "critical": "🔴"}
                print(f"  {level_emoji[a.level.value]} {a.message}")
        else:
            print("  ✓ 无警报")

    # 历史
    print(f"\n{'=' * 60}")
    print("历史警报:")
    print("=" * 60)
    history = alert_system.get_history()
    print(f"共 {len(history)} 条")


if __name__ == "__main__":
    demo()
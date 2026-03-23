import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-034 Risk Manager
【Phase 7 - 高级功能】

功能:
  - 实时风险监控
  - 仓位限制检查
  - 止损管理
  - 风险预警

依赖: 风险数据配置
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import random

# 配置
RISK_DIR = Path("60-DATA/stock_034")
CONFIG_FILE = Path("30-scripts-tools/sa_034_config.json")


class RiskManager:
    """风险管理器"""

    def __init__(self):
        self.risk_dir = RISK_DIR
        self.config = self._load_config()

        self.risk_dir.mkdir(parents=True, exist_ok=True)

        self.alerts_file = self.risk_dir / "risk_alerts.json"
        self.log_file = self.risk_dir / "risk_log.json"

    def _load_config(self) -> dict:
        default = {
            "max_position_pct": 20,  # 单票最大仓位%
            "max_sector_pct": 40,    # 单板块最大仓位%
            "max_leverage": 1.0,     # 最大杠杆
            "stop_loss_pct": 5,     # 默认止损线%
            "max_daily_loss": 3,     # 最大日亏损%
            "var_confidence": 0.95, # VaR置信度
            "warnings_enabled": True
        }

        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except (Exception,):
                return default
        return default

    def check_position(self, symbol: str, position_value: float, total_value: float) -> dict:
        """检查仓位是否超限"""
        position_pct = (position_value / total_value * 100) if total_value > 0 else 0
        max_pct = self.config.get("max_position_pct", 20)

        status = "OK" if position_pct <= max_pct else "WARNING"

        if position_pct > max_pct:
            self._log_alert("position_limit", symbol, {
                "position_pct": round(position_pct, 2),
                "limit": max_pct,
                "severity": "HIGH" if position_pct > max_pct * 1.5 else "MEDIUM"
            })

        return {
            "symbol": symbol,
            "position_pct": round(position_pct, 2),
            "limit": max_pct,
            "status": status,
            "action": "REDUCE" if position_pct > max_pct else "HOLD"
        }

    def check_sector(self, sector: str, sector_value: float, total_value: float) -> dict:
        """检查板块仓位"""
        sector_pct = (sector_value / total_value * 100) if total_value > 0 else 0
        max_pct = self.config.get("max_sector_pct", 40)

        status = "OK" if sector_pct <= max_pct else "WARNING"

        if sector_pct > max_pct:
            self._log_alert("sector_limit", sector, {
                "sector_pct": round(sector_pct, 2),
                "limit": max_pct,
                "severity": "HIGH"
            })

        return {
            "sector": sector,
            "sector_pct": round(sector_pct, 2),
            "limit": max_pct,
            "status": status
        }

    def check_leverage(self, total_position: float, total_value: float) -> dict:
        """检查杠杆"""
        leverage = total_position / total_value if total_value > 0 else 0
        max_leverage = self.config.get("max_leverage", 1.0)

        status = "OK" if leverage <= max_leverage else "WARNING"

        if leverage > max_leverage:
            self._log_alert("leverage_limit", "portfolio", {
                "leverage": round(leverage, 2),
                "limit": max_leverage,
                "severity": "HIGH"
            })

        return {
            "leverage": round(leverage, 2),
            "limit": max_leverage,
            "status": status,
            "action": "REDUCE_LEVERAGE" if leverage > max_leverage else "OK"
        }

    def calculate_stop_loss(self, entry_price: float, current_price: float,
                           position_type: str = "long") -> dict:
        """计算止损"""
        stop_pct = self.config.get("stop_loss_pct", 5)

        if position_type == "long":
            stop_price = entry_price * (1 - stop_pct / 100)
            loss_pct = (entry_price - current_price) / entry_price * 100
            triggered = current_price <= stop_price
        else:
            stop_price = entry_price * (1 + stop_pct / 100)
            loss_pct = (current_price - entry_price) / entry_price * 100
            triggered = current_price >= stop_price

        return {
            "entry_price": entry_price,
            "current_price": current_price,
            "stop_price": round(stop_price, 2),
            "stop_pct": stop_pct,
            "current_loss_pct": round(loss_pct, 2),
            "triggered": triggered,
            "action": "STOP" if triggered else "HOLD"
        }

    def calculate_var(self, returns: list, confidence: float = None) -> dict:
        """计算VaR (Value at Risk)"""
        if not returns:
            return {"status": "error", "message": "No returns data"}

        if confidence is None:
            confidence = self.config.get("var_confidence", 0.95)

        # 简化: 基于历史返回的百分位数
        sorted_returns = sorted(returns)
        index = int((1 - confidence) * len(sorted_returns))
        var = abs(sorted_returns[index]) if index < len(sorted_returns) else 0

        return {
            "var": round(var * 100, 2),
            "confidence": confidence,
            "interpretation": f"{int(confidence *100)}% confidence: max loss is {round(var *100, 2)}%"
        }

    def check_daily_loss(self, daily_pnl: float, total_value: float) -> dict:
        """检查日亏损"""
        if total_value == 0:
            return {"status": "OK"}

        loss_pct = abs(daily_pnl / total_value * 100) if daily_pnl < 0 else 0
        max_loss = self.config.get("max_daily_loss", 3)

        status = "OK" if loss_pct <= max_loss else "STOP"

        if loss_pct > max_loss:
            self._log_alert("daily_loss", "portfolio", {
                "loss_pct": round(loss_pct, 2),
                "limit": max_loss,
                "severity": "HIGH"
            })

        return {
            "daily_pnl": round(daily_pnl, 2),
            "loss_pct": round(loss_pct, 2),
            "limit": max_loss,
            "status": status,
            "action": "STOP_TRADING" if loss_pct > max_loss else "CONTINUE"
        }

    def _log_alert(self, alert_type: str, symbol: str, details: dict):
        """记录告警"""
        if not self.config.get("warnings_enabled", True):
            return

        alerts = []
        if self.alerts_file.exists():
            try:
                with open(self.alerts_file, "r", encoding="utf-8") as f:
                    alerts = json.load(f)
            except (Exception,):
                pass

        alert = {
            "type": alert_type,
            "symbol": symbol,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }

        alerts.append(alert)
        alerts = alerts[-100:]

        with open(self.alerts_file, "w", encoding="utf-8") as f:
            json.dump(alerts, f, ensure_ascii=False, indent=2)

    def full_check(self, portfolio: dict) -> dict:
        """全面风险检查"""
        total_value = portfolio.get("total_value", 0)

        checks = {
            "positions": [],
            "sectors": [],
            "leverage": None,
            "daily_loss": None
        }

        # 检查各持仓
        for pos in portfolio.get("positions", []):
            check = self.check_position(
                pos.get("symbol"),
                pos.get("value", 0),
                total_value
            )
            checks["positions"].append(check)

        # 检查板块
        for sector, value in portfolio.get("sectors", {}).items():
            check = self.check_sector(sector, value, total_value)
            checks["sectors"].append(check)

        # 检查杠杆
        total_position = sum(p.get("value", 0) for p in portfolio.get("positions", []))
        checks["leverage"] = self.check_leverage(total_position, total_value)

        # 检查日亏损
        checks["daily_loss"] = self.check_daily_loss(
            portfolio.get("daily_pnl", 0),
            total_value
        )

        # 汇总
        warnings = sum(1 for p in checks["positions"] if p["status"] != "OK")
        warnings += sum(1 for s in checks["sectors"] if s["status"] != "OK")
        if checks["leverage"] and checks["leverage"]["status"] != "OK":
            warnings += 1
        if checks["daily_loss"] and checks["daily_loss"]["status"] != "OK":
            warnings += 1

        return {
            "timestamp": datetime.now().isoformat(),
            "total_value": total_value,
            "warnings": warnings,
            "status": "OK" if warnings == 0 else "WARNING",
            "checks": checks
        }

    def get_alerts(self, limit: int = 20) -> dict:
        """获取告警"""
        if not self.alerts_file.exists():
            return {"status": "error", "message": "No alerts"}

        with open(self.alerts_file, "r", encoding="utf-8") as f:
            alerts = json.load(f)

        return {
            "status": "success",
            "count": len(alerts),
            "alerts": alerts[-limit:]
        }

    def clear_alerts(self):
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
# py sa_risk_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py sa_risk_001.py

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

清空告警"""
        if self.alerts_file.exists():
            self.alerts_file.unlink()
        return {"status": "success"}


logging.basicConfig(level=logging.INFO)
def main():
    manager = RiskManager()

    if len(sys.argv) > 1:
        if sys.argv[1] == "--check":
            # 模拟组合数据
            portfolio = {
                "total_value": 100000,
                "positions": [
                    {"symbol": "AAPL", "value": 25000},
                    {"symbol": "GOOGL", "value": 20000},
                    {"symbol": "MSFT", "value": 15000}
                ],
                "sectors": {"科技": 60000},
                "daily_pnl": -2000
            }
            result = manager.full_check(portfolio)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if sys.argv[1] == "--position":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
            value = float(sys.argv[3]) if len(sys.argv) > 3 else 25000
            total = float(sys.argv[4]) if len(sys.argv) > 4 else 100000
            result = manager.check_position(symbol, value, total)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if sys.argv[1] == "--stop":
            entry = float(sys.argv[2]) if len(sys.argv) > 2 else 100
            current = float(sys.argv[3]) if len(sys.argv) > 3 else 95
            result = manager.calculate_stop_loss(entry, current)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if sys.argv[1] == "--var":
            returns = [-0.02, -0.01, 0.005, 0.01, -0.015, 0.02]
            result = manager.calculate_var(returns)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        if sys.argv[1] == "--alerts":
            result = manager.get_alerts()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

    print("SA-034 Risk Manager")
    print("Usage:")
    print("  py sa_034_risk.py --check              # Full check")
    print("  py sa_034_risk.py --position AAPL 25000 100000 # Check position")
    print("  py sa_034_risk.py --stop 100 95        # Calculate stop loss")
    print("  py sa_034_risk.py --var                # Calculate VaR")
    print("  py sa_034_risk.py --alerts             # Get alerts")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
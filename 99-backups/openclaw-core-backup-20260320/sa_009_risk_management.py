#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-009: Risk Management
Position sizing, stop-loss, take-profit, risk-reward calculation
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import math

class RiskManager:
    """Manage trading risk and position sizing"""

    def __init__(self, data_dir: str = "60-DATA/stock_risk"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.analysis_log = self._load_analysis_log()

    def _load_analysis_log(self) -> Dict:
        """Load analysis log"""
        log_file = self.data_dir / "analysis_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "version": "1.0",
            "analyses": [],
            "stats": {
                "total_analyses": 0,
                "positions_calculated": 0,
            }
        }

    def _save_analysis_log(self):
        """Save analysis log"""
        log_file = self.data_dir / "analysis_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.analysis_log, f, ensure_ascii=False, indent=2)

    def calculate_position_size(self, account_size: float, risk_per_trade: float,
                               entry_price: float, stop_loss_price: float) -> Dict:
        """
        Calculate optimal position size based on risk parameters
        
        Args:
            account_size: Total account value
            risk_per_trade: Risk percentage per trade (e.g., 0.02 for 2%)
            entry_price: Entry price
            stop_loss_price: Stop loss price
            
        Returns:
            Dict with position size details
        """
        if entry_price <= 0 or stop_loss_price <= 0:
            return {"error": "Invalid price"}

        if account_size <= 0:
            return {"error": "Invalid account size"}

        # Calculate risk amount
        risk_amount = account_size * risk_per_trade

        # Calculate risk per share
        risk_per_share = abs(entry_price - stop_loss_price)

        if risk_per_share == 0:
            return {"error": "Stop loss equals entry price"}

        # Calculate position size (shares)
        shares = int(risk_amount / risk_per_share)

        # Calculate position value
        position_value = shares * entry_price

        # Calculate position size as percentage of account
        position_pct = (position_value / account_size) * 100 if account_size > 0 else 0

        return {
            "account_size": round(account_size, 2),
            "risk_per_trade_pct": round(risk_per_trade * 100, 2),
            "risk_amount": round(risk_amount, 2),
            "entry_price": round(entry_price, 2),
            "stop_loss_price": round(stop_loss_price, 2),
            "risk_per_share": round(risk_per_share, 2),
            "position_size_shares": shares,
            "position_value": round(position_value, 2),
            "position_size_pct": round(position_pct, 2),
            "max_loss": round(risk_amount, 2)
        }

    def calculate_stop_loss(self, entry_price: float, volatility: float,
                           support_level: Optional[float] = None,
                           method: str = "volatility") -> Dict:
        """
        Calculate stop loss level using different methods
        
        Args:
            entry_price: Entry price
            volatility: Price volatility (ATR or standard deviation)
            support_level: Key support level (optional)
            method: Calculation method (volatility/support/percentage)
            
        Returns:
            Dict with stop loss details
        """
        if entry_price <= 0:
            return {"error": "Invalid entry price"}

        result = {
            "entry_price": round(entry_price, 2),
            "method": method,
            "stop_loss_price": 0,
            "stop_loss_pct": 0,
            "risk_per_share": 0
        }

        if method == "volatility":
            # ATR-based stop loss (2x ATR)
            stop_distance = volatility * 2
            stop_price = entry_price - stop_distance
            result["stop_loss_price"] = round(stop_price, 2)
            result["stop_loss_pct"] = round((stop_distance / entry_price) * 100, 2)
            result["risk_per_share"] = round(stop_distance, 2)
            result["atr_multiple"] = 2.0

        elif method == "support":
            if support_level and support_level < entry_price:
                # Place stop slightly below support
                buffer = (entry_price - support_level) * 0.02  # 2% buffer
                stop_price = support_level - buffer
                result["stop_loss_price"] = round(stop_price, 2)
                result["stop_loss_pct"] = round(((entry_price - stop_price) / entry_price) * 100, 2)
                result["risk_per_share"] = round(entry_price - stop_price, 2)
                result["support_level"] = round(support_level, 2)
            else:
                result["error"] = "Invalid support level"

        elif method == "percentage":
            # Fixed percentage stop (e.g., 5%)
            stop_pct = 0.05
            stop_price = entry_price * (1 - stop_pct)
            result["stop_loss_price"] = round(stop_price, 2)
            result["stop_loss_pct"] = round(stop_pct * 100, 2)
            result["risk_per_share"] = round(entry_price - stop_price, 2)
            result["fixed_pct"] = stop_pct * 100

        return result

    def calculate_take_profit(self, entry_price: float, resistance_level: Optional[float],
                             risk_reward_ratio: float = 2.0,
                             stop_loss_price: float = 0) -> Dict:
        """
        Calculate take profit levels
        
        Args:
            entry_price: Entry price
            resistance_level: Key resistance level
            risk_reward_ratio: Target risk-reward ratio
            stop_loss_price: Stop loss price
            
        Returns:
            Dict with take profit levels
        """
        if entry_price <= 0:
            return {"error": "Invalid entry price"}

        result = {
            "entry_price": round(entry_price, 2),
            "take_profit_levels": []
        }

        # Calculate based on risk-reward ratio
        if stop_loss_price > 0:
            risk = entry_price - stop_loss_price
            reward = risk * risk_reward_ratio

            tp1 = entry_price + reward * 0.5  # 50% at 1:1
            tp2 = entry_price + reward  # 50% at target R:R

            result["take_profit_levels"].append({
                "level": "TP1",
                "price": round(tp1, 2),
                "pct_gain": round((tp1 - entry_price) / entry_price * 100, 2),
                "portion": "50%"
            })

            result["take_profit_levels"].append({
                "level": "TP2",
                "price": round(tp2, 2),
                "pct_gain": round((tp2 - entry_price) / entry_price * 100, 2),
                "portion": "50%"
            })

        # Add resistance-based target
        if resistance_level and resistance_level > entry_price:
            result["resistance_target"] = round(resistance_level, 2)
            result["resistance_gain_pct"] = round((resistance_level - entry_price) / entry_price * 100, 2)

        return result

    def calculate_risk_reward(self, entry_price: float, stop_loss: float,
                             take_profit: float) -> Dict:
        """
        Calculate risk-reward ratio
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            
        Returns:
            Dict with risk-reward analysis
        """
        if entry_price <= 0 or stop_loss <= 0 or take_profit <= 0:
            return {"error": "Invalid prices"}

        risk = entry_price - stop_loss
        reward = take_profit - entry_price

        if risk <= 0:
            return {"error": "Stop loss must be below entry"}

        rr_ratio = reward / risk

        return {
            "entry_price": round(entry_price, 2),
            "stop_loss": round(stop_loss, 2),
            "take_profit": round(take_profit, 2),
            "risk_amount": round(risk, 2),
            "reward_amount": round(reward, 2),
            "risk_pct": round((risk / entry_price) * 100, 2),
            "reward_pct": round((reward / entry_price) * 100, 2),
            "risk_reward_ratio": round(rr_ratio, 2),
            "quality": self._evaluate_rr_quality(rr_ratio)
        }

    def _evaluate_rr_quality(self, rr_ratio: float) -> str:
        """Evaluate risk-reward ratio quality"""
        if rr_ratio >= 3.0:
            return "excellent"
        elif rr_ratio >= 2.0:
            return "good"
        elif rr_ratio >= 1.5:
            return "acceptable"
        else:
            return "poor"

    def analyze_trade(self, symbol: str, entry_price: float,
                     account_size: float = 100000,
                     risk_per_trade: float = 0.02,
                     volatility: float = 2.0,
                     support: Optional[float] = None,
                     resistance: Optional[float] = None) -> Dict:
        """
        Comprehensive trade risk analysis
        
        Args:
            symbol: Stock symbol
            entry_price: Entry price
            account_size: Account size
            risk_per_trade: Risk percentage per trade
            volatility: Price volatility (ATR)
            support: Support level
            resistance: Resistance level
            
        Returns:
            Dict with complete trade analysis
        """
        result = {
            "symbol": symbol,
            "analyzed_at": datetime.now().isoformat(),
            "entry_price": round(entry_price, 2),
            "account_size": round(account_size, 2),
            "position_sizing": {},
            "stop_loss": {},
            "take_profit": {},
            "risk_reward": {},
            "recommendation": ""
        }

        # Calculate stop loss (volatility-based)
        result["stop_loss"] = self.calculate_stop_loss(
            entry_price, volatility, support, method="volatility"
        )

        stop_price = result["stop_loss"].get("stop_loss_price", entry_price * 0.95)

        # Calculate position size
        result["position_sizing"] = self.calculate_position_size(
            account_size, risk_per_trade, entry_price, stop_price
        )

        # Calculate take profit
        result["take_profit"] = self.calculate_take_profit(
            entry_price, resistance, risk_reward_ratio=2.0, stop_loss_price=stop_price
        )

        # Calculate risk-reward
        if result["take_profit"]["take_profit_levels"]:
            tp_price = result["take_profit"]["take_profit_levels"][1]["price"]
            result["risk_reward"] = self.calculate_risk_reward(
                entry_price, stop_price, tp_price
            )

        # Generate recommendation
        result["recommendation"] = self._generate_trade_recommendation(result)

        # Save to cache
        cache_file = self.data_dir / f"{symbol}_risk_analysis.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        # Log analysis
        self._log_analysis(symbol, result["risk_reward"].get("risk_reward_ratio", 0), success=True)

        return result

    def _generate_trade_recommendation(self, result: Dict) -> str:
        """Generate trade recommendation"""
        rr_quality = result.get("risk_reward", {}).get("quality", "unknown")
        position_pct = result.get("position_sizing", {}).get("position_size_pct", 0)

        if rr_quality in ["excellent", "good"]:
            if position_pct < 50:
                return f"GOOD TRADE SETUP - R:R {rr_quality}, position size {position_pct:.1f}% of account"
            else:
                return f"CAUTION - Good R:R but position too large ({position_pct:.1f}%)"
        elif rr_quality == "acceptable":
            return f"MARGINAL - Acceptable R:R, consider waiting for better setup"
        else:
            return f"POOR SETUP - R:R ratio too low, skip this trade"

    def _log_analysis(self, symbol: str, rr_ratio: float, success: bool):
        """Log analysis attempt"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "rr_ratio": rr_ratio,
            "success": success
        }

        self.analysis_log["analyses"].append(log_entry)
        self.analysis_log["stats"]["total_analyses"] += 1
        self.analysis_log["stats"]["positions_calculated"] += 1

        # Keep only last 500 entries
        self.analysis_log["analyses"] = self.analysis_log["analyses"][-500:]

        self._save_analysis_log()

    def get_stats(self) -> Dict:
        """Get analysis statistics"""
        return self.analysis_log["stats"].copy()

    def display_status(self) -> str:
        """Display manager status"""
        stats = self.get_stats()

        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 18 + "Risk Manager Status")
        output.append("=" * 70)

        output.append(f"\n[Risk Management Features]")
        output.append("  - Position Sizing (Kelly-based)")
        output.append("  - Stop Loss Calculation (ATR/Support/Percentage)")
        output.append("  - Take Profit Targets (R:R based)")
        output.append("  - Risk-Reward Analysis")

        output.append(f"\n[Statistics]")
        output.append(f"  Total Analyses:        {stats['total_analyses']}")
        output.append(f"  Positions Calculated:  {stats['positions_calculated']}")

        output.append("\n" + "=" * 70 + "\n")

        return "\n".join(output)


def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 18 + "SA-009: Risk Management")
    print("=" * 70)

    manager = RiskManager()

    # Test 1: Display status
    print(manager.display_status())

    # Test 2: Analyze sample trade
    print("\n[Test 1] Analyze Sample Trade")
    print("-" * 70)

    result = manager.analyze_trade(
        symbol="TEST",
        entry_price=100.0,
        account_size=100000,
        risk_per_trade=0.02,
        volatility=2.5,
        support=95.0,
        resistance=110.0
    )

    print(f"  Symbol:           {result['symbol']}")
    print(f"  Entry Price:      ${result['entry_price']}")
    print(f"  Account Size:     ${result['account_size']:,.0f}")

    print(f"\n  Position Sizing:")
    ps = result["position_sizing"]
    if "error" not in ps:
        print(f"    Risk per Trade:   {ps['risk_per_trade_pct']}% (${ps['risk_amount']:,.2f})")
        print(f"    Stop Loss:        ${ps['stop_loss_price']}")
        print(f"    Position Size:    {ps['position_size_shares']} shares")
        print(f"    Position Value:   ${ps['position_value']:,.2f} ({ps['position_size_pct']:.1f}% of account)")
        print(f"    Max Loss:         ${ps['max_loss']:,.2f}")

    print(f"\n  Stop Loss:")
    sl = result["stop_loss"]
    if "error" not in sl:
        print(f"    Method:           {sl['method']}")
        print(f"    Stop Price:       ${sl['stop_loss_price']}")
        print(f"    Stop Distance:    {sl['stop_loss_pct']}%")
        if "atr_multiple" in sl:
            print(f"    ATR Multiple:     {sl['atr_multiple']}x")

    print(f"\n  Take Profit:")
    tp = result["take_profit"]
    for level in tp.get("take_profit_levels", []):
        print(f"    {level['level']:6} ${level['price']:7.2f} (+{level['pct_gain']:.1f}%) - {level['portion']}")

    print(f"\n  Risk-Reward:")
    rr = result.get("risk_reward", {})
    if "error" not in rr:
        print(f"    R:R Ratio:        {rr['risk_reward_ratio']:.2f}:1")
        print(f"    Quality:          {rr['quality'].upper()}")
        print(f"    Risk:             {rr['risk_pct']:.2f}%")
        print(f"    Reward:           {rr['reward_pct']:.2f}%")

    print(f"\n  Recommendation: {result['recommendation']}")

    # Test 3: Final stats
    print("\n[Test 2] Final Statistics")
    print("-" * 70)
    stats = manager.get_stats()
    print(f"  Total Analyses:        {stats['total_analyses']}")
    print(f"  Positions Calculated:  {stats['positions_calculated']}")

    print("\n[OK] SA-009 Risk Management test completed")

if __name__ == "__main__":
    main()

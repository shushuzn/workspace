import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis - SA-011: Backtesting Engine
Simple backtesting for trading strategies
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import math

class Backtester:
    """Backtest trading strategies on historical data"""
    
    def __init__(self, data_dir: str = "60-DATA/stock_backtests"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.backtest_log = self._load_backtest_log()
    
    def _load_backtest_log(self) -> Dict:
        """Load backtest log"""
        log_file = self.data_dir / "backtest_log.json"
        if log_file.exists():
            with open(log_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "backtests": [],
            "stats": {
                "total_backtests": 0,
            }
        }
    
    def _save_backtest_log(self):
        """Save backtest log"""
        log_file = self.data_dir / "backtest_log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(self.backtest_log, f, ensure_ascii=False, indent=2)
    
    def run_backtest(self, symbol: str, candles: List[Dict],
                    strategy: Dict, initial_capital: float = 100000) -> Dict:
        """
        Run simple backtest
        
        Args:
            symbol: Stock symbol
            candles: List of historical candles
            strategy: Strategy parameters
            initial_capital: Starting capital
            
        Returns:
            Dict with backtest results
        """
        if not candles or len(candles) < 50:
            return {"error": "Insufficient data (need at least 50 candles)"}
        
        capital = initial_capital
        position = 0
        trades = []
        equity_curve = []
        
        # Strategy parameters
        entry_signal = strategy.get("entry_signal", "buy")
        exit_signal = strategy.get("exit_signal", "sell")
        position_size_pct = strategy.get("position_size", 0.1)
        stop_loss_pct = strategy.get("stop_loss", 0.05)
        take_profit_pct = strategy.get("take_profit", 0.10)
        
        entry_price = 0
        stop_loss = 0
        take_profit = 0
        
        for i, candle in enumerate(candles):
            current_price = candle["close"]
            
            # Check for exit conditions if we have a position
            if position > 0:
                # Check stop loss
                if current_price <= stop_loss:
                    # Stop loss hit
                    proceeds = position * current_price
                    pnl = proceeds - (position * entry_price)
                    capital += proceeds
                    trades.append({
                        "type": "stop_loss",
                        "entry_price": entry_price,
                        "exit_price": current_price,
                        "shares": position,
                        "pnl": round(pnl, 2),
                        "pnl_pct": round(pnl / (position * entry_price) * 100, 2),
                        "exit_index": i,
                        "exit_date": candle.get("date", "")
                    })
                    position = 0
                    
                # Check take profit
                elif current_price >= take_profit:
                    # Take profit hit
                    proceeds = position * current_price
                    pnl = proceeds - (position * entry_price)
                    capital += proceeds
                    trades.append({
                        "type": "take_profit",
                        "entry_price": entry_price,
                        "exit_price": current_price,
                        "shares": position,
                        "pnl": round(pnl, 2),
                        "pnl_pct": round(pnl / (position * entry_price) * 100, 2),
                        "exit_index": i,
                        "exit_date": candle.get("date", "")
                    })
                    position = 0
                
                # Check manual exit signal
                elif self._check_exit_signal(candle, exit_signal):
                    proceeds = position * current_price
                    pnl = proceeds - (position * entry_price)
                    capital += proceeds
                    trades.append({
                        "type": "signal_exit",
                        "entry_price": entry_price,
                        "exit_price": current_price,
                        "shares": position,
                        "pnl": round(pnl, 2),
                        "pnl_pct": round(pnl / (position * entry_price) * 100, 2),
                        "exit_index": i,
                        "exit_date": candle.get("date", "")
                    })
                    position = 0
            
            # Check for entry conditions if we don't have a position
            if position == 0 and self._check_entry_signal(candle, entry_signal):
                # Calculate position size
                position_value = capital * position_size_pct
                position = int(position_value / current_price)
                
                if position > 0:
                    entry_price = current_price
                    stop_loss = entry_price * (1 - stop_loss_pct)
                    take_profit = entry_price * (1 + take_profit_pct)
                    capital -= position * entry_price
            
            # Record equity
            total_equity = capital + (position * current_price)
            equity_curve.append({
                "index": i,
                "date": candle.get("date", ""),
                "price": current_price,
                "equity": round(total_equity, 2),
                "capital": round(capital, 2),
                "position_value": round(position * current_price, 2)
            })
        
        # Close any remaining position at the end
        if position > 0 and candles:
            final_price = candles[-1]["close"]
            proceeds = position * final_price
            pnl = proceeds - (position * entry_price)
            capital += proceeds
            trades.append({
                "type": "final_close",
                "entry_price": entry_price,
                "exit_price": final_price,
                "shares": position,
                "pnl": round(pnl, 2),
                "pnl_pct": round(pnl / (position * entry_price) * 100, 2) if entry_price > 0 else 0
            })
        
        # Calculate performance metrics
        final_equity = capital + (position * candles[-1]["close"] if candles else 0)
        total_return = (final_equity - initial_capital) / initial_capital * 100
        
        # Calculate max drawdown
        max_equity = max(e["equity"] for e in equity_curve)
        min_equity_after_peak = min_equity = equity_curve[0]["equity"]
        max_drawdown = 0
        
        for e in equity_curve:
            if e["equity"] > max_equity:
                max_equity = e["equity"]
            drawdown = (max_equity - e["equity"]) / max_equity * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        # Calculate win rate
        winning_trades = sum(1 for t in trades if t["pnl"] > 0)
        total_trades = len(trades)
        win_rate = (winning_trades / total_trades * 100) if total_trades > 0 else 0
        
        # Calculate average win/loss
        winning_pnls = [t["pnl"] for t in trades if t["pnl"] > 0]
        losing_pnls = [t["pnl"] for t in trades if t["pnl"] <= 0]
        
        avg_win = sum(winning_pnls) / len(winning_pnls) if winning_pnls else 0
        avg_loss = sum(losing_pnls) / len(losing_pnls) if losing_pnls else 0
        
        result = {
            "symbol": symbol,
            "backtested_at": datetime.now().isoformat(),
            "strategy": strategy,
            "initial_capital": round(initial_capital, 2),
            "final_equity": round(final_equity, 2),
            "total_return_pct": round(total_return, 2),
            "total_trades": total_trades,
            "winning_trades": winning_trades,
            "losing_trades": total_trades - winning_trades,
            "win_rate_pct": round(win_rate, 2),
            "avg_win": round(avg_win, 2),
            "avg_loss": round(avg_loss, 2),
            "profit_factor": round(abs(sum(winning_pnls) / sum(losing_pnls)), 2) if losing_pnls and sum(losing_pnls) != 0 else 999,
            "max_drawdown_pct": round(max_drawdown, 2),
            "sharpe_ratio": self._calculate_sharpe(equity_curve),
            "trades": trades[-20:],  # Last 20 trades
            "equity_curve": equity_curve[-50:]  # Last 50 points
        }
        
        # Save to cache
        cache_file = self.data_dir / f"{symbol}_backtest.json"
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        # Log backtest
        self._log_backtest(symbol, total_return, success=True)
        
        return result
    
    def _check_entry_signal(self, candle: Dict, signal_type: str) -> bool:
        """Check if entry signal is triggered (simplified)"""
        # In real implementation, this would check technical indicators
        # For now, use simple random or pattern matching
        return False  # Placeholder
    
    def _check_exit_signal(self, candle: Dict, signal_type: str) -> bool:
        """Check if exit signal is triggered (simplified)"""
        return False  # Placeholder
    
    def _calculate_sharpe(self, equity_curve: List[Dict]) -> float:
        """Calculate Sharpe ratio (simplified)"""
        if len(equity_curve) < 10:
            return 0
        
        # Calculate daily returns
        returns = []
        for i in range(1, len(equity_curve)):
            prev_equity = equity_curve[i-1]["equity"]
            curr_equity = equity_curve[i]["equity"]
            if prev_equity > 0:
                daily_return = (curr_equity - prev_equity) / prev_equity
                returns.append(daily_return)
        
        if not returns:
            return 0
        
        # Calculate mean and std of returns
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_return = math.sqrt(variance)
        
        # Annualize (assume 252 trading days)
        annualized_return = mean_return * 252
        annualized_std = std_return * math.sqrt(252)
        
        # Sharpe ratio (assume risk-free rate = 0 for simplicity)
        sharpe = annualized_return / annualized_std if annualized_std > 0 else 0
        
        return round(sharpe, 2)
    
    def _log_backtest(self, symbol: str, return_pct: float, success: bool):
        """Log backtest"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "symbol": symbol,
            "return_pct": return_pct,
            "success": success
        }
        
        self.backtest_log["backtests"].append(log_entry)
        self.backtest_log["stats"]["total_backtests"] += 1
        
        # Keep only last 100 entries
        self.backtest_log["backtests"] = self.backtest_log["backtests"][-100:]
        
        self._save_backtest_log()
    
    def get_stats(self) -> Dict:
        """Get backtest statistics"""
        return self.backtest_log["stats"].copy()
    
    def display_status(self) -> str:
        """Display backtester status"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 16 + "Backtesting Engine Status")
        output.append("=" * 70)
        
        output.append(f"\n[Features]")
        output.append("  - Historical backtesting")
        output.append("  - Position sizing")
        output.append("  - Stop loss / Take profit")
        output.append("  - Performance metrics")
        output.append("  - Equity curve tracking")
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Backtests:  {stats['total_backtests']}")
        
        output.append("\n" + "=" * 70 + "\n")
        
        return "\n".join(output)


logging.basicConfig(level=logging.INFO)
def main():
    """Test entry point"""
    print("=" * 70)
    print(" " * 16 + "SA-011: Backtesting Engine")
    print("=" * 70)
    
    backtester = Backtester()
    
    # Test 1: Display status
    print(backtester.display_status())
    
    # Test 2: Generate test data
    print("\n[Test 1] Generate Test Data")
    print("-" * 70)
    import random
    random.seed(42)
    
    candles = []
    price = 100
    
    for i in range(200):
        # Create trending price with noise
        trend = 0.0005 * i  # Slight uptrend
        noise = random.uniform(-0.02, 0.02)
        price *= (1 + trend + noise)
        
        open_p = price
        close_p = price * (1 + random.uniform(-0.01, 0.01))
        high_p = max(open_p, close_p) * (1 + random.uniform(0, 0.015))
        low_p = min(open_p, close_p) * (1 - random.uniform(0, 0.015))
        volume = random.randint(5000000, 50000000)
        
        candles.append({
            "date": f"2026-01-{i%30+1:02d}",
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2),
            "volume": volume
        })
    
    print(f"  Generated {len(candles)} candles")
    print(f"  Price range: {min(c['low'] for c in candles):.2f} - {max(c['high'] for c in candles):.2f}")
    
    # Test 3: Run backtest
    print("\n[Test 2] Run Backtest")
    print("-" * 70)
    
    strategy = {
        "entry_signal": "ma_crossover",
        "exit_signal": "reverse_crossover",
        "position_size": 0.2,
        "stop_loss": 0.05,
        "take_profit": 0.10
    }
    
    result = backtester.run_backtest("TEST", candles, strategy, initial_capital=100000)
    
    if "error" not in result:
        print(f"  Symbol:           {result['symbol']}")
        print(f"  Initial Capital:  ${result['initial_capital']:,.0f}")
        print(f"  Final Equity:     ${result['final_equity']:,.0f}")
        print(f"  Total Return:     {result['total_return_pct']:+.2f}%")
        
        print(f"\n  Trade Statistics:")
        print(f"    Total Trades:   {result['total_trades']}")
        print(f"    Winning:        {result['winning_trades']}")
        print(f"    Losing:         {result['losing_trades']}")
        print(f"    Win Rate:       {result['win_rate_pct']:.1f}%")
        
        print(f"\n  Performance Metrics:")
        print(f"    Avg Win:        ${result['avg_win']:,.2f}")
        print(f"    Avg Loss:       ${result['avg_loss']:,.2f}")
        print(f"    Profit Factor:  {result['profit_factor']:.2f}")
        print(f"    Max Drawdown:   {result['max_drawdown_pct']:.2f}%")
        print(f"    Sharpe Ratio:   {result['sharpe_ratio']:.2f}")
        
        if result["trades"]:
            print(f"\n  Recent Trades:")
            for i, trade in enumerate(result["trades"][-5:], 1):
                print(f"    [{i}] {trade['type']:12} PnL: ${trade['pnl']:>8.2f} ({trade['pnl_pct']:+.1f}%)")
    
    # Test 4: Final stats
    print("\n[Test 3] Final Statistics")
    print("-" * 70)
    stats = backtester.get_stats()
    print(f"  Total Backtests:  {stats['total_backtests']}")
    
    print("\n[OK] SA-011 Backtesting Engine test completed")

if __name__ == "__main__":
    main()

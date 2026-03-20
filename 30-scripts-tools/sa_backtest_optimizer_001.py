#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-BACKTEST-OPTIMIZER-001 Enhanced Backtesting Engine
======================================================
Advanced backtesting with optimization and parameter scanning
"""

import json, sys, random, math
from pathlib import Path
from datetime import datetime, timedelta

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class BacktestOptimizer:
    def __init__(self):
        self.results = []
        self.data_dir = Path("60-DATA/stock_backtest")
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_data(self, days=200, start_price=100, volatility=0.02):
        """Generate realistic OHLCV data"""
        candles = []
        price = start_price
        
        for i in range(days):
            change = random.gauss(0, volatility)
            open_price = price
            high = price * (1 + abs(change) + random.uniform(0, 0.01))
            low = price * (1 - abs(change) - random.uniform(0, 0.01))
            close = price * (1 + change)
            volume = int(random.uniform(1e6, 5e6))
            
            candles.append({
                "date": (datetime.now() - timedelta(days=days-i)).strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high, 2),
                "low": round(low, 2),
                "close": round(close, 2),
                "volume": volume
            })
            price = close
        
        return candles
    
    def backtest(self, candles, strategy="ma_cross", capital=100000, params=None):
        """Run backtest with given strategy"""
        params = params or self.default_params(strategy)
        
        if strategy == "ma_cross":
            return self.ma_cross_strategy(candles, capital, params)
        elif strategy == "rsi":
            return self.rsi_strategy(candles, capital, params)
        elif strategy == "bollinger":
            return self.bollinger_strategy(candles, capital, params)
        else:
            return self.sma_strategy(candles, capital, params)
    
    def default_params(self, strategy):
        """Get default parameters for strategy"""
        defaults = {
            "ma_cross": {"fast": 10, "slow": 30, "stop_loss": 0.02, "take_profit": 0.05},
            "rsi": {"period": 14, "oversold": 30, "overbought": 70, "stop_loss": 0.02},
            "bollinger": {"period": 20, "std_dev": 2, "stop_loss": 0.02},
            "sma": {"period": 20, "stop_loss": 0.02}
        }
        return defaults.get(strategy, defaults["ma_cross"])
    
    def calculate_ma(self, candles, period):
        """Calculate moving average"""
        ma = []
        for i in range(len(candles)):
            if i < period - 1:
                ma.append(None)
            else:
                avg = sum(c["close"] for c in candles[i-period+1:i+1]) / period
                ma.append(round(avg, 2))
        return ma
    
    def calculate_rsi(self, candles, period=14):
        """Calculate RSI"""
        if len(candles) < period + 1:
            return [50] * len(candles)
        
        gains = []
        losses = []
        for i in range(1, len(candles)):
            change = candles[i]["close"] - candles[i-1]["close"]
            gains.append(max(0, change))
            losses.append(max(0, -change))
        
        rsi = [50] * period
        for i in range(period, len(gains) + 1):
            avg_gain = sum(gains[i-period:i]) / period
            avg_loss = sum(losses[i-period:i]) / period if sum(losses[i-period:i]) > 0 else 1
            rs = avg_gain / avg_loss
            rsi.append(round(100 - (100 / (1 + rs)), 2))
        
        return rsi
    
    def ma_cross_strategy(self, candles, capital, params):
        """MA Crossover Strategy"""
        fast = params.get("fast", 10)
        slow = params.get("slow", 30)
        stop_loss = params.get("stop_loss", 0.02)
        take_profit = params.get("take_profit", 0.05)
        
        ma_fast = self.calculate_ma(candles, fast)
        ma_slow = self.calculate_ma(candles, slow)
        
        position = 0
        entry_price = 0
        trades = []
        equity = capital
        
        for i in range(slow, len(candles)):
            date = candles[i]["date"]
            close = candles[i]["close"]
            
            if ma_fast[i] is None or ma_slow[i] is None:
                continue
            
            # Buy signal
            if ma_fast[i] > ma_slow[i] and position == 0:
                shares = math.floor(equity * 0.95 / close)
                if shares > 0:
                    position = shares
                    entry_price = close
                    equity -= position * close
                    trades.append({"type": "BUY", "date": date, "price": close, "shares": position})
            
            # Sell signal
            elif ma_fast[i] < ma_slow[i] and position > 0:
                equity += position * close
                pnl = (close - entry_price) / entry_price * 100
                trades.append({"type": "SELL", "date": date, "price": close, "shares": position, "pnl": round(pnl, 2)})
                position = 0
            
            # Stop loss / Take profit
            elif position > 0:
                pnl_pct = (close - entry_price) / entry_price
                if pnl_pct <= -stop_loss or pnl_pct >= take_profit:
                    equity += position * close
                    reason = "STOP_LOSS" if pnl_pct < 0 else "TAKE_PROFIT"
                    trades.append({"type": "SELL", "date": date, "price": close, "shares": position, "reason": reason})
                    position = 0
        
        # Close final position
        if position > 0:
            equity += position * candles[-1]["close"]
        
        return self.calculate_metrics(candles, trades, capital, equity)
    
    def rsi_strategy(self, candles, capital, params):
        """RSI Strategy"""
        period = params.get("period", 14)
        oversold = params.get("oversold", 30)
        overbought = params.get("overbought", 70)
        stop_loss = params.get("stop_loss", 0.02)
        
        rsi = self.calculate_rsi(candles, period)
        
        position = 0
        entry_price = 0
        trades = []
        equity = capital
        
        for i in range(period + 1, len(candles)):
            date = candles[i]["date"]
            close = candles[i]["close"]
            
            # Buy oversold
            if rsi[i] < oversold and position == 0:
                shares = math.floor(equity * 0.95 / close)
                if shares > 0:
                    position = shares
                    entry_price = close
                    equity -= position * close
                    trades.append({"type": "BUY", "date": date, "price": close, "shares": position, "rsi": rsi[i]})
            
            # Sell overbought
            elif rsi[i] > overbought and position > 0:
                equity += position * close
                pnl = (close - entry_price) / entry_price * 100
                trades.append({"type": "SELL", "date": date, "price": close, "shares": position, "pnl": round(pnl, 2), "rsi": rsi[i]})
                position = 0
            
            # Stop loss
            elif position > 0 and (close - entry_price) / entry_price <= -stop_loss:
                equity += position * close
                trades.append({"type": "SELL", "date": date, "price": close, "shares": position, "reason": "STOP_LOSS"})
                position = 0
        
        if position > 0:
            equity += position * candles[-1]["close"]
        
        return self.calculate_metrics(candles, trades, capital, equity)
    
    def bollinger_strategy(self, candles, capital, params):
        """Bollinger Bands Strategy"""
        period = params.get("period", 20)
        std_dev = params.get("std_dev", 2)
        stop_loss = params.get("stop_loss", 0.02)
        
        # Calculate Bollinger Bands
        middle = self.calculate_ma(candles, period)
        upper = [None] * len(candles)
        lower = [None] * len(candles)
        
        for i in range(period - 1, len(candles)):
            if middle[i]:
                std = math.sqrt(sum((c["close"] - middle[i])**2 for c in candles[i-period+1:i+1]) / period)
                upper[i] = round(middle[i] + std_dev * std, 2)
                lower[i] = round(middle[i] - std_dev * std, 2)
        
        position = 0
        entry_price = 0
        trades = []
        equity = capital
        
        for i in range(period, len(candles)):
            date = candles[i]["date"]
            close = candles[i]["close"]
            
            # Buy at lower band
            if lower[i] and close <= lower[i] and position == 0:
                shares = math.floor(equity * 0.95 / close)
                if shares > 0:
                    position = shares
                    entry_price = close
                    equity -= position * close
                    trades.append({"type": "BUY", "date": date, "price": close, "shares": position})
            
            # Sell at upper band
            elif upper[i] and close >= upper[i] and position > 0:
                equity += position * close
                pnl = (close - entry_price) / entry_price * 100
                trades.append({"type": "SELL", "date": date, "price": close, "shares": position, "pnl": round(pnl, 2)})
                position = 0
            
            # Stop loss
            elif position > 0 and (close - entry_price) / entry_price <= -stop_loss:
                equity += position * close
                trades.append({"type": "SELL", "date": date, "price": close, "shares": position, "reason": "STOP_LOSS"})
                position = 0
        
        if position > 0:
            equity += position * candles[-1]["close"]
        
        return self.calculate_metrics(candles, trades, capital, equity)
    
    def sma_strategy(self, candles, capital, params):
        """Simple SMA Strategy"""
        period = params.get("period", 20)
        stop_loss = params.get("stop_loss", 0.02)
        
        ma = self.calculate_ma(candles, period)
        
        position = 0
        entry_price = 0
        trades = []
        equity = capital
        
        for i in range(period, len(candles)):
            date = candles[i]["date"]
            close = candles[i]["close"]
            
            if ma[i] and close > ma[i] and position == 0:
                shares = math.floor(equity * 0.95 / close)
                if shares > 0:
                    position = shares
                    entry_price = close
                    equity -= position * close
                    trades.append({"type": "BUY", "date": date, "price": close, "shares": position})
            
            elif ma[i] and close < ma[i] and position > 0:
                equity += position * close
                pnl = (close - entry_price) / entry_price * 100
                trades.append({"type": "SELL", "date": date, "price": close, "shares": position, "pnl": round(pnl, 2)})
                position = 0
        
        if position > 0:
            equity += position * candles[-1]["close"]
        
        return self.calculate_metrics(candles, trades, capital, equity)
    
    def calculate_metrics(self, candles, trades, capital, final_equity):
        """Calculate performance metrics"""
        total_return = (final_equity - capital) / capital * 100
        winning_trades = [t for t in trades if t.get("type") == "SELL" and t.get("pnl", 0) > 0]
        losing_trades = [t for t in trades if t.get("type") == "SELL" and t.get("pnl", 0) <= 0]
        
        win_rate = len(winning_trades) / len(trades) * 100 if trades else 0
        
        # Calculate max drawdown
        peak = capital
        max_dd = 0
        equity_curve = [capital]
        for t in trades:
            if t["type"] == "BUY":
                equity_curve.append(equity_curve[-1] - t["shares"] * t["price"])
            else:
                equity_curve.append(equity_curve[-1] + t["shares"] * t["price"])
        
        for eq in equity_curve:
            if eq > peak:
                peak = eq
            dd = (peak - eq) / peak * 100
            if dd > max_dd:
                max_dd = dd
        
        # Sharpe ratio (simplified)
        returns = []
        for i in range(1, len(equity_curve)):
            returns.append((equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1])
        
        avg_return = sum(returns) / len(returns) if returns else 0
        std_return = math.sqrt(sum((r - avg_return)**2 for r in returns) / len(returns)) if len(returns) > 1 else 1
        sharpe = (avg_return / std_return * math.sqrt(252)) if std_return > 0 else 0
        
        return {
            "strategy": "optimized",
            "initial_capital": capital,
            "final_equity": round(final_equity, 2),
            "total_return": round(total_return, 2),
            "total_trades": len([t for t in trades if t.get("type") == "SELL"]),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": round(win_rate, 1),
            "max_drawdown": round(max_dd, 2),
            "sharpe_ratio": round(sharpe, 2),
            "trades": trades[-10:]  # Last 10 trades
        }
    
    def optimize(self, strategy, candles, param_grid, capital=100000):
        """Optimize strategy parameters"""
        results = []
        
        # Generate parameter combinations
        keys = list(param_grid.keys())
        values = list(param_grid.values())
        combinations = [[]]
        
        for v in values:
            combinations = [c + [item] for c in combinations for item in v]
        
        print(f"Testing {len(combinations)} parameter combinations...")
        
        for combo in combinations[:50]:  # Limit to 50 combinations
            params = dict(zip(keys, combo))
            result = self.backtest(candles, strategy, capital, params)
            result["params"] = params
            results.append(result)
        
        # Sort by total return
        results.sort(key=lambda x: x["total_return"], reverse=True)
        
        return {
            "strategy": strategy,
            "combinations_tested": len(results),
            "best_params": results[0]["params"] if results else {},
            "best_return": results[0]["total_return"] if results else 0,
            "top_results": results[:5]
        }

if __name__ == "__main__":
    optimizer = BacktestOptimizer()
    
    # Generate test data
    candles = optimizer.generate_data(days=300, start_price=100, volatility=0.015)
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "--strategy":
            strategy = sys.argv[2] if len(sys.argv) > 2 else "ma_cross"
            result = optimizer.backtest(candles, strategy=strategy)
            print(json.dumps(result, ensure_ascii=False, indent=2))
        elif cmd == "--optimize":
            strategy = sys.argv[2] if len(sys.argv) > 2 else "ma_cross"
            param_grid = {
                "fast": [5, 10, 15],
                "slow": [20, 30, 50],
                "stop_loss": [0.01, 0.02, 0.03]
            }
            result = optimizer.optimize(strategy, candles, param_grid)
            print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print("SA-BACKTEST-OPTIMIZER-001")
        print("Commands:")
        print("  --strategy <name>   Run backtest")
        print("  --optimize <name>   Optimize parameters")
        print()
        print("Strategies: ma_cross, rsi, bollinger, sma")
        print()
        print("Running default backtest...")
        result = optimizer.backtest(candles, strategy="ma_cross")
        print(json.dumps(result, ensure_ascii=False, indent=2))
       
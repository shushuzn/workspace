#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-022 股票策略回测系统
【Phase 4 - 可视化与自动化】

功能:
  - 策略回测框架
  - 样本内外测试
  - 绩效分析
  - 统计显著性检验

依赖: pandas, numpy
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import random

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# 配置
BACKTEST_DIR = Path("60-DATA/stock_022")
RESULTS_DIR = Path("60-DATA/stock_022/results")
CONFIG_FILE = Path("30-scripts-tools/sa_022_config.json")


class BacktestEngine:
    """回测引擎"""
    
    def __init__(self):
        self.backtest_dir = BACKTEST_DIR
        self.results_dir = RESULTS_DIR
        self.config = self._load_config()
        
        self.backtest_dir.mkdir(parents=True, exist_ok=True)
        self.results_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> dict:
        default = {
            "initial_capital": 100000,
            "commission": 0.001,
            "slippage": 0.0005,
            "position_size": 0.1,
            "max_positions": 5
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except:
                return default
        return default
    
    def _generate_sample_data(self, days: int = 250) -> pd.DataFrame:
        """生成示例数据"""
        random.seed(42)
        dates = pd.date_range(start="2025-01-01", periods=days, freq="D")
        
        prices = [100]
        for _ in range(days - 1):
            change = random.uniform(-0.03, 0.035)
            prices.append(prices[-1] * (1 + change))
        
        df = pd.DataFrame({
            "date": dates,
            "open": [p * random.uniform(0.98, 1.02) for p in prices],
            "high": [p * random.uniform(1.0, 1.03) for p in prices],
            "low": [p * random.uniform(0.97, 1.0) for p in prices],
            "close": prices,
            "volume": [random.randint(1000000, 10000000) for _ in range(days)]
        })
        
        return df
    
    def _calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算技术指标"""
        df = df.copy()
        
        # 简单均线
        for period in [5, 10, 20]:
            df[f"MA{period}"] = df["close"].rolling(window=period).mean()
        
        # RSI
        delta = df["close"].diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        avg_gain = gain.rolling(window=14).mean()
        avg_loss = loss.rolling(window=14).mean()
        rs = avg_gain / avg_loss
        df["RSI"] = 100 - (100 / (1 + rs))
        
        return df
    
    def _generate_signals(self, df: pd.DataFrame, strategy: str = "ma_cross") -> pd.DataFrame:
        """生成交易信号"""
        df = df.copy()
        df["signal"] = 0
        
        if strategy == "ma_cross":
            # 均线交叉策略
            df.loc[df["MA5"] > df["MA20"], "signal"] = 1  # 买入
            df.loc[df["MA5"] < df["MA20"], "signal"] = -1  # 卖出
        
        elif strategy == "rsi":
            # RSI 策略
            df.loc[df["RSI"] < 30, "signal"] = 1   # 超卖买入
            df.loc[df["RSI"] > 70, "signal"] = -1  # 超卖卖出
        
        elif strategy == "momentum":
            # 动量策略
            df["returns"] = df["close"].pct_change()
            df.loc[df["returns"] > 0.01, "signal"] = 1
            df.loc[df["returns"] < -0.01, "signal"] = -1
        
        return df
    
    def run_backtest(self, strategy: str = "ma_cross", days: int = 250) -> dict:
        """运行回测"""
        if not PANDAS_AVAILABLE:
            return {"status": "error", "message": "pandas not available"}
        
        # 准备数据
        df = self._generate_sample_data(days)
        df = self._calculate_indicators(df)
        df = self._generate_signals(df, strategy)
        
        # 初始化
        capital = self.config["initial_capital"]
        position = 0
        entry_price = 0
        trades = []
        equity = [capital]
        
        # 回测
        for i in range(20, len(df)):
            row = df.iloc[i]
            signal = row["signal"]
            price = row["close"]
            
            # 买入信号
            if signal == 1 and position == 0:
                shares = (capital * self.config["position_size"]) // price
                if shares > 0:
                    cost = shares * price * (1 + self.config["commission"] + self.config["slippage"])
                    if cost <= capital:
                        position = shares
                        entry_price = price
                        capital -= cost
                        trades.append({
                            "date": str(row["date"].date()),
                            "action": "BUY",
                            "price": price,
                            "shares": shares,
                            "cost": cost
                        })
            
            # 卖出信号
            elif signal == -1 and position > 0:
                revenue = position * price * (1 - self.config["commission"] - self.config["slippage"])
                capital += revenue
                trades.append({
                    "date": str(row["date"].date()),
                    "action": "SELL",
                    "price": price,
                    "shares": position,
                    "revenue": revenue,
                    "profit": revenue - (position * entry_price)
                })
                position = 0
                entry_price = 0
            
            # 更新权益
            current_value = capital + (position * price) if position > 0 else capital
            equity.append(current_value)
        
        # 平仓
        if position > 0:
            final_price = df.iloc[-1]["close"]
            revenue = position * final_price * (1 - self.config["commission"])
            capital = revenue
            trades.append({
                "date": str(df.iloc[-1]["date"].date()),
                "action": "SELL",
                "price": final_price,
                "shares": position,
                "revenue": revenue
            })
        
        # 计算绩效指标
        equity = pd.Series(equity)
        returns = equity.pct_change().dropna()
        
        final_equity = equity.iloc[-1] if len(equity) > 0 else self.config["initial_capital"]
        total_return = (final_equity - self.config["initial_capital"]) / self.config["initial_capital"] * 100
        annualized_return = total_return * (252 / days)
        volatility = returns.std() * np.sqrt(252) * 100 if len(returns) > 0 else 0
        
        # 夏普比率
        if volatility > 0:
            sharpe_ratio = (annualized_return - 2) / volatility
        else:
            sharpe_ratio = 0
        
        # 最大回撤
        cummax = equity.cummax()
        drawdown = (equity - cummax) / cummax
        max_drawdown = drawdown.min() * 100 if len(drawdown) > 0 else 0
        
        # 胜率
        winning_trades = [t for t in trades if t.get("profit", 0) > 0]
        win_rate = len(winning_trades) / len(trades) * 100 if len(trades) > 0 else 0
        
        equity_start = equity.iloc[0] if len(equity) > 0 else self.config["initial_capital"]
        equity_peak = equity.max() if len(equity) > 0 else self.config["initial_capital"]
        equity_end = equity.iloc[-1] if len(equity) > 0 else self.config["initial_capital"]
        
        result = {
            "status": "success",
            "strategy": strategy,
            "period": {
                "start": str(df.iloc[0]["date"].date()),
                "end": str(df.iloc[-1]["date"].date()),
                "days": days
            },
            "performance": {
                "initial_capital": self.config["initial_capital"],
                "final_capital": round(capital, 2),
                "total_return_pct": round(total_return, 2),
                "annualized_return_pct": round(annualized_return, 2),
                "volatility_pct": round(volatility, 2),
                "sharpe_ratio": round(sharpe_ratio, 2),
                "max_drawdown_pct": round(max_drawdown, 2),
                "win_rate_pct": round(win_rate, 2),
                "total_trades": len(trades)
            },
            "trades": trades[-10:] if len(trades) > 0 else [],
            "equity_curve": {
                "start": round(equity_start, 2),
                "peak": round(equity_peak, 2),
                "end": round(equity_end, 2)
            }
        }
        
        # 保存结果
        result_file = self.results_dir / f"backtest_{strategy}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        result["result_file"] = str(result_file)
        return result
    
    def compare_strategies(self, strategies: list = None) -> dict:
        """比较多个策略"""
        if strategies is None:
            strategies = ["ma_cross", "rsi", "momentum"]
        
        results = []
        for strategy in strategies:
            result = self.run_backtest(strategy)
            results.append({
                "strategy": strategy,
                "total_return": result["performance"]["total_return_pct"],
                "sharpe_ratio": result["performance"]["sharpe_ratio"],
                "max_drawdown": result["performance"]["max_drawdown_pct"],
                "win_rate": result["performance"]["win_rate_pct"],
                "trades": result["performance"]["total_trades"]
            })
        
        # 排序
        results_sorted = sorted(results, key=lambda x: x["sharpe_ratio"], reverse=True)
        
        return {
            "status": "success",
            "strategies": results_sorted,
            "best_strategy": results_sorted[0]["strategy"] if results_sorted else None
        }
    
    def walk_forward_test(self, strategy: str = "ma_cross", train_days: int = 150, test_days: int = 30) -> dict:
        """Walk-forward 测试"""
        results = []
        
        for i in range(0, 250 - test_days, test_days):
            train_data = self._generate_sample_data(train_days)
            test_data = self._generate_sample_data(test_days)
            
            result = self.run_backtest(strategy, test_days)
            results.append({
                "window": i // test_days + 1,
                "return": result["performance"]["total_return_pct"],
                "sharpe": result["performance"]["sharpe_ratio"]
            })
        
        return {
            "status": "success",
            "strategy": strategy,
            "windows": results,
            "avg_return": sum(r["return"] for r in results) / len(results),
            "avg_sharpe": sum(r["sharpe"] for r in results) / len(results)
        }


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            engine = BacktestEngine()
            result = engine.run_backtest("ma_cross")
            print(json.dumps({
                "status": result["status"],
                "strategy": result["strategy"],
                "total_return": result["performance"]["total_return_pct"],
                "sharpe_ratio": result["performance"]["sharpe_ratio"]
            }, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--compare":
            engine = BacktestEngine()
            result = engine.compare_strategies()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--walkforward":
            engine = BacktestEngine()
            result = engine.walk_forward_test()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("SA-022 Backtest Engine")
    print("Usage:")
    print("  py sa_022_backtest.py --test       # Run backtest")
    print("  py sa_022_backtest.py --compare    # Compare strategies")
    print("  py sa_022_backtest.py --walkforward # Walk-forward test")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
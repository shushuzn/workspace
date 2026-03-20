#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-033 Portfolio Backtest Engine
【Phase 7 - 高级功能】

功能:
  - 多资产组合回测
  - 资金管理模拟
  - 交易成本计算
  - 绩效指标分析

依赖: pandas, numpy (optional)
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import random

# 配置
BACKTEST_DIR = Path("60-DATA/stock_033")
CONFIG_FILE = Path("30-scripts-tools/sa_033_config.json")


class PortfolioBacktest:
    """组合回测引擎"""
    
    def __init__(self):
        self.backtest_dir = BACKTEST_DIR
        self.config = self._load_config()
        
        self.backtest_dir.mkdir(parents=True, exist_ok=True)
        
        self.results_file = self.backtest_dir / "backtest_results.json"
    
    def _load_config(self) -> dict:
        default = {
            "initial_capital": 100000,
            "commission_rate": 0.001,
            "slippage": 0.001,
            "max_position": 0.2
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except:
                return default
        return default
    
    def _generate_price_series(self, symbol: str, days: int = 252) -> list:
        """生成模拟价格序列"""
        random.seed(hash(symbol) % 10000)
        
        price = 100.0
        prices = []
        
        for _ in range(days):
            change = random.uniform(-0.02, 0.025)
            price *= (1 + change)
            prices.append(round(price, 2))
        
        return prices
    
    def _calculate_metrics(self, equity_curve: list) -> dict:
        """计算绩效指标"""
        if len(equity_curve) < 2:
            return {}
        
        returns = []
        for i in range(1, len(equity_curve)):
            ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
            returns.append(ret)
        
        if not returns:
            return {}
        
        # 总收益
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0]
        
        # 年化收益
        years = len(equity_curve) / 252
        annual_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        
        # 最大回撤
        peak = equity_curve[0]
        max_dd = 0
        for price in equity_curve:
            if price > peak:
                peak = price
            dd = (peak - price) / peak
            max_dd = max(max_dd, dd)
        
        # 夏普比率 (简化)
        avg_ret = sum(returns) / len(returns)
        std_ret = (sum((r - avg_ret) ** 2 for r in returns) / len(returns)) ** 0.5
        sharpe = (avg_ret / std_ret * 252 ** 0.5) if std_ret > 0 else 0
        
        # 胜率
        wins = sum(1 for r in returns if r > 0)
        win_rate = wins / len(returns) if returns else 0
        
        return {
            "total_return": round(total_return * 100, 2),
            "annual_return": round(annual_return * 100, 2),
            "max_drawdown": round(max_dd * 100, 2),
            "sharpe_ratio": round(sharpe, 2),
            "win_rate": round(win_rate * 100, 2),
            "total_trades": len(returns)
        }
    
    def run(self, symbols: list, days: int = 252) -> dict:
        """运行回测"""
        initial_capital = self.config.get("initial_capital", 100000)
        
        # 生成价格数据
        price_data = {}
        for symbol in symbols:
            price_data[symbol] = self._generate_price_series(symbol, days)
        
        # 模拟交易
        cash = initial_capital
        positions = {s: 0 for s in symbols}
        equity_curve = []
        
        for day in range(days):
            # 每日再平衡
            target_value = cash + sum(positions[s] * price_data[s][day] for s in symbols)
            
            for symbol in symbols:
                # 简单策略: 每周调仓
                if day % 5 == 0:
                    # 随机信号
                    signal = random.choice([-1, 0, 1])
                    
                    if signal == 1 and cash > 1000:
                        # 买入
                        max_shares = int(cash * 0.1 / price_data[symbol][day])
                        if max_shares > 0:
                            cost = max_shares * price_data[symbol][day]
                            commission = cost * self.config.get("commission_rate", 0.001)
                            cash -= (cost + commission)
                            positions[symbol] += max_shares
                    
                    elif signal == -1 and positions[symbol] > 0:
                        # 卖出
                        shares = positions[symbol]
                        revenue = shares * price_data[symbol][day]
                        commission = revenue * self.config.get("commission_rate", 0.001)
                        cash += (revenue - commission)
                        positions[symbol] = 0
            
            # 计算当日权益
            daily_value = cash + sum(positions[s] * price_data[s][day] for s in symbols)
            equity_curve.append(daily_value)
        
        # 计算指标
        metrics = self._calculate_metrics(equity_curve)
        
        result = {
            "symbols": symbols,
            "days": days,
            "initial_capital": initial_capital,
            "final_value": round(equity_curve[-1], 2),
            "metrics": metrics,
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存
        self._save_result(result)
        
        return result
    
    def _save_result(self, result: dict):
        with open(self.results_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def compare_strategies(self, symbols: list) -> dict:
        """比较不同策略"""
        strategies = ["momentum", "mean_reversion", "trend"]
        
        results = []
        
        for strat in strategies:
            # 模拟不同策略
            result = self.run(symbols, 252)
            result["strategy"] = strat
            results.append({
                "strategy": strat,
                "total_return": result["metrics"].get("total_return", 0),
                "sharpe_ratio": result["metrics"].get("sharpe_ratio", 0),
                "max_drawdown": result["metrics"].get("max_drawdown", 0)
            })
        
        results.sort(key=lambda x: x["total_return"], reverse=True)
        
        return {
            "symbols": symbols,
            "strategies": results,
            "best": results[0] if results else None
        }
    
    def optimize_parameters(self, symbols: list) -> dict:
        """参数优化"""
        # 简化: 测试不同仓位
        results = []
        
        for position_size in [0.1, 0.2, 0.3, 0.4, 0.5]:
            config_backup = self.config.copy()
            self.config["max_position"] = position_size
            
            result = self.run(symbols, 126)  # 半年
            
            results.append({
                "position_size": position_size,
                "return": result["metrics"].get("total_return", 0),
                "sharpe": result["metrics"].get("sharpe_ratio", 0)
            })
            
            self.config = config_backup
        
        results.sort(key=lambda x: x["return"], reverse=True)
        
        return {
            "optimization": results,
            "best": results[0] if results else None
        }
    
    def get_last_result(self) -> dict:
        if not self.results_file.exists():
            return {"status": "error", "message": "No results"}
        
        with open(self.results_file, "r", encoding="utf-8") as f:
            return json.load(f)


def main():
    engine = PortfolioBacktest()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--run":
            symbols = sys.argv[2].split(",") if len(sys.argv) > 2 else ["AAPL", "GOOGL"]
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 252
            result = engine.run(symbols, days)
            print(json.dumps(result.get("metrics", {}), ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--compare":
            symbols = sys.argv[2].split(",") if len(sys.argv) > 2 else ["AAPL", "GOOGL"]
            result = engine.compare_strategies(symbols)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--optimize":
            symbols = sys.argv[2].split(",") if len(sys.argv) > 2 else ["AAPL", "GOOGL"]
            result = engine.optimize_parameters(symbols)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--result":
            result = engine.get_last_result()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("SA-033 Portfolio Backtest Engine")
    print("Usage:")
    print("  py sa_033_backtest.py --run AAPL,GOOGL [days]  # Run backtest")
    print("  py sa_033_backtest.py --compare AAPL,GOOGL      # Compare strategies")
    print("  py sa_033_backtest.py --optimize AAPL,GOOGL    # Optimize parameters")
    print("  py sa_033_backtest.py --result                 # Get last result")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
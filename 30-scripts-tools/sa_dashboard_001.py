#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-021 股票监控仪表板
【Phase 4 - 可视化与自动化】

功能:
  - 实时行情监控
  - 持仓监控
  - 告警中心
  - 组合概览
  - Web Dashboard 输出 (JSON/HTML)

依赖: Flask (可选), 可生成静态 HTML
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import random
import subprocess

# 配置
DASHBOARD_DIR = Path("60-DATA/stock_019/dashboard")
CONFIG_FILE = Path("30-scripts-tools/sa_021_config.json")


class StockDashboard:
    """股票监控仪表板"""
    
    def __init__(self):
        self.dashboard_dir = DASHBOARD_DIR
        self.config = self._load_config()
        
        # 确保目录存在
        self.dashboard_dir.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self) -> dict:
        """加载配置"""
        default = {
            "watchlist": ["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA"],
            "refresh_interval": 60,  # 秒
            "alerts": {
                "price_change_threshold": 5.0,  # 价格变动超过 5%
                "volume_spike_threshold": 2.0,  # 成交量超过平均 2 倍
                "rsi_overbought": 70,
                "rsi_oversold": 30
            },
            "dashboard_type": "realtime",
            "output_format": "html"
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except:
                return default
        return default
    
    def _get_mock_realtime_data(self, symbol: str) -> dict:
        """模拟实时数据"""
        base_prices = {
            "AAPL": 185.0,
            "GOOGL": 142.0,
            "MSFT": 415.0,
            "AMZN": 178.0,
            "TSLA": 245.0
        }
        base = base_prices.get(symbol, 100.0)
        
        change = random.uniform(-3, 3)
        current = base + change
        
        return {
            "symbol": symbol,
            "timestamp": datetime.now().isoformat(),
            "price": {
                "current": round(current, 2),
                "change": round(change, 2),
                "change_pct": round(change / base * 100, 2),
                "open": round(base - random.uniform(0, 2), 2),
                "high": round(current + random.uniform(0, 3), 2),
                "low": round(current - random.uniform(0, 3), 2),
                "prev_close": round(base, 2)
            },
            "volume": {
                "current": random.randint(10000000, 50000000),
                "avg_20d": random.randint(20000000, 40000000)
            },
            "indicators": {
                "rsi": round(random.uniform(30, 80), 1),
                "macd_signal": random.choice(["bullish", "bearish", "neutral"]),
                "ma_position": random.choice(["above_ma20", "below_ma20"])
            }
        }
    
    def _check_alerts(self, data: dict) -> list:
        """检查告警"""
        alerts = []
        price = data["price"]
        indicators = data["indicators"]
        
        # 价格变动告警
        if abs(price["change_pct"]) > self.config["alerts"]["price_change_threshold"]:
            alerts.append({
                "type": "price_alert",
                "severity": "high",
                "message": f"{data['symbol']} 价格变动 {price['change_pct']:+.2f}%",
                "timestamp": datetime.now().isoformat()
            })
        
        # RSI 超买超卖
        rsi = indicators["rsi"]
        if rsi > self.config["alerts"]["rsi_overbought"]:
            alerts.append({
                "type": "rsi_alert",
                "severity": "medium",
                "message": f"{data['symbol']} RSI 超买 ({rsi})",
                "timestamp": datetime.now().isoformat()
            })
        elif rsi < self.config["alerts"]["rsi_oversold"]:
            alerts.append({
                "type": "rsi_alert",
                "severity": "medium",
                "message": f"{data['symbol']} RSI 超卖 ({rsi})",
                "timestamp": datetime.now().isoformat()
            })
        
        # 成交量异常
        vol = data["volume"]
        if vol["current"] > vol["avg_20d"] * self.config["alerts"]["volume_spike_threshold"]:
            alerts.append({
                "type": "volume_alert",
                "severity": "medium",
                "message": f"{data['symbol']} 成交量激增",
                "timestamp": datetime.now().isoformat()
            })
        
        return alerts
    
    def get_watchlist_data(self) -> dict:
        """获取监控列表数据"""
        watchlist = self.config.get("watchlist", [])
        
        all_data = []
        all_alerts = []
        
        for symbol in watchlist:
            data = self._get_mock_realtime_data(symbol)
            data["alerts"] = self._check_alerts(data)
            all_data.append(data)
            all_alerts.extend(data["alerts"])
        
        return {
            "timestamp": datetime.now().isoformat(),
            "symbols_count": len(watchlist),
            "watchlist": all_data,
            "total_alerts": len(all_alerts),
            "alerts": all_alerts
        }
    
    def get_portfolio_summary(self) -> dict:
        """获取组合概要"""
        # 模拟持仓
        positions = [
            {"symbol": "AAPL", "shares": 100, "avg_cost": 175.0, "current_price": 185.0},
            {"symbol": "MSFT", "shares": 50, "avg_cost": 380.0, "current_price": 415.0},
            {"symbol": "GOOGL", "shares": 30, "avg_cost": 135.0, "current_price": 142.0}
        ]
        
        total_value = 0
        total_cost = 0
        
        for pos in positions:
            pos["market_value"] = pos["shares"] * pos["current_price"]
            pos["cost_value"] = pos["shares"] * pos["avg_cost"]
            pos["profit_loss"] = pos["market_value"] - pos["cost_value"]
            pos["profit_pct"] = (pos["profit_loss"] / pos["cost_value"]) * 100
            
            total_value += pos["market_value"]
            total_cost += pos["cost_value"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "positions": positions,
            "summary": {
                "total_value": round(total_value, 2),
                "total_cost": round(total_cost, 2),
                "total_profit": round(total_value - total_cost, 2),
                "total_profit_pct": round((total_value - total_cost) / total_cost * 100, 2),
                "positions_count": len(positions)
            }
        }
    
    def generate_html_dashboard(self, data: dict = None) -> str:
        """生成 HTML 仪表板"""
        if data is None:
            data = self.get_watchlist_data()
        
        portfolio = self.get_portfolio_summary()
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Stock Dashboard</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #1a1a2e; color: #eee; padding: 20px; }}
        .header {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }}
        .header h1 {{ color: #00d4ff; }}
        .timestamp {{ color: #888; font-size: 14px; }}
        .grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
        .card {{ background: #16213e; border-radius: 12px; padding: 20px; }}
        .card h2 {{ color: #00d4ff; margin-bottom: 15px; font-size: 18px; }}
        
        .stock-item {{ display: flex; justify-content: space-between; align-items: center; padding: 12px; background: #0f3460; border-radius: 8px; margin-bottom: 10px; }}
        .stock-symbol {{ font-weight: bold; font-size: 16px; }}
        .stock-price {{ font-size: 18px; }}
        .positive {{ color: #00ff88; }}
        .negative {{ color: #ff4757; }}
        
        .alert-item {{ padding: 10px; background: #2d1b1b; border-left: 3px solid #ff4757; margin-bottom: 8px; border-radius: 4px; }}
        .alert-high {{ border-left-color: #ff4757; }}
        .alert-medium {{ border-left-color: #ffa502; }}
        
        .summary-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; }}
        .summary-item {{ background: #0f3460; padding: 15px; border-radius: 8px; text-align: center; }}
        .summary-value {{ font-size: 24px; font-weight: bold; }}
        .summary-label {{ color: #888; font-size: 12px; margin-top: 5px; }}
        
        @media (max-width: 768px) {{ .grid {{ grid-template-columns: 1fr; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Stock Dashboard</h1>
        <div class="timestamp">更新时间: {data['timestamp']}</div>
    </div>
    
    <div class="grid">
        <div class="card">
            <h2>Watchlist ({data['symbols_count']})</h2>
            {''.join(f'''<div class="stock-item">
                <div>
                    <div class="stock-symbol">{d['symbol']}</div>
                    <div style="color:#888;font-size:12px;">Vol: {d['volume']['current']:,}</div>
                </div>
                <div class="stock-price">
                    <div>${d['price']['current']:.2f}</div>
                    <div class="{'positive' if d['price']['change'] >= 0 else 'negative'}">{d['price']['change_pct']:+.2f}%</div>
                </div>
            </div>''' for d in data['watchlist'])}
        </div>
        
        <div class="card">
            <h2>Alerts ({data['total_alerts']})</h2>
            {''.join(f'''<div class="alert-item alert-{a['severity']}">
                <div style="font-weight:bold;">{a['type']}</div>
                <div style="font-size:14px;">{a['message']}</div>
            </div>''' for a in data['alerts']) if data['alerts'] else '<div style="color:#888;">No alerts</div>'}
        </div>
        
        <div class="card">
            <h2>Portfolio Summary</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <div class="summary-value">${portfolio['summary']['total_value']:,.0f}</div>
                    <div class="summary-label">Total Value</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value">${portfolio['summary']['total_cost']:,.0f}</div>
                    <div class="summary-label">Total Cost</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value class="{'positive' if portfolio['summary']['total_profit'] >= 0 else 'negative'}">${portfolio['summary']['total_profit']:,.0f}</div>
                    <div class="summary-label">P/L</div>
                </div>
                <div class="summary-item">
                    <div class="summary-value class="{'positive' if portfolio['summary']['total_profit_pct'] >= 0 else 'negative'}">{portfolio['summary']['total_profit_pct']:+.2f}%</div>
                    <div class="summary-label">Return</div>
                </div>
            </div>
        </div>
        
        <div class="card">
            <h2>Positions</h2>
            {''.join(f'''<div class="stock-item">
                <div>
                    <div class="stock-symbol">{p['symbol']}</div>
                    <div style="color:#888;font-size:12px;">{p['shares']} shares @ ${p['avg_cost']:.2f}</div>
                </div>
                <div class="stock-price">
                    <div>${p['market_value']:,.0f}</div>
                    <div class="{'positive' if p['profit_loss'] >= 0 else 'negative'}">{p['profit_pct']:+.2f}%</div>
                </div>
            </div>''' for p in portfolio['positions'])}
        </div>
    </div>
</body>
</html>"""
        
        return html
    
    def save_dashboard(self, data: dict = None, format: str = "html") -> dict:
        """保存仪表板"""
        if data is None:
            data = self.get_watchlist_data()
        
        portfolio = self.get_portfolio_summary()
        
        if format == "html":
            html = self.generate_html_dashboard(data)
            filepath = self.dashboard_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(html)
            
            return {
                "status": "success",
                "format": "html",
                "file_path": str(filepath),
                "watchlist_count": data["symbols_count"],
                "alerts_count": data["total_alerts"],
                "portfolio_value": portfolio["summary"]["total_value"]
            }
        
        elif format == "json":
            combined = {
                "timestamp": data["timestamp"],
                "watchlist": data,
                "portfolio": portfolio
            }
            
            filepath = self.dashboard_dir / f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(combined, f, ensure_ascii=False, indent=2)
            
            return {
                "status": "success",
                "format": "json",
                "file_path": str(filepath)
            }
        
        return {"status": "error", "message": "Unsupported format"}


def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            dashboard = StockDashboard()
            result = dashboard.save_dashboard(format="html")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--json":
            dashboard = StockDashboard()
            result = dashboard.save_dashboard(format="json")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--watchlist":
            dashboard = StockDashboard()
            result = dashboard.get_watchlist_data()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--portfolio":
            dashboard = StockDashboard()
            result = dashboard.get_portfolio_summary()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("SA-021 Stock Dashboard")
    print("Usage:")
    print("  py sa_021_dashboard.py --test      # Generate dashboard")
    print("  py sa_021_dashboard.py --json      # Generate JSON dashboard")
    print("  py sa_021_dashboard.py --watchlist # Get watchlist data")
    print("  py sa_021_dashboard.py --portfolio # Get portfolio summary")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
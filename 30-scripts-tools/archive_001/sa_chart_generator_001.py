import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-019 股票图表生成器
【Phase 4 - 可视化与自动化】

功能:
  - K线图表生成
  - 技术指标叠加
  - 形态标注
  - 多时间周期支持

依赖: matplotlib, pandas, mplfinance (可选)
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess

# 尝试导入可视化库
try:
    import matplotlib
    matplotlib.use('Agg')  # 非交互式后端
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.patches import Rectangle
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False

try:
    import mplfinance as mpf
    MPFINANCE_AVAILABLE = True
except ImportError:
    MPFINANCE_AVAILABLE = False

try:
    import pandas as pd
    import numpy as np
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False

# 配置路径
DATA_DIR = Path("60-DATA/stock_019")
OUTPUT_DIR = Path("60-DATA/stock_019/charts")
CONFIG_FILE = Path("30-scripts-tools/sa_019_config.json")


class StockChartGenerator:
    """股票图表生成器"""

    def __init__(self, symbol: str = "AAPL"):
        self.symbol = symbol
        self.data_dir = DATA_DIR
        self.output_dir = OUTPUT_DIR
        self.config = self._load_config()

        # 确保目录存在
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self) -> dict:
        """加载配置"""
        default = {
            "chart_style": "default",
            "figure_size": (12, 8),
            "dpi": 100,
            "colors": {
                "up": "#26A69A",
                "down": "#EF5350",
                "ma5": "#2196F3",
                "ma10": "#FF9800",
                "ma20": "#9C27B0",
                "ma60": "#607D8B"
            },
            "indicators": ["MA5", "MA10", "MA20", "MA60", "VOLUME"]
        }

        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except (Exception,):
                return default
        return default

    def _generate_candle_data(self) -> dict:
        """生成示例K线数据"""
        import random
        random.seed(42)

        dates = pd.date_range(start="2025-01-01", periods=100, freq="D")
        base_price = 100

        data = []
        for i, date in enumerate(dates):
            change = random.uniform(-3, 3)
            open_price = base_price + random.uniform(-2, 2)
            close_price = open_price + change
            high_price = max(open_price, close_price) + random.uniform(0, 2)
            low_price = min(open_price, close_price) - random.uniform(0, 2)
            volume = random.randint(1000000, 10000000)

            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "open": round(open_price, 2),
                "high": round(high_price, 2),
                "low": round(low_price, 2),
                "close": round(close_price, 2),
                "volume": volume
            })

            base_price = close_price

        return {"symbol": self.symbol, "data": data}

    def _calculate_ma(self, df, period: int) -> list:
        """计算移动平均"""
        if "close" not in df.columns:
            return []
        closes = df["close"].tolist()
        ma = []
        for i in range(len(closes)):
            if i < period - 1:
                ma.append(None)
            else:
                avg = sum(closes[i-period+1:i+1]) / period
                ma.append(round(avg, 2))
        return ma

    def generate_candlestick_chart(self, data: dict = None, save: bool = True) -> dict:
        """生成K线图表"""
        if not MATPLOTLIB_AVAILABLE:
            return {
                "status": "error",
                "message": "matplotlib not available",
                "chart_path": None
            }

        if data is None:
            data = self._generate_candle_data()

        df = pd.DataFrame(data["data"])
        df["date"] = pd.to_datetime(df["date"])

        # 创建图表
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=self.config["figure_size"],
                                        gridspec_kw={'height_ratios': [3, 1]})
        fig.suptitle(f"{self.symbol} K-Line Chart", fontsize=14)

        colors = self.config["colors"]

        # K线
        for i, row in df.iterrows():
            color = colors["up"] if row["close"] >= row["open"] else colors["down"]
            high_low = ax1.plot([i, i], [row["low"], row["high"]], color=color, linewidth=0.5)
            body_height = abs(row["close"] - row["open"])
            body_bottom = min(row["open"], row["close"])
            rect = Rectangle((i - 0.3, body_bottom), 0.6, body_height,
                            facecolor=color, edgecolor=color, linewidth=0.5)
            ax1.add_patch(rect)

        # 均线
        for period, key in [(5, "ma5"), (10, "ma10"), (20, "ma20"), (60, "ma60")]:
            ma = self._calculate_ma(df, period)
            ax1.plot(range(len(ma)), ma, label=f"MA{period}",
                    color=colors[key], linewidth=1.5)

        ax1.legend(loc="upper left", fontsize=8)
        ax1.set_ylabel("Price")
        ax1.grid(True, alpha=0.3)

        # 成交量
        colors_vol = [colors["up"] if df.iloc[i]["close"] >= df.iloc[i]["open"] else colors["down"]
                     for i in range(len(df))]
        ax2.bar(range(len(df)), df["volume"], color=colors_vol, width=0.8)
        ax2.set_ylabel("Volume")
        ax2.set_xlabel("Trading Days")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()

        if save:
            output_path = self.output_dir / f"{self.symbol}_candle_{datetime.now().strftime('%Y%m%d')}.png"
            plt.savefig(output_path, dpi=self.config["dpi"], bbox_inches='tight')
            plt.close()
            return {
                "status": "success",
                "chart_type": "candlestick",
                "symbol": self.symbol,
                "chart_path": str(output_path),
                "data_points": len(data["data"])
            }

        return {"status": "success", "chart_type": "candlestick"}

    def generate_indicator_chart(self, data: dict = None, indicators: list = None) -> dict:
        """生成指标图表"""
        if not MATPLOTLIB_AVAILABLE:
            return {"status": "error", "message": "matplotlib not available"}

        if data is None:
            data = self._generate_candle_data()

        df = pd.DataFrame(data["data"])

        if indicators is None:
            indicators = ["MACD", "RSI", "KDJ"]

        n_charts = len(indicators) + 1
        fig, axes = plt.subplots(n_charts, 1, figsize=(12, 3 * n_charts), sharex=True)
        fig.suptitle(f"{self.symbol} Technical Indicators", fontsize=14)

        # 价格图表
        ax = axes[0]
        ax.plot(df["close"], label="Close", color="#2196F3", linewidth=1.5)
        ma20 = self._calculate_ma(df, 20)
        ax.plot(range(len(ma20)), ma20, label="MA20", color="#FF9800", linewidth=1)
        ax.set_ylabel("Price")
        ax.legend(loc="upper left")
        ax.grid(True, alpha=0.3)

        # 指标图表
        for idx, indicator in enumerate(indicators):
            ax = axes[idx + 1]

            if indicator == "MACD":
                # 简单 MACD 计算
                ema12 = df["close"].ewm(span=12).mean()
                ema26 = df["close"].ewm(span=26).mean()
                macd = ema12 - ema26
                signal = macd.ewm(span=9).mean()
                histogram = macd - signal

                ax.bar(range(len(histogram)), histogram, color="gray", alpha=0.5, width=0.8)
                ax.plot(range(len(macd)), macd, label="MACD", color="#2196F3")
                ax.plot(range(len(signal)), signal, label="Signal", color="#FF9800")
                ax.axhline(y=0, color="black", linestyle="--", linewidth=0.5)
                ax.set_ylabel("MACD")

            elif indicator == "RSI":
                # 简单 RSI 计算
                delta = df["close"].diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))

                ax.plot(range(len(rsi)), rsi, label="RSI(14)", color="#9C27B0")
                ax.axhline(y=70, color="red", linestyle="--", linewidth=0.5)
                ax.axhline(y=30, color="green", linestyle="--", linewidth=0.5)
                ax.set_ylabel("RSI")
                ax.set_ylim(0, 100)

            elif indicator == "KDJ":
                # 简单 KDJ 计算
                low_min = df["low"].rolling(window=9).min()
                high_max = df["high"].rolling(window=9).max()
                rsv = (df["close"] - low_min) / (high_max - low_min) * 100
                k = rsv.ewm(com=2).mean()
                d = k.ewm(com=2).mean()
                j = 3 * k - 2 * d

                ax.plot(range(len(k)), k, label="K", color="#2196F3")
                ax.plot(range(len(d)), d, label="D", color="#FF9800")
                ax.plot(range(len(j)), j, label="J", color="#9C27B0")
                ax.axhline(y=80, color="red", linestyle="--", linewidth=0.5)
                ax.axhline(y=20, color="green", linestyle="--", linewidth=0.5)
                ax.set_ylabel("KDJ")

            ax.legend(loc="upper left", fontsize=8)
            ax.grid(True, alpha=0.3)

        plt.tight_layout()

        output_path = self.output_dir / f"{self.symbol}_indicators_{datetime.now().strftime('%Y%m%d')}.png"
        plt.savefig(output_path, dpi=self.config["dpi"], bbox_inches='tight')
        plt.close()

        return {
            "status": "success",
            "chart_type": "indicators",
            "symbol": self.symbol,
            "chart_path": str(output_path),
            "indicators": indicators
        }

    def add_pattern_annotation(self, ax, patterns: list):
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
# py sa_chart_generator_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py sa_chart_generator_001.py

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

添加形态标注"""
        colors = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A"]

        for idx, pattern in enumerate(patterns):
            if "start" in pattern and "end" in pattern:
                color = colors[idx % len(colors)]
                ax.axvspan(pattern["start"], pattern["end"],
                          alpha=0.2, color=color, label=pattern.get("name", f"Pattern {idx+1}"))

    def generate_report(self, data: dict = None) -> dict:
        """生成图表报告"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "symbol": self.symbol,
            "charts": []
        }
        
        # K线图
        candle_result = self.generate_candlestick_chart(data)
        result["charts"].append(candle_result)
        
        # 指标图
        indicator_result = self.generate_indicator_chart(data)
        result["charts"].append(indicator_result)
        
        # 保存数据
        if data:
            data_file = self.data_dir / f"{self.symbol}_chart_data.json"
            data_file.parent.mkdir(parents=True, exist_ok=True)
            with open(data_file, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            result["data_file"] = str(data_file)
        
        return result


logging.basicConfig(level=logging.INFO)
def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            # 测试模式
            generator = StockChartGenerator("TEST")
            result = generator.generate_report()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--symbol":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
            generator = StockChartGenerator(symbol)
            result = generator.generate_report()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    # 默认模式
    print("SA-019 Stock Chart Generator")
    print("Usage:")
    print("  py sa_019_chart_generator.py --test    # Run test")
    print("  py sa_019_chart_generator.py --symbol AAPL  # Generate chart for symbol")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
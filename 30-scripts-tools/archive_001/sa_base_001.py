#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
股票分析工具 - 基类 v2.0
统一日志、配置、错误处理
"""

import json
import sys
import logging
from pathlib import Path
from datetime import datetime

if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')


class SA_Config:
    """统一配置管理"""

    def __init__(self, name, defaults=None):
        self.name = name
        self.data_dir = Path(r"D:\OpenClaw\workspace\.openclaw\stock_analysis\data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        self.defaults = defaults or {}
        self.config = self._load()

    def _load(self):
        config_file = self.data_dir / f"{self.name}_config.json"
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return {**self.defaults, **json.load(f)}
        return self.defaults

    def save(self, key, value):
        self.config[key] = value
        config_file = self.data_dir / f"{self.name}_config.json"
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def get(self, key, default=None):
        return self.config.get(key, default)


class SA_Logger:
    """统一日志管理"""

    def __init__(self, name):
        self.name = name
        self.data_dir = Path(r"D:\OpenClaw\workspace\.openclaw\stock_analysis\data")
        self.data_dir.mkdir(parents=True, exist_ok=True)

        log_file = self.data_dir / f"{name}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s [%(levelname)s] %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(name)

    def info(self, msg):
        self.logger.info(msg)

    def warning(self, msg):
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.error(msg)


class SA_Base:
    """股票分析工具基类"""

    def __init__(self, name, defaults=None):
        self.name = name
        self.config = SA_Config(name, defaults)
        self.logger = SA_Logger(name)
        self.data_dir = self.config.data_dir

    def retry(self, func, *args, retries=3, delay=1, **kwargs):
        """重试装饰器"""
        for i in range(retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                self.logger.warning(f"Retry {i +1}/{retries}: {e}")
                if i < retries - 1:
                    import time
                    time.sleep(delay)
        return None

    def save_json(self, data, filename):
        """保存JSON"""
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp = self.data_dir / f"{filename}_{ts}.json"
        with open(fp, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        self.logger.info(f"Saved: {fp.name}")
        return fp

    def save_csv(self, data, filename):
        """保存CSV"""
        import csv
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fp = self.data_dir / f"{filename}_{ts}.csv"
        if data:
            with open(fp, 'w', encoding='utf-8-sig', newline='') as f:
                w = csv.DictWriter(f, fieldnames=list(data[0].keys()))
                w.writeheader()
                w.writerows(data)
            self.logger.info(f"CSV: {fp.name}")
        return fp

    def load_json(self, filename):
        """读取JSON"""
        # 找到最新的文件
        files = sorted(self.data_dir.glob(f"{filename}*.json"), reverse=True)
        if files:
            with open(files[0], 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

    def format_result(self, status, data, message=""):
        """统一返回格式"""
        return {
            "status": status,
            "data": data,
            "message": message,
            "meta": {
                "tool": self.name,
                "created_at": datetime.now().isoformat(),
                "version": "2.0"
            }
        }


# ========== 具体工具示例 ==========

class SA_Strategy(SA_Base):
    """策略推荐"""

    def __init__(self):
        super().__init__("strategy", {
            "risk_free_rate": 0.03,
            "trading_days": 252
        })

    def recommend(self, risk_level="moderate", *args):
        """推荐策略"""
        self.logger.info(f"Risk level: {risk_level}")

        strategies = {
            "conservative": {
                "name": "保守型",
                "max_drawdown": 0.05,
                "expected_return": 0.08
            },
            "moderate": {
                "name": "稳健型",
                "max_drawdown": 0.10,
                "expected_return": 0.15
            },
            "aggressive": {
                "name": "激进型",
                "max_drawdown": 0.20,
                "expected_return": 0.25
            }
        }

        strategy = strategies.get(risk_level, strategies["moderate"])
        return self.format_result("success", strategy)


class SA_Analyzer(SA_Base):
    """分析器"""

    def __init__(self):
        super().__init__("analyzer")

    def analyze(self, symbol="AAPL", *args):
        """分析股票"""
        self.logger.info(f"Analyzing: {symbol}")

        # 模拟分析结果
        result = {
            "symbol": symbol,
            "price": 100.0,
            "change": 2.5,
            "change_pct": 2.5
        }

        return self.format_result("success", result)


class SA_Backtest(SA_Base):
    """回测"""

    def __init__(self):
        super().__init__("backtest")

    def run(self, strategy="ma_cross", start_date="2024-01-01", end_date="2024-12-31", *args):
        """运行回测"""
        self.logger.info(f"Backtest: {strategy} {start_date} - {end_date}")

        result = {
            "strategy": strategy,
            "start_date": start_date,
            "end_date": end_date,
            "total_return": 15.5,
            "sharpe_ratio": 1.2,
            "max_drawdown": 8.5
        }

        return self.format_result("success", result)


# ========== 统一入口 ==========

class SA_Main:
    """股票分析统一入口"""

    def __init__(self):
        self.tools = {
            "strategy": SA_Strategy(),
            "analyzer": SA_Analyzer(),
            "backtest": SA_Backtest()
        }

    def run(self, tool, action, *args, **kwargs):
        """执行工具"""
        if tool not in self.tools:
            return {"status": "error", "message": f"Unknown tool: {tool}"}

        t = self.tools[tool]

        if hasattr(t, action):
            func = getattr(t, action)
            return func(*args, **kwargs)

        return {"status": "error", "message": f"Unknown action: {action}"}

    def list_tools(self):
        """列出所有工具"""
        return {
            "tools": list(self.tools.keys())
        }


def main():
    print("=" * 60)
    print("股票分析工具 v2.0 (整合版)")
    print("=" * 60)

    main_tool = SA_Main()

    if len(sys.argv) < 2:
        print("\n用法: py sa_base_001.py <工具> <操作> [参数]")
        print("\n可用工具:")
        print("  strategy          策略推荐")
        print("  analyzer         股票分析")
        print("  backtest         回测")
        print("\n示例:")
        print("  py sa_base_001.py strategy recommend moderate")
        print("  py sa_base_001.py analyzer analyze AAPL")
        print("  py sa_base_001.py backtest run ma_cross 2024-01-01 2024-12-31")
        return

    tool = sys.argv[1] if len(sys.argv) > 1 else "help"
    action = sys.argv[2] if len(sys.argv) > 2 else "run"
    args = sys.argv[3:] if len(sys.argv) > 3 else []

    if tool == "help":
        print("\n用法: py sa_base_001.py <工具> <操作> [参数]")
        print("\n可用工具:")
        for t in main_tool.tools:
            print(f"  {t}")
        return

    result = main_tool.run(tool, action, *args)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

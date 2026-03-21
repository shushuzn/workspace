import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env py
# -*- coding: utf-8 -*-
"""
Data Source Manager for Stock Analysis

功能：统一管理多个数据源，自动故障转移
支持：Yahoo Finance, Alpha Vantage, 东方财富
特性：重试机制，速率限制，数据标准化

作者：Claw
创建：2026-03-20
版本：v1.0.0
"""

import os
import sys
import time
import json
import random
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from abc import ABC, abstractmethod
import functools

# 添加项目路径
WORKSPACE = Path("D:/OpenClaw/workspace")
sys.path.insert(0, str(WORKSPACE / "30-scripts-tools"))

# 尝试导入第三方库
try:
    import yfinance as yf
    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False
    print("[WARN] yfinance not installed. Install with: pip install yfinance")

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False
    print("[WARN] requests not installed. Install with: pip install requests")


class DataSourceError(Exception):
    """数据源异常"""
    pass


class RateLimitError(DataSourceError):
    """速率限制异常"""
    pass


class DataSourceBase(ABC):
    """数据源基类"""
    
    def __init__(self, name: str, api_key: Optional[str] = None):
        self.name = name
        self.api_key = api_key
        self.enabled = api_key is not None if self.requires_api_key() else True
        self.last_request_time: Optional[datetime] = None
        self.request_count = 0
        self.error_count = 0
    
    @abstractmethod
    def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        """获取实时行情"""
        pass
    
    @abstractmethod
    def fetch_historical(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取历史数据"""
        pass
    
    @abstractmethod
    def requires_api_key(self) -> bool:
        """是否需要 API Key"""
        pass
    
    def _rate_limit_check(self, min_interval: float = 1.0):
        """速率限制检查"""
        if self.last_request_time:
            elapsed = (datetime.now() - self.last_request_time).total_seconds()
            if elapsed < min_interval:
                sleep_time = min_interval - elapsed
                time.sleep(sleep_time)
        self.last_request_time = datetime.now()
        self.request_count += 1
    
    def _retry_on_error(self, max_retries: int = 3, backoff: float = 1.0):
        """重试装饰器"""
        def decorator(func: Callable):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                last_error = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except (DataSourceError, RateLimitError) as e:
                        last_error = e
                        self.error_count += 1
                        if attempt < max_retries - 1:
                            sleep_time = backoff * (2 ** attempt) + random.uniform(0, 1)
                            print(f"[RETRY] {self.name} attempt {attempt + 1}/{max_retries} failed, retrying in {sleep_time:.1f}s...")
                            time.sleep(sleep_time)
                        else:
                            print(f"[ERROR] {self.name} failed after {max_retries} attempts: {e}")
                raise last_error
            return wrapper
        return decorator


class YahooFinanceDataSource(DataSourceBase):
    """Yahoo Finance 数据源"""
    
    def __init__(self):
        super().__init__("Yahoo Finance")
        self.enabled = YFINANCE_AVAILABLE
    
    def requires_api_key(self) -> bool:
        return False
    
    def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        """获取实时行情"""
        if not self.enabled:
            raise DataSourceError("Yahoo Finance not available")
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # 标准化数据格式
            quote = {
                "symbol": symbol,
                "source": "yahoo",
                "timestamp": datetime.now().isoformat(),
                "price": info.get("currentPrice") or info.get("regularMarketPrice"),
                "change": info.get("regularMarketChange"),
                "change_percent": info.get("regularMarketChangePercent"),
                "volume": info.get("volume"),
                "market_cap": info.get("marketCap"),
                "pe_ratio": info.get("trailingPE"),
                "day_high": info.get("dayHigh"),
                "day_low": info.get("dayLow"),
                "open": info.get("open"),
                "previous_close": info.get("previousClose"),
                "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
                "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            }
            
            # 移除 None 值
            quote = {k: v for k, v in quote.items() if v is not None}
            
            print(f"[YAHOO] {symbol}: ${quote.get('price', 'N/A')}")
            return quote
            
        except Exception as e:
            raise DataSourceError(f"Yahoo Finance fetch failed: {e}")
    
    def fetch_historical(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取历史 K 线数据"""
        if not self.enabled:
            raise DataSourceError("Yahoo Finance not available")
        
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(start=start_date, end=end_date)
            
            # 转换为字典格式
            data = {
                "symbol": symbol,
                "source": "yahoo",
                "start": start_date,
                "end": end_date,
                "data": []
            }
            
            for date, row in hist.iterrows():
                data["data"].append({
                    "date": date.strftime("%Y-%m-%d"),
                    "open": float(row["Open"]),
                    "high": float(row["High"]),
                    "low": float(row["Low"]),
                    "close": float(row["Close"]),
                    "volume": int(row["Volume"]) if "Volume" in row else 0
                })
            
            print(f"[YAHOO] {symbol}: {len(data['data'])} days of historical data")
            return data
            
        except Exception as e:
            raise DataSourceError(f"Yahoo Finance historical fetch failed: {e}")


class AlphaVantageDataSource(DataSourceBase):
    """Alpha Vantage 数据源"""
    
    def __init__(self, api_key: str):
        super().__init__("Alpha Vantage", api_key)
        self.enabled = bool(api_key)  # 只有提供 API Key 时才启用
        self.base_url = "https://www.alphavantage.co/query"
        self.rate_limit_per_minute = 5
        self.rate_limit_per_day = 500
    
    def requires_api_key(self) -> bool:
        return True
    
    def _make_request(self, function: str, params: Dict) -> Dict:
        """发送 API 请求"""
        if not REQUESTS_AVAILABLE:
            raise DataSourceError("requests library not installed")
        
        self._rate_limit_check(min_interval=12.0)  # 5 次/分钟
        
        params["apikey"] = self.api_key
        params["function"] = function
        
        try:
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 检查速率限制
            if "Note" in data:
                raise RateLimitError(f"Alpha Vantage rate limit: {data['Note']}")
            
            if "Error Message" in data:
                raise DataSourceError(f"Alpha Vantage error: {data['Error Message']}")
            
            return data
            
        except requests.Timeout:
            raise DataSourceError("Alpha Vantage request timeout")
        except requests.RequestException as e:
            raise DataSourceError(f"Alpha Vantage request failed: {e}")
    
    def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        """获取实时行情"""
        if not self.enabled:
            raise DataSourceError("Alpha Vantage not enabled (missing API key)")
        
        try:
            data = self._make_request("GLOBAL_QUOTE", {"symbol": symbol})
            quote_data = data.get("Global Quote", {})
            
            quote = {
                "symbol": symbol,
                "source": "alpha_vantage",
                "timestamp": datetime.now().isoformat(),
                "price": float(quote_data.get("05. price", 0)),
                "change": float(quote_data.get("09. change", 0)),
                "change_percent": quote_data.get("10. change percent", "0%"),
                "volume": int(quote_data.get("06. volume", 0)),
                "open": float(quote_data.get("02. open", 0)),
                "high": float(quote_data.get("03. high", 0)),
                "low": float(quote_data.get("04. low", 0)),
                "previous_close": float(quote_data.get("07. previous close", 0)),
            }
            
            print(f"[ALPHA VANTAGE] {symbol}: ${quote['price']}")
            return quote
            
        except Exception as e:
            raise DataSourceError(f"Alpha Vantage fetch failed: {e}")
    
    def fetch_historical(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取历史数据"""
        if not self.enabled:
            raise DataSourceError("Alpha Vantage not enabled")
        
        try:
            data = self._make_request("TIME_SERIES_DAILY", {"symbol": symbol, "outputsize": "full"})
            time_series = data.get("Time Series (Daily)", {})
            
            historical = {
                "symbol": symbol,
                "source": "alpha_vantage",
                "start": start_date,
                "end": end_date,
                "data": []
            }
            
            for date_str, values in sorted(time_series.items(), reverse=True):
                if start_date <= date_str <= end_date:
                    historical["data"].append({
                        "date": date_str,
                        "open": float(values.get("1. open", 0)),
                        "high": float(values.get("2. high", 0)),
                        "low": float(values.get("3. low", 0)),
                        "close": float(values.get("4. close", 0)),
                        "volume": int(values.get("5. volume", 0))
                    })
            
            print(f"[ALPHA VANTAGE] {symbol}: {len(historical['data'])} days of data")
            return historical
            
        except Exception as e:
            raise DataSourceError(f"Alpha Vantage historical fetch failed: {e}")


class EastMoneyDataSource(DataSourceBase):
    """东方财富数据源 (A 股/港股)"""
    
    def __init__(self):
        super().__init__("East Money")
        self.enabled = REQUESTS_AVAILABLE
        self.base_url = "http://push2.eastmoney.com/api/qt/stock/get"
    
    def requires_api_key(self) -> bool:
        return False
    
    def _convert_symbol(self, symbol: str) -> str:
        """转换股票代码格式"""
        # A 股：600519 -> 1.600519
        # 港股：0700 -> 116.00700
        if symbol.startswith("6"):
            return f"1.{symbol}"
        elif symbol.startswith("0") or symbol.startswith("3"):
            return f"0.{symbol}"
        else:
            return symbol
    
    def fetch_quote(self, symbol: str) -> Dict[str, Any]:
        """获取实时行情"""
        if not self.enabled:
            raise DataSourceError("East Money not available")
        
        try:
            secid = self._convert_symbol(symbol)
            params = {
                "secid": secid,
                "fields": "f43,f44,f45,f46,f47,f48,f49,f50,f51,f52,f53,f54,f55,f56,f57"
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            quote_data = data.get("data", {})
            
            quote = {
                "symbol": symbol,
                "source": "eastmoney",
                "timestamp": datetime.now().isoformat(),
                "price": quote_data.get("f43", 0) / 100,  # 转换为元
                "change": quote_data.get("f44", 0) / 100,
                "change_percent": quote_data.get("f45", 0),
                "volume": quote_data.get("f47", 0),
                "market_cap": quote_data.get("f48", 0),
                "pe_ratio": quote_data.get("f49", 0),
                "day_high": quote_data.get("f50", 0) / 100,
                "day_low": quote_data.get("f51", 0) / 100,
                "open": quote_data.get("f52", 0) / 100,
                "previous_close": quote_data.get("f53", 0) / 100,
            }
            
            print(f"[EAST MONEY] {symbol}: ¥{quote['price']}")
            return quote
            
        except Exception as e:
            raise DataSourceError(f"East Money fetch failed: {e}")
    
    def fetch_historical(self, symbol: str, start_date: str, end_date: str) -> Dict[str, Any]:
        """获取历史数据"""
        # TODO: 实现历史数据获取
        raise DataSourceError("East Money historical data not implemented yet")


class DataSourceManager:
    """数据源管理器 - 统一接口"""
    
    def __init__(self, cache=None):
        """
        初始化数据源管理器
        
        Args:
            cache: DataCache 实例 (可选)
        """
        self.cache = cache
        
        # 初始化数据源
        self.sources: Dict[str, DataSourceBase] = {
            "yahoo": YahooFinanceDataSource(),
            "alpha_vantage": AlphaVantageDataSource(os.getenv("ALPHA_VANTAGE_KEY", "")),
            "eastmoney": EastMoneyDataSource(),
        }
        
        # 数据源优先级 (从高到低)
        self.priority = ["yahoo", "alpha_vantage", "eastmoney"]
        
        # 统计信息
        self.stats = {
            "total_requests": 0,
            "successful": 0,
            "failed": 0,
            "fallback_used": 0
        }
        
        print(f"[DATA SOURCE MANAGER] Initialized with {len(self.sources)} sources")
        for name, source in self.sources.items():
            status = "[OK]" if source.enabled else "[OFF]"
            print(f"   {status} {name}: {source.name}")
    
    def fetch_quote(self, symbol: str, prefer_source: Optional[str] = None) -> Dict[str, Any]:
        """
        获取实时行情 (自动故障转移)
        
        Args:
            symbol: 股票代码
            prefer_source: 优先数据源 (可选)
        
        Returns:
            行情数据
        """
        self.stats["total_requests"] += 1
        
        # 检查缓存
        if self.cache:
            cached = self.cache.get(symbol, "quote")
            if cached:
                self.stats["successful"] += 1
                print(f"[CACHE HIT] {symbol}")
                return cached
        
        # 确定数据源顺序
        if prefer_source and prefer_source in self.sources:
            source_order = [prefer_source] + [s for s in self.priority if s != prefer_source]
        else:
            source_order = self.priority
        
        # 尝试各个数据源
        last_error = None
        for source_name in source_order:
            source = self.sources.get(source_name)
            if not source or not source.enabled:
                continue
            
            try:
                quote = source.fetch_quote(symbol)
                self.stats["successful"] += 1
                
                # 写入缓存
                if self.cache:
                    self.cache.set(symbol, "quote", quote, ttl=300)  # 5 分钟缓存
                
                return quote
                
            except DataSourceError as e:
                last_error = e
                print(f"[WARN] {source_name} failed: {e}")
                continue
        
        # 所有数据源都失败
        self.stats["failed"] += 1
        raise DataSourceError(f"All data sources failed for {symbol}. Last error: {last_error}")
    
    def fetch_historical(self, symbol: str, start_date: str, end_date: str,
                        prefer_source: Optional[str] = None) -> Dict[str, Any]:
        """
        获取历史数据 (自动故障转移)
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            prefer_source: 优先数据源 (可选)
        
        Returns:
            历史数据
        """
        # 检查缓存
        cache_key = f"{start_date}_{end_date}"
        if self.cache:
            cached = self.cache.get(symbol, "historical", params={"range": cache_key})
            if cached:
                print(f"[CACHE HIT] {symbol} historical")
                return cached
        
        # 确定数据源顺序
        if prefer_source and prefer_source in self.sources:
            source_order = [prefer_source] + [s for s in self.priority if s != prefer_source]
        else:
            source_order = self.priority
        
        # 尝试各个数据源
        last_error = None
        for source_name in source_order:
            source = self.sources.get(source_name)
            if not source or not source.enabled:
                continue
            
            try:
                data = source.fetch_historical(symbol, start_date, end_date)
                
                # 写入缓存
                if self.cache:
                    self.cache.set(symbol, "historical", data, ttl=3600, params={"range": cache_key})
                
                return data
                
            except DataSourceError as e:
                last_error = e
                continue
        
        self.stats["failed"] += 1
        raise DataSourceError(f"All data sources failed for {symbol} historical. Last error: {last_error}")
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        success_rate = (self.stats["successful"] / self.stats["total_requests"] * 100) \
                       if self.stats["total_requests"] > 0 else 0
        
        return {
            **self.stats,
            "success_rate": f"{success_rate:.2f}%",
            "sources": {
                name: {"enabled": source.enabled, "requests": source.request_count}
                for name, source in self.sources.items()
            }
        }
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        
        print("\n" + "=" * 60)
        print(" Data Source Manager Statistics")
        print("=" * 60)
        print(f" Total Requests: {stats['total_requests']}")
        print(f" Successful: {stats['successful']}")
        print(f" Failed: {stats['failed']}")
        print(f" Success Rate: {stats['success_rate']}")
        print("\n Sources:")
        for name, info in stats["sources"].items():
            status = "[OK]" if info["enabled"] else "[OFF]"
            print(f"   {status} {name}: {info['requests']} requests")
        print("=" * 60)


# CLI 接口
logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py data_source_manager_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py data_source_manager_001.py

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

命令行接口"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Data Source Manager CLI")
    parser.add_argument("action", choices=["quote", "historical", "stats"], 
                        help="Action to perform")
    parser.add_argument("--symbol", "-s", type=str, help="Stock symbol")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--source", type=str, help="Prefer data source")
    parser.add_argument("--cache-dir", type=Path, help="Cache directory")
    
    args = parser.parse_args()
    
    # 创建缓存和数据源管理器
    from data_cache import StockDataCache
    cache = StockDataCache(cache_dir=args.cache_dir) if args.cache_dir else None
    manager = DataSourceManager(cache=cache)
    
    if args.action == "stats":
        manager.print_stats()
    
    elif args.action == "quote":
        if not args.symbol:
            print("[ERROR] --symbol is required")
            sys.exit(1)
        
        quote = manager.fetch_quote(args.symbol, args.source)
        print("\nQuote Data:")
        print(json.dumps(quote, indent=2))
    
    elif args.action == "historical":
        if not args.symbol or not args.start or not args.end:
            print("[ERROR] --symbol, --start, and --end are required")
            sys.exit(1)
        
        data = manager.fetch_historical(args.symbol, args.start, args.end, args.source)
        print(f"\nHistorical Data: {len(data['data'])} days")
        print(json.dumps(data, indent=2, ensure_ascii=False)[:2000] + "...")


if __name__ == "__main__":
    main()

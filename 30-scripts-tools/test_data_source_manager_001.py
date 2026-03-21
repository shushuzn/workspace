#!/usr/bin/env py
# -*- coding: utf-8 -*-
"""
Unit Tests for Data Source Manager

测试数据源管理器

作者：Claw
创建：2026-03-20
版本：v1.0.0
"""

import unittest
import sys
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import json

# 添加项目路径
WORKSPACE = Path("D:/OpenClaw/workspace")
sys.path.insert(0, str(WORKSPACE / "30-scripts-tools"))

from data_source_manager import (
    DataSourceManager,
    DataSourceBase,
    YahooFinanceDataSource,
    AlphaVantageDataSource,
    EastMoneyDataSource,
    DataSourceError,
    RateLimitError
)


class TestDataSourceBase(unittest.TestCase):
    """数据源基类测试"""
    
    def test_rate_limit_check(self) -> None:
        """测试速率限制检查"""
        source = YahooFinanceDataSource()
        
        # 首次请求应该立即返回
        start = __import__('time').time()
        source._rate_limit_check(min_interval=0.1)
        elapsed = __import__('time').time() - start
        
        self.assertLess(elapsed, 0.05)  # 应该几乎不等待
        
        # 第二次请求应该等待
        start = __import__('time').time()
        source._rate_limit_check(min_interval=0.1)
        elapsed = __import__('time').time() - start
        
        self.assertGreaterEqual(elapsed, 0.09)  # 应该等待约 0.1 秒


class TestYahooFinanceDataSource(unittest.TestCase):
    """Yahoo Finance 数据源测试"""
    
    def test_initialization(self) -> None:
        """测试初始化"""
        source = YahooFinanceDataSource()
        self.assertEqual(source.name, "Yahoo Finance")
        self.assertFalse(source.requires_api_key())
    
    @patch('data_source_manager.yf')
    def test_fetch_quote_mock(self, mock_yf) -> None:
        """测试获取行情 (mock)"""
        # 设置 mock 数据
        mock_ticker = MagicMock()
        mock_ticker.info = {
            "currentPrice": 150.23,
            "regularMarketChange": 2.34,
            "regularMarketChangePercent": 1.58,
            "volume": 1000000,
            "marketCap": 2500000000000
        }
        mock_yf.Ticker.return_value = mock_ticker
        
        source = YahooFinanceDataSource()
        source.enabled = True
        
        quote = source.fetch_quote("AAPL")
        
        self.assertEqual(quote["symbol"], "AAPL")
        self.assertEqual(quote["source"], "yahoo")
        self.assertEqual(quote["price"], 150.23)
        self.assertIn("timestamp", quote)
    
    @patch('data_source_manager.yf')
    def test_fetch_historical_mock(self, mock_yf) -> None:
        """测试获取历史数据 (mock)"""
        import pandas as pd
        from datetime import datetime, timedelta
        
        # 创建 mock 历史数据
        dates = pd.date_range(start="2026-03-01", end="2026-03-20", freq="B")
        mock_hist = pd.DataFrame({
            "Open": [150.0] * len(dates),
            "High": [152.0] * len(dates),
            "Low": [149.0] * len(dates),
            "Close": [151.0] * len(dates),
            "Volume": [1000000] * len(dates)
        }, index=dates)
        
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_hist
        mock_yf.Ticker.return_value = mock_ticker
        
        source = YahooFinanceDataSource()
        source.enabled = True
        
        data = source.fetch_historical("AAPL", "2026-03-01", "2026-03-20")
        
        self.assertEqual(data["symbol"], "AAPL")
        self.assertEqual(data["source"], "yahoo")
        self.assertGreater(len(data["data"]), 0)
        self.assertIn("date", data["data"][0])
        self.assertIn("open", data["data"][0])


class TestAlphaVantageDataSource(unittest.TestCase):
    """Alpha Vantage 数据源测试"""
    
    def test_initialization(self) -> None:
        """测试初始化"""
        source = AlphaVantageDataSource("test_key")
        self.assertEqual(source.name, "Alpha Vantage")
        self.assertTrue(source.requires_api_key())
        self.assertTrue(source.enabled)
    
    def test_initialization_no_key(self) -> None:
        """测试无 API Key 初始化"""
        source = AlphaVantageDataSource("")
        self.assertFalse(source.enabled)
    
    @patch('data_source_manager.requests')
    def test_fetch_quote_mock(self, mock_requests) -> None:
        """测试获取行情 (mock)"""
        # 设置 mock 响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "Global Quote": {
                "05. price": "150.23",
                "09. change": "2.34",
                "10. change percent": "1.58%",
                "06. volume": "1000000",
                "02. open": "148.00",
                "03. high": "151.00",
                "04. low": "147.50",
                "07. previous close": "147.89"
            }
        }
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response
        
        source = AlphaVantageDataSource("test_key")
        quote = source.fetch_quote("AAPL")
        
        self.assertEqual(quote["symbol"], "AAPL")
        self.assertEqual(quote["source"], "alpha_vantage")
        self.assertEqual(quote["price"], 150.23)


class TestEastMoneyDataSource(unittest.TestCase):
    """东方财富数据源测试"""
    
    def test_initialization(self) -> None:
        """测试初始化"""
        source = EastMoneyDataSource()
        self.assertEqual(source.name, "East Money")
        self.assertFalse(source.requires_api_key())
    
    def test_symbol_conversion(self) -> None:
        """测试股票代码转换"""
        source = EastMoneyDataSource()
        
        # A 股
        self.assertEqual(source._convert_symbol("600519"), "1.600519")
        self.assertEqual(source._convert_symbol("000001"), "0.000001")
        self.assertEqual(source._convert_symbol("300750"), "0.300750")


class TestDataSourceManager(unittest.TestCase):
    """数据源管理器测试"""
    
    def setUp(self) -> None:
        """测试前准备"""
        self.mock_cache = Mock()
        self.mock_cache.get.return_value = None  # 缓存未命中
        self.mock_cache.set.return_value = None
    
    def test_initialization(self) -> None:
        """测试初始化"""
        manager = DataSourceManager(cache=self.mock_cache)
        
        self.assertEqual(len(manager.sources), 3)
        self.assertIn("yahoo", manager.sources)
        self.assertIn("alpha_vantage", manager.sources)
        self.assertIn("eastmoney", manager.sources)
    
    @patch('data_source_manager.YahooFinanceDataSource')
    def test_fetch_quote_success(self, mock_yahoo) -> None:
        """测试成功获取行情"""
        # 设置 mock
        mock_source = Mock()
        mock_source.enabled = True
        mock_source.fetch_quote.return_value = {
            "symbol": "AAPL",
            "price": 150.23,
            "source": "yahoo"
        }
        mock_yahoo.return_value = mock_source
        
        manager = DataSourceManager(cache=self.mock_cache)
        quote = manager.fetch_quote("AAPL")
        
        self.assertEqual(quote["symbol"], "AAPL")
        self.assertEqual(quote["price"], 150.23)
        self.assertEqual(quote["source"], "yahoo")
        
        # 验证缓存被调用
        self.mock_cache.set.assert_called_once()
    
    @patch('data_source_manager.YahooFinanceDataSource')
    @patch('data_source_manager.AlphaVantageDataSource')
    def test_fetch_quote_fallback(self, mock_alpha, mock_yahoo) -> None:
        """测试故障转移"""
        # Yahoo 失败
        mock_yahoo_source = Mock()
        mock_yahoo_source.enabled = True
        mock_yahoo_source.fetch_quote.side_effect = DataSourceError("Yahoo failed")
        mock_yahoo.return_value = mock_yahoo_source
        
        # Alpha Vantage 成功
        mock_alpha_source = Mock()
        mock_alpha_source.enabled = True
        mock_alpha_source.fetch_quote.return_value = {
            "symbol": "AAPL",
            "price": 150.50,
            "source": "alpha_vantage"
        }
        mock_alpha.return_value = mock_alpha_source
        
        manager = DataSourceManager(cache=self.mock_cache)
        quote = manager.fetch_quote("AAPL")
        
        # 应该从 Alpha Vantage 获取成功
        self.assertEqual(quote["source"], "alpha_vantage")
        self.assertEqual(quote["price"], 150.50)
    
    def test_fetch_quote_cache_hit(self) -> None:
        """测试缓存命中"""
        cached_data = {"symbol": "AAPL", "price": 150.00, "source": "cache"}
        self.mock_cache.get.return_value = cached_data
        
        manager = DataSourceManager(cache=self.mock_cache)
        quote = manager.fetch_quote("AAPL")
        
        # 应该直接返回缓存数据
        self.assertEqual(quote["price"], 150.00)
        self.assertEqual(quote["source"], "cache")
    
    def test_fetch_quote_all_sources_fail(self) -> None:
        """测试所有数据源失败"""
        # 所有数据源都失败
        for source in ["yahoo", "alpha_vantage", "eastmoney"]:
            manager = DataSourceManager(cache=self.mock_cache)
            manager.sources[source].enabled = True
            manager.sources[source].fetch_quote = Mock(side_effect=DataSourceError("Failed"))
        
        # 应该抛出异常
        with self.assertRaises(DataSourceError):
            manager.fetch_quote("AAPL")
    
    def test_stats_collection(self) -> None:
        """测试统计信息收集"""
        manager = DataSourceManager(cache=self.mock_cache)
        
        stats = manager.get_stats()
        
        self.assertIn("total_requests", stats)
        self.assertIn("successful", stats)
        self.assertIn("failed", stats)
        self.assertIn("success_rate", stats)
        self.assertIn("sources", stats)


class TestDataSourceError(unittest.TestCase):
    """异常类测试"""
    
    def test_datasource_error(self) -> None:
        """测试 DataSourceError"""
        error = DataSourceError("Test error")
        self.assertEqual(str(error), "Test error")
    
    def test_ratelimit_error(self) -> None:
        """测试 RateLimitError"""
        error = RateLimitError("Rate limited")
        self.assertIsInstance(error, DataSourceError)
        self.assertEqual(str(error), "Rate limited")


if __name__ == "__main__":
    # 运行测试
    unittest.main(verbosity=2)

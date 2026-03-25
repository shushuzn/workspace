#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Stock Analysis API - Python Client Example
"""
import requests
import json
import time

API_BASE = "http://localhost:8080/api/v1"
API_KEY = "your-api-key-here"

class StockAPIClient:
    def __init__(self, base_url=API_BASE, api_key=API_KEY):
        self.base_url = base_url
        self.api_key = api_key
        self.session = requests.Session()
        self.session.headers.update({"X-API-Key": api_key})

    def get_quote(self, symbol):
        """获取实时行情"""
        response = self.session.get(f"{self.base_url}/quote/{symbol}")
        return response.json()

    def get_history(self, symbol, period="1m", interval="1d"):
        """获取历史数据"""
        params = {"period": period, "interval": interval}
        response = self.session.get(f"{self.base_url}/history/{symbol}", params=params)
        return response.json()

    def get_indicators(self, symbol, indicators="MA,RSI,MACD"):
        """获取技术指标"""
        params = {"indicators": indicators}
        response = self.session.get(f"{self.base_url}/indicators/{symbol}", params=params)
        return response.json()

    def get_signals(self, symbol):
        """获取交易信号"""
        response = self.session.get(f"{self.base_url}/signals/{symbol}")
        return response.json()

    def get_portfolio(self):
        """获取投资组合"""
        response = self.session.get(f"{self.base_url}/portfolio")
        return response.json()

    def trade(self, action, symbol, shares):
        """交易"""
        data = {"action": action, "symbol": symbol, "shares": shares}
        response = self.session.post(f"{self.base_url}/portfolio", json=data)
        return response.json()

    def backtest(self, strategy, symbol, period="1y", capital=100000):
        """回测"""
        data = {
            "strategy": strategy,
            "symbol": symbol,
            "period": period,
            "initial_capital": capital
        }
        response = self.session.post(f"{self.base_url}/backtest", json=data)
        return response.json()

    def get_alerts(self):
        """获取告警"""
        response = self.session.get(f"{self.base_url}/alerts")
        return response.json()

    def create_alert(self, symbol, condition, threshold):
        """创建告警"""
        data = {"symbol": symbol, "condition": condition, "threshold": threshold}
        response = self.session.post(f"{self.base_url}/alerts", json=data)
        return response.json()


# 使用示例
if __name__ == "__main__":
    client = StockAPIClient()

    # 获取行情
    quote = client.get_quote("AAPL")
    print(f"AAPL: ${quote['price']}")

    # 获取信号
    signals = client.get_signals("AAPL")
    print(f"Signal: {signals['signal']} (confidence: {signals['confidence']}%)")

    # 获取组合
    portfolio = client.get_portfolio()
    print(f"Portfolio value: ${portfolio['total_value']}")

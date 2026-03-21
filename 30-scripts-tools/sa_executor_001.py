import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-035 Trade Executor
【Phase 7 - 高级功能】

功能:
  - 订单管理
  - 成交确认
  - 交易日志
  - 持仓同步

依赖: 交易API (可选demo模式)
"""
import json
import sys
from pathlib import Path
from datetime import datetime
import random

# 配置
TRADE_DIR = Path("60-DATA/stock_035")
CONFIG_FILE = Path("30-scripts-tools/sa_035_config.json")


class TradeExecutor:
    """交易执行器"""
    
    def __init__(self):
        self.trade_dir = TRADE_DIR
        self.config = self._load_config()
        
        self.trade_dir.mkdir(parents=True, exist_ok=True)
        
        self.orders_file = self.trade_dir / "orders.json"
        self.positions_file = self.trade_dir / "positions.json"
        self.trades_file = self.trade_dir / "trades.json"
        
        self.orders = self._load_orders()
        self.positions = self._load_positions()
        self.trades = self._load_trades()
    
    def _load_config(self) -> dict:
        default = {
            "demo_mode": True,
            "default_quantity": 100,
            "slippage": 0.001,
            "commission": 0.001,
            "max_orders": 10
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except (Exception,):
                return default
        return default
    
    def _load_orders(self) -> list:
        if self.orders_file.exists():
            try:
                with open(self.orders_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (Exception,):
                return []
        return []
    
    def _load_positions(self) -> dict:
        if self.positions_file.exists():
            try:
                with open(self.positions_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (Exception,):
                return {}
        return {}
    
    def _load_trades(self) -> list:
        if self.trades_file.exists():
            try:
                with open(self.trades_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (Exception,):
                return []
        return []
    
    def _save_orders(self):
        with open(self.orders_file, "w", encoding="utf-8") as f:
            json.dump(self.orders, f, ensure_ascii=False, indent=2)
    
    def _save_positions(self):
        with open(self.positions_file, "w", encoding="utf-8") as f:
            json.dump(self.positions, f, ensure_ascii=False, indent=2)
    
    def _save_trades(self):
        with open(self.trades_file, "w", encoding="utf-8") as f:
            json.dump(self.trades, f, ensure_ascii=False, indent=2)
    
    def create_order(self, symbol: str, side: str, quantity: int = None, 
                    order_type: str = "MARKET", price: float = None) -> dict:
        """创建订单"""
        if quantity is None:
            quantity = self.config.get("default_quantity", 100)
        
        # 检查未完成订单数
        pending = sum(1 for o in self.orders if o.get("status") == "PENDING")
        if pending >= self.config.get("max_orders", 10):
            return {"status": "error", "message": "Too many pending orders"}
        
        order_id = f"ORD_{len(self.orders) + 1:04d}"
        
        order = {
            "order_id": order_id,
            "symbol": symbol,
            "side": side.upper(),
            "quantity": quantity,
            "type": order_type,
            "price": price,
            "status": "PENDING",
            "created_at": datetime.now().isoformat(),
            "filled_at": None
        }
        
        self.orders.append(order)
        self._save_orders()
        
        return order
    
    def execute_order(self, order_id: str, current_price: float = None) -> dict:
        """执行订单"""
        order = None
        for o in self.orders:
            if o.get("order_id") == order_id:
                order = o
                break
        
        if not order:
            return {"status": "error", "message": "Order not found"}
        
        if order.get("status") != "PENDING":
            return {"status": "error", "message": "Order not pending"}
        
        # 计算成交价
        if current_price is None:
            current_price = 100.0  # 默认价格
        
        slippage = self.config.get("slippage", 0.001)
        if order["side"] == "BUY":
            fill_price = current_price * (1 + slippage)
        else:
            fill_price = current_price * (1 - slippage)
        
        # 更新订单
        order["status"] = "FILLED"
        order["fill_price"] = round(fill_price, 2)
        order["filled_at"] = datetime.now().isoformat()
        
        # 记录成交
        trade = {
            "trade_id": f"TRD_{len(self.trades) + 1:04d}",
            "order_id": order_id,
            "symbol": order["symbol"],
            "side": order["side"],
            "quantity": order["quantity"],
            "price": fill_price,
            "commission": round(fill_price * order["quantity"] * self.config.get("commission", 0.001), 2),
            "timestamp": datetime.now().isoformat()
        }
        
        self.trades.append(trade)
        
        # 更新持仓
        self._update_position(order["symbol"], order["side"], order["quantity"], fill_price)
        
        self._save_orders()
        self._save_trades()
        self._save_positions()
        
        return {
            "status": "success",
            "order": order,
            "trade": trade
        }
    
    def _update_position(self, symbol: str, side: str, quantity: int, price: float):
        """更新持仓"""
        if symbol not in self.positions:
            self.positions[symbol] = {
                "symbol": symbol,
                "quantity": 0,
                "avg_price": 0,
                "value": 0
            }
        
        pos = self.positions[symbol]
        
        if side == "BUY":
            # 更新平均成本
            total_value = pos["quantity"] * pos["avg_price"] + quantity * price
            pos["quantity"] += quantity
            pos["avg_price"] = total_value / pos["quantity"] if pos["quantity"] > 0 else 0
        else:
            pos["quantity"] -= quantity
            if pos["quantity"] <= 0:
                del self.positions[symbol]
                return
        
        pos["value"] = pos["quantity"] * pos["avg_price"]
    
    def cancel_order(self, order_id: str) -> dict:
        """取消订单"""
        for order in self.orders:
            if order.get("order_id") == order_id and order.get("status") == "PENDING":
                order["status"] = "CANCELLED"
                order["cancelled_at"] = datetime.now().isoformat()
                self._save_orders()
                return {"status": "success", "order": order}
        
        return {"status": "error", "message": "Order not found or not cancellable"}
    
    def get_orders(self, status: str = None) -> dict:
        """获取订单"""
        orders = self.orders
        if status:
            orders = [o for o in orders if o.get("status") == status]
        
        return {
            "status": "success",
            "count": len(orders),
            "orders": orders[-20:]
        }
    
    def get_positions(self) -> dict:
        """获取持仓"""
        return {
            "status": "success",
            "count": len(self.positions),
            "positions": list(self.positions.values())
        }
    
    def get_trades(self, limit: int = 20) -> dict:
        """获取成交记录"""
        return {
            "status": "success",
            "count": len(self.trades),
            "trades": self.trades[-limit:]
        }
    
    def get_portfolio_value(self, current_prices: dict = None) -> dict:
        """获取组合市值"""
        total_value = 0
        positions = []
        
        for symbol, pos in self.positions.items():
            price = current_prices.get(symbol, pos["avg_price"]) if current_prices else pos["avg_price"]
            value = pos["quantity"] * price
            total_value += value
            
            positions.append({
                "symbol": symbol,
                "quantity": pos["quantity"],
                "avg_price": pos["avg_price"],
                "current_price": price,
                "value": round(value, 2),
                "pnl": round(value - pos["value"], 2)
            })
        
        return {
            "total_value": round(total_value, 2),
            "positions": positions,
            "timestamp": datetime.now().isoformat()
        }
    
    def close_position(self, symbol: str) -> dict:
        """清空持仓"""
        if symbol not in self.positions:
            return {"status": "error", "message": "No position"}
        
        pos = self.positions[symbol]
        
        # 创建卖出订单
        order = self.create_order(symbol, "SELL", pos["quantity"])
        
        # 直接执行
        result = self.execute_order(order["order_id"], pos["avg_price"])
        
        return result
    
    def reset(self):
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py sa_executor_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py sa_executor_001.py

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

重置交易状态"""
        self.orders = []
        self.positions = {}
        self.trades = []
        
        self._save_orders()
        self._save_positions()
        self._save_trades()
        
        return {"status": "success", "message": "Reset complete"}


logging.basicConfig(level=logging.INFO)
def main():
    executor = TradeExecutor()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--buy":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
            qty = int(sys.argv[3]) if len(sys.argv) > 3 else 100
            order = executor.create_order(symbol, "BUY", qty)
            print(json.dumps(order, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--sell":
            symbol = sys.argv[2] if len(sys.argv) > 2 else "AAPL"
            qty = int(sys.argv[3]) if len(sys.argv) > 3 else 100
            order = executor.create_order(symbol, "SELL", qty)
            print(json.dumps(order, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--execute":
            order_id = sys.argv[2] if len(sys.argv) > 2 else None
            if not order_id:
                return 1
            price = float(sys.argv[3]) if len(sys.argv) > 3 else 100
            result = executor.execute_order(order_id, price)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--orders":
            status = sys.argv[2] if len(sys.argv) > 2 else None
            result = executor.get_orders(status)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--positions":
            result = executor.get_positions()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--trades":
            result = executor.get_trades()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--portfolio":
            result = executor.get_portfolio_value()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--reset":
            result = executor.reset()
            print(json.dumps(result, ensure_ascii=False))
            return 0
    
    print("SA-035 Trade Executor")
    print("Usage:")
    print("  py sa_035_executor.py --buy AAPL [qty]    # Create buy order")
    print("  py sa_035_executor.py --sell AAPL [qty]   # Create sell order")
    print("  py sa_035_executor.py --execute ORD_0001 [price] # Execute order")
    print("  py sa_035_executor.py --orders [status]   # Get orders")
    print("  py sa_035_executor.py --positions        # Get positions")
    print("  py sa_035_executor.py --trades            # Get trades")
    print("  py sa_035_executor.py --portfolio         # Get portfolio value")
    print("  py sa_035_executor.py --reset             # Reset all")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
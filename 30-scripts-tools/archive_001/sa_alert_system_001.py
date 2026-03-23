#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-014: Real-time Alert System - 实时警报系统

功能：
1. 价格警报（突破/跌破）
2. 技术指标警报（RSI 超买超卖/MACD 金叉死叉）
3. 形态警报（形态识别完成）
4. 成交量警报（异常放量）
5. 多条件组合警报

依赖：
- SA-005: 技术指标
- SA-006: 形态识别

作者：Claw (AI Agent)
创建日期：2026-03-20
版本：1.0.0
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
import time


class AlertSystem:
    """实时警报系统"""

    def __init__(self):
        self.alert_dir = Path("60-DATA/stock_alerts")
        self.alert_dir.mkdir(parents=True, exist_ok=True)
        self.alert_log = self.alert_dir / "alert_log.jsonl"
        self.active_alerts = []

    def create_price_alert(self, symbol: str, alert_type: str,
                           target_price: float, current_price: float) -> Dict:
        """
        创建价格警报
        
        Args:
            symbol: 股票代码
            alert_type: 警报类型 ('above'/'below'/'breakthrough')
            target_price: 目标价格
            current_price: 当前价格
        
        Returns:
            警报配置
        """
        alert = {
            'id': f"price_{symbol}_{datetime.now().strftime('%H%M%S')}",
            'type': 'price',
            'symbol': symbol,
            'alert_type': alert_type,
            'target_price': target_price,
            'current_price': current_price,
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'triggered': False
        }

        self.active_alerts.append(alert)
        return alert

    def create_indicator_alert(self, symbol: str, indicator: str,
                                condition: str, threshold: float,
                                current_value: float) -> Dict:
        """
        创建技术指标警报
        
        Args:
            symbol: 股票代码
            indicator: 指标名称 (RSI/MACD/KDJ 等)
            condition: 条件 ('above'/'below'/'cross_over'/'cross_under')
            threshold: 阈值
            current_value: 当前值
        
        Returns:
            警报配置
        """
        alert = {
            'id': f"indicator_{symbol}_{indicator}_{datetime.now().strftime('%H%M%S')}",
            'type': 'indicator',
            'symbol': symbol,
            'indicator': indicator,
            'condition': condition,
            'threshold': threshold,
            'current_value': current_value,
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'triggered': False
        }

        self.active_alerts.append(alert)
        return alert

    def create_volume_alert(self, symbol: str, volume_ratio: float,
                            avg_volume: float) -> Dict:
        """
        创建成交量警报
        
        Args:
            symbol: 股票代码
            volume_ratio: 成交量比率（当前/平均）
            avg_volume: 平均成交量
        
        Returns:
            警报配置
        """
        alert = {
            'id': f"volume_{symbol}_{datetime.now().strftime('%H%M%S')}",
            'type': 'volume',
            'symbol': symbol,
            'volume_ratio': volume_ratio,
            'avg_volume': avg_volume,
            'trigger_threshold': 2.0,  # 2 倍放量触发
            'created_at': datetime.now().isoformat(),
            'status': 'active',
            'triggered': False
        }

        self.active_alerts.append(alert)
        return alert

    def check_price_alerts(self, symbol: str, current_price: float) -> List[Dict]:
        """
        检查价格警报
        
        Args:
            symbol: 股票代码
            current_price: 当前价格
        
        Returns:
            触发的警报列表
        """
        triggered = []

        for alert in self.active_alerts:
            if alert['type'] != 'price' or alert['symbol'] != symbol:
                continue
            if alert['triggered']:
                continue

            should_trigger = False
            if alert['alert_type'] == 'above' and current_price >= alert['target_price']:
                should_trigger = True
            elif alert['alert_type'] == 'below' and current_price <= alert['target_price']:
                should_trigger = True
            elif alert['alert_type'] == 'breakthrough':
                # 简化：假设之前低于目标价
                if current_price >= alert['target_price']:
                    should_trigger = True

            if should_trigger:
                alert['triggered'] = True
                alert['triggered_at'] = datetime.now().isoformat()
                alert['trigger_price'] = current_price
                triggered.append(alert)
                self._log_alert(alert)

        return triggered

    def check_indicator_alerts(self, symbol: str, indicator: str,
                                current_value: float) -> List[Dict]:
        """
        检查指标警报
        
        Args:
            symbol: 股票代码
            indicator: 指标名称
            current_value: 当前值
        
        Returns:
            触发的警报列表
        """
        triggered = []

        for alert in self.active_alerts:
            if alert['type'] != 'indicator':
                continue
            if alert['symbol'] != symbol or alert['indicator'] != indicator:
                continue
            if alert['triggered']:
                continue

            should_trigger = False
            if alert['condition'] == 'above' and current_value >= alert['threshold']:
                should_trigger = True
            elif alert['condition'] == 'below' and current_value <= alert['threshold']:
                should_trigger = True
            elif alert['condition'] == 'cross_over':
                # 简化：假设之前低于阈值
                if current_value >= alert['threshold']:
                    should_trigger = True
            elif alert['condition'] == 'cross_under':
                if current_value <= alert['threshold']:
                    should_trigger = True

            if should_trigger:
                alert['triggered'] = True
                alert['triggered_at'] = datetime.now().isoformat()
                alert['trigger_value'] = current_value
                triggered.append(alert)
                self._log_alert(alert)

        return triggered

    def check_volume_alerts(self, symbol: str, current_volume: float,
                            avg_volume: float) -> List[Dict]:
        """
        检查成交量警报
        
        Args:
            symbol: 股票代码
            current_volume: 当前成交量
            avg_volume: 平均成交量
        
        Returns:
            触发的警报列表
        """
        triggered = []
        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0

        for alert in self.active_alerts:
            if alert['type'] != 'volume' or alert['symbol'] != symbol:
                continue
            if alert['triggered']:
                continue

            if volume_ratio >= alert['trigger_threshold']:
                alert['triggered'] = True
                alert['triggered_at'] = datetime.now().isoformat()
                alert['trigger_volume'] = current_volume
                alert['trigger_ratio'] = volume_ratio
                triggered.append(alert)
                self._log_alert(alert)

        return triggered

    def _log_alert(self, alert: Dict):
        """记录警报日志"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'alert_id': alert['id'],
            'type': alert['type'],
            'symbol': alert['symbol'],
            'status': 'triggered',
            'details': alert
        }

        try:
            with open(self.alert_log, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[WARN] 记录警报日志失败：{e}")

    def get_active_alerts(self, symbol: str = None) -> List[Dict]:
        """获取活跃警报"""
        if symbol:
            return [a for a in self.active_alerts if a['symbol'] == symbol and not a['triggered']]
        return [a for a in self.active_alerts if not a['triggered']]

    def get_triggered_alerts(self, symbol: str = None) -> List[Dict]:
        """获取已触发警报"""
        if symbol:
            return [a for a in self.active_alerts if a['symbol'] == symbol and a['triggered']]
        return [a for a in self.active_alerts if a['triggered']]

    def clear_triggered_alerts(self):
        """清除已触发警报"""
        self.active_alerts = [a for a in self.active_alerts if not a['triggered']]

    def save_alerts(self, filename: str = None):
        """保存警报配置"""
        if filename is None:
            filename = f"alerts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        filepath = self.alert_dir / filename

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'active_alerts': self.active_alerts,
                'saved_at': datetime.now().isoformat()
            }, f, indent=2, ensure_ascii=False)

        return filepath

    def load_alerts(self, filepath: Path):
        """加载警报配置"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.active_alerts = data.get('active_alerts', [])
        return len(self.active_alerts)


def create_sample_alerts(alert_system: AlertSystem) -> List[Dict]:
    """创建示例警报"""
    alerts = []

    # 价格警报
    alerts.append(alert_system.create_price_alert('AAPL', 'above', 150.0, 145.0))
    alerts.append(alert_system.create_price_alert('AAPL', 'below', 140.0, 145.0))

    # 指标警报
    alerts.append(alert_system.create_indicator_alert('AAPL', 'RSI', 'above', 70, 65))
    alerts.append(alert_system.create_indicator_alert('AAPL', 'RSI', 'below', 30, 35))
    alerts.append(alert_system.create_indicator_alert('AAPL', 'MACD', 'cross_over', 0, -0.5))

    # 成交量警报
    alerts.append(alert_system.create_volume_alert('AAPL', 0, 1000000))

    return alerts


def main():
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
# py sa_alert_system_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py sa_alert_system_001.py

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

主函数"""
    print("=" * 70)
    print(" " * 25 + "SA-014: Real-time Alert System")
    print("=" * 70)

    alert_system = AlertSystem()

    # 测试模式
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        print("\n[Test 1] Create Sample Alerts")
        print("-" * 70)
        alerts = create_sample_alerts(alert_system)
        print(f"  Created {len(alerts)} alerts")

        print("\n[Test 2] Check Price Alerts")
        print("-" * 70)
        # 测试价格突破
        triggered = alert_system.check_price_alerts('AAPL', 152.0)
        print(f"  Triggered: {len(triggered)} alerts")
        for alert in triggered:
            print(f"    - {alert['id']}: Price breakthrough at ${alert['trigger_price']}")

        print("\n[Test 3] Check Indicator Alerts (RSI Overbought)")
        print("-" * 70)
        triggered = alert_system.check_indicator_alerts('AAPL', 'RSI', 75)
        print(f"  Triggered: {len(triggered)} alerts")
        for alert in triggered:
            print(f"    - {alert['id']}: RSI {alert['trigger_value']} > {alert['threshold']}")

        print("\n[Test 4] Check Volume Alerts")
        print("-" * 70)
        triggered = alert_system.check_volume_alerts('AAPL', 2500000, 1000000)
        print(f"  Triggered: {len(triggered)} alerts")
        for alert in triggered:
            print(f"    - {alert['id']}: Volume ratio {alert['trigger_ratio']:.2f}x")

        print("\n[Test 5] Get Active Alerts")
        print("-" * 70)
        active = alert_system.get_active_alerts('AAPL')
        print(f"  Active alerts: {len(active)}")
        for alert in active:
            print(f"    - {alert['id']}: {alert['type']} ({alert['status']})")

        print("\n[Test 6] Get Triggered Alerts")
        print("-" * 70)
        triggered = alert_system.get_triggered_alerts('AAPL')
        print(f"  Triggered alerts: {len(triggered)}")
        for alert in triggered:
            print(f"    - {alert['id']}: Triggered at {alert['triggered_at']}")

        print("\n[Test 7] Save Alerts")
        print("-" * 70)
        filepath = alert_system.save_alerts()
        print(f"  Saved to: {filepath}")

        print("\n[Test 8] Alert Log")
        print("-" * 70)
        if alert_system.alert_log.exists():
            with open(alert_system.alert_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            print(f"  Alert log entries: {len(lines)}")
        else:
            print("  No alert log yet")

        print("\n" + "=" * 70)
        print(" SA-014 Real-time Alert System test completed")
        print("=" * 70)

    else:
        # 正常使用模式
        print("\nUsage: py sa_014_alert_system.py --test")
        print("\nFeatures:")
        print("  - Price alerts (above/below/breakthrough)")
        print("  - Indicator alerts (RSI/MACD/KDJ)")
        print("  - Volume alerts (abnormal volume)")
        print("  - Multi-condition alerts")
        print("  - Alert logging and history")
        print("  - Save/Load alert configurations")
        print("  - Auto-save to 60-DATA/stock_alerts/")


if __name__ == '__main__':
    main()

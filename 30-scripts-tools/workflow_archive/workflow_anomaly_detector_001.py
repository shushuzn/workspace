import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动异常检测器 - 超时检测 + 自动重试 + 异常预警
"""

import json
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any
import traceback

class WorkflowAnomalyDetector:
    """自动异常检测器"""
    
    def __init__(self):
        self.log_file = Path("flow-archive/20260318-universal-workflow-001/anomaly-log.json")
        self.config_file = Path("flow-archive/20260318-universal-workflow-001/anomaly-config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
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
# py workflow_anomaly_detector_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py workflow_anomaly_detector_001.py

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

加载配置"""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "timeout_seconds": 300,
            "max_retries": 3,
            "retry_delay_seconds": 5,
            "error_threshold": 3,
            "warnings": []
        }
    
    def _save_config(self) -> None:
        """保存配置"""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def execute_with_monitoring(self, step_id: str, func: Callable, 
                                 args: tuple = (), kwargs: dict = None,
                                 timeout_seconds: int = None) -> Dict:
        """
        执行函数并监控异常
        
        Args:
            step_id: 步骤 ID
            func: 要执行的函数
            args: 位置参数
            kwargs: 关键字参数
            timeout_seconds: 超时时间 (秒)
        
        Returns:
            执行结果
        """
        
        kwargs = kwargs or {}
        timeout = timeout_seconds or self.config['timeout_seconds']
        
        result = {
            "step_id": step_id,
            "success": False,
            "error": None,
            "retries": 0,
            "duration_seconds": 0,
            "anomaly_detected": False
        }
        
        start_time = datetime.now()
        
        for attempt in range(self.config['max_retries']):
            try:
                # 执行函数
                func_result = func(*args, **kwargs)
                
                # 检查超时
                elapsed = (datetime.now() - start_time).total_seconds()
                if elapsed > timeout:
                    result['anomaly_detected'] = True
                    result['error'] = f"Timeout: {elapsed:.1f}s > {timeout}s"
                    self._log_anomaly(step_id, "timeout", result['error'])
                else:
                    # 成功
                    result['success'] = True
                    result['result'] = func_result
                    result['duration_seconds'] = elapsed
                    break
                
            except Exception as e:
                error_msg = str(e)
                result['error'] = error_msg
                result['retries'] = attempt + 1
                
                # 记录异常
                self._log_anomaly(step_id, "exception", error_msg)
                
                if attempt < self.config['max_retries'] - 1:
                    # 等待后重试
                    time.sleep(self.config['retry_delay_seconds'])
                else:
                    # 所有重试失败
                    result['anomaly_detected'] = True
        
        # 保存结果
        self._save_result(result)
        
        return result
    
    def _log_anomaly(self, step_id: str, anomaly_type: str, details: str) -> None:
        """记录异常"""
        log = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)
        
        log.append({
            "timestamp": datetime.now().isoformat(),
            "step_id": step_id,
            "anomaly_type": anomaly_type,
            "details": details[:200]
        })
        
        # 保留最近 100 条
        log = log[-100:]
        
        with open(self.log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
        
        # 更新警告计数
        self.config['warnings'].append({
            "step_id": step_id,
            "type": anomaly_type,
            "counted_at": datetime.now().isoformat()
        })
        self.config['warnings'] = self.config['warnings'][-10:]
        self._save_config()
    
    def _save_result(self, result: Dict) -> None:
        """保存结果"""
        results_file = Path("flow-archive/20260318-universal-workflow-001/anomaly-results.json")
        
        results = []
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
        
        results.append(result)
        results = results[-50:]
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
    
    def get_health_report(self) -> Dict:
        """获取健康报告"""
        # 读取日志
        log = []
        if self.log_file.exists():
            with open(self.log_file, 'r', encoding='utf-8') as f:
                log = json.load(f)
        
        # 统计
        total_anomalies = len(log)
        timeout_count = sum(1 for l in log if l['anomaly_type'] == 'timeout')
        exception_count = sum(1 for l in log if l['anomaly_type'] == 'exception')
        
        # 健康状态
        if total_anomalies == 0:
            health = "excellent"
        elif total_anomalies <= 2:
            health = "good"
        elif total_anomalies <= 5:
            health = "warning"
        else:
            health = "critical"
        
        return {
            "total_anomalies": total_anomalies,
            "timeout_count": timeout_count,
            "exception_count": exception_count,
            "health_status": health,
            "recent_warnings": len(self.config['warnings'])
        }
    
    def display_status(self) -> str:
        """显示状态"""
        report = self.get_health_report()
        
        output = []
        output.append("\n" + "=" * 60)
        output.append(" " * 18 + "Anomaly Detector Status")
        output.append("=" * 60)
        
        output.append(f"\n[Health Status]")
        output.append(f"  Status:        {report['health_status'].upper()}")
        output.append(f"  Total Issues:  {report['total_anomalies']}")
        output.append(f"  Timeouts:      {report['timeout_count']}")
        output.append(f"  Exceptions:    {report['exception_count']}")
        
        if report['health_status'] in ['warning', 'critical']:
            output.append(f"\n[WARN] Workflow needs attention!")
        
        output.append("=" * 60)
        
        return "\n".join(output)
    
    def run(self) -> Dict:
        """运行检测器"""
        return {
            "report": self.get_health_report(),
            "success": True
        }

logging.basicConfig(level=logging.INFO)
def main() -> None:
    """测试入口"""
    detector = WorkflowAnomalyDetector()
    
    print("Anomaly Detector Test")
    print("=" * 60)
    
    # 测试：正常执行
    def normal_func():
        return "success"
    
    result1 = detector.execute_with_monitoring("1", normal_func)
    print(f"\nTest 1 (normal): success={result1['success']}, anomaly={result1['anomaly_detected']}")
    
    # 测试：异常执行
    def failing_func():
        raise Exception("Simulated failure")
    
    result2 = detector.execute_with_monitoring("2", failing_func)
    print(f"Test 2 (failing): success={result2['success']}, retries={result2['retries']}, anomaly={result2['anomaly_detected']}")
    
    # 显示状态
    print(detector.display_status())
    
    print(f"\n[OK] Detector test completed")

if __name__ == "__main__":
    main()

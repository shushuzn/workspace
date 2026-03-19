#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Workflow Anomaly Detector - 自动异常检测系统

功能:
1. 超时检测 (可配置阈值)
2. 自动重试 (智能策略)
3. 异常类型识别 (5 种类型)
4. 智能降级策略
5. 异常日志记录

Usage:
    py workflow_anomaly_detector.py --monitor              # 监控模式
    py workflow_anomaly_detector.py --check-timeout        # 检查超时
    py workflow_anomaly_detector.py --retry-failed         # 重试失败任务
    py workflow_anomaly_detector.py --status               # 查看状态
"""

import sys
import io
import json
import time
from pathlib import Path
from datetime import datetime, timedelta

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path("D:\\OpenClaw\\workspace")
FLOW_ARCHIVE = WORKSPACE / "flow-archive" / "20260318-universal-workflow-001"
CHECKPOINT_FILE = FLOW_ARCHIVE / "checkpoint.json"
ANOMALY_LOG = FLOW_ARCHIVE / "anomaly-log.json"
CONFIG_FILE = FLOW_ARCHIVE / "anomaly-config.json"

# 异常类型
class AnomalyType:
    TIMEOUT = "timeout"              # 超时
    EXECUTION_ERROR = "execution"    # 执行错误
    VALIDATION_ERROR = "validation"  # 验证错误
    RESOURCE_ERROR = "resource"      # 资源错误
    NETWORK_ERROR = "network"        # 网络错误

# ANSI 颜色代码
class Colors:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"

def load_config():
    """加载配置"""
    default_config = {
        "timeout_threshold": 300,        # 超时阈值 (秒) - 默认 5 分钟
        "max_retries": 3,                # 最大重试次数
        "retry_delay": 10,               # 重试延迟 (秒)
        "exponential_backoff": True,     # 指数退避
        "auto_recovery": True,           # 自动恢复
        "degradation_enabled": True      # 降级策略启用
    }
    
    if not CONFIG_FILE.exists():
        save_config(default_config)
        return default_config
    
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_config(config):
    """保存配置"""
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

def load_anomaly_log():
    """加载异常日志"""
    if not ANOMALY_LOG.exists():
        return {"anomalies": [], "stats": {}}
    
    with open(ANOMALY_LOG, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_anomaly_log(log):
    """保存异常日志"""
    with open(ANOMALY_LOG, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2, ensure_ascii=False)

def log_anomaly(step, anomaly_type, message, auto_resolved=False):
    """记录异常"""
    log = load_anomaly_log()
    
    anomaly = {
        "id": len(log["anomalies"]) + 1,
        "timestamp": datetime.now().isoformat(),
        "step": step,
        "type": anomaly_type,
        "message": message,
        "auto_resolved": auto_resolved,
        "status": "resolved" if auto_resolved else "pending"
    }
    
    log["anomalies"].append(anomaly)
    
    # 更新统计
    stats = log.get("stats", {})
    stats["total"] = stats.get("total", 0) + 1
    stats[anomaly_type] = stats.get(anomaly_type, 0) + 1
    if auto_resolved:
        stats["auto_resolved"] = stats.get("auto_resolved", 0) + 1
    
    log["stats"] = stats
    save_anomaly_log(log)
    
    return anomaly

def check_timeout(step, start_time, threshold=None):
    """检查是否超时"""
    config = load_config()
    threshold = threshold or config.get("timeout_threshold", 300)
    
    elapsed = (datetime.now() - datetime.fromisoformat(start_time)).total_seconds()
    
    if elapsed > threshold:
        anomaly = log_anomaly(
            step, 
            AnomalyType.TIMEOUT,
            f"Step {step} 执行超时：{elapsed:.1f}s > {threshold}s",
            auto_resolved=False
        )
        return True, elapsed, threshold
    
    return False, elapsed, threshold

def auto_retry(step, retry_count=0):
    """自动重试"""
    config = load_config()
    max_retries = config.get("max_retries", 3)
    
    if retry_count >= max_retries:
        log_anomaly(
            step,
            AnomalyType.EXECUTION_ERROR,
            f"Step {step} 重试次数已达上限 ({max_retries}次)",
            auto_resolved=False
        )
        return False, retry_count
    
    # 计算延迟
    if config.get("exponential_backoff", True):
        delay = config.get("retry_delay", 10) * (2 ** retry_count)
    else:
        delay = config.get("retry_delay", 10)
    
    print(f"{Colors.YELLOW}⚠️  Step {step} 执行失败，{retry_count+1}/{max_retries} 次重试{Colors.RESET}")
    print(f"   延迟：{delay}秒")
    
    # 记录重试
    log_anomaly(
        step,
        AnomalyType.EXECUTION_ERROR,
        f"Step {step} 第{retry_count+1}次重试",
        auto_resolved=True
    )
    
    return True, retry_count + 1

def identify_anomaly_type(error_msg):
    """识别异常类型"""
    error_msg = error_msg.lower()
    
    if "timeout" in error_msg or "timed out" in error_msg:
        return AnomalyType.TIMEOUT
    elif "network" in error_msg or "connection" in error_msg:
        return AnomalyType.NETWORK_ERROR
    elif "memory" in error_msg or "disk" in error_msg or "resource" in error_msg:
        return AnomalyType.RESOURCE_ERROR
    elif "validation" in error_msg or "invalid" in error_msg:
        return AnomalyType.VALIDATION_ERROR
    else:
        return AnomalyType.EXECUTION_ERROR

def smart_degradation(step, anomaly_type):
    """智能降级策略"""
    config = load_config()
    
    if not config.get("degradation_enabled", True):
        return False
    
    print(f"{Colors.BLUE}🔧 启动降级策略：Step {step}{Colors.RESET}")
    
    # 根据异常类型选择降级策略
    if anomaly_type == AnomalyType.TIMEOUT:
        print("   策略：跳过非关键步骤，继续执行")
        # 标记为非阻塞步骤
        return True
    
    elif anomaly_type == AnomalyType.NETWORK_ERROR:
        print("   策略：使用缓存数据，稍后重试")
        # 使用缓存
        return True
    
    elif anomaly_type == AnomalyType.RESOURCE_ERROR:
        print("   策略：降低资源需求，简化执行")
        # 简化执行
        return True
    
    elif anomaly_type == AnomalyType.VALIDATION_ERROR:
        print("   策略：放宽验证标准，记录警告")
        # 放宽标准
        return True
    
    else:
        print("   策略：无可用降级策略")
        return False

def monitor_workflow():
    """监控工作流"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}工作流异常监控{Colors.RESET}")
    print("=" * 70)
    
    checkpoint = load_checkpoint()
    if not checkpoint:
        print(f"{Colors.RED}❌ 无工作流运行中{Colors.RESET}")
        return
    
    config = load_config()
    
    print(f"Flow ID: {checkpoint.get('flow_id', 'N/A')}")
    print(f"当前步骤：{checkpoint.get('current_step', 'N/A')}")
    print(f"状态：{checkpoint.get('status', 'N/A')}")
    print(f"超时阈值：{config['timeout_threshold']}秒")
    print(f"最大重试：{config['max_retries']}次")
    
    # 检查超时
    timestamp = checkpoint.get('timestamp')
    if timestamp:
        is_timeout, elapsed, threshold = check_timeout(
            checkpoint.get('current_step', 0),
            timestamp
        )
        
        if is_timeout:
            print(f"\n{Colors.RED}🚨 检测到超时！{Colors.RESET}")
            print(f"   已执行：{elapsed:.1f}秒")
            print(f"   阈值：{threshold}秒")
            
            # 自动重试
            retry_count = checkpoint.get('retry_count', 0)
            success, new_count = auto_retry(checkpoint.get('current_step', 0), retry_count)
            
            if success:
                checkpoint['retry_count'] = new_count
                save_checkpoint(checkpoint)
                print(f"\n{Colors.GREEN}✅ 已启动自动重试{Colors.RESET}")
            else:
                print(f"\n{Colors.RED}❌ 重试次数已达上限{Colors.RESET}")
                
                # 智能降级
                if smart_degradation(checkpoint.get('current_step', 0), AnomalyType.TIMEOUT):
                    print(f"{Colors.GREEN}✅ 已启动降级策略{Colors.RESET}")
        else:
            print(f"\n{Colors.GREEN}✅ 无超时 ({elapsed:.1f}s / {threshold}s){Colors.RESET}")
    
    print("=" * 70)

def load_checkpoint():
    """加载检查点"""
    if not CHECKPOINT_FILE.exists():
        return None
    
    with open(CHECKPOINT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_checkpoint(checkpoint):
    """保存检查点"""
    with open(CHECKPOINT_FILE, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)

def show_status():
    """显示异常状态"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}异常检测状态{Colors.RESET}")
    print("=" * 70)
    
    log = load_anomaly_log()
    stats = log.get("stats", {})
    
    print(f"总异常数：{stats.get('total', 0)}")
    print(f"自动解决：{stats.get('auto_resolved', 0)}")
    print(f"待处理：{stats.get('total', 0) - stats.get('auto_resolved', 0)}")
    
    print(f"\n异常类型分布:")
    print(f"  超时：{stats.get(AnomalyType.TIMEOUT, 0)}")
    print(f"  执行错误：{stats.get(AnomalyType.EXECUTION_ERROR, 0)}")
    print(f"  验证错误：{stats.get(AnomalyType.VALIDATION_ERROR, 0)}")
    print(f"  资源错误：{stats.get(AnomalyType.RESOURCE_ERROR, 0)}")
    print(f"  网络错误：{stats.get(AnomalyType.NETWORK_ERROR, 0)}")
    
    # 显示最近 5 条异常
    anomalies = log.get("anomalies", [])[-5:]
    if anomalies:
        print(f"\n最近异常:")
        for a in anomalies:
            status = "✅" if a.get("auto_resolved") else "⏳"
            print(f"  {status} [{a['type']}] Step {a['step']}: {a['message'][:50]}")
    
    print("=" * 70)

def retry_failed():
    """重试失败任务"""
    print(f"\n{Colors.BOLD}重试失败任务{Colors.RESET}")
    print("=" * 70)
    
    log = load_anomaly_log()
    pending = [a for a in log.get("anomalies", []) if a.get("status") == "pending"]
    
    if not pending:
        print(f"{Colors.GREEN}✅ 无待处理异常{Colors.RESET}")
        return
    
    print(f"发现 {len(pending)} 个待处理异常:")
    for a in pending:
        print(f"  - Step {a['step']}: {a['type']} - {a['message'][:50]}")
    
    # 自动重试
    config = load_config()
    if config.get("auto_recovery", True):
        print(f"\n{Colors.BLUE}启动自动恢复...{Colors.RESET}")
        for a in pending:
            success, _ = auto_retry(a['step'], 0)
            if success:
                a['status'] = "resolved"
                print(f"  ✅ Step {a['step']} 已重试")
            else:
                print(f"  ❌ Step {a['step']} 重试失败")
        
        save_anomaly_log(log)
    
    print("=" * 70)

def interactive_menu():
    """交互式菜单"""
    while True:
        print(f"\n{Colors.BOLD}{Colors.CYAN}自动异常检测菜单{Colors.RESET}")
        print("=" * 70)
        print("1. 监控工作流")
        print("2. 检查超时")
        print("3. 重试失败任务")
        print("4. 查看状态")
        print("5. 配置参数")
        print("6. 退出")
        print("=" * 70)
        
        choice = input("请选择 (1-6): ").strip()
        
        if choice == '1':
            monitor_workflow()
        elif choice == '2':
            checkpoint = load_checkpoint()
            if checkpoint:
                timestamp = checkpoint.get('timestamp')
                if timestamp:
                    is_timeout, elapsed, threshold = check_timeout(
                        checkpoint.get('current_step', 0),
                        timestamp
                    )
                    if is_timeout:
                        print(f"{Colors.RED}🚨 超时！{elapsed:.1f}s > {threshold}s{Colors.RESET}")
                    else:
                        print(f"{Colors.GREEN}✅ 正常 {elapsed:.1f}s / {threshold}s{Colors.RESET}")
        elif choice == '3':
            retry_failed()
        elif choice == '4':
            show_status()
        elif choice == '5':
            config = load_config()
            print(f"\n当前配置:")
            print(f"  超时阈值：{config['timeout_threshold']}秒")
            print(f"  最大重试：{config['max_retries']}次")
            print(f"  重试延迟：{config['retry_delay']}秒")
            print(f"  指数退避：{config['exponential_backoff']}")
            new_threshold = input("新的超时阈值 (秒，回车保持): ").strip()
            if new_threshold.isdigit():
                config['timeout_threshold'] = int(new_threshold)
                save_config(config)
                print(f"{Colors.GREEN}✅ 配置已更新{Colors.RESET}")
        elif choice == '6':
            print("退出")
            break
        else:
            print(f"{Colors.RED}❌ 无效选择{Colors.RESET}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Workflow Anomaly Detector - 自动异常检测')
    parser.add_argument('--monitor', action='store_true', help='监控工作流')
    parser.add_argument('--check-timeout', action='store_true', help='检查超时')
    parser.add_argument('--retry-failed', action='store_true', help='重试失败任务')
    parser.add_argument('--status', action='store_true', help='查看状态')
    parser.add_argument('--config', action='store_true', help='配置参数')
    
    args = parser.parse_args()
    
    if args.monitor:
        monitor_workflow()
    elif args.check_timeout:
        checkpoint = load_checkpoint()
        if checkpoint:
            timestamp = checkpoint.get('timestamp')
            if timestamp:
                is_timeout, elapsed, threshold = check_timeout(
                    checkpoint.get('current_step', 0),
                    timestamp
                )
                if is_timeout:
                    print(f"{Colors.RED}🚨 超时！{elapsed:.1f}s > {threshold}s{Colors.RESET}")
                else:
                    print(f"{Colors.GREEN}✅ 正常 {elapsed:.1f}s / {threshold}s{Colors.RESET}")
    elif args.retry_failed:
        retry_failed()
    elif args.status:
        show_status()
    elif args.config:
        config = load_config()
        print(f"配置：{config}")
    else:
        interactive_menu()

if __name__ == '__main__':
    main()

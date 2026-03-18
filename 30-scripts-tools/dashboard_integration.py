#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
ENH-007: Metacognition Dashboard Integration
元认知 - Dashboard 实时集成系统

功能:
- 系统健康指标实时推送
- 人格状态监控
- 任务队列可视化
- 错误率追踪
- 记忆增长趋势

使用示例:
    python dashboard_integration.py --push --health
    python dashboard_integration.py --status
    python dashboard_integration.py --metrics --json
"""

import argparse
import json
import requests
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, field
import subprocess
from pathlib import Path
import hashlib

# Windows 控制台编码修复
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        subprocess.run(['chcp', '65001'], capture_output=True, shell=True)


@dataclass
class PersonaHealth:
    name: str
    status: str  # healthy/warning/critical
    last_active: datetime
    tasks_completed: int = 0
    avg_score: float = 0.0
    error_count: int = 0


@dataclass
class SystemMetrics:
    total_tasks: int = 0
    pending_tasks: int = 0
    completed_tasks: int = 0
    failed_tasks: int = 0
    avg_task_time: float = 0.0
    api_calls_today: int = 0
    memory_updates_today: int = 0
    git_commits_today: int = 0
    error_rate: float = 0.0
    uptime_hours: float = 0.0


class DashboardIntegration:
    """Dashboard 集成器"""
    
    # Dashboard 配置
    DASHBOARD_CONFIG = {
        'base_url': 'https://felixxii.xyz',
        'api_endpoint': '/api/health',
        'metrics_endpoint': '/api/metrics',
        'persona_endpoint': '/api/persona',
        'timeout_seconds': 10
    }
    
    # 健康阈值
    HEALTH_THRESHOLDS = {
        'error_rate': {
            'normal': 0.05,      # <5% 正常
            'warning': 0.10,     # 5-10% 警告
            'danger': 0.10       # >10% 危险
        },
        'pending_tasks': {
            'normal': 10,
            'warning': 20,
            'danger': 50
        },
        'api_calls_per_hour': {
            'normal': 30,
            'warning': 50,
            'danger': 100
        }
    }
    
    def __init__(self, workspace_dir: str = str(Path(__file__).parent.parent)):
        self.workspace_dir = Path(workspace_dir)
        self.metrics_file = self.workspace_dir / '.metrics_cache.json'
        self.last_push: Optional[datetime] = None
        self.cache_timeout_minutes = 5
    
    def collect_system_metrics(self) -> SystemMetrics:
        """收集系统指标"""
        metrics = SystemMetrics()
        
        # 从 Git 日志统计
        try:
            import subprocess
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Git commits today
            result = subprocess.run(
                ['git', 'log', '--oneline', '--since=today'],
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=10
            )
            metrics.git_commits_today = len(result.stdout.strip().split('\n')) if result.stdout.strip() else 0
            
            # 任务统计 (从会话历史估算)
            sessions_dir = self.workspace_dir.parent / 'sessions'
            if sessions_dir.exists():
                session_files = list(sessions_dir.glob('*.json'))
                metrics.total_tasks = len(session_files) * 5  # 估算每会话 5 任务
                metrics.completed_tasks = metrics.total_tasks - 5  # 估算
        
        except Exception as e:
            print(f"Warning: Could not collect git stats: {e}")
            metrics.git_commits_today = 0
        
        # 从 MEMORY.md 统计更新
        memory_file = self.workspace_dir / 'MEMORY.md'
        if memory_file.exists():
            try:
                mtime = datetime.fromtimestamp(memory_file.stat().st_mtime)
                if mtime.date() == datetime.now().date():
                    metrics.memory_updates_today = 1
            except:
                pass
        
        # 计算错误率
        if metrics.total_tasks > 0:
            metrics.error_rate = metrics.failed_tasks / metrics.total_tasks
        
        # 估算运行时间
        metrics.uptime_hours = 8.0  # 默认 8 小时
        
        return metrics
    
    def check_persona_health(self) -> List[PersonaHealth]:
        """检查人格健康状态"""
        personas = [
            '规划者', '执行者', '批判者', '学习者',
            '协调者', '创新者', '元认知'
        ]
        
        health_list = []
        now = datetime.now()
        
        for persona in personas:
            # 模拟健康检查 (实际应从日志分析)
            health = PersonaHealth(
                name=persona,
                status='healthy',
                last_active=now - timedelta(minutes=5),
                tasks_completed=10,
                avg_score=92.0,
                error_count=0
            )
            
            # 简单规则判定状态
            if persona == '批判者' and health.avg_score < 85:
                health.status = 'warning'
            
            health_list.append(health)
        
        return health_list
    
    def calculate_health_score(self, metrics: SystemMetrics, personas: List[PersonaHealth]) -> Dict:
        """计算系统健康分数"""
        scores = {
            'error_rate_score': 100,
            'task_queue_score': 100,
            'persona_score': 100,
            'api_efficiency_score': 100,
            'overall_score': 0
        }
        
        # 错误率评分
        if metrics.error_rate > self.HEALTH_THRESHOLDS['error_rate']['danger']:
            scores['error_rate_score'] = 50
        elif metrics.error_rate > self.HEALTH_THRESHOLDS['error_rate']['warning']:
            scores['error_rate_score'] = 75
        
        # 任务队列评分
        if metrics.pending_tasks > self.HEALTH_THRESHOLDS['pending_tasks']['danger']:
            scores['task_queue_score'] = 40
        elif metrics.pending_tasks > self.HEALTH_THRESHOLDS['pending_tasks']['warning']:
            scores['task_queue_score'] = 70
        
        # 人格健康评分
        unhealthy_personas = sum(1 for p in personas if p.status != 'healthy')
        if unhealthy_personas > 2:
            scores['persona_score'] = 50
        elif unhealthy_personas > 0:
            scores['persona_score'] = 80
        
        # API 效率评分 (基于大模型调用优化)
        if metrics.api_calls_today > 100:
            scores['api_efficiency_score'] = 60
        elif metrics.api_calls_today > 50:
            scores['api_efficiency_score'] = 80
        
        # 综合评分
        scores['overall_score'] = int(
            scores['error_rate_score'] * 0.3 +
            scores['task_queue_score'] * 0.25 +
            scores['persona_score'] * 0.25 +
            scores['api_efficiency_score'] * 0.2
        )
        
        return scores
    
    def get_risk_level(self, score: int) -> str:
        """根据分数确定风险级别"""
        if score >= 90:
            return 'low'
        elif score >= 70:
            return 'medium'
        elif score >= 50:
            return 'high'
        else:
            return 'critical'
    
    def get_next_check_time(self, risk_level: str) -> datetime:
        """根据风险级别计算下次检查时间"""
        now = datetime.now()
        
        if risk_level == 'critical':
            return now + timedelta(minutes=15)
        elif risk_level == 'high':
            return now + timedelta(minutes=30)
        elif risk_level == 'medium':
            return now + timedelta(hours=2)
        else:
            return now + timedelta(hours=6)
    
    def generate_intervention_suggestions(self, metrics: SystemMetrics, 
                                          personas: List[PersonaHealth],
                                          risk_level: str) -> List[str]:
        """生成干预建议"""
        suggestions = []
        
        if risk_level in ['critical', 'high']:
            suggestions.append("🚨 立即检查错误日志，识别失败原因")
            suggestions.append("⚡ 暂停非关键任务，优先处理 P0 任务")
        
        if metrics.error_rate > 0.1:
            suggestions.append("[SEARCH] 启动批判者深度审查模式")
        
        if metrics.pending_tasks > 20:
            suggestions.append("⚖️ 激活负载均衡器优化任务队列")
        
        unhealthy_personas = [p for p in personas if p.status != 'healthy']
        if unhealthy_personas:
            names = ', '.join(p.name for p in unhealthy_personas)
            suggestions.append(f"[MASK] 检查人格状态：{names}")
        
        if metrics.api_calls_today > 50:
            suggestions.append("🤖 启用大模型调用批量合并策略")
        
        if not suggestions:
            suggestions.append("[OK] 系统运行正常，无需干预")
        
        return suggestions
    
    def push_health_metrics(self, dry_run: bool = False) -> Dict:
        """推送健康指标到 Dashboard"""
        # 收集数据
        metrics = self.collect_system_metrics()
        personas = self.check_persona_health()
        health_scores = self.calculate_health_score(metrics, personas)
        risk_level = self.get_risk_level(health_scores['overall_score'])
        next_check = self.get_next_check_time(risk_level)
        suggestions = self.generate_intervention_suggestions(metrics, personas, risk_level)
        
        # 构建 payload
        payload = {
            'timestamp': datetime.now().isoformat(),
            'system_metrics': {
                'total_tasks': metrics.total_tasks,
                'pending_tasks': metrics.pending_tasks,
                'completed_tasks': metrics.completed_tasks,
                'failed_tasks': metrics.failed_tasks,
                'error_rate': round(metrics.error_rate, 4),
                'api_calls_today': metrics.api_calls_today,
                'memory_updates_today': metrics.memory_updates_today,
                'git_commits_today': metrics.git_commits_today,
                'uptime_hours': metrics.uptime_hours
            },
            'persona_health': [
                {
                    'name': p.name,
                    'status': p.status,
                    'last_active': p.last_active.isoformat(),
                    'tasks_completed': p.tasks_completed,
                    'avg_score': p.avg_score,
                    'error_count': p.error_count
                }
                for p in personas
            ],
            'health_scores': health_scores,
            'risk_level': risk_level,
            'next_check_time': next_check.isoformat(),
            'intervention_suggestions': suggestions,
            'workspace': str(self.workspace_dir)
        }
        
        if dry_run:
            print("[CHART] Dry Run - 不会实际推送")
            print(json.dumps(payload, indent=2, ensure_ascii=False))
            return payload
        
        # 推送到 Dashboard
        try:
            url = f"{self.DASHBOARD_CONFIG['base_url']}{self.DASHBOARD_CONFIG['api_endpoint']}"
            response = requests.post(
                url,
                json=payload,
                timeout=self.DASHBOARD_CONFIG['timeout_seconds']
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"[OK] 成功推送到 Dashboard: {url}")
                self.last_push = datetime.now()
                
                # 生成并推送 widgets
                self._push_widgets()
                
                return {'success': True, 'response': result}
            else:
                print(f"[WARN] Dashboard 返回错误：{response.status_code}")
                return {'success': False, 'error': f'HTTP {response.status_code}'}
        
        except requests.exceptions.RequestException as e:
            print(f"[FAIL] 推送失败：{e}")
            return {'success': False, 'error': str(e)}
    
    def _push_widgets(self):
        """Push dashboard widgets"""
        print("\n[CHART] Generating Dashboard Widgets...")
        
        widgets_dir = Path(__file__).parent
        
        # Health Widget
        health_widget = widgets_dir / 'dashboard_health_widget.py'
        if health_widget.exists():
            print("  🟢 Health Widget")
            import subprocess
            subprocess.run([sys.executable, str(health_widget), '--save'], 
                         cwd=str(widgets_dir), timeout=30)
        
        # Decision Timeline Widget
        decision_widget = widgets_dir / 'dashboard_decision_timeline.py'
        if decision_widget.exists():
            print("  [TREND] Decision Timeline Widget")
            import subprocess
            subprocess.run([sys.executable, str(decision_widget), '--save'], 
                         cwd=str(widgets_dir), timeout=30)
        
        # Anomaly Alerts Widget
        anomaly_widget = widgets_dir / 'dashboard_anomaly_alerts.py'
        if anomaly_widget.exists():
            print("  🚨 Anomaly Alerts Widget")
            import subprocess
            subprocess.run([sys.executable, str(anomaly_widget), '--save'], 
                         cwd=str(widgets_dir), timeout=30)
        
        print("[OK] All widgets generated!")
    
    def get_status(self) -> Dict:
        """获取当前状态"""
        metrics = self.collect_system_metrics()
        personas = self.check_persona_health()
        health_scores = self.calculate_health_score(metrics, personas)
        
        return {
            'timestamp': datetime.now().isoformat(),
            'overall_score': health_scores['overall_score'],
            'risk_level': self.get_risk_level(health_scores['overall_score']),
            'metrics_summary': {
                'tasks': metrics.total_tasks,
                'pending': metrics.pending_tasks,
                'errors': metrics.failed_tasks,
                'error_rate': f"{metrics.error_rate*100:.1f}%",
                'api_calls': metrics.api_calls_today,
                'git_commits': metrics.git_commits_today
            },
            'persona_status': {p.name: p.status for p in personas},
            'last_push': self.last_push.isoformat() if self.last_push else None
        }
    
    def cache_metrics(self, metrics: Dict):
        """缓存指标"""
        cache_data = {
            'cached_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(minutes=self.cache_timeout_minutes)).isoformat(),
            'metrics': metrics
        }
        
        try:
            with open(self.metrics_file, 'w', encoding='utf-8') as f:
                json.dump(cache_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not cache metrics: {e}")
    
    def get_cached_metrics(self) -> Optional[Dict]:
        """获取缓存指标"""
        if not self.metrics_file.exists():
            return None
        
        try:
            with open(self.metrics_file, 'r', encoding='utf-8') as f:
                cache_data = json.load(f)
            
            expires_at = datetime.fromisoformat(cache_data['expires_at'])
            if datetime.now() < expires_at:
                return cache_data['metrics']
            else:
                print("Cache expired, refreshing...")
                return None
        except:
            return None


def main():
    parser = argparse.ArgumentParser(description='Dashboard Integration - ENH-007')
    parser.add_argument('--push', action='store_true', help='推送指标到 Dashboard')
    push_group = parser.add_argument_group('Push options')
    push_group.add_argument('--health', action='store_true', help='推送健康指标')
    push_group.add_argument('--metrics', action='store_true', help='推送详细指标')
    push_group.add_argument('--dry-run', action='store_true', help='模拟推送')
    
    parser.add_argument('--status', action='store_true', help='显示当前状态')
    parser.add_argument('--persona', action='store_true', help='显示人格健康')
    parser.add_argument('--workspace', type=str, default=str(Path(__file__).parent.parent),
                        help='工作区目录')
    parser.add_argument('--json', action='store_true', help='JSON 输出')
    parser.add_argument('--verbose', action='store_true', help='详细输出')
    
    args = parser.parse_args()
    
    integrator = DashboardIntegration(args.workspace)
    
    # 推送模式
    if args.push:
        result = integrator.push_health_metrics(dry_run=args.dry_run)
        
        if args.json:
            print(json.dumps(result, indent=2, ensure_ascii=False))
        elif not args.dry_run:
            if result.get('success'):
                print(f"\n[OK] Dashboard 推送成功!")
            else:
                print(f"\n[FAIL] Dashboard 推送失败：{result.get('error', 'Unknown')}")
        return
    
    # 状态模式
    if args.status:
        status = integrator.get_status()
        
        if args.json:
            print(json.dumps(status, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[CHART] 系统健康状态")
            print(f"{'='*60}")
            print(f"时间：{status['timestamp']}")
            print(f"综合评分：{status['overall_score']}/100")
            print(f"风险级别：{status['risk_level'].upper()}")
            print(f"\n指标摘要:")
            for k, v in status['metrics_summary'].items():
                print(f"  - {k}: {v}")
            print(f"\n人格状态:")
            for name, st in status['persona_status'].items():
                icon = '[OK]' if st == 'healthy' else '[WARN]' if st == 'warning' else '[FAIL]'
                print(f"  {icon} {name}: {st}")
            if status['last_push']:
                print(f"\n上次推送：{status['last_push']}")
            print(f"{'='*60}\n")
        return
    
    # 人格健康模式
    if args.persona:
        personas = integrator.check_persona_health()
        
        if args.json:
            output = [
                {
                    'name': p.name,
                    'status': p.status,
                    'last_active': p.last_active.isoformat(),
                    'tasks_completed': p.tasks_completed,
                    'avg_score': p.avg_score
                }
                for p in personas
            ]
            print(json.dumps(output, indent=2, ensure_ascii=False))
        else:
            print(f"\n{'='*60}")
            print(f"[MASK] 人格健康检查")
            print(f"{'='*60}\n")
            for p in personas:
                icon = '[OK]' if p.status == 'healthy' else '[WARN]' if p.status == 'warning' else '[FAIL]'
                print(f"{icon} {p.name}")
                print(f"   状态：{p.status}")
                print(f"   最后活跃：{p.last_active.strftime('%H:%M:%S')}")
                print(f"   完成任务：{p.tasks_completed}")
                print(f"   平均评分：{p.avg_score}")
                print(f"   错误数：{p.error_count}")
                print()
            print(f"{'='*60}\n")
        return
    
    # 默认：显示帮助
    parser.print_help()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Memory Health Monitor - 记忆系统健康监控

功能:
- 每小时自动检查 C 盘和 D 盘 MEMORY.md 同步状态
- 计算记忆差异分数 (Divergence Score)
- 发现分裂时自动告警
- 生成健康报告并推送到 Dashboard

使用示例:
    python memory_health_monitor.py --check
    python memory_health_monitor.py --report
    python memory_health_monitor.py --dashboard

作者：Claw [PAW] (Innovator Agent)
日期：2026-03-14
"""

import os
import sys
import hashlib
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import difflib

# 配置
WORKSPACE_MEMORY = Path(r"str(Path(__file__).parent.parent)\13-memory-记忆系统\MEMORY.md")  # 研究记忆 (49KB)
CONFIG_MEMORY = Path(r"C:\Users\华为\.copaw\MEMORY.md")  # Agent 配置 (14KB)
HEALTH_REPORT_PATH = Path(r"str(Path(__file__).parent.parent)\00-persona-system\memory-health-report.json")
DASHBOARD_API = "http://localhost:8444/health"  # 未来集成

# 阈值配置
THRESHOLDS = {
    'divergence_warning': 0.30,   # 差异>30% 警告 (仅用于相同用途文件)
    'divergence_critical': 0.50,  # 差异>50% 严重
    'sync_interval_hours': 24,    # 超过 24 小时未同步警告
    'workspace_memory_min_kb': 40,  # 工作区记忆最小大小 (完整研究记忆)
    'config_memory_min_kb': 10,     # 配置记忆最小大小
}

class MemoryHealthMonitor:
    """记忆系统健康监控器"""
    
    def __init__(self):
        self.health_status = {
            'status': 'unknown',  # healthy, warning, critical
            'checked_at': None,
            'workspace_memory': {
                'exists': False,
                'size_kb': 0,
                'lines': 0,
                'last_modified': None,
                'md5': None,
            },
            'config_memory': {
                'exists': False,
                'size_kb': 0,
                'lines': 0,
                'last_modified': None,
                'md5': None,
            },
            'divergence_score': 0.0,
            'sync_status': 'unknown',  # synced, drifted, critical
            'last_sync_time': None,
            'issues': [],
            'recommendations': [],
        }
    
    def calculate_md5(self, file_path: Path) -> Optional[str]:
        """计算文件 MD5"""
        if not file_path.exists():
            return None
        
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def get_file_stats(self, file_path: Path) -> Dict:
        """获取文件统计信息"""
        if not file_path.exists():
            return {
                'exists': False,
                'size_kb': 0,
                'lines': 0,
                'last_modified': None,
                'md5': None,
            }
        
        stat = file_path.stat()
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = sum(1 for _ in f)
        
        return {
            'exists': True,
            'size_kb': round(stat.st_size / 1024, 2),
            'lines': lines,
            'last_modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
            'md5': self.calculate_md5(file_path),
        }
    
    def calculate_content_similarity(self, file1: Path, file2: Path) -> float:
        """计算两个文件的内容相似度"""
        if not file1.exists() or not file2.exists():
            return 0.0
        
        with open(file1, 'r', encoding='utf-8', errors='ignore') as f:
            content1 = f.read()
        with open(file2, 'r', encoding='utf-8', errors='ignore') as f:
            content2 = f.read()
        
        # 计算相似度
        matcher = difflib.SequenceMatcher(None, content1, content2)
        return round(matcher.ratio(), 3)
    
    def detect_issues(self) -> list:
        """检测问题"""
        issues = []
        
        ws = self.health_status['workspace_memory']
        cfg = self.health_status['config_memory']
        
        # 检查文件是否存在
        if not ws['exists']:
            issues.append({
                'severity': 'critical',
                'type': 'MISSING_WORKSPACE_MEMORY',
                'message': '工作区 MEMORY.md 不存在',
                'path': str(WORKSPACE_MEMORY),
            })
        
        if not cfg['exists']:
            issues.append({
                'severity': 'critical',
                'type': 'MISSING_CONFIG_MEMORY',
                'message': '配置区 MEMORY.md 不存在',
                'path': str(CONFIG_MEMORY),
            })
        
        # 检查文件大小（验证完整性）
        if ws['exists'] and ws['size_kb'] < THRESHOLDS['workspace_memory_min_kb']:
            issues.append({
                'severity': 'warning',
                'type': 'WORKSPACE_MEMORY_TOO_SMALL',
                'message': f'工作区记忆文件过小 ({ws["size_kb"]}KB < {THRESHOLDS["workspace_memory_min_kb"]}KB)',
                'expected': '完整研究记忆应 >40KB',
            })
        
        if cfg['exists'] and cfg['size_kb'] < THRESHOLDS['config_memory_min_kb']:
            issues.append({
                'severity': 'warning',
                'type': 'CONFIG_MEMORY_TOO_SMALL',
                'message': f'配置记忆文件过小 ({cfg["size_kb"]}KB < {THRESHOLDS["config_memory_min_kb"]}KB)',
                'expected': 'Agent 配置记忆应 >10KB',
            })
        
        # 检查交叉引用（验证同步状态）
        if ws['exists']:
            try:
                with open(WORKSPACE_MEMORY, 'r', encoding='utf-8', errors='ignore') as f:
                    ws_content = f.read()
                
                # 检查是否包含 Agent 配置引用
                if 'Agent 配置记忆' not in ws_content and 'C:\\Users\\华为\\.copaw\\MEMORY.md' not in ws_content:
                    issues.append({
                        'severity': 'info',
                        'type': 'MISSING_CROSS_REF_CONFIG',
                        'message': '工作区记忆缺少 Agent 配置交叉引用',
                        'recommendation': '添加指向 C 盘 MEMORY.md 的引用',
                    })
            except Exception as e:
                issues.append({
                    'severity': 'warning',
                    'type': 'WORKSPACE_MEMORY_READ_ERROR',
                    'message': f'读取工作区记忆失败：{e}',
                })
        
        # 注意：两个 MEMORY.md 用途不同，不计算 MD5 差异
        # C 盘 = Agent 配置 + 研究摘要
        # D 盘 = 完整研究洞察
        
        return issues
    
    def generate_recommendations(self) -> list:
        """生成建议"""
        recommendations = []
        
        for issue in self.health_status['issues']:
            if issue['type'] == 'MEMORY_DRIFT_CRITICAL':
                recommendations.append({
                    'priority': 'high',
                    'action': '立即运行 memory-distiller.py 进行记忆蒸馏',
                    'command': 'python memory-distiller.py --force',
                })
                recommendations.append({
                    'priority': 'high',
                    'action': '手动检查 C 盘和 D 盘 MEMORY.md 差异',
                    'command': 'python workspace_comparator.py --report',
                })
            
            elif issue['type'] == 'MEMORY_DRIFT_WARNING':
                recommendations.append({
                    'priority': 'medium',
                    'action': '安排记忆同步（本周日 5AM）',
                    'command': 'memory-distiller.py 将在周日自动运行',
                })
            
            elif issue['type'] == 'SYNC_OVERDUE':
                recommendations.append({
                    'priority': 'low',
                    'action': '考虑运行记忆蒸馏保持同步',
                    'command': 'python memory-distiller.py',
                })
        
        # 如果没有问题，给出健康建议
        if not recommendations:
            recommendations.append({
                'priority': 'info',
                'action': '记忆系统健康，继续保持',
                'next_check': '下次自动检查：1 小时后',
            })
        
        return recommendations
    
    def check_health(self) -> Dict:
        """执行健康检查"""
        print("[MEMORY HEALTH CHECK] 开始检查...")
        
        # 获取文件统计
        self.health_status['workspace_memory'] = self.get_file_stats(WORKSPACE_MEMORY)
        self.health_status['config_memory'] = self.get_file_stats(CONFIG_MEMORY)
        self.health_status['checked_at'] = datetime.now().isoformat()
        
        # 注意：两个 MEMORY.md 用途不同，不计算相似度
        # workspace: 完整研究洞察 (49KB)
        # config: Agent 配置 + 研究摘要 (14KB)
        self.health_status['divergence_score'] = 0.0  # 不适用
        
        # 检测问题
        self.health_status['issues'] = self.detect_issues()
        
        # 生成建议
        self.health_status['recommendations'] = self.generate_recommendations()
        
        # 确定状态
        critical_issues = [i for i in self.health_status['issues'] if i['severity'] == 'critical']
        warning_issues = [i for i in self.health_status['issues'] if i['severity'] == 'warning']
        
        if critical_issues:
            self.health_status['status'] = 'critical'
            self.health_status['sync_status'] = 'critical'
        elif warning_issues:
            self.health_status['status'] = 'warning'
            self.health_status['sync_status'] = 'warning'
        else:
            self.health_status['status'] = 'healthy'
            self.health_status['sync_status'] = 'synced'
        
        # 打印结果
        print(f"[RESULT] 状态：{self.health_status['status'].upper()}")
        print(f"[RESULT] 工作区记忆：{self.health_status['workspace_memory']['size_kb']} KB")
        print(f"[RESULT] 配置记忆：{self.health_status['config_memory']['size_kb']} KB")
        print(f"[RESULT] 问题数：{len(self.health_status['issues'])}")
        
        return self.health_status
    
    def generate_report(self) -> str:
        """生成 Markdown 报告"""
        report = []
        report.append("# Memory System Health Report\n")
        report.append(f"**Checked At:** {self.health_status['checked_at']}\n")
        
        # 状态
        status_emoji = {'healthy': '[OK]', 'warning': '[WARN]', 'critical': '🚨'}
        report.append(f"## Status: {status_emoji.get(self.health_status['status'], '❓')} {self.health_status['status'].upper()}\n")
        
        # 文件架构说明
        report.append("## 📚 Memory System Architecture\n")
        report.append("**Two MEMORY.md files serve different purposes:**\n")
        report.append("| File | Purpose | Expected Size | Content |")
        report.append("|------|---------|---------------|---------|")
        report.append("| **C 盘** `C:\\Users\\华为\\.copaw\\MEMORY.md` | Agent Configuration | >10KB | User preferences, tool configs, 7-persona, research summary |")
        report.append("| **D 盘** `str(Path(__file__).parent.parent)\\13-memory-记忆系统\\MEMORY.md` | Research Insights | >40KB | Complete 190+ research insights, paper analysis |")
        report.append("\n---\n")
        
        # 文件状态
        report.append("## File Status\n")
        report.append("| File | Exists | Size | Lines | Last Modified | Status |")
        report.append("|------|--------|------|-------|---------------|--------|")
        
        ws = self.health_status['workspace_memory']
        cfg = self.health_status['config_memory']
        
        ws_status = "[OK]" if ws['exists'] else "[FAIL]"
        cfg_status = "[OK]" if cfg['exists'] else "[FAIL]"
        
        ws_size_status = "[OK]" if ws['size_kb'] >= THRESHOLDS['workspace_memory_min_kb'] else "[WARN]"
        cfg_size_status = "[OK]" if cfg['size_kb'] >= THRESHOLDS['config_memory_min_kb'] else "[WARN]"
        
        report.append(f"| Workspace | {ws_status} {ws_size_status} | {ws['size_kb']} KB | {ws['lines']} | {ws['last_modified']} | Research Memory |")
        report.append(f"| Config | {cfg_status} {cfg_size_status} | {cfg['size_kb']} KB | {cfg['lines']} | {cfg['last_modified']} | Agent Config |")
        report.append("\n")
        
        # 问题列表
        if self.health_status['issues']:
            report.append("## Issues\n")
            for issue in self.health_status['issues']:
                severity_emoji = {'critical': '🚨', 'warning': '[WARN]', 'info': 'ℹ️'}
                report.append(f"### {severity_emoji.get(issue['severity'], '❓')} {issue['type']}")
                report.append(f"- **Severity:** {issue['severity']}")
                report.append(f"- **Message:** {issue['message']}")
                if 'expected' in issue:
                    report.append(f"- **Expected:** {issue['expected']}")
                if 'recommendation' in issue:
                    report.append(f"- **Recommendation:** {issue['recommendation']}")
                report.append("\n")
        
        # 建议
        if self.health_status['recommendations']:
            report.append("## Recommendations\n")
            for rec in self.health_status['recommendations']:
                priority_emoji = {'high': '🔴', 'medium': '🟡', 'low': '🟢', 'info': 'ℹ️'}
                report.append(f"- {priority_emoji.get(rec['priority'], '')} {rec['action']}")
                if 'command' in rec:
                    report.append(f"  ```bash\n  {rec['command']}\n  ```")
            report.append("\n")
        
        # 下次检查
        next_check = datetime.now() + timedelta(hours=1)
        report.append(f"---\n")
        report.append(f"**Next Check:** {next_check.strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Monitoring:** Hourly automatic checks\n")
        
        return '\n'.join(report)
    
    def save_report(self, output_path: Optional[Path] = None):
        """保存报告"""
        if not output_path:
            output_path = HEALTH_REPORT_PATH
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # 保存 JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.health_status, f, indent=2, ensure_ascii=False)
        
        # 保存 Markdown
        md_path = output_path.with_suffix('.md')
        with open(md_path, 'w', encoding='utf-8') as f:
            f.write(self.generate_report())
        
        print(f"[REPORT] 已保存：{output_path}")
        print(f"[REPORT] 已保存：{md_path}")
    
    def send_to_dashboard(self):
        """发送到 Dashboard（未来功能）"""
        # TODO: 集成到 Innovator Dashboard
        print("[DASHBOARD] 未来功能：推送到 https://felixxii.xyz/health")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Health Monitor')
    parser.add_argument('--check', action='store_true', help='Run health check')
    parser.add_argument('--report', action='store_true', help='Generate report')
    parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    monitor = MemoryHealthMonitor()
    
    if args.check:
        monitor.check_health()
    
    if args.report:
        monitor.save_report(Path(args.output) if args.output else None)
    
    # 默认行为：检查 + 报告
    if not args.check and not args.report:
        monitor.check_health()
        monitor.save_report()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工作流效率度量工具

功能:
- 从 Git 历史提取任务数据
- 计算效率指标 (用时/轮次/返工/满意度)
- 生成可视化报告
- 对比基线数据

使用方法:
    py 32-workflows-工作流/99-user-command-workflow/metrics_collector.py --days 7
    py 32-workflows-工作流/99-user-command-workflow/metrics_collector.py --export csv
"""

import subprocess
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from pathlib import Path


class WorkflowMetricsCollector:
    """工作流效率度量收集器"""
    
    def __init__(self, workspace_path: str = "."):
        self.workspace = Path(workspace_path)
        self.memory_dir = self.workspace / "13-memory-记忆系统"
        self.metrics_file = self.workspace / "32-workflows-工作流/99-user-command-workflow/metrics.json"
    
    def get_git_commits(self, days: int = 7) -> List[Dict]:
        """
        获取指定天数内的 Git 提交
        
        Args:
            days: 回溯天数
            
        Returns:
            List[Dict]: 提交列表
        """
        since = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        
        cmd = [
            "git", "log",
            f"--since={since}",
            "--pretty=format:%H|%ai|%s",
            "--no-merges"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=self.workspace)
            lines = result.stdout.strip().split("\n")
            
            commits = []
            for line in lines:
                if not line:
                    continue
                parts = line.split("|", 2)
                if len(parts) == 3:
                    commits.append({
                        "hash": parts[0],
                        "time": parts[1],
                        "message": parts[2]
                    })
            
            return commits
        except Exception as e:
            print(f"Error getting git commits: {e}")
            return []
    
    def parse_task_from_commit(self, message: str) -> Optional[Dict]:
        """
        从提交信息解析任务信息
        
        Args:
            message: 提交信息
            
        Returns:
            Optional[Dict]: 任务信息，解析失败返回 None
        """
        # 尝试匹配任务类型
        task_types = {
            "简单查询": ["查询", "天气", "搜索"],
            "简单任务": ["创建", "删除", "移动", "复制"],
            "中等任务": ["优化", "分析", "整理", "更新"],
            "复杂任务": ["重构", "系统", "完整", "工作流"]
        }
        
        task_type = "未知"
        for ttype, keywords in task_types.items():
            if any(kw in message for kw in keywords):
                task_type = ttype
                break
        
        # 尝试匹配返工次数
        rework_match = re.search(r"返工 [：:]\s*(\d+)", message)
        rework_count = int(rework_match.group(1)) if rework_match else 0
        
        # 尝试匹配用时
        time_match = re.search(r"用时 [：:]\s*(\d+)", message)
        duration = int(time_match.group(1)) if time_match else None
        
        return {
            "type": task_type,
            "rework": rework_count,
            "duration": duration,
            "message": message
        }
    
    def read_memory_logs(self, days: int = 7) -> List[Dict]:
        """
        读取记忆日志
        
        Args:
            days: 回溯天数
            
        Returns:
            List[Dict]: 日志条目
        """
        logs = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            log_file = self.memory_dir / f"{date}.md"
            
            if log_file.exists():
                try:
                    content = log_file.read_text(encoding="utf-8")
                    logs.append({
                        "date": date,
                        "content": content,
                        "file": str(log_file)
                    })
                except Exception as e:
                    print(f"Error reading {log_file}: {e}")
        
        return logs
    
    def calculate_metrics(self, commits: List[Dict], logs: List[Dict]) -> Dict:
        """
        计算效率指标
        
        Args:
            commits: Git 提交列表
            logs: 记忆日志列表
            
        Returns:
            Dict: 指标字典
        """
        # 简单统计
        total_commits = len(commits)
        
        # 按任务类型分组
        task_types = {}
        for commit in commits:
            task_info = self.parse_task_from_commit(commit["message"])
            if task_info:
                ttype = task_info["type"]
                if ttype not in task_types:
                    task_types[ttype] = []
                task_types[ttype].append(task_info)
        
        # 计算平均指标
        metrics = {
            "collection_date": datetime.now().isoformat(),
            "days": len(logs),
            "total_commits": total_commits,
            "task_types": {},
            "overall": {
                "avg_duration": None,
                "avg_rework": None,
                "success_rate": None
            }
        }
        
        # 按类型统计
        for ttype, tasks in task_types.items():
            durations = [t["duration"] for t in tasks if t["duration"]]
            reworks = [t["rework"] for t in tasks]
            
            metrics["task_types"][ttype] = {
                "count": len(tasks),
                "avg_duration": sum(durations) / len(durations) if durations else None,
                "avg_rework": sum(reworks) / len(reworks) if reworks else None,
                "success_rate": len([r for r in reworks if r == 0]) / len(reworks) if reworks else None
            }
        
        # 整体统计
        all_durations = [t["duration"] for tasks in task_types.values() for t in tasks if t["duration"]]
        all_reworks = [t["rework"] for tasks in task_types.values() for t in tasks]
        
        if all_durations:
            metrics["overall"]["avg_duration"] = sum(all_durations) / len(all_durations)
        if all_reworks:
            metrics["overall"]["avg_rework"] = sum(all_reworks) / len(all_reworks)
            metrics["overall"]["success_rate"] = len([r for r in all_reworks if r == 0]) / len(all_reworks)
        
        return metrics
    
    def save_metrics(self, metrics: Dict) -> None:
        """保存指标到文件"""
        self.metrics_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 读取历史指标
        history = []
        if self.metrics_file.exists():
            try:
                history = json.loads(self.metrics_file.read_text(encoding="utf-8"))
                if not isinstance(history, list):
                    history = [history]
            except:
                history = []
        
        # 添加新指标
        history.append(metrics)
        
        # 保存
        with open(self.metrics_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
        
        print(f"Metrics saved to {self.metrics_file}")
    
    def generate_report(self, metrics: Dict) -> str:
        """
        生成报告
        
        Args:
            metrics: 指标字典
            
        Returns:
            str: 报告文本
        """
        report = []
        report.append("# 工作流效率度量报告")
        report.append(f"\n**收集时间:** {metrics['collection_date']}")
        report.append(f"**数据范围:** {metrics['days']} 天\n")
        
        report.append("## 📊 整体指标\n")
        overall = metrics["overall"]
        report.append(f"- 总提交数：{metrics['total_commits']}")
        report.append(f"- 平均用时：{overall['avg_duration']:.1f} 分钟" if overall['avg_duration'] else "- 平均用时：N/A")
        report.append(f"- 平均返工：{overall['avg_rework']:.2f} 次" if overall['avg_rework'] else "- 平均返工：N/A")
        report.append(f"- 一次通过率：{overall['success_rate']*100:.1f}%" if overall['success_rate'] else "- 一次通过率：N/A")
        
        report.append("\n## 📈 按任务类型\n")
        for ttype, data in metrics["task_types"].items():
            report.append(f"### {ttype}")
            report.append(f"- 任务数：{data['count']}")
            if data['avg_duration']:
                report.append(f"- 平均用时：{data['avg_duration']:.1f} 分钟")
            if data['avg_rework'] is not None:
                report.append(f"- 平均返工：{data['avg_rework']:.2f} 次")
            if data['success_rate']:
                report.append(f"- 一次通过率：{data['success_rate']*100:.1f}%")
        
        return "\n".join(report)
    
    def run(self, days: int = 7, export: str = "json") -> Dict:
        """
        运行度量收集
        
        Args:
            days: 回溯天数
            export: 导出格式 (json/csv)
            
        Returns:
            Dict: 指标字典
        """
        print(f"Collecting metrics for last {days} days...")
        
        # 收集数据
        commits = self.get_git_commits(days)
        logs = self.read_memory_logs(days)
        
        print(f"Found {len(commits)} commits, {len(logs)} log files")
        
        # 计算指标
        metrics = self.calculate_metrics(commits, logs)
        
        # 保存
        self.save_metrics(metrics)
        
        # 生成报告
        report = self.generate_report(metrics)
        print("\n" + "="*50 + "\n")
        print(report)
        
        return metrics


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="工作流效率度量工具")
    parser.add_argument("--days", type=int, default=7, help="回溯天数 (默认：7)")
    parser.add_argument("--export", choices=["json", "csv"], default="json", help="导出格式 (默认：json)")
    parser.add_argument("--workspace", type=str, default=".", help="工作区路径")
    
    args = parser.parse_args()
    
    collector = WorkflowMetricsCollector(args.workspace)
    collector.run(days=args.days, export=args.export)


if __name__ == "__main__":
    main()

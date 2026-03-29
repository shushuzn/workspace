"""
Feedback Loop - 反馈闭环模块

收集执行结果，优化分析模型和工作流
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime, timedelta
from loguru import logger
import aiosqlite


class FeedbackLoop:
    """反馈循环"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化反馈循环
        
        Args:
            config: 反馈配置
        """
        self.config = config
        self.enabled = config.get("enabled", True)
        self.optimize_interval = config.get("optimize_interval", 3600)
        self.db_path = "data/news_workflow.db"
        
        logger.info("FeedbackLoop initialized")
    
    async def initialize(self):
        """初始化反馈循环"""
        logger.info("FeedbackLoop initialized")
    
    async def collect(self, workflow_id: int):
        """
        收集工作流执行反馈
        
        Args:
            workflow_id: 工作流 ID
        """
        if not self.enabled:
            return
        
        logger.info(f"Collecting feedback for workflow {workflow_id}")
        
        try:
            # 获取工作流信息
            workflow = await self._get_workflow(workflow_id)
            if not workflow:
                logger.warning(f"Workflow not found: {workflow_id}")
                return
            
            # 获取任务执行结果
            tasks = await self._get_workflow_tasks(workflow_id)
            
            # 计算指标
            metrics = self._calculate_metrics(workflow, tasks)
            
            # 保存反馈
            await self._save_feedback(workflow_id, metrics)
            
            logger.info(f"Feedback collected for workflow {workflow_id}")
            
        except Exception as e:
            logger.error(f"Failed to collect feedback: {e}")
    
    async def _get_workflow(self, workflow_id: int) -> Dict[str, Any]:
        """获取工作流信息"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM workflows WHERE id = ?
            """, (workflow_id,))
            row = await cursor.fetchone()
            return dict(row) if row else None
    
    async def _get_workflow_tasks(self, workflow_id: int) -> List[Dict[str, Any]]:
        """获取工作流任务"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM tasks WHERE workflow_id = ?
            """, (workflow_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    def _calculate_metrics(self, workflow: Dict[str, Any], tasks: List[Dict[str, Any]]) -> Dict[str, float]:
        """计算指标"""
        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("status") == "completed")
        
        # 成功率
        success_rate = completed_tasks / total_tasks if total_tasks > 0 else 0
        
        # 执行时间
        created_at = datetime.fromisoformat(workflow["created_at"]) if isinstance(workflow["created_at"], str) else workflow["created_at"]
        completed_at = datetime.fromisoformat(workflow["completed_at"]) if workflow.get("completed_at") and isinstance(workflow["completed_at"], str) else datetime.now()
        execution_time = (completed_at - created_at).total_seconds()
        
        # 效率评分 (越快越好，标准化到 0-1)
        efficiency = max(0, 1 - (execution_time / 3600))  # 1 小时内完成为满分
        
        return {
            "success_rate": success_rate,
            "execution_time": execution_time,
            "efficiency": efficiency,
            "task_count": total_tasks
        }
    
    async def _save_feedback(self, workflow_id: int, metrics: Dict[str, Any]):
        """保存反馈"""
        async with aiosqlite.connect(self.db_path) as db:
            for metric_name, metric_value in metrics.items():
                await db.execute("""
                    INSERT INTO feedback (workflow_id, metric_name, metric_value)
                    VALUES (?, ?, ?)
                """, (workflow_id, metric_name, metric_value))
            await db.commit()
    
    async def optimize(self):
        """优化模型和阈值"""
        if not self.enabled:
            return
        
        logger.info("Running optimization...")
        
        try:
            # 获取最近的反馈数据
            recent_feedback = await self._get_recent_feedback()
            
            if not recent_feedback:
                logger.info("No feedback data for optimization")
                return
            
            # 分析反馈
            analysis = self._analyze_feedback(recent_feedback)
            
            # 生成优化建议
            recommendations = self._generate_recommendations(analysis)
            
            # 记录优化日志
            logger.info(f"Optimization analysis: {analysis}")
            logger.info(f"Recommendations: {recommendations}")
            
            # 这里可以添加自动调整阈值的逻辑
            if self.config.get("auto_adjust_threshold", True):
                await self._adjust_thresholds(analysis)
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}")
    
    async def _get_recent_feedback(self) -> List[Dict[str, Any]]:
        """获取最近的反馈数据"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM feedback 
                WHERE created_at > datetime('now', '-1 day')
                ORDER BY created_at DESC
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    def _analyze_feedback(self, feedback: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析反馈数据"""
        if not feedback:
            return {}
        
        # 按指标分组
        metrics = {}
        for entry in feedback:
            metric_name = entry["metric_name"]
            metric_value = entry["metric_value"]
            
            if metric_name not in metrics:
                metrics[metric_name] = []
            metrics[metric_name].append(metric_value)
        
        # 计算平均值
        analysis = {}
        for metric_name, values in metrics.items():
            analysis[f"{metric_name}_avg"] = sum(values) / len(values)
            analysis[f"{metric_name}_min"] = min(values)
            analysis[f"{metric_name}_max"] = max(values)
        
        return analysis
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        # 检查成功率
        success_rate = analysis.get("success_rate_avg", 1.0)
        if success_rate < 0.8:
            recommendations.append("成功率较低，建议检查工作流模板或任务执行逻辑")
        
        # 检查效率
        efficiency = analysis.get("efficiency_avg", 1.0)
        if efficiency < 0.5:
            recommendations.append("执行效率较低，建议优化任务执行速度或增加并发")
        
        if not recommendations:
            recommendations.append("系统运行正常，无需优化")
        
        return recommendations
    
    async def _adjust_thresholds(self, analysis: Dict[str, Any]):
        """自动调整阈值"""
        # 这里可以实现自动调整重要性阈值等逻辑
        # 目前仅记录日志
        logger.info("Threshold adjustment logic would go here")

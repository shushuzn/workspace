"""
Workflow Manager - 工作流管理器

负责工作流模板匹配、创建、状态管理
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from loguru import logger
import yaml
import aiosqlite


class WorkflowManager:
    """工作流管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化工作流管理器
        
        Args:
            config: 工作流配置
        """
        self.config = config
        self.templates = {}
        self.db_path = "data/news_workflow.db"
        
        logger.info("WorkflowManager initialized")
    
    async def load_templates(self):
        """加载工作流模板"""
        templates_dir = Path("config/workflows")
        templates_dir.mkdir(parents=True, exist_ok=True)
        
        # 如果模板目录为空，创建默认模板
        if not any(templates_dir.glob("*.yaml")):
            await self._create_default_templates(templates_dir)
        
        # 加载所有模板
        for template_file in templates_dir.glob("*.yaml"):
            try:
                with open(template_file, "r", encoding="utf-8") as f:
                    template = yaml.safe_load(f)
                    self.templates[template["id"]] = template
                    logger.info(f"Loaded template: {template['id']}")
            except Exception as e:
                logger.error(f"Failed to load template {template_file}: {e}")
        
        logger.info(f"Loaded {len(self.templates)} workflow templates")
    
    async def _create_default_templates(self, templates_dir: Path):
        """创建默认工作流模板"""
        
        # 科技新闻调研模板
        tech_research = {
            "id": "tech_research",
            "name": "科技新闻调研",
            "description": "针对科技新闻自动调研相关 GitHub 项目",
            "trigger": {
                "category": "tech",
                "min_importance": 0.7
            },
            "tasks": [
                {
                    "name": "搜索 GitHub 项目",
                    "description": "根据新闻关键词搜索相关 GitHub 项目",
                    "action": "github_search",
                    "priority": 10
                },
                {
                    "name": "分析项目活跃度",
                    "description": "分析项目的 stars、commit 频率、issue 活跃度",
                    "action": "analyze_project",
                    "priority": 8,
                    "depends_on": [0]
                },
                {
                    "name": "生成调研报告",
                    "description": "生成包含项目对比和分析的调研报告",
                    "action": "generate_report",
                    "priority": 6,
                    "depends_on": [1]
                }
            ]
        }
        
        # 市场监控模板
        market_monitor = {
            "id": "market_monitor",
            "name": "市场监控",
            "description": "监控市场动态并更新仪表板",
            "trigger": {
                "category": ["finance", "market"],
                "min_importance": 0.6
            },
            "tasks": [
                {
                    "name": "提取关键数据",
                    "description": "从新闻中提取关键市场数据",
                    "action": "extract_data",
                    "priority": 10
                },
                {
                    "name": "更新监控仪表板",
                    "description": "更新市场监控仪表板数据",
                    "action": "update_dashboard",
                    "priority": 8,
                    "depends_on": [0]
                },
                {
                    "name": "检查异常波动",
                    "description": "检查是否有异常波动并告警",
                    "action": "check_anomaly",
                    "priority": 7,
                    "depends_on": [1]
                }
            ]
        }
        
        # 风险预警模板
        risk_alert = {
            "id": "risk_alert",
            "name": "风险预警",
            "description": "针对负面新闻生成风险预警",
            "trigger": {
                "sentiment": "negative",
                "min_importance": 0.8
            },
            "tasks": [
                {
                    "name": "提取风险因素",
                    "description": "从新闻中提取风险因素",
                    "action": "extract_risks",
                    "priority": 10
                },
                {
                    "name": "评估影响范围",
                    "description": "评估风险的影响范围和程度",
                    "action": "assess_impact",
                    "priority": 9,
                    "depends_on": [0]
                },
                {
                    "name": "生成应对建议",
                    "description": "生成风险应对建议",
                    "action": "generate_recommendations",
                    "priority": 7,
                    "depends_on": [1]
                },
                {
                    "name": "高优先级推送",
                    "description": "将预警信息高优先级推送给相关人员",
                    "action": "urgent_push",
                    "priority": 10,
                    "depends_on": [2]
                }
            ]
        }
        
        # 竞品分析模板
        competitor_analysis = {
            "id": "competitor_analysis",
            "name": "竞品分析",
            "description": "针对竞品新闻进行分析",
            "trigger": {
                "category": "company",
                "keywords": ["竞品", "竞争对手", "竞争"],
                "min_importance": 0.7
            },
            "tasks": [
                {
                    "name": "识别竞品",
                    "description": "从新闻中识别竞品信息",
                    "action": "identify_competitor",
                    "priority": 10
                },
                {
                    "name": "收集竞品信息",
                    "description": "收集竞品的最新动态和信息",
                    "action": "gather_intel",
                    "priority": 8,
                    "depends_on": [0]
                },
                {
                    "name": "对比分析",
                    "description": "与我方产品进行对比分析",
                    "action": "compare_analysis",
                    "priority": 6,
                    "depends_on": [1]
                }
            ]
        }
        
        # 保存模板文件
        for template in [tech_research, market_monitor, risk_alert, competitor_analysis]:
            template_path = templates_dir / f"{template['id']}.yaml"
            with open(template_path, "w", encoding="utf-8") as f:
                yaml.dump(template, f, allow_unicode=True, default_flow_style=False)
        
        logger.info(f"Created {4} default workflow templates")
    
    async def match_templates(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        匹配适用的工作流模板
        
        Args:
            analysis: 新闻分析结果
        
        Returns:
            匹配的模板列表
        """
        matched = []
        
        for template_id, template in self.templates.items():
            if self._matches_template(analysis, template):
                matched.append(template)
        
        logger.info(f"Matched {len(matched)} workflow templates")
        return matched
    
    def _matches_template(self, analysis: Dict[str, Any], template: Dict[str, Any]) -> bool:
        """检查新闻分析是否匹配模板触发条件"""
        trigger = template.get("trigger", {})
        
        # 检查分类
        if "category" in trigger:
            trigger_cat = trigger["category"]
            analysis_cat = analysis.get("category", "")
            
            if isinstance(trigger_cat, list):
                if analysis_cat not in trigger_cat:
                    return False
            elif trigger_cat != analysis_cat:
                return False
        
        # 检查情感
        if "sentiment" in trigger:
            if trigger["sentiment"] != analysis.get("sentiment", ""):
                return False
        
        # 检查重要性
        if "min_importance" in trigger:
            if analysis.get("importance", 0) < trigger["min_importance"]:
                return False
        
        # 检查关键词
        if "keywords" in trigger:
            news_keywords = analysis.get("keywords", [])
            trigger_keywords = trigger["keywords"]
            
            if not any(kw in news_keywords for kw in trigger_keywords):
                return False
        
        return True
    
    async def create_workflow(self, template_id: str, news_id: int, analysis: Dict[str, Any]) -> Optional[int]:
        """
        创建工作流实例
        
        Args:
            template_id: 模板 ID
            news_id: 新闻 ID
            analysis: 新闻分析结果
        
        Returns:
            工作流 ID
        """
        template = self.templates.get(template_id)
        if not template:
            logger.error(f"Template not found: {template_id}")
            return None
        
        async with aiosqlite.connect(self.db_path) as db:
            # 创建工作流记录
            cursor = await db.execute("""
                INSERT INTO workflows (template_id, news_id, status)
                VALUES (?, ?, 'pending')
            """, (template_id, news_id))
            workflow_id = cursor.lastrowid
            
            # 创建任务
            for idx, task_template in enumerate(template.get("tasks", [])):
                # 计算优先级（基于新闻重要性）
                base_priority = task_template.get("priority", 5)
                importance_boost = int(analysis.get("importance", 0.5) * 5)
                priority = min(10, base_priority + importance_boost)
                
                await db.execute("""
                    INSERT INTO tasks (workflow_id, name, description, priority, status)
                    VALUES (?, ?, ?, ?, 'pending')
                """, (
                    workflow_id,
                    task_template.get("name", f"Task {idx}"),
                    task_template.get("description", ""),
                    priority
                ))
            
            await db.commit()
        
        logger.info(f"Created workflow {workflow_id} from template {template_id}")
        return workflow_id
    
    async def get_pending_workflows(self) -> List[Dict[str, Any]]:
        """获取待处理的工作流"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM workflows WHERE status = 'pending'
                ORDER BY created_at ASC
            """)
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def get_workflow_tasks(self, workflow_id: int) -> List[Dict[str, Any]]:
        """获取工作流的任务列表"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("""
                SELECT * FROM tasks 
                WHERE workflow_id = ? AND status = 'pending'
                ORDER BY priority DESC, id ASC
            """, (workflow_id,))
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]
    
    async def update_task_status(self, task_id: int, result: Dict[str, Any]):
        """更新任务状态"""
        async with aiosqlite.connect(self.db_path) as db:
            status = "completed" if result.get("success", False) else "failed"
            await db.execute("""
                UPDATE tasks 
                SET status = ?, result = ?, completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, str(result), task_id))
            
            # 记录执行日志
            await db.execute("""
                INSERT INTO execution_log (task_id, action, result, error)
                VALUES (?, ?, ?, ?)
            """, (
                task_id,
                result.get("action", "unknown"),
                str(result.get("output", "")),
                result.get("error", "")
            ))
            
            await db.commit()
        
        logger.info(f"Updated task {task_id} status: {status}")
    
    async def complete_workflow(self, workflow_id: int):
        """完成工作流"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE workflows 
                SET status = 'completed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (workflow_id,))
            await db.commit()
        
        logger.info(f"Completed workflow {workflow_id}")
    
    async def mark_workflow_failed(self, workflow_id: int, error: str):
        """标记工作流失败"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("""
                UPDATE workflows 
                SET status = 'failed', completed_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (workflow_id,))
            await db.commit()
        
        logger.error(f"Workflow {workflow_id} failed: {error}")

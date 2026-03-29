"""
Task Executor - 任务执行器

负责执行工作流中的具体任务
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger
from datetime import datetime


class TaskExecutor:
    """任务执行器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化执行器
        
        Args:
            config: 执行器配置
        """
        self.config = config
        self.retry_enabled = config.get("retry", {}).get("enabled", True)
        self.max_retries = config.get("retry", {}).get("max_retries", 3)
        self.retry_delay = config.get("retry", {}).get("delay", 10)
        self.timeout = config.get("task_timeout", 600)
        
        logger.info("TaskExecutor initialized")
    
    async def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行任务
        
        Args:
            task: 任务信息
        
        Returns:
            执行结果
        """
        task_name = task.get("name", "Unknown Task")
        task_action = task.get("description", "")
        
        logger.info(f"Executing task: {task_name}")
        
        # 提取 action 类型
        action = self._extract_action(task)
        
        # 执行对应动作
        try:
            result = await asyncio.wait_for(
                self._execute_action(action, task),
                timeout=self.timeout
            )
            
            result["success"] = True
            result["action"] = action
            result["completed_at"] = datetime.now().isoformat()
            
            logger.info(f"Task completed: {task_name}")
            return result
            
        except asyncio.TimeoutError:
            logger.error(f"Task timeout: {task_name}")
            return {
                "success": False,
                "error": "Task timeout",
                "action": action
            }
            
        except Exception as e:
            logger.error(f"Task failed: {task_name}, error: {e}")
            
            # 重试逻辑
            if self.retry_enabled:
                return await self._retry_task(action, task, e)
            
            return {
                "success": False,
                "error": str(e),
                "action": action
            }
    
    def _extract_action(self, task: Dict[str, Any]) -> str:
        """从任务中提取 action 类型"""
        # 尝试从 description 或 name 中提取 action
        description = task.get("description", "").lower()
        name = task.get("name", "").lower()
        
        # 映射到预定义的 action
        action_map = {
            "github": "github_search",
            "搜索": "github_search",
            "分析": "analyze_project",
            "生成": "generate_report",
            "报告": "generate_report",
            "提取": "extract_data",
            "更新": "update_dashboard",
            "检查": "check_anomaly",
            "风险": "extract_risks",
            "评估": "assess_impact",
            "建议": "generate_recommendations",
            "推送": "urgent_push",
            "竞品": "identify_competitor",
            "收集": "gather_intel",
            "对比": "compare_analysis"
        }
        
        for keyword, action in action_map.items():
            if keyword in description or keyword in name:
                return action
        
        return "generic_task"
    
    async def _execute_action(self, action: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """执行具体动作"""
        
        action_handlers = {
            "github_search": self._github_search,
            "analyze_project": self._analyze_project,
            "generate_report": self._generate_report,
            "extract_data": self._extract_data,
            "update_dashboard": self._update_dashboard,
            "check_anomaly": self._check_anomaly,
            "extract_risks": self._extract_risks,
            "assess_impact": self._assess_impact,
            "generate_recommendations": self._generate_recommendations,
            "urgent_push": self._urgent_push,
            "identify_competitor": self._identify_competitor,
            "gather_intel": self._gather_intel,
            "compare_analysis": self._compare_analysis,
            "generic_task": self._generic_task
        }
        
        handler = action_handlers.get(action, self._generic_task)
        return await handler(task)
    
    async def _github_search(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """GitHub 搜索"""
        # 模拟实现 - 实际应调用 GitHub API
        await asyncio.sleep(1)  # 模拟 API 调用
        
        return {
            "output": {
                "query": task.get("description", ""),
                "results": [
                    {"name": "example-repo-1", "stars": 1000, "url": "https://github.com/example/repo1"},
                    {"name": "example-repo-2", "stars": 500, "url": "https://github.com/example/repo2"}
                ]
            }
        }
    
    async def _analyze_project(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """分析项目"""
        await asyncio.sleep(1)
        
        return {
            "output": {
                "activity_score": 0.8,
                "quality_score": 0.75,
                "recommendation": "值得关注"
            }
        }
    
    async def _generate_report(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """生成报告"""
        await asyncio.sleep(1)
        
        return {
            "output": {
                "report_path": "reports/tech_research_20260328.md",
                "summary": "调研报告已生成"
            }
        }
    
    async def _extract_data(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """提取数据"""
        await asyncio.sleep(0.5)
        
        return {
            "output": {
                "extracted_fields": ["价格", "涨跌幅", "成交量"],
                "values": [100.5, 2.3, 1000000]
            }
        }
    
    async def _update_dashboard(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """更新仪表板"""
        await asyncio.sleep(0.5)
        
        return {
            "output": {
                "dashboard_updated": True,
                "timestamp": datetime.now().isoformat()
            }
        }
    
    async def _check_anomaly(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """检查异常"""
        await asyncio.sleep(0.5)
        
        return {
            "output": {
                "anomaly_detected": False,
                "status": "正常"
            }
        }
    
    async def _extract_risks(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """提取风险"""
        await asyncio.sleep(0.5)
        
        return {
            "output": {
                "risks": ["市场风险", "政策风险"],
                "severity": "中等"
            }
        }
    
    async def _assess_impact(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """评估影响"""
        await asyncio.sleep(0.5)
        
        return {
            "output": {
                "impact_level": "中等",
                "affected_areas": ["业务 A", "业务 B"]
            }
        }
    
    async def _generate_recommendations(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """生成建议"""
        await asyncio.sleep(0.5)
        
        return {
            "output": {
                "recommendations": [
                    "建议 1: 加强监控",
                    "建议 2: 制定应急预案"
                ]
            }
        }
    
    async def _urgent_push(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """紧急推送"""
        await asyncio.sleep(0.5)
        
        return {
            "output": {
                "pushed": True,
                "channels": ["feishu", "telegram"]
            }
        }
    
    async def _identify_competitor(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """识别竞品"""
        await asyncio.sleep(0.5)
        
        return {
            "output": {
                "competitors": ["竞品 A", "竞品 B"],
                "confidence": 0.85
            }
        }
    
    async def _gather_intel(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """收集情报"""
        await asyncio.sleep(1)
        
        return {
            "output": {
                "intel_gathered": True,
                "sources": 3
            }
        }
    
    async def _compare_analysis(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """对比分析"""
        await asyncio.sleep(1)
        
        return {
            "output": {
                "comparison": {
                    "our_advantage": ["技术领先", "用户体验"],
                    "their_advantage": ["价格", "市场份额"]
                }
            }
        }
    
    async def _generic_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """通用任务处理"""
        await asyncio.sleep(0.5)
        
        return {
            "output": {
                "status": "completed",
                "note": "通用任务已执行"
            }
        }
    
    async def _retry_task(self, action: str, task: Dict[str, Any], error: Exception) -> Dict[str, Any]:
        """重试任务"""
        for attempt in range(1, self.max_retries + 1):
            logger.info(f"Retrying task (attempt {attempt}/{self.max_retries})")
            await asyncio.sleep(self.retry_delay * attempt)
            
            try:
                result = await self._execute_action(action, task)
                result["success"] = True
                result["retried"] = True
                result["retry_attempts"] = attempt
                return result
            except Exception as e:
                logger.warning(f"Retry {attempt} failed: {e}")
        
        return {
            "success": False,
            "error": f"Failed after {self.max_retries} retries: {str(error)}",
            "action": action,
            "retried": True,
            "retry_attempts": self.max_retries
        }

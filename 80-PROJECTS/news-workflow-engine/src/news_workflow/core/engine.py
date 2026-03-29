"""
Core Engine - 核心引擎

负责协调新闻获取、分析、工作流触发、执行和反馈的完整流程
"""

import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger
import yaml

from ..analyzer.analyzer import NewsAnalyzer
from ..workflow.manager import WorkflowManager
from ..executor.runner import TaskExecutor
from ..feedback.loop import FeedbackLoop
from ..push.notifier import PushNotifier


class NewsWorkflowEngine:
    """新闻工作流引擎主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化引擎
        
        Args:
            config_path: 配置文件路径
        """
        self.config = self._load_config(config_path)
        self.running = False
        
        # 初始化各模块
        self.analyzer = NewsAnalyzer(self.config.get("analysis", {}))
        self.workflow_manager = WorkflowManager(self.config.get("workflows", {}))
        self.executor = TaskExecutor(self.config.get("executor", {}))
        self.feedback_loop = FeedbackLoop(self.config.get("feedback", {}))
        self.notifier = PushNotifier(self.config.get("push", {}))
        
        # 数据库路径
        db_path = self.config.get("database", {}).get("path", "data/news_workflow.db")
        self.db_path = Path(db_path)
        
        logger.info("NewsWorkflowEngine initialized")
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        if config_path is None:
            config_path = "config/config.yaml"
        
        path = Path(config_path)
        if not path.exists():
            logger.warning(f"Config file not found: {config_path}, using defaults")
            return {}
        
        with open(path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        
        logger.info(f"Config loaded from: {config_path}")
        return config
    
    async def initialize(self):
        """初始化引擎（数据库、连接等）"""
        logger.info("Initializing engine...")
        
        # 创建数据库
        await self._init_database()
        
        # 加载工作流模板
        await self.workflow_manager.load_templates()
        
        # 初始化反馈循环
        if self.config.get("feedback", {}).get("enabled", True):
            await self.feedback_loop.initialize()
        
        logger.info("Engine initialized successfully")
    
    async def _init_database(self):
        """初始化数据库"""
        import aiosqlite
        
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        async with aiosqlite.connect(self.db_path) as db:
            # 新闻表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS news (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    content TEXT,
                    source TEXT,
                    url TEXT,
                    category TEXT,
                    importance REAL,
                    sentiment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    processed BOOLEAN DEFAULT FALSE
                )
            """)
            
            # 工作流表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS workflows (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    template_id TEXT NOT NULL,
                    news_id INTEGER,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (news_id) REFERENCES news(id)
                )
            """)
            
            # 任务表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id INTEGER,
                    name TEXT NOT NULL,
                    description TEXT,
                    status TEXT DEFAULT 'pending',
                    priority INTEGER DEFAULT 5,
                    result TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    completed_at TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
                )
            """)
            
            # 执行日志表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS execution_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER,
                    action TEXT,
                    result TEXT,
                    error TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (task_id) REFERENCES tasks(id)
                )
            """)
            
            # 反馈表
            await db.execute("""
                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    workflow_id INTEGER,
                    metric_name TEXT,
                    metric_value REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (workflow_id) REFERENCES workflows(id)
                )
            """)
            
            await db.commit()
        
        logger.info(f"Database initialized: {self.db_path}")
    
    async def process_news(self, news_items: list) -> int:
        """
        处理新闻列表
        
        Args:
            news_items: 新闻列表，每项包含 title, content, source, url
        
        Returns:
            处理的工作流数量
        """
        logger.info(f"Processing {len(news_items)} news items")
        
        workflows_created = 0
        
        for item in news_items:
            # 1. 分析新闻
            analysis = await self.analyzer.analyze(item)
            
            # 2. 检查是否达到重要性阈值
            threshold = self.config.get("analysis", {}).get("importance_threshold", 0.7)
            if analysis.get("importance", 0) < threshold:
                logger.debug(f"News importance too low: {item.get('title', 'N/A')}")
                continue
            
            # 3. 保存新闻到数据库
            news_id = await self._save_news(item, analysis)
            
            # 4. 匹配工作流模板
            workflows = await self.workflow_manager.match_templates(analysis)
            
            # 5. 创建工作流实例
            for workflow_template in workflows:
                workflow_id = await self.workflow_manager.create_workflow(
                    template_id=workflow_template["id"],
                    news_id=news_id,
                    analysis=analysis
                )
                
                if workflow_id:
                    workflows_created += 1
                    
                    # 6. 推送通知
                    if analysis.get("importance", 0) >= self.config.get("push", {}).get("importance_threshold", 0.8):
                        await self.notifier.send_workflow_alert(workflow_id, analysis)
        
        logger.info(f"Created {workflows_created} workflows from {len(news_items)} news items")
        return workflows_created
    
    async def _save_news(self, item: dict, analysis: dict) -> int:
        """保存新闻到数据库"""
        import aiosqlite
        
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO news (title, content, source, url, category, importance, sentiment)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                item.get("title", ""),
                item.get("content", ""),
                item.get("source", ""),
                item.get("url", ""),
                analysis.get("category", "unknown"),
                analysis.get("importance", 0.5),
                analysis.get("sentiment", "neutral")
            ))
            await db.commit()
            return cursor.lastrowid
    
    async def execute_pending_workflows(self) -> int:
        """
        执行待处理的工作流
        
        Returns:
            执行的工作流数量
        """
        logger.info("Executing pending workflows...")
        
        workflows = await self.workflow_manager.get_pending_workflows()
        executed = 0
        
        for workflow in workflows:
            try:
                # 获取工作流任务
                tasks = await self.workflow_manager.get_workflow_tasks(workflow["id"])
                
                # 执行任务
                for task in tasks:
                    result = await self.executor.execute_task(task)
                    await self.workflow_manager.update_task_status(task["id"], result)
                
                # 更新工作流状态
                await self.workflow_manager.complete_workflow(workflow["id"])
                
                # 收集反馈
                if self.config.get("feedback", {}).get("enabled", True):
                    await self.feedback_loop.collect(workflow["id"])
                
                executed += 1
                
            except Exception as e:
                logger.error(f"Error executing workflow {workflow['id']}: {e}")
                await self.workflow_manager.mark_workflow_failed(workflow["id"], str(e))
        
        logger.info(f"Executed {executed} workflows")
        return executed
    
    async def run_scheduler(self):
        """运行定时调度器"""
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        from apscheduler.triggers.interval import IntervalTrigger
        
        scheduler = AsyncIOScheduler()
        
        # 定时抓取新闻 (由外部 NewsHub 模块负责，这里只处理)
        # 定时执行工作流
        scheduler.add_job(
            self.execute_pending_workflows,
            trigger=IntervalTrigger(seconds=60),
            id="execute_workflows",
            name="Execute pending workflows"
        )
        
        # 定时优化反馈
        if self.config.get("feedback", {}).get("enabled", True):
            optimize_interval = self.config.get("feedback", {}).get("optimize_interval", 3600)
            scheduler.add_job(
                self.feedback_loop.optimize,
                trigger=IntervalTrigger(seconds=optimize_interval),
                id="optimize_feedback",
                name="Optimize feedback loop"
            )
        
        scheduler.start()
        logger.info("Scheduler started")
        
        # 保持运行
        try:
            while self.running:
                await asyncio.sleep(1)
        finally:
            scheduler.shutdown()
    
    async def start(self):
        """启动引擎"""
        self.running = True
        await self.initialize()
        await self.run_scheduler()
    
    def stop(self):
        """停止引擎"""
        self.running = False
        logger.info("Engine stopped")


async def main():
    """主函数"""
    engine = NewsWorkflowEngine()
    await engine.start()


if __name__ == "__main__":
    asyncio.run(main())

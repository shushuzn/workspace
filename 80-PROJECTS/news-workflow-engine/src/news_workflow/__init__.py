"""
News Workflow Engine

智能新闻工作流引擎 - 整合 NewsHub + agentic-bpm + patrol-agent
"""

__version__ = "0.1.0"
__author__ = "OpenClaw Workspace"

from .core.engine import NewsWorkflowEngine
from .analyzer.analyzer import NewsAnalyzer
from .workflow.manager import WorkflowManager
from .executor.runner import TaskExecutor
from .feedback.loop import FeedbackLoop

__all__ = [
    "NewsWorkflowEngine",
    "NewsAnalyzer",
    "WorkflowManager",
    "TaskExecutor",
    "FeedbackLoop",
]

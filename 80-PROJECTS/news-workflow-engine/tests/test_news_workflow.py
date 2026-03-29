"""
Unit Tests for News Workflow Engine
"""

import pytest
import asyncio
from pathlib import Path
import sys

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from news_workflow.analyzer.analyzer import NewsAnalyzer
from news_workflow.workflow.manager import WorkflowManager
from news_workflow.executor.runner import TaskExecutor


class TestNewsAnalyzer:
    """测试新闻分析器"""
    
    @pytest.fixture
    def analyzer(self):
        return NewsAnalyzer({"model": "ollama/llama3"})
    
    @pytest.mark.asyncio
    async def test_analyze_with_rules(self, analyzer):
        """测试规则分析"""
        news = {
            "title": "AI 大模型新突破",
            "content": "某公司发布了新一代 AI 大模型，技术领先，性能大幅提升",
            "source": "test",
            "url": "https://example.com"
        }
        
        result = await analyzer.analyze(news)
        
        assert "importance" in result
        assert "category" in result
        assert "sentiment" in result
        assert "keywords" in result
        assert "summary" in result
        
        assert result["category"] == "tech"
        assert result["sentiment"] == "positive"
    
    @pytest.mark.asyncio
    async def test_analyze_finance_news(self, analyzer):
        """测试金融新闻分析"""
        news = {
            "title": "股市大涨，金融板块领涨",
            "content": "今日股市大幅上涨，银行、保险等金融板块领涨，成交量创新高",
            "source": "test",
            "url": "https://example.com"
        }
        
        result = await analyzer.analyze(news)
        
        assert result["category"] in ["finance", "market"]
    
    @pytest.mark.asyncio
    async def test_analyze_negative_news(self, analyzer):
        """测试负面新闻分析"""
        news = {
            "title": "公司面临监管风险，股价下跌",
            "content": "该公司因违规操作面临监管处罚，股价大幅下跌，投资者警告风险",
            "source": "test",
            "url": "https://example.com"
        }
        
        result = await analyzer.analyze(news)
        
        assert result["sentiment"] == "negative"


class TestWorkflowManager:
    """测试工作流管理器"""
    
    @pytest.fixture
    def manager(self):
        return WorkflowManager({})
    
    @pytest.mark.asyncio
    async def test_load_templates(self, manager):
        """测试加载模板"""
        await manager.load_templates()
        
        assert len(manager.templates) > 0
        assert "tech_research" in manager.templates
        assert "risk_alert" in manager.templates
    
    @pytest.mark.asyncio
    async def test_match_tech_template(self, manager):
        """测试科技新闻模板匹配"""
        await manager.load_templates()
        
        analysis = {
            "category": "tech",
            "importance": 0.8,
            "sentiment": "positive",
            "keywords": ["AI", "大模型"]
        }
        
        matched = await manager.match_templates(analysis)
        
        assert len(matched) > 0
        assert any(t["id"] == "tech_research" for t in matched)
    
    @pytest.mark.asyncio
    async def test_match_risk_template(self, manager):
        """测试风险预警模板匹配"""
        await manager.load_templates()
        
        analysis = {
            "category": "company",
            "importance": 0.9,
            "sentiment": "negative",
            "keywords": ["风险"]
        }
        
        matched = await manager.match_templates(analysis)
        
        assert any(t["id"] == "risk_alert" for t in matched)


class TestTaskExecutor:
    """测试任务执行器"""
    
    @pytest.fixture
    def executor(self):
        return TaskExecutor({})
    
    @pytest.mark.asyncio
    async def test_execute_github_search(self, executor):
        """测试 GitHub 搜索任务"""
        task = {
            "name": "搜索 GitHub 项目",
            "description": "根据关键词搜索 GitHub 项目"
        }
        
        result = await executor.execute_task(task)
        
        assert result["success"] is True
        assert "output" in result
    
    @pytest.mark.asyncio
    async def test_execute_generate_report(self, executor):
        """测试生成报告任务"""
        task = {
            "name": "生成调研报告",
            "description": "生成包含项目对比和分析的调研报告"
        }
        
        result = await executor.execute_task(task)
        
        assert result["success"] is True
        assert "report_path" in result["output"]
    
    @pytest.mark.asyncio
    async def test_execute_with_retry(self, executor):
        """测试重试逻辑"""
        executor.retry_enabled = True
        executor.max_retries = 2
        
        task = {
            "name": "测试任务",
            "description": "通用任务"
        }
        
        result = await executor.execute_task(task)
        
        assert result["success"] is True


class TestIntegration:
    """集成测试"""
    
    @pytest.mark.asyncio
    async def test_full_workflow(self):
        """测试完整工作流"""
        # 1. 分析新闻
        analyzer = NewsAnalyzer({"model": "ollama/llama3"})
        news = {
            "title": "AI 大模型新突破，性能提升 10 倍",
            "content": "某科技公司发布了新一代 AI 大模型...",
            "source": "test",
            "url": "https://example.com"
        }
        
        analysis = await analyzer.analyze(news)
        assert analysis["category"] == "tech"
        
        # 2. 匹配工作流
        manager = WorkflowManager({})
        await manager.load_templates()
        matched = await manager.match_templates(analysis)
        assert len(matched) > 0
        
        # 3. 执行任务
        executor = TaskExecutor({})
        task = {
            "name": "测试任务",
            "description": "GitHub 搜索"
        }
        result = await executor.execute_task(task)
        assert result["success"] is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

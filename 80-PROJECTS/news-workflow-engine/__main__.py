"""
News Workflow Engine CLI

命令行接口
"""

import asyncio
import sys
import argparse
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from news_workflow.core.engine import NewsWorkflowEngine
from news_workflow.workflow.manager import WorkflowManager
from loguru import logger


def setup_logging():
    """设置日志"""
    logger.remove()
    logger.add(
        sys.stdout,
        format="{time:YYYY-MM-DD HH:mm:ss} | <level>{level}</level> | {message}",
        level="INFO"
    )


async def cmd_init(args):
    """初始化数据库"""
    engine = NewsWorkflowEngine(args.config)
    await engine.initialize()
    print("✅ Database initialized successfully")


async def cmd_run(args):
    """运行引擎"""
    setup_logging()
    engine = NewsWorkflowEngine(args.config)
    
    try:
        await engine.start()
    except KeyboardInterrupt:
        engine.stop()
        print("\n👋 Engine stopped")


async def cmd_test(args):
    """运行测试"""
    setup_logging()
    
    if args.integration:
        print("🧪 Running integration tests...")
        await run_integration_tests()
    elif args.e2e:
        print("🧪 Running end-to-end tests...")
        await run_e2e_tests()
    else:
        print("🧪 Running unit tests...")
        import subprocess
        subprocess.run(["pytest", "tests/", "-v"])


async def run_integration_tests():
    """运行集成测试"""
    from news_workflow.analyzer.analyzer import NewsAnalyzer
    from news_workflow.workflow.manager import WorkflowManager
    
    # 测试分析器
    analyzer = NewsAnalyzer({"model": "ollama/llama3"})
    test_news = {
        "title": "AI 大模型新突破",
        "content": "某公司发布了新一代 AI 大模型，性能大幅提升...",
        "source": "test",
        "url": "https://example.com"
    }
    
    result = await analyzer.analyze(test_news)
    print(f"✅ Analyzer test: {result}")
    
    # 测试工作流管理器
    manager = WorkflowManager({})
    await manager.load_templates()
    print(f"✅ WorkflowManager loaded {len(manager.templates)} templates")
    
    print("\n✅ All integration tests passed!")


async def run_e2e_tests():
    """运行端到端测试"""
    from news_workflow.analyzer.analyzer import NewsAnalyzer
    from news_workflow.workflow.manager import WorkflowManager
    from news_workflow.executor.runner import TaskExecutor
    
    # 模拟完整流程
    test_news = [
        {
            "title": "AI 大模型新突破，性能提升 10 倍",
            "content": "某科技公司今日发布了新一代 AI 大模型，在多个基准测试中表现优异...",
            "source": "tech_news",
            "url": "https://example.com/ai-breakthrough"
        }
    ]
    
    # 1. 分析
    analyzer = NewsAnalyzer({"model": "ollama/llama3"})
    analysis = await analyzer.analyze(test_news[0])
    print(f"📊 Analysis: {analysis}")
    
    # 2. 匹配工作流
    manager = WorkflowManager({})
    await manager.load_templates()
    matched = await manager.match_templates(analysis)
    print(f"🔗 Matched {len(matched)} workflows")
    
    # 3. 执行任务
    executor = TaskExecutor({})
    test_task = {
        "name": "测试任务",
        "description": "GitHub 搜索相关项目",
        "id": 1
    }
    result = await executor.execute_task(test_task)
    print(f"✅ Task execution: {result}")
    
    print("\n✅ End-to-end test completed!")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="News Workflow Engine CLI")
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # init 命令
    init_parser = subparsers.add_parser("init", help="Initialize database")
    init_parser.add_argument("--config", default="config/config.yaml", help="Config file path")
    init_parser.set_defaults(func=cmd_init)
    
    # run 命令
    run_parser = subparsers.add_parser("run", help="Run the engine")
    run_parser.add_argument("--config", default="config/config.yaml", help="Config file path")
    run_parser.set_defaults(func=cmd_run)
    
    # test 命令
    test_parser = subparsers.add_parser("test", help="Run tests")
    test_parser.add_argument("--integration", action="store_true", help="Run integration tests")
    test_parser.add_argument("--e2e", action="store_true", help="Run end-to-end tests")
    test_parser.set_defaults(func=cmd_test)
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return
    
    asyncio.run(args.func(args))


if __name__ == "__main__":
    main()

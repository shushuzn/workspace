"""
News Workflow Engine - Full Flow Test

测试完整流程：分析 → 匹配工作流 → 执行任务
"""

import sys
import sqlite3
import importlib.util
from pathlib import Path

# 添加 src 到路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

# 直接加载模块，避免 __init__.py 的循环导入
def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# 加载分析器和执行器
analyzer_module = load_module("analyzer", Path(__file__).parent / "src" / "news_workflow" / "analyzer" / "analyzer.py")
executor_module = load_module("executor", Path(__file__).parent / "src" / "news_workflow" / "executor" / "runner.py")

NewsAnalyzer = analyzer_module.NewsAnalyzer
TaskExecutor = executor_module.TaskExecutor


def test_analyzer():
    """测试新闻分析器"""
    print("=" * 60)
    print("📊 测试新闻分析器")
    print("=" * 60)
    
    import asyncio
    
    async def run_test():
        analyzer = NewsAnalyzer({"model": "custom"})  # 使用规则分析
        
        test_cases = [
            {
                "name": "科技新闻",
                "news": {
                    "title": "AI 大模型新突破，性能提升 10 倍",
                    "content": "某科技公司发布了新一代 AI 大模型，在多个基准测试中表现优异，技术领先",
                    "source": "tech_news",
                    "url": "https://example.com/ai"
                }
            },
            {
                "name": "金融新闻",
                "news": {
                    "title": "股市大涨，金融板块领涨",
                    "content": "今日股市大幅上涨，银行、保险等金融板块领涨，成交量创新高",
                    "source": "finance_news",
                    "url": "https://example.com/finance"
                }
            },
            {
                "name": "风险新闻",
                "news": {
                    "title": "公司面临监管风险，股价下跌",
                    "content": "该公司因违规操作面临监管处罚，股价大幅下跌，投资者警告风险",
                    "source": "risk_news",
                    "url": "https://example.com/risk"
                }
            }
        ]
        
        for case in test_cases:
            print(f"\n测试：{case['name']}")
            result = await analyzer.analyze(case["news"])
            print(f"  分类：{result['category']}")
            print(f"  情感：{result['sentiment']}")
            print(f"  重要性：{result['importance']:.2f}")
            print(f"  关键词：{', '.join(result['keywords'][:3])}")
        
        return True
    
    return asyncio.run(run_test())


def test_executor():
    """测试任务执行器"""
    print("\n" + "=" * 60)
    print("🤖 测试任务执行器")
    print("=" * 60)
    
    import asyncio
    
    async def run_test():
        executor = TaskExecutor({})
        
        test_tasks = [
            {"name": "GitHub 搜索", "description": "搜索相关 GitHub 项目"},
            {"name": "生成报告", "description": "生成调研报告"},
            {"name": "风险提取", "description": "提取风险因素"},
            {"name": "紧急推送", "description": "高优先级推送告警"}
        ]
        
        for task in test_tasks:
            print(f"\n执行任务：{task['name']}")
            result = await executor.execute_task(task)
            print(f"  状态：{'✅ 成功' if result['success'] else '❌ 失败'}")
            if result.get('output'):
                print(f"  输出：{list(result['output'].keys())}")
        
        return True
    
    return asyncio.run(run_test())


def test_workflow_templates():
    """测试工作流模板"""
    print("\n" + "=" * 60)
    print("🔗 测试工作流模板")
    print("=" * 60)
    
    import yaml
    
    templates_dir = Path("config/workflows")
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    # 检查是否已有模板
    template_files = list(templates_dir.glob("*.yaml"))
    
    if not template_files:
        print("⚠️  模板目录为空，需要先运行 WorkflowManager.load_templates()")
        return False
    
    for template_file in template_files:
        with open(template_file, "r", encoding="utf-8") as f:
            template = yaml.safe_load(f)
        
        print(f"\n模板：{template['name']} ({template['id']})")
        print(f"  描述：{template['description']}")
        print(f"  触发条件：{template.get('trigger', {})}")
        print(f"  任务数：{len(template.get('tasks', []))}")
    
    return True


def test_database():
    """测试数据库"""
    print("\n" + "=" * 60)
    print("💾 测试数据库")
    print("=" * 60)
    
    db_path = Path("data/news_workflow.db")
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 创建表
    cursor.execute("""
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
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workflows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            template_id TEXT NOT NULL,
            news_id INTEGER,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_id INTEGER,
            name TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            priority INTEGER DEFAULT 5,
            result TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP
        )
    """)
    
    conn.commit()
    
    # 验证表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print(f"数据库：{db_path}")
    print(f"表：{', '.join(tables)}")
    
    # 插入测试数据
    cursor.execute("""
        INSERT INTO news (title, content, source, category, importance, sentiment)
        VALUES (?, ?, ?, ?, ?, ?)
    """, ("测试新闻", "测试内容", "test", "tech", 0.8, "positive"))
    
    conn.commit()
    
    cursor.execute("SELECT COUNT(*) FROM news")
    count = cursor.fetchone()[0]
    print(f"新闻记录数：{count}")
    
    conn.close()
    
    return True


def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("🦸 News Workflow Engine - 全流程测试")
    print("=" * 60)
    
    results = []
    
    # 1. 测试分析器
    try:
        results.append(("分析器", test_analyzer()))
    except Exception as e:
        print(f"❌ 分析器测试失败：{e}")
        results.append(("分析器", False))
    
    # 2. 测试执行器
    try:
        results.append(("执行器", test_executor()))
    except Exception as e:
        print(f"❌ 执行器测试失败：{e}")
        results.append(("执行器", False))
    
    # 3. 测试数据库
    try:
        results.append(("数据库", test_database()))
    except Exception as e:
        print(f"❌ 数据库测试失败：{e}")
        results.append(("数据库", False))
    
    # 4. 测试工作流模板
    try:
        results.append(("工作流模板", test_workflow_templates()))
    except Exception as e:
        print(f"❌ 工作流模板测试失败：{e}")
        results.append(("工作流模板", False))
    
    # 总结
    print("\n" + "=" * 60)
    print("📋 测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {name}: {status}")
    
    print(f"\n总计：{passed}/{total} 通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！全流程跑通！")
        return 0
    else:
        print("\n⚠️  部分测试失败")
        return 1


if __name__ == "__main__":
    sys.exit(main())

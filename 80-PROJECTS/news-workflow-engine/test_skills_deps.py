"""
GitHub Skills Integration Test - Simple Version
测试已安装的 GitHub 技能依赖
"""

import sys
import importlib

print("=" * 70)
print("🦸 GitHub 技能依赖检查")
print("=" * 70)

skills = [
    ("langgraph", "LangGraph 工作流", "0.2+"),
    ("chromadb", "Chroma 向量记忆", "1.5+"),
    ("autogen_agentchat", "AutoGen 多 Agent", "0.7+"),
    ("langchain", "LangChain 框架", "1.2+"),
]

results = {}

for module, name, min_ver in skills:
    try:
        mod = importlib.import_module(module)
        version = getattr(mod, "__version__", "unknown")
        print(f"\n✅ {name}")
        print(f"   模块：{module}")
        print(f"   版本：{version}")
        results[name] = True
    except ImportError as e:
        print(f"\n❌ {name}")
        print(f"   模块：{module}")
        print(f"   错误：{e}")
        results[name] = False

# 总结
print("\n" + "=" * 70)
print("📋 依赖检查总结")
print("=" * 70)

passed = sum(1 for v in results.values() if v)
total = len(results)

for name, ok in results.items():
    status = "✅ 已安装" if ok else "❌ 未安装"
    print(f"  {name}: {status}")

print(f"\n总计：{passed}/{total} 已安装")

if passed >= 3:
    print("\n🎉 核心依赖已就绪！可以开始使用 GitHub 技能！")
    
    if not results.get("AutoGen 多 Agent"):
        print("\n📝 提示：AutoGen 可选安装")
        print("   pip install pyautogen")
    
    print("\n📚 使用示例:")
    print("""
# LangGraph 工作流
from langgraph.graph import StateGraph, END

class MyState(dict):
    pass

workflow = StateGraph(MyState)
workflow.add_node("step1", lambda s: {"step": 1})
workflow.set_entry_point("step1")
workflow.add_edge("step1", END)
app = workflow.compile()

# Chroma 记忆
import chromadb
client = chromadb.Client()
collection = client.create_collection("my_collection")
collection.add(documents=["doc1"], ids=["1"])

# AutoGen 多 Agent (需额外安装)
from autogen_agentchat.agents import AssistantAgent
agent = AssistantAgent("assistant")
    """)
else:
    print("\n⚠️  依赖不足，请安装缺失的包")
    print("\n📝 安装命令:")
    print("   pip install langgraph langchain chromadb pyautogen")

sys.exit(0 if passed >= 3 else 1)

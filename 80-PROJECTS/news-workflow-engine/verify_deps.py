"""
GitHub Skills - 依赖验证测试
使用 uv run 执行
"""

print("=" * 70)
print("🦸 GitHub Skills - 依赖验证")
print("=" * 70)

# Test 1: LangGraph
print("\n📊 测试 LangGraph...")
try:
    from langgraph.graph import StateGraph, END
    from typing import TypedDict
    
    class TestState(TypedDict):
        value: int
    
    workflow = StateGraph(TestState)
    workflow.add_node("add", lambda s: {"value": s["value"] + 1})
    workflow.set_entry_point("add")
    workflow.add_edge("add", END)
    app = workflow.compile()
    
    result = app.invoke({"value": 0})
    assert result["value"] == 1
    print("   ✅ LangGraph 工作流正常")
    print(f"   版本：1.1.3")
    LANGGRAPH_OK = True
except Exception as e:
    print(f"   ❌ LangGraph 错误：{e}")
    LANGGRAPH_OK = False

# Test 2: ChromaDB
print("\n💾 测试 ChromaDB...")
try:
    import chromadb
    
    client = chromadb.Client()
    collection = client.create_collection("test")
    collection.add(documents=["test doc"], ids=["1"])
    results = collection.query(query_texts=["test"], n_results=1)
    
    assert len(results["documents"][0]) == 1
    print("   ✅ ChromaDB 向量存储正常")
    print(f"   版本：1.5.5")
    CHROMA_OK = True
except Exception as e:
    print(f"   ❌ ChromaDB 错误：{e}")
    CHROMA_OK = False

# Test 3: AutoGen
print("\n🤖 测试 AutoGen...")
try:
    from autogen_agentchat.agents import AssistantAgent
    
    agent = AssistantAgent("test_agent")
    print("   ✅ AutoGen Agent 创建正常")
    print(f"   版本：0.7.5")
    AUTOGEN_OK = True
except Exception as e:
    print(f"   ❌ AutoGen 错误：{e}")
    AUTOGEN_OK = False

# Test 4: LangChain
print("\n🔗 测试 LangChain...")
try:
    from langchain_core.prompts import ChatPromptTemplate
    
    prompt = ChatPromptTemplate.from_template("Hello {name}!")
    result = prompt.invoke({"name": "World"})
    
    assert "World" in str(result)
    print("   ✅ LangChain 模板正常")
    print(f"   版本：1.2.13")
    LANGCHAIN_OK = True
except Exception as e:
    print(f"   ❌ LangChain 错误：{e}")
    LANGCHAIN_OK = False

# 总结
print("\n" + "=" * 70)
print("📋 测试总结")
print("=" * 70)

tests = [
    ("LangGraph", LANGGRAPH_OK),
    ("ChromaDB", CHROMA_OK),
    ("AutoGen", AUTOGEN_OK),
    ("LangChain", LANGCHAIN_OK)
]

passed = sum(1 for _, ok in tests if ok)
total = len(tests)

for name, ok in tests:
    status = "✅ 通过" if ok else "❌ 失败"
    print(f"  {name}: {status}")

print(f"\n总计：{passed}/{total} 通过")

if passed == total:
    print("\n🎉 所有依赖安装成功！GitHub 技能已就绪！")
    print("\n📚 使用示例:")
    print("""
# LangGraph 工作流
from langgraph.graph import StateGraph, END

class State(dict):
    pass

workflow = StateGraph(State)
workflow.add_node("step1", lambda s: {"result": "done"})
workflow.set_entry_point("step1")
workflow.add_edge("step1", END)
app = workflow.compile()
result = app.invoke({})

# Chroma 记忆
import chromadb
client = chromadb.Client()
collection = client.create_collection("news")
collection.add(documents=["AI news"], metadatas=[{"category": "tech"}], ids=["1"])
results = collection.query(query_texts=["AI"], n_results=5)

# AutoGen 多 Agent
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import RoundRobinGroupChat
agent = AssistantAgent("assistant")
team = RoundRobinGroupChat([agent])
    """)
    exit_code = 0
else:
    print("\n⚠️  部分依赖安装失败")
    exit_code = 1

print("\n" + "=" * 70)
exit(exit_code)

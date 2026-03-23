#!/usr/bin/env python3
"""
MCP 工具调用测试脚本
"""
import sys
sys.path.insert(0, 'str(Path(__file__).parent.parent)\\scripts')

import importlib.util
spec = importlib.util.spec_from_file_location("mcp_integrator", "str(Path(__file__).parent.parent)\\scripts\\mcp-integrator.py")
mcp_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mcp_module)
call_tool = mcp_module.call_tool
import asyncio
from pathlib import Path

async def main():
    # 测试文件搜索
    print("🔍 测试 filesystem.search...")
    result = await call_tool("filesystem.search", {
        "pattern": "*.md",
        "path": "str(Path(__file__).parent.parent)\\Arxiv"
    })
    print(f"找到 {len(result.get('files', []))} 个文件")
    for f in result.get('files', [])[:5]:
        print(f"  - {f}")

    # 测试文件读取
    print("\n📖 测试 filesystem.read_file...")
    result = await call_tool("filesystem.read_file", {
        "path": "str(Path(__file__).parent.parent)\\mcp-config.json"
    })
    if 'content' in result:
        print(f"读取成功，内容长度：{len(result['content'])}")
        print(result['content'][:200])

    # 测试网页抓取
    print("\n🌐 测试 fetch.get...")
    result = await call_tool("fetch.get", {
        "url": "https://arxiv.org"
    })
    if 'content' in result:
        print(f"抓取成功，状态码：{result.get('status', 'N/A')}")
        print(f"内容长度：{len(result['content'])}")

if __name__ == "__main__":
    asyncio.run(main())

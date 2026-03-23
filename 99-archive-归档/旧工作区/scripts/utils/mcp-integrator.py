#!/usr/bin/env python3
"""
MCP Tool Integrator - MCP 工具集成
连接外部 MCP 服务器，调用工具，扩展能力
"""

import sys
import os
import json
import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional

# Windows UTF-8 编码支持
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ============ 配置 ============
WORKSPACE = r"D:\OpenClaw\workspace"
CONFIG_PATH = os.path.join(WORKSPACE, "mcp-config.json")
LOG_PATH = os.path.join(WORKSPACE, "scripts", "mcp-integrator.log")
OUTPUT_DIR = os.path.join(WORKSPACE, "mcp-output")

# 默认 MCP 服务器配置
DEFAULT_SERVERS = {
    "filesystem": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-filesystem", WORKSPACE],
        "description": "文件系统操作（读取/写入/搜索）",
        "enabled": True,
    },
    "github": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-github"],
        "description": "GitHub API（issues/PRs/repos）",
        "enabled": False,  # 需要 GITHUB_TOKEN
    },
    "slack": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-slack"],
        "description": "Slack 消息发送/频道管理",
        "enabled": False,  # 需要 SLACK_TOKEN
    },
    "postgres": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-postgres", "postgresql://localhost"],
        "description": "PostgreSQL 数据库操作",
        "enabled": False,
    },
    "fetch": {
        "command": "npx",
        "args": ["-y", "@modelcontextprotocol/server-fetch"],
        "description": "网页内容抓取",
        "enabled": True,
    },
}

# ============ 工具函数 ============
def log(msg: str):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except Exception:
        pass

def load_config() -> Dict:
    """加载 MCP 配置"""
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"servers": DEFAULT_SERVERS}

def save_config(config: Dict):
    """保存 MCP 配置"""
    os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
    with open(CONFIG_PATH, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    log(f"💾 配置已保存到 {CONFIG_PATH}")

def list_available_tools() -> List[Dict]:
    """列出可用的 MCP 工具"""
    # 这里简化实现，实际应该连接 MCP 服务器获取工具列表
    tools = [
        {
            "name": "filesystem.read_file",
            "description": "读取文件内容",
            "input_schema": {"path": "string"},
        },
        {
            "name": "filesystem.write_file",
            "description": "写入文件内容",
            "input_schema": {"path": "string", "content": "string"},
        },
        {
            "name": "filesystem.search",
            "description": "搜索文件",
            "input_schema": {"pattern": "string", "path": "string"},
        },
        {
            "name": "fetch.get",
            "description": "获取网页内容",
            "input_schema": {"url": "string"},
        },
        {
            "name": "github.get_issue",
            "description": "获取 GitHub issue",
            "input_schema": {"owner": "string", "repo": "string", "issue_number": "integer"},
        },
        {
            "name": "github.create_issue",
            "description": "创建 GitHub issue",
            "input_schema": {"owner": "string", "repo": "string", "title": "string", "body": "string"},
        },
    ]
    return tools

async def call_tool(tool_name: str, arguments: Dict) -> Any:
    """调用 MCP 工具"""
    # 简化实现：模拟工具调用
    # 实际应该使用 @modelcontextprotocol/sdk 连接服务器
    
    log(f"🔧 调用工具：{tool_name}")
    log(f"   参数：{json.dumps(arguments, ensure_ascii=False)}")
    
    # 模拟响应
    if tool_name == "filesystem.read_file":
        path = arguments.get('path', '')
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return {"content": f.read()[:1000]}
        return {"error": f"File not found: {path}"}
    
    elif tool_name == "filesystem.write_file":
        path = arguments.get('path', '')
        content = arguments.get('content', '')
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"success": True, "path": path}
        except Exception as e:
            return {"error": str(e)}
    
    elif tool_name == "fetch.get":
        url = arguments.get('url', '')
        try:
            import requests
            resp = requests.get(url, timeout=30)
            return {"content": resp.text[:2000], "status": resp.status_code}
        except Exception as e:
            return {"error": str(e)}
    
    elif tool_name == "filesystem.search":
        path = arguments.get('path', WORKSPACE)
        pattern = arguments.get('pattern', '*.md')
        try:
            import fnmatch
            results = []
            for root, dirs, files in os.walk(path):
                for filename in files:
                    if fnmatch.fnmatch(filename, pattern):
                        results.append(os.path.join(root, filename))
            return {"files": results[:50]}
        except Exception as e:
            return {"error": str(e)}
    
    else:
        return {"error": f"Unknown tool: {tool_name}"}

# ============ 命令接口 ============
def cmd_init():
    """初始化 MCP 配置"""
    log("🚀 初始化 MCP 配置")
    config = {"servers": DEFAULT_SERVERS}
    save_config(config)
    
    print("\n✅ MCP 配置已创建")
    print(f"📁 位置：{CONFIG_PATH}")
    print("\n可用服务器:")
    for name, server in DEFAULT_SERVERS.items():
        status = "✅" if server.get('enabled', False) else "⏸️"
        print(f"  {status} {name}: {server['description']}")

def cmd_list():
    """列出可用工具"""
    log("📋 列出 MCP 工具")
    tools = list_available_tools()
    
    print("\n🔧 可用 MCP 工具:\n")
    for tool in tools:
        print(f"### {tool['name']}")
        print(f"   {tool['description']}")
        print(f"   参数：{json.dumps(tool['input_schema'], ensure_ascii=False)}")
        print()

def cmd_call(tool_name: str, args_json: str):
    """调用工具"""
    log(f"🔧 调用工具：{tool_name}")
    
    try:
        arguments = json.loads(args_json) if args_json else {}
    except json.JSONDecodeError as e:
        print(f"❌ 参数解析失败：{e}")
        return
    
    result = asyncio.run(call_tool(tool_name, arguments))
    
    print("\n📤 工具返回结果:\n")
    print(json.dumps(result, indent=2, ensure_ascii=False))

def cmd_status():
    """显示 MCP 状态"""
    log("📊 MCP 状态")
    config = load_config()
    
    print("\n📡 MCP 服务器状态:\n")
    for name, server in config.get('servers', {}).items():
        status = "✅" if server.get('enabled', False) else "⏸️"
        print(f"{status} {name}")
        print(f"   描述：{server.get('description', 'N/A')}")
        print(f"   命令：{server.get('command', '')} {' '.join(server.get('args', []))}")
        print()

def cmd_enable(server_name: str):
    """启用服务器"""
    log(f"✅ 启用服务器：{server_name}")
    config = load_config()
    
    if server_name in config.get('servers', {}):
        config['servers'][server_name]['enabled'] = True
        save_config(config)
        print(f"✅ 已启用 {server_name}")
    else:
        print(f"❌ 未知服务器：{server_name}")

def cmd_disable(server_name: str):
    """禁用服务器"""
    log(f"⏸️ 禁用服务器：{server_name}")
    config = load_config()
    
    if server_name in config.get('servers', {}):
        config['servers'][server_name]['enabled'] = False
        save_config(config)
        print(f"⏸️ 已禁用 {server_name}")
    else:
        print(f"❌ 未知服务器：{server_name}")

# ============ 主流程 ============
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='MCP 工具集成')
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # init 命令
    subparsers.add_parser('init', help='初始化 MCP 配置')
    
    # list 命令
    subparsers.add_parser('list', help='列出可用工具')
    
    # status 命令
    subparsers.add_parser('status', help='显示 MCP 状态')
    
    # call 命令
    call_parser = subparsers.add_parser('call', help='调用工具')
    call_parser.add_argument('tool', type=str, help='工具名称')
    call_parser.add_argument('args', type=str, nargs='?', default='{}', help='JSON 参数')
    
    # enable 命令
    enable_parser = subparsers.add_parser('enable', help='启用服务器')
    enable_parser.add_argument('server', type=str, help='服务器名称')
    
    # disable 命令
    disable_parser = subparsers.add_parser('disable', help='禁用服务器')
    disable_parser.add_argument('server', type=str, help='服务器名称')
    
    args = parser.parse_args()
    
    if args.command == 'init':
        cmd_init()
    elif args.command == 'list':
        cmd_list()
    elif args.command == 'status':
        cmd_status()
    elif args.command == 'call':
        cmd_call(args.tool, args.args)
    elif args.command == 'enable':
        cmd_enable(args.server)
    elif args.command == 'disable':
        cmd_disable(args.server)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

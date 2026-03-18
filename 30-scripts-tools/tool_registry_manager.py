#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tool Registry Manager - 工具注册表管理工具

功能：
- 注册新工具到 tools_registry.json
- 更新工具定义
- 验证工具完整性

Usage:
    py tool_registry_manager.py --register <tool_json_file>
    py tool_registry_manager.py --update <tool_id> <field> <value>
    py tool_registry_manager.py --verify
    py tool_registry_manager.py --list
"""

import json
import sys
import os
import subprocess
import codecs
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional

if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

WORKSPACE = Path(__file__).parent.parent
REGISTRY_FILE = WORKSPACE / "30-scripts-tools" / "tools_registry.json"


class ToolRegistryManager:
    """工具注册表管理器"""
    
    def __init__(self):
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """加载注册表"""
        if not REGISTRY_FILE.exists():
            return {
                "version": "1.0.0",
                "last_updated": datetime.now().isoformat(),
                "tools": {}
            }
        
        with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_registry(self):
        """保存注册表"""
        self.registry['last_updated'] = datetime.now().isoformat()
        
        with open(REGISTRY_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def register_tool(self, tool_def: Dict) -> bool:
        """注册新工具"""
        tool_id = tool_def.get('tool_id')
        
        if not tool_id:
            print("ERROR: tool_id required")
            return False
        
        if tool_id in self.registry['tools']:
            print(f"WARNING: Tool {tool_id} already exists, updating...")
        
        self.registry['tools'][tool_id] = tool_def
        
        # 更新版本
        version_parts = self.registry.get('version', '1.0.0').split('.')
        version_parts[-1] = str(int(version_parts[-1]) + 1)
        self.registry['version'] = '.'.join(version_parts)
        
        self._save_registry()
        print(f"OK: Tool {tool_id} registered (registry v{self.registry['version']})")
        return True
    
    def update_tool(self, tool_id: str, field: str, value: Any) -> bool:
        """更新工具字段"""
        if tool_id not in self.registry['tools']:
            print(f"ERROR: Tool {tool_id} not found")
            return False
        
        self.registry['tools'][tool_id][field] = value
        self._save_registry()
        print(f"OK: Tool {tool_id}.{field} updated")
        return True
    
    def verify(self) -> bool:
        """验证注册表完整性"""
        issues = []
        
        # 检查工具 ID 唯一性
        tool_ids = list(self.registry['tools'].keys())
        if len(tool_ids) != len(set(tool_ids)):
            issues.append("Duplicate tool_ids found")
        
        # 检查每个工具的必需字段
        for tool_id, tool in self.registry['tools'].items():
            if 'tool_id' not in tool:
                issues.append(f"Tool {tool_id} missing tool_id")
            if 'command' not in tool:
                issues.append(f"Tool {tool_id} missing command")
            if 'description' not in tool:
                issues.append(f"Tool {tool_id} missing description")
        
        # 检查工具文件是否存在
        for tool_id, tool in self.registry['tools'].items():
            command = tool.get('command', '')
            if 'py ' in command:
                # 提取脚本路径
                parts = command.split()
                for part in parts:
                    if part.endswith('.py'):
                        script_path = WORKSPACE / part.replace('\\', '/')
                        if not script_path.exists():
                            issues.append(f"Tool {tool_id} script not found: {script_path}")
        
        if issues:
            print(f"VERIFICATION FAILED: {len(issues)} issues")
            for issue in issues[:10]:
                print(f"  - {issue}")
            return False
        
        print(f"VERIFICATION PASSED: {len(self.registry['tools'])} tools OK")
        return True
    
    def list_tools(self):
        """列出所有工具"""
        tools = self.registry['tools']
        print(f"Total tools: {len(tools)}")
        print(f"Registry version: {self.registry.get('version', 'unknown')}")
        print("\nTools:")
        for tool_id, tool in sorted(tools.items()):
            desc = tool.get('description', 'No description')[:60]
            print(f"  - {tool_id}: {desc}")


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Tool Registry Manager")
    parser.add_argument('--register', type=str, help='Register tool from JSON file')
    parser.add_argument('--update', nargs=3, metavar=('TOOL_ID', 'FIELD', 'VALUE'), help='Update tool field')
    parser.add_argument('--verify', action='store_true', help='Verify registry integrity')
    parser.add_argument('--list', action='store_true', help='List all tools')
    
    args = parser.parse_args()
    
    manager = ToolRegistryManager()
    
    if args.register:
        with open(args.register, 'r', encoding='utf-8') as f:
            tool_def = json.load(f)
        manager.register_tool(tool_def)
    
    elif args.update:
        tool_id, field, value = args.update
        # 尝试解析 JSON 值
        try:
            value = json.loads(value)
        except:
            pass  # Keep as string
        manager.update_tool(tool_id, field, value)
    
    elif args.verify:
        success = manager.verify()
        sys.exit(0 if success else 1)
    
    elif args.list:
        manager.list_tools()
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

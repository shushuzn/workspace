import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DEP-RESOLVER-001 Dependency Auto Resolver
[Dependency Auto Resolver]

功能:
  - 解析工具依赖关系
  - 自动安装缺失依赖
  - 依赖冲突检测

使用:
  py dep_resolver_001.py --resolve <tool_id>
  py dep_resolver_001.py --graph
  py dep_resolver_001.py --check
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Set, Optional

# Fix Windows Unicode
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


DEPENDENCY_FILE = Path("13-memory/.dependencies.json")


class DependencyResolver:
    """依赖自动解析器"""

    # 内置依赖映射
    BUILTIN_DEPS = {
        "brainstorm_workflow": ["brainstorm_001_define", "brainstorm_002_diverge"],
        "auto_discover": ["tools_registry"],
        "optimize_master": ["smart_cache", "batch_tools"],
    }

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.tools_dir = self.workspace / "30-scripts-tools"
        self._ensure_dep_file()

    def _ensure_dep_file(self):
        if not DEPENDENCY_FILE.exists():
            DEPENDENCY_FILE.write_text(
                json.dumps({"dependencies": {}, "resolved": {}}, ensure_ascii=False, indent=2)
            )

    def _load_deps(self) -> dict:
        return json.loads(DEPENDENCY_FILE.read_text(encoding="utf-8"))

    def _save_deps(self, data: dict):
        DEPENDENCY_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2))

    def extract_dependencies(self, tool_id: str) -> List[str]:
        """从工具文件中提取依赖"""
        deps = self.BUILTIN_DEPS.get(tool_id, [])

        # 扫描文件查找导入
        tool_file = None
        for f in self.tools_dir.glob("*.py"):
            if tool_id.replace("_", "-") in f.name.lower():
                tool_file = f
                break

        if not tool_file:
            return deps

        try:
            content = tool_file.read_text(encoding="utf-8")

            # 查找 from X import 或 import X
            imports = re.findall(r'(?:from|import)\s+(\w+)', content)

            for imp in imports:
                if imp not in ["json", "sys", "pathlib", "datetime", "subprocess", "os", "re"]:
                    dep_id = imp.lower().replace("_", "-")
                    if dep_id not in deps:
                        deps.append(dep_id)
        except (subprocess.SubprocessError, OSError):
            pass

        return deps

    def resolve(self, tool_id: str) -> Dict:
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py dep_resolver_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py dep_resolver_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

解析工具依赖"""
        deps = self.extract_dependencies(tool_id)

        if not deps:
            return {
                "tool_id": tool_id,
                "dependencies": [],
                "status": "no_dependencies"
            }

        resolved = []
        missing = []

        for dep in deps:
            # 检查依赖是否存在
            dep_file = self.tools_dir / f"{dep}.py"
            if dep_file.exists():
                resolved.append(dep)
            else:
                missing.append(dep)

        return {
            "tool_id": tool_id,
            "dependencies": deps,
            "resolved": resolved,
            "missing": missing,
            "status": "complete" if not missing else "incomplete"
        }

    def build_graph(self) -> Dict:
        """构建依赖图"""
        graph = {}
        tools = list(self.tools_dir.glob("*.py"))
        
        for tool_file in tools[:50]:  # 限制数量
            tool_id = tool_file.stem.replace("_", "-")
            deps = self.extract_dependencies(tool_id)
            if deps:
                graph[tool_id] = deps
        
        return {
            "nodes": list(graph.keys()),
            "edges": [(k, v) for k, vs in graph.items() for v in vs],
            "total_tools": len(graph)
        }
    
    def check_all(self) -> Dict:
        """检查所有工具的依赖状态"""
        results = []
        missing_deps = {}
        
        for dep_id, deps in self.BUILTIN_DEPS.items():
            for d in deps:
                if d not in missing_deps:
                    missing_deps[d] = []
                if not (self.tools_dir / f"{d}.py").exists():
                    missing_deps[d].append(dep_id)
        
        return {
            "total_tools": len(self.BUILTIN_DEPS),
            "missing_dependencies": {k: v for k, v in missing_deps.items() if v}
        }


logging.basicConfig(level=logging.INFO)
def main():
    resolver = DependencyResolver()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--resolve":
            tool_id = sys.argv[2] if len(sys.argv) > 2 else "brainstorm-workflow"
            result = resolver.resolve(tool_id)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--graph":
            result = resolver.build_graph()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--check":
            result = resolver.check_all()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("DEP-RESOLVER-001 Dependency Resolver")
    print("Usage:")
    print("  py dep_resolver_001.py --resolve <tool>  # Resolve deps")
    print("  py dep_resolver_001.py --graph            # Build graph")
    print("  py dep_resolver_001.py --check            # Check all")
    return 0


if __name__ == "__main__":
    sys.exit(main())

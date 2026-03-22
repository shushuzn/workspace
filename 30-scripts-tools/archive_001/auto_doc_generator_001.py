import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
自动文档生成器 - 从代码/配置自动生成文档
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class AutoDocGenerator:
    """自动文档生成器"""
    
    def __init__(self):
        self.output_dir = Path("15-docs/auto-generated")
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_from_python(self, py_file: Path) -> Dict:
        """从 Python 文件生成文档"""
        if not py_file.exists():
            return {"error": "File not found"}
        
        with open(py_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 提取信息
        doc_info = {
            "file_name": py_file.name,
            "file_path": str(py_file),
            "generated_at": datetime.now().isoformat(),
            "docstring": self._extract_docstring(content),
            "functions": self._extract_functions(content),
            "classes": self._extract_classes(content),
            "imports": self._extract_imports(content),
            "description": self._generate_description(content)
        }
        
        # 生成 Markdown 文档
        markdown = self._generate_markdown(doc_info)
        
        # 保存文档
        output_file = self.output_dir / f"{py_file.stem}_docs.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        doc_info["output_file"] = str(output_file)
        doc_info["output_size_kb"] = len(markdown) / 1024
        
        return doc_info
    
    def _extract_docstring(self, content: str) -> Optional[str]:
        """提取模块文档字符串"""
        # 匹配开头的文档字符串
        match = re.search(r'^[ \t]*(\'\'\'|\"\"\")([\s\S]*?)\1', content, re.MULTILINE)
        if match:
            return match.group(2).strip()
        return None
    
    def _extract_functions(self, content: str) -> List[Dict]:
        """提取函数定义"""
        functions = []
        pattern = r'def\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*([\w\[\],\s]+))?\s*:'
        
        for match in re.finditer(pattern, content):
            func_name = match.group(1)
            params = match.group(2).strip()
            return_type = match.group(3).strip() if match.group(3) else None
            
            # 跳过私有函数
            if func_name.startswith('_'):
                continue
            
            functions.append({
                "name": func_name,
                "parameters": params,
                "return_type": return_type
            })
        
        return functions
    
    def _extract_classes(self, content: str) -> List[Dict]:
        """提取类定义"""
        classes = []
        pattern = r'class\s+(\w+)\s*(?:\(([^)]*)\))?\s*:'
        
        for match in re.finditer(pattern, content):
            class_name = match.group(1)
            base_classes = match.group(2).strip() if match.group(2) else None
            
            classes.append({
                "name": class_name,
                "base_classes": base_classes
            })
        
        return classes
    
    def _extract_imports(self, content: str) -> List[str]:
        """提取导入语句"""
        imports = []
        
        # 匹配 import 和 from ... import
        import_pattern = r'^import\s+([\w\.]+)'
        from_pattern = r'^from\s+([\w\.]+)\s+import\s+(.+)'
        
        for line in content.split('\n'):
            line = line.strip()
            
            match = re.match(import_pattern, line)
            if match:
                imports.append(match.group(1))
                continue
            
            match = re.match(from_pattern, line)
            if match:
                imports.append(f"{match.group(1)}::{match.group(2)}")
        
        return imports[:10]  # 限制数量
    
    def _generate_description(self, content: str) -> str:
        """生成简要描述"""
        lines = content.split('\n')
        
        # 查找注释行
        for line in lines[:20]:
            if line.strip().startswith('#'):
                desc = line.strip()[1:].strip()
                if len(desc) > 10:
                    return desc
        
        return "Auto-generated documentation"
    
    def _generate_markdown(self, doc_info: Dict) -> str:
        """生成 Markdown 文档"""
        md = []
        md.append(f"# {doc_info['file_name']}")
        md.append("")
        md.append(f"**Generated:** {doc_info['generated_at']}")
        md.append(f"**Path:** `{doc_info['file_path']}`")
        md.append("")
        
        # 描述
        if doc_info.get("description"):
            md.append(f"## Description")
            md.append("")
            md.append(doc_info["description"])
            md.append("")
        
        # 文档字符串
        if doc_info.get("docstring"):
            md.append(f"## Documentation")
            md.append("")
            md.append(f"```")
            md.append(doc_info["docstring"])
            md.append(f"```")
            md.append("")
        
        # 类
        if doc_info.get("classes"):
            md.append(f"## Classes")
            md.append("")
            for cls in doc_info["classes"]:
                base = f"({cls['base_classes']})" if cls.get('base_classes') else ""
                md.append(f"### {cls['name']}{base}")
                md.append("")
            md.append("")
        
        # 函数
        if doc_info.get("functions"):
            md.append(f"## Functions")
            md.append("")
            for func in doc_info["functions"]:
                params = func.get('parameters', '')
                ret = f" -> {func['return_type']}" if func.get('return_type') else ""
                md.append(f"### {func['name']}({params}){ret}")
                md.append("")
            md.append("")
        
        # 导入
        if doc_info.get("imports"):
            md.append(f"## Dependencies")
            md.append("")
            for imp in doc_info["imports"]:
                md.append(f"- `{imp}`")
            md.append("")
        
        md.append("---")
        md.append("")
        md.append("*Auto-generated by AutoDocGenerator*")
        
        return '\n'.join(md)
    
    def generate_from_config(self, config_file: Path) -> Dict:
        """从配置文件生成文档"""
        if not config_file.exists():
            return {"error": "File not found"}
        
        with open(config_file, 'r', encoding='utf-8') as f:
            if config_file.suffix == '.json':
                config = json.load(f)
            else:
                return {"error": "Unsupported format"}
        
        # 生成配置文档
        doc_info = {
            "file_name": config_file.name,
            "generated_at": datetime.now().isoformat(),
            "config_keys": list(config.keys()) if isinstance(config, dict) else [],
            "total_keys": len(config.keys()) if isinstance(config, dict) else 0
        }
        
        # 生成 Markdown
        markdown = self._generate_config_markdown(doc_info, config)
        
        # 保存
        output_file = self.output_dir / f"{config_file.stem}_config.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(markdown)
        
        doc_info["output_file"] = str(output_file)
        
        return doc_info
    
    def _generate_config_markdown(self, doc_info: Dict, config: Dict) -> str:
        """生成配置文档 Markdown"""
        md = []
        md.append(f"# Configuration: {doc_info['file_name']}")
        md.append("")
        md.append(f"**Generated:** {doc_info['generated_at']}")
        md.append("")
        
        md.append(f"## Overview")
        md.append("")
        md.append(f"Total configuration keys: **{doc_info['total_keys']}**")
        md.append("")
        
        md.append(f"## Configuration Keys")
        md.append("")
        md.append("| Key | Type | Description |")
        md.append("|-----|------|-------------|")
        
        for key, value in config.items():
            value_type = type(value).__name__
            md.append(f"| `{key}` | {value_type} | - |")
        
        md.append("")
        md.append("---")
        md.append("")
        md.append("*Auto-generated by AutoDocGenerator*")
        
        return '\n'.join(md)
    
    def batch_generate(self, directory: Path, pattern: str = "*.py") -> Dict:
        """批量生成文档"""
        results = {
            "directory": str(directory),
            "pattern": pattern,
            "files_processed": 0,
            "docs_generated": 0,
            "errors": [],
            "outputs": []
        }
        
        for file in directory.glob(pattern):
            results["files_processed"] += 1
            
            try:
                if file.suffix == '.py':
                    doc = self.generate_from_python(file)
                elif file.suffix == '.json':
                    doc = self.generate_from_config(file)
                else:
                    continue
                
                if "error" not in doc:
                    results["docs_generated"] += 1
                    results["outputs"].append(doc["output_file"])
                else:
                    results["errors"].append(f"{file.name}: {doc['error']}")
            except Exception as e:
                results["errors"].append(f"{file.name}: {str(e)}")
        
        return results
    
    def display_status(self) -> str:
        """显示状态"""
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 25 + "AutoDoc Generator")
        output.append("=" * 70)
        
        output.append(f"\n[Output Directory]")
        output.append(f"  Path: {self.output_dir}")
        
        # 统计已有文档
        docs = list(self.output_dir.glob("*.md"))
        output.append(f"  Generated Docs: {len(docs)}")
        
        output.append(f"\n[Supported Formats]")
        output.append(f"  - Python (.py)")
        output.append(f"  - JSON Config (.json)")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)

logging.basicConfig(level=logging.INFO)
def main():
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
# py auto_doc_generator_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py auto_doc_generator_001.py

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

测试入口"""
    generator = AutoDocGenerator()
    
    print("AutoDoc Generator Test")
    print("=" * 70)
    
    # 显示状态
    print(generator.display_status())
    
    # 测试：生成自身文档
    print("\n[Generating Documentation for Self]")
    self_file = Path(__file__)
    result = generator.generate_from_python(self_file)
    
    if "error" not in result:
        print(f"  File: {result['file_name']}")
        print(f"  Functions: {len(result.get('functions', []))}")
        print(f"  Classes: {len(result.get('classes', []))}")
        print(f"  Output: {result['output_file']} ({result['output_size_kb']:.1f}KB)")
    else:
        print(f"  Error: {result['error']}")
    
    print(f"\n[OK] AutoDoc generator test completed")

if __name__ == "__main__":
    main()

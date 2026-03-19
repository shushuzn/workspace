#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Doc Generator - 自动文档生成器

根据代码/项目结构自动生成文档
"""

import os
import json
from datetime import datetime
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"
DOCS_DIR = "15-docs"

def generate_project_overview():
    """生成项目概览文档"""
    doc = f"""# 📊 项目概览

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 目录结构

```
workspace/
├── 00-09/   → Core config
├── 10-19/   → Knowledge
├── 20-29/   → Data & Reports
├── 30-39/   → Tools
├── 40-49/   → Collectors
└── 90-99/   → Archive
```

## 关键指标

- 总文件数：{count_files(WORKSPACE)}
- 总代码行数：{count_lines(WORKSPACE)}
- 工具数量：{count_tools()}
- 工作流数量：{count_workflows()}

## 最近变更

{get_recent_changes()}

---

*本文档由 auto_doc_generator.py 自动生成*
"""
    return doc

def count_files(directory):
    """统计文件数"""
    count = 0
    try:
        for root, dirs, files in os.walk(directory):
            if any(skip in root for skip in ['node_modules', 'venv', '.git', '__pycache__']):
                continue
            count += len(files)
    except:
        pass
    return count

def count_lines(directory):
    """统计代码行数"""
    total = 0
    extensions = ['.py', '.js', '.ts', '.md', '.json', '.bat', '.sh']
    try:
        for root, dirs, files in os.walk(directory):
            if any(skip in root for skip in ['node_modules', 'venv', '.git', '__pycache__']):
                continue
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    try:
                        with open(os.path.join(root, file), 'r', encoding='utf-8', errors='ignore') as f:
                            total += len(f.readlines())
                    except:
                        pass
    except:
        pass
    return total

def count_tools():
    """统计工具数量"""
    registry_path = os.path.join(WORKSPACE, "30-scripts-tools", "tools_registry.json")
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return len(data.get('tools', {}))
    except:
        return 0

def count_workflows():
    """统计工作流数量"""
    workflow_dir = os.path.join(WORKSPACE, "flow-archive")
    count = 0
    try:
        for root, dirs, files in os.walk(workflow_dir):
            count += sum(1 for f in files if f.endswith('.json'))
    except:
        pass
    return count

def get_recent_changes():
    """获取最近变更"""
    import subprocess
    try:
        result = subprocess.run(
            ['git', 'log', '--oneline', '-5'],
            cwd=WORKSPACE,
            capture_output=True,
            text=True,
            encoding='utf-8'
        )
        return f"```\n{result.stdout}\n```"
    except:
        return "无法获取 Git 历史"

def generate_tool_docs():
    """生成工具文档"""
    registry_path = os.path.join(WORKSPACE, "30-scripts-tools", "tools_registry.json")
    try:
        with open(registry_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        tools = data.get('tools', {})
        version = data.get('version', 'unknown')
        
        doc = f"""# 🛠️ 工具文档

**版本:** {version}  
**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**工具总数:** {len(tools)}

## 工具列表

"""
        
        for tool_id, info in sorted(tools.items()):
            doc += f"""### {tool_id}

- **名称:** {info.get('name', 'N/A')}
- **描述:** {info.get('description', 'N/A')}
- **文件:** {info.get('file', 'N/A')}
- **类别:** {info.get('category', 'N/A')}
- **参数:** {', '.join(info.get('parameters', []))}
- **示例:** `{info.get('examples', [''])[0] if info.get('examples') else 'N/A'}`

"""
        
        return doc
    except Exception as e:
        return f"生成工具文档失败：{e}"

def generate_workflow_docs():
    """生成工作流文档"""
    workflow_path = os.path.join(WORKSPACE, "flow-archive", "20260318-universal-workflow-001", "workflow.json")
    try:
        with open(workflow_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        version = data.get('version', 'unknown')
        steps = data.get('steps', [])
        
        doc = f"""# 🔄 工作流文档

**工作流 ID:** 20260318-universal-workflow-001  
**版本:** {version}  
**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**总步骤:** {len(steps)}

## 步骤列表

"""
        
        for step in steps:
            step_id = step.get('step_id', 'N/A')
            name = step.get('name', 'N/A')
            desc = step.get('description', 'N/A')
            blocking = "是" if step.get('blocking', False) else "否"
            timeout = step.get('timeout_seconds', 'N/A')
            
            doc += f"""### Step {step_id}: {name}

- **描述:** {desc}
- **阻塞:** {blocking}
- **超时:** {timeout}秒
- **工具:** {step.get('tool_id', 'N/A')}

"""
        
        return doc
    except Exception as e:
        return f"生成工作流文档失败：{e}"

def main():
    """主函数"""
    print("=" * 60)
    print("Auto Doc Generator v1.0 - 自动文档生成器")
    print("=" * 60)
    
    docs_output = os.path.join(WORKSPACE, DOCS_DIR)
    os.makedirs(docs_output, exist_ok=True)
    
    # 生成项目概览
    print("\n[1/3] 生成项目概览...")
    project_doc = generate_project_overview()
    project_path = os.path.join(docs_output, "PROJECT-OVERVIEW.md")
    with open(project_path, 'w', encoding='utf-8') as f:
        f.write(project_doc)
    print(f"✅ 已保存：{project_path}")
    
    # 生成工具文档
    print("\n[2/3] 生成工具文档...")
    tool_doc = generate_tool_docs()
    tool_path = os.path.join(docs_output, "TOOLS-DOCUMENTATION.md")
    with open(tool_path, 'w', encoding='utf-8') as f:
        f.write(tool_doc)
    print(f"✅ 已保存：{tool_path}")
    
    # 生成工作流文档
    print("\n[3/3] 生成工作流文档...")
    workflow_doc = generate_workflow_docs()
    workflow_path = os.path.join(docs_output, "WORKFLOW-DOCUMENTATION.md")
    with open(workflow_path, 'w', encoding='utf-8') as f:
        f.write(workflow_doc)
    print(f"✅ 已保存：{workflow_path}")
    
    print("\n" + "=" * 60)
    print("✅ 文档生成完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()

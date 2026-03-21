import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流模板库 - 预定义常用工作流模板
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

class WorkflowTemplates:
    """工作流模板库"""
    
    def __init__(self):
        self.templates_dir = Path("flow-archive/20260318-universal-workflow-001/templates")
        self.templates_dir.mkdir(parents=True, exist_ok=True)
        self.registry_file = self.templates_dir / "template_registry.json"
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """加载模板注册表"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "templates": {},
            "total_uses": 0,
            "updated_at": datetime.now().isoformat()
        }
    
    def _save_registry(self):
        """保存注册表"""
        self.registry['updated_at'] = datetime.now().isoformat()
        with open(self.registry_file, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, ensure_ascii=False, indent=2)
    
    def register_template(self, template_id: str, template_data: Dict) -> bool:
        """注册模板"""
        self.registry['templates'][template_id] = {
            "id": template_id,
            "name": template_data.get('name', template_id),
            "description": template_data.get('description', ''),
            "steps": template_data.get('steps', []),
            "created_at": datetime.now().isoformat(),
            "uses": 0,
            "file": str(self.templates_dir / f"{template_id}.json")
        }
        
        # 保存模板文件
        template_file = self.templates_dir / f"{template_id}.json"
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template_data, f, ensure_ascii=False, indent=2)
        
        self._save_registry()
        return True
    
    def use_template(self, template_id: str) -> Optional[Dict]:
        """使用模板"""
        if template_id not in self.registry['templates']:
            return None
        
        # 读取模板
        template_file = self.templates_dir / f"{template_id}.json"
        with open(template_file, 'r', encoding='utf-8') as f:
            template = json.load(f)
        
        # 更新使用计数
        self.registry['templates'][template_id]['uses'] += 1
        self.registry['total_uses'] += 1
        self._save_registry()
        
        return template
    
    def list_templates(self) -> List[Dict]:
        """列出所有模板"""
        return list(self.registry['templates'].values())
    
    def get_template(self, template_id: str) -> Optional[Dict]:
        """获取模板详情"""
        return self.registry['templates'].get(template_id)
    
    def create_default_templates(self):
        """创建默认模板"""
        # 模板 1: 研究任务
        research_template = {
            "name": "Research Task",
            "description": "Standard research workflow with literature review and analysis",
            "steps": [
                {"id": 1, "name": "Define research question"},
                {"id": 2, "name": "Literature search"},
                {"id": 3, "name": "Data collection"},
                {"id": 4, "name": "Analysis"},
                {"id": 5, "name": "Write report"},
                {"id": 6, "name": "Review and validate"},
                {"id": 7, "name": "Publish results"}
            ],
            "estimated_time_minutes": 120,
            "complexity": "high"
        }
        self.register_template("research-001", research_template)
        
        # 模板 2: 项目任务
        project_template = {
            "name": "Project Task",
            "description": "Standard project execution workflow",
            "steps": [
                {"id": 1, "name": "Define project scope"},
                {"id": 2, "name": "Plan tasks"},
                {"id": 3, "name": "Execute tasks"},
                {"id": 4, "name": "Test and validate"},
                {"id": 5, "name": "Document"},
                {"id": 6, "name": "Deploy"},
                {"id": 7, "name": "Review"}
            ],
            "estimated_time_minutes": 90,
            "complexity": "medium"
        }
        self.register_template("project-001", project_template)
        
        # 模板 3: 文档任务
        doc_template = {
            "name": "Documentation Task",
            "description": "Quick documentation workflow",
            "steps": [
                {"id": 1, "name": "Gather requirements"},
                {"id": 2, "name": "Draft content"},
                {"id": 3, "name": "Review"},
                {"id": 4, "name": "Format"},
                {"id": 5, "name": "Publish"}
            ],
            "estimated_time_minutes": 45,
            "complexity": "low"
        }
        self.register_template("doc-001", doc_template)
        
        # 模板 4: 快速修复
        fix_template = {
            "name": "Quick Fix",
            "description": "Fast bug fix workflow (skip heavy validation)",
            "steps": [
                {"id": 1, "name": "Identify issue"},
                {"id": 2, "name": "Fix code"},
                {"id": 3, "name": "Test fix"},
                {"id": 4, "name": "Commit"}
            ],
            "estimated_time_minutes": 20,
            "complexity": "low"
        }
        self.register_template("fix-001", fix_template)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return {
            "total_templates": len(self.registry['templates']),
            "total_uses": self.registry['total_uses'],
            "most_used": max(
                self.registry['templates'].values(),
                key=lambda x: x['uses'],
                default=None
            )
        }
    
    def display_status(self) -> str:
        """显示状态"""
        stats = self.get_stats()
        templates = self.list_templates()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 22 + "Workflow Templates Library")
        output.append("=" * 70)
        
        output.append(f"\n[Library Stats]")
        output.append(f"  Total Templates:  {stats['total_templates']}")
        output.append(f"  Total Uses:       {stats['total_uses']}")
        
        output.append(f"\n[Available Templates]")
        for template in templates:
            output.append(f"\n  {template['id']}: {template['name']}")
            output.append(f"    Description: {template['description']}")
            output.append(f"    Steps: {len(template['steps'])}")
            output.append(f"    Uses: {template['uses']}")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)
    
    def run(self) -> Dict:
        """运行模板库"""
        return {
            "stats": self.get_stats(),
            "templates": self.list_templates(),
            "success": True
        }

logging.basicConfig(level=logging.INFO)
def main():
    """测试入口"""
    templates = WorkflowTemplates()
    
    print("Workflow Templates Test")
    print("=" * 70)
    
    # 创建默认模板
    templates.create_default_templates()
    print(f"\n[OK] Created default templates")
    
    # 列出模板
    template_list = templates.list_templates()
    print(f"[OK] Available templates: {len(template_list)}")
    
    # 使用模板
    research = templates.use_template("research-001")
    print(f"[OK] Used template: research-001")
    
    # 显示状态
    print(templates.display_status())
    
    print(f"\n[OK] Templates test completed")

if __name__ == "__main__":
    main()

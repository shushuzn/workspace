#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
REPORT-003 Template Generator
【模板生成器】

功能:
  - 报告模板创建
  - 变量替换
  - 样式定制
"""
import json
import sys
from pathlib import Path


class TemplateGenerator:
    """模板生成器"""
    
    TEMPLATES = {
        "status": {
            "name": "Status Report",
            "variables": ["project", "date", "status", "owner"],
            "content": "# Status Report\n\n**Project:** {project}\n**Date:** {date}\n**Status:** {status}\n**Owner:** {owner}\n\n## Details\n\n"
        },
        "metric": {
            "name": "Metrics Report", 
            "variables": ["metric_name", "value", "target", "trend"],
            "content": "# Metrics Report\n\n**Metric:** {metric_name}\n**Value:** {value}\n**Target:** {target}\n**Trend:** {trend}\n\n"
        },
        "summary": {
            "name": "Executive Summary",
            "variables": ["title", "overview", "key_points", "recommendation"],
            "content": "# {title}\n\n## Overview\n{overview}\n\n## Key Points\n{key_points}\n\n## Recommendation\n{recommendation}\n"
        }
    }
    
    @staticmethod
    def list_templates() -> list:
        return [{"id": k, "name": v["name"], "vars": v["variables"]} 
                for k, v in TemplateGenerator.TEMPLATES.items()]
    
    @staticmethod
    def generate(template_id: str, values: dict = None) -> str:
        template = TemplateGenerator.TEMPLATES.get(template_id, {})
        content = template.get("content", "")
        
        if values:
            for key, value in values.items():
                content = content.replace(f"{{{key}}}", str(value))
        
        return content
    
    @staticmethod
    def get_variables(template_id: str) -> list:
        template = TemplateGenerator.TEMPLATES.get(template_id, {})
        return template.get("variables", [])


def main():
    generator = TemplateGenerator()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--list":
            print(json.dumps(generator.list_templates(), ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--generate":
            tid = sys.argv[2] if len(sys.argv) > 2 else "status"
            result = generator.generate(tid)
            print(result)
            return 0
        
        if cmd == "--vars":
            tid = sys.argv[2] if len(sys.argv) > 2 else "status"
            print(json.dumps(generator.get_variables(tid), ensure_ascii=False, indent=2))
            return 0
    
    print("REPORT-003 Template Generator")
    print("Usage:")
    print("  py report_003.py --list")
    print("  py report_003.py --generate <template_id>")
    print("  py report_003.py --vars <template_id>")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
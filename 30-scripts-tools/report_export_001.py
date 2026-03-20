#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
REPORT-002 Export Tool
【导出工具】

功能:
  - 数据导出为多种格式
  - 批量导出
  - 自定义字段
"""
import json
import sys
import csv
from pathlib import Path


class ExportTool:
    """导出工具"""
    
    SUPPORTED_FORMATS = ["json", "csv", "txt", "xml"]
    
    @staticmethod
    def export_json(data: list, file_path: str = None) -> str:
        content = json.dumps(data, ensure_ascii=False, indent=2)
        if file_path:
            Path(file_path).write_text(content, encoding="utf-8")
        return content
    
    @staticmethod
    def export_csv(data: list, file_path: str = None) -> str:
        if not data:
            return ""
        
        headers = list(data[0].keys())
        lines = [",".join(headers)]
        
        for row in data:
            values = [str(row.get(h, "")) for h in headers]
            lines.append(",".join(values))
        
        content = "\n".join(lines)
        if file_path:
            Path(file_path).write_text(content, encoding="utf-8")
        return content
    
    @staticmethod
    def export_txt(data: list, file_path: str = None) -> str:
        lines = []
        for i, row in enumerate(data, 1):
            lines.append(f"--- Item {i} ---")
            for k, v in row.items():
                lines.append(f"  {k}: {v}")
            lines.append("")
        
        content = "\n".join(lines)
        if file_path:
            Path(file_path).write_text(content, encoding="utf-8")
        return content
    
    @staticmethod
    def export_xml(data: list, file_path: str = None) -> str:
        xml = '<?xml version="1.0" encoding="UTF-8"?>\n<items>\n'
        for row in data:
            xml += "  <item>\n"
            for k, v in row.items():
                xml += f"    <{k}>{v}</{k}>\n"
            xml += "  </item>\n"
        xml += "</items>"
        
        if file_path:
            Path(file_path).write_text(xml, encoding="utf-8")
        return xml


def main():
    tool = ExportTool()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--json":
            sample = [{"id": 1, "name": "Test", "value": 100}]
            print(tool.export_json(sample))
            return 0
        
        if cmd == "--csv":
            sample = [{"id": 1, "name": "Test", "value": 100}]
            print(tool.export_csv(sample))
            return 0
        
        if cmd == "--txt":
            sample = [{"id": 1, "name": "Test", "value": 100}]
            print(tool.export_txt(sample))
            return 0
        
        if cmd == "--xml":
            sample = [{"id": 1, "name": "Test", "value": 100}]
            print(tool.export_xml(sample))
            return 0
    
    print("REPORT-002 Export Tool")
    print("Usage:")
    print("  py report_002.py --json")
    print("  py report_002.py --csv")
    print("  py report_002.py --txt")
    print("  py report_002.py --xml")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
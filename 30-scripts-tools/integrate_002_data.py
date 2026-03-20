#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
INTEGRATE-002 Data Connector
【数据连接器】

功能:
  - CSV/JSON数据导入
  - 数据转换
  - 批量处理
"""
import json
import sys
import csv
from pathlib import Path


class DataConnector:
    """数据连接器"""
    
    @staticmethod
    def read_csv(file_path: str) -> list:
        """读取CSV"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
        return data
    
    @staticmethod
    def read_json(file_path: str) -> dict:
        """读取JSON"""
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    @staticmethod
    def convert_format(input_data: list, output_format: str = "json") -> str:
        """转换格式"""
        if output_format == "json":
            return json.dumps(input_data, ensure_ascii=False, indent=2)
        return str(input_data)
    
    @staticmethod
    def filter_data(data: list, key: str, value: str) -> list:
        """过滤数据"""
        return [item for item in data if item.get(key) == value]


def main():
    connector = DataConnector()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--csv":
            path = sys.argv[2] if len(sys.argv) > 2 else "data.csv"
            try:
                data = connector.read_csv(path)
                print(json.dumps(data[:3], ensure_ascii=False, indent=2))
            except Exception as e:
                print(f"Error: {e}")
            return 0
        
        if cmd == "--json":
            path = sys.argv[2] if len(sys.argv) > 2 else "data.json"
            try:
                data = connector.read_json(path)
                print(json.dumps(data, ensure_ascii=False, indent=2))
            except Exception as e:
                print(f"Error: {e}")
            return 0
        
        if cmd == "--convert":
            print(connector.convert_format([{"a": 1}, {"b": 2}], "json"))
            return 0
    
    print("INTEGRATE-002 Data Connector")
    print("Usage:")
    print("  py integrate_002.py --csv <path>")
    print("  py integrate_002.py --json <path>")
    print("  py integrate_002.py --convert")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
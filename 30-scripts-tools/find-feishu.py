#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""查找飞书缓存位置"""

import os
from pathlib import Path

def find_feishu_paths():
    """查找所有可能的飞书路径"""
    search_paths = [
        Path(r"C:\Users"),
        Path(r"D:\Users"),
        Path(os.getenv('APPDATA', '')),
        Path(os.getenv('LOCALAPPDATA', '')),
        Path(r"C:\Program Files"),
        Path(r"D:\Program Files"),
    ]
    
    keywords = ['Lark', 'feishu', 'Feishu', '飞书']
    
    print("="*70)
    print("  飞书路径搜索")
    print("="*70)
    
    found = []
    
    for base in search_paths:
        if not base.exists():
            continue
        
        print(f"\n搜索：{base}")
        
        try:
            for item in base.rglob('*'):
                if item.is_dir():
                    name = item.name
                    for kw in keywords:
                        if kw.lower() in name.lower():
                            found.append(item)
                            print(f"  [FOUND] {item}")
                            break
        except Exception as e:
            print(f"  [SKIP] 权限不足或错误")
    
    print(f"\n{'='*70}")
    print(f"  共找到 {len(found)} 个相关目录")
    print("="*70)
    
    return found

if __name__ == "__main__":
    find_feishu_paths()

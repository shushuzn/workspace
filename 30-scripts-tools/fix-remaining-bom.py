#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速修复剩余 BOM 头问题
"""

import sys
import io
from pathlib import Path

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent

FILES_TO_FIX = [
    "06-research/领域研究/cnt-lig-composite/data/cnt_lig_composite_dataset.csv",
    "06-research/领域研究/cnt-lig-graphene-mxene-pedot-quinary/data/quinary_composite_dataset.csv",
    "06-research/领域研究/cnt-lig-graphene-mxene-quaternary/data/quaternary_composite_dataset.csv",
]

def fix_bom(file_path):
    """修复 BOM 头"""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()
        
        if data[:3] == b'\xef\xbb\xbf':
            with open(file_path, 'wb') as f:
                f.write(data[3:])
            return True
        return False
    except Exception as e:
        print(f"  ❌ {file_path}: {e}")
        return False

def main():
    print("=" * 60)
    print("修复剩余 BOM 头")
    print("=" * 60)
    
    fixed = 0
    for file_str in FILES_TO_FIX:
        file_path = WORKSPACE / file_str.replace('/', '\\')
        if file_path.exists():
            print(f"\n处理：{file_str}")
            if fix_bom(file_path):
                print(f"  ✅ 修复成功")
                fixed += 1
            else:
                print(f"  ℹ️ 无需修复 (无 BOM)")
        else:
            print(f"  ⚠️ 文件不存在：{file_str}")
    
    print(f"\n修复完成：{fixed}/{len(FILES_TO_FIX)}")

if __name__ == "__main__":
    main()

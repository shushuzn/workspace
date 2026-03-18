#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
工具深度优化
1. 分析超大文件 (>30KB)
2. 识别可简化的函数
3. 删除未使用的导入
"""

import os
import sys
import io
import ast
from pathlib import Path
from collections import defaultdict

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TOOLS_DIR = Path(__file__).parent.parent / "30-scripts-tools"

def analyze_large_files():
    """分析超大文件"""
    print("="*60)
    print("🔍 大文件分析")
    print("="*60)
    
    large_files = []
    for py_file in TOOLS_DIR.glob("*.py"):
        size = py_file.stat().st_size
        if size > 30*1024:  # >30KB
            large_files.append((py_file, size))
    
    print(f"\n发现 {len(large_files)} 个大文件 (>30KB):\n")
    
    for file, size in sorted(large_files, key=lambda x: x[1], reverse=True):
        print(f"📄 {file.name}")
        print(f"   大小：{size/1024:.1f}KB")
        print(f"   路径：{file.relative_to(TOOLS_DIR.parent)}")
        
        # 分析代码结构
        try:
            with open(file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # 统计函数数量
            functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]
            classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
            
            print(f"   函数：{len(functions)} 个")
            print(f"   类：{len(classes)} 个")
            
            # 识别超大函数 (>50 行)
            large_funcs = []
            for func in functions:
                func_lines = func.end_lineno - func.lineno if hasattr(func, 'end_lineno') else 0
                if func_lines > 50:
                    large_funcs.append((func.name, func_lines))
            
            if large_funcs:
                print(f"   ⚠️  超大函数 (>50 行): {len(large_funcs)} 个")
                for fname, flines in sorted(large_funcs, key=lambda x: x[1], reverse=True)[:3]:
                    print(f"      - {fname}() ({flines}行)")
            
            # 统计导入数量
            imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
            print(f"   导入：{len(imports)} 个")
            
        except Exception as e:
            print(f"   ⚠️  无法解析：{e}")
        
        print()
    
    return large_files

def find_code_smells():
    """识别代码异味"""
    print("="*60)
    print("🔍 代码异味检测")
    print("="*60)
    
    smells = []
    
    for py_file in TOOLS_DIR.glob("*.py"):
        if py_file.stat().st_size < 5*1024:  # 跳过小文件
            continue
        
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            # 检测重复代码模式
            line_counts = defaultdict(int)
            for line in lines:
                stripped = line.strip()
                if len(stripped) > 20:  # 忽略短行
                    line_counts[stripped] += 1
            
            duplicates = {k: v for k, v in line_counts.items() if v > 3}
            if duplicates:
                smells.append({
                    'file': py_file,
                    'type': '重复代码',
                    'count': len(duplicates)
                })
            
            # 检测过长行 (>120 字符)
            long_lines = [i+1 for i, line in enumerate(lines) if len(line.strip()) > 120]
            if len(long_lines) > 10:
                smells.append({
                    'file': py_file,
                    'type': '过长行',
                    'count': len(long_lines)
                })
            
            # 检测过多注释 (>30%)
            comment_lines = sum(1 for line in lines if line.strip().startswith('#'))
            total_lines = len([l for l in lines if l.strip()])
            if total_lines > 0 and comment_lines / total_lines > 0.3:
                smells.append({
                    'file': py_file,
                    'type': '过多注释',
                    'ratio': f"{comment_lines/total_lines*100:.1f}%"
                })
        
        except Exception as e:
            pass
    
    print(f"\n发现 {len(smells)} 个代码异味:\n")
    
    # 按文件分组
    by_file = defaultdict(list)
    for smell in smells:
        by_file[smell['file']].append(smell)
    
    for file, file_smells in sorted(by_file.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"📄 {file.name}:")
        for smell in file_smells:
            print(f"   - {smell['type']}: {smell.get('count', smell.get('ratio', 'N/A'))}")
        print()
    
    return smells

def optimization_tips(large_files, smells):
    """提供优化建议"""
    print("="*60)
    print("💡 优化建议")
    print("="*60)
    
    tips = []
    
    # 针对大文件
    if large_files:
        tips.append("\n1. 📦 大文件重构优先级:")
        for file, size in large_files[:5]:
            tips.append(f"   - {file.name} ({size/1024:.1f}KB)")
        tips.append("   建议：拆分为多个模块，每个<20KB")
    
    # 针对代码异味
    if smells:
        tips.append("\n2. 🧹 代码清理:")
        tips.append("   - 删除重复代码 → 提取为公共函数")
        tips.append("   - 缩短过长行 → 使用括号换行")
        tips.append("   - 精简注释 → 保留关键说明，删除冗余")
    
    tips.append("\n3. 📊 目标指标:")
    tips.append("   - 平均文件大小：<15KB")
    tips.append("   - 最大文件：<50KB")
    tips.append("   - 函数长度：<30 行")
    tips.append("   - 重复代码：<5%")
    
    for tip in tips:
        print(tip)
    
    print("\n" + "="*60)

def main():
    print("="*60)
    print("🚀 工具深度优化分析")
    print("="*60)
    
    # 1. 分析大文件
    large_files = analyze_large_files()
    
    # 2. 检测代码异味
    smells = find_code_smells()
    
    # 3. 提供优化建议
    optimization_tips(large_files, smells)
    
    print("✅ 分析完成！")
    print("\n下一步：根据建议手动重构大文件")

if __name__ == "__main__":
    main()

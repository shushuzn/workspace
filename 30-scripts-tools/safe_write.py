#!/usr/bin/env python3
"""
写文件防护包装器 - 强制路径验证
用法：from safe_write import safe_write
"""

from pathlib import Path
import sys
import os

# 添加工作区到路径
WORKSPACE = Path(__file__).parent.parent
CONFIG = Path(r"C:\Users\华为\.copaw")
ALLOWED_CONFIG_FILES = ["MEMORY.md", "SOUL.md", "PROFILE.md", "AGENTS.md", "HEARTBEAT.md"]

def validate_and_fix_path(file_path: str) -> str:
    """
    验证并修正文件路径
    
    规则:
    1. 配置文件 -> C 盘
    2. 其他文件 -> D 盘
    3. 自动修正错误路径
    """
    path = Path(file_path).resolve()
    path_str = str(path)
    file_name = path.name
    
    # 检查是否是配置文件
    if file_name in ALLOWED_CONFIG_FILES:
        # 配置文件应该在 C 盘
        if not path_str.startswith(str(CONFIG)):
            correct_path = CONFIG / file_name
            print(f"[AUTO-FIX] 配置文件路径修正:")
            print(f"  原路径：{path}")
            print(f"  修正为：{correct_path}")
            return str(correct_path)
        return path_str
    
    # 非配置文件应该在 D 盘
    if path_str.startswith(str(CONFIG)):
        # 在 C 盘但不是配置文件 → 移动到 D 盘
        correct_path = WORKSPACE / file_name
        print(f"[AUTO-FIX] 工作文件路径修正:")
        print(f"  原路径：{path}")
        print(f"  修正为：{correct_path}")
        
        # 如果原文件存在，移动它
        if path.exists():
            print(f"[AUTO-FIX] 移动现有文件...")
            path.rename(correct_path)
        
        return str(correct_path)
    
    # 已经在 D 盘 → 正确
    if path_str.startswith(str(WORKSPACE)):
        return path_str
    
    # 其他位置 → 建议移动到 D 盘
    correct_path = WORKSPACE / file_name
    print(f"[WARN] 文件在非标准位置:")
    print(f"  原路径：{path}")
    print(f"  建议：{correct_path}")
    return str(correct_path)

def safe_write(file_path: str, content: str, encoding: str = 'utf-8'):
    """
    安全写入文件 - 自动验证和修正路径
    
    Args:
        file_path: 文件路径
        content: 文件内容
        encoding: 编码 (默认 utf-8)
    """
    # 验证并修正路径
    corrected_path = validate_and_fix_path(file_path)
    
    # 确保目录存在
    Path(corrected_path).parent.mkdir(parents=True, exist_ok=True)
    
    # 写入文件
    with open(corrected_path, 'w', encoding=encoding) as f:
        f.write(content)
    
    print(f"[OK] 文件已写入：{corrected_path}")
    return corrected_path

def safe_read(file_path: str, encoding: str = 'utf-8') -> str:
    """
    安全读取文件 - 自动验证路径
    
    Args:
        file_path: 文件路径
        encoding: 编码 (默认 utf-8)
    
    Returns:
        文件内容
    """
    # 验证路径
    path = Path(file_path).resolve()
    path_str = str(path)
    
    # 检查路径合法性
    if not (path_str.startswith(str(WORKSPACE)) or 
            (path_str.startswith(str(CONFIG)) and path.name in ALLOWED_CONFIG_FILES)):
        print(f"[WARN] 读取非标准路径：{path}")
    
    # 读取文件
    with open(path, 'r', encoding=encoding) as f:
        return f.read()

# 测试
if __name__ == "__main__":
    print("=" * 60)
    print("Safe Write 防护包装器测试")
    print("=" * 60)
    
    # 测试 1: C 盘非配置文件 → 自动修正到 D 盘
    print("\n[测试 1] C 盘非配置文件:")
    test_path = r"C:\Users\华为\.copaw\test-file.md"
    corrected = validate_and_fix_path(test_path)
    print(f"  结果：{corrected}")
    
    # 测试 2: C 盘配置文件 → 保持 C 盘
    print("\n[测试 2] C 盘配置文件:")
    test_path = r"C:\Users\华为\.copaw\MEMORY.md"
    corrected = validate_and_fix_path(test_path)
    print(f"  结果：{corrected}")
    
    # 测试 3: D 盘文件 → 保持 D 盘
    print("\n[测试 3] D 盘工作文件:")
    test_path = r"str(Path(__file__).parent.parent)\report.md"
    corrected = validate_and_fix_path(test_path)
    print(f"  结果：{corrected}")
    
    # 测试 4: 其他位置 → 建议 D 盘
    print("\n[测试 4] 其他位置:")
    test_path = r"E:\other\file.md"
    corrected = validate_and_fix_path(test_path)
    print(f"  结果：{corrected}")
    
    print("\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)

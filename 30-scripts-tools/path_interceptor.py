#!/usr/bin/env python3
"""
工具路径拦截器 - 修改工具默认行为
用法：在工具调用前导入

效果：拦截 write_file 等工具调用，自动修正路径
"""

import os
import sys
from pathlib import Path

# 工作区配置
WORKSPACE = Path(__file__).parent.parent
CONFIG = Path(r"C:\Users\华为\.copaw")
ALLOWED_CONFIG_FILES = ["MEMORY.md", "SOUL.md", "PROFILE.md", "AGENTS.md", "HEARTBEAT.md"]

# 导入环境变量
from workspace_init import init_workspace
init_workspace()

class PathInterceptor:
    """路径拦截器 - 自动修正工具路径"""
    
    @staticmethod
    def intercept_path(file_path: str) -> str:
        """
        拦截并修正文件路径
        
        规则:
        1. 配置文件 → C 盘
        2. 其他文件 → D 盘
        3. 自动修正错误路径
        """
        path = Path(file_path)
        path_str = str(path.resolve()) if path.is_absolute() else str((WORKSPACE / path).resolve())
        file_name = path.name
        
        # 配置文件白名单 → C 盘 (支持 MEMORY.md, MEMORY-TEST.md 等)
        is_config = any(
            file_name == cfg or file_name.startswith(cfg.replace('.md', '-'))
            for cfg in ALLOWED_CONFIG_FILES
        )
        
        # 配置文件 → C 盘
        if is_config:
            if not path_str.startswith(str(CONFIG)):
                print(f"[INTERCEPT] 配置文件路径修正:")
                print(f"  原路径：{path}")
                print(f"  修正为：{CONFIG / file_name}")
                return str(CONFIG / file_name)
            return path_str
        
        # 非配置文件 → D 盘
        if path_str.startswith(str(CONFIG)):
            print(f"[INTERCEPT] 工作文件路径修正:")
            print(f"  原路径：{path}")
            print(f"  修正为：{WORKSPACE / file_name}")
            return str(WORKSPACE / file_name)
        
        # 已在 D 盘 → 正确
        if path_str.startswith(str(WORKSPACE)):
            return path_str
        
        # 其他位置 → 建议 D 盘
        print(f"[INTERCEPT] 非标准位置:")
        print(f"  原路径：{path}")
        print(f"  建议：{WORKSPACE / file_name}")
        return str(WORKSPACE / file_name)
    
    @staticmethod
    def wrap_write_file(original_write_file):
        """
        包装 write_file 函数，自动修正路径
        
        用法:
            write_file = PathInterceptor.wrap_write_file(original_write_file)
        """
        def wrapped_write_file(file_path, content, **kwargs):
            # 修正路径
            corrected_path = PathInterceptor.intercept_path(file_path)
            # 调用原函数
            return original_write_file(corrected_path, content, **kwargs)
        
        return wrapped_write_file

# 自动拦截示例
def demo_intercept():
    """演示路径拦截"""
    print("=" * 60)
    print("路径拦截器演示")
    print("=" * 60)
    
    test_paths = [
        r"C:\Users\华为\.copaw\test.md",
        r"C:\Users\华为\.copaw\MEMORY.md",
        r"str(Path(__file__).parent.parent)\report.md",
        r"E:\other\file.md",
    ]
    
    print("\n测试路径拦截:")
    for path in test_paths:
        corrected = PathInterceptor.intercept_path(path)
        print(f"  {path}")
        print(f"    → {corrected}")
        print()

if __name__ == "__main__":
    demo_intercept()

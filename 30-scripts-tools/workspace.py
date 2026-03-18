#!/usr/bin/env python3
"""
工作区路径管理 - 确保所有文件操作在正确目录
用法：from workspace import Workspace
"""

from pathlib import Path
import os
import sys

class Workspace:
    """工作区路径管理器"""
    
    # 主工作区
    WORKSPACE = Path(__file__).parent.parent
    
    # 配置区 (仅配置文件)
    CONFIG = Path(r"C:\Users\华为\.copaw")
    
    # 允许的配置文件
    ALLOWED_CONFIG_FILES = ["MEMORY.md", "SOUL.md", "PROFILE.md", "AGENTS.md", "HEARTBEAT.md"]
    
    # 子目录
    SCRIPTS = WORKSPACE / "30-scripts-tools"
    REPORTS = WORKSPACE / "20-data-reports"
    MEMORY = WORKSPACE / "13-memory-记忆系统"
    PERSONA = WORKSPACE / "00-人格系统"
    DATA = WORKSPACE / "20-data-reports"
    TOOLS = WORKSPACE / "30-scripts-tools"
    
    @classmethod
    def get_path(cls, filename: str, is_config: bool = False) -> Path:
        """
        获取文件完整路径
        
        Args:
            filename: 文件名
            is_config: 是否是配置文件 (默认 False)
        
        Returns:
            完整路径
        
        Raises:
            ValueError: 如果配置文件名称不合法
        """
        if is_config:
            if filename not in cls.ALLOWED_CONFIG_FILES:
                raise ValueError(f"配置文件只能是：{cls.ALLOWED_CONFIG_FILES}")
            return cls.CONFIG / filename
        else:
            return cls.WORKSPACE / filename
    
    @classmethod
    def get_script_path(cls, filename: str) -> Path:
        """获取脚本文件路径"""
        return cls.SCRIPTS / filename
    
    @classmethod
    def get_report_path(cls, filename: str) -> Path:
        """获取报告文件路径"""
        return cls.REPORTS / filename
    
    @classmethod
    def get_memory_path(cls, filename: str) -> Path:
        """获取记忆文件路径"""
        return cls.MEMORY / filename
    
    @classmethod
    def get_persona_path(cls, filename: str) -> Path:
        """获取人格系统文件路径"""
        return cls.PERSONA / filename
    
    @classmethod
    def get_data_path(cls, filename: str) -> Path:
        """获取数据文件路径"""
        return cls.DATA / filename
    
    @classmethod
    def get_tools_path(cls, filename: str) -> Path:
        """获取工具文件路径"""
        return cls.TOOLS / filename
    
    @classmethod
    def validate_path(cls, path: str) -> bool:
        """
        验证路径是否合法
        
        Args:
            path: 文件路径
        
        Returns:
            bool: 是否合法
        """
        path = Path(path).resolve()
        path_str = str(path)
        
        # 检查配置目录
        if path_str.startswith(str(cls.CONFIG)):
            return path.name in cls.ALLOWED_CONFIG_FILES
        
        # 检查工作区
        return path_str.startswith(str(cls.WORKSPACE))
    
    @classmethod
    def suggest_path(cls, path: str) -> str:
        """
        建议正确的路径
        
        Args:
            path: 原路径
        
        Returns:
            建议的正确路径
        """
        path = Path(path).resolve()
        path_str = str(path)
        
        # 如果在配置目录但不是配置文件
        if path_str.startswith(str(cls.CONFIG)):
            if path.name not in cls.ALLOWED_CONFIG_FILES:
                return str(cls.WORKSPACE / path.name)
        
        # 如果在其他位置
        if not path_str.startswith(str(cls.WORKSPACE)):
            return str(cls.WORKSPACE / path.name)
        
        # 路径正确
        return str(path)
    
    @classmethod
    def ensure_dirs(cls):
        """确保所有子目录存在"""
        dirs = [cls.WORKSPACE, cls.SCRIPTS, cls.REPORTS, cls.MEMORY, cls.PERSONA, cls.DATA, cls.TOOLS]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        print(f"[OK] 工作区目录已确认:")
        print(f"   WORKSPACE: {cls.WORKSPACE}")
        print(f"   SCRIPTS: {cls.SCRIPTS}")
        print(f"   REPORTS: {cls.REPORTS}")
        print(f"   MEMORY: {cls.MEMORY}")
        print(f"   PERSONA: {cls.PERSONA}")
        print(f"   DATA: {cls.DATA}")
        print(f"   TOOLS: {cls.TOOLS}")

def demo():
    """演示 Workspace 类的使用"""
    print("=" * 60)
    print("Workspace 路径管理器演示")
    print("=" * 60)
    
    # 确保目录存在
    Workspace.ensure_dirs()
    print()
    
    # 获取各种路径
    print("[INFO] 获取路径示例:")
    print(f"  报告路径：{Workspace.get_report_path('test-report.md')}")
    print(f"  脚本路径：{Workspace.get_script_path('test.py')}")
    print(f"  记忆路径：{Workspace.get_memory_path('2026-03-14.md')}")
    print(f"  人格路径：{Workspace.get_persona_path('7-PERSONA.md')}")
    print(f"  配置文件：{Workspace.get_path('MEMORY.md', is_config=True)}")
    print()
    
    # 验证路径
    print("[INFO] 路径验证:")
    test_paths = [
        r"str(Path(__file__).parent.parent)\test.md",
        r"C:\Users\华为\.copaw\MEMORY.md",
        r"C:\Users\华为\.copaw\test.md",
        r"E:\other\test.md",
    ]
    
    for path in test_paths:
        is_valid = Workspace.validate_path(path)
        status = "[OK]" if is_valid else "[ERR]"
        print(f"  {status} {path}")
    print()
    
    # 路径建议
    print("[INFO] 路径建议:")
    wrong_paths = [
        r"C:\Users\华为\.copaw\test.md",
        r"E:\other\report.md",
    ]
    
    for path in wrong_paths:
        suggested = Workspace.suggest_path(path)
        print(f"  原路径：{path}")
        print(f"  建议：{suggested}")
        print()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # 命令行使用：验证路径
        path = sys.argv[1]
        is_valid = Workspace.validate_path(path)
        if is_valid:
            print(f"[OK] 路径合法：{path}")
            sys.exit(0)
        else:
            suggested = Workspace.suggest_path(path)
            print(f"[ERR] 路径不合法：{path}")
            print(f"   建议：{suggested}")
            sys.exit(1)
    else:
        # 演示模式
        demo()

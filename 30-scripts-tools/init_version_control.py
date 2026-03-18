#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
配置版本控制初始化脚本
创建版本目录并备份当前 tools_registry.json
"""

import sys
import io
import shutil
import json
from pathlib import Path
from datetime import datetime

# Windows 编码修复
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent  # 返回到 workspace 根目录
FLOW_ARCHIVE = WORKSPACE / "flow-archive"
VERSIONS_DIR = FLOW_ARCHIVE / "tools_registry_versions"
REGISTRY_FILE = WORKSPACE / "30-scripts-tools" / "tools_registry.json"  # 正确位置

def main():
    print("=" * 60)
    print("配置版本控制初始化")
    print("=" * 60)
    
    # Step 1: 创建版本目录
    print("\n[Step 1] 创建版本目录...")
    VERSIONS_DIR.mkdir(exist_ok=True)
    print(f"  [OK] 已创建：{VERSIONS_DIR}")
    
    # Step 2: 备份当前版本
    print("\n[Step 2] 备份当前 tools_registry.json...")
    if not REGISTRY_FILE.exists():
        print(f"  [ERROR] 未找到 {REGISTRY_FILE}")
        return 1
    
    # 获取当前版本号
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        registry = json.load(f)
    current_version = registry.get('version', 'unknown')
    
    # 生成备份文件名
    today = datetime.now().strftime('%Y%m%d')
    backup_filename = f"v{current_version}-{today}.json"
    backup_path = VERSIONS_DIR / backup_filename
    
    # 执行备份
    shutil.copy2(REGISTRY_FILE, backup_path)
    print(f"  [OK] 已备份：{backup_filename}")
    print(f"       源文件：{REGISTRY_FILE}")
    print(f"       目标：{backup_path}")
    
    # Step 3: 创建版本索引
    print("\n[Step 3] 创建版本索引...")
    index_file = VERSIONS_DIR / "VERSION_INDEX.json"
    
    if index_file.exists():
        with open(index_file, 'r', encoding='utf-8') as f:
            index = json.load(f)
    else:
        index = {"versions": [], "current_version": None}
    
    # 添加新版本记录
    version_record = {
        "version": current_version,
        "filename": backup_filename,
        "created_at": datetime.now().isoformat(),
        "backup_path": str(backup_path),
        "reason": "Initial backup - configuration version control setup"
    }
    index["versions"].append(version_record)
    index["current_version"] = current_version
    
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    print(f"  [OK] 已创建版本索引：{index_file}")
    
    # Step 4: 显示当前版本列表
    print("\n[Step 4] 当前可用版本:")
    for v in index["versions"]:
        print(f"  - {v['version']} ({v['filename']}) - {v['created_at'][:10]}")
    
    print("\n" + "=" * 60)
    print("[OK] 配置版本控制初始化完成!")
    print("=" * 60)
    print("\n下一步:")
    print("  1. 在 flow_manager.py 中添加 --rollback-registry 功能")
    print("  2. 在 tool_executor.py 中添加自动版本快照")
    print("\n使用示例:")
    print("  py flow_manager.py --rollback-registry --to v1.3.0")
    print("=" * 60)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())

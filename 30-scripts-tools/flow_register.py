#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flow Register - 注册 Flow ID 到 flow_registry.json

Usage:
    py flow_register.py --flow_id 20260318-backend-crud-001 --business backend-crud --desc "Backend CRUD API"
"""

import json
import sys
import argparse
from pathlib import Path
from datetime import datetime

WORKSPACE = Path(__file__).parent.parent
FLOW_ARCHIVE = WORKSPACE / "flow-archive"
FLOW_REGISTRY = FLOW_ARCHIVE / "flow_registry.json"


def register_flow(flow_id: str, business_name: str, description: str = "") -> bool:
    """注册 Flow ID"""
    # 确保目录存在
    FLOW_ARCHIVE.mkdir(exist_ok=True)
    flow_dir = FLOW_ARCHIVE / flow_id
    flow_dir.mkdir(exist_ok=True)
    
    # 加载或创建注册表
    if FLOW_REGISTRY.exists():
        with open(FLOW_REGISTRY, 'r', encoding='utf-8') as f:
            registry = json.load(f)
    else:
        registry = {"version": "1.0.0", "flows": {}}
    
    # 注册 Flow
    registry["flows"][flow_id] = {
        "business_name": business_name,
        "description": description,
        "created_at": datetime.now().isoformat(),
        "status": "active",
        "directory": str(flow_dir.resolve()),
        "last_updated": datetime.now().isoformat()
    }
    registry["last_updated"] = datetime.now().isoformat()
    
    # 保存注册表
    with open(FLOW_REGISTRY, 'w', encoding='utf-8') as f:
        json.dump(registry, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Flow registered: {flow_id}")
    print(f"   Directory: {flow_dir}")
    return True


def main():
    parser = argparse.ArgumentParser(description='Flow Register')
    parser.add_argument('--flow_id', type=str, required=True, help='Flow ID')
    parser.add_argument('--business', type=str, required=True, help='业务名称')
    parser.add_argument('--desc', type=str, default='', help='任务描述')
    
    args = parser.parse_args()
    
    success = register_flow(args.flow_id, args.business, args.desc)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()

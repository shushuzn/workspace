#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Flow Manager - Flow ID 管理器

核心功能:
1. 生成唯一 Flow ID: {日期}-{业务}-{序号}
2. 创建隔离目录: flow-archive/{flow_id}/
3. 状态快照管理: 保存/恢复工作流状态
4. 生命周期管理: 启动→快照→归档

Usage:
    py flow_manager.py --create <business_name>     # 创建新工作流
    py flow_manager.py --snapshot <flow_id>         # 保存状态快照
    py flow_manager.py --restore <flow_id>          # 恢复状态
    py flow_manager.py --list                       # 列出所有工作流
    py flow_manager.py --archive <flow_id>          # 归档工作流

Author: Claw
Date: 2026-03-18
Version: 1.0
"""

import json
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional, List

# 工作区根目录
WORKSPACE = Path(__file__).parent.parent
FLOW_ARCHIVE = WORKSPACE / "flow-archive"
FLOW_REGISTRY = FLOW_ARCHIVE / "flow_registry.json"

# 确保 UTF-8 编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')


class FlowManager:
    """Flow ID 管理器"""
    
    def __init__(self):
        self.registry = self._load_registry()
    
    def _load_registry(self) -> Dict:
        """加载 Flow 注册表"""
        if not FLOW_REGISTRY.exists():
            return {
                "version": "1.0.0",
                "flows": {},
                "last_updated": datetime.now().isoformat()
            }
        
        with open(FLOW_REGISTRY, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_registry(self):
        """保存 Flow 注册表"""
        self.registry['last_updated'] = datetime.now().isoformat()
        
        FLOW_ARCHIVE.mkdir(parents=True, exist_ok=True)
        with open(FLOW_REGISTRY, 'w', encoding='utf-8') as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def generate_flow_id(self, business_name: str) -> str:
        """生成唯一 Flow ID: {日期}-{业务}-{序号}"""
        today = datetime.now().strftime("%Y%m%d")
        business = business_name.lower().replace(' ', '-').replace('_', '-')[:20]
        
        # 计算今日序号
        today_flows = [
            fid for fid in self.registry['flows'].keys()
            if fid.startswith(today) and business in fid
        ]
        seq_num = len(today_flows) + 1
        
        flow_id = f"{today}-{business}-{seq_num:03d}"
        return flow_id
    
    def create_flow(self, business_name: str, description: str = "") -> str:
        """创建新工作流"""
        flow_id = self.generate_flow_id(business_name)
        
        # 创建隔离目录
        flow_dir = FLOW_ARCHIVE / flow_id
        flow_dir.mkdir(parents=True, exist_ok=True)
        
        # 创建初始状态文件
        state_file = flow_dir / "state-snapshot.json"
        initial_state = {
            "flow_id": flow_id,
            "business_name": business_name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "last_snapshot": None,
            "execution_count": 0,
            "variables": {},
            "context": {}
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(initial_state, f, indent=2, ensure_ascii=False)
        
        # 创建执行日志文件
        log_file = flow_dir / "execution-log.json"
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({"flow_id": flow_id, "logs": []}, f, indent=2, ensure_ascii=False)
        
        # 注册到 Flow 注册表
        self.registry['flows'][flow_id] = {
            "business_name": business_name,
            "description": description,
            "created_at": initial_state['created_at'],
            "status": "active",
            "directory": str(flow_dir),
            "last_updated": datetime.now().isoformat()
        }
        
        self._save_registry()
        
        print(f"✅ Flow created: {flow_id}")
        print(f"   Directory: {flow_dir}")
        print(f"   State: {state_file}")
        return flow_id
    
    def snapshot(self, flow_id: str, variables: Optional[Dict] = None, context: Optional[Dict] = None) -> bool:
        """保存状态快照"""
        if flow_id not in self.registry['flows']:
            print(f"❌ Flow not found: {flow_id}")
            return False
        
        flow_dir = FLOW_ARCHIVE / flow_id
        state_file = flow_dir / "state-snapshot.json"
        
        if not state_file.exists():
            print(f"❌ State file not found: {state_file}")
            return False
        
        # 加载当前状态
        with open(state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        # 更新状态
        state['last_snapshot'] = datetime.now().isoformat()
        state['execution_count'] += 1
        
        if variables:
            state['variables'].update(variables)
        
        if context:
            state['context'].update(context)
        
        # 保存快照
        snapshot_file = flow_dir / f"snapshot-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        # 更新主状态文件
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Snapshot saved: {snapshot_file}")
        return True
    
    def restore(self, flow_id: str, snapshot_file: Optional[str] = None) -> bool:
        """恢复状态"""
        if flow_id not in self.registry['flows']:
            print(f"❌ Flow not found: {flow_id}")
            return False
        
        flow_dir = FLOW_ARCHIVE / flow_id
        
        if snapshot_file:
            snapshot_path = flow_dir / snapshot_file
        else:
            # 找最新快照
            snapshots = list(flow_dir.glob("snapshot-*.json"))
            if not snapshots:
                print(f"❌ No snapshots found for {flow_id}")
                return False
            snapshot_path = sorted(snapshots)[-1]
        
        if not snapshot_path.exists():
            print(f"❌ Snapshot not found: {snapshot_path}")
            return False
        
        # 恢复状态
        with open(snapshot_path, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        state_file = flow_dir / "state-snapshot.json"
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
        
        print(f"✅ State restored from: {snapshot_path}")
        print(f"   Variables: {len(state.get('variables', {}))} items")
        print(f"   Context: {len(state.get('context', {}))} items")
        return True
    
    def archive_flow(self, flow_id: str) -> bool:
        """归档工作流"""
        if flow_id not in self.registry['flows']:
            print(f"❌ Flow not found: {flow_id}")
            return False
        
        # 更新状态
        self.registry['flows'][flow_id]['status'] = 'archived'
        self.registry['flows'][flow_id]['archived_at'] = datetime.now().isoformat()
        
        # 更新状态文件
        flow_dir = FLOW_ARCHIVE / flow_id
        state_file = flow_dir / "state-snapshot.json"
        
        if state_file.exists():
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            state['status'] = 'archived'
            state['archived_at'] = datetime.now().isoformat()
            
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, indent=2, ensure_ascii=False)
        
        self._save_registry()
        print(f"[OK] Flow archived: {flow_id}")
        return True
    
    def list_flows(self, status_filter: Optional[str] = None):
        """列出所有工作流"""
        flows = self.registry['flows']
        
        if status_filter:
            flows = {fid: f for fid, f in flows.items() if f.get('status') == status_filter}
        
        if not flows:
            print("No flows found")
            return
        
        print(f"\n{'Flow ID':<35} {'Business':<20} {'Status':<10} {'Created':<20}")
        print("-" * 90)
        
        for flow_id, info in sorted(flows.items(), key=lambda x: x[1]['created_at'], reverse=True):
            business = info.get('business_name', 'unknown')[:18]
            status = info.get('status', 'unknown')
            created = info.get('created_at', '')[:19]
            print(f"{flow_id:<35} {business:<20} {status:<10} {created:<20}")
        
        print("-" * 90)
        print(f"Total: {len(flows)} flows")


# ============================================================================
# 配置版本控制功能 (新增)
# ============================================================================

def list_registry_versions():
    """列出所有可用的 tools_registry 版本"""
    
    versions_dir = WORKSPACE / "flow-archive" / "tools_registry_versions"
    index_file = versions_dir / "VERSION_INDEX.json"
    
    print("=" * 60)
    print("可用的 tools_registry 版本")
    print("=" * 60)
    
    if not index_file.exists():
        print("[ERROR] 版本索引不存在")
        print(f"  路径：{index_file}")
        print("\n请先运行初始化:")
        print("  py 30-scripts-tools\\init_version_control.py")
        return
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    versions = index.get('versions', [])
    current = index.get('current_version')
    
    if not versions:
        print("[INFO] 暂无备份版本")
        return
    
    print(f"\n{'版本':<15} {'文件名':<30} {'日期':<12} {'说明'}")
    print("-" * 80)
    
    for v in sorted(versions, key=lambda x: x['created_at'], reverse=True):
        version = v.get('version', 'unknown')
        filename = v.get('filename', '')[:28]
        date = v.get('created_at', '')[:10]
        reason = v.get('reason', '')[:20]
        marker = " [CURRENT]" if version == current else ""
        print(f"v{version:<14} {filename:<30} {date:<12} {reason}{marker}")
    
    print("-" * 80)
    print(f"当前版本：v{current}")
    print(f"可用版本数：{len(versions)}")
    print("\n使用示例:")
    print("  py flow_manager.py --rollback-registry --to v1.3.0")
    print("=" * 60)


def rollback_registry(target_version: str):
    """回滚 tools_registry.json 到指定版本"""
    import shutil
    
    versions_dir = WORKSPACE / "flow-archive" / "tools_registry_versions"
    index_file = versions_dir / "VERSION_INDEX.json"
    registry_file = WORKSPACE / "30-scripts-tools" / "tools_registry.json"
    
    print("=" * 60)
    print(f"回滚 tools_registry.json 到 v{target_version}")
    print("=" * 60)
    
    # 检查版本索引
    if not index_file.exists():
        print("[ERROR] 版本索引不存在")
        return 1
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index = json.load(f)
    
    # 查找目标版本
    target = None
    for v in index.get('versions', []):
        if v.get('version') == target_version:
            target = v
            break
    
    if not target:
        print(f"[ERROR] 未找到版本 v{target_version}")
        print("\n使用 --list-versions 查看可用版本")
        return 1
    
    # 备份当前版本 (回滚前的快照)
    current_version = index.get('current_version')
    if current_version:
        print(f"\n[Step 1] 备份当前版本 v{current_version}...")
        today = datetime.now().strftime('%Y%m%d')
        backup_filename = f"v{current_version}-{today}-pre-rollback.json"
        backup_path = versions_dir / backup_filename
        shutil.copy2(registry_file, backup_path)
        print(f"  [OK] 已备份：{backup_filename}")
        
        # 添加到版本索引
        rollback_record = {
            "version": current_version,
            "filename": backup_filename,
            "created_at": datetime.now().isoformat(),
            "backup_path": str(backup_path),
            "reason": f"Pre-rollback backup before restoring to v{target_version}"
        }
        index["versions"].append(rollback_record)
    
    # 执行回滚
    print(f"\n[Step 2] 恢复 v{target_version}...")
    source_file = versions_dir / target['filename']
    
    if not source_file.exists():
        print(f"[ERROR] 版本文件不存在：{source_file}")
        return 1
    
    shutil.copy2(source_file, registry_file)
    print(f"  [OK] 已恢复：{target['filename']}")
    
    # 更新版本索引
    index["current_version"] = target_version
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index, f, indent=2, ensure_ascii=False)
    
    print(f"\n[Step 3] 更新版本索引...")
    print(f"  [OK] 当前版本：v{target_version}")
    
    # 验证回滚
    print(f"\n[Step 4] 验证回滚...")
    with open(registry_file, 'r', encoding='utf-8') as f:
        restored = json.load(f)
    restored_version = restored.get('version', 'unknown')
    
    if restored_version == target_version:
        print(f"  [OK] 验证通过 - 当前版本 v{restored_version}")
    else:
        print(f"  [WARN] 版本不匹配 - 期望 v{target_version}, 实际 v{restored_version}")
    
    print("\n" + "=" * 60)
    print(f"[OK] 回滚完成!")
    print(f"  从 v{current_version} 回滚到 v{target_version}")
    print("=" * 60)
    
    return 0


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Flow Manager - Flow ID 管理器")
    parser.add_argument('--create', type=str, metavar='BUSINESS', help='创建新工作流')
    parser.add_argument('--description', type=str, default='', help='工作流描述')
    parser.add_argument('--snapshot', type=str, metavar='FLOW_ID', help='保存状态快照')
    parser.add_argument('--restore', type=str, metavar='FLOW_ID', help='恢复状态')
    parser.add_argument('--archive', type=str, metavar='FLOW_ID', help='归档工作流')
    parser.add_argument('--list', action='store_true', help='列出所有工作流')
    parser.add_argument('--status', type=str, choices=['active', 'archived'], help='状态过滤')
    parser.add_argument('--variables', type=str, help='变量 (JSON 格式)')
    parser.add_argument('--context', type=str, help='上下文 (JSON 格式)')
    
    # 新增：配置版本控制功能
    parser.add_argument('--rollback-registry', action='store_true', help='回滚 tools_registry.json 到指定版本')
    parser.add_argument('--to', type=str, metavar='VERSION', help='目标版本号 (如 v1.3.0)')
    parser.add_argument('--list-versions', action='store_true', help='列出所有可用版本')
    
    args = parser.parse_args()
    
    manager = FlowManager()
    
    if args.create:
        flow_id = manager.create_flow(args.create, args.description)
        print(f"\n[INFO] 启动指令模板:")
        print(f"Flow ID: {flow_id}")
        print(f"任务目标：{args.description or '[填写具体需求]'}")
        print(f"隔离铁则：所有操作、文件、变量、日志，全部绑定本 Flow ID")
        print(f"闭环规则：完成后自动触发 auto-critic_v7.py --flow_id {flow_id}")
    
    elif args.snapshot:
        variables = json.loads(args.variables) if args.variables else None
        context = json.loads(args.context) if args.context else None
        manager.snapshot(args.snapshot, variables, context)
    
    elif args.restore:
        manager.restore(args.restore)
    
    elif args.archive:
        manager.archive_flow(args.archive)
    
    elif args.list:
        manager.list_flows(args.status)
    
    # 新增：配置版本控制功能
    elif args.list_versions:
        list_registry_versions()
    
    elif args.rollback_registry:
        if not args.to:
            print("[ERROR] 必须指定目标版本 --to <VERSION>")
            print("使用 --list-versions 查看可用版本")
            sys.exit(1)
        rollback_registry(args.to)
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rollback Manager - 回滚管理器

管理工作流失败时的回滚操作
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"
ROLLBACK_DIR = "cache\\rollbacks"
CHECKPOINT_FILE = "flow-archive/20260318-universal-workflow-001/checkpoint.json"

class RollbackManager:
    """回滚管理器"""
    
    def __init__(self):
        self.rollback_dir = os.path.join(WORKSPACE, ROLLBACK_DIR)
        os.makedirs(self.rollback_dir, exist_ok=True)
    
    def create_checkpoint(self, name="auto"):
        """创建检查点"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        checkpoint_name = f"{name}_{timestamp}"
        
        checkpoint_data = {
            "name": checkpoint_name,
            "created_at": datetime.now().isoformat(),
            "files": {},
            "workflow_state": None
        }
        
        # 保存关键文件
        files_to_backup = [
            CHECKPOINT_FILE,
            "30-scripts-tools/tools_registry.json",
            "flow-archive/20260318-universal-workflow-001/workflow.json"
        ]
        
        backup_dir = os.path.join(self.rollback_dir, checkpoint_name)
        os.makedirs(backup_dir, exist_ok=True)
        
        for file_path in files_to_backup:
            full_path = os.path.join(WORKSPACE, file_path)
            if os.path.exists(full_path):
                # 复制文件
                backup_path = os.path.join(backup_dir, os.path.basename(file_path))
                shutil.copy2(full_path, backup_path)
                
                checkpoint_data["files"][file_path] = backup_path
        
        # 保存工作流状态
        if os.path.exists(os.path.join(WORKSPACE, CHECKPOINT_FILE)):
            with open(os.path.join(WORKSPACE, CHECKPOINT_FILE), 'r', encoding='utf-8') as f:
                checkpoint_data["workflow_state"] = json.load(f)
        
        # 保存检查点元数据
        meta_path = os.path.join(backup_dir, "checkpoint_meta.json")
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(checkpoint_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 创建检查点：{checkpoint_name}")
        return checkpoint_name
    
    def list_checkpoints(self):
        """列出所有检查点"""
        checkpoints = []
        
        try:
            for name in os.listdir(self.rollback_dir):
                checkpoint_path = os.path.join(self.rollback_dir, name)
                if os.path.isdir(checkpoint_path):
                    meta_file = os.path.join(checkpoint_path, "checkpoint_meta.json")
                    if os.path.exists(meta_file):
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                        checkpoints.append(meta)
        except Exception as e:
            print(f"列出检查点失败：{e}")
        
        return sorted(checkpoints, key=lambda x: x.get('created_at', ''), reverse=True)
    
    def rollback(self, checkpoint_name):
        """回滚到指定检查点"""
        checkpoint_path = os.path.join(self.rollback_dir, checkpoint_name)
        
        if not os.path.exists(checkpoint_path):
            print(f"❌ 检查点不存在：{checkpoint_name}")
            return False
        
        meta_file = os.path.join(checkpoint_path, "checkpoint_meta.json")
        if not os.path.exists(meta_file):
            print(f"❌ 检查点元数据丢失：{checkpoint_name}")
            return False
        
        with open(meta_file, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        
        print(f"🔄 开始回滚到：{checkpoint_name}")
        
        # 恢复文件
        for original_path, backup_path in checkpoint_data.get("files", {}).items():
            if os.path.exists(backup_path):
                full_original = os.path.join(WORKSPACE, original_path)
                os.makedirs(os.path.dirname(full_original), exist_ok=True)
                shutil.copy2(backup_path, full_original)
                print(f"  ✅ 恢复：{original_path}")
        
        # 恢复工作流状态
        if checkpoint_data.get("workflow_state"):
            checkpoint_path = os.path.join(WORKSPACE, CHECKPOINT_FILE)
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint_data["workflow_state"], f, indent=2, ensure_ascii=False)
            print(f"  ✅ 恢复工作流状态")
        
        print(f"✅ 回滚完成：{checkpoint_name}")
        return True
    
    def cleanup_old_checkpoints(self, keep_days=7):
        """清理旧检查点"""
        deleted = []
        cutoff = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        try:
            for name in os.listdir(self.rollback_dir):
                checkpoint_path = os.path.join(self.rollback_dir, name)
                if os.path.isdir(checkpoint_path):
                    meta_file = os.path.join(checkpoint_path, "checkpoint_meta.json")
                    if os.path.exists(meta_file):
                        with open(meta_file, 'r', encoding='utf-8') as f:
                            meta = json.load(f)
                        
                        created_at = datetime.fromisoformat(meta.get('created_at', '')).timestamp()
                        if created_at < cutoff:
                            shutil.rmtree(checkpoint_path)
                            deleted.append(name)
        except Exception as e:
            print(f"清理检查点失败：{e}")
        
        return deleted

def generate_report(checkpoints, deleted):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""# 🔄 回滚管理器报告

**生成时间:** {timestamp}

## 检查点列表

"""
    
    if checkpoints:
        report += "| 名称 | 创建时间 | 文件数 | 状态 |\n"
        report += "|------|----------|--------|------|\n"
        
        for cp in checkpoints[:10]:
            name = cp.get('name', 'Unknown')
            created = cp.get('created_at', 'Unknown')[:19]
            file_count = len(cp.get('files', {}))
            report += f"| {name} | {created} | {file_count} | 可用 |\n"
        
        report += f"\n**总检查点数:** {len(checkpoints)}\n\n"
    else:
        report += "没有检查点。\n\n"
    
    report += f"""## 清理结果

"""
    
    if deleted:
        report += f"已删除 {len(deleted)} 个旧检查点:\n\n"
        for name in deleted:
            report += f"- {name}\n"
        report += "\n"
    else:
        report += "没有需要清理的检查点。\n\n"
    
    report += """## 使用说明

### 创建检查点
```bash
py rollback_manager.py --create [name]
```

### 列出检查点
```bash
py rollback_manager.py --list
```

### 回滚
```bash
py rollback_manager.py --rollback <checkpoint_name>
```

### 清理旧检查点
```bash
py rollback_manager.py --cleanup --days 7
```

---

*本报告由 rollback_manager.py 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("Rollback Manager v1.0 - 回滚管理器")
    print("=" * 60)
    
    manager = RollbackManager()
    
    # 创建检查点
    print(f"\n[1/4] 创建检查点...")
    checkpoint_name = manager.create_checkpoint("medium_priority_fix")
    
    # 列出检查点
    print(f"\n[2/4] 列出检查点...")
    checkpoints = manager.list_checkpoints()
    print(f"✅ 找到 {len(checkpoints)} 个检查点")
    
    for cp in checkpoints[:5]:
        print(f"  - {cp.get('name', 'Unknown')} ({cp.get('created_at', '')[:19]})")
    
    # 清理旧检查点
    print(f"\n[3/4] 清理旧检查点 (>7 天)...")
    deleted = manager.cleanup_old_checkpoints(keep_days=7)
    print(f"✅ 删除了 {len(deleted)} 个旧检查点")
    
    # 生成报告
    print(f"\n[4/4] 生成报告...")
    report = generate_report(checkpoints, deleted)
    
    # 保存报告
    report_dir = os.path.join(WORKSPACE, "21-reports")
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"rollback_{timestamp}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存：{report_path}")
    
    print("\n" + "=" * 60)
    print("✅ 回滚管理器就绪!")
    print("=" * 60)

if __name__ == '__main__':
    main()

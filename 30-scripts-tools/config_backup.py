#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Config Backup - 配置备份

自动备份关键配置文件
"""

import os
import json
import shutil
from datetime import datetime
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"
BACKUP_DIR = "99-backups\\configs"

# 关键配置文件
CRITICAL_CONFIGS = [
    "30-scripts-tools/tools_registry.json",
    "flow-archive/20260318-universal-workflow-001/workflow.json",
    "13-memory/memory-db.json",
    "cache/cache-config.json",
    "proactive/proactive-config.json",
    "multimodal/multimodal-config.json"
]

class ConfigBackup:
    """配置备份"""
    
    def __init__(self):
        self.backup_dir = os.path.join(WORKSPACE, BACKUP_DIR)
        os.makedirs(self.backup_dir, exist_ok=True)
    
    def backup_config(self, config_path):
        """备份单个配置"""
        full_path = os.path.join(WORKSPACE, config_path)
        
        if not os.path.exists(full_path):
            return {"status": "skip", "reason": "file_not_found", "file": config_path}
        
        # 创建带时间戳的备份
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        config_name = os.path.basename(config_path)
        backup_name = f"{config_name.replace('.json', '')}_{timestamp}.json"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # 确保目录存在
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        # 复制文件
        shutil.copy2(full_path, backup_path)
        
        # 计算大小
        size = os.path.getsize(backup_path)
        
        return {
            "status": "success",
            "file": config_path,
            "backup": backup_path,
            "size": size,
            "size_kb": size / 1024
        }
    
    def backup_all(self):
        """备份所有配置"""
        results = []
        
        for config in CRITICAL_CONFIGS:
            result = self.backup_config(config)
            results.append(result)
        
        return results
    
    def list_backups(self):
        """列出所有备份"""
        backups = []
        
        try:
            for file in os.listdir(self.backup_dir):
                if file.endswith('.json'):
                    file_path = os.path.join(self.backup_dir, file)
                    stat = os.stat(file_path)
                    backups.append({
                        "name": file,
                        "path": file_path,
                        "size": stat.st_size,
                        "size_kb": stat.st_size / 1024,
                        "created": datetime.fromtimestamp(stat.st_ctime).isoformat()
                    })
        except Exception as e:
            print(f"列出备份失败：{e}")
        
        return sorted(backups, key=lambda x: x['created'], reverse=True)
    
    def cleanup_old_backups(self, keep_days=7, keep_count=5):
        """清理旧备份"""
        deleted = []
        cutoff = datetime.now().timestamp() - (keep_days * 24 * 60 * 60)
        
        try:
            # 按配置文件分组
            config_backups = {}
            
            for file in os.listdir(self.backup_dir):
                if file.endswith('.json'):
                    # 提取配置名 (去掉时间戳)
                    parts = file.rsplit('_', 1)
                    if len(parts) == 2:
                        config_name = parts[0]
                        if config_name not in config_backups:
                            config_backups[config_name] = []
                        
                        file_path = os.path.join(self.backup_dir, file)
                        stat = os.stat(file_path)
                        config_backups[config_name].append({
                            "name": file,
                            "path": file_path,
                            "created": stat.st_ctime
                        })
            
            # 清理每个配置的旧备份
            for config_name, backups in config_backups.items():
                backups = sorted(backups, key=lambda x: x['created'], reverse=True)
                
                # 保留最近的 keep_count 个
                for backup in backups[keep_count:]:
                    age_days = (datetime.now().timestamp() - backup['created']) / (24 * 60 * 60)
                    if age_days > keep_days:
                        os.remove(backup['path'])
                        deleted.append(backup['name'])
        
        except Exception as e:
            print(f"清理备份失败：{e}")
        
        return deleted
    
    def restore_config(self, backup_name):
        """恢复配置"""
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        if not os.path.exists(backup_path):
            return {"status": "error", "message": "备份文件不存在"}
        
        # 解析原始配置名
        parts = backup_name.rsplit('_', 1)
        if len(parts) != 2:
            return {"status": "error", "message": "无效的备份文件名"}
        
        original_name = parts[0] + '.json'
        
        # 查找原始配置路径
        original_path = None
        for config in CRITICAL_CONFIGS:
            if os.path.basename(config) == original_name:
                original_path = os.path.join(WORKSPACE, config)
                break
        
        if not original_path:
            return {"status": "error", "message": "找不到原始配置路径"}
        
        # 恢复
        shutil.copy2(backup_path, original_path)
        
        return {
            "status": "success",
            "backup": backup_name,
            "restored_to": original_path
        }

def generate_report(results, deleted):
    """生成报告"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""# 💾 配置备份报告

**生成时间:** {timestamp}

## 备份结果

"""
    
    success = [r for r in results if r['status'] == 'success']
    skipped = [r for r in results if r['status'] == 'skip']
    
    if success:
        report += "| 配置文件 | 备份文件 | 大小 | 状态 |\n"
        report += "|----------|----------|------|------|\n"
        
        total_size = 0
        for result in success:
            backup_name = os.path.basename(result['backup'])
            size_kb = result.get('size_kb', 0)
            total_size += size_kb
            report += f"| {result['file']} | {backup_name} | {size_kb:.1f}KB | ✅ |\n"
        
        report += f"\n**总备份数:** {len(success)}\n"
        report += f"**总大小:** {total_size:.1f}KB\n\n"
    
    if skipped:
        report += "### 跳过的文件\n\n"
        for result in skipped:
            report += f"- {result['file']}: {result.get('reason', 'unknown')}\n"
        report += "\n"
    
    report += f"""## 清理结果

"""
    
    if deleted:
        report += f"已删除 {len(deleted)} 个旧备份:\n\n"
        for name in deleted:
            report += f"- {name}\n"
        report += "\n"
    else:
        report += "没有需要清理的备份。\n\n"
    
    report += """## 使用说明

### 备份所有配置
```bash
py config_backup.py --backup-all
```

### 列出备份
```bash
py config_backup.py --list
```

### 恢复配置
```bash
py config_backup.py --restore <backup_name>
```

### 清理旧备份
```bash
py config_backup.py --cleanup --days 7 --keep 5
```

---

*本报告由 config_backup.py 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("Config Backup v1.0 - 配置备份")
    print("=" * 60)
    
    backup = ConfigBackup()
    
    # 备份所有配置
    print(f"\n[1/4] 备份关键配置...")
    results = backup.backup_all()
    
    success = sum(1 for r in results if r['status'] == 'success')
    skipped = sum(1 for r in results if r['status'] == 'skip')
    print(f"✅ 成功：{success}, 跳过：{skipped}")
    
    # 列出备份
    print(f"\n[2/4] 列出备份...")
    backups = backup.list_backups()
    print(f"✅ 找到 {len(backups)} 个备份")
    
    # 清理旧备份
    print(f"\n[3/4] 清理旧备份 (>7 天，保留 5 个)...")
    deleted = backup.cleanup_old_backups(keep_days=7, keep_count=5)
    print(f"✅ 删除了 {len(deleted)} 个旧备份")
    
    # 生成报告
    print(f"\n[4/4] 生成报告...")
    report = generate_report(results, deleted)
    
    # 保存报告
    report_dir = os.path.join(WORKSPACE, "21-reports")
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"config_backup_{timestamp}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存：{report_path}")
    
    print("\n" + "=" * 60)
    print("✅ 配置备份完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()

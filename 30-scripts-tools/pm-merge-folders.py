#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P0 级别重复文件夹合并脚本 v2
使用 copytree + rmtree 方法，更稳健
"""

import os
import sys
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict

# UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class FolderMerger:
    """文件夹合并工具 v2"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.backup_dir = self.workspace / "agent-pm" / "backups" / datetime.now().strftime("%Y%m%d_%H%M%S")
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.stats = {
            "folders_merged": 0,
            "files_moved": 0,
            "bytes_moved": 0,
            "folders_deleted": 0,
            "errors": 0,
            "skipped": 0
        }
    
    def count_files(self, folder: Path) -> tuple:
        """统计文件数和大小"""
        if not folder.exists():
            return 0, 0
        
        file_count = 0
        total_size = 0
        
        for item in folder.rglob('*'):
            if item.is_file():
                file_count += 1
                total_size += item.stat().st_size
        
        return file_count, total_size
    
    def merge_folders(self, keep: str, merge: str) -> Dict:
        """合并两个文件夹（v2 方法）"""
        keep_path = self.workspace / keep
        merge_path = self.workspace / merge
        
        result = {
            "action": "MERGE",
            "keep": str(keep_path),
            "merge": str(merge_path),
            "status": "pending",
            "files_counted": 0,
            "bytes_counted": 0,
            "errors": []
        }
        
        # 检查源文件夹是否存在
        if not merge_path.exists():
            result["status"] = "skipped"
            result["errors"].append(f"源文件夹不存在：{merge_path}")
            self.stats["skipped"] += 1
            return result
        
        # 统计源文件
        file_count, total_size = self.count_files(merge_path)
        result["files_counted"] = file_count
        result["bytes_counted"] = total_size
        
        print(f"  📊 源文件夹统计：{file_count} 个文件 ({total_size/1024/1024:.2f}MB)")
        
        # 如果源文件夹为空，直接删除
        if file_count == 0:
            print(f"  🗑️  空文件夹，直接删除")
            try:
                shutil.rmtree(merge_path)
                result["status"] = "completed"
                self.stats["folders_deleted"] += 1
                self.stats["folders_merged"] += 1
            except Exception as e:
                result["status"] = "error"
                result["errors"].append(str(e))
                self.stats["errors"] += 1
            return result
        
        # 备份源文件夹
        backup_path = self.backup_dir / merge_path.name.replace('\\', '_').replace('/', '_')
        print(f"  📦 备份：{merge_path.name} → {backup_path.name}")
        try:
            shutil.copytree(merge_path, backup_path, dirs_exist_ok=True)
        except Exception as e:
            result["errors"].append(f"备份失败：{e}")
        
        # 确保目标文件夹存在
        if not keep_path.exists():
            print(f"  📁 创建目标文件夹：{keep_path}")
            keep_path.mkdir(parents=True, exist_ok=True)
        
        # 方法：逐个文件复制，然后删除源文件夹
        print(f"  📦 复制文件到目标文件夹...")
        files_copied = 0
        
        try:
            for item in merge_path.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(merge_path)
                    target_path = keep_path / rel_path
                    
                    # 确保目标目录存在
                    target_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 如果目标文件已存在，添加后缀
                    if target_path.exists():
                        stem = target_path.stem
                        suffix = target_path.suffix
                        target_path = target_path.with_name(f"{stem}_from_{merge_path.name}{suffix}")
                    
                    # 复制文件
                    shutil.copy2(str(item), str(target_path))
                    files_copied += 1
            
            print(f"  ✅ 复制完成：{files_copied} 个文件")
            
            # 删除源文件夹
            print(f"  🗑️  删除源文件夹：{merge_path}")
            shutil.rmtree(merge_path)
            
            result["status"] = "completed"
            result["files_moved"] = files_copied
            self.stats["folders_merged"] += 1
            self.stats["folders_deleted"] += 1
            self.stats["files_moved"] += files_copied
            self.stats["bytes_moved"] += total_size
            
        except Exception as e:
            result["status"] = "error"
            result["errors"].append(str(e))
            self.stats["errors"] += 1
            print(f"  ❌ 错误：{e}")
        
        return result
    
    def execute_p0_merges(self):
        """执行 P0 级别合并（100% 重复）"""
        print("=" * 80)
        print("🔧 P0 级别文件夹合并（100% 重复）")
        print("=" * 80)
        print()
        
        # P0 合并列表（100% 重复）
        p0_merges = [
            ("08-collectors", "40-collectors"),
            ("10-data", "data"),
            ("32-workflows", "40-workflows"),
            ("32-workflows", "workflows"),
            ("50-cache", "cache"),
            ("logs", "91-logs"),
            ("dashboard-data", "dashboard-tasks"),
            ("memory", "13-memory"),
        ]
        
        print(f"📋 合并计划：{len(p0_merges)} 对")
        print(f"📦 备份位置：{self.backup_dir}")
        print()
        
        results = []
        
        for i, (keep, merge) in enumerate(p0_merges, 1):
            print(f"\n[{i}/{len(p0_merges)}] 合并：{merge} → {keep}")
            print("-" * 80)
            
            result = self.merge_folders(keep, merge)
            results.append(result)
            
            if result["status"] == "completed":
                if result.get("files_counted", 0) > 0:
                    print(f"  ✅ 完成！复制 {result.get('files_moved', 0)} 个文件")
                else:
                    print(f"  ✅ 完成！（空文件夹已删除）")
            elif result["status"] == "skipped":
                print(f"  ⚠️  跳过：{result['errors'][0]}")
            else:
                print(f"  ❌ 错误：{result['errors']}")
        
        # 保存操作日志
        self.save_log(results, "p0")
        
        # 打印统计
        self.print_stats()
        
        return results
    
    def execute_p1_merges(self):
        """执行 P1 级别合并（80% 重复 - 双语文件夹）"""
        print("=" * 80)
        print("🔧 P1 级别文件夹合并（80% 重复 - 双语文件夹）")
        print("=" * 80)
        print()
        
        # P1 合并列表（80% 重复 - 优先保留英文命名）
        p1_merges = [
            # 配置类
            ("00-config", "00-09-core-config"),
            ("00-config", "03-config-files"),
            ("00-config", "03-config-配置文件"),
            ("01-obsidian-config", "00-config"),
            
            # 文档类
            ("15-docs", "00-root-docs"),
            ("04-plugins", "31-skills-plugins"),
            
            # 模板/研究/知识
            ("05-templates", "05-templates-模板"),
            ("06-research", "06-research-研究"),
            ("07-knowledge", "07-knowledge-知识"),
            ("07-knowledge", "60-knowledge-cards"),
            
            # 收集/创作/数据
            ("08-collectors", "08-collectors-收集"),
            ("09-creation", "09-creation-创作"),
            ("10-data", "10-data-数据"),
            ("10-data", "20-data-reports"),
            ("10-data", "dashboard-data"),
            
            # 记忆/笔记
            ("memory", "13-memory-system"),
            ("memory", "13-memory-记忆系统"),
            ("14-notes", "14-notes-笔记"),
            
            # 文档规范
            ("15-docs-standard", "15-docs-文档规范"),
            
            # 脚本工具
            ("30-scripts-tools", "30-scripts-脚本工具"),
            
            # 技能插件
            ("31-skills-plugins", "31-skills-技能插件"),
            
            # 工作流
            ("32-workflows", "32-workflows-工作流"),
            
            # 仪表板
            ("33-dashboard", "33-dashboard-仪表板"),
            
            # 人格系统
            ("00-persona-system", "00-人格系统"),
            
            # OpenClaw 系统
            ("02-openclaw-system", "02-openclaw-系统配置"),
            
            # 项目
            ("50-projects-项目", "projects"),
            
            # 网页
            ("51-web", "51-web-网页"),
            
            # 测试
            ("92-tests", "92-tests-测试"),
            
            # 归档
            ("99-archive-归档", "99-archive-old"),
            ("99-archive-归档", "99-archive"),
            
            # 日志
            ("logs", "91-logs-日志"),
        ]
        
        print(f"📋 合并计划：{len(p1_merges)} 对")
        print(f"📦 备份位置：{self.backup_dir}")
        print()
        print("⚠️  警告：P1 合并涉及大量文件，请确认已备份重要数据！")
        print()
        
        results = []
        
        for i, (keep, merge) in enumerate(p1_merges, 1):
            print(f"\n[{i}/{len(p1_merges)}] 合并：{merge} → {keep}")
            print("-" * 80)
            
            result = self.merge_folders(keep, merge)
            results.append(result)
            
            if result["status"] == "completed":
                if result.get("files_counted", 0) > 0:
                    print(f"  ✅ 完成！复制 {result.get('files_moved', 0)} 个文件 ({result.get('bytes_counted', 0)/1024/1024:.2f}MB)")
                else:
                    print(f"  ✅ 完成！（空文件夹已删除）")
            elif result["status"] == "skipped":
                print(f"  ⚠️  跳过：{result['errors'][0]}")
            else:
                print(f"  ❌ 错误：{result['errors']}")
        
        # 保存操作日志
        self.save_log(results, "p1")
        
        # 打印统计
        self.print_stats()
        
        return results
    
    def save_log(self, results: List[Dict], level: str = "p0"):
        """保存操作日志"""
        log_file = self.backup_dir / f"merge-log-{level}.json"
        
        log = {
            "timestamp": datetime.now().isoformat(),
            "backup_location": str(self.backup_dir),
            "operations": results,
            "stats": self.stats
        }
        
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
        
        print(f"\n📝 操作日志已保存：{log_file}")
    
    def print_stats(self):
        """打印统计信息"""
        print()
        print("=" * 80)
        print("📊 合并统计")
        print("=" * 80)
        print(f"✅ 成功合并：{self.stats['folders_merged']} 个")
        print(f"📦 移动文件：{self.stats['files_moved']} 个")
        print(f"💾 移动数据：{self.stats['bytes_moved']/(1024*1024):.2f}MB")
        print(f"🗑️  删除文件夹：{self.stats['folders_deleted']} 个")
        print(f"⚠️  跳过：{self.stats['skipped']} 个")
        print(f"❌ 错误：{self.stats['errors']} 个")
        print(f"💾 备份位置：{self.backup_dir}")
        print("=" * 80)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="文件夹合并工具")
    parser.add_argument("--workspace", default="D:\\OpenClaw\\workspace",
                       help="工作区路径")
    parser.add_argument("--level", default="p1", choices=["p0", "p1", "all"],
                       help="合并级别：p0（100% 重复）, p1（80% 重复）, all（全部）")
    parser.add_argument("--dry-run", action="store_true",
                       help="仅模拟，不实际执行")
    parser.add_argument("--confirm", action="store_true",
                       help="自动确认执行")
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("⚠️  警告：此操作将合并重复文件夹")
    print("=" * 80)
    print()
    
    if args.level == "p0":
        print("P0 合并列表（100% 重复）：")
        print("  1. 08-collectors + 40-collectors → 08-collectors")
        print("  2. 10-data + data → 10-data")
        print("  3. 32-workflows + 40-workflows → 32-workflows")
        print("  4. 32-workflows + workflows → 32-workflows")
        print("  5. 50-cache + cache → 50-cache")
        print("  6. logs + 91-logs → logs")
        print("  7. dashboard-data + dashboard-tasks → dashboard-data")
        print("  8. memory + 13-memory → memory")
    elif args.level == "p1":
        print("P1 合并列表（80% 重复 - 双语文件夹）：")
        print("  - 00-config + 03-config-* → 00-config")
        print("  - 06-research + 06-research-研究 → 06-research")
        print("  - 30-scripts-tools + 30-scripts-脚本工具 → 30-scripts-tools")
        print("  - ... (共 37 对)")
    else:
        print("合并全部级别（P0 + P1）")
    
    print()
    print("所有源文件夹将被备份到：agent-pm/backups/")
    print()
    
    if not args.confirm and not args.dry_run:
        response = input("确认执行？(yes/no): ")
        if response.lower() != 'yes':
            print("❌ 已取消")
            return
    else:
        print("✅ 自动确认执行")
        print()
    
    if args.dry_run:
        print("🔍 干运行模式 - 不实际执行")
        return
    
    merger = FolderMerger(args.workspace)
    
    if args.level == "p0":
        merger.execute_p0_merges()
    elif args.level == "p1":
        merger.execute_p1_merges()
    else:
        merger.execute_p0_merges()
        print("\n" + "=" * 80 + "\n")
        merger.execute_p1_merges()


if __name__ == "__main__":
    main()

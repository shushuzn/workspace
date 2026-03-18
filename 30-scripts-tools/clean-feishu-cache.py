#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Feishu Cache Cleaner - 飞书缓存清理工具

功能:
- 扫描飞书缓存位置
- 计算缓存大小
- 安全清理缓存
- 生成清理报告

使用:
    py clean-feishu-cache.py --scan     # 扫描缓存
    py clean-feishu-cache.py --clean    # 清理缓存
    py clean-feishu-cache.py --report   # 生成报告
"""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

class FeishuCacheCleaner:
    def __init__(self):
        self.user = os.getenv('USERNAME', 'User')
        self.base_paths = [
            Path(rf"C:\Users\{self.user}\AppData\Roaming\Lark"),
            Path(rf"C:\Users\{self.user}\AppData\Local\Lark"),
            Path(rf"C:\Users\{self.user}\AppData\Roaming\feishu"),
            Path(rf"C:\Users\{self.user}\AppData\Local\feishu"),
        ]
        self.cache_dirs = ['Cache', 'Caches', 'cache']
        self.log_dirs = ['logs', 'log', 'Logs']
        self.temp_dirs = ['Temp', 'tmp', 'temp']
        
    def get_size(self, path):
        """计算目录大小"""
        total = 0
        try:
            for entry in path.rglob('*'):
                if entry.is_file():
                    total += entry.stat().st_size
        except Exception as e:
            pass
        return total
    
    def format_size(self, size_bytes):
        """格式化大小显示"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.2f} TB"
    
    def scan(self):
        """扫描飞书缓存"""
        print("\n" + "="*70)
        print("  飞书 (Feishu/Lark) 缓存扫描")
        print("="*70)
        
        total_size = 0
        found_paths = []
        
        for base_path in self.base_paths:
            if base_path.exists():
                size = self.get_size(base_path)
                total_size += size
                found_paths.append((base_path, size))
                
                print(f"\n[FOUND] {base_path}")
                print(f"        Size: {self.format_size(size)}")
                
                # 扫描子目录
                for subdir in ['Cache', 'logs', 'Temp']:
                    subpath = base_path / subdir
                    if subpath.exists():
                        subsize = self.get_size(subpath)
                        if subsize > 0:
                            print(f"    - {subdir}/: {self.format_size(subsize)}")
        
        if not found_paths:
            print("\n[INFO] 未找到飞书缓存目录")
            print("可能的位置:")
            print("  - C:\\Users\\<用户名>\\AppData\\Roaming\\Lark")
            print("  - C:\\Users\\<用户名>\\AppData\\Local\\Lark")
        else:
            print(f"\n{'='*70}")
            print(f"  总缓存大小：{self.format_size(total_size)}")
            print(f"  找到 {len(found_paths)} 个目录")
            print("="*70)
        
        return found_paths, total_size
    
    def clean(self, dry_run=True):
        """清理缓存"""
        print("\n" + "="*70)
        print("  飞书缓存清理")
        print("="*70)
        
        if dry_run:
            print("\n[DRY RUN] 模拟清理模式 (不会实际删除)")
            print("使用 --clean 执行实际清理\n")
        
        cleaned_size = 0
        cleaned_files = 0
        
        for base_path in self.base_paths:
            if not base_path.exists():
                continue
            
            # 清理 Cache 目录
            for cache_dir in self.cache_dirs:
                cache_path = base_path / cache_dir
                if cache_path.exists():
                    try:
                        size = self.get_size(cache_path)
                        if not dry_run:
                            shutil.rmtree(cache_path)
                        cleaned_size += size
                        cleaned_files += 1
                        action = "[CLEANED]" if not dry_run else "[WOULD CLEAN]"
                        print(f"{action} {cache_path} ({self.format_size(size)})")
                    except Exception as e:
                        print(f"[ERROR] {cache_path}: {e}")
            
            # 清理日志 (保留最近 7 天)
            for log_dir in self.log_dirs:
                log_path = base_path / log_dir
                if log_path.exists():
                    try:
                        for log_file in log_path.rglob('*.log'):
                            try:
                                mtime = datetime.fromtimestamp(log_file.stat().st_mtime)
                                age_days = (datetime.now() - mtime).days
                                if age_days > 7:
                                    size = log_file.stat().st_size
                                    if not dry_run:
                                        log_file.unlink()
                                    cleaned_size += size
                                    cleaned_files += 1
                                    action = "[CLEANED]" if not dry_run else f"[WOULD CLEAN] ({age_days}天)"
                                    print(f"{action} {log_file} ({self.format_size(size)})")
                            except Exception:
                                pass
                    except Exception as e:
                        print(f"[ERROR] {log_path}: {e}")
            
            # 清理临时文件
            for temp_dir in self.temp_dirs:
                temp_path = base_path / temp_dir
                if temp_path.exists():
                    try:
                        size = self.get_size(temp_path)
                        if not dry_run:
                            shutil.rmtree(temp_path)
                        cleaned_size += size
                        cleaned_files += 1
                        action = "[CLEANED]" if not dry_run else "[WOULD CLEAN]"
                        print(f"{action} {temp_path} ({self.format_size(size)})")
                    except Exception as e:
                        print(f"[ERROR] {temp_path}: {e}")
        
        print(f"\n{'='*70}")
        if dry_run:
            print(f"  预计清理：{cleaned_files} 个文件/目录")
            print(f"  预计释放：{self.format_size(cleaned_size)}")
        else:
            print(f"  已清理：{cleaned_files} 个文件/目录")
            print(f"  已释放：{self.format_size(cleaned_size)}")
        print("="*70)
        
        return cleaned_size, cleaned_files
    
    def generate_report(self):
        """生成清理报告"""
        found_paths, total_size = self.scan()
        
        report = f"""# 飞书缓存清理报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**用户:** {self.user}

---

## 缓存概览

- **总缓存大小:** {self.format_size(total_size)}
- **找到目录数:** {len(found_paths)}

---

## 目录详情

| 路径 | 大小 |
|------|------|
"""
        for path, size in found_paths:
            report += f"| {path} | {self.format_size(size)} |\n"
        
        report += f"""
---

## 建议操作

1. **安全清理** (推荐):
   - Cache 文件夹
   - Temp 文件夹
   - 7 天前的日志文件
   
   预计释放：{self.format_size(total_size * 0.7)}

2. **完全清理** (谨慎):
   - 所有缓存文件
   
   预计释放：{self.format_size(total_size)}
   
   **注意:** 完全清理后飞书需要重新下载缓存，首次启动可能变慢

---

## 清理命令

```bash
# 扫描缓存
py clean-feishu-cache.py --scan

# 模拟清理 (不会实际删除)
py clean-feishu-cache.py --clean

# 实际清理
py clean-feishu-cache.py --clean --force
```
"""
        
        reports_dir = Path(r"D:\OpenClaw\workspace\21-reports")
        reports_dir.mkdir(parents=True, exist_ok=True)
        report_file = reports_dir / f"feishu-cache-{datetime.now().strftime('%Y%m%d')}.md"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n[OK] Report saved to: {report_file}")
        print(report)


def main():
    cleaner = FeishuCacheCleaner()
    
    if len(sys.argv) < 2:
        print(__doc__)
        cleaner.scan()
        return
    
    cmd = sys.argv[1]
    
    if cmd == "--scan" or cmd == "-s":
        cleaner.scan()
    
    elif cmd == "--clean" or cmd == "-c":
        force = "--force" in sys.argv or "-f" in sys.argv
        cleaner.clean(dry_run=not force)
    
    elif cmd == "--report" or cmd == "-r":
        cleaner.generate_report()
    
    elif cmd == "--help" or cmd == "-h":
        print(__doc__)
    
    else:
        print(f"[ERROR] Unknown command: {cmd}")
        print("Use --help for usage")


if __name__ == "__main__":
    main()

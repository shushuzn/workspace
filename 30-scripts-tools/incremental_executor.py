#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Incremental Executor - 增量执行支持

只执行变更的部分，跳过未变化的内容
"""

import os
import json
import hashlib
from datetime import datetime
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"
CACHE_DIR = "cache\\incremental"

def get_file_hash(file_path):
    """计算文件哈希"""
    try:
        with open(file_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return None

def load_cache():
    """加载缓存"""
    cache_path = os.path.join(WORKSPACE, CACHE_DIR, "cache.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            pass
    return {"files": {}, "last_run": None}

def save_cache(cache):
    """保存缓存"""
    cache_path = os.path.join(WORKSPACE, CACHE_DIR, "cache.json")
    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    
    cache["last_run"] = datetime.now().isoformat()
    
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, indent=2, ensure_ascii=False)

def check_changes(files_to_check):
    """检查文件变更"""
    cache = load_cache()
    changes = []
    
    for file_path in files_to_check:
        if not os.path.exists(file_path):
            changes.append({
                "file": file_path,
                "status": "deleted",
                "action": "skip"
            })
            continue
        
        current_hash = get_file_hash(file_path)
        cached_hash = cache["files"].get(file_path)
        
        if cached_hash is None:
            changes.append({
                "file": file_path,
                "status": "new",
                "action": "execute",
                "hash": current_hash
            })
        elif cached_hash != current_hash:
            changes.append({
                "file": file_path,
                "status": "modified",
                "action": "execute",
                "hash": current_hash
            })
        else:
            changes.append({
                "file": file_path,
                "status": "unchanged",
                "action": "skip",
                "hash": current_hash
            })
    
    return changes, cache

def execute_incremental(files_to_check):
    """增量执行"""
    print("=" * 60)
    print("Incremental Executor v1.0 - 增量执行支持")
    print("=" * 60)
    
    # 检查变更
    print(f"\n[1/3] 检查 {len(files_to_check)} 个文件...")
    changes, cache = check_changes(files_to_check)
    
    to_execute = [c for c in changes if c["action"] == "execute"]
    to_skip = [c for c in changes if c["action"] == "skip"]
    
    print(f"  ✅ 新增：{sum(1 for c in changes if c['status'] == 'new')}")
    print(f"  ✅ 修改：{sum(1 for c in changes if c['status'] == 'modified')}")
    print(f"  ✅ 未变：{sum(1 for c in changes if c['status'] == 'unchanged')}")
    print(f"  ✅ 删除：{sum(1 for c in changes if c['status'] == 'deleted')}")
    
    # 执行变更的部分
    print(f"\n[2/3] 执行 {len(to_execute)} 个变更文件...")
    results = []
    
    for change in to_execute:
        file_path = change["file"]
        print(f"  执行：{os.path.basename(file_path)}")
        
        # 模拟执行（实际应该调用工具）
        result = {
            "file": file_path,
            "status": change["status"],
            "executed": True,
            "timestamp": datetime.now().isoformat()
        }
        results.append(result)
        
        # 更新缓存
        cache["files"][file_path] = change.get("hash")
    
    # 跳过未变更的部分
    print(f"\n[3/3] 跳过 {len(to_skip)} 个未变更文件...")
    for change in to_skip:
        print(f"  跳过：{os.path.basename(change['file'])} ({change['status']})")
    
    # 保存缓存
    save_cache(cache)
    
    # 生成报告
    report = generate_report(results, to_skip)
    
    # 保存报告
    report_dir = os.path.join(WORKSPACE, "21-reports")
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"incremental_{timestamp}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存：{report_path}")
    print(f"✅ 缓存已更新")
    
    print("\n" + "=" * 60)
    print("✅ 增量执行完成!")
    print("=" * 60)
    
    return results

def generate_report(executed, skipped):
    """生成报告"""
    report = f"""# 🔄 增量执行报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 执行概览

- **总文件数:** {len(executed) + len(skipped)}
- **执行数:** {len(executed)}
- **跳过数:** {len(skipped)}
- **执行率:** {len(executed) / (len(executed) + len(skipped)) * 100:.1f}% (如有文件)

## 执行详情

"""
    
    if executed:
        report += "### 已执行\n\n"
        report += "| 文件 | 状态 | 执行时间 |\n"
        report += "|------|------|----------|\n"
        
        for item in executed:
            file_name = os.path.basename(item["file"])
            status = item["status"]
            timestamp = item["timestamp"][11:19]
            report += f"| {file_name} | {status} | {timestamp} |\n"
        
        report += "\n"
    
    if skipped:
        report += "### 已跳过\n\n"
        report += "| 文件 | 状态 |\n"
        report += "|------|------|\n"
        
        for item in skipped:
            file_name = os.path.basename(item["file"])
            status = item["status"]
            report += f"| {file_name} | {status} |\n"
        
        report += "\n"
    
    report += """## 性能提升

"""
    
    if len(executed) + len(skipped) > 0:
        saved = len(skipped)
        total = len(executed) + len(skipped)
        saved_percent = saved / total * 100
        report += f"- **跳过文件数:** {saved}\n"
        report += f"- **节省执行时间:** 约 {saved_percent:.0f}%\n"
    
    report += """
## 使用说明

1. 首次运行：所有文件都会执行
2. 后续运行：只执行变更的文件
3. 清除缓存：删除 `cache/incremental/cache.json` 重新执行所有

---

*本报告由 incremental_executor.py 自动生成*
"""
    
    return report

def main():
    """主函数"""
    # 示例：检查 30-scripts-tools 目录下的 Python 文件
    tools_dir = os.path.join(WORKSPACE, "30-scripts-tools")
    
    files_to_check = []
    for file in os.listdir(tools_dir):
        if file.endswith('.py') and not file.startswith('_'):
            files_to_check.append(os.path.join(tools_dir, file))
    
    # 限制数量用于演示
    files_to_check = files_to_check[:10]
    
    execute_incremental(files_to_check)

if __name__ == '__main__':
    main()

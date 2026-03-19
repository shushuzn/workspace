#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Memory Auto Compress - 记忆自动压缩

自动压缩过期的记忆文件
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = "D:\\OpenClaw\\workspace"
MEMORY_DIR = "13-memory"
MEMORY_DB = "13-memory\\memory-db.json"

def get_daily_notes():
    """获取所有日常笔记"""
    memory_path = os.path.join(WORKSPACE, MEMORY_DIR)
    notes = []
    
    try:
        for file in os.listdir(memory_path):
            if file.endswith('.md') and file[0].isdigit():
                file_path = os.path.join(memory_path, file)
                stat = os.stat(file_path)
                notes.append({
                    'file': file,
                    'path': file_path,
                    'size': stat.st_size,
                    'modified': datetime.fromtimestamp(stat.st_mtime),
                    'created': datetime.fromtimestamp(stat.st_ctime)
                })
    except Exception as e:
        print(f"读取日常笔记失败：{e}")
    
    return sorted(notes, key=lambda x: x['file'], reverse=True)

def compress_old_note(note, days_old=7):
    """压缩旧笔记"""
    # 检查是否超过指定天数
    age = datetime.now() - note['modified']
    if age.days < days_old:
        return None
    
    # 读取内容
    try:
        with open(note['path'], 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"读取 {note['file']} 失败：{e}")
        return None
    
    # 简单压缩：保留关键信息
    lines = content.split('\n')
    compressed_lines = []
    
    # 保留标题和关键部分
    in_important_section = False
    for line in lines:
        # 保留标题
        if line.startswith('#') or line.startswith('##'):
            compressed_lines.append(line)
            in_important_section = True
        # 保留列表项
        elif line.strip().startswith('-') or line.strip().startswith('*'):
            if in_important_section or len(compressed_lines) < 50:
                compressed_lines.append(line)
        # 保留空行分隔
        elif line.strip() == '' and compressed_lines:
            compressed_lines.append('')
        # 限制总行数
        elif len(compressed_lines) < 100:
            compressed_lines.append(line)
    
    # 生成压缩版本
    compressed_content = '\n'.join(compressed_lines[:100])
    compressed_content += f"\n\n---\n\n*原文 {len(lines)} 行，已压缩到 {len(compressed_lines)} 行 - {datetime.now().strftime('%Y-%m-%d')}*\n"
    
    # 保存压缩版本
    compressed_path = note['path'].replace('.md', '-compressed.md')
    with open(compressed_path, 'w', encoding='utf-8') as f:
        f.write(compressed_content)
    
    original_size = note['size']
    compressed_size = len(compressed_content.encode('utf-8'))
    compression_ratio = (original_size - compressed_size) / original_size * 100 if original_size > 0 else 0
    
    return {
        'original': note['file'],
        'original_size_kb': original_size / 1024,
        'compressed': os.path.basename(compressed_path),
        'compressed_size_kb': compressed_size / 1024,
        'compression_ratio': compression_ratio,
        'age_days': age.days
    }

def cleanup_old_compressed(days_old=30):
    """清理旧的压缩文件"""
    memory_path = os.path.join(WORKSPACE, MEMORY_DIR)
    deleted = []
    
    try:
        for file in os.listdir(memory_path):
            if '-compressed.md' in file:
                file_path = os.path.join(memory_path, file)
                stat = os.stat(file_path)
                age = datetime.now() - datetime.fromtimestamp(stat.st_mtime)
                
                if age.days > days_old:
                    os.remove(file_path)
                    deleted.append({
                        'file': file,
                        'age_days': age.days
                    })
    except Exception as e:
        print(f"清理失败：{e}")
    
    return deleted

def generate_report(results, deleted):
    """生成报告"""
    report = f"""# 🗜️ 记忆自动压缩报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 压缩结果

"""
    
    if not results:
        report += "没有需要压缩的记忆文件。\n\n"
    else:
        report += "| 原文件 | 原大小 | 压缩后 | 压缩率 | 文件年龄 |\n"
        report += "|--------|--------|--------|--------|----------|\n"
        
        total_original = 0
        total_compressed = 0
        
        for result in results:
            report += f"| {result['original']} | {result['original_size_kb']:.1f}KB | {result['compressed_size_kb']:.1f}KB | {result['compression_ratio']:.1f}% | {result['age_days']}天 |\n"
            total_original += result['original_size_kb']
            total_compressed += result['compressed_size_kb']
        
        overall_ratio = (total_original - total_compressed) / total_original * 100 if total_original > 0 else 0
        report += f"\n**总计:** {total_original:.1f}KB → {total_compressed:.1f}KB (压缩 {overall_ratio:.1f}%)\n"
        report += f"**压缩文件数:** {len(results)}\n\n"
    
    report += "## 清理结果\n\n"
    
    if not deleted:
        report += "没有需要清理的压缩文件。\n\n"
    else:
        report += f"已删除 {len(deleted)} 个旧的压缩文件:\n\n"
        for item in deleted:
            report += f"- {item['file']} ({item['age_days']}天)\n"
        report += "\n"
    
    report += """## 建议

- 定期运行此脚本保持记忆文件整洁
- 重要内容建议手动保存到 MEMORY.md
- 压缩文件保留 30 天后自动删除

---

*本报告由 memory_auto_compress.py 自动生成*
"""
    
    return report

def main():
    """主函数"""
    print("=" * 60)
    print("Memory Auto Compress v1.0 - 记忆自动压缩")
    print("=" * 60)
    
    # 获取日常笔记
    print("\n[1/4] 获取日常笔记...")
    notes = get_daily_notes()
    print(f"✅ 找到 {len(notes)} 个日常笔记")
    
    # 压缩旧笔记
    print("\n[2/4] 压缩旧笔记 (>7 天)...")
    results = []
    for note in notes:
        result = compress_old_note(note, days_old=7)
        if result:
            results.append(result)
            print(f"  ✅ {result['original']}: {result['compression_ratio']:.1f}% 压缩率")
    
    print(f"✅ 压缩了 {len(results)} 个文件")
    
    # 清理旧压缩文件
    print("\n[3/4] 清理旧压缩文件 (>30 天)...")
    deleted = cleanup_old_compressed(days_old=30)
    print(f"✅ 删除了 {len(deleted)} 个文件")
    
    # 生成报告
    print("\n[4/4] 生成报告...")
    report = generate_report(results, deleted)
    
    # 保存报告
    report_dir = os.path.join(WORKSPACE, "21-reports")
    os.makedirs(report_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    report_path = os.path.join(report_dir, f"memory_compress_{timestamp}.md")
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存：{report_path}")
    
    print("\n" + "=" * 60)
    print("✅ 记忆自动压缩完成!")
    print("=" * 60)

if __name__ == '__main__':
    main()

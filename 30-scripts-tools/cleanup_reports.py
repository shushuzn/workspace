#!/usr/bin/env python3
"""
🧹 报告系统清理工具

功能:
- 扫描所有报告文件
- 识别重复报告
- 标记可归档报告
- 生成清理建议
"""

import os
import re
import hashlib
from pathlib import Path
from datetime import datetime
from collections import defaultdict


def get_report_files(root_dir):
    """获取所有报告文件"""
    report_files = []
    exclude_dirs = {'.git', 'node_modules', '__pycache__', '.copaw'}
    
    for path in Path(root_dir).rglob('*REPORT*.md'):
        # 排除特定目录
        if any(exclude in str(path) for exclude in exclude_dirs):
            continue
        
        # 排除归档目录
        if '90-archive' in str(path) or '99-archive' in str(path):
            continue
        
        report_files.append(path)
    
    return report_files


def calculate_file_hash(file_path):
    """计算文件哈希值 (用于检测重复)"""
    hasher = hashlib.md5()
    try:
        with open(file_path, 'rb') as f:
            buf = f.read()
            hasher.update(buf)
        return hasher.hexdigest()
    except:
        return None


def get_file_age_days(file_path):
    """获取文件年龄 (天)"""
    mtime = os.path.getmtime(file_path)
    age = (datetime.now().timestamp() - mtime) / 86400
    return int(age)


def analyze_report(file_path):
    """分析单个报告"""
    info = {
        'path': str(file_path),
        'name': file_path.name,
        'size': file_path.stat().st_size,
        'age_days': get_file_age_days(file_path),
        'hash': calculate_file_hash(file_path),
        'type': 'unknown',
        'importance': 'medium'
    }
    
    # 判断报告类型
    name = file_path.name.upper()
    
    if 'FINAL' in name or 'COMPLETE' in name:
        info['type'] = 'completion'
        info['importance'] = 'high'
    elif 'VERIFICATION' in name or 'TEST' in name:
        info['type'] = 'verification'
    elif 'FIX' in name or 'TROUBLESHOOTING' in name:
        info['type'] = 'fix'
    elif 'INTEGRATION' in name or 'DEPLOYMENT' in name:
        info['type'] = 'integration'
    elif 'PROGRESS' in name or 'WEEKLY' in name or 'DAILY' in name:
        info['type'] = 'progress'
    elif 'SECURITY' in name:
        info['type'] = 'security'
        info['importance'] = 'high'
    
    # 判断是否可能重复
    if 'copy' in name.lower() or 'backup' in name.lower() or 'v2' in name.lower():
        info['possible_duplicate'] = True
    else:
        info['possible_duplicate'] = False
    
    # 判断是否建议归档
    if info['age_days'] > 30 and info['type'] in ['verification', 'test', 'fix']:
        info['suggest_archive'] = True
    else:
        info['suggest_archive'] = False
    
    return info


def find_duplicates(reports):
    """查找重复报告 (基于哈希)"""
    hash_map = defaultdict(list)
    
    for report in reports:
        if report['hash']:
            hash_map[report['hash']].append(report)
    
    duplicates = {h: rpts for h, rpts in hash_map.items() if len(rpts) > 1}
    
    return duplicates


def find_similar_names(reports):
    """查找相似命名的报告"""
    name_map = defaultdict(list)
    
    for report in reports:
        # 提取核心名称 (去掉日期和版本)
        name = report['name']
        name_clean = re.sub(r'[-_]?\d{8}[-_]?\d{0,6}', '', name)  # 去掉日期
        name_clean = re.sub(r'[-_]?v\d+\.?\d*', '', name_clean, flags=re.IGNORECASE)  # 去掉版本号
        name_clean = re.sub(r'[-_]?\d+', '', name_clean)  # 去掉数字
        name_clean = name_clean.replace('_', '').replace('-', '').upper()
        
        name_map[name_clean].append(report)
    
    similar = {n: rpts for n, rpts in name_map.items() if len(rpts) > 1}
    
    return similar


def generate_cleanup_report(reports, duplicates, similar):
    """生成清理报告"""
    output = []
    
    output.append("# 🧹 报告系统清理建议\n")
    output.append(f"**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M')}\n")
    output.append(f"**总报告数:** {len(reports)}\n")
    
    # 统计
    type_counts = defaultdict(int)
    importance_counts = defaultdict(int)
    archive_count = 0
    
    for r in reports:
        type_counts[r['type']] += 1
        importance_counts[r['importance']] += 1
        if r['suggest_archive']:
            archive_count += 1
    
    output.append("\n## 📊 统计概览\n")
    output.append("### 按类型分布\n")
    output.append("| 类型 | 数量 | 占比 |")
    output.append("|------|------|------|")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1]):
        pct = c / len(reports) * 100
        output.append(f"| {t} | {c} | {pct:.1f}% |")
    
    output.append("\n### 按重要性分布\n")
    output.append("| 重要性 | 数量 | 占比 |")
    output.append("|--------|------|------|")
    for imp, c in sorted(importance_counts.items(), key=lambda x: -x[1]):
        pct = c / len(reports) * 100
        output.append(f"| {imp} | {c} | {pct:.1f}% |")
    
    # 重复报告
    output.append("\n\n## ⚠️ 重复报告检测\n")
    
    if duplicates:
        output.append(f"发现 **{len(duplicates)}** 组完全重复的报告:\n")
        for i, (hash_val, dups) in enumerate(duplicates.items(), 1):
            output.append(f"\n### 重复组 {i}")
            output.append(f"**哈希:** `{hash_val[:8]}...`\n")
            output.append("**文件:**")
            for dup in dups:
                output.append(f"- `{dup['name']}` ({dup['size']} bytes)")
            output.append(f"\n**建议:** 保留 1 个，删除 {len(dups)-1} 个")
    else:
        output.append("✅ 未发现完全重复的报告\n")
    
    # 相似命名
    output.append("\n\n## 🔍 相似命名报告\n")
    
    if similar:
        output.append(f"发现 **{len(similar)}** 组相似命名的报告:\n")
        for i, (name, group) in enumerate(list(similar.items())[:10], 1):  # 只显示前 10 组
            if len(group) > 1:
                output.append(f"\n### 相似组 {i}: `{name}`")
                output.append("**文件:**")
                for rep in group:
                    output.append(f"- `{rep['name']}` (年龄：{rep['age_days']}天)")
    else:
        output.append("✅ 未发现相似命名的报告\n")
    
    # 建议归档
    output.append("\n\n## 🗄️ 建议归档的报告\n")
    output.append(f"共 **{archive_count}** 个报告建议归档 (年龄>30 天且为测试/修复类)\n")
    
    archive_reports = [r for r in reports if r['suggest_archive']]
    if archive_reports:
        output.append("\n| 文件名 | 类型 | 年龄 (天) | 大小 |")
        output.append("|--------|------|----------|------|")
        for r in sorted(archive_reports, key=lambda x: -x['age_days'])[:30]:  # 只显示前 30 个
            output.append(f"| {r['name']} | {r['type']} | {r['age_days']} | {r['size']}B |")
    
    # 重要报告
    output.append("\n\n## ⭐ 重要报告清单\n")
    important = [r for r in reports if r['importance'] == 'high']
    output.append(f"共 **{len(important)}** 个重要报告:\n")
    for r in important[:20]:
        output.append(f"- ✅ `{r['name']}` ({r['type']})")
    
    # 清理建议
    output.append("\n\n## 🎯 清理建议\n")
    output.append("### 立即执行\n")
    output.append("1. **删除完全重复的报告** - 可节省空间")
    output.append("2. **归档旧测试报告** - 移动到 90-archive/")
    output.append("3. **合并相似报告** - 整合内容相似的报告\n")
    
    output.append("### 建议执行\n")
    output.append("1. **统一命名规范** - 使用标准模板")
    output.append("2. **添加报告索引** - 便于查找")
    output.append("3. **定期清理** - 每季度一次\n")
    
    # 命令
    output.append("\n\n## 🛠️ 清理命令\n")
    output.append("```bash\n")
    output.append("# 1. 查看重复报告\n")
    output.append("python cleanup_reports.py --show-duplicates\n\n")
    output.append("# 2. 归档旧报告\n")
    output.append("python cleanup_reports.py --archive-old\n\n")
    output.append("# 3. 删除重复报告 (谨慎!)\n")
    output.append("python cleanup_reports.py --delete-duplicates\n")
    output.append("```\n")
    
    return '\n'.join(output)


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='报告系统清理工具')
    parser.add_argument('--root', default='D:\\OpenClaw\\workspace', help='根目录')
    parser.add_argument('--output', default='CLEANUP-RECOMMENDATIONS.md', help='输出文件')
    parser.add_argument('--show-duplicates', action='store_true', help='显示重复报告')
    parser.add_argument('--archive-old', action='store_true', help='归档旧报告')
    parser.add_argument('--dry-run', action='store_true', help='仅显示，不执行')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Report Cleanup Tool")
    print("=" * 60)
    
    # 扫描报告
    print(f"\n[1/4] Scanning report files...")
    reports = get_report_files(args.root)
    print(f"  Found {len(reports)} report files")
    
    # 分析
    print(f"\n[2/4] Analyzing reports...")
    analyzed = [analyze_report(r) for r in reports]
    
    # 查找重复
    print(f"\n[3/4] Finding duplicates...")
    duplicates = find_duplicates(analyzed)
    similar = find_similar_names(analyzed)
    print(f"  Exact duplicates: {len(duplicates)} groups")
    print(f"  Similar names: {len(similar)} groups")
    
    # 生成报告
    print(f"\n[4/4] Generating cleanup recommendations...")
    cleanup_report = generate_cleanup_report(analyzed, duplicates, similar)
    
    # 保存
    output_path = Path(args.root) / args.output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(cleanup_report)
    
    print(f"\n[OK] Cleanup recommendations saved to: {output_path}")
    print(f"\n{'=' * 60}")
    print("Summary:")
    print(f"  Total reports: {len(analyzed)}")
    print(f"  Suggest archive: {len([r for r in analyzed if r['suggest_archive']])}")
    print(f"  Exact duplicates: {len(duplicates)} groups")
    print(f"  High importance: {len([r for r in analyzed if r['importance'] == 'high'])}")
    print(f"{'=' * 60}")


if __name__ == '__main__':
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Scan Daily Notes - 日常笔记扫描与清理工具

功能:
- 扫描 13-memory/ 目录下所有日常笔记
- 检测污染笔记 (包含历史总结章节)
- 提供清理建议
- 自动备份并清理污染内容

使用:
  py scan-daily-notes.py --scan          # 只扫描
  py scan-daily-notes.py --clean         # 清理 (先备份)
  py scan-daily-notes.py --report        # 生成报告
"""

import sys
import io
import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple

# Windows 编码修复
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

WORKSPACE = Path(__file__).parent.parent
MEMORY_DIR = WORKSPACE / '13-memory'
BACKUP_DIR = WORKSPACE / '99-backups' / 'daily-note-cleanup'

# 污染检测配置
MAX_LINES = 150
MAX_SIZE_KB = 8
POLLUTION_CHAPTERS = [
    "## 历史总结",
    "## Previous Summary",
    "## 昨日成果",
    "## 所有会话",
    "## 总结所有",
    "## 全部会话",
    "## 过往成果",
]

# 保留的章节 (正常内容)
KEEP_SECTIONS = [
    "# YYYY-MM-DD",
    "## 📊 会话",
    "## 🎯 进度",
    "## 📝 下一步",
    "## Session Summary",
    "## Session Context",
]


def scan_daily_notes() -> List[Dict]:
    """扫描所有日常笔记"""
    if not MEMORY_DIR.exists():
        print(f"[ERROR] 目录不存在：{MEMORY_DIR}")
        return []
    
    results = []
    daily_notes = sorted(MEMORY_DIR.glob("20*.md"))  # 匹配 2026-03-18.md 格式
    
    for note_file in daily_notes:
        # 跳过模板文件
        if "template" in note_file.name.lower():
            continue
        
        result = check_note_pollution(note_file)
        results.append(result)
    
    return results


def check_note_pollution(note_file: Path) -> Dict:
    """检查单个笔记是否被污染"""
    try:
        content = note_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        size_kb = note_file.stat().st_size / 1024
        
        issues = []
        pollution_found = []
        
        # 检查 1: 行数
        if len(lines) > MAX_LINES:
            issues.append(f"行数过多 ({len(lines)}行 > {MAX_LINES}行)")
        
        # 检查 2: 大小
        if size_kb > MAX_SIZE_KB:
            issues.append(f"文件过大 ({size_kb:.1f}KB > {MAX_SIZE_KB}KB)")
        
        # 检查 3: 污染章节
        for chapter in POLLUTION_CHAPTERS:
            if chapter in content:
                pollution_found.append(chapter)
                issues.append(f"污染章节：{chapter}")
        
        return {
            'file': str(note_file.relative_to(WORKSPACE)),
            'lines': len(lines),
            'size_kb': size_kb,
            'is_polluted': len(pollution_found) > 0,
            'pollution_chapters': pollution_found,
            'issues': issues,
            'status': 'POLLUTED' if pollution_found else 'CLEAN'
        }
    
    except Exception as e:
        return {
            'file': str(note_file.relative_to(WORKSPACE)),
            'status': 'ERROR',
            'error': str(e)
        }


def print_scan_report(results: List[Dict]):
    """打印扫描报告"""
    print("="*60)
    print("日常笔记扫描报告")
    print("="*60)
    print()
    
    total = len(results)
    polluted = sum(1 for r in results if r.get('is_polluted', False))
    clean = sum(1 for r in results if r.get('status') == 'CLEAN')
    errors = sum(1 for r in results if r.get('status') == 'ERROR')
    
    print(f"总文件数：{total}")
    print(f"清洁笔记：{clean} ({clean/total*100:.0f}%)")
    print(f"污染笔记：{polluted} ({polluted/total*100:.0f}%)")
    print(f"检查错误：{errors}")
    print()
    
    if polluted > 0:
        print("-"*60)
        print("污染笔记详情:")
        print("-"*60)
        print()
        
        for result in results:
            if result.get('is_polluted'):
                print(f"📄 {result['file']}")
                print(f"   行数：{result['lines']}行")
                print(f"   大小：{result['size_kb']:.1f}KB")
                print(f"   污染章节:")
                for chapter in result['pollution_chapters']:
                    print(f"     - {chapter}")
                if result.get('issues'):
                    print(f"   其他问题:")
                    for issue in result['issues']:
                        if not any(ch in issue for ch in POLLUTION_CHAPTERS):
                            print(f"     - {issue}")
                print()
    
    print("="*60)


def backup_and_clean(note_file: Path, workspace: Path) -> bool:
    """备份并清理污染笔记"""
    try:
        # 创建备份目录
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        
        # 备份文件
        backup_path = BACKUP_DIR / f"{note_file.stem}_{timestamp}.md"
        shutil.copy2(note_file, backup_path)
        print(f"  [BACKUP] {backup_path}")
        
        # 读取内容
        content = note_file.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # 清理污染章节
        cleaned_lines = []
        in_pollution_section = False
        pollution_start = -1
        
        for i, line in enumerate(lines):
            # 检查是否进入污染章节
            if any(line.strip() == chapter for chapter in POLLUTION_CHAPTERS):
                in_pollution_section = True
                pollution_start = i
                continue
            
            # 检查是否进入下一个正常章节
            if in_pollution_section and line.startswith('## '):
                in_pollution_section = False
                # 保留新章节
                cleaned_lines.append(line)
                continue
            
            # 如果不是污染章节，保留
            if not in_pollution_section:
                cleaned_lines.append(line)
        
        # 写入清理后的内容
        cleaned_content = '\n'.join(cleaned_lines)
        note_file.write_text(cleaned_content, encoding='utf-8')
        
        rel_path = note_file.relative_to(workspace)
        print(f"  [CLEANED] {rel_path}")
        print(f"            {len(lines)}行 → {len(cleaned_lines)}行 (-{len(lines)-len(cleaned_lines)}行)")
        
        return True
    
    except Exception as e:
        print(f"  [ERROR] 清理失败：{e}")
        return False


def clean_polluted_notes(results: List[Dict], workspace: Path) -> int:
    """清理所有污染笔记"""
    cleaned_count = 0
    
    for result in results:
        if result.get('is_polluted'):
            note_file = Path(result['file'])
            if not note_file.is_absolute():
                note_file = workspace / note_file
            if note_file.exists():
                print(f"\n清理：{note_file}")
                if backup_and_clean(note_file, workspace):
                    cleaned_count += 1
    
    return cleaned_count


def generate_report(results: List[Dict]):
    """生成详细报告"""
    report_file = WORKSPACE / '21-reports' / f'daily-notes-scan-{datetime.now().strftime("%Y%m%d")}.md'
    report_file.parent.mkdir(parents=True, exist_ok=True)
    
    total = len(results)
    polluted = sum(1 for r in results if r.get('is_polluted', False))
    
    content = f"""# 日常笔记扫描报告

**日期:** {datetime.now().strftime("%Y-%m-%d %H:%M")}  
**总文件数:** {total}  
**污染笔记:** {polluted} ({polluted/total*100:.1f}%)

---

## 污染笔记详情

"""
    
    for result in results:
        if result.get('is_polluted'):
            content += f"### {result['file']}\n\n"
            content += f"- 行数：{result['lines']}行\n"
            content += f"- 大小：{result['size_kb']:.1f}KB\n"
            content += f"- 污染章节:\n"
            for chapter in result['pollution_chapters']:
                content += f"  - {chapter}\n"
            content += "\n"
    
    content += """---

## 建议

1. 定期运行扫描：`py 30-scripts-tools/scan-daily-notes.py --scan`
2. 发现污染立即清理：`py 30-scripts-tools/scan-daily-notes.py --clean`
3. 使用模板创建笔记：`13-memory/YYYY-MM-DD-template.md`

"""
    
    report_file.write_text(content, encoding='utf-8')
    print(f"\n报告已保存：{report_file}")


def main():
    print("="*60)
    print("Scan Daily Notes - 日常笔记扫描与清理 v1.0")
    print("="*60)
    print()
    
    # 解析参数
    if len(sys.argv) < 2:
        print("使用:")
        print("  py scan-daily-notes.py --scan     # 只扫描")
        print("  py scan-daily-notes.py --clean    # 清理 (先备份)")
        print("  py scan-daily-notes.py --report   # 生成报告")
        return 1
    
    mode = sys.argv[1].lower()
    
    # 扫描
    print("[1/3] 扫描日常笔记...")
    results = scan_daily_notes()
    
    if not results:
        print("[ERROR] 未找到日常笔记")
        return 1
    
    print(f"     找到 {len(results)} 个笔记")
    print()
    
    # 打印报告
    print("[2/3] 生成扫描报告...")
    print_scan_report(results)
    
    # 根据模式处理
    if mode == '--scan':
        print("\n[OK] 扫描完成")
        return 0
    
    elif mode == '--clean':
        print("\n[3/3] 清理污染笔记...")
        polluted_count = sum(1 for r in results if r.get('is_polluted', False))
        
        if polluted_count == 0:
            print("[OK] 无污染笔记，无需清理")
            return 0
        
        print(f"发现 {polluted_count} 个污染笔记")
        print()
        
        # 确认
        response = input("确认清理？(y/N): ").strip().lower()
        if response != 'y':
            print("[CANCEL] 清理已取消")
            return 0
        
        cleaned_count = clean_polluted_notes(results, WORKSPACE)
        
        print()
        print("="*60)
        print(f"[OK] 清理完成！")
        print(f"     清理：{cleaned_count}/{polluted_count} 个笔记")
        print(f"     备份：{BACKUP_DIR}")
        print("="*60)
        return 0
    
    elif mode == '--report':
        print("\n[3/3] 生成详细报告...")
        generate_report(results)
        return 0
    
    else:
        print(f"[ERROR] 未知模式：{mode}")
        return 1


if __name__ == '__main__':
    sys.exit(main())

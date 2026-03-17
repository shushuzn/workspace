#!/usr/bin/env python3

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Workspace File Comparator - 自动化工作区文件对比工具

功能:
- 自动扫描指定目录的 md 文件
- 与 C 盘配置目录进行对比
- 识别独特内容
- 生成对比报告
- 标记需要人工审查的关键差异

使用示例:
    python workspace_comparator.py --dirs "15-docs-文档规范" "30-scripts-tools"
    python workspace_comparator.py --all  # 扫描所有目录
    python workspace_comparator.py --report  # 生成详细报告

作者：Claw [PAW]
日期：2026-03-14
"""

import os
import sys
import hashlib
import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import difflib

# UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# 配置
WORKSPACE_DIR = Path(__file__).parent.parent
CONFIG_DIR = Path(r"C:\Users\华为\.copaw")

# 忽略的目录
IGNORE_DIRS = {
    'node_modules',
    '__pycache__',
    '.git',
    '99-archive-old',
    'OpenClaw-RL',
    '06-research',
    'tests',
    '__tests__',
}

# 忽略的文件模式
IGNORE_PATTERNS = {
    '*.test.md',
    '*.spec.md',
    '*.bak',
    '*.tmp',
    '*.backup',
}

@dataclass
class FileInfo:
    """文件信息数据类"""
    path: str
    relative_path: str
    size: int
    size_kb: float
    md5: str
    lines: int
    words: int
    modified: str
    
@dataclass
class ComparisonResult:
    """对比结果数据类"""
    file_path: str
    status: str  # 'identical', 'modified', 'unique_workspace', 'unique_config'
    workspace_info: Optional[FileInfo]
    config_info: Optional[FileInfo]
    similarity: float  # 0.0-1.0
    diff_lines: List[str]
    unique_content_workspace: List[str]
    unique_content_config: List[str]
    priority: str  # 'high', 'medium', 'low'
    review_needed: bool

class WorkspaceComparator:
    """工作区文件对比器"""
    
    def __init__(self, workspace_dir: Path = WORKSPACE_DIR, config_dir: Path = CONFIG_DIR):
        self.workspace_dir = workspace_dir
        self.config_dir = config_dir
        self.results: List[ComparisonResult] = []
        self.stats = {
            'total_scanned': 0,
            'identical': 0,
            'modified': 0,
            'unique_workspace': 0,
            'unique_config': 0,
            'high_priority': 0,
            'review_needed': 0,
        }
    
    def calculate_md5(self, file_path: Path) -> str:
        """计算文件 MD5 哈希值"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def count_words(self, file_path: Path) -> int:
        """计算文件单词数"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return len(content.split())
    
    def count_lines(self, file_path: Path) -> int:
        """计算文件行数"""
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return sum(1 for _ in f)
    
    def get_file_info(self, file_path: Path, base_dir: Path) -> FileInfo:
        """获取文件详细信息"""
        stat = file_path.stat()
        return FileInfo(
            path=str(file_path),
            relative_path=str(file_path.relative_to(base_dir)),
            size=stat.st_size,
            size_kb=round(stat.st_size / 1024, 2),
            md5=self.calculate_md5(file_path),
            lines=self.count_lines(file_path),
            words=self.count_words(file_path),
            modified=datetime.fromtimestamp(stat.st_mtime).isoformat()
        )
    
    def should_ignore(self, file_path: Path) -> bool:
        """检查是否应该忽略文件"""
        # 检查目录
        for part in file_path.parts:
            if part in IGNORE_DIRS:
                return True
        
        # 检查文件模式
        for pattern in IGNORE_PATTERNS:
            if file_path.match(pattern):
                return True
        
        return False
    
    def scan_directory(self, directory: Path, base_dir: Path, min_size_kb: float = 0) -> Dict[str, FileInfo]:
        """扫描目录获取文件信息"""
        files = {}
        
        if not directory.exists():
            print(f"[WARN]  目录不存在：{directory}")
            return files
        
        for file_path in directory.rglob("*.md"):
            if self.should_ignore(file_path):
                continue
            
            if file_path.stat().st_size / 1024 < min_size_kb:
                continue
            
            try:
                info = self.get_file_info(file_path, base_dir)
                files[info.relative_path] = info
            except Exception as e:
                print(f"[WARN]  读取失败 {file_path}: {e}")
        
        return files
    
    def calculate_similarity(self, content1: str, content2: str) -> float:
        """计算两个内容的相似度"""
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        
        matcher = difflib.SequenceMatcher(None, lines1, lines2)
        return round(matcher.ratio(), 3)
    
    def get_diff_lines(self, content1: str, content2: str, context_lines: int = 3) -> List[str]:
        """获取差异行"""
        lines1 = content1.splitlines()
        lines2 = content2.splitlines()
        
        diff = difflib.unified_diff(lines1, lines2, lineterm='', n=context_lines)
        return list(diff)[:50]  # 限制最多 50 行差异
    
    def extract_unique_content(self, content: str, reference: str) -> List[str]:
        """提取独特内容片段"""
        unique = []
        lines = content.splitlines()
        ref_lines = reference.splitlines()
        
        for line in lines:
            if len(line.strip()) > 20:  # 忽略短行
                # 检查是否在参考内容中存在相似行
                found = False
                for ref_line in ref_lines:
                    if difflib.SequenceMatcher(None, line, ref_line).ratio() > 0.8:
                        found = True
                        break
                
                if not found:
                    unique.append(line)
        
        return unique[:20]  # 限制最多 20 条
    
    def determine_priority(self, file_path: str, workspace_info: Optional[FileInfo], 
                          config_info: Optional[FileInfo], similarity: float) -> str:
        """确定对比优先级"""
        # 高优先级：核心配置文件
        core_files = [
            'AGENTS.md', 'SOUL.md', 'MEMORY.md', 'PROFILE.md',
            'HEARTBEAT.md', 'README.md', 'CHANGELOG.md'
        ]
        
        for core in core_files:
            if core in file_path:
                return 'high'
        
        # 高优先级：大文件 (>20KB)
        if workspace_info and workspace_info.size_kb > 20:
            return 'high'
        if config_info and config_info.size_kb > 20:
            return 'high'
        
        # 中优先级：中等差异
        if 0.5 <= similarity <= 0.9:
            return 'medium'
        
        # 低优先级：小文件或高度相似
        return 'low'
    
    def compare_files(self, workspace_files: Dict[str, FileInfo], 
                     config_files: Dict[str, FileInfo]) -> List[ComparisonResult]:
        """对比文件"""
        results = []
        all_paths = set(workspace_files.keys()) | set(config_files.keys())
        
        for rel_path in all_paths:
            ws_info = workspace_files.get(rel_path)
            cfg_info = config_files.get(rel_path)
            
            # 确定状态
            if ws_info and cfg_info:
                if ws_info.md5 == cfg_info.md5:
                    status = 'identical'
                    similarity = 1.0
                    diff_lines = []
                    unique_ws = []
                    unique_cfg = []
                else:
                    status = 'modified'
                    # 读取内容计算相似度
                    try:
                        with open(ws_info.path, 'r', encoding='utf-8', errors='ignore') as f:
                            ws_content = f.read()
                        with open(cfg_info.path, 'r', encoding='utf-8', errors='ignore') as f:
                            cfg_content = f.read()
                        
                        similarity = self.calculate_similarity(ws_content, cfg_content)
                        diff_lines = self.get_diff_lines(ws_content, cfg_content)
                        unique_ws = self.extract_unique_content(ws_content, cfg_content)
                        unique_cfg = self.extract_unique_content(cfg_content, ws_content)
                    except Exception as e:
                        print(f"[WARN]  对比失败 {rel_path}: {e}")
                        similarity = 0.0
                        diff_lines = []
                        unique_ws = []
                        unique_cfg = []
            elif ws_info:
                status = 'unique_workspace'
                similarity = 0.0
                diff_lines = []
                unique_ws = []
                unique_cfg = []
            else:
                status = 'unique_config'
                similarity = 0.0
                diff_lines = []
                unique_ws = []
                unique_cfg = []
            
            # 确定优先级
            priority = self.determine_priority(rel_path, ws_info, cfg_info, similarity)
            
            # 是否需要人工审查
            review_needed = (
                status == 'modified' and similarity < 0.9 or
                status == 'unique_workspace' and (ws_info and ws_info.size_kb > 10) or
                status == 'unique_config' and (cfg_info and cfg_info.size_kb > 10) or
                priority == 'high'
            )
            
            result = ComparisonResult(
                file_path=rel_path,
                status=status,
                workspace_info=ws_info,
                config_info=cfg_info,
                similarity=similarity,
                diff_lines=diff_lines,
                unique_content_workspace=unique_ws,
                unique_content_config=unique_cfg,
                priority=priority,
                review_needed=review_needed
            )
            
            results.append(result)
            
            # 更新统计
            self.stats['total_scanned'] += 1
            self.stats[status] += 1
            if priority == 'high':
                self.stats['high_priority'] += 1
            if review_needed:
                self.stats['review_needed'] += 1
        
        return results
    
    def scan_and_compare(self, target_dirs: List[str] = None, min_size_kb: float = 5.0):
        """扫描并对比"""
        print("[SCAN] 开始扫描工作区...")
        
        # 扫描工作区
        workspace_files = {}
        if target_dirs:
            for dir_name in target_dirs:
                dir_path = self.workspace_dir / dir_name
                files = self.scan_directory(dir_path, self.workspace_dir, min_size_kb)
                workspace_files.update(files)
                print(f"  [DIR] {dir_name}: {len(files)} 个文件")
        else:
            workspace_files = self.scan_directory(self.workspace_dir, self.workspace_dir, min_size_kb)
            print(f"  [DIR] 全工作区：{len(workspace_files)} 个文件")
        
        # 扫描配置目录
        print("[SCAN] 开始扫描配置目录...")
        config_files = self.scan_directory(self.config_dir, self.config_dir, min_size_kb)
        print(f"  [DIR] C 盘配置：{len(config_files)} 个文件")
        
        # 对比
        print("[COMPARE] 开始对比文件...")
        self.results = self.compare_files(workspace_files, config_files)
        
        print(f"[DONE] 对比完成！共扫描 {self.stats['total_scanned']} 个文件")
    
    def generate_report(self, output_path: str = None, save_to_file: bool = False):
        """生成对比报告
        
        Args:
            output_path: 报告文件路径
            save_to_file: 是否保存到文件（默认 False，只输出到控制台）
        
        合规说明 [FILE-006]:
        - 默认不创建报告文件（save_to_file=False）
        - 只在控制台输出结果
        - 如需保存，使用 --save 参数（明确指定）
        """
        if save_to_file:
            # 只有明确指定 --save 才创建文件
            if not output_path:
                output_path = self.workspace_dir / "00-persona-system" / "workspace-comparison-latest.md"
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        else:
            # 默认：只输出到控制台，不创建文件
            output_path = None
        
        # 按优先级排序
        high_priority = [r for r in self.results if r.priority == 'high' and r.review_needed]
        medium_priority = [r for r in self.results if r.priority == 'medium' and r.review_needed]
        low_priority = [r for r in self.results if r.priority == 'low' and r.review_needed]
        
        report = []
        report.append("# Workspace File Comparison Report\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Workspace:** {self.workspace_dir}\n")
        report.append(f"**Config:** {self.config_dir}\n")
        report.append("---\n")
        
        # 统计摘要
        report.append("## Summary\n")
        report.append(f"| Metric | Count |")
        report.append(f"|--------|-------|")
        report.append(f"| Total Scanned | {self.stats['total_scanned']} |")
        report.append(f"| Identical | {self.stats['identical']} |")
        report.append(f"| Modified | {self.stats['modified']} |")
        report.append(f"| Unique (Workspace) | {self.stats['unique_workspace']} |")
        report.append(f"| Unique (Config) | {self.stats['unique_config']} |")
        report.append(f"| High Priority | {self.stats['high_priority']} |")
        report.append(f"| Review Needed | {self.stats['review_needed']} |")
        report.append("\n")
        
        # 高优先级需要审查的文件
        if high_priority:
            report.append("## High Priority - Review Needed\n")
            for result in high_priority[:20]:  # 限制最多 20 个
                report.append(f"### {result.file_path}\n")
                report.append(f"- **Status:** {result.status}")
                report.append(f"- **Similarity:** {result.similarity:.1%}")
                
                if result.workspace_info:
                    report.append(f"- **Workspace Size:** {result.workspace_info.size_kb} KB")
                if result.config_info:
                    report.append(f"- **Config Size:** {result.config_info.size_kb} KB")
                
                if result.unique_content_workspace:
                    report.append(f"\n**Unique in Workspace:**")
                    for line in result.unique_content_workspace[:5]:
                        report.append(f"- `{line[:80]}...`")
                
                if result.unique_content_config:
                    report.append(f"\n**Unique in Config:**")
                    for line in result.unique_content_config[:5]:
                        report.append(f"- `{line[:80]}...`")
                
                report.append("\n---\n")
        
        # 中优先级
        if medium_priority:
            report.append("## Medium Priority\n")
            report.append(f"*{len(medium_priority)} files need review*\n")
            report.append("| File | Status | Similarity | Size (WS/CFG) |")
            report.append("|------|--------|------------|---------------|")
            for result in medium_priority[:30]:
                ws_size = f"{result.workspace_info.size_kb}KB" if result.workspace_info else "N/A"
                cfg_size = f"{result.config_info.size_kb}KB" if result.config_info else "N/A"
                report.append(f"| {result.file_path} | {result.status} | {result.similarity:.1%} | {ws_size}/{cfg_size} |")
            report.append("\n")
        
        # 低优先级摘要
        if low_priority:
            report.append("## Low Priority\n")
            report.append(f"*{len(low_priority)} files, minor differences*\n")
        
        # 完整文件列表
        report.append("## Complete File List\n")
        report.append("| File | Status | Similarity | Priority | Review |")
        report.append("|------|--------|------------|----------|--------|")
        for result in sorted(self.results, key=lambda x: (x.priority != 'high', x.similarity)):
            review = "[x]" if result.review_needed else ""
            report.append(f"| {result.file_path} | {result.status} | {result.similarity:.1%} | {result.priority} | {review} |")
        
        # 写入文件（只有 save_to_file=True 时才执行）
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(report))
            print(f"[REPORT] 报告已生成：{output_path}")
        else:
            # 只输出到控制台，不创建文件
            print("\n" + "="*60)
            print("COMPARISON REPORT (Console Output)")
            print("="*60)
            print('\n'.join(report))
            print("="*60)
        
        return output_path
    
    def generate_json_report(self, output_path: str = None):
        """生成 JSON 格式报告"""
        if not output_path:
            output_path = self.workspace_dir / "00-persona-system" / f"workspace-comparison-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'generated': datetime.now().isoformat(),
            'workspace_dir': str(self.workspace_dir),
            'config_dir': str(self.config_dir),
            'statistics': self.stats,
            'results': []
        }
        
        for result in self.results:
            result_dict = {
                'file_path': result.file_path,
                'status': result.status,
                'similarity': result.similarity,
                'priority': result.priority,
                'review_needed': result.review_needed,
            }
            
            if result.workspace_info:
                result_dict['workspace'] = asdict(result.workspace_info)
            if result.config_info:
                result_dict['config'] = asdict(result.config_info)
            
            data['results'].append(result_dict)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"[JSON] 报告已生成：{output_path}")
        return output_path


def main():
    parser = argparse.ArgumentParser(description='Workspace File Comparator')
    parser.add_argument('--dirs', nargs='+', help='Target directories to scan')
    parser.add_argument('--all', action='store_true', help='Scan all directories')
    parser.add_argument('--min-size', type=float, default=5.0, help='Minimum file size in KB')
    parser.add_argument('--report', action='store_true', help='Generate detailed report (console output)')
    parser.add_argument('--save', action='store_true', help='Save report to file (creates file, use sparingly)')
    parser.add_argument('--json', action='store_true', help='Generate JSON report')
    parser.add_argument('--output', type=str, help='Output file path')
    
    args = parser.parse_args()
    
    comparator = WorkspaceComparator()
    
    # 扫描并对比
    if args.all:
        comparator.scan_and_compare(target_dirs=None, min_size_kb=args.min_size)
    else:
        target_dirs = args.dirs or ['15-docs-文档规范', '30-scripts-tools']
        comparator.scan_and_compare(target_dirs=target_dirs, min_size_kb=args.min_size)
    
    # 生成报告
    # 合规 [FILE-006]: 默认不创建文件，只输出到控制台
    save_to_file = args.save  # 只有明确指定 --save 才创建文件
    
    if args.report or args.json:
        if args.report:
            comparator.generate_report(args.output, save_to_file=save_to_file)
        if args.json:
            comparator.generate_json_report(args.output)
    
    # 打印摘要
    print("\n" + "="*60)
    print("COMPARISON SUMMARY")
    print("="*60)
    print(f"Total Scanned:     {comparator.stats['total_scanned']}")
    print(f"Identical:         {comparator.stats['identical']}")
    print(f"Modified:          {comparator.stats['modified']}")
    print(f"Unique (Workspace):{comparator.stats['unique_workspace']}")
    print(f"Unique (Config):   {comparator.stats['unique_config']}")
    print(f"High Priority:     {comparator.stats['high_priority']}")
    print(f"Review Needed:     {comparator.stats['review_needed']}")
    print("="*60)


if __name__ == '__main__':
    main()

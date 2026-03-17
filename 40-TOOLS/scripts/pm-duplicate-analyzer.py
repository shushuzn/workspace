#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细重复文件夹分析工具
分析工作区中的重复文件夹，生成合并建议
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Set
from difflib import SequenceMatcher

# UTF-8 for Windows
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)


class DuplicateFolderAnalyzer:
    """重复文件夹分析器"""
    
    def __init__(self, workspace: str):
        self.workspace = Path(workspace)
        self.folders = []
        self.duplicate_pairs = []
        self.naming_patterns = {
            "english": [],
            "chinese": [],
            "bilingual": []
        }
    
    def scan_folders(self, max_depth: int = 1):
        """扫描文件夹"""
        print(f"📁 扫描工作区：{self.workspace}")
        print(f"最大深度：{max_depth} 层\n")
        
        self.folders = []
        for item in self.workspace.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                self.folders.append({
                    "name": item.name,
                    "path": str(item),
                    "depth": 1,
                    "file_count": self.count_files(item),
                    "size_mb": self.get_folder_size(item) / (1024 * 1024)
                })
        
        print(f"发现文件夹：{len(self.folders)} 个\n")
        return self.folders
    
    def count_files(self, folder: Path) -> int:
        """统计文件夹内文件数"""
        try:
            return sum(1 for _ in folder.rglob('*') if _.is_file())
        except:
            return 0
    
    def get_folder_size(self, folder: Path) -> int:
        """获取文件夹大小（字节）"""
        try:
            return sum(f.stat().st_size for f in folder.rglob('*') if f.is_file())
        except:
            return 0
    
    def classify_naming(self, name: str) -> str:
        """分类命名风格"""
        has_chinese = any('\u4e00' <= c <= '\u9fff' for c in name)
        has_english = any(c.isalpha() for c in name)
        has_hyphen = '-' in name
        
        if has_chinese and has_english and has_hyphen:
            return "bilingual"
        elif has_chinese:
            return "chinese"
        else:
            return "english"
    
    def analyze_naming_patterns(self):
        """分析命名模式"""
        print("📊 分析命名模式...\n")
        
        for folder in self.folders:
            pattern = self.classify_naming(folder["name"])
            self.naming_patterns[pattern].append(folder["name"])
        
        print(f"英文命名：{len(self.naming_patterns['english'])} 个")
        print(f"中文命名：{len(self.naming_patterns['chinese'])} 个")
        print(f"双语命名：{len(self.naming_patterns['bilingual'])} 个")
        print()
    
    def similarity_ratio(self, s1: str, s2: str) -> float:
        """计算相似度"""
        # 移除数字前缀和连字符
        def normalize(s):
            # 移除数字前缀如 "00-", "01-"
            parts = s.split('-', 1)
            if len(parts) > 1 and parts[0].isdigit():
                s = parts[1]
            return s.lower().replace('-', '').replace('_', '').replace(' ', '')
        
        n1 = normalize(s1)
        n2 = normalize(s2)
        
        # 完全匹配
        if n1 == n2:
            return 1.0
        
        # 包含关系
        if n1 in n2 or n2 in n1:
            return 0.8
        
        # 相似度计算
        return SequenceMatcher(None, n1, n2).ratio()
    
    def find_duplicates(self, threshold: float = 0.6):
        """查找重复文件夹"""
        print(f"🔍 查找重复文件夹（阈值：{threshold}）...\n")
        
        self.duplicate_pairs = []
        
        for i, f1 in enumerate(self.folders):
            for f2 in self.folders[i+1:]:
                similarity = self.similarity_ratio(f1["name"], f2["name"])
                
                if similarity >= threshold:
                    self.duplicate_pairs.append({
                        "folder1": f1,
                        "folder2": f2,
                        "similarity": similarity,
                        "reason": self.get_similarity_reason(f1["name"], f2["name"], similarity)
                    })
        
        # 按相似度排序
        self.duplicate_pairs.sort(key=lambda x: x["similarity"], reverse=True)
        
        print(f"发现重复文件夹对：{len(self.duplicate_pairs)} 对\n")
        return self.duplicate_pairs
    
    def get_similarity_reason(self, name1: str, name2: str, similarity: float) -> str:
        """获取相似度原因"""
        if similarity == 1.0:
            return "完全匹配（仅前缀不同）"
        elif similarity >= 0.8:
            return "包含关系或高度相似"
        elif similarity >= 0.6:
            return "部分相似"
        else:
            return "弱相似"
    
    def generate_merge_recommendations(self):
        """生成合并建议"""
        print("💡 生成合并建议...\n")
        
        recommendations = []
        
        for pair in self.duplicate_pairs:
            f1 = pair["folder1"]
            f2 = pair["folder2"]
            
            # 决定保留哪个文件夹
            # 优先保留：英文命名 > 文件多 > 体积小
            def score_folder(f):
                score = 0
                if self.classify_naming(f["name"]) == "english":
                    score += 10
                score += f["file_count"] * 0.1
                score -= f["size_mb"] * 0.01  # 体积小优先
                return score
            
            score1 = score_folder(f1)
            score2 = score_folder(f2)
            
            if score1 > score2:
                keep = f1
                merge = f2
            else:
                keep = f2
                merge = f1
            
            recommendations.append({
                "action": "MERGE",
                "keep": keep,
                "merge": merge,
                "reason": f"相似度 {pair['similarity']:.0%} - {pair['reason']}",
                "files_to_move": merge["file_count"],
                "size_to_move_mb": merge["size_mb"]
            })
        
        return recommendations
    
    def print_detailed_report(self):
        """打印详细报告"""
        print("=" * 80)
        print("📊 重复文件夹详细分析报告")
        print("=" * 80)
        print()
        
        # 1. 总体统计
        print("📈 总体统计")
        print("-" * 80)
        print(f"总文件夹数：{len(self.folders)}")
        print(f"重复文件夹对：{len(self.duplicate_pairs)}")
        print(f"预计可减少：{len(self.duplicate_pairs)} 个文件夹")
        print(f"预计最终文件夹数：{len(self.folders) - len(self.duplicate_pairs)}")
        print()
        
        # 2. 命名模式
        print("📝 命名模式分析")
        print("-" * 80)
        print(f"英文命名：{len(self.naming_patterns['english'])} 个 ({len(self.naming_patterns['english'])/len(self.folders)*100:.1f}%)")
        print(f"中文命名：{len(self.naming_patterns['chinese'])} 个 ({len(self.naming_patterns['chinese'])/len(self.folders)*100:.1f}%)")
        print(f"双语命名：{len(self.naming_patterns['bilingual'])} 个 ({len(self.naming_patterns['bilingual'])/len(self.folders)*100:.1f}%)")
        print()
        
        # 3. 重复文件夹列表
        print("🔄 重复文件夹对（按相似度排序）")
        print("-" * 80)
        for i, pair in enumerate(self.duplicate_pairs[:20], 1):  # 显示前 20 个
            f1 = pair["folder1"]["name"]
            f2 = pair["folder2"]["name"]
            sim = pair["similarity"]
            reason = pair["reason"]
            print(f"{i:2d}. {f1:40} ↔ {f2:40} ({sim:.0%} - {reason})")
        
        if len(self.duplicate_pairs) > 20:
            print(f"... 还有 {len(self.duplicate_pairs) - 20} 对")
        print()
        
        # 4. 合并建议
        print("💡 合并建议（前 10 个）")
        print("-" * 80)
        recommendations = self.generate_merge_recommendations()
        for i, rec in enumerate(recommendations[:10], 1):
            keep = rec["keep"]["name"]
            merge = rec["merge"]["name"]
            files = rec["files_to_move"]
            size = rec["size_to_move_mb"]
            print(f"{i:2d}. 保留：{keep:40} | 合并：{merge:40} | 文件：{files:3d} | 大小：{size:.1f}MB")
        print()
        
        # 5. 完整文件夹列表
        print("📂 完整文件夹列表")
        print("-" * 80)
        for folder in sorted(self.folders, key=lambda x: x["name"]):
            pattern = self.classify_naming(folder["name"])
            pattern_icon = {"english": "🔤", "chinese": "🈳", "bilingual": "🔠"}[pattern]
            print(f"{pattern_icon} {folder['name']:45} | 文件：{folder['file_count']:4d} | 大小：{folder['size_mb']:7.2f}MB")
        print()
    
    def save_report(self, output_path: str):
        """保存报告到文件"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "workspace": str(self.workspace),
            "statistics": {
                "total_folders": len(self.folders),
                "duplicate_pairs": len(self.duplicate_pairs),
                "naming_patterns": {
                    "english": len(self.naming_patterns["english"]),
                    "chinese": len(self.naming_patterns["chinese"]),
                    "bilingual": len(self.naming_patterns["bilingual"])
                }
            },
            "duplicate_pairs": [
                {
                    "folder1": pair["folder1"]["name"],
                    "folder2": pair["folder2"]["name"],
                    "similarity": pair["similarity"],
                    "reason": pair["reason"]
                }
                for pair in self.duplicate_pairs
            ],
            "recommendations": [
                {
                    "keep": rec["keep"]["name"],
                    "merge": rec["merge"]["name"],
                    "files_to_move": rec["files_to_move"],
                    "size_mb": rec["size_to_move_mb"]
                }
                for rec in self.generate_merge_recommendations()
            ]
        }
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"✅ 报告已保存：{output_file}")
        return output_file


def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="重复文件夹分析工具")
    parser.add_argument("--workspace", default="D:\\OpenClaw\\workspace",
                       help="工作区路径")
    parser.add_argument("--output", default="agent-pm/reports/cleanliness-reports/duplicate-analysis.json",
                       help="输出报告路径")
    parser.add_argument("--threshold", type=float, default=0.6,
                       help="相似度阈值 (0-1)")
    
    args = parser.parse_args()
    
    analyzer = DuplicateFolderAnalyzer(args.workspace)
    analyzer.scan_folders()
    analyzer.analyze_naming_patterns()
    analyzer.find_duplicates(args.threshold)
    analyzer.print_detailed_report()
    
    if args.output:
        analyzer.save_report(args.output)


if __name__ == "__main__":
    main()

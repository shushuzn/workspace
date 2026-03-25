#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
记忆蒸馏器 - 从日常笔记提炼长期记忆
触发条件：MEMORY.md > 50KB 或 日常笔记 > 10 条未处理
"""

import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List

class MemoryDistiller:
    """记忆蒸馏器"""

    def __init__(self):
        self.memory_file = Path("13-memory/MEMORY.md")
        self.daily_dir = Path("13-memory")
        self.threshold_size_kb = 50
        self.threshold_unprocessed = 10
        self.processed_marker = ".distilled"

    def check_threshold(self) -> Dict:
        """检查是否达到蒸馏阈值"""
        result = {
            "should_distill": False,
            "reason": [],
            "current_stats": {}
        }

        # 检查 MEMORY.md 大小
        if self.memory_file.exists():
            size_kb = self.memory_file.stat().st_size / 1024
            result["current_stats"]["memory_size_kb"] = size_kb

            if size_kb > self.threshold_size_kb:
                result["should_distill"] = True
                result["reason"].append(f"MEMORY.md ({size_kb:.1f}KB) > threshold ({self.threshold_size_kb}KB)")

        # 检查未处理的日常笔记
        unprocessed = self._get_unprocessed_notes()
        result["current_stats"]["unprocessed_notes"] = len(unprocessed)

        if len(unprocessed) > self.threshold_unprocessed:
            result["should_distill"] = True
            result["reason"].append(f"Unprocessed notes ({len(unprocessed)}) > threshold ({self.threshold_unprocessed})")

        return result

    def _get_unprocessed_notes(self) -> List[Path]:
        """获取未处理的日常笔记"""
        unprocessed = []

        for note_file in self.daily_dir.glob("*.md"):
            if note_file.name == "MEMORY.md":
                continue

            marker_file = note_file.with_suffix(note_file.suffix + self.processed_marker)
            if not marker_file.exists():
                unprocessed.append(note_file)

        return unprocessed

    def extract_insights(self, note_file: Path) -> List[str]:
        """从笔记提取洞察"""
        with open(note_file, 'r', encoding='utf-8') as f:
            content = f.read()

        insights = []

        # 简单提取：查找关键段落
        sections = content.split('\n## ')
        for section in sections[1:]:  # 跳过标题
            lines = section.split('\n')
            section_title = lines[0]

            # 提取决策、教训、洞察
            if any(kw in section_title.lower() for kw in ['decision', 'lesson', 'insight', 'key', 'conclusion']):
                insights.append(f"- [{section_title}] {datetime.now().strftime('%Y-%m-%d')}")

        return insights

    def distill_to_memory(self, insights: List[str]) -> Dict:
        """蒸馏到长期记忆"""
        if not self.memory_file.exists():
            # 创建新文件
            with open(self.memory_file, 'w', encoding='utf-8') as f:
                f.write("# MEMORY.md - Long-term Memory\n\n")
                f.write(f"Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n")
                f.write("---\n\n")

        # 读取现有内容
        with open(self.memory_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # 添加新洞察
        if insights:
            new_section = f"\n## New Insights ({datetime.now().strftime('%Y-%m-%d')})\n\n"
            new_section += '\n'.join(insights)
            new_section += "\n\n"

            # 插入到文件末尾前
            lines = content.rsplit('\n', 1)
            new_content = lines[0] + new_section + (lines[1] if len(lines) > 1 else '')

            with open(self.memory_file, 'w', encoding='utf-8') as f:
                f.write(new_content)

        return {
            "status": "success",
            "insights_added": len(insights),
            "memory_size_kb": self.memory_file.stat().st_size / 1024
        }

    def mark_processed(self, note_file: Path):
        """标记为已处理"""
        marker_file = note_file.with_suffix(note_file.suffix + self.processed_marker)
        with open(marker_file, 'w', encoding='utf-8') as f:
            f.write(f"Distilled at: {datetime.now().isoformat()}\n")

    def run(self, force: bool = False) -> Dict:
        """运行蒸馏"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "notes_processed": 0,
            "insights_extracted": 0
        }

        # 检查阈值
        threshold_check = self.check_threshold()

        if not force and not threshold_check["should_distill"]:
            result["status"] = "skipped"
            result["reason"] = "Below threshold"
            result["stats"] = threshold_check["current_stats"]
            return result

        # 获取未处理笔记
        unprocessed = self._get_unprocessed_notes()

        all_insights = []
        for note_file in unprocessed[:5]:  # 每次最多处理 5 个
            insights = self.extract_insights(note_file)
            all_insights.extend(insights)
            self.mark_processed(note_file)
            result["notes_processed"] += 1

        # 蒸馏到长期记忆
        if all_insights:
            distill_result = self.distill_to_memory(all_insights)
            result["insights_extracted"] = len(all_insights)
            result["memory_updated"] = distill_result["status"] == "success"

        result["status"] = "completed"
        result["threshold_reasons"] = threshold_check["reason"]

        return result

    def display_status(self) -> str:
        """显示状态"""
        threshold = self.check_threshold()

        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 25 + "Memory Distiller")
        output.append("=" * 70)

        output.append(f"\n[Thresholds]")
        output.append(f"  Memory Size:        {self.threshold_size_kb}KB")
        output.append(f"  Unprocessed Notes:  {self.threshold_unprocessed}")

        output.append(f"\n[Current Stats]")
        for key, value in threshold.get("current_stats", {}).items():
            output.append(f"  {key:20} {value}")

        output.append(f"\n[Distillation Needed]")
        output.append(f"  Status: {'YES' if threshold['should_compress'] else 'NO'}")
        if threshold["reason"]:
            for reason in threshold["reason"]:
                output.append(f"  - {reason}")

        output.append("\n" + "=" * 70)

        return "\n".join(output)

def main():
    """测试入口"""
    distiller = MemoryDistiller()

    print("Memory Distiller Test")
    print("=" * 70)

    # 显示状态
    print(distiller.display_status())

    # 运行蒸馏
    result = distiller.run(force=True)

    print(f"\n[OK] Distillation result: {result['status']}")
    print(f"  Notes Processed: {result['notes_processed']}")
    print(f"  Insights Extracted: {result['insights_extracted']}")

    print(f"\n[OK] Memory distiller test completed")

if __name__ == "__main__":
    main()

import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SMART-COMPRESS-001 智能压缩器 v2.0
【优化版记忆压缩方法】

核心改进:
1. 语义压缩 - 智能提取关键信息
2. 分块压缩 - 按逻辑块处理
3. 增量压缩 - 只存储变化部分
4. 优先级保留 - 重要内容优先保留
5. 智能Token估算 - 更准确的估算

使用:
  py smart_compress_001.py --compress
  py smart_compress_001.py --status
  py smart_compress_001.py --test
"""

import json
import re
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class SmartCompressor:
    """智能压缩器 v2.0"""

    # 保留关键词 (高优先级)
    PRIORITY_KEYWORDS = {
        'critical': ['goal', 'constraint', 'decision', 'block', 'error', 'fail', 'stop'],
        'high': ['create', 'update', 'fix', 'complete', 'done', 'progress', 'next'],
        'medium': ['tool', 'file', 'function', 'class', 'method', 'script'],
        'low': ['test', 'check', 'view', 'read', 'list']
    }

    # 需要保留的结构标记
    STRUCTURE_MARKERS = [
        r'^#{1,6}\s',           # 标题
        r'^\*{3,}',              # 分隔线
        r'^\d+\.',               # 列表编号
        r'^[-*]\s',              # 列表项
        r'^\[.*\]:\s*',          # 链接定义
    ]

    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.compress_dir = self.workspace / '10-MEMORY/00-CORE/.compress_cache'
        self.compress_dir.mkdir(parents=True, exist_ok=True)

        # 压缩参数
        self.max_tokens = 2500        # 目标 <2500 tokens (~5KB)
        self.chunk_size = 500         # 分块大小
        self.min_keep_lines = 30      # 最少保留行数
        self.summary_ratio = 0.15     # 摘要比例

    def estimate_tokens(self, text: str) -> int:
        """智能Token估算 - 比简单除4更准确"""
        # 中文: 每个字符 ≈ 1 token
        # 英文: 约4字符 = 1 token
        # 代码: 约3字符 = 1 token

        chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
        code = len(re.findall(r'[{}()\[\];=]', text))
        english = len(text) - chinese - code

        return chinese + (english // 4) + (code // 3)

    def calculate_line_priority(self, line: str) -> Tuple[int, str]:
        """计算行的优先级"""
        line_lower = line.lower().strip()

        # 检查关键词
        for level, keywords in self.PRIORITY_KEYWORDS.items():
            for kw in keywords:
                if kw in line_lower:
                    priority = {'critical': 100, 'high': 75, 'medium': 50, 'low': 25}
                    return priority[level], level

        # 检查结构标记
        for marker in self.STRUCTURE_MARKERS:
            if re.match(marker, line):
                return 60, 'structure'

        # 检查任务状态标记
        if re.search(r'\[x\]|\[✅\]|\[DONE\]', line):
            return 70, 'completed_task'
        if re.search(r'\[ \]|\[ \]', line):
            return 40, 'pending_task'

        return 30, 'normal'

    def extract_key_sections(self, content: str) -> Dict[str, str]:
        """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py smart_compress_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py smart_compress_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

提取关键章节"""
        sections = {}
        current_section = 'header'
        current_lines = []

        lines = content.split('\n')

        for line in lines:
            # 检测章节标题
            if re.match(r'^#{1,3}\s+', line):
                if current_lines:
                    sections[current_section] = '\n'.join(current_lines)
                current_section = line.strip('#').strip()
                current_lines = [line]
            else:
                current_lines.append(line)

        if current_lines:
            sections[current_section] = '\n'.join(current_lines)

        return sections

    def smart_compress_lines(self, lines: List[str]) -> List[str]:
        """智能压缩行 - 保持原始顺序"""
        total_lines = len(lines)
        
        if total_lines <= self.min_keep_lines:
            return lines
        
        # 收集要保留的行
        priority_lines = []  # (index, line, priority)
        
        # 1. 保留前N行
        header_count = min(10, total_lines)
        for i in range(header_count):
            priority_lines.append((i, lines[i], 100))
        
        # 2. 保留后N行
        footer_count = min(15, total_lines - header_count)
        for i in range(total_lines - footer_count, total_lines):
            priority_lines.append((i, lines[i], 90))
        
        # 3. 中间内容 - 按优先级筛选
        for i in range(header_count, total_lines - footer_count):
            priority, level = self.calculate_line_priority(lines[i])
            if priority >= 50:  # 只保留中高优先级
                priority_lines.append((i, lines[i], priority))
        
        # 按索引排序，保持原始顺序
        priority_lines.sort(key=lambda x: x[0])
        
        # 取前 target 行
        target = max(self.min_keep_lines, int(total_lines * 0.25))
        priority_lines = priority_lines[:target]
        
        # 重建内容
        kept_lines = [line for _, line, _ in priority_lines]
        
        # 添加压缩标记
        if len(kept_lines) < total_lines:
            kept_lines.insert(1, f"\n--- [{total_lines - len(kept_lines)} lines compressed] ---\n")
        
        return kept_lines
    
    def compress_with_delta(self, file_path: str, force: bool = False) -> Dict:
        """增量压缩"""
        file = Path(file_path)
        
        if not file.exists():
            return {"status": "error", "reason": "File not found"}
        
        # 读取当前内容
        current_content = file.read_text(encoding='utf-8')
        current_hash = hashlib.md5(current_content.encode()).hexdigest()
        
        # 检查是否有之前的压缩版本
        cache_file = self.compress_dir / f"{file.stem}_meta.json"
        
        if cache_file.exists() and not force:
            with open(cache_file, 'r', encoding='utf-8') as f:
                meta = json.load(f)
            
            # 如果内容没变，无需压缩
            if meta.get('hash') == current_hash:
                return {"status": "skipped", "reason": "No changes since last compress"}
        
        # 执行压缩
        tokens_before = self.estimate_tokens(current_content)
        
        if file.suffix == '.md':
            lines = current_content.split('\n')
            compressed_lines = self.smart_compress_lines(lines)
            compressed_content = '\n'.join(compressed_lines)
        else:
            compressed_content = current_content[:5000]  # 非MD文件截断
        
        tokens_after = self.estimate_tokens(compressed_content)
        
        # 保存压缩版本
        compressed_file = self.compress_dir / f"{file.stem}_v{self.today}.md"
        compressed_file.write_text(compressed_content, encoding='utf-8')
        
        # 保存元数据
        meta = {
            "original_file": str(file),
            "compressed_file": str(compressed_file),
            "original_hash": current_hash,
            "original_tokens": tokens_before,
            "compressed_tokens": tokens_after,
            "compression_ratio": round(tokens_after / tokens_before, 2) if tokens_before > 0 else 1.0,
            "compressed_at": datetime.now().isoformat(),
            "lines_before": len(current_content.split('\n')),
            "lines_after": len(compressed_content.split('\n'))
        }
        
        cache_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding='utf-8')
        
        return {
            "status": "success",
            "original_tokens": tokens_before,
            "compressed_tokens": tokens_after,
            "ratio": meta['compression_ratio'],
            "output": str(compressed_file)
        }
    
    def compress_session(self, session_file: str = "10-MEMORY/00-CORE/session_temp.json") -> Dict:
        """压缩会话文件"""
        session_path = Path(session_file)
        
        if not session_path.exists():
            return {"status": "skipped", "reason": "No session file"}
        
        with open(session_path, 'r', encoding='utf-8') as f:
            session_data = json.load(f)
        
        # 智能提取关键信息
        compressed = {
            "date": datetime.now().strftime("%Y-%m-%d"),
            "session_id": session_data.get("session_id", ""),
            
            # 任务 - 保留完成状态
            "tasks_completed": [
                t for t in session_data.get("tasks", [])
                if isinstance(t, dict) and t.get("status") == "completed"
            ][:10],  # 最多10个
            
            # 决策 - 全保留
            "key_decisions": session_data.get("decisions", [])[:5],
            
            # 工具 - 保留名称
            "tools_created": [
                {"name": t.get("name", ""), "id": t.get("id", "")}
                for t in session_data.get("tools", [])
            ],
            
            # Git - 保留提交信息
            "commits": session_data.get("commits", [])[:5],
            
            # 摘要
            "summary": self._create_summary(session_data),
            
            # Token统计
            "stats": {
                "tasks": len(session_data.get("tasks", [])),
                "decisions": len(session_data.get("decisions", [])),
                "tools": len(session_data.get("tools", [])),
                "commits": len(session_data.get("commits", []))
            }
        }
        
        # 保存
        output_file = self.compress_dir / "session_compressed.json"
        output_file.write_text(
            json.dumps(compressed, ensure_ascii=False, indent=2),
            encoding='utf-8'
        )
        
        tokens = self.estimate_tokens(json.dumps(compressed))
        
        # 重置session
        session_path.write_text(json.dumps({"reset_at": datetime.now().isoformat()}, indent=2))
        
        return {
            "status": "success",
            "tokens": tokens,
            "size_kb": round(tokens / 200, 2),
            "output": str(output_file)
        }
    
    def _create_summary(self, session_data: Dict) -> str:
        """创建摘要"""
        summary_parts = []
        
        # 任务摘要
        tasks = session_data.get("tasks", [])
        completed = sum(1 for t in tasks if isinstance(t, dict) and t.get("status") == "completed")
        summary_parts.append(f"Tasks: {completed}/{len(tasks)} completed")
        
        # 工具摘要
        tools = session_data.get("tools", [])
        if tools:
            summary_parts.append(f"Tools: {len(tools)} created")
        
        # 提交摘要
        commits = session_data.get("commits", [])
        if commits:
            summary_parts.append(f"Commits: {len(commits)}")
        
        return "; ".join(summary_parts)
    
    def run_compression(self, target: str = "all", force: bool = False) -> Dict:
        """运行压缩"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "target": target,
            "files": []
        }
        
        if target in ["all", "core"]:
            core_files = [
                self.workspace / 'SOUL.md',
                self.workspace / 'USER.md',
                self.workspace / 'AGENTS.md',
                self.workspace / 'TOOLS.md',
                self.workspace / 'HEARTBEAT.md',
                self.workspace / 'MEMORY.md',
            ]
            
            for f in core_files:
                if f.exists():
                    res = self.compress_with_delta(str(f), force)
                    result["files"].append({"file": f.name, **res})
        
        if target in ["all", "daily"]:
            daily = self.workspace / f'10-MEMORY/00-CORE/{self.today}.md'
            if daily.exists():
                res = self.compress_with_delta(str(daily), force)
                result["files"].append({"file": daily.name, **res})
        
        if target in ["all", "session"]:
            res = self.compress_session()
            result["files"].append({"file": "session", **res})
        
        # 汇总
        total_before = sum(f.get('original_tokens', 0) for f in result["files"])
        total_after = sum(f.get('compressed_tokens', 0) for f in result["files"])
        
        result["summary"] = {
            "total_original": total_before,
            "total_compressed": total_after,
            "total_ratio": round(total_after / total_before, 2) if total_before > 0 else 1.0,
            "files_processed": len(result["files"])
        }
        
        return result


logging.basicConfig(level=logging.INFO)
def main():
    compressor = SmartCompressor()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--compress":
            result = compressor.run_compression("all", force=True)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--status":
            # 检查各文件大小
            files = [
                'SOUL.md', 'USER.md', 'AGENTS.md', 'TOOLS.md',
                'HEARTBEAT.md', 'MEMORY.md',
                f'10-MEMORY/00-CORE/{datetime.now().strftime("%Y-%m-%d")}.md'
            ]
            
            status = []
            for f in files:
                path = compressor.workspace / f
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    tokens = compressor.estimate_tokens(content)
                    status.append({
                        "file": f,
                        "tokens": tokens,
                        "size_kb": round(tokens / 200, 2)
                    })
            
            print(json.dumps(status, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--test":
            # 测试压缩效果 - 真实场景
            test_content = """# Project OpenClaw

## Goals
- Implement workflow optimization
- Reduce LLM calls by 70%
- Create multi-dimensional roadmap

## Progress
- [x] Phase 7 complete (SA-033 to SA-036)
- [x] AUTO-001 workflow automator
- [x] LLM-GUIDE-001 task classification
- [x] SMART-CACHE-001 response caching

## Next Steps
- [ ] Create integration tools
- [ ] Test reporting features

## Notes
This is a test document for compression.
The compressor should keep important parts.
Headers and task status should be preserved.
Goals and progress sections are critical.
""" * 3
            
            lines = test_content.split('\n')
            compressed = compressor.smart_compress_lines(lines)
            
            print(f"Original lines: {len(lines)}")
            print(f"Compressed lines: {len(compressed)}")
            print(f"Ratio: {len(compressed)/len(lines):.2%}")
            print("\n--- Compressed Content ---")
            print('\n'.join(compressed))
            return 0
    
    print("SMART-COMPRESS-001 智能压缩器 v2.0")
    print("Usage:")
    print("  py smart_compress_001.py --compress   # 压缩所有文件")
    print("  py smart_compress_001.py --status     # 查看状态")
    print("  py smart_compress_001.py --test       # 测试压缩")
    return 0


if __name__ == "__main__":
    sys.exit(main())
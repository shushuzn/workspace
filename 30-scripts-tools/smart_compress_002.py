#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SMART-COMPRESS-002 超级压缩器 v3.0
【终极记忆压缩方案】

核心创新:
1. 结构感知压缩 - 理解Markdown结构
2. 语义摘要生成 - 智能提取核心信息  
3. 多级压缩 - 支持不同压缩级别
4. 自适应阈值 - 根据内容类型自动调整
5. 对话模式 - 专为会话压缩优化

使用:
  py smart_compress_002.py --compress [level]
  py smart_compress_002.py --session
  py smart_compress_002.py --analyze
"""

import json
import re
import hashlib
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict


class SuperCompressor:
    """超级压缩器 v3.0"""
    
    # Markdown结构标记
    STRUCT_PATTERNS = {
        'h1': r'^#\s+',
        'h2': r'^##\s+',
        'h3': r'^###\s+',
        'list_bullet': r'^[-*]\s+',
        'list_number': r'^\d+\.\s+',
        'code_block': r'^```',
        'table': r'^\|',
        'blockquote': r'^>\s+',
        'task_done': r'^[-*]\s+\[x\]',
        'task_pending': r'^[-*]\s+\[ \]',
    }
    
    # 优先级关键词
    PRIORITY_WORDS = {
        'critical': 100,  # goal, decision, block, error, stop, critical
        'important': 80,  # done, complete, fix, create, update
        'normal': 50,      # tool, file, function, method
        'context': 30,     # test, check, view, list
    }
    
    KEYWORDS = {
        'critical': ['goal', 'constraint', 'decision', 'block', 'error', 'fail', 'stop', 'critical', 'must', 'required'],
        'important': ['done', 'complete', 'fix', 'create', 'update', 'progress', 'next', 'achieved', 'success'],
        'normal': ['tool', 'file', 'function', 'class', 'method', 'script', 'implementation', 'feature'],
        'context': ['test', 'check', 'view', 'read', 'list', 'example', 'note']
    }
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.cache_dir = self.workspace / '13-memory/.compress_cache'
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 压缩级别配置
        self.LEVELS = {
            'light': {'ratio': 0.7, 'min_lines': 50, 'keep_struct': True},
            'normal': {'ratio': 0.5, 'min_lines': 40, 'keep_struct': True},
            'aggressive': {'ratio': 0.3, 'min_lines': 30, 'keep_struct': False},
            'extreme': {'ratio': 0.15, 'min_lines': 20, 'keep_struct': False},
        }
    
    # ========== 核心方法 ==========
    
    def analyze_content(self, content: str) -> Dict:
        """分析内容结构"""
        lines = content.split('\n')
        
        analysis = {
            'total_lines': len(lines),
            'total_chars': len(content),
            'tokens': self._estimate_tokens(content),
            'structure': self._analyze_structure(lines),
            'priority_map': self._build_priority_map(lines),
            'sections': self._extract_sections(lines),
        }
        
        return analysis
    
    def _estimate_tokens(self, text: str) -> int:
        """智能Token估算"""
        chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
        code = len(re.findall(r'[{}()\[\];=]', text))
        english = len(text) - chinese - code
        return chinese + (english // 4) + (code // 3)
    
    def _analyze_structure(self, lines: List[str]) -> Dict:
        """分析Markdown结构"""
        structure = defaultdict(int)
        
        for line in lines:
            for name, pattern in self.STRUCT_PATTERNS.items():
                if re.match(pattern, line):
                    structure[name] += 1
                    break
        
        return dict(structure)
    
    def _build_priority_map(self, lines: List[str]) -> Dict[int, int]:
        """构建行优先级映射"""
        priority_map = {}
        
        for i, line in enumerate(lines):
            score = 50  # 默认优先级
            
            # 位置权重
            if i < 5:
                score += 30
            elif i < 10:
                score += 15
            elif i > len(lines) - 5:
                score += 20
            
            # 结构权重
            for name, pattern in self.STRUCT_PATTERNS.items():
                if re.match(pattern, line):
                    if name in ['h1', 'h2', 'h3']:
                        score += 25
                    elif name in ['task_done', 'task_pending']:
                        score += 15
                    break
            
            # 关键词权重
            line_lower = line.lower()
            for level, keywords in self.KEYWORDS.items():
                for kw in keywords:
                    if kw in line_lower:
                        score += self.PRIORITY_WORDS[level]
                        break
            
            priority_map[i] = min(score, 150)  # 上限150
        
        return priority_map
    
    def _extract_sections(self, lines: List[str]) -> List[Dict]:
        """提取章节"""
        sections = []
        current = {'start': 0, 'title': 'header', 'level': 0}
        
        for i, line in enumerate(lines):
            # 检测标题
            h_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if h_match:
                if current['title']:
                    current['end'] = i
                    sections.append(current)
                level = len(h_match.group(1))
                current = {'start': i, 'title': h_match.group(2), 'level': level, 'end': len(lines)}
        
        if current.get('title'):
            current['end'] = len(lines)
            sections.append(current)
        
        return sections
    
    # ========== 压缩方法 ==========
    
    def compress_structural(self, content: str, level: str = 'normal') -> str:
        """结构感知压缩"""
        lines = content.split('\n')
        config = self.LEVELS.get(level, self.LEVELS['normal'])
        
        analysis = self.analyze_content(content)
        priority_map = analysis['priority_map']
        
        # 计算目标行数
        target_lines = max(config['min_lines'], int(len(lines) * config['ratio']))
        
        # 选择要保留的行
        # 1. 保留所有标题
        # 2. 保留所有任务项
        # 3. 按优先级保留其他行
        
        keep_indices = set()
        
        # 策略: 保留标题行
        for i, line in enumerate(lines):
            if re.match(r'^#{1,3}\s+', line):
                keep_indices.add(i)
        
        # 策略: 保留任务行
        for i, line in enumerate(lines):
            if re.match(r'^[-*]\s+\[', line):
                keep_indices.add(i)
        
        # 策略: 按优先级填充剩余
        sorted_by_priority = sorted(priority_map.items(), key=lambda x: x[1], reverse=True)
        
        for idx, score in sorted_by_priority:
            if len(keep_indices) >= target_lines:
                break
            keep_indices.add(idx)
        
        # 保持顺序并重建
        keep_indices = sorted(keep_indices)
        kept_lines = [lines[i] for i in keep_indices]
        
        # 添加压缩标记
        if len(kept_lines) < len(lines):
            kept_lines.insert(1, f"\n> [{len(lines) - len(kept_lines)} lines compressed | {level} mode]\n")
        
        return '\n'.join(kept_lines)
    
    def compress_semantic(self, content: str) -> str:
        """语义摘要压缩 - 提取核心信息"""
        lines = content.split('\n')
        analysis = self.analyze_content(content)
        sections = analysis['sections']
        
        result_lines = []
        
        # 保留头部
        header_end = min(5, len(lines))
        result_lines.extend(lines[:header_end])
        result_lines.append("")
        
        # 为每个章节生成摘要
        for section in sections[1:]:  # 跳过header
            title_line = lines[section['start']]
            result_lines.append(title_line)
            
            # 提取该章节中的关键行
            section_lines = lines[section['start']:section['end']]
            key_lines = self._extract_key_lines(section_lines, max(3, len(section_lines) // 5))
            result_lines.extend(key_lines)
            result_lines.append("")
        
        # 添加压缩标记
        result_lines.insert(1, f"\n> [Compressed to {len(result_lines)} lines | Semantic mode]\n")
        
        return '\n'.join(result_lines)
    
    def _extract_key_lines(self, lines: List[str], max_lines: int) -> List[str]:
        """从一组行中提取关键行"""
        if len(lines) <= max_lines:
            return lines
        
        priority_map = {}
        for i, line in enumerate(lines):
            score = 30
            line_lower = line.lower()
            
            for level, keywords in self.KEYWORDS.items():
                for kw in keywords:
                    if kw in line_lower:
                        score += self.PRIORITY_WORDS[level]
                        break
            
            # 保留结构行
            for name, pattern in self.STRUCT_PATTERNS.items():
                if re.match(pattern, lines[i]):
                    score += 15
                    break
            
            priority_map[i] = score
        
        # 选择高分行
        sorted_lines = sorted(priority_map.items(), key=lambda x: x[1], reverse=True)
        indices = [idx for idx, _ in sorted_lines[:max_lines]]
        indices.sort()
        
        return [lines[i] for i in indices]
    
    def compress_session(self, session_data: Dict) -> str:
        """会话模式压缩 - 专为会话优化"""
        lines = []
        
        # 头部
        lines.append(f"# Session Compression - {session_data.get('date', '')}")
        lines.append(f"**Session ID:** {session_data.get('session_id', 'N/A')}")
        lines.append("")
        
        # 任务摘要
        tasks = session_data.get('tasks', [])
        completed = [t for t in tasks if isinstance(t, dict) and t.get('status') == 'completed']
        pending = [t for t in tasks if isinstance(t, dict) and t.get('status') != 'completed']
        
        lines.append("## Tasks")
        lines.append(f"- **Completed:** {len(completed)}")
        lines.append(f"- **Pending:** {len(pending)}")
        
        # 列出完成的关键任务
        if completed:
            lines.append("")
            lines.append("### Completed")
            for task in completed[:5]:  # 最多5个
                lines.append(f"- [x] {task.get('name', task.get('id', 'Task'))}")
        
        # 关键决策
        decisions = session_data.get('decisions', [])
        if decisions:
            lines.append("")
            lines.append("## Key Decisions")
            for decision in decisions[:3]:
                lines.append(f"- {decision}")
        
        # 工具创建
        tools = session_data.get('tools', [])
        if tools:
            lines.append("")
            lines.append("## Tools Created")
            for tool in tools[:5]:
                name = tool.get('name', tool.get('id', 'Tool'))
                lines.append(f"- {name}")
        
        # Git提交
        commits = session_data.get('commits', [])
        if commits:
            lines.append("")
            lines.append("## Commits")
            for commit in commits[:3]:
                msg = commit.get('message', '')[:50]
                lines.append(f"- {msg}")
        
        # 原始摘要
        if session_data.get('summary'):
            lines.append("")
            lines.append("## Summary")
            lines.append(session_data['summary'])
        
        return '\n'.join(lines)
    
    def compress_multi_level(self, content: str, target_kb: float = 5.0) -> str:
        """多级压缩 - 渐进式达到目标大小"""
        levels = ['light', 'normal', 'aggressive', 'extreme']
        
        for level in levels:
            compressed = self.compress_structural(content, level)
            tokens = self._estimate_tokens(compressed)
            size_kb = tokens / 200
            
            if size_kb <= target_kb:
                return compressed
        
        # 如果还不够，尝试语义压缩
        return self.compress_semantic(content)
    
    # ========== 批量压缩 ==========
    
    def compress_file(self, file_path: str, method: str = 'structural', level: str = 'normal') -> Dict:
        """压缩单个文件"""
        file = Path(file_path)
        
        if not file.exists():
            return {"status": "error", "reason": "File not found"}
        
        original = file.read_text(encoding='utf-8')
        original_hash = hashlib.md5(original.encode()).hexdigest()
        original_tokens = self._estimate_tokens(original)
        
        # 检查缓存
        cache_file = self.cache_dir / f"{file.stem}_{method}_{level}.json"
        
        if cache_file.exists():
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
            if cached.get('hash') == original_hash:
                return {"status": "cached", "tokens": cached['compressed_tokens']}
        
        # 执行压缩
        if method == 'structural':
            compressed = self.compress_structural(original, level)
        elif method == 'semantic':
            compressed = self.compress_semantic(original)
        elif method == 'multi':
            compressed = self.compress_multi_level(original)
        else:
            compressed = original
        
        compressed_tokens = self._estimate_tokens(compressed)
        
        # 保存
        output_file = self.cache_dir / f"{file.stem}_compressed.md"
        output_file.write_text(compressed, encoding='utf-8')
        
        # 保存缓存元数据
        cache_data = {
            "hash": original_hash,
            "method": method,
            "level": level,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "compressed_at": datetime.now().isoformat()
        }
        cache_file.write_text(json.dumps(cache_data, ensure_ascii=False, indent=2))
        
        return {
            "status": "success",
            "method": method,
            "level": level,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "ratio": round(compressed_tokens / original_tokens, 2) if original_tokens else 1,
            "output": str(output_file)
        }
    
    def run(self, target: str = 'all', method: str = 'structural', level: str = 'normal') -> Dict:
        """运行压缩"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "method": method,
            "level": level,
            "files": []
        }
        
        # 核心文件
        core_files = [
            'SOUL.md', 'USER.md', 'AGENTS.md', 'TOOLS.md',
            'HEARTBEAT.md', 'MEMORY.md',
        ]
        
        for f in core_files:
            path = self.workspace / f
            if path.exists() and target in ['all', 'core']:
                res = self.compress_file(str(path), method, level)
                result["files"].append({"file": f, **res})
        
        # 今日笔记
        if target in ['all', 'daily']:
            daily = self.workspace / f'13-memory/{datetime.now().strftime("%Y-%m-%d")}.md'
            if daily.exists():
                res = self.compress_file(str(daily), method, level)
                result["files"].append({"file": daily.name, **res})
        
        # 汇总
        total_orig = sum(f.get('original_tokens', 0) for f in result["files"])
        total_comp = sum(f.get('compressed_tokens', 0) for f in result["files"])
        
        result["summary"] = {
            "original_tokens": total_orig,
            "compressed_tokens": total_comp,
            "total_ratio": round(total_comp / total_orig, 2) if total_orig else 1,
            "files_processed": len(result["files"])
        }
        
        return result


def main():
    compressor = SuperCompressor()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--compress":
            level = sys.argv[2] if len(sys.argv) > 2 else "normal"
            result = compressor.run("all", "structural", level)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--semantic":
            result = compressor.run("all", "semantic", "normal")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--multi":
            result = compressor.run("all", "multi", "normal")
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--analyze":
            # 分析核心文件
            files = ['SOUL.md', 'USER.md', 'AGENTS.md']
            for f in files:
                path = compressor.workspace / f
                if path.exists():
                    content = path.read_text(encoding='utf-8')
                    analysis = compressor.analyze_content(content)
                    print(f"\n=== {f} ===")
                    print(f"Lines: {analysis['total_lines']}")
                    print(f"Tokens: {analysis['tokens']}")
                    print(f"Structure: {analysis['structure']}")
            return 0
        
        if cmd == "--session":
            # 测试会话压缩
            test_session = {
                "session_id": "test-001",
                "date": datetime.now().strftime("%Y-%m-%d"),
                "tasks": [
                    {"name": "Create tool", "status": "completed"},
                    {"name": "Fix bug", "status": "completed"},
                    {"name": "Update docs", "status": "pending"},
                ],
                "decisions": ["Use JSON format", "Implement caching"],
                "tools": [{"name": "TestTool", "id": "test-001"}],
                "commits": [{"message": "Add feature X"}],
                "summary": "Completed 2 tasks, created 1 tool"
            }
            result = compressor.compress_session(test_session)
            print(result)
            return 0
    
    print("SMART-COMPRESS-002 超级压缩器 v3.0")
    print("Usage:")
    print("  py smart_compress_002.py --compress [level]    # 结构压缩")
    print("  py smart_compress_002.py --semantic           # 语义压缩")
    print("  py smart_compress_002.py --multi             # 多级压缩")
    print("  py smart_compress_002.py --analyze            # 分析文件结构")
    print("  py smart_compress_002.py --session            # 测试会话压缩")
    return 0


if __name__ == "__main__":
    sys.exit(main())
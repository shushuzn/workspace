import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PROMPT-OPTIMIZER-001 提示词优化器
【简化提示词，减少token消耗】

功能:
  - 简化冗长提示词
  - 提取核心指令
  - 压缩重复内容
  - 标准化格式

使用:
  py prompt_optimizer_001.py --optimize "long prompt..."
  py prompt_optimizer_001.py --file <file>
  py prompt_optimizer_001.py --test
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List


class PromptOptimizer:
    """提示词优化器"""
    
    # 常见冗余模式
    REDUNDANT_PATTERNS = [
        (r'以下.*请注意[:：]\s*', ''),
        (r'请务必.*确保[:：]\s*', ''),
        (r'请先.*然后.*最后', '请按顺序执行'),
        (r'认真.*仔细.*详细', '仔细'),
        (r'\s+', ' '),  # 多余空格
    ]
    
    # 可以简化的模板
    TEMPLATE_SIMPLIFICATIONS = {
        "请创建一个": "创建",
        "请帮我创建": "创建",
        "我需要你": "",
        "你是一个": "作为",
        "请执行": "执行",
        "请完成": "完成",
        "请你": "",
        "麻烦你": "",
    }
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        
    def optimize(self, prompt: str) -> str:
        """优化提示词"""
        lines = prompt.split('\n')
        result_lines = []
        
        for line in lines:
            result = line
            
            # 1. 移除冗余模式
            for pattern, replacement in self.REDUNDANT_PATTERNS:
                result = re.sub(pattern, replacement, result)
            
            # 2. 简化模板
            for old, new in self.TEMPLATE_SIMPLIFICATIONS.items():
                result = result.replace(old, new)
            
            # 跳过完全空的行
            if result.strip():
                result_lines.append(result)
        
        # 3. 移除重复行
        result_lines = self._remove_duplicates_lines(result_lines)
        
        return '\n'.join(result_lines).strip()
    
    def _remove_duplicates_lines(self, lines: List[str]) -> List[str]:
        """移除重复行"""
        seen = set()
        result = []
        
        for line in lines:
            line_stripped = line.strip()
            if line_stripped and line_stripped not in seen:
                result.append(line)
                seen.add(line_stripped)
            elif not line_stripped:
                # 保留空行
                if result and result[-1].strip():
                    result.append(line)
        
        return result
    
    # _remove_duplicates_lines 已在 optimize 中实现
    
    def extract_core_instructions(self, prompt: str) -> List[str]:
        """提取核心指令"""
        instructions = []
        
        # 按行分析
        for line in prompt.split('\n'):
            line = line.strip()
            if not line:
                continue
            
            # 跳过注释和说明
            if line.startswith('#') or line.startswith('//'):
                continue
            
            # 提取动词开头的指令
            if re.match(r'^(创建|执行|完成|生成|读取|写入|计算|分析|优化|检查|验证|实现)\s+', line):
                instructions.append(line)
            elif re.match(r'^(create|execute|complete|generate|read|write|calculate|analyze|optimize|check|implement)\s+', line, re.I):
                instructions.append(line)
        
        return instructions
    
    def estimate_tokens(self, text: str) -> int:
        """估算token数"""
        chinese = len(re.findall(r'[\u4e00-\u9fff]', text))
        code = len(re.findall(r'[{}()\[\];=]', text))
        english = len(text) - chinese - code
        return chinese + (english // 4) + (code // 3)
    
    def optimize_file(self, file_path: str) -> Dict:
        """优化文件中的提示词"""
        path = Path(file_path)
        
        if not path.exists():
            return {"status": "error", "reason": "File not found"}
        
        original = path.read_text(encoding='utf-8')
        tokens_before = self.estimate_tokens(original)
        
        optimized = self.optimize(original)
        tokens_after = self.estimate_tokens(optimized)
        
        # 保存优化版本
        output_path = path.parent / f"{path.stem}_optimized{path.suffix}"
        output_path.write_text(optimized, encoding='utf-8')
        
        return {
            "status": "success",
            "original_tokens": tokens_before,
            "optimized_tokens": tokens_after,
            "saved": tokens_before - tokens_after,
            "saved_ratio": round((tokens_before - tokens_after) / tokens_before, 2) if tokens_before else 0,
            "output": str(output_path)
        }


logging.basicConfig(level=logging.INFO)
def main():
    optimizer = PromptOptimizer()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--optimize":
            prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            if prompt:
                result = optimizer.optimize(prompt)
                print(result)
            else:
                print("Usage: --optimize <prompt>")
            return 0
        
        if cmd == "--file":
            path = sys.argv[2] if len(sys.argv) > 2 else ""
            if path:
                result = optimizer.optimize_file(path)
                print(json.dumps(result, ensure_ascii=False, indent=2))
            else:
                print("Usage: --file <file_path>")
            return 0
        
        if cmd == "--extract":
            prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            if prompt:
                instructions = optimizer.extract_core_instructions(prompt)
                print(json.dumps(instructions, ensure_ascii=False, indent=2))
            return 0
        
        if cmd == "--test":
            test_prompt = """
# Test Prompt

请务必认真仔细阅读以下内容。
我需要你帮我创建一个文件。
请先读取数据，然后进行处理，最后保存结果。

请注意以下事项：
1. 认真执行
2. 仔细检查
3. 详细记录

这是一段重复的内容。
这是一段重复的内容。
这是一段重复的内容。
"""
            print("=== Original ===")
            print(test_prompt)
            print("\n=== Optimized ===")
            result = optimizer.optimize(test_prompt)
            print(result)
            
            before = optimizer.estimate_tokens(test_prompt)
            after = optimizer.estimate_tokens(result)
            print(f"\nTokens: {before} -> {after} (saved {before - after})")
            return 0
    
    print("PROMPT-OPTIMIZER-001 Prompt Optimizer")
    print("Usage:")
    print("  py prompt_optimizer_001.py --optimize <prompt>")
    print("  py prompt_optimizer_001.py --file <file>")
    print("  py prompt_optimizer_001.py --extract <prompt>")
    print("  py prompt_optimizer_001.py --test")
    return 0


if __name__ == "__main__":
    sys.exit(main())
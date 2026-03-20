#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PROMPT-OPTIMIZER-001 Prompt Optimization Tool
【Prompt优化器】

功能:
  - 简化冗长prompts
  - 提取关键信息
  - 合并重复请求
  - 生成结构化prompt
"""
import json
import sys
import re
from pathlib import Path
from datetime import datetime


PROMPT_DIR = Path("60-DATA/prompt_optimizer_001")
PROMPT_TEMPLATES = PROMPT_DIR / "templates.json"
PROMPT_HISTORY = PROMPT_DIR / "history.json"


class PromptOptimizer:
    """Prompt优化器"""
    
    def __init__(self):
        self.dir = PROMPT_DIR
        self.dir.mkdir(parents=True, exist_ok=True)
        
        self.templates_file = PROMPT_TEMPLATES
        self.history_file = PROMPT_HISTORY
        
        self._ensure_files()
    
    def _ensure_files(self):
        if not self.templates_file.exists():
            default_templates = {
                "code_review": "Review this code for bugs, performance issues, and best practices:\n```\n{code}\n```",
                "debug": "Find and fix the bug in this code:\n```\n{code}\n```\nError: {error}",
                "explain": "Explain this code in simple terms:\n```\n{code}\n```",
                "optimize": "Optimize this code for performance:\n```\n{code}\n```",
                "test": "Write unit tests for:\n```\n{code}\n```",
                "document": "Generate documentation for:\n```\n{code}\n```"
            }
            with open(self.templates_file, "w", encoding="utf-8") as f:
                json.dump(default_templates, f, ensure_ascii=False, indent=2)
    
    def simplify(self, prompt: str) -> dict:
        """简化prompt"""
        # 移除冗余词
        redundant = ["请", "能不能", "帮我", "能不能帮我", "请问", "麻烦", "非常感谢", "谢谢"]
        simplified = prompt
        
        for word in redundant:
            simplified = simplified.replace(word, "")
        
        # 移除多余空格
        simplified = re.sub(r'\s+', ' ', simplified).strip()
        
        # 提取关键指令
        instructions = []
        if "写" in prompt or "创建" in prompt or "生成" in prompt:
            instructions.append("CREATE")
        if "修改" in prompt or "改" in prompt:
            instructions.append("MODIFY")
        if "分析" in prompt or "检查" in prompt:
            instructions.append("ANALYZE")
        if "优化" in prompt:
            instructions.append("OPTIMIZE")
        if "解释" in prompt:
            instructions.append("EXPLAIN")
        
        return {
            "original": prompt,
            "simplified": simplified,
            "instructions": instructions,
            "word_count_reduction": f"{((len(prompt) - len(simplified)) / len(prompt) * 100):.1f}%"
        }
    
    def extract_code(self, prompt: str) -> dict:
        """提取代码块"""
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', prompt, re.DOTALL)
        
        return {
            "has_code": len(code_blocks) > 0,
            "code_count": len(code_blocks),
            "code_blocks": code_blocks[:3]
        }
    
    def merge_prompts(self, prompts: list) -> dict:
        """合并多个prompts"""
        if not prompts:
            return {"merged": "", "count": 0}
        
        # 按类型分组
        by_type = {}
        for p in prompts:
            p_lower = p.lower()
            if "review" in p_lower or "检查" in p_lower:
                by_type.setdefault("review", []).append(p)
            elif "test" in p_lower or "测试" in p_lower:
                by_type.setdefault("test", []).append(p)
            elif "fix" in p_lower or "修复" in p_lower:
                by_type.setdefault("fix", []).append(p)
            else:
                by_type.setdefault("other", []).append(p)
        
        # 合并同类
        merged = []
        for ptype, plist in by_type.items():
            if len(plist) == 1:
                merged.append(plist[0])
            else:
                combined = plist[0] + f"\n\nAlso: " + " | ".join(plist[1:])
                merged.append(combined)
        
        return {
            "original_count": len(prompts),
            "merged_count": len(merged),
            "merged": merged,
            "saved_calls": len(prompts) - len(merged)
        }
    
    def use_template(self, template_name: str, **kwargs) -> str:
        """使用模板"""
        with open(self.templates_file, "r", encoding="utf-8") as f:
            templates = json.load(f)
        
        if template_name not in templates:
            return f"Template '{template_name}' not found"
        
        template = templates[template_name]
        
        # 替换占位符
        for key, value in kwargs.items():
            template = template.replace(f"{{{key}}}", value)
        
        return template
    
    def save_to_history(self, original: str, optimized: str, method: str):
        """保存到历史"""
        history = []
        if self.history_file.exists():
            with open(self.history_file, "r", encoding="utf-8") as f:
                history = json.load(f)
        
        history.append({
            "original": original[:100],
            "optimized": optimized[:100],
            "method": method,
            "timestamp": datetime.now().isoformat()
        })
        
        history = history[-50:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def get_templates(self) -> dict:
        with open(self.templates_file, "r", encoding="utf-8") as f:
            return json.load(f)


def main():
    optimizer = PromptOptimizer()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--simplify":
            prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            if not prompt:
                return 1
            
            result = optimizer.simplify(prompt)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--extract":
            prompt = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            result = optimizer.extract_code(prompt)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--templates":
            templates = optimizer.get_templates()
            print(json.dumps(templates, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--use":
            # --use code_review code="def foo(): pass"
            if len(sys.argv) < 4:
                return 1
            
            template_name = sys.argv[2]
            code = sys.argv[3] if len(sys.argv) > 3 else ""
            
            result = optimizer.use_template(template_name, code=code)
            print(result)
            return 0
        
        if sys.argv[1] == "--merge":
            prompts = sys.argv[2:] if len(sys.argv) > 2 else []
            result = optimizer.merge_prompts(prompts)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("PROMPT-OPTIMIZER-001 Prompt Optimization Tool")
    print("Usage:")
    print("  py prompt_optimizer_001.py --simplify <prompt>    # Simplify prompt")
    print("  py prompt_optimizer_001.py --extract <prompt>     # Extract code blocks")
    print("  py prompt_optimizer_001.py --templates            # List templates")
    print("  py prompt_optimizer_001.py --use <name> <code>    # Use template")
    print("  py prompt_optimizer_001.py --merge <p1> <p2>...   # Merge prompts")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
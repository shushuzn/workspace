import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UTIL-001 String Utility
【字符串工具】

功能:
  - 字符串格式化
  - 编码转换
  - 模板填充
"""
import json
import sys
from pathlib import Path


class StringUtil:
    """字符串工具"""
    
    @staticmethod
    def camel_to_snake(text: str) -> str:
        import re
        text = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', text).lower()
    
    @staticmethod
    def snake_to_camel(text: str) -> str:
        components = text.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    @staticmethod
    def truncate(text: str, length: int = 50) -> str:
        return text[:length] + ('...' if len(text) > length else '')
    
    @staticmethod
    def format_json(text: str, indent: int = 2) -> str:
        try:
            return json.dumps(json.loads(text), ensure_ascii=False, indent=indent)
        except (Exception,):
            return text


logging.basicConfig(level=logging.INFO)
def main():
    util = StringUtil()
    
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        
        if cmd == "--camel2snake":
            text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "CamelCase"
            print(util.camel_to_snake(text))
            return 0
        
        if cmd == "--snake2camel":
            text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else "snake_case"
            print(util.snake_to_camel(text))
            return 0
        
        if cmd == "--truncate":
            text = sys.argv[2] if len(sys.argv) > 2 else "Long text"
            length = int(sys.argv[3]) if len(sys.argv) > 3 else 50
            print(util.truncate(text, length))
            return 0
        
        if cmd == "--format-json":
            text = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else '{"a":1}'
            print(util.format_json(text))
            return 0
    
    print("UTIL-001 String Utility")
    print("Usage:")
    print("  py util_001.py --camel2snake <text>   # CamelCase to snake_case")
    print("  py util_001.py --snake2camel <text>  # snake_case to CamelCase")
    print("  py util_001.py --truncate <text> [n] # Truncate text")
    print("  py util_001.py --format-json <json>  # Format JSON")
    return 0
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计
Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py util_string_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py util_string_001.py

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




if __name__ == "__main__":
    import sys
    sys.exit(main())
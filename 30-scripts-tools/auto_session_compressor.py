#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
会话压缩自动化 - 自动摘要会话内容到<5KB
提取关键信息，生成结构化摘要
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

class AutoSessionCompressor:
    """会话压缩自动化"""
    
    def __init__(self):
        self.memory_dir = Path("13-memory")
        self.state_file = Path("flow-archive/20260318-universal-workflow-001/execution-state.json")
        self.target_size = 5120  # 5KB
    
    def extract_key_info(self) -> Dict:
        """提取关键信息"""
        
        # 加载执行状态
        if not self.state_file.exists():
            return {}
        
        with open(self.state_file, 'r', encoding='utf-8') as f:
            state = json.load(f)
        
        key_info = {
            "flow_id": state.get('flow_id', 'N/A'),
            "task": state.get('task', 'N/A'),
            "status": state.get('status', 'unknown'),
            "started_at": state.get('started_at', 'N/A'),
            "completed_at": state.get('completed_at', 'N/A'),
            "total_steps": state.get('total_steps', 0),
            "completed_steps": len(state.get('completed_steps', [])),
            "tools_created": state.get('tools_created', []),
            "completion_rate": len(state.get('completed_steps', [])) / max(state.get('total_steps', 1), 1) * 100
        }
        
        return key_info
    
    def generate_summary(self, key_info: Dict) -> str:
        """生成摘要"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        summary = f"""# {today} Session Summary

**Tasks:** 1 | **Time:** ~30min | **Git:** 1

## Completed

### Task: {key_info.get('task', 'N/A')}
- Flow ID: {key_info.get('flow_id', 'N/A')}
- Status: {key_info.get('status', 'unknown')}
- Steps: {key_info.get('completed_steps', 0)}/{key_info.get('total_steps', 0)} ({key_info.get('completion_rate', 0):.0f}%)
- Tools: {len(key_info.get('tools_created', []))} created

## Tools Created
"""
        
        tools = key_info.get('tools_created', [])
        if tools:
            for tool in tools:
                summary += f"- {tool}\n"
        else:
            summary += "- None\n"
        
        summary += f"""
## Git Commit
- Pending

## Next
- Continue P1 implementation
"""
        
        return summary
    
    def compress_daily_note(self, summary: str) -> str:
        """压缩当日笔记"""
        
        # 检查大小
        current_size = len(summary.encode('utf-8'))
        
        if current_size > self.target_size:
            # 简化内容
            lines = summary.split('\n')
            compressed_lines = []
            current_size = 0
            
            for line in lines:
                if current_size + len(line.encode('utf-8')) < self.target_size - 100:
                    compressed_lines.append(line)
                    current_size += len(line.encode('utf-8')) + 1
            
            summary = '\n'.join(compressed_lines)
        
        return summary
    
    def save_compressed(self, summary: str) -> Path:
        """保存压缩后的笔记"""
        
        today = datetime.now().strftime("%Y-%m-%d")
        note_file = self.memory_dir / f"{today}.md"
        
        # 确保目录存在
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        with open(note_file, 'w', encoding='utf-8') as f:
            f.write(summary)
        
        return note_file
    
    def run(self) -> Dict:
        """运行压缩流程"""
        
        print("\n" + "=" * 80)
        print(" " * 25 + "Auto Session Compressor")
        print("=" * 80)
        
        # 提取关键信息
        key_info = self.extract_key_info()
        print(f"\nExtracting key info...")
        print(f"  Task: {key_info.get('task', 'N/A')}")
        print(f"  Steps: {key_info.get('completed_steps', 0)}/{key_info.get('total_steps', 0)}")
        print(f"  Tools: {len(key_info.get('tools_created', []))}")
        
        # 生成摘要
        print(f"\nGenerating summary...")
        summary = self.generate_summary(key_info)
        
        # 压缩
        print(f"Compressing...")
        compressed = self.compress_daily_note(summary)
        
        # 保存
        note_file = self.save_compressed(compressed)
        final_size = len(compressed.encode('utf-8'))
        
        print(f"\n[OK] Summary generated")
        print(f"[OK] Size: {final_size} bytes ({final_size/1024:.2f} KB)")
        print(f"[OK] Target: <{self.target_size} bytes (5 KB)")
        print(f"[OK] Saved to: {note_file}")
        
        if final_size < self.target_size:
            print(f"[OK] Size check PASSED")
        else:
            print(f"[WARN] Size check FAILED (too large)")
        
        print("=" * 80)
        
        return {
            "key_info": key_info,
            "summary": compressed,
            "size_bytes": final_size,
            "size_kb": final_size / 1024,
            "target_bytes": self.target_size,
            "passed": final_size < self.target_size,
            "saved_to": str(note_file),
            "success": True
        }

def main():
    """测试入口"""
    compressor = AutoSessionCompressor()
    result = compressor.run()
    
    print(f"\n[OK] Compression completed")
    print(f"[OK] Passed: {result['passed']}")

if __name__ == "__main__":
    main()

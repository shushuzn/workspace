#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
会话结束脚本 - 完整的会话结束流程

功能：
1. 检查会话状态
2. 压缩核心文件
3. 压缩今日笔记
4. 生成会话摘要
5. 更新 MEMORY.md
6. 清理临时文件
7. 生成审计报告

使用：
  py session_end.py "完成描述"
  py session_end.py --flow-id 20260318-universal-workflow-001
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

# 导入核心模块
sys.path.insert(0, str(Path(__file__).parent))

from core_files_compressor import CoreFilesCompressor
from session_compressor import SessionCompressor


class SessionEnd:
    """会话结束处理器"""
    
    def __init__(self, flow_id: str = None):
        self.workspace = Path(__file__).parent.parent
        self.today = datetime.now().strftime('%Y-%m-%d')
        self.flow_id = flow_id or f"{self.today.replace('-', '')}-universal-workflow-001"
        self.session_file = self.workspace / '13-memory/session_temp.json'
        self.execution_state = self.workspace / f'flow-archive/{self.flow_id}/execution-state.json'
        self.daily_note = self.workspace / f'13-memory/{self.today}.md'
        
    def check_session_state(self) -> Dict:
        """检查会话状态"""
        result = {
            'session_file_exists': self.session_file.exists(),
            'execution_state_exists': self.execution_state.exists(),
            'daily_note_exists': self.daily_note.exists(),
            'session_data': None,
            'execution_data': None
        }
        
        if result['session_file_exists']:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                result['session_data'] = json.load(f)
        
        if result['execution_state_exists']:
            with open(self.execution_state, 'r', encoding='utf-8') as f:
                result['execution_data'] = json.load(f)
        
        return result
    
    def compress_core_files(self) -> Dict:
        """压缩核心文件"""
        compressor = CoreFilesCompressor()
        return compressor.compress_all()
    
    def compress_session(self) -> Dict:
        """压缩会话"""
        compressor = SessionCompressor()
        return compressor.compress_session()
    
    def generate_summary(self, description: str = "") -> str:
        """生成会话摘要"""
        state = self.check_session_state()
        
        summary = []
        summary.append(f"\n{'='*60}")
        summary.append(f"会话结束报告 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        summary.append(f"{'='*60}")
        summary.append(f"Flow ID: {self.flow_id}")
        summary.append(f"描述: {description}")
        summary.append("")
        
        # 会话状态
        summary.append("会话状态:")
        if state['session_file_exists']:
            summary.append("  [OK] session_temp.json 存在")
        else:
            summary.append("  [WARN] session_temp.json 不存在")
        
        if state['execution_state_exists']:
            summary.append("  [OK] execution-state.json 存在")
            if state['execution_data']:
                summary.append(f"    - 步骤: {state['execution_data'].get('current_step', 0)}/{state['execution_data'].get('total_steps', 0)}")
                summary.append(f"    - 状态: {state['execution_data'].get('status', 'unknown')}")
        else:
            summary.append("  [WARN] execution-state.json 不存在")
        
        summary.append("")
        
        # 核心文件状态
        summary.append("核心文件:")
        core_compressor = CoreFilesCompressor()
        check_result = core_compressor.check_files()
        for f in check_result['files']:
            if f['exists']:
                status = "[OK]" if f['within_limit'] else "[WARN]"
                summary.append(f"  {status} {f['name']:<25} {f['size_kb']:>6.2f}KB")
            else:
                summary.append(f"  [MISSING] {f['name']:<25}")
        
        summary.append(f"  总计: {check_result['total_size_kb']:.2f}KB")
        summary.append("")
        
        # 建议
        if not check_result['within_limit']:
            summary.append("建议: 运行 py core_files_compressor.py --compress")
        
        summary.append(f"{'='*60}\n")
        
        return "\n".join(summary)
    
    def cleanup_temp_files(self) -> Dict:
        """清理临时文件"""
        temp_files = [
            self.workspace / '13-memory/session_temp.json',
            self.workspace / 'tool_result',
        ]
        
        result = {
            'cleaned': [],
            'errors': []
        }
        
        for temp_file in temp_files:
            if temp_file.exists():
                try:
                    if temp_file.is_file():
                        temp_file.unlink()
                        result['cleaned'].append(str(temp_file.name))
                    elif temp_file.is_dir():
                        import shutil
                        shutil.rmtree(temp_file)
                        result['cleaned'].append(str(temp_file.name) + '/')
                except Exception as e:
                    result['errors'].append(f"{temp_file.name}: {str(e)}")
        
        return result
    
    def execute(self, description: str = "") -> Dict:
        """执行完整的会话结束流程"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'flow_id': self.flow_id,
            'description': description,
            'steps': {}
        }
        
        # 1. 检查会话状态
        result['steps']['check_state'] = self.check_session_state()
        
        # 2. 压缩核心文件
        result['steps']['compress_core'] = self.compress_core_files()
        
        # 3. 压缩会话
        result['steps']['compress_session'] = self.compress_session()
        
        # 4. 生成摘要
        result['summary'] = self.generate_summary(description)
        print(result['summary'])
        
        # 5. 清理临时文件（可选）
        # result['steps']['cleanup'] = self.cleanup_temp_files()
        
        return result


def main():
    """主函数"""
    if len(sys.argv) < 2:
        print("用法: py session_end.py \"完成描述\" [--flow-id FLOW_ID]")
        return
    
    # 解析参数
    description = ""
    flow_id = None
    
    i = 1
    while i < len(sys.argv):
        if sys.argv[i] == '--flow-id' and i + 1 < len(sys.argv):
            flow_id = sys.argv[i + 1]
            i += 2
        else:
            description = sys.argv[i]
            i += 1
    
    # 执行会话结束
    session_end = SessionEnd(flow_id=flow_id)
    result = session_end.execute(description)
    
    # 返回状态码
    if result['steps']['compress_core']['after']['within_limit']:
        sys.exit(0)
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
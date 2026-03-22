#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
工作流优化器 - 统一入口
整合: 会话压缩、自动阈值、状态检查
"""

import json
import sys
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional

class WorkflowOptimizer:
    """工作流优化器"""
    
    TOTAL_LIMIT = 100 * 1024  # 100KB
    
    def __init__(self):
        self.workspace = Path(__file__).parent.parent
        self.today = datetime.now().strftime('%Y-%m-%d')
        
    def check_core_files(self) -> Dict:
        """检查核心文件状态"""
        files = ['SOUL.md', 'USER.md', 'AGENTS.md', 'TOOLS.md', 'HEARTBEAT.md', 'MEMORY.md']
        daily = self.workspace / f'13-memory/{self.today}.md'
        if daily.exists():
            files.append(str(daily.relative_to(self.workspace)))
        
        result = {'files': [], 'total_size': 0, 'within_limit': True, 'issues': []}
        
        for f in files:
            path = self.workspace / f
            if path.exists():
                size = path.stat().st_size
                result['files'].append({'name': f, 'size_kb': round(size/1024, 2)})
                result['total_size'] += size
            else:
                result['issues'].append(f"{f} 不存在")
        
        result['total_size_kb'] = round(result['total_size']/1024, 2)
        result['within_limit'] = result['total_size'] <= self.TOTAL_LIMIT
        return result
    
    def compress_core_files(self) -> Dict:
        """压缩核心文件 - 自动阈值"""
        check = self.check_core_files()
        
        # 计算自动阈值
        if check['within_limit']:
            threshold = 5.0  # 默认阈值
        else:
            excess = check['total_size'] - self.TOTAL_LIMIT
            threshold = max(0.1, (excess / check['total_size']) * 100 - 5)
        
        result = {
            'timestamp': datetime.now().isoformat(),
            'before_size_kb': check['total_size_kb'],
            'auto_threshold': threshold,
            'compressions': [],
            'after_size_kb': 0
        }
        
        for f in check['files']:
            path = self.workspace / f['name']
            if not path.exists():
                continue
                
            with open(path, 'r', encoding='utf-8') as fp:
                content = fp.read()
            
            original_size = len(content)
            
            # 压缩策略
            content = re.sub(r'\n{3,}', '\n\n', content)
            content = re.sub(r'[ \t]+\n', '\n', content)
            
            compressed_size = len(content)
            rate = (1 - compressed_size/original_size)*100 if original_size > 0 else 0
            
            if rate > threshold:
                with open(path, 'w', encoding='utf-8') as fp:
                    fp.write(content)
                result['compressions'].append({
                    'file': f['name'],
                    'rate': round(rate, 2)
                })
        
        # 验证压缩后
        after = self.check_core_files()
        result['after_size_kb'] = after['total_size_kb']
        result['total_rate'] = round((1 - after['total_size']/check['total_size'])*100, 2) if check['total_size'] > 0 else 0
        result['within_limit'] = after['within_limit']
        
        return result
    
    def run(self, mode: str = 'check') -> Dict:
        """运行工作流优化"""
        if mode == 'check':
            return self.check_core_files()
        elif mode == 'compress':
            return self.compress_core_files()
        else:
            return {'error': f'Unknown mode: {mode}'}


def main():
    """主入口"""
    optimizer = WorkflowOptimizer()
    
    if len(sys.argv) < 2:
        # 默认检查
        result = optimizer.run('check')
        print(f"\n核心文件总大小: {result['total_size_kb']:.2f}KB")
        print(f"限制: {WorkflowOptimizer.TOTAL_LIMIT/1024:.0f}KB")
        print(f"状态: {'[OK] 符合' if result['within_limit'] else '[WARN] 超限'}")
        print(f"文件数: {len(result['files'])}")
        return
    
    mode = sys.argv[1]
    if mode == '--check':
        result = optimizer.run('check')
        print(json.dumps(result, indent=2, ensure_ascii=False))
    elif mode == '--compress':
        result = optimizer.run('compress')
        print(f"\n[AUTO] 阈值: {result['auto_threshold']:.1f}%")
        print(f"压缩前: {result['before_size_kb']:.2f}KB")
        print(f"压缩后: {result['after_size_kb']:.2f}KB")
        print(f"压缩率: {result['total_rate']:.2f}%")
        print(f"状态: {'[OK]' if result['within_limit'] else '[WARN]'}")
        if result['compressions']:
            print("已压缩:")
            for c in result['compressions']:
                print(f"  - {c['file']}: {c['rate']:.1f}%")
    else:
        print(f"用法: python {sys.argv[0]} [--check|--compress]")


if __name__ == "__main__":
    main()

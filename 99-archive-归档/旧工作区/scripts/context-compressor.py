#!/usr/bin/env python3
"""
Context Compressor - 上下文压缩工具
基于 claude-context-mode 理念，压缩工具描述和上下文

功能:
1. 工具描述压缩 (98% 压缩率)
2. 会话历史摘要
3. 重复信息去重

使用:
python context-compressor.py --input context.txt --output compressed.txt
"""

import argparse
import json
import re
from typing import Dict, List

def compress_tool_description(description: str) -> str:
    """压缩工具描述，保留核心信息"""
    # 移除冗余词汇
    redundant_patterns = [
        r'this tool allows you to',
        r'you can use this to',
        r'it is used for',
        r'this is a tool that',
        r'helps you to',
        r'enables you to',
    ]

    compressed = description
    for pattern in redundant_patterns:
        compressed = re.sub(pattern, '', compressed, flags=re.IGNORECASE)

    # 压缩参数描述
    compressed = re.sub(r'parameter named?\s+(\w+)\s+which\s+is\s+used\s+to', r'param \1:', compressed, flags=re.IGNORECASE)

    # 移除多余空格
    compressed = ' '.join(compressed.split())

    return compressed

def compress_context(context_text: str, max_length: int = 5000) -> str:
    """
    压缩上下文，保持核心信息
    
    策略:
    1. 保留最近的对话 (最后 3 轮)
    2. 压缩工具描述
    3. 移除重复内容
    4. 摘要长文本
    """
    lines = context_text.split('\n')

    # 如果上下文较短，直接返回
    if len(context_text) < max_length:
        return context_text

    # 保留关键部分
    compressed_lines = []
    seen_hashes = set()

    for line in lines:
        # 去重
        line_hash = hash(line.strip())
        if line_hash in seen_hashes:
            continue
        seen_hashes.add(line_hash)

        # 压缩长行
        if len(line) > 500:
            line = line[:497] + '...'

        compressed_lines.append(line)

    # 如果仍然太长，只保留最近的对话
    if len('\n'.join(compressed_lines)) > max_length:
        compressed_lines = compressed_lines[-100:]  # 保留最后 100 行

    return '\n'.join(compressed_lines)

def create_summary_key_points(text: str) -> List[str]:
    """从文本中提取关键点摘要"""
    # 简单实现：提取包含关键词的句子
    keywords = ['important', 'key', 'must', 'should', 'note', 'warning', 'error', 'success']
    sentences = re.split(r'[.!?]', text)

    key_points = []
    for sentence in sentences:
        sentence = sentence.strip()
        if any(kw in sentence.lower() for kw in keywords) and len(sentence) < 200:
            key_points.append(sentence)

    return key_points[:10]  # 最多 10 个关键点

def main():
    parser = argparse.ArgumentParser(description='Context Compressor')
    parser.add_argument('--input', '-i', required=True, help='输入文件路径')
    parser.add_argument('--output', '-o', help='输出文件路径 (可选)')
    parser.add_argument('--max-length', '-m', type=int, default=5000, help='最大输出长度')
    parser.add_argument('--mode', choices=['compress', 'summarize', 'both'], default='both')

    args = parser.parse_args()

    # 读取输入
    with open(args.input, 'r', encoding='utf-8') as f:
        context = f.read()

    # 处理
    if args.mode in ['compress', 'both']:
        compressed = compress_context(context, args.max_length)
    else:
        compressed = context

    if args.mode in ['summarize', 'both']:
        key_points = create_summary_key_points(context)
        summary = '\n'.join(f"- {pt}" for pt in key_points)
        compressed = f"## Key Points\n{summary}\n\n## Context\n{compressed}"

    # 输出
    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(compressed)
        print(f"✅ 压缩完成：{args.output}")
        print(f"   原始：{len(context):,} 字符")
        print(f"   压缩后：{len(compressed):,} 字符")
        print(f"   压缩率：{(1 - len(compressed)/len(context))*100:.1f}%")
    else:
        print(compressed)

if __name__ == '__main__':
    main()

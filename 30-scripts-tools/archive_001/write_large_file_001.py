#!/usr/bin/env python3
"""
Write Large File Tool - 绕过 write_file 8KB 限制
用法: python write_large_file_001.py <file_path> <content_file>
"""
import sys
import os

def write_large_file(file_path, content):
    """写入大文件，无大小限制"""
    os.makedirs(os.path.dirname(file_path) or '.', exist_ok=True)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    return os.path.getsize(file_path)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python write_large_file_001.py <file_path> <content_file>")
        sys.exit(1)

    file_path = sys.argv[1]
    content_file = sys.argv[2]

    with open(content_file, 'r', encoding='utf-8') as f:
        content = f.read()

    size = write_large_file(file_path, content)
    print(f"写入成功: {size} bytes -> {file_path}")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
P-Note 自动填充主流程
集成元数据提取 + AI 贡献提取 + 模板填充
"""

import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def run_pipeline(date_str=None):
    """执行完整 P-Note 自动填充流程"""

    print("=" * 60)
    print("P-Note 自动填充流程")
    print("=" * 60)

    # 步骤 1: 提取 PDF 元数据
    print("\n[1/3] 提取 PDF 元数据...")
    cmd1 = [sys.executable, str(SCRIPT_DIR / 'pdf-metadata-extractor.py')]
    if date_str:
        cmd1.append(date_str)

    result1 = subprocess.run(cmd1, capture_output=True, text=True)
    print(result1.stdout)
    if result1.returncode != 0:
        print(f"[ERROR] 元数据提取失败：{result1.stderr}")
        return False

    # 步骤 2: AI 提取核心贡献并生成 P-Note
    print("\n[2/3] AI 提取核心贡献并生成 P-Note...")
    cmd2 = [sys.executable, str(SCRIPT_DIR / 'ai-contribution-extractor.py')]

    result2 = subprocess.run(cmd2, capture_output=True, text=True)
    print(result2.stdout)
    if result2.returncode != 0:
        print(f"[ERROR] P-Note 生成失败：{result2.stderr}")
        return False

    # 步骤 3: 统计结果
    print("\n[3/3] 统计结果...")
    output_dir = Path(r"D:\obsidian\Vault\AI-Research\P-Note")
    pnote_files = list(output_dir.glob('P-*.md'))

    print(f"  生成 P-Note 数量：{len(pnote_files)}")
    print(f"  输出目录：{output_dir}")

    print("\n" + "=" * 60)
    print("[COMPLETE] P-Note 自动填充完成")
    print("=" * 60)

    return True

if __name__ == "__main__":
    date_str = sys.argv[1] if len(sys.argv) > 1 else None
    success = run_pipeline(date_str)
    sys.exit(0 if success else 1)

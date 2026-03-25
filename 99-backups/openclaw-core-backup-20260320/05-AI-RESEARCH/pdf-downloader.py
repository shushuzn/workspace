#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 批量下载器
从 arXiv ID 批量下载 PDF 论文
"""

import requests
import os
import time
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

# 配置
PDF_SAVE_DIR = Path(r"D:\obsidian\Vault\Arxiv\PDF")
MAX_WORKERS = 10  # 最大并发数
MAX_RETRIES = 3   # 最大重试次数
TIMEOUT = 30      # 请求超时 (秒)

def get_pdf_url(arxiv_id):
    """生成 arXiv PDF 下载链接"""
    # 处理 arXiv ID 格式 (如 2603.00267)
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"

def download_pdf(arxiv_id, save_path):
    """下载单个 PDF"""
    url = get_pdf_url(arxiv_id)

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.get(url, timeout=TIMEOUT, stream=True)
            response.raise_for_status()

            # 保存到文件
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True, f"成功：{arxiv_id}"

        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                return False, f"失败：{arxiv_id} - {str(e)}"

    return False, f"失败：{arxiv_id} - 超过重试次数"

def batch_download(arxiv_ids, date_str=None):
    """批量下载 PDF"""

    # 创建保存目录
    if date_str:
        save_dir = PDF_SAVE_DIR / date_str
    else:
        save_dir = PDF_SAVE_DIR

    save_dir.mkdir(parents=True, exist_ok=True)

    results = {'success': 0, 'failed': 0}

    print(f"开始下载 {len(arxiv_ids)} 个 PDF...")
    print(f"保存目录：{save_dir}")
    print(f"并发数：{MAX_WORKERS}")
    print("-" * 50)

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_id = {}

        # 提交下载任务
        for arxiv_id in arxiv_ids:
            filename = f"{arxiv_id}.pdf"
            save_path = save_dir / filename
            future = executor.submit(download_pdf, arxiv_id, save_path)
            future_to_id[future] = arxiv_id

        # 收集结果
        for future in as_completed(future_to_id):
            arxiv_id = future_to_id[future]
            success, message = future.result()

            if success:
                results['success'] += 1
                print(f"[OK] {message}")
            else:
                results['failed'] += 1
                print(f"[FAIL] {message}")

    print("-" * 50)
    print(f"下载完成：成功 {results['success']}/{len(arxiv_ids)}, 失败 {results['failed']}")

    return results

def load_arxiv_ids_from_summary(summary_file):
    """从 arXiv summary 文件加载 arXiv ID"""
    import re

    arxiv_ids = []
    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 匹配 arXiv ID (如 2603.00267)
    pattern = r'arxiv\.org/abs/(\d+\.\d+)'
    matches = re.findall(pattern, content)
    arxiv_ids = list(set(matches))  # 去重

    return arxiv_ids

if __name__ == "__main__":
    import sys

    # 用法 1: 从命令行参数读取 arXiv ID
    if len(sys.argv) > 1:
        arxiv_ids = sys.argv[1:]
        date_str = time.strftime('%Y-%m-%d')

    # 用法 2: 从 summary 文件读取
    elif len(sys.argv) == 1:
        # 默认使用今日 summary
        date_str = time.strftime('%Y-%m-%d')
        summary_file = Path(rf"D:\obsidian\Vault\Arxiv\daily\{date_str[:4]}\{date_str[:7]}\{date_str}\{date_str}-summary.md")

        if summary_file.exists():
            print(f"从 summary 文件加载 arXiv ID: {summary_file}")
            arxiv_ids = load_arxiv_ids_from_summary(summary_file)
        else:
            print(f"未找到 summary 文件：{summary_file}")
            print("用法：py pdf-downloader.py [arxiv_id1] [arxiv_id2] ...")
            sys.exit(1)

    else:
        print("用法：py pdf-downloader.py [arxiv_id1] [arxiv_id2] ...")
        print("   或：py pdf-downloader.py (从今日 summary 自动加载)")
        sys.exit(1)

    # 执行批量下载
    batch_download(arxiv_ids, date_str)

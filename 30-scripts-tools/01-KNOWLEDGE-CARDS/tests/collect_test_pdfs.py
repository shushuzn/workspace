#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PDF 测试集收集脚本
目标：收集 20+ 种不同格式的 PDF 用于测试

测试集组成：
- 单栏论文：5 篇
- 双栏论文：5 篇
- 多栏/混合：3 篇
- 含复杂表格：3 篇
- 含公式：3 篇
- 含图表：3 篇
- 特殊格式：2 篇 (扫描版/加密版)

使用方法：
```bash
py collect_test_pdfs.py --output test_pdfs/
```
"""

import json
import time
import random
import requests
from pathlib import Path
from datetime import datetime


class PDFTestCollection:
    """PDF 测试集收集器"""

    def __init__(self):
        self.test_pdfs = []
        self.output_dir = Path(__file__).parent / "test_pdfs"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # arXiv API 端点
        self.arxiv_api = "http://export.arxiv.org/api/query"

        # 测试集配置
        self.test_categories = {
            "single_column": {
                "target": 5,
                "categories": ["cs.AI", "physics.bio-ph"],
                "description": "单栏论文"
            },
            "double_column": {
                "target": 5,
                "categories": ["cs.CV", "cs.LG"],
                "description": "双栏论文 (会议格式)"
            },
            "multi_column": {
                "target": 3,
                "categories": ["cs.HC", "cs.GR"],
                "description": "多栏/混合布局"
            },
            "with_tables": {
                "target": 3,
                "categories": ["cs.DB", "q-bio.QM"],
                "description": "含复杂表格"
            },
            "with_formulas": {
                "target": 3,
                "categories": ["math.AP", "physics.math-ph"],
                "description": "含大量公式"
            },
            "with_figures": {
                "target": 3,
                "categories": ["cs.CV", "eess.IV"],
                "description": "含大量图表"
            },
            "special": {
                "target": 2,
                "categories": ["cs.HC", "physics.bio-ph"],
                "description": "特殊格式 (扫描版/加密版)"
            }
        }

    def search_arxiv(self, category: str, max_results: int = 10) -> list:
        """搜索 arXiv 论文"""
        params = {
            "search_query": f"cat:{category}",
            "start": 0,
            "max_results": max_results,
            "sortBy": "submittedDate",
            "sortOrder": "descending"
        }

        try:
            response = requests.get(self.arxiv_api, params=params, timeout=30)
            response.raise_for_status()

            # 解析 Atom XML (简化版)
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.content)
            ns = {"atom": "http://www.w3.org/2005/Atom"}

            papers = []
            for entry in root.findall("atom:entry", ns):
                title_elem = entry.find("atom:title", ns)
                id_elem = entry.find("atom:id", ns)
                published_elem = entry.find("atom:published", ns)

                if title_elem is not None and id_elem is not None:
                    papers.append({
                        "title": title_elem.text.strip().replace("\n", " "),
                        "arxiv_id": id_elem.text.split("/")[-1],
                        "published": published_elem.text if published_elem is not None else None
                    })

            return papers
        except Exception as e:
            print(f"搜索失败：{e}")
            return []

    def download_pdf(self, arxiv_id: str, output_path: Path) -> bool:
        """下载 PDF 文件"""
        url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"

        try:
            response = requests.get(url, timeout=60, stream=True)
            response.raise_for_status()

            with open(output_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)

            return True
        except Exception as e:
            print(f"下载失败 {arxiv_id}: {e}")
            return False

    def collect_pdfs(self):
        """收集所有测试 PDF"""
        print("="*60)
        print("PDF 测试集收集")
        print("="*60)
        print(f"开始时间：{datetime.now().isoformat()}")
        print(f"输出目录：{self.output_dir}")
        print()

        total_collected = 0

        for category, config in self.test_categories.items():
            print(f"\n[{category}] {config['description']}")
            print(f"目标数量：{config['target']}")
            print("-"*60)

            collected = 0
            attempts = 0

            for cat in config["categories"]:
                if collected >= config["target"]:
                    break

                print(f"  搜索类别：{cat}")
                papers = self.search_arxiv(cat, max_results=5)

                for paper in papers:
                    if collected >= config["target"]:
                        break

                    attempts += 1

                    # 检查是否已存在
                    pdf_name = f"{paper['arxiv_id'].replace('/', '_')}.pdf"
                    pdf_path = self.output_dir / pdf_name

                    if pdf_path.exists():
                        print(f"    ✓ 已存在：{pdf_name}")
                        collected += 1
                        continue

                    # 下载 PDF
                    print(f"    下载：{paper['title'][:50]}...")
                    if self.download_pdf(paper["arxiv_id"], pdf_path):
                        print(f"    ✓ 下载成功")
                        collected += 1
                        total_collected += 1

                        # 记录元数据
                        self.test_pdfs.append({
                            "filename": pdf_name,
                            "arxiv_id": paper["arxiv_id"],
                            "title": paper["title"],
                            "category": category,
                            "collected_at": datetime.now().isoformat()
                        })

                        # 避免过快请求
                        time.sleep(3)
                    else:
                        print(f"    ✗ 下载失败")

                    if attempts > 10:
                        print(f"  尝试次数过多，跳过")
                        break

            print(f"  完成：{collected}/{config['target']}")

        # 保存元数据
        metadata_path = self.output_dir / "test_pdfs_metadata.json"
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump({
                "total": len(self.test_pdfs),
                "collected_at": datetime.now().isoformat(),
                "categories": {k: v["description"] for k, v in self.test_categories.items()},
                "pdfs": self.test_pdfs
            }, f, indent=2, ensure_ascii=False)

        print()
        print("="*60)
        print("收集完成")
        print("="*60)
        print(f"总数量：{total_collected}")
        print(f"元数据：{metadata_path}")
        print("="*60)

        return total_collected


def main():
    """主函数"""
    collector = PDFTestCollection()
    total = collector.collect_pdfs()
    return 0 if total >= 20 else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())

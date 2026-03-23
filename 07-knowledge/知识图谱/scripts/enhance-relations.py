#!/usr/bin/env python3
"""
知识图谱增强 - 第 2 阶段：关系增强

从 P-Note 中提取论文间的关系
"""

import json
import re
from pathlib import Path
from collections import defaultdict

class RelationExtractor:
    """关系提取器"""

    def __init__(self):
        # 关系关键词
        self.relation_patterns = {
            "cites": [
                r'引用 [：:\s]*(.+?)(?:[,.。]|$)',
                r'cite[ds]?\s+(.+?)(?:[,.]|$)',
                r'based on\s+(.+?)(?:[,.]|$)',
                r'根据\s+(.+?)(?:[,.。]|$)',
                r'arXiv[:\s]+(\d+\.\d+)'  # 文中提到的 arXiv ID
            ],
            "extends": [
                r'扩展 [：:\s]*(.+?)(?:[,.。]|$)',
                r'extend[s]?\s+(.+?)(?:[,.]|$)',
                r'改进 [：:\s]*(.+?)(?:[,.。]|$)',
                r'改进了\s+(.+?)(?:[,.。]|$)',
                r'builds upon\s+(.+?)(?:[,.]|$)'
            ],
            "critiques": [
                r'局限性 [：:\s]*(.+?)(?:[,.。]|$)',
                r'limitation[s]?\s+(.+?)(?:[,.]|$)',
                r'不足 [：:\s]*(.+?)(?:[,.。]|$)',
                r'缺点 [：:\s]*(.+?)(?:[,.。]|$)',
                r'无法\s+(.+?)(?:[,.。]|$)'
            ],
            "uses_method": [
                r'使用 [：:\s]*(.+?)(?:[,.。]|$)',
                r'employ[s]?\s+(.+?)(?:[,.]|$)',
                r'采用 [：:\s]*(.+?)(?:[,.。]|$)',
                r'基于\s+(.+?)(?:[,.。]|$)',
                r'方法 [：:\s]*(.+?)(?:[,.。]|$)'
            ]
        }

    def extract_relations_from_pnote(self, file_path: Path, arxiv_id: str) -> list:
        """从 P-Note 提取关系"""
        relations = []

        try:
            content = file_path.read_text(encoding="utf-8")
        except:
            return relations

        source = f"paper_{arxiv_id.replace('.', '_')}"

        # 提取文中提到的所有 arXiv ID
        mentioned_arxiv = re.findall(r'arXiv[:\s]+(\d+\.\d+)', content)

        for target_arxiv in mentioned_arxiv:
            if target_arxiv != arxiv_id:  # 排除自己
                target = f"paper_{target_arxiv.replace('.', '_')}"

                # 判断关系类型
                relation_type = "related_work"  # 默认关系

                # 检查是否有特定关系关键词
                for rel_type, patterns in self.relation_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            relation_type = rel_type
                            break

                relations.append({
                    "source": source,
                    "target": target,
                    "type": relation_type,
                    "confidence": 0.7,
                    "evidence": f"在 {file_path.name} 中提到"
                })

        return relations

    def extract_from_summaries(self, summaries: dict) -> list:
        """从摘要中提取关系"""
        relations = []

        # 基于共同作者建立关系
        author_papers = defaultdict(list)
        for paper_id, summary in summaries.items():
            authors = summary.get("authors", "")
            if authors:
                for author in authors.split(","):
                    author = author.strip()
                    if author:
                        author_papers[author].append(paper_id)

        # 同一作者的论文建立 extends 关系
        for author, papers in author_papers.items():
            if len(papers) > 1:
                for i, p1 in enumerate(papers):
                    for p2 in papers[i+1:]:
                        relations.append({
                            "source": p1,
                            "target": p2,
                            "type": "same_author",
                            "confidence": 0.8,
                            "evidence": f"共同作者：{author}"
                        })

        # 基于共同方法建立关系
        method_papers = defaultdict(list)
        for paper_id, summary in summaries.items():
            methods = summary.get("methods", [])
            for method in methods:
                if method:
                    method_papers[method[:50]].append(paper_id)

        for method, papers in method_papers.items():
            if len(papers) > 1:
                for i, p1 in enumerate(papers):
                    for p2 in papers[i+1:]:
                        relations.append({
                            "source": p1,
                            "target": p2,
                            "type": "uses_same_method",
                            "confidence": 0.6,
                            "evidence": f"共同方法：{method[:50]}..."
                        })

        return relations

def enhance_relations():
    """增强关系"""
    print("=" * 50)
    print("知识图谱增强 - 第 2 阶段：关系增强")
    print("=" * 50)
    print()

    extractor = RelationExtractor()
    all_relations = []

    # 1. 从摘要中提取关系
    print("[INFO] 从摘要中提取关系...")
    summaries_file = Path("D:/OpenClaw/workspace/knowledge-graph/paper-summaries.json")

    if summaries_file.exists():
        with open(summaries_file, 'r', encoding='utf-8') as f:
            summaries = json.load(f)

        summary_relations = extractor.extract_from_summaries(summaries)
        all_relations.extend(summary_relations)
        print(f"  [OK] 从摘要提取 {len(summary_relations)} 个关系\n")

    # 2. 从 P-Note 全文中提取关系
    print("[INFO] 从 P-Note 全文中提取关系...")
    medium_dir = Path("D:/OpenClaw/workspace/Medium")

    if medium_dir.exists():
        pnote_files = list(medium_dir.glob("P-*.md"))

        for pnote_file in pnote_files:
            # 从文件名或内容提取 arXiv ID
            content = pnote_file.read_text(encoding="utf-8", errors="ignore")
            arxiv_match = re.search(r'arXiv[:\s]+(\d+\.\d+)', content)

            if arxiv_match:
                arxiv_id = arxiv_match.group(1)
                print(f"[EXTRACT] {pnote_file.stem} ({arxiv_id})")

                relations = extractor.extract_relations_from_pnote(pnote_file, arxiv_id)
                all_relations.extend(relations)

                if relations:
                    print(f"  [OK] 提取 {len(relations)} 个关系")
                else:
                    print(f"  [INFO] 无关系")

    print()

    # 3. 去重
    unique_relations = []
    seen = set()
    for rel in all_relations:
        key = (rel["source"], rel["target"], rel["type"])
        if key not in seen:
            unique_relations.append(rel)
            seen.add(key)

    # 4. 保存关系
    output_file = Path("D:/OpenClaw/workspace/knowledge-graph/enhanced-relations.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(unique_relations, f, indent=2, ensure_ascii=False)

    print("=" * 50)
    print(f"[OK] 关系已保存：{output_file}")
    print(f"[INFO] 共提取 {len(unique_relations)} 个唯一关系")
    print()
    print("[关系类型分布]")
    type_counts = defaultdict(int)
    for rel in unique_relations:
        type_counts[rel["type"]] += 1
    for rel_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {rel_type}: {count} 个")
    print("=" * 50)

    return unique_relations

if __name__ == "__main__":
    enhance_relations()

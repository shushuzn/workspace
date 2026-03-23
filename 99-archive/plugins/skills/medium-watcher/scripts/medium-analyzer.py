#!/usr/bin/env python3
"""
Medium Analyzer — Medium 文章深度分析器 (增强版)

功能:
- 全文内容提取 (标题/副标题/段落/代码/图片)
- 智能质量评分 (多维度评估)
- 关键观点抽取
- 情感分析
- 主题分类
- 与 arXiv 论文关联
- 生成结构化分析笔记

使用:
    python medium-analyzer.py --input Medium/Raw/*.md --output Medium/Analysis/
"""

import argparse
import json
import re
from datetime import datetime
from pathlib import Path
from collections import Counter


class MediumAnalyzer:
    """Medium 文章深度分析器"""
    
    def __init__(self):
        self.analysis_results = []
    
    def load_article(self, file_path: Path) -> dict:
        """加载文章文件"""
        content = file_path.read_text(encoding="utf-8")
        
        # 解析 YAML frontmatter
        metadata = {}
        body = content
        
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                yaml_content = parts[1]
                body = parts[2]
                
                # 简单 YAML 解析
                for line in yaml_content.strip().split("\n"):
                    if ":" in line:
                        key, value = line.split(":", 1)
                        metadata[key.strip()] = value.strip().strip('"\'')
        
        return {
            "file": str(file_path),
            "metadata": metadata,
            "body": body,
            "full_content": content
        }
    
    def extract_structure(self, body: str) -> dict:
        """提取文章结构"""
        structure = {
            "title": "",
            "subtitles": [],
            "paragraphs": [],
            "code_blocks": [],
            "images": [],
            "links": [],
            "lists": []
        }
        
        lines = body.strip().split("\n")
        
        for line in lines:
            line = line.strip()
            
            # 标题
            if line.startswith("# "):
                structure["title"] = line[2:].strip()
            elif line.startswith("## "):
                structure["subtitles"].append(line[3:].strip())
            elif line.startswith("### "):
                structure["subtitles"].append(line[4:].strip())
            
            # 段落 (非空行且不是特殊格式)
            elif line and not line.startswith((">", "```", "!", "- ", "* ", "[", "http")):
                if len(line) > 20:  # 忽略短行
                    structure["paragraphs"].append(line)
            
            # 代码块
            elif line.startswith("```"):
                structure["code_blocks"].append(line)
            
            # 图片
            elif line.startswith("![") or "![" in line:
                structure["images"].append(line)
            
            # 链接
            elif "http" in line:
                structure["links"].append(line)
            
            # 列表
            elif line.startswith(("- ", "* ", "1. ")):
                structure["lists"].append(line)
        
        return structure
    
    def calculate_quality_score(self, article: dict, structure: dict) -> dict:
        """计算质量评分 (多维度)"""
        scores = {}
        
        # 1. 内容长度评分 (0-2 分)
        word_count = len(structure["paragraphs"]) * 15  # 估算词数
        if word_count >= 2000:
            scores["content_length"] = 2.0
        elif word_count >= 1000:
            scores["content_length"] = 1.5
        elif word_count >= 500:
            scores["content_length"] = 1.0
        else:
            scores["content_length"] = 0.5
        
        # 2. 结构完整性评分 (0-2 分)
        structure_score = 0
        if structure["title"]:
            structure_score += 0.5
        if len(structure["subtitles"]) >= 3:
            structure_score += 0.5
        if len(structure["paragraphs"]) >= 10:
            structure_score += 0.5
        if len(structure["code_blocks"]) >= 1:
            structure_score += 0.5
        scores["structure"] = structure_score
        
        # 3. 代码示例评分 (0-2 分)
        if len(structure["code_blocks"]) >= 5:
            scores["code_examples"] = 2.0
        elif len(structure["code_blocks"]) >= 2:
            scores["code_examples"] = 1.5
        elif len(structure["code_blocks"]) >= 1:
            scores["code_examples"] = 1.0
        else:
            scores["code_examples"] = 0.5
        
        # 4. 作者权威性评分 (0-2 分)
        author = article["metadata"].get("author", "").lower()
        known_authors = ["karpathy", "simon willison", "andrej", "yann lecun", "demis hassabis"]
        if any(name in author for name in known_authors):
            scores["author_authority"] = 2.0
        elif "medium.com" in article["metadata"].get("url", ""):
            scores["author_authority"] = 1.0
        else:
            scores["author_authority"] = 0.5
        
        # 5. 时效性评分 (0-1 分)
        pub_date = article["metadata"].get("date", "")
        if pub_date:
            try:
                pub_datetime = datetime.fromisoformat(pub_date.replace("Z", "+00:00"))
                days_old = (datetime.now() - pub_datetime).days
                if days_old <= 7:
                    scores["timeliness"] = 1.0
                elif days_old <= 30:
                    scores["timeliness"] = 0.8
                elif days_old <= 90:
                    scores["timeliness"] = 0.6
                else:
                    scores["timeliness"] = 0.4
            except Exception:
                scores["timeliness"] = 0.5
        else:
            scores["timeliness"] = 0.5
        
        # 6. 标签相关性评分 (0-1 分)
        tags = article["metadata"].get("tags", "").lower()
        relevant_tags = ["ai", "llm", "machine-learning", "deep-learning", "nlp", "agentic", "mcp"]
        if any(tag in tags for tag in relevant_tags):
            scores["relevance"] = 1.0
        else:
            scores["relevance"] = 0.5
        
        # 计算总分
        total = sum(scores.values())
        max_score = 10.0
        
        return {
            "scores": scores,
            "total": round(total, 2),
            "max": max_score,
            "percentage": round(total / max_score * 100, 1)
        }
    
    def extract_key_points(self, structure: dict) -> list:
        """提取关键观点"""
        key_points = []
        
        # 从副标题提取
        for subtitle in structure["subtitles"][:5]:
            key_points.append({
                "type": "section",
                "content": subtitle,
                "confidence": 0.8
            })
        
        # 从段落首句提取 (可能是主题句)
        for para in structure["paragraphs"][:5]:
            if len(para) > 30 and len(para) < 200:
                key_points.append({
                    "type": "claim",
                    "content": para,
                    "confidence": 0.6
                })
        
        # 从列表项提取
        for item in structure["lists"][:10]:
            key_points.append({
                "type": "list_item",
                "content": item,
                "confidence": 0.7
            })
        
        return key_points[:15]  # 限制数量
    
    def analyze_sentiment(self, body: str) -> dict:
        """简单情感分析"""
        positive_words = ["improve", "better", "success", "effective", "powerful", "innovative", "breakthrough", "exciting"]
        negative_words = ["problem", "issue", "challenge", "difficult", "limitation", "fail", "error", "warning"]
        
        body_lower = body.lower()
        
        positive_count = sum(1 for word in positive_words if word in body_lower)
        negative_count = sum(1 for word in negative_words if word in body_lower)
        
        if positive_count > negative_count * 1.5:
            sentiment = "positive"
        elif negative_count > positive_count * 1.5:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "sentiment": sentiment,
            "positive_count": positive_count,
            "negative_count": negative_count
        }
    
    def identify_topics(self, structure: dict) -> list:
        """识别主题"""
        topic_keywords = {
            "LLM": ["llm", "large language model", "gpt", "claude", "transformer"],
            "Agentic AI": ["agent", "agentic", "autonomous", "planning", "tool use"],
            "MCP": ["mcp", "model context protocol", "tool integration"],
            "RAG": ["rag", "retrieval", "embedding", "vector database"],
            "Fine-tuning": ["fine-tune", "fine-tuning", "lora", "adapter"],
            "Evaluation": ["evaluate", "benchmark", "metric", "accuracy"],
            "Deployment": ["deploy", "production", "inference", "optimization"],
            "Ethics": ["ethics", "bias", "fairness", "safety", "alignment"]
        }
        
        body_lower = (structure["title"] + " " + " ".join(structure["paragraphs"])).lower()
        
        identified_topics = []
        for topic, keywords in topic_keywords.items():
            if any(keyword in body_lower for keyword in keywords):
                identified_topics.append(topic)
        
        return identified_topics
    
    def link_to_arxiv(self, structure: dict) -> list:
        """关联 arXiv 论文"""
        arxiv_links = []
        
        # 查找 arXiv ID 模式
        arxiv_pattern = r'arXiv[:\s]+(\d+\.\d+)'
        
        all_text = structure["title"] + " " + " ".join(structure["paragraphs"]) + " " + " ".join(structure["links"])
        
        for match in re.finditer(arxiv_pattern, all_text, re.IGNORECASE):
            arxiv_id = match.group(1)
            arxiv_links.append({
                "arxiv_id": arxiv_id,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "context": "mentioned_in_article"
            })
        
        return arxiv_links
    
    def generate_analysis_note(self, article: dict, structure: dict, quality: dict, key_points: list, topics: list, arxiv_links: list) -> str:
        """生成分析笔记"""
        metadata = article["metadata"]
        
        note = f"""---
type: medium-analysis
tags: [Medium/分析，{" ".join(topics)}]
source: {metadata.get('url', 'unknown')}
author: {metadata.get('author', 'unknown')}
date: {metadata.get('date', 'unknown')}
quality_score: {quality['total']}/{quality['max']} ({quality['percentage']}%)
analyzed: {datetime.now().isoformat()}
---

# Medium 文章分析：{structure['title'] or metadata.get('title', 'Unknown')}

**作者:** {metadata.get('author', 'Unknown')}  
**来源:** [{metadata.get('url', '#')}]({metadata.get('url', '#')})  
**发布日期:** {metadata.get('date', 'Unknown')}  
**质量评分:** ⭐ {quality['total']}/{quality['max']} ({quality['percentage']}%)

---

## 📊 质量评估

| 维度 | 得分 | 说明 |
|------|------|------|
| 内容长度 | {quality['scores'].get('content_length', 0)}/2.0 | 估算词数 |
| 结构完整性 | {quality['scores'].get('structure', 0)}/2.0 | 标题/副标题/段落 |
| 代码示例 | {quality['scores'].get('code_examples', 0)}/2.0 | 代码块数量 |
| 作者权威性 | {quality['scores'].get('author_authority', 0)}/2.0 | 知名作者 |
| 时效性 | {quality['scores'].get('timeliness', 0)}/1.0 | 发布时长 |
| 相关性 | {quality['scores'].get('relevance', 0)}/1.0 | 主题相关 |

---

## 🏷️ 主题分类

{', '.join(topics) if topics else '未识别到明确主题'}

---

## 💡 关键观点

"""
        
        for i, point in enumerate(key_points[:10], 1):
            note += f"{i}. **{point['type']}**: {point['content']}\n\n"
        
        if arxiv_links:
            note += """
---

## 🔗 关联 arXiv 论文

"""
            for link in arxiv_links:
                note += f"- [{link['arxiv_id']}]({link['url']})\n"
        
        note += """
---

## 📝 原文结构

"""
        note += f"- **副标题数量:** {len(structure['subtitles'])}\n"
        note += f"- **段落数量:** {len(structure['paragraphs'])}\n"
        note += f"- **代码块数量:** {len(structure['code_blocks'])}\n"
        note += f"- **图片数量:** {len(structure['images'])}\n"
        note += f"- **链接数量:** {len(structure['links'])}\n"
        
        note += """
---

*分析由 Medium Analyzer 自动生成*
"""
        
        return note
    
    def analyze_article(self, file_path: Path, output_dir: Path) -> dict:
        """分析单篇文章"""
        # 使用 ASCII 安全文件名
        safe_name = file_path.stem.encode('ascii', 'ignore').decode('ascii')[:60]
        print(f"[ANALYZE] {safe_name}")
        
        # 加载文章
        article = self.load_article(file_path)
        
        # 提取结构
        structure = self.extract_structure(article["body"])
        
        # 质量评分
        quality = self.calculate_quality_score(article, structure)
        
        # 关键观点
        key_points = self.extract_key_points(structure)
        
        # 主题识别
        topics = self.identify_topics(structure)
        
        # arXiv 关联
        arxiv_links = self.link_to_arxiv(structure)
        
        # 生成分析笔记
        analysis_note = self.generate_analysis_note(
            article, structure, quality, key_points, topics, arxiv_links
        )
        
        # 保存分析结果
        output_file = output_dir / f"analysis-{file_path.stem}.md"
        output_file.write_text(analysis_note, encoding="utf-8")
        
        print(f"  [OK] Quality: {quality['total']}/{quality['max']} | Topics: {', '.join(topics) if topics else 'N/A'}")
        print(f"  [SAVE] {output_file}")
        
        return {
            "file": str(file_path),
            "output": str(output_file),
            "quality": quality,
            "topics": topics,
            "arxiv_links": arxiv_links,
            "key_points_count": len(key_points)
        }
    
    def analyze_directory(self, input_dir: Path, output_dir: Path) -> list:
        """分析目录下所有文章"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        md_files = list(input_dir.glob("*.md"))
        print(f"[INFO] 找到 {len(md_files)} 个 Markdown 文件\n")
        
        results = []
        for file_path in md_files:
            try:
                result = self.analyze_article(file_path, output_dir)
                results.append(result)
            except Exception as e:
                safe_name = file_path.stem.encode('ascii', 'ignore').decode('ascii')[:60]
                print(f"[ERROR] {safe_name}: {e}")
        
        # 生成汇总报告
        self.generate_summary_report(results, output_dir)
        
        return results
    
    def generate_summary_report(self, results: list, output_dir: Path):
        """生成汇总报告"""
        if not results:
            return
        
        high_quality = [r for r in results if r["quality"]["percentage"] >= 70]
        topics_counter = Counter(topic for r in results for topic in r["topics"])
        
        report = f"""# Medium 文章分析汇总

**分析时间:** {datetime.now().isoformat()}  
**文章总数:** {len(results)}  
**高质量文章:** {len(high_quality)} (≥70%)

---

## 📊 质量分布

| 质量等级 | 数量 | 占比 |
|----------|------|------|
| 优秀 (≥80%) | {len([r for r in results if r['quality']['percentage'] >= 80])} | {len([r for r in results if r['quality']['percentage'] >= 80]) / len(results) * 100:.1f}% |
| 良好 (70-79%) | {len([r for r in results if 70 <= r['quality']['percentage'] < 80])} | {len([r for r in results if 70 <= r['quality']['percentage'] < 80]) / len(results) * 100:.1f}% |
| 一般 (50-69%) | {len([r for r in results if 50 <= r['quality']['percentage'] < 70])} | {len([r for r in results if 50 <= r['quality']['percentage'] < 70]) / len(results) * 100:.1f}% |
| 较低 (<50%) | {len([r for r in results if r['quality']['percentage'] < 50])} | {len([r for r in results if r['quality']['percentage'] < 50]) / len(results) * 100:.1f}% |

---

## 🏷️ 主题分布

"""
        for topic, count in topics_counter.most_common(10):
            report += f"- **{topic}**: {count} 篇\n"
        
        report += """
---

## ⭐ 高质量文章推荐

"""
        for r in sorted(high_quality, key=lambda x: x["quality"]["total"], reverse=True)[:5]:
            report += f"1. {Path(r['file']).stem} - {r['quality']['total']}/{r['quality']['max']}\n"
        
        report += f"""
---

## 📁 输出文件

- 分析笔记：`{output_dir}/analysis-*.md`
- 汇总报告：`{output_dir}/analysis-summary.md` (本文件)

---

*报告由 Medium Analyzer 自动生成*
"""
        
        summary_file = output_dir / "analysis-summary.md"
        summary_file.write_text(report, encoding="utf-8")
        print(f"\n[SUMMARY] 报告已保存：{summary_file}")


def main():
    parser = argparse.ArgumentParser(description="Medium Analyzer")
    parser.add_argument("--input", type=str, required=True, help="输入目录或文件")
    parser.add_argument("--output", type=str, default="Medium/Analysis", help="输出目录")
    args = parser.parse_args()
    
    print(f"\n=== Medium Analyzer ===")
    print(f"Input: {args.input}")
    print(f"Output: {args.output}\n")
    
    analyzer = MediumAnalyzer()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if input_path.is_dir():
        results = analyzer.analyze_directory(input_path, output_path)
    else:
        result = analyzer.analyze_article(input_path, output_path)
        results = [result]
    
    print(f"\n[COMPLETE] 分析完成！共 {len(results)} 篇文章")
    
    return 0


if __name__ == "__main__":
    exit(main())

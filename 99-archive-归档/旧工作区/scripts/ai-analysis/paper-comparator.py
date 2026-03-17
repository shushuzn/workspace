#!/usr/bin/env python3
"""
Paper Comparator - 论文对比分析
多篇论文横向对比（方法/实验/结论）
输出对比报告
"""

import sys
import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

# Windows UTF-8 编码支持
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ============ 配置 ============
WORKSPACE = r"D:\OpenClaw\workspace"
ARXIV_DIR = os.path.join(WORKSPACE, "Arxiv")
OUTPUT_DIR = os.path.join(WORKSPACE, "reports", "comparisons")

# 对比维度
COMPARISON_DIMENSIONS = {
    "problem": ["problem", "challenge", "issue", "问题", "挑战"],
    "method": ["method", "approach", "technique", "algorithm", "方法", "算法"],
    "model": ["model", "architecture", "framework", "结构", "模型"],
    "dataset": ["dataset", "data", "benchmark", "数据", "评测"],
    "metric": ["metric", "accuracy", "performance", "指标", "性能"],
    "result": ["result", "experiment", "evaluation", "结果", "实验"],
    "conclusion": ["conclusion", "finding", "contribution", "结论", "贡献"],
    "limitation": ["limitation", "future work", "局限", "未来工作"],
}

# 提取模式
PATTERNS = {
    "title": r'^#\s+(.+)$',
    "abstract": r'(?:abstract|摘要)[:：]\s*(.+?)(?=\n#|\n##|$)',
    "method": r'(?:method|approach|方法)[:：]\s*(.+?)(?=\n#|\n##|$)',
    "result": r'(?:result|experiment|结果)[:：]\s*(.+?)(?=\n#|\n##|$)',
}

# ============ 工具函数 ============
def log(msg: str):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)

def extract_text(filepath: str, max_chars: int = 10000) -> str:
    """提取文件内容"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 移除 YAML frontmatter
        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                content = content[end + 3:]
        
        return content[:max_chars]
    except Exception as e:
        log(f"⚠️ 读取失败 {filepath}: {e}")
        return ""

def extract_metadata(content: str) -> Dict:
    """提取元数据"""
    metadata = {}
    
    # 标题
    title_match = re.search(PATTERNS['title'], content, re.MULTILINE)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    
    # 摘要
    abstract_match = re.search(PATTERNS['abstract'], content, re.IGNORECASE | re.DOTALL)
    if abstract_match:
        metadata['abstract'] = abstract_match.group(1).strip()[:500]
    
    # 标签
    tags_match = re.search(r'tags:\s*\[([^\]]+)\]', content)
    if tags_match:
        metadata['tags'] = [t.strip() for t in tags_match.group(1).split(',')]
    
    # 领域
    domain_match = re.search(r'domain:\s*(\S+)', content)
    if domain_match:
        metadata['domain'] = domain_match.group(1)
    
    # 日期
    date_match = re.search(r'(\d{4}-\d{2}-\d{2})', filepath if 'filepath' in dir() else content)
    if date_match:
        metadata['date'] = date_match.group(1)
    
    return metadata

def extract_dimension(content: str, dimension: str, keywords: List[str]) -> str:
    """提取特定维度的内容"""
    text_lower = content.lower()
    
    # 查找包含关键词的段落
    paragraphs = content.split('\n\n')
    relevant = []
    
    for para in paragraphs:
        para_lower = para.lower()
        if any(kw.lower() in para_lower for kw in keywords):
            # 清理并截取
            cleaned = para.strip()
            if len(cleaned) > 50 and len(cleaned) < 1000:
                relevant.append(cleaned)
    
    # 返回最相关的 2-3 段
    return '\n\n'.join(relevant[:3])

def compare_papers(papers: List[Dict]) -> Dict:
    """对比多篇论文"""
    comparison = {
        "dimensions": {},
        "common_themes": [],
        "key_differences": [],
    }
    
    # 按维度对比
    for dim_name, keywords in COMPARISON_DIMENSIONS.items():
        dim_data = {}
        for paper in papers:
            content = extract_dimension(paper['content'], dim_name, keywords)
            if content:
                dim_data[paper['name']] = content[:300] + "..." if len(content) > 300 else content
        
        if dim_data:
            comparison["dimensions"][dim_name] = dim_data
    
    # 找出共同主题
    all_tags = []
    for paper in papers:
        all_tags.extend(paper.get('metadata', {}).get('tags', []))
    
    from collections import Counter
    tag_counts = Counter(all_tags)
    comparison["common_themes"] = [tag for tag, count in tag_counts.items() if count > 1]
    
    # 关键差异（简化：基于标签差异）
    paper_tags = {p['name']: set(p.get('metadata', {}).get('tags', [])) for p in papers}
    for i, p1 in enumerate(papers):
        for p2 in papers[i+1:]:
            tags1 = paper_tags[p1['name']]
            tags2 = paper_tags[p2['name']]
            diff1 = tags1 - tags2
            diff2 = tags2 - tags1
            if diff1 or diff2:
                comparison["key_differences"].append({
                    "papers": [p1['name'], p2['name']],
                    f"{p1['name']} 独有": list(diff1)[:5],
                    f"{p2['name']} 独有": list(diff2)[:5],
                })
    
    return comparison

def find_related_papers(topic: str, limit: int = 5) -> List[str]:
    """查找相关论文"""
    papers = []
    
    for root, dirs, files in os.walk(ARXIV_DIR):
        if '_archive' in root or 'archive' in root:
            continue
        
        for filename in files:
            if not filename.endswith('.md'):
                continue
            
            filepath = os.path.join(root, filename)
            content = extract_text(filepath, max_chars=2000)
            
            # 检查是否相关
            if topic.lower() in content.lower() or topic.lower() in filename.lower():
                papers.append(filepath)
        
        if len(papers) >= limit:
            break
    
    return papers[:limit]

# ============ 报告生成 ============
def generate_comparison_report(papers: List[Dict], comparison: Dict, output_path: str):
    """生成对比报告"""
    report = f"""# 论文对比分析报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**对比论文:** {len(papers)} 篇

---

## 📚 论文列表

"""
    
    for i, paper in enumerate(papers, 1):
        meta = paper.get('metadata', {})
        report += f"### {i}. {meta.get('title', paper['name'])}\n\n"
        report += f"- **文件:** `{paper['name']}`\n"
        if meta.get('date'):
            report += f"- **日期:** {meta['date']}\n"
        if meta.get('domain'):
            report += f"- **领域:** {meta['domain']}\n"
        if meta.get('tags'):
            report += f"- **标签:** {', '.join(f'`#{t}`' for t in meta['tags'][:10])}\n"
        if meta.get('abstract'):
            report += f"\n**摘要:** {meta['abstract'][:200]}...\n"
        report += "\n---\n\n"
    
    # 共同主题
    report += "## 🔍 共同主题\n\n"
    if comparison['common_themes']:
        for theme in comparison['common_themes']:
            report += f"- `#{theme}`\n"
    else:
        report += "无明显共同主题\n"
    report += "\n---\n\n"
    
    # 按维度对比
    report += "## 📊 维度对比\n\n"
    
    dim_names_cn = {
        "problem": "问题定义",
        "method": "方法",
        "model": "模型架构",
        "dataset": "数据集",
        "metric": "评估指标",
        "result": "实验结果",
        "conclusion": "结论",
        "limitation": "局限性",
    }
    
    for dim_name, dim_data in comparison['dimensions'].items():
        report += f"### {dim_names_cn.get(dim_name, dim_name)}\n\n"
        
        # 表格形式
        report += "| 论文 | 内容 |\n"
        report += "|------|------|\n"
        
        for paper_name, content in dim_data.items():
            # 清理内容用于表格
            clean_content = content.replace('|', '｜').replace('\n', '<br>')
            report += f"| {paper_name} | {clean_content} |\n"
        
        report += "\n"
    
    # 关键差异
    report += "## ⚖️ 关键差异\n\n"
    if comparison['key_differences']:
        for diff in comparison['key_differences']:
            papers_str = " vs ".join(diff['papers'])
            report += f"### {papers_str}\n\n"
            
            for key, value in diff.items():
                if key not in ['papers']:
                    if value:
                        report += f"- **{key}:** {', '.join(f'`#{t}`' for t in value)}\n"
            
            report += "\n"
    else:
        report += "无显著差异\n"
    
    # 总结
    report += """## 💡 总结

### 核心洞察
（此处手动填写分析结论）

### 研究趋势
- 

### 待探索方向
- 

---

**报告结束时间:** """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

# ============ 主流程 ============
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='论文对比分析')
    parser.add_argument('--topic', type=str, help='主题/关键词（自动查找相关论文）')
    parser.add_argument('--files', type=str, nargs='+', help='指定文件路径')
    parser.add_argument('--limit', type=int, default=5, help='最大论文数')
    args = parser.parse_args()
    
    log("🚀 启动论文对比分析")
    
    papers = []
    
    # 模式 1: 按主题查找
    if args.topic:
        log(f"🔍 查找主题：{args.topic}")
        filepaths = find_related_papers(args.topic, limit=args.limit)
        log(f"  → 找到 {len(filepaths)} 篇相关论文")
        
        for filepath in filepaths:
            content = extract_text(filepath)
            if content:
                papers.append({
                    'name': os.path.basename(filepath),
                    'path': filepath,
                    'content': content,
                    'metadata': extract_metadata(content),
                })
    
    # 模式 2: 指定文件
    elif args.files:
        for filepath in args.files:
            if os.path.exists(filepath):
                content = extract_text(filepath)
                if content:
                    papers.append({
                        'name': os.path.basename(filepath),
                        'path': filepath,
                        'content': content,
                        'metadata': extract_metadata(content),
                    })
    
    # 验证
    if len(papers) < 2:
        log("❌ 至少需要 2 篇论文进行对比")
        return
    
    log(f"📊 对比 {len(papers)} 篇论文")
    
    # 执行对比
    comparison = compare_papers(papers)
    
    # 生成报告
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    topic_str = args.topic or "custom"
    timestamp = datetime.now().strftime('%Y%m%d-%H%M')
    output_path = os.path.join(OUTPUT_DIR, f"comparison-{topic_str}-{timestamp}.md")
    
    generate_comparison_report(papers, comparison, output_path)
    
    log(f"💾 报告已保存到 {output_path}")
    log("✅ 完成")

if __name__ == "__main__":
    main()

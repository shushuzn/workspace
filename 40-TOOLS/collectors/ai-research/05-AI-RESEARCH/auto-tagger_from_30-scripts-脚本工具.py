#!/usr/bin/env python3
"""
Auto Tagger - 自动标签系统
扫描笔记/论文，自动分类打标签
输出到 Obsidian vault
"""

import sys
import os
import re
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple

# Windows UTF-8 编码支持
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ============ 配置 ============
WORKSPACE = r"D:\OpenClaw\workspace"

# 扫描目录
SCAN_DIRS = {
    "arxiv": os.path.join(WORKSPACE, "Arxiv"),
    "medium": os.path.join(WORKSPACE, "Medium"),
    "notes": os.path.join(WORKSPACE, "notes"),
    "memory": os.path.join(WORKSPACE, "memory"),
}

# 标签规则（关键词 → 标签）
TAG_RULES = {
    # AI/ML 核心
    "llm": ["llm", "large language model", "语言模型"],
    "transformer": ["transformer", "attention", "self-attention"],
    "diffusion": ["diffusion", "stable diffusion", "生成模型"],
    "rag": ["rag", "retrieval augmented generation", "检索增强"],
    "agent": ["agent", "agentic", "智能体", "自主"],
    "mcp": ["mcp", "model context protocol"],
    
    # 技术方向
    "fine-tuning": ["fine-tune", "fine tuning", "微调", "lora", "qlora"],
    "prompt-engineering": ["prompt", "提示词", "in-context learning"],
    "rlhf": ["rlhf", "reinforcement learning", "强化学习", "人类反馈"],
    "quantization": ["quantization", "量化", "int8", "int4"],
    "distillation": ["distillation", "知识蒸馏", "小型化"],
    
    # 应用领域
    "computer-vision": ["cv", "computer vision", "图像", "视觉", "cnn"],
    "nlp": ["nlp", "natural language", "文本", "语言处理"],
    "speech": ["speech", "语音", "tts", "asr", "whisper"],
    "robotics": ["robot", "robotics", "机器人", "控制"],
    "recommendation": ["recommend", "推荐系统", "ranking"],
    
    # 模型/框架
    "gpt": ["gpt", "openai", "chatgpt"],
    "claude": ["claude", "anthropic"],
    "llama": ["llama", "meta", "facebook"],
    "qwen": ["qwen", "通义", "alibaba"],
    "mistral": ["mistral", "mixtral"],
    "pytorch": ["pytorch", "torch"],
    "tensorflow": ["tensorflow", "tf", "keras"],
    
    # 研究类型
    "survey": ["survey", "综述", "review", "overview"],
    "benchmark": ["benchmark", "评测", "evaluation", "baseline"],
    "dataset": ["dataset", "数据", "corpus"],
    "method": ["method", "approach", "算法", "方法"],
    "theory": ["theory", "理论", "analysis", "证明"],
    
    # 系统/工程
    "inference": ["inference", "推理", "部署", "serving"],
    "training": ["training", "训练", "分布式训练"],
    "optimization": ["optimization", "优化", "加速", "efficient"],
    "system": ["system", "架构", "框架", "platform"],
    "mlops": ["mlops", "devops", "pipeline", "ci/cd"],
}

# 领域分类
DOMAIN_RULES = {
    "AI-Core": ["llm", "transformer", "gpt", "claude", "llama", "qwen", "mistral"],
    "AI-Application": ["computer-vision", "nlp", "speech", "robotics", "recommendation"],
    "AI-Engineering": ["inference", "training", "optimization", "mlops", "system"],
    "AI-Method": ["fine-tuning", "prompt-engineering", "rlhf", "quantization", "distillation"],
    "AI-Research": ["survey", "benchmark", "dataset", "method", "theory"],
}

# 输出配置
OUTPUT_DIR = os.path.join(WORKSPACE, "tags")
LOG_PATH = os.path.join(WORKSPACE, "scripts", "auto-tagger.log")

# ============ 工具函数 ============
def log(msg: str):
    line = f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}"
    print(line)
    try:
        with open(LOG_PATH, "a", encoding="utf-8") as f:
            f.write(line + "\n")
    except:
        pass

def extract_text(filepath: str, max_chars: int = 5000) -> str:
    """提取文件内容（前 N 字符）"""
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

def extract_existing_tags(filepath: str) -> List[str]:
    """提取文件已有标签"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tags = []
        
        # 从 frontmatter 提取
        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                frontmatter = content[4:end]
                for line in frontmatter.split('\n'):
                    if line.startswith('tags:'):
                        tag_line = line.replace('tags:', '').strip()
                        if tag_line.startswith('['):
                            # YAML 数组格式
                            tag_str = tag_line.strip('[]')
                            tags = [t.strip().strip('"\'') for t in tag_str.split(',')]
                        else:
                            # 空格分隔格式
                            tags = tag_line.split()
                        break
        
        # 从正文提取 Obsidian 标签
        body_tags = re.findall(r'#([\w/-]+)', content)
        tags.extend(body_tags)
        
        return list(set(tags))
    except:
        return []

def generate_tags(text: str) -> List[str]:
    """基于内容生成标签"""
    text_lower = text.lower()
    tags = []
    
    for tag, keywords in TAG_RULES.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                tags.append(tag)
                break
    
    return list(set(tags))

def generate_domain(tags: List[str]) -> str:
    """基于标签生成领域分类"""
    domain_scores = {domain: 0 for domain in DOMAIN_RULES}
    
    for tag in tags:
        for domain, domain_tags in DOMAIN_RULES.items():
            if tag in domain_tags:
                domain_scores[domain] += 1
    
    # 返回得分最高的领域
    max_domain = max(domain_scores, key=domain_scores.get)
    if domain_scores[max_domain] > 0:
        return max_domain
    return "AI-General"

def update_file_tags(filepath: str, new_tags: List[str], domain: str) -> bool:
    """更新文件标签"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        existing_tags = extract_existing_tags(filepath)
        
        # 合并标签（去重）
        all_tags = list(set(existing_tags + new_tags))
        all_tags.sort()
        
        # 生成标签行
        tags_yaml = f"tags: [{', '.join(all_tags)}]"
        domain_yaml = f"domain: {domain}"
        
        # 如果有 frontmatter，更新它
        if content.startswith('---'):
            end = content.find('---', 3)
            if end > 0:
                frontmatter = content[4:end]
                rest = content[end + 3:]
                
                # 移除旧的 tags 行
                new_frontmatter = '\n'.join(
                    line for line in frontmatter.split('\n')
                    if not line.startswith('tags:') and not line.startswith('domain:')
                )
                
                # 添加新标签
                new_frontmatter = new_frontmatter.strip() + '\n' + tags_yaml + '\n' + domain_yaml
                
                new_content = '---\n' + new_frontmatter + '\n---' + rest
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                return True
        
        # 没有 frontmatter，添加一个
        else:
            new_content = '---\n' + tags_yaml + '\n' + domain_yaml + '\n---\n\n' + content
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return True
            
    except Exception as e:
        log(f"❌ 更新失败 {filepath}: {e}")
        return False

def scan_files(directory: str, extensions: List[str] = ['.md']) -> List[str]:
    """扫描目录中的文件"""
    files = []
    
    if not os.path.exists(directory):
        log(f"⚠️ 目录不存在：{directory}")
        return files
    
    for root, dirs, filenames in os.walk(directory):
        # 跳过 archive 目录
        if '_archive' in root or 'archive' in root:
            continue
        
        for filename in filenames:
            if any(filename.endswith(ext) for ext in extensions):
                files.append(os.path.join(root, filename))
    
    return sorted(files)

# ============ 报告生成 ============
def generate_report(results: List[Dict], output_path: str):
    """生成标签报告"""
    report = f"""# 自动标签报告

**生成时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**处理文件:** {len(results)} 个

---

## 📊 统计

### 按领域分布
"""
    
    domain_counts = {}
    tag_counts = {}
    
    for result in results:
        domain = result.get('domain', 'Unknown')
        domain_counts[domain] = domain_counts.get(domain, 0) + 1
        
        for tag in result.get('tags', []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    for domain, count in sorted(domain_counts.items(), key=lambda x: -x[1]):
        report += f"- **{domain}:** {count} 篇\n"
    
    report += "\n### 热门标签\n\n"
    for tag, count in sorted(tag_counts.items(), key=lambda x: -x[1])[:20]:
        report += f"- `#{tag}`: {count} 篇\n"
    
    report += "\n---\n\n## 📁 详细结果\n\n"
    
    for result in results[:50]:  # 最多显示 50 个
        report += f"### {result['filename']}\n\n"
        report += f"- **领域:** {result['domain']}\n"
        report += f"- **标签:** {', '.join(f'`#{t}`' for t in result['tags'])}\n"
        report += f"- **新增:** {len(result['new_tags'])} 个\n"
        report += f"- **路径:** `{result['path']}`\n\n"
    
    report += f"\n**结束时间:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(report)

# ============ 主流程 ============
def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='自动标签系统')
    parser.add_argument('--dir', type=str, default='all', help='扫描目录 (all/arxiv/medium/notes/memory)')
    parser.add_argument('--dry-run', action='store_true', help='仅预览，不修改文件')
    parser.add_argument('--limit', type=int, default=0, help='限制处理文件数 (0=全部)')
    args = parser.parse_args()
    
    log("🚀 启动自动标签系统")
    
    # 确定扫描目录
    if args.dir == 'all':
        dirs_to_scan = SCAN_DIRS
    else:
        dirs_to_scan = {args.dir: SCAN_DIRS.get(args.dir)}
    
    results = []
    total_files = 0
    
    for dir_name, dir_path in dirs_to_scan.items():
        if not dir_path:
            continue
        
        log(f"📁 扫描 {dir_name}: {dir_path}")
        files = scan_files(dir_path)
        log(f"  → 找到 {len(files)} 个文件")
        
        if args.limit > 0 and total_files >= args.limit:
            break
        
        for filepath in files:
            if args.limit > 0 and total_files >= args.limit:
                break
            
            # 提取内容
            text = extract_text(filepath)
            if not text:
                continue
            
            # 生成标签
            new_tags = generate_tags(text)
            domain = generate_domain(new_tags)
            
            if not new_tags:
                continue
            
            result = {
                'path': filepath,
                'filename': os.path.basename(filepath),
                'tags': new_tags,
                'domain': domain,
                'new_tags': new_tags,  # 简化：假设都是新标签
            }
            results.append(result)
            
            if not args.dry_run:
                if update_file_tags(filepath, new_tags, domain):
                    log(f"  ✅ {os.path.basename(filepath)}: +{len(new_tags)} 标签")
            else:
                log(f"  📝 {os.path.basename(filepath)}: +{len(new_tags)} 标签 (dry-run)")
            
            total_files += 1
    
    # 生成报告
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    report_path = os.path.join(OUTPUT_DIR, f"auto-tag-report-{datetime.now().strftime('%Y%m%d-%H%M')}.md")
    generate_report(results, report_path)
    
    log(f"💾 报告已保存到 {report_path}")
    log(f"✅ 完成 - 处理 {len(results)} 个文件")

if __name__ == "__main__":
    main()

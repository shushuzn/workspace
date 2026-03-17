#!/usr/bin/env python3
"""
知识图谱增强 - 合并现有数据并生成增强版
"""

import json
from pathlib import Path
from datetime import datetime

def merge_graphs():
    """合并知识图谱数据"""
    print("=" * 50)
    print("知识图谱增强 - 合并与增强")
    print("=" * 50)
    print()
    
    # 1. 加载现有图谱
    print("[INFO] 加载现有图谱...")
    graph_file = Path("D:/OpenClaw/workspace/knowledge-graph/graph.json")
    
    if graph_file.exists():
        with open(graph_file, 'r', encoding='utf-8') as f:
            graph = json.load(f)
        print(f"  [OK] 加载 {len(graph.get('entities', []))} 个实体")
        print(f"  [OK] 加载 {len(graph.get('relations', []))} 个关系")
    else:
        graph = {"entities": [], "relations": []}
        print("  [WARN] 图谱文件不存在，创建新图谱")
    
    # 2. 加载摘要
    print("\n[INFO] 加载摘要...")
    summaries_file = Path("D:/OpenClaw/workspace/knowledge-graph/paper-summaries.json")
    
    if summaries_file.exists():
        with open(summaries_file, 'r', encoding='utf-8') as f:
            summaries = json.load(f)
        print(f"  [OK] 加载 {len(summaries)} 篇论文摘要")
        
        # 将摘要信息添加到实体
        for entity in graph["entities"]:
            if entity["type"] == "Paper":
                arxiv_id = entity["properties"].get("arxiv_id", "")
                paper_key = f"paper_{arxiv_id.replace('.', '_')}"
                
                if paper_key in summaries:
                    summary = summaries[paper_key]
                    entity["properties"]["title"] = summary.get("title", "")
                    entity["properties"]["authors"] = summary.get("authors", "")
                    entity["properties"]["key_findings"] = summary.get("key_findings", [])
                    entity["properties"]["methods"] = summary.get("methods", [])
                    entity["properties"]["confidence"] = summary.get("confidence", 0.0)
                    print(f"  [OK] 增强：{arxiv_id}")
    else:
        summaries = {}
        print("  [WARN] 摘要文件不存在")
    
    # 3. 加载关系
    print("\n[INFO] 加载关系...")
    relations_file = Path("D:/OpenClaw/workspace/knowledge-graph/enhanced-relations.json")
    
    if relations_file.exists():
        with open(relations_file, 'r', encoding='utf-8') as f:
            new_relations = json.load(f)
        
        # 合并关系 (去重)
        existing_rels = {(r["source"], r["target"], r["type"]) for r in graph["relations"]}
        
        for rel in new_relations:
            key = (rel["source"], rel["target"], rel["type"])
            if key not in existing_rels:
                graph["relations"].append(rel)
        
        print(f"  [OK] 新增 {len(new_relations)} 个关系")
    else:
        print("  [INFO] 无新增关系")
    
    # 4. 统计
    print("\n[INFO] 统计信息")
    entity_types = {}
    for entity in graph["entities"]:
        etype = entity["type"]
        entity_types[etype] = entity_types.get(etype, 0) + 1
    
    relation_types = {}
    for rel in graph["relations"]:
        rtype = rel["type"]
        relation_types[rtype] = relation_types.get(rtype, 0) + 1
    
    print(f"  总实体：{len(graph['entities'])} 个")
    print(f"  总关系：{len(graph['relations'])} 个")
    print(f"  实体类型：{entity_types}")
    print(f"  关系类型：{relation_types}")
    
    # 5. 保存增强图谱
    print("\n[INFO] 保存增强图谱...")
    output_file = Path("D:/OpenClaw/workspace/knowledge-graph/enhanced-graph.json")
    
    enhanced_graph = {
        "metadata": {
            "created": datetime.now().isoformat(),
            "version": "2.0-enhanced",
            "source": "OpenClaw Knowledge Graph"
        },
        "stats": {
            "total_entities": len(graph["entities"]),
            "total_relations": len(graph["relations"]),
            "entity_types": entity_types,
            "relation_types": relation_types,
            "papers_with_summaries": len(summaries)
        },
        "entities": graph["entities"],
        "relations": graph["relations"]
    }
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(enhanced_graph, f, indent=2, ensure_ascii=False)
    
    print(f"  [OK] 已保存：{output_file}")
    
    # 6. 生成 Mermaid 可视化
    print("\n[INFO] 生成 Mermaid 可视化...")
    mermaid_file = Path("D:/OpenClaw/workspace/knowledge-graph/enhanced-graph.mmd")
    
    with open(mermaid_file, 'w', encoding='utf-8') as f:
        f.write("graph TD\n")
        
        # 添加实体节点
        for entity in graph["entities"][:20]:  # 限制前 20 个
            eid = entity["id"]
            etype = entity["type"]
            props = entity["properties"]
            
            if etype == "Paper":
                label = props.get("title", eid)[:40]
                arxiv = props.get("arxiv_id", "")
                f.write(f'    {eid}["📄 {label}\\n(arXiv:{arxiv})"]\n')
            elif etype == "Concept":
                label = props.get("name", eid)[:40]
                f.write(f'    {eid}["💡 {label}"]\n')
        
        # 添加关系边
        for rel in graph["relations"][:30]:  # 限制前 30 个
            f.write(f'    {rel["source"]} --{rel["type"]}--> {rel["target"]}\n')
    
    print(f"  [OK] 已保存：{mermaid_file}")
    
    print("\n" + "=" * 50)
    print("✅ 知识图谱增强完成！")
    print("=" * 50)
    
    return enhanced_graph

if __name__ == "__main__":
    merge_graphs()

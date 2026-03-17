#!/usr/bin/env python3
"""
Knowledge Graph Generator
Auto-builds knowledge graph from papers and sessions
Outputs: Interactive HTML visualization with D3.js
"""

import json
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

OUTPUT_DIR = "/opt/openclaw/knowledge-graph"
LOG_FILE = "/var/log/knowledge-graph.log"

def log(message):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_msg = f"[{timestamp}] {message}"
    print(log_msg)
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, 'a') as f:
        f.write(log_msg + '\n')

def extract_entities():
    """Extract entities from papers and sessions"""
    entities = []
    entity_counts = defaultdict(int)
    
    # Extract from arXiv papers
    arxiv_dir = Path("/opt/openclaw/papers/arxiv")
    if arxiv_dir.exists():
        for json_file in arxiv_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                papers = data.get('papers', []) if isinstance(data, dict) else data
                
                for paper in papers:
                    # Extract keywords as entities
                    for kw in paper.get('matched_keywords', []):
                        entities.append({
                            'id': f"keyword_{kw.lower().replace(' ', '_')}",
                            'label': kw,
                            'type': 'keyword',
                            'group': 1
                        })
                        entity_counts[kw] += 1
                    
                    # Extract categories as entities
                    for cat in paper.get('categories', []):
                        entities.append({
                            'id': f"category_{cat}",
                            'label': cat,
                            'type': 'category',
                            'group': 2
                        })
                    
                    # Extract authors as entities
                    for author in paper.get('authors', [])[:3]:  # Top 3 authors
                        entities.append({
                            'id': f"author_{author.replace(' ', '_').lower()}",
                            'label': author,
                            'type': 'author',
                            'group': 3
                        })
            except Exception as e:
                log(f"Error processing {json_file}: {e}")
    
    # Deduplicate entities
    seen = set()
    unique_entities = []
    for entity in entities:
        if entity['id'] not in seen:
            seen.add(entity['id'])
            entity['count'] = entity_counts.get(entity['label'], 1)
            unique_entities.append(entity)
    
    return unique_entities

def extract_relationships(entities):
    """Extract relationships between entities"""
    relationships = []
    
    # Group entities by type
    keywords = [e for e in entities if e['type'] == 'keyword']
    categories = [e for e in entities if e['type'] == 'category']
    
    # Create relationships: keywords connected to categories
    for kw in keywords:
        for cat in categories:
            # Simple heuristic: connect if category matches keyword context
            if any(term in kw['label'].lower() for term in ['learning', 'neural', 'ai']):
                if cat['label'] in ['cs.AI', 'cs.LG', 'cs.NE']:
                    relationships.append({
                        'source': kw['id'],
                        'target': cat['id'],
                        'type': 'belongs_to',
                        'value': 1
                    })
    
    # Connect related keywords
    for i, kw1 in enumerate(keywords[:10]):  # Limit for clarity
        for kw2 in keywords[i+1:15]:
            # Connect if they share words
            words1 = set(kw1['label'].lower().split())
            words2 = set(kw2['label'].lower().split())
            if words1 & words2:  # Intersection
                relationships.append({
                    'source': kw1['id'],
                    'target': kw2['id'],
                    'type': 'related_to',
                    'value': len(words1 & words2)
                })
    
    return relationships

def generate_html_graph(entities, relationships):
    """Generate interactive HTML knowledge graph with D3.js"""
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 Knowledge Graph - OpenClaw</title>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
            background: linear-gradient(135deg, #1e1e1e 0%, #2d2d30 100%); 
            color: #fff;
            overflow: hidden;
        }}
        #graph-container {{ 
            width: 100vw; 
            height: 100vh; 
        }}
        .header {{
            position: absolute;
            top: 20px;
            left: 20px;
            z-index: 10;
            background: rgba(0,0,0,0.7);
            padding: 20px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }}
        h1 {{ font-size: 1.8em; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }}
        .stats {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-top: 15px; }}
        .stat {{ background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; text-align: center; }}
        .stat-value {{ font-size: 1.5em; font-weight: bold; color: #61dafb; }}
        .stat-label {{ font-size: 0.85em; opacity: 0.7; }}
        .legend {{
            position: absolute;
            bottom: 20px;
            left: 20px;
            z-index: 10;
            background: rgba(0,0,0,0.7);
            padding: 15px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }}
        .legend-item {{ display: flex; align-items: center; gap: 10px; margin: 8px 0; }}
        .legend-color {{ width: 16px; height: 16px; border-radius: 50%; }}
        .tooltip {{
            position: absolute;
            background: rgba(0,0,0,0.9);
            padding: 15px;
            border-radius: 8px;
            font-size: 0.9em;
            pointer-events: none;
            z-index: 100;
            max-width: 300px;
            border: 1px solid rgba(255,255,255,0.2);
        }}
        .controls {{
            position: absolute;
            top: 20px;
            right: 20px;
            z-index: 10;
            background: rgba(0,0,0,0.7);
            padding: 15px;
            border-radius: 12px;
            backdrop-filter: blur(10px);
        }}
        button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 8px;
            cursor: pointer;
            margin: 5px 0;
            width: 100%;
            font-size: 0.9em;
            transition: transform 0.2s;
        }}
        button:hover {{ transform: scale(1.05); }}
        .node {{ stroke: #fff; stroke-width: 2px; }}
        .link {{ stroke: #666; stroke-opacity: 0.6; }}
    </style>
</head>
<body>
    <div id="graph-container"></div>
    
    <div class="header">
        <h1>🧠 Knowledge Graph</h1>
        <p>OpenClaw Research Knowledge</p>
        <div class="stats">
            <div class="stat">
                <div class="stat-value" id="entity-count">{len(entities)}</div>
                <div class="stat-label">Entities</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="relationship-count">{len(relationships)}</div>
                <div class="stat-label">Relationships</div>
            </div>
            <div class="stat">
                <div class="stat-value" id="density">0</div>
                <div class="stat-label">Density</div>
            </div>
        </div>
    </div>
    
    <div class="legend">
        <div class="legend-item">
            <div class="legend-color" style="background: #667eea;"></div>
            <span>Keywords</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #764ba2;"></div>
            <span>Categories</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background: #f093fb;"></div>
            <span>Authors</span>
        </div>
    </div>
    
    <div class="controls">
        <button onclick="zoomToFit()">🔍 Zoom to Fit</button>
        <button onclick="toggleLabels()">🏷️ Toggle Labels</button>
        <button onclick="restartSimulation()">🔄 Restart</button>
    </div>
    
    <div class="tooltip" id="tooltip" style="display: none;"></div>

    <script>
        // Graph data
        const graphData = {{
            nodes: {json.dumps(entities)},
            links: {json.dumps(relationships)}
        }};
        
        // Color scale
        const colorScale = d3.scaleOrdinal()
            .domain([1, 2, 3])
            .range(['#667eea', '#764ba2', '#f093fb']);
        
        // SVG setup
        const width = window.innerWidth;
        const height = window.innerHeight;
        
        const svg = d3.select("#graph-container")
            .append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("viewBox", [0, 0, width, height]);
        
        // Zoom behavior
        const zoom = d3.zoom()
            .scaleExtent([0.1, 4])
            .on("zoom", (event) => {{
                g.attr("transform", event.transform);
            }});
        
        svg.call(zoom);
        
        const g = svg.append("g");
        
        // Force simulation
        const simulation = d3.forceSimulation()
            .force("link", d3.forceLink().id(d => d.id).distance(100))
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .force("collide", d3.forceCollide().radius(30));
        
        // Create links
        const link = g.append("g")
            .selectAll("line")
            .data(graphData.links)
            .join("line")
            .attr("class", "link")
            .attr("stroke-width", d => Math.sqrt(d.value) * 2);
        
        // Create nodes
        const node = g.append("g")
            .selectAll("circle")
            .data(graphData.nodes)
            .join("circle")
            .attr("class", "node")
            .attr("r", d => 8 + (d.count || 1) * 2)
            .attr("fill", d => colorScale(d.group))
            .call(d3.drag()
                .on("start", dragstarted)
                .on("drag", dragged)
                .on("end", dragended));
        
        // Add labels
        const labels = g.append("g")
            .selectAll("text")
            .data(graphData.nodes)
            .join("text")
            .text(d => d.label)
            .attr("font-size", "12px")
            .attr("fill", "#fff")
            .attr("dx", 15)
            .attr("dy", 4)
            .style("opacity", 0.8);
        
        // Tooltip
        const tooltip = d3.select("#tooltip");
        
        node.on("mouseover", (event, d) => {{
            tooltip.style("display", "block")
                .html(`
                    <strong>${{d.label}}</strong><br>
                    <span style="opacity: 0.7">Type: ${{d.type}}</span><br>
                    <span style="opacity: 0.7">Count: ${{d.count || 1}}</span>
                `);
        }})
        .on("mousemove", (event) => {{
            tooltip.style("left", (event.pageX + 15) + "px")
                .style("top", (event.pageY - 15) + "px");
        }})
        .on("mouseout", () => {{
            tooltip.style("display", "none");
        }});
        
        // Simulation tick
        simulation.nodes(graphData.nodes).on("tick", () => {{
            link
                .attr("x1", d => d.source.x)
                .attr("y1", d => d.source.y)
                .attr("x2", d => d.target.x)
                .attr("y2", d => d.target.y);
            
            node
                .attr("cx", d => d.x)
                .attr("cy", d => d.y);
            
            labels
                .attr("x", d => d.x)
                .attr("y", d => d.y);
        }});
        
        simulation.force("link").links(graphData.links);
        
        // Drag functions
        function dragstarted(event, d) {{
            if (!event.active) simulation.alphaTarget(0.3).restart();
            d.fx = d.x;
            d.fy = d.y;
        }}
        
        function dragged(event, d) {{
            d.fx = event.x;
            d.fy = event.y;
        }}
        
        function dragended(event, d) {{
            if (!event.active) simulation.alphaTarget(0);
            d.fx = null;
            d.fy = null;
        }}
        
        // Control functions
        function zoomToFit() {{
            svg.transition().duration(750).call(
                zoom.transform,
                d3.zoomIdentity
            );
        }}
        
        function toggleLabels() {{
            labels.style("opacity", l => l.style("opacity") == 0.8 ? 0 : 0.8);
        }}
        
        function restartSimulation() {{
            simulation.alpha(1).restart();
        }}
        
        // Update density
        const density = (graphData.links.length / graphData.nodes.length).toFixed(2);
        document.getElementById("density").textContent = density;
    </script>
</body>
</html>
"""
    return html

def main():
    """Main function"""
    log("🧠 Knowledge Graph Generator started")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Extract entities
    log("📊 Extracting entities...")
    entities = extract_entities()
    log(f"   Found {len(entities)} entities")
    
    # Extract relationships
    log("🔗 Extracting relationships...")
    relationships = extract_relationships(entities)
    log(f"   Found {len(relationships)} relationships")
    
    # Generate HTML visualization
    log("🎨 Generating HTML visualization...")
    html = generate_html_graph(entities, relationships)
    
    output_file = f"{OUTPUT_DIR}/knowledge-graph-{datetime.now().strftime('%Y%m%d-%H%M%S')}.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    log(f"✅ Knowledge graph saved to: {output_file}")
    
    # Save JSON data
    json_file = f"{OUTPUT_DIR}/graph-data-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'entities': entities,
            'relationships': relationships,
            'generated_at': datetime.now().isoformat()
        }, f, indent=2)
    
    log(f"✅ Graph data saved to: {json_file}")
    log("\n🎉 Knowledge Graph Generator complete!")
    log(f"\n📊 Summary:")
    log(f"   - Entities: {len(entities)}")
    log(f"   - Relationships: {len(relationships)}")
    log(f"   - HTML visualization: {output_file}")

if __name__ == "__main__":
    main()

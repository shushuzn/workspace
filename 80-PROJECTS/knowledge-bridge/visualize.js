/**
 * Knowledge Bridge - Visualization
 * Generates interactive HTML visualization of the knowledge graph
 */

const fs = require('fs');
const { graph } = require('./knowledgeGraph');

// Load the saved graph
graph.load('pla-knowledge-graph.json');

const visData = graph.getVisData();

// Domain colors
const domainColors = {
  'chemistry': { bg: '#34A853', border: '#2E7D32' },
  'programming': { bg: '#4285F4', border: '#1565C0' },
  'medicine': { bg: '#EA4335', border: '#C62828' },
  'engineering': { bg: '#9C27B0', border: '#6A1B9A' },
  'cooking': { bg: '#FF9800', border: '#E65100' }
};

// Generate vis.js nodes
const nodes = visData.nodes.map(n => ({
  id: n.id,
  label: n.label,
  title: n.title,
  color: {
    background: domainColors[n.domain]?.bg || '#9E9E9E',
    border: domainColors[n.domain]?.border || '#757575',
    highlight: { background: '#FFF', border: '#000' }
  },
  font: { color: '#FFF', size: 14 },
  domain: n.domain
}));

// Generate vis.js edges
const edges = visData.edges.map(e => ({
  from: e.from,
  to: e.to,
  title: e.title,
  value: e.value || 1
}));

const html = `<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <title>Knowledge Bridge - 知识的六度分隔</title>
  <script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      background: #1a1a2e;
      color: #eee;
    }
    header {
      background: linear-gradient(135deg, #16213e, #0f3460);
      padding: 20px 30px;
      border-bottom: 2px solid #e94560;
    }
    h1 { font-size: 24px; margin-bottom: 5px; }
    .subtitle { color: #888; font-size: 14px; }
    #network {
      width: 100%;
      height: calc(100vh - 180px);
      border-bottom: 1px solid #333;
    }
    #legend {
      display: flex;
      gap: 20px;
      padding: 15px 30px;
      background: #16213e;
      flex-wrap: wrap;
    }
    .legend-item {
      display: flex;
      align-items: center;
      gap: 8px;
      font-size: 13px;
    }
    .legend-color {
      width: 16px;
      height: 16px;
      border-radius: 4px;
    }
    #analogy-panel {
      position: fixed;
      right: 20px;
      top: 100px;
      width: 320px;
      max-height: calc(100vh - 220px);
      background: #16213e;
      border-radius: 12px;
      padding: 20px;
      box-shadow: 0 8px 32px rgba(0,0,0,0.4);
      overflow-y: auto;
      display: none;
    }
    #analogy-panel.show { display: block; }
    #analogy-panel h3 {
      color: #e94560;
      margin-bottom: 15px;
      font-size: 16px;
    }
    .analogy-item {
      background: #1a1a2e;
      border-radius: 8px;
      padding: 12px;
      margin-bottom: 10px;
    }
    .analogy-item .domains {
      font-size: 11px;
      color: #888;
      margin-bottom: 6px;
    }
    .analogy-item .text {
      font-size: 13px;
      line-height: 1.5;
    }
    .instructions {
      position: fixed;
      bottom: 20px;
      left: 20px;
      background: rgba(22, 33, 62, 0.9);
      padding: 12px 16px;
      border-radius: 8px;
      font-size: 12px;
      color: #888;
    }
  </style>
</head>
<body>
  <header>
    <h1>🧠 Knowledge Bridge</h1>
    <div class="subtitle">知识的六度分隔 — Cross-domain knowledge graph</div>
  </header>

  <div id="network"></div>

  <div id="legend">
    <span style="color:#888;font-size:12px;">Domain:</span>
    ${Object.entries(domainColors).map(([d, c]) =>
      `<div class="legend-item"><div class="legend-color" style="background:${c.bg}"></div>${d}</div>`
    ).join('')}
  </div>

  <div id="analogy-panel">
    <h3>🔗 Cross-Domain Analogies</h3>
    <div id="analogy-list"></div>
  </div>

  <div class="instructions">
    💡 Click a node to see related cross-domain analogies
  </div>

  <script>
    const nodes = new vis.DataSet(${JSON.stringify(nodes)});
    const edges = new vis.DataSet(${JSON.stringify(edges)});

    const container = document.getElementById('network');
    const data = { nodes, edges };

    const options = {
      nodes: {
        shape: 'dot',
        size: 20,
        borderWidth: 2,
        shadow: true
      },
      edges: {
        width: 1,
        color: { color: '#444', highlight: '#e94560' },
        smooth: { type: 'continuous' }
      },
      physics: {
        stabilization: { iterations: 200 },
        barnesHut: {
          gravitationalConstant: -3000,
          springLength: 200
        }
      },
      interaction: {
        hover: true,
        tooltipDelay: 200
      }
    };

    const network = new vis.Network(container, data, options);

    // Show analogies on click
    const analogyList = document.getElementById('analogy-list');
    const analogyPanel = document.getElementById('analogy-panel');
    const analogies = ${JSON.stringify(graph.analogyBank)};

    network.on('click', function(params) {
      if (params.nodes.length > 0) {
        const nodeId = params.nodes[0];
        const node = nodes.get(nodeId);

        // Find analogies for this node
        const related = analogies.filter(a => a.source === nodeId || a.target === nodeId);

        if (related.length > 0) {
          analogyList.innerHTML = related.map(a => {
            const otherId = a.source === nodeId ? a.target : a.source;
            const other = nodes.get(otherId);
            return \`
              <div class="analogy-item">
                <div class="domains">\${node.label} (\${node.domain}) ↔ \${other.label} (\${other.domain})</div>
                <div class="text">\${a.text}</div>
              </div>
            \`;
          }).join('');
          analogyPanel.classList.add('show');
        }
      } else {
        analogyPanel.classList.remove('show');
      }
    });
  </script>
</body>
</html>`;

fs.writeFileSync('knowledge-graph.html', html);
console.log('Visualization saved to: knowledge-graph.html');
console.log('Open it in a browser to explore the knowledge graph!');

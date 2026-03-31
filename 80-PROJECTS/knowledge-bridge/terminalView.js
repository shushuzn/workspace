/**
 * Knowledge Bridge - Terminal Visualization
 * ASCII art knowledge graph for terminal display (plain text version)
 */

const { graph } = require('./knowledgeGraph');

graph.load('pla-knowledge-graph.json');

console.log('\n');
console.log('============================================================');
console.log('  KNOWLEDGE BRIDGE -- 知识的六度分隔');
console.log('  Cross-Domain Knowledge Graph');
console.log('============================================================');
console.log('');

// Domain labels
const domainLabels = {
  chemistry: '[化学]',
  programming: '[编程]',
  medicine: '[医学]',
  engineering: '[工程]',
  cooking: '[烹饪]'
};

// Print concepts by domain
console.log('------------------------------------------------------------');
console.log('  DOMAIN CLUSTERS');
console.log('------------------------------------------------------------');

const byDomain = {};
[...graph.nodes.values()].forEach(n => {
  if (!byDomain[n.domain]) byDomain[n.domain] = [];
  byDomain[n.domain].push(n);
});

Object.entries(byDomain).forEach(([domain, nodes]) => {
  const label = domainLabels[domain] || `[${domain}]`;
  console.log(`\n  ${label}`);
  nodes.forEach(n => {
    // Find connections
    const connections = graph.edges.filter(e => e.from === n.id || e.to === n.id);
    const connectedLabels = connections.map(e => {
      const otherId = e.from === n.id ? e.to : e.from;
      const other = graph.nodes.get(otherId);
      return other ? other.label : '';
    }).filter(Boolean);

    console.log(`    |-> ${n.label}`);
    if (connectedLabels.length > 0) {
      console.log(`        -> ${connectedLabels.slice(0, 4).join(', ')}${connectedLabels.length > 4 ? '...' : ''}`);
    }
  });
});

// Print analogies
console.log('\n');
console.log('------------------------------------------------------------');
console.log('  CROSS-DOMAIN ANALOGIES -- 跨域类比');
console.log('------------------------------------------------------------');

graph.analogyBank.forEach((a, i) => {
  const source = graph.nodes.get(a.source);
  const target = graph.nodes.get(a.target);
  if (!source || !target) return;

  console.log(`\n  ${i + 1}. ${source.label} (${source.domain})`);
  console.log(`     <==> ${target.label} (${target.domain})`);
  console.log(`     "${a.text}"`);
});

console.log('\n');
console.log('------------------------------------------------------------');
console.log('  GRAPH STATISTICS');
console.log('------------------------------------------------------------');
console.log(`    Concepts:    ${graph.nodes.size}`);
console.log(`    Connections: ${graph.edges.length}`);
console.log(`    Analogies:   ${graph.analogyBank.length}`);
console.log(`    Domains:     ${[...graph.domains].join(', ')}`);
console.log('\n');

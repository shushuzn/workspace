/**
 * Knowledge Bridge - Core Graph System
 * "知识的六度分隔" - Cross-domain knowledge graph with analogies
 */

const { v4: uuidv4 } = require('uuid');
const fs = require('fs');
const path = require('path');

// Graph data structure
class KnowledgeGraph {
  constructor() {
    this.nodes = new Map();      // id -> { id, label, domain, connections: [] }
    this.edges = [];             // { from, to, type, strength, analogy }
    this.domains = new Set();    // track all domains
    this.analogyBank = [];       // cross-domain analogies
  }

  // Add a concept node
  addConcept(label, domain, description = '') {
    const id = uuidv4();
    this.nodes.set(id, {
      id,
      label,
      domain,
      description,
      connections: [],
      createdAt: new Date().toISOString()
    });
    this.domains.add(domain);
    return id;
  }

  // Add connection between concepts
  connect(fromId, toId, type = 'related', strength = 1) {
    if (!this.nodes.has(fromId) || !this.nodes.has(toId)) {
      return false;
    }

    const edge = { from: fromId, to: toId, type, strength, id: uuidv4() };
    this.edges.push(edge);

    // Update node connections
    this.nodes.get(fromId).connections.push(toId);
    this.nodes.get(toId).connections.push(fromId);

    return true;
  }

  // Find concepts by domain
  findByDomain(domain) {
    return [...this.nodes.values()].filter(n => n.domain === domain);
  }

  // Find cross-domain connections
  findCrossDomainConnections(conceptId) {
    const concept = this.nodes.get(conceptId);
    if (!concept) return [];

    return this.edges
      .filter(e => e.from === conceptId || e.to === conceptId)
      .map(e => {
        const otherId = e.from === conceptId ? e.to : e.from;
        return this.nodes.get(otherId);
      })
      .filter(n => n && n.domain !== concept.domain);
  }

  // Add an analogy between concepts (by ID)
  addAnalogy(sourceId, targetId, analogyText, contributor = 'system') {
    const analogy = {
      id: uuidv4(),
      source: sourceId,  // concept ID
      target: targetId,  // concept ID
      text: analogyText,
      contributor,
      createdAt: new Date().toISOString(),
      usefulness: 0
    };
    this.analogyBank.push(analogy);
    return analogy;
  }

  // Find analogies for a concept
  findAnalogies(conceptId) {
    return this.analogyBank.filter(
      a => a.source === conceptId || a.target === conceptId
    );
  }

  // Get graph data for visualization
  getVisData() {
    const nodes = [...this.nodes.values()].map(n => ({
      id: n.id,
      label: n.label,
      domain: n.domain,
      title: n.description,
      color: this.domainColor(n.domain)
    }));

    const edges = this.edges.map(e => ({
      from: e.from,
      to: e.to,
      title: e.type,
      value: e.strength
    }));

    return { nodes, edges };
  }

  // Assign color to domain
  domainColor(domain) {
    const colors = {
      'programming': '#4285F4',
      'chemistry': '#34A853',
      'biology': '#EA4335',
      'physics': '#9C27B0',
      'cooking': '#FF9800',
      'medicine': '#00BCD4',
      'business': '#795548',
      'daily': '#607D8B'
    };
    return colors[domain] || '#9E9E9E';
  }

  // Save to file
  save(filename = 'knowledge-graph.json') {
    const data = {
      nodes: [...this.nodes.entries()],
      edges: this.edges,
      analogyBank: this.analogyBank,
      domains: [...this.domains],
      savedAt: new Date().toISOString()
    };
    fs.writeFileSync(path.join('data', filename), JSON.stringify(data, null, 2));
    return path.join('data', filename);
  }

  // Load from file
  load(filename = 'knowledge-graph.json') {
    const filepath = path.join('data', filename);
    if (!fs.existsSync(filepath)) return false;

    const data = JSON.parse(fs.readFileSync(filepath));
    this.nodes = new Map(data.nodes);
    this.edges = data.edges;
    this.analogyBank = data.analogyBank;
    this.domains = new Set(data.domains);
    return true;
  }
}

// Create global instance
const graph = new KnowledgeGraph();

module.exports = { KnowledgeGraph, graph };

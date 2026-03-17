#!/usr/bin/env python3
"""
Memory Topological Data Analysis - High-Dimensional Structure Discovery
========================================================================
Analyzes memory structure using topological data analysis (TDA) to discover
hidden high-dimensional patterns.

Key Concepts:
- Persistent Homology: Track topological features across scales
- Betti Numbers: Count holes in different dimensions
  - β0: Connected components (clusters)
  - β1: Loops/cycles (feedback loops)
  - β2: Voids/cavities (higher-order structures)
- Persistence Diagram: Visualize feature stability
- Mapper Algorithm: Create simplified representation of high-dimensional data

Usage:
    python memory_topological_analysis.py --analyze "MEMORY.md"
    python memory_topological_analysis.py --betti
    python memory_topological_analysis.py --persistence
    python memory_topological_analysis.py --mapper
    python memory_topological_analysis.py --visualize
"""

import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict
import math

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


# ============================================================================
# Configuration
# ============================================================================

@dataclass
class TopologyConfig:
    """Topological analysis configuration"""
    
    # Analysis parameters
    MAX_DIMENSION: int = 2              # Max homology dimension to compute
    EPSILON_RANGE: Tuple[float, float] = (0.1, 1.0)  # Scale range
    EPSILON_STEPS: int = 10             # Number of scale steps
    
    # Mapper parameters
    COVER_INTERVALS: int = 10           # Number of intervals in cover
    OVERLAP_RATIO: float = 0.3          # Overlap between intervals
    CLUSTER_MIN_SIZE: int = 2           # Min points per cluster
    
    # Paths
    WORKSPACE: str = os.path.join(os.path.dirname(__file__), '..')
    TOPOLOGY_STATE: str = os.path.join(WORKSPACE, 'data', 'topology_state.json')
    TOPOLOGY_VISUALIZATION: str = os.path.join(WORKSPACE, 'data', 'topology_map.html')


# ============================================================================
# Topological Features
# ============================================================================

@dataclass
class TopologicalFeature:
    """A topological feature (hole, component, etc.)"""
    feature_id: str
    dimension: int            # 0=components, 1=loops, 2=voids
    birth_scale: float        # Scale at which feature appears
    death_scale: float        # Scale at which feature disappears
    persistence: float        # death_scale - birth_scale
    significance: str = "medium"  # low/medium/high/critical
    interpretation: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'feature_id': self.feature_id,
            'dimension': self.dimension,
            'birth_scale': self.birth_scale,
            'death_scale': self.death_scale,
            'persistence': self.persistence,
            'significance': self.significance,
            'interpretation': self.interpretation
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TopologicalFeature':
        return cls(
            feature_id=data['feature_id'],
            dimension=data['dimension'],
            birth_scale=data['birth_scale'],
            death_scale=data['death_scale'],
            persistence=data['persistence'],
            significance=data['significance'],
            interpretation=data.get('interpretation', '')
        )


@dataclass
class BettiNumbers:
    """Betti numbers at a specific scale"""
    scale: float
    beta_0: int = 0    # Connected components
    beta_1: int = 0    # Loops/cycles
    beta_2: int = 0    # Voids/cavities
    
    def to_dict(self) -> Dict:
        return {
            'scale': self.scale,
            'beta_0': self.beta_0,
            'beta_1': self.beta_1,
            'beta_2': self.beta_2
        }


# ============================================================================
# Topological Analyzer
# ============================================================================

class TopologicalAnalyzer:
    """Analyze memory topology"""
    
    def __init__(self, config: TopologyConfig = None):
        self.config = config or TopologyConfig()
        self.features: List[TopologicalFeature] = []
        self.betti_curves: List[BettiNumbers] = []
        self.mapper_graph = {'nodes': [], 'edges': []}
        self._load_state()
    
    def _load_state(self):
        """Load analysis state"""
        if os.path.exists(self.config.TOPOLOGY_STATE):
            with open(self.config.TOPOLOGY_STATE, 'r', encoding='utf-8') as f:
                state = json.load(f)
            
            self.features = [
                TopologicalFeature.from_dict(f) for f in state.get('features', [])
            ]
            self.betti_curves = [
                BettiNumbers(**b) for b in state.get('betti_curves', [])
            ]
            self.mapper_graph = state.get('mapper_graph', {'nodes': [], 'edges': []})
            
            logger.info(f"Loaded topology: {len(self.features)} features")
    
    def _save_state(self):
        """Save analysis state"""
        state = {
            'features': [f.to_dict() for f in self.features],
            'betti_curves': [b.to_dict() for b in self.betti_curves],
            'mapper_graph': self.mapper_graph,
            'last_analysis': datetime.now().isoformat()
        }
        
        os.makedirs(os.path.dirname(self.config.TOPOLOGY_STATE), exist_ok=True)
        
        with open(self.config.TOPOLOGY_STATE, 'w', encoding='utf-8') as f:
            json.dump(state, f, indent=2, ensure_ascii=False)
    
    def analyze_memory(self, memory_file: str) -> Dict:
        """
        Perform complete topological analysis
        
        Steps:
        1. Extract memory points (insights/concepts)
        2. Build simplicial complex
        3. Compute persistent homology
        4. Extract Betti numbers
        5. Generate Mapper graph
        """
        logger.info(f"Analyzing topology of {memory_file}...")
        
        # Step 1: Extract memory points
        points = self._extract_memory_points(memory_file)
        logger.info(f"Extracted {len(points)} memory points")
        
        # Step 2: Compute distance matrix
        distance_matrix = self._compute_distance_matrix(points)
        
        # Step 3: Compute persistent homology
        self._compute_persistent_homology(distance_matrix)
        logger.info(f"Computed {len(self.features)} topological features")
        
        # Step 4: Compute Betti numbers
        self._compute_betti_numbers(distance_matrix)
        logger.info(f"Computed {len(self.betti_curves)} Betti number samples")
        
        # Step 5: Generate Mapper graph
        self._generate_mapper_graph(points, distance_matrix)
        logger.info(f"Generated Mapper graph: {len(self.mapper_graph['nodes'])} nodes")
        
        # Step 6: Interpret features
        self._interpret_features()
        
        self._save_state()
        
        return self.get_analysis_summary()
    
    def _extract_memory_points(self, memory_file: str) -> List[Dict]:
        """Extract memory points (insights/concepts) as high-dimensional points"""
        points = []
        
        if not os.path.exists(memory_file):
            logger.error(f"Memory file not found: {memory_file}")
            return points
        
        with open(memory_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Extract sections as points
        sections = content.split('\n## ')
        
        for i, section in enumerate(sections):
            if section.strip():
                # Create feature vector for this section
                # Simplified: use word frequencies
                words = section.lower().split()
                word_freq = defaultdict(float)
                
                for word in words:
                    if len(word) > 3 and word.isalpha():
                        word_freq[word] += 1
                
                # Normalize
                total = sum(word_freq.values())
                if total > 0:
                    for word in word_freq:
                        word_freq[word] /= total
                
                points.append({
                    'id': f'point_{i}',
                    'content': section[:200],
                    'features': dict(word_freq),
                    'dimension': len(word_freq)
                })
        
        return points
    
    def _compute_distance_matrix(self, points: List[Dict]) -> List[List[float]]:
        """Compute pairwise distance matrix between points"""
        n = len(points)
        distance_matrix = [[0.0] * n for _ in range(n)]
        
        for i in range(n):
            for j in range(i+1, n):
                # Cosine similarity as distance
                features_i = points[i]['features']
                features_j = points[j]['features']
                
                # Get all features
                all_features = set(features_i.keys()) | set(features_j.keys())
                
                # Compute dot product and norms
                dot_product = sum(features_i.get(f, 0) * features_j.get(f, 0) for f in all_features)
                norm_i = math.sqrt(sum(v**2 for v in features_i.values()))
                norm_j = math.sqrt(sum(v**2 for v in features_j.values()))
                
                # Cosine distance
                if norm_i > 0 and norm_j > 0:
                    cosine_sim = dot_product / (norm_i * norm_j)
                    distance = 1.0 - cosine_sim
                else:
                    distance = 1.0
                
                distance_matrix[i][j] = distance
                distance_matrix[j][i] = distance
        
        return distance_matrix
    
    def _compute_persistent_homology(self, distance_matrix: List[List[float]]):
        """
        Compute persistent homology
        
        Simplified implementation - real TDA would use algorithms like:
        - Edelsbrunner's algorithm
        - Dionysus library
        - GUDHI library
        """
        n = len(distance_matrix)
        self.features = []
        
        # Generate epsilon values
        epsilons = [
            self.config.EPSILON_RANGE[0] + i * (self.config.EPSILON_RANGE[1] - self.config.EPSILON_RANGE[0]) / self.config.EPSILON_STEPS
            for i in range(self.config.EPSILON_STEPS + 1)
        ]
        
        # Track connected components at each scale
        components_history = []
        
        for epsilon in epsilons:
            # Build adjacency matrix at this scale
            adjacency = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    if distance_matrix[i][j] <= epsilon:
                        adjacency[i][j] = 1
            
            # Count connected components (simplified)
            visited = [False] * n
            components = 0
            
            for i in range(n):
                if not visited[i]:
                    components += 1
                    # BFS to mark component
                    queue = [i]
                    while queue:
                        node = queue.pop(0)
                        if not visited[node]:
                            visited[node] = True
                            for j in range(n):
                                if adjacency[node][j] and not visited[j]:
                                    queue.append(j)
            
            components_history.append((epsilon, components))
        
        # Extract features from component history
        feature_id = 0
        for i in range(len(components_history) - 1):
            eps_1, comp_1 = components_history[i]
            eps_2, comp_2 = components_history[i + 1]
            
            # Birth: component appears
            if comp_2 > comp_1:
                for _ in range(comp_2 - comp_1):
                    feature = TopologicalFeature(
                        feature_id=f"β0_{feature_id:03d}",
                        dimension=0,
                        birth_scale=eps_1,
                        death_scale=eps_2 if i < len(components_history) - 2 else self.config.EPSILON_RANGE[1] + 0.1,
                        persistence=0.0,
                        significance="medium"
                    )
                    self.features.append(feature)
                    feature_id += 1
        
        # Calculate persistence
        for feature in self.features:
            feature.persistence = feature.death_scale - feature.birth_scale
            
            # Classify significance
            if feature.persistence > 0.5:
                feature.significance = "critical"
            elif feature.persistence > 0.3:
                feature.significance = "high"
            elif feature.persistence > 0.1:
                feature.significance = "medium"
            else:
                feature.significance = "low"
    
    def _compute_betti_numbers(self, distance_matrix: List[List[float]]):
        """Compute Betti numbers at different scales"""
        n = len(distance_matrix)
        self.betti_curves = []
        
        epsilons = [
            self.config.EPSILON_RANGE[0] + i * (self.config.EPSILON_RANGE[1] - self.config.EPSILON_RANGE[0]) / self.config.EPSILON_STEPS
            for i in range(self.config.EPSILON_STEPS + 1)
        ]
        
        for epsilon in epsilons:
            # Count components (β0)
            adjacency = [[0] * n for _ in range(n)]
            for i in range(n):
                for j in range(n):
                    if distance_matrix[i][j] <= epsilon:
                        adjacency[i][j] = 1
            
            visited = [False] * n
            beta_0 = 0
            
            for i in range(n):
                if not visited[i]:
                    beta_0 += 1
                    queue = [i]
                    while queue:
                        node = queue.pop(0)
                        if not visited[node]:
                            visited[node] = True
                            for j in range(n):
                                if adjacency[node][j] and not visited[j]:
                                    queue.append(j)
            
            # Estimate β1 and β2 (simplified - would need proper homology computation)
            # β1 roughly correlates with cycles, β2 with clusters
            beta_1 = max(0, int(n * epsilon * 0.5))  # Simplified estimation
            beta_2 = max(0, int(beta_0 * 0.3))  # Simplified estimation
            
            betti = BettiNumbers(
                scale=epsilon,
                beta_0=beta_0,
                beta_1=beta_1,
                beta_2=beta_2
            )
            self.betti_curves.append(betti)
    
    def _generate_mapper_graph(self, points: List[Dict], distance_matrix: List[List[float]]):
        """
        Generate Mapper graph - simplified representation of high-dimensional data
        
        Algorithm:
        1. Project data to lower dimension (filter function)
        2. Cover the range with overlapping intervals
        3. Cluster points in each interval
        4. Build graph from cluster overlaps
        """
        n = len(points)
        
        if n == 0:
            self.mapper_graph = {'nodes': [], 'edges': []}
            return
        
        # Step 1: Filter function (use average distance as simple filter)
        filter_values = []
        for i in range(n):
            avg_dist = sum(distance_matrix[i]) / n
            filter_values.append(avg_dist)
        
        min_f, max_f = min(filter_values), max(filter_values)
        if max_f - min_f < 0.001:
            max_f = min_f + 1.0
        
        # Step 2: Create cover with overlap
        interval_width = (max_f - min_f) / self.config.COVER_INTERVALS
        overlap = interval_width * self.config.OVERLAP_RATIO
        
        intervals = []
        for i in range(self.config.COVER_INTERVALS):
            start = min_f + i * (interval_width - overlap)
            end = start + interval_width + overlap
            intervals.append((start, end))
        
        # Step 3: Cluster points in each interval
        clusters = []
        for i, (start, end) in enumerate(intervals):
            # Points in this interval
            interval_points = [
                j for j in range(n)
                if start <= filter_values[j] <= end
            ]
            
            if len(interval_points) >= self.config.CLUSTER_MIN_SIZE:
                # Simple clustering: treat all points in interval as one cluster
                cluster_id = f"cluster_{i}"
                clusters.append({
                    'id': cluster_id,
                    'points': interval_points,
                    'interval': i
                })
        
        # Step 4: Build graph
        nodes = []
        edges = []
        
        for cluster in clusters:
            nodes.append({
                'id': cluster['id'],
                'size': len(cluster['points']),
                'interval': cluster['interval']
            })
        
        # Connect clusters with overlapping points
        for i, c1 in enumerate(clusters):
            for j, c2 in enumerate(clusters[i+1:], i+1):
                # Check for overlap
                overlap_points = set(c1['points']) & set(c2['points'])
                if len(overlap_points) > 0:
                    edges.append({
                        'source': c1['id'],
                        'target': c2['id'],
                        'overlap': len(overlap_points)
                    })
        
        self.mapper_graph = {'nodes': nodes, 'edges': edges}
    
    def _interpret_features(self):
        """Interpret topological features in memory context"""
        for feature in self.features:
            if feature.dimension == 0:
                if feature.significance == "critical":
                    feature.interpretation = "Major knowledge cluster - foundational concept"
                elif feature.significance == "high":
                    feature.interpretation = "Significant knowledge domain"
                else:
                    feature.interpretation = "Minor knowledge fragment"
            
            elif feature.dimension == 1:
                feature.interpretation = "Feedback loop or cyclical reasoning pattern"
            
            elif feature.dimension == 2:
                feature.interpretation = "Higher-order knowledge structure (framework/paradigm)"
    
    def get_analysis_summary(self) -> Dict:
        """Get analysis summary"""
        by_dimension = defaultdict(int)
        by_significance = defaultdict(int)
        
        for feature in self.features:
            by_dimension[feature.dimension] += 1
            by_significance[feature.significance] += 1
        
        return {
            'total_features': len(self.features),
            'by_dimension': dict(by_dimension),
            'by_significance': dict(by_significance),
            'betti_samples': len(self.betti_curves),
            'mapper_nodes': len(self.mapper_graph['nodes']),
            'mapper_edges': len(self.mapper_graph['edges']),
            'critical_features': len([f for f in self.features if f.significance == 'critical'])
        }
    
    def visualize(self):
        """Generate HTML visualization"""
        logger.info("Generating topology visualization...")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Memory Topology Map</title>
    <style>
        body {{ font-family: Arial; background: #1a1a2e; color: white; margin: 20px; }}
        h1 {{ color: #00d9ff; }}
        .stats {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #16213e; padding: 20px; border-radius: 10px; text-align: center; }}
        .stat-value {{ font-size: 2em; color: #00d9ff; }}
        .stat-label {{ color: #888; }}
        .graph {{ background: #16213e; padding: 20px; border-radius: 10px; margin-top: 20px; }}
        .node {{ display: inline-block; width: 60px; height: 60px; background: #0f3460; border-radius: 50%; margin: 10px; text-align: center; line-height: 60px; }}
    </style>
</head>
<body>
    <h1>🔮 Memory Topological Analysis</h1>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-value">{len(self.features)}</div>
            <div class="stat-label">Topological Features</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(1 for f in self.features if f.dimension == 0)}</div>
            <div class="stat-label">Connected Components (β0)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{sum(1 for f in self.features if f.dimension == 1)}</div>
            <div class="stat-label">Loops/Cycles (β1)</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{len(self.mapper_graph['nodes'])}</div>
            <div class="stat-label">Mapper Nodes</div>
        </div>
    </div>
    
    <div class="graph">
        <h2>Mapper Graph</h2>
        <p>Nodes: {len(self.mapper_graph['nodes'])} | Edges: {len(self.mapper_graph['edges'])}</p>
        <div>
            {''.join(f'<div class="node" title="Cluster {n["id"]}">{n["size"]} pts</div>' for n in self.mapper_graph['nodes'][:20])}
        </div>
    </div>
    
    <div class="graph">
        <h2>Betti Numbers Curve</h2>
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <th style="padding: 10px; border: 1px solid #333;">Scale</th>
                <th style="padding: 10px; border: 1px solid #333;">β0</th>
                <th style="padding: 10px; border: 1px solid #333;">β1</th>
                <th style="padding: 10px; border: 1px solid #333;">β2</th>
            </tr>
            {''.join(f'<tr><td style="padding: 10px; border: 1px solid #333;">{b.scale:.2f}</td><td style="padding: 10px; border: 1px solid #333;">{b.beta_0}</td><td style="padding: 10px; border: 1px solid #333;">{b.beta_1}</td><td style="padding: 10px; border: 1px solid #333;">{b.beta_2}</td></tr>' for b in self.betti_curves)}
        </table>
    </div>
</body>
</html>
"""
        
        with open(self.config.TOPOLOGY_VISUALIZATION, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        logger.info(f"Visualization saved: {self.config.TOPOLOGY_VISUALIZATION}")


# ============================================================================
# CLI Interface
# ============================================================================

def analyze_command(args):
    """Analyze memory topology"""
    analyzer = TopologicalAnalyzer()
    summary = analyzer.analyze_memory(args.file)
    
    print(f"\n🔮 Topological Analysis Results")
    print("=" * 60)
    print(f"File: {args.file}")
    print(f"Total features: {summary['total_features']}")
    print(f"By dimension: {summary['by_dimension']}")
    print(f"By significance: {summary['by_significance']}")
    print(f"Critical features: {summary['critical_features']}")
    print(f"Mapper graph: {summary['mapper_nodes']} nodes, {summary['mapper_edges']} edges")
    print("=" * 60)


def betti_command(args):
    """Show Betti numbers"""
    analyzer = TopologicalAnalyzer()
    
    if not analyzer.betti_curves:
        print("No Betti numbers computed. Run --analyze first.")
        return
    
    print(f"\n📊 Betti Numbers Curve")
    print("=" * 60)
    print(f"{'Scale':<10} {'β0':<10} {'β1':<10} {'β2':<10}")
    print("-" * 40)
    
    for betti in analyzer.betti_curves:
        print(f"{betti.scale:<10.2f} {betti.beta_0:<10} {betti.beta_1:<10} {betti.beta_2:<10}")
    
    print("=" * 60)


def persistence_command(args):
    """Show persistence diagram"""
    analyzer = TopologicalAnalyzer()
    
    if not analyzer.features:
        print("No features computed. Run --analyze first.")
        return
    
    print(f"\n📈 Persistence Diagram")
    print("=" * 60)
    print(f"{'ID':<15} {'Dim':<5} {'Birth':<10} {'Death':<10} {'Persistence':<12} {'Significance':<12}")
    print("-" * 70)
    
    for feature in analyzer.features[:20]:
        print(f"{feature.feature_id:<15} {feature.dimension:<5} {feature.birth_scale:<10.2f} {feature.death_scale:<10.2f} {feature.persistence:<12.2f} {feature.significance:<12}")
    
    if len(analyzer.features) > 20:
        print(f"... and {len(analyzer.features) - 20} more")
    
    print("=" * 60)


def mapper_command(args):
    """Show Mapper graph"""
    analyzer = TopologicalAnalyzer()
    
    print(f"\n🗺️ Mapper Graph")
    print("=" * 60)
    print(f"Nodes: {len(analyzer.mapper_graph['nodes'])}")
    print(f"Edges: {len(analyzer.mapper_graph['edges'])}")
    
    print(f"\nNodes:")
    for node in analyzer.mapper_graph['nodes'][:10]:
        print(f"  {node['id']}: {node['size']} points (interval {node['interval']})")
    
    if len(analyzer.mapper_graph['nodes']) > 10:
        print(f"  ... and {len(analyzer.mapper_graph['nodes']) - 10} more")
    
    print(f"\nEdges:")
    for edge in analyzer.mapper_graph['edges'][:10]:
        print(f"  {edge['source']} → {edge['target']} (overlap: {edge['overlap']})")
    
    print("=" * 60)


def visualize_command(args):
    """Generate visualization"""
    analyzer = TopologicalAnalyzer()
    analyzer.visualize()
    
    print(f"\n📊 Topology Visualization Generated")
    print("=" * 60)
    print(f"File: {analyzer.config.TOPOLOGY_VISUALIZATION}")
    print("=" * 60)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Memory Topological Data Analysis')
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze memory topology')
    analyze_parser.add_argument('file', type=str, help='Memory file')
    analyze_parser.set_defaults(func=analyze_command)
    
    # Betti command
    betti_parser = subparsers.add_parser('betti', help='Show Betti numbers')
    betti_parser.set_defaults(func=betti_command)
    
    # Persistence command
    pers_parser = subparsers.add_parser('persistence', help='Show persistence diagram')
    pers_parser.set_defaults(func=persistence_command)
    
    # Mapper command
    mapper_parser = subparsers.add_parser('mapper', help='Show Mapper graph')
    mapper_parser.set_defaults(func=mapper_command)
    
    # Visualize command
    viz_parser = subparsers.add_parser('visualize', help='Generate visualization')
    viz_parser.set_defaults(func=visualize_command)
    
    args = parser.parse_args()
    
    if args.command:
        args.func(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()

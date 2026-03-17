#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tool Similarity Engine - Semantic tool comparison

Features:
- Semantic tool comparison
- Functionality clustering
- Duplicate detection (advanced)
- Merge recommendations
- Similarity scoring
- Cluster visualization
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Set
from collections import defaultdict
import difflib

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
DATA_DIR = WORKSPACE / 'data' / 'ai_suggestions'
DATA_DIR.mkdir(parents=True, exist_ok=True)

class ToolVectorizer:
    """Convert tools to vector representations"""
    
    def __init__(self):
        self.vocab = set()
        self.tool_vectors = {}
    
    def build_vocab(self, tools: List[Dict]) -> Set[str]:
        """Build vocabulary from tools"""
        vocab = set()
        
        for tool in tools:
            # From name
            vocab.update(tool['name'].lower().split('_'))
            
            # From keywords
            vocab.update(tool.get('keywords', []))
            
            # From description
            if 'description' in tool:
                words = tool['description'].lower().split()
                vocab.update([w for w in words if len(w) > 2])
        
        self.vocab = vocab
        return vocab
    
    def vectorize(self, tool: Dict) -> Dict[str, float]:
        """Convert tool to vector"""
        vector = defaultdict(float)
        
        # Name features (high weight)
        name_parts = tool['name'].lower().split('_')
        for part in name_parts:
            vector[part] += 0.5
        
        # Keyword features (medium weight)
        for keyword in tool.get('keywords', []):
            vector[keyword] += 0.3
        
        # Description features (low weight)
        if 'description' in tool:
            words = tool['description'].lower().split()
            for word in set(words):
                if len(word) > 2:
                    vector[word] += 0.1
        
        return dict(vector)
    
    def cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Calculate cosine similarity between vectors"""
        # Get all keys
        all_keys = set(vec1.keys()) | set(vec2.keys())
        
        if not all_keys:
            return 0.0
        
        # Dot product
        dot = sum(vec1.get(k, 0) * vec2.get(k, 0) for k in all_keys)
        
        # Magnitudes
        mag1 = sum(v**2 for v in vec1.values()) ** 0.5
        mag2 = sum(v**2 for v in vec2.values()) ** 0.5
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot / (mag1 * mag2)


class SimilarityCalculator:
    """Calculate similarity between tools"""
    
    def __init__(self):
        self.vectorizer = ToolVectorizer()
        self.tool_vectors = {}
    
    def calculate_all(self, tools: List[Dict]) -> List[Dict]:
        """Calculate similarity for all tool pairs"""
        # Build vectors
        self.vectorizer.build_vocab(tools)
        
        for tool in tools:
            self.tool_vectors[tool['name']] = self.vectorizer.vectorize(tool)
        
        # Calculate pairwise similarity
        similarities = []
        tool_names = list(self.tool_vectors.keys())
        
        for i, name1 in enumerate(tool_names):
            for name2 in tool_names[i+1:]:
                sim = self.vectorizer.cosine_similarity(
                    self.tool_vectors[name1],
                    self.tool_vectors[name2]
                )
                
                if sim > 0.3:  # Threshold
                    similarities.append({
                        'tool1': name1,
                        'tool2': name2,
                        'similarity': round(sim, 3),
                        'type': self._classify_similarity(sim),
                    })
        
        # Sort by similarity
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        
        return similarities
    
    def _classify_similarity(self, sim: float) -> str:
        """Classify similarity level"""
        if sim >= 0.8:
            return 'very_high'
        elif sim >= 0.6:
            return 'high'
        elif sim >= 0.4:
            return 'medium'
        else:
            return 'low'


class ClusterAnalyzer:
    """Analyze tool clusters"""
    
    def __init__(self, similarities: List[Dict], tools: List[Dict]):
        self.similarities = similarities
        self.tools = {t['name']: t for t in tools}
        self.clusters = []
    
    def find_clusters(self, threshold: float = 0.5) -> List[Dict]:
        """Find clusters of similar tools"""
        # Build adjacency list
        adjacency = defaultdict(set)
        
        for sim in self.similarities:
            if sim['similarity'] >= threshold:
                adjacency[sim['tool1']].add(sim['tool2'])
                adjacency[sim['tool2']].add(sim['tool1'])
        
        # Find connected components (clusters)
        visited = set()
        clusters = []
        
        for tool_name in adjacency.keys():
            if tool_name not in visited:
                cluster = self._dfs(tool_name, adjacency, visited)
                if len(cluster) >= 2:
                    clusters.append({
                        'tools': cluster,
                        'size': len(cluster),
                        'avg_similarity': self._avg_cluster_similarity(cluster),
                        'recommendation': self._generate_recommendation(cluster),
                    })
        
        # Sort by size
        clusters.sort(key=lambda x: x['size'], reverse=True)
        
        self.clusters = clusters
        return clusters
    
    def _dfs(self, node: str, adjacency: Dict, visited: Set) -> List[str]:
        """Depth-first search to find cluster"""
        stack = [node]
        cluster = []
        
        while stack:
            current = stack.pop()
            if current not in visited:
                visited.add(current)
                cluster.append(current)
                stack.extend(adjacency[current] - visited)
        
        return cluster
    
    def _avg_cluster_similarity(self, cluster: List[str]) -> float:
        """Calculate average similarity within cluster"""
        sims = []
        
        for i, tool1 in enumerate(cluster):
            for tool2 in cluster[i+1:]:
                for sim in self.similarities:
                    if (sim['tool1'] == tool1 and sim['tool2'] == tool2) or \
                       (sim['tool1'] == tool2 and sim['tool2'] == tool1):
                        sims.append(sim['similarity'])
                        break
        
        return sum(sims) / max(1, len(sims))
    
    def _generate_recommendation(self, cluster: List[str]) -> Dict:
        """Generate recommendation for cluster"""
        if len(cluster) == 2:
            return {
                'action': 'review_merge',
                'reason': 'Two highly similar tools',
                'effort': 'medium',
                'impact': 'reduce duplication',
            }
        elif len(cluster) >= 3:
            return {
                'action': 'create_module',
                'reason': 'Multiple tools in same domain',
                'effort': 'high',
                'impact': 'consolidate functionality',
            }
        else:
            return {
                'action': 'monitor',
                'reason': 'Low similarity',
                'effort': 'low',
                'impact': 'minimal',
            }


class ToolSimilarityEngine:
    """
    Semantic tool comparison and clustering
    
    Features:
    - Semantic tool comparison
    - Functionality clustering
    - Duplicate detection (advanced)
    - Merge recommendations
    - Similarity scoring
    - Cluster visualization
    """
    
    def __init__(self):
        self.tools = []
        self.similarities = []
        self.clusters = []
    
    def scan_tools(self, tools_dir: Path) -> List[Dict]:
        """Scan tools"""
        tools = []
        
        for py_file in tools_dir.glob('*.py'):
            if py_file.name.startswith('_'):
                continue
            
            tool_info = self._scan_tool(py_file)
            if tool_info:
                tools.append(tool_info)
        
        self.tools = tools
        return tools
    
    def _scan_tool(self, file_path: Path) -> Optional[Dict]:
        """Scan single tool"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract docstring
            docstring = ''
            if '"""' in content:
                start = content.find('"""')
                end = content.find('"""', start + 3)
                if end > start:
                    docstring = content[start+3:end]
            
            return {
                'name': file_path.stem,
                'file': file_path.name,
                'description': docstring.split('\n')[0] if docstring else '',
                'keywords': self._extract_keywords(file_path.stem, docstring),
                'size_kb': round(file_path.stat().st_size / 1024, 2),
            }
        
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
            return None
    
    def _extract_keywords(self, name: str, docstring: str) -> List[str]:
        """Extract keywords"""
        keywords = name.lower().split('_')
        
        if docstring:
            words = docstring.lower().split()
            keywords.extend([w for w in words if len(w) > 2][:20])
        
        return list(set(keywords))
    
    def analyze_similarity(self, threshold: float = 0.3) -> Dict:
        """Analyze tool similarities"""
        if not self.tools:
            return {'status': 'no_tools'}
        
        # Calculate similarities
        calculator = SimilarityCalculator()
        self.similarities = calculator.calculate_all(self.tools)
        
        # Find clusters
        analyzer = ClusterAnalyzer(self.similarities, self.tools)
        self.clusters = analyzer.find_clusters(threshold=0.5)
        
        # Statistics
        high_sim = [s for s in self.similarities if s['similarity'] >= 0.7]
        medium_sim = [s for s in self.similarities if 0.5 <= s['similarity'] < 0.7]
        
        return {
            'status': 'success',
            'total_tools': len(self.tools),
            'total_pairs_analyzed': len(self.similarities),
            'high_similarity_pairs': len(high_sim),
            'medium_similarity_pairs': len(medium_sim),
            'clusters_found': len(self.clusters),
            'tools_in_clusters': sum(c['size'] for c in self.clusters),
            'top_similarities': self.similarities[:10],
            'clusters': self.clusters[:5],  # Top 5 clusters
        }
    
    def get_merge_recommendations(self) -> List[Dict]:
        """Get merge recommendations"""
        recommendations = []
        
        for cluster in self.clusters:
            if cluster['size'] >= 2 and cluster['avg_similarity'] >= 0.6:
                recommendations.append({
                    'type': 'merge',
                    'tools': cluster['tools'],
                    'avg_similarity': cluster['avg_similarity'],
                    'reason': cluster['recommendation']['reason'],
                    'effort': cluster['recommendation']['effort'],
                    'impact': cluster['recommendation']['impact'],
                })
        
        return recommendations
    
    def print_report(self):
        """Print analysis report"""
        result = self.analyze_similarity()
        
        if result['status'] != 'success':
            print("❌ No tools to analyze")
            return
        
        print("\n" + "=" * 60)
        print("🔍 TOOL SIMILARITY ANALYSIS")
        print("=" * 60)
        
        print(f"\n📊 STATISTICS:")
        print(f"   Total tools: {result['total_tools']}")
        print(f"   Pairs analyzed: {result['total_pairs_analyzed']}")
        print(f"   High similarity (≥0.7): {result['high_similarity_pairs']}")
        print(f"   Medium similarity (0.5-0.7): {result['medium_similarity_pairs']}")
        print(f"   Clusters found: {result['clusters_found']}")
        print(f"   Tools in clusters: {result['tools_in_clusters']}")
        
        print(f"\n🔥 TOP SIMILAR PAIRS:")
        for sim in result['top_similarities'][:5]:
            print(f"   {sim['tool1']} ↔ {sim['tool2']}: {sim['similarity']} ({sim['type']})")
        
        print(f"\n📦 CLUSTERS:")
        for i, cluster in enumerate(result['clusters'][:3], 1):
            print(f"   Cluster {i} ({cluster['size']} tools):")
            print(f"      Tools: {', '.join(cluster['tools'])}")
            print(f"      Avg similarity: {cluster['avg_similarity']:.3f}")
            print(f"      Recommendation: {cluster['recommendation']['action']}")
        
        print(f"\n💡 MERGE RECOMMENDATIONS:")
        recs = self.get_merge_recommendations()
        for rec in recs[:5]:
            print(f"   [{rec['effort'].upper()}] Merge {', '.join(rec['tools'][:3])}")
            print(f"      Reason: {rec['reason']}")
        
        print("\n" + "=" * 60)
    
    def save_report(self, output_file: Path = None):
        """Save report to file"""
        if output_file is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_file = DATA_DIR / f'similarity_report_{timestamp}.json'
        
        result = self.analyze_similarity()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"💾 Report saved: {output_file}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Tool Similarity Engine")
    parser.add_argument('--analyze', action='store_true', help='Analyze similarities')
    parser.add_argument('--clusters', action='store_true', help='Find clusters')
    parser.add_argument('--recommend', action='store_true', help='Get recommendations')
    parser.add_argument('--report', action='store_true', help='Save report')
    parser.add_argument('--threshold', type=float, default=0.5, help='Similarity threshold')
    args = parser.parse_args()
    
    engine = ToolSimilarityEngine()
    engine.scan_tools(TOOLS_DIR)
    
    if args.analyze:
        engine.print_report()
    
    elif args.clusters:
        result = engine.analyze_similarity()
        print(f"\n📦 Found {result['clusters_found']} clusters")
        for i, cluster in enumerate(result['clusters'][:5], 1):
            print(f"   {i}. {', '.join(cluster['tools'])}")
    
    elif args.recommend:
        recs = engine.get_merge_recommendations()
        print(f"\n💡 Found {len(recs)} merge recommendations:")
        for rec in recs[:5]:
            print(f"   - {', '.join(rec['tools'][:3])}")
    
    elif args.report:
        engine.save_report()
    
    else:
        engine.print_report()

if __name__ == "__main__":
    main()

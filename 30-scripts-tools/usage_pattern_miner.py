#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Usage Pattern Miner - Extract usage patterns

Features:
- Tool usage analytics
- Pattern extraction
- Peak time identification
- Optimization opportunities
- Trend analysis
- Behavioral insights
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
DATA_DIR = WORKSPACE / 'data' / 'ai_suggestions'
DATA_DIR.mkdir(parents=True, exist_ok=True)

USAGE_HISTORY = DATA_DIR / 'usage_history.json'
PATTERNS_FILE = DATA_DIR / 'usage_patterns.json'

class UsageAnalyzer:
    """Analyze tool usage patterns"""
    
    def __init__(self):
        self.usage_data = self._load_usage_history()
        self.patterns = []
    
    def _load_usage_history(self) -> Dict:
        """Load usage history"""
        if USAGE_HISTORY.exists():
            with open(USAGE_HISTORY, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'tools': {}, 'queries': []}
    
    def analyze_tool_usage(self) -> Dict:
        """Analyze individual tool usage"""
        tools = self.usage_data.get('tools', {})
        
        if not tools:
            return {'status': 'no_data'}
        
        # Statistics per tool
        tool_stats = []
        
        for tool_name, data in tools.items():
            count = data.get('count', 0)
            last_used = data.get('last_used')
            queries = data.get('queries', [])
            
            # Analyze queries
            query_patterns = self._analyze_queries(queries)
            
            # Time-based analysis
            time_patterns = self._analyze_time_patterns(queries)
            
            tool_stats.append({
                'tool': tool_name,
                'usage_count': count,
                'last_used': last_used,
                'frequency': self._calculate_frequency(queries),
                'query_patterns': query_patterns,
                'time_patterns': time_patterns,
                'popularity_rank': 0,  # Will be set later
            })
        
        # Sort by usage count
        tool_stats.sort(key=lambda x: x['usage_count'], reverse=True)
        
        # Set ranks
        for i, stat in enumerate(tool_stats, 1):
            stat['popularity_rank'] = i
        
        return {
            'status': 'success',
            'total_tools': len(tools),
            'total_usage': sum(t['usage_count'] for t in tool_stats),
            'tool_stats': tool_stats,
        }
    
    def _analyze_queries(self, queries: List[Dict]) -> Dict:
        """Analyze query patterns"""
        if not queries:
            return {'status': 'no_queries'}
        
        # Extract keywords
        all_keywords = []
        for q in queries:
            query_text = q.get('query', '').lower()
            words = [w for w in query_text.split() if len(w) > 2]
            all_keywords.extend(words)
        
        keyword_counts = Counter(all_keywords)
        
        return {
            'status': 'success',
            'total_queries': len(queries),
            'top_keywords': keyword_counts.most_common(10),
            'avg_query_length': sum(len(q.get('query', '')) for q in queries) / len(queries),
        }
    
    def _analyze_time_patterns(self, queries: List[Dict]) -> Dict:
        """Analyze time-based patterns"""
        if not queries:
            return {'status': 'no_data'}
        
        # Extract hours and days
        hours = []
        days = []
        
        for q in queries:
            timestamp = q.get('timestamp')
            if timestamp:
                try:
                    dt = datetime.fromisoformat(timestamp)
                    hours.append(dt.hour)
                    days.append(dt.strftime('%A'))
                except:
                    pass
        
        if not hours:
            return {'status': 'no_timestamps'}
        
        # Peak hours
        hour_counts = Counter(hours)
        peak_hour = hour_counts.most_common(1)[0][0] if hour_counts else None
        
        # Peak days
        day_counts = Counter(days)
        peak_day = day_counts.most_common(1)[0][0] if day_counts else None
        
        return {
            'status': 'success',
            'peak_hour': peak_hour,
            'peak_day': peak_day,
            'hour_distribution': dict(hour_counts),
            'day_distribution': dict(day_counts),
        }
    
    def _calculate_frequency(self, queries: List[Dict]) -> str:
        """Calculate usage frequency"""
        if not queries:
            return 'never'
        
        # Get timestamps
        timestamps = []
        for q in queries:
            ts = q.get('timestamp')
            if ts:
                try:
                    timestamps.append(datetime.fromisoformat(ts))
                except:
                    pass
        
        if len(timestamps) < 2:
            return 'rare'
        
        # Calculate average interval
        timestamps.sort()
        intervals = [
            (timestamps[i+1] - timestamps[i]).total_seconds()
            for i in range(len(timestamps)-1)
        ]
        
        avg_interval = sum(intervals) / len(intervals)
        
        # Classify
        if avg_interval < 3600:  # <1 hour
            return 'very_frequent'
        elif avg_interval < 86400:  # <1 day
            return 'frequent'
        elif avg_interval < 604800:  # <1 week
            return 'moderate'
        else:
            return 'infrequent'


class PatternMiner:
    """Mine usage patterns"""
    
    def __init__(self, usage_data: Dict):
        self.usage_data = usage_data
        self.patterns = []
    
    def mine_patterns(self) -> List[Dict]:
        """Mine patterns from usage data"""
        tools = self.usage_data.get('tools', {})
        
        patterns = []
        
        # Pattern 1: Most popular tools
        if tools:
            sorted_tools = sorted(
                tools.items(),
                key=lambda x: x[1].get('count', 0),
                reverse=True
            )
            
            if len(sorted_tools) >= 3:
                patterns.append({
                    'type': 'popularity',
                    'description': 'Top 3 most used tools',
                    'tools': [t[0] for t in sorted_tools[:3]],
                    'insight': 'These tools provide core functionality',
                    'action': 'Ensure these tools are well-documented and optimized',
                })
        
        # Pattern 2: Unused tools
        unused = [name for name, data in tools.items() if data.get('count', 0) == 0]
        if unused:
            patterns.append({
                'type': 'unused',
                'description': f'{len(unused)} tools never used',
                'tools': unused[:10],
                'insight': 'These tools may be redundant or poorly discovered',
                'action': 'Review for removal or improve discoverability',
            })
        
        # Pattern 3: Usage trends
        recent_tools = self._get_recent_tools(days=7)
        if recent_tools:
            patterns.append({
                'type': 'trending',
                'description': f'{len(recent_tools)} tools used in last 7 days',
                'tools': recent_tools,
                'insight': 'Active development focus',
                'action': 'Continue supporting these tools',
            })
        
        # Pattern 4: Time-based patterns
        time_pattern = self._analyze_global_time_pattern()
        if time_pattern:
            patterns.append({
                'type': 'temporal',
                'description': 'Peak usage times identified',
                'peak_hour': time_pattern.get('peak_hour'),
                'peak_day': time_pattern.get('peak_day'),
                'insight': 'Users most active at specific times',
                'action': 'Schedule maintenance during low-usage periods',
            })
        
        # Pattern 5: Query patterns
        query_pattern = self._analyze_query_patterns()
        if query_pattern:
            patterns.append({
                'type': 'behavioral',
                'description': 'Common query patterns',
                'top_keywords': query_pattern.get('top_keywords', [])[:5],
                'insight': 'Users search for specific functionality',
                'action': 'Optimize tool discovery for these keywords',
            })
        
        self.patterns = patterns
        return patterns
    
    def _get_recent_tools(self, days: int = 7) -> List[str]:
        """Get tools used in last N days"""
        recent = []
        cutoff = datetime.now() - timedelta(days=days)
        
        for tool_name, data in self.usage_data.get('tools', {}).items():
            last_used = data.get('last_used')
            if last_used:
                try:
                    last_dt = datetime.fromisoformat(last_used)
                    if last_dt >= cutoff:
                        recent.append(tool_name)
                except:
                    pass
        
        return recent
    
    def _analyze_global_time_pattern(self) -> Optional[Dict]:
        """Analyze global time patterns"""
        all_hours = []
        all_days = []
        
        for tool_data in self.usage_data.get('tools', {}).values():
            for query in tool_data.get('queries', []):
                timestamp = query.get('timestamp')
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp)
                        all_hours.append(dt.hour)
                        all_days.append(dt.strftime('%A'))
                    except:
                        pass
        
        if not all_hours:
            return None
        
        hour_counts = Counter(all_hours)
        day_counts = Counter(all_days)
        
        return {
            'peak_hour': hour_counts.most_common(1)[0][0],
            'peak_day': day_counts.most_common(1)[0][0],
        }
    
    def _analyze_query_patterns(self) -> Optional[Dict]:
        """Analyze global query patterns"""
        all_keywords = []
        
        for tool_data in self.usage_data.get('tools', {}).values():
            for query in tool_data.get('queries', []):
                query_text = query.get('query', '').lower()
                words = [w for w in query_text.split() if len(w) > 2]
                all_keywords.extend(words)
        
        if not all_keywords:
            return None
        
        keyword_counts = Counter(all_keywords)
        
        return {
            'top_keywords': keyword_counts.most_common(10),
        }


class UsagePatternMiner:
    """
    Usage pattern mining and analytics
    
    Features:
    - Tool usage analytics
    - Pattern extraction
    - Peak time identification
    - Optimization opportunities
    - Trend analysis
    - Behavioral insights
    """
    
    def __init__(self):
        self.analyzer = UsageAnalyzer()
        self.miner = None
        self.patterns = []
    
    def analyze(self) -> Dict:
        """Run full analysis"""
        # Analyze tool usage
        usage_analysis = self.analyzer.analyze_tool_usage()
        
        if usage_analysis['status'] == 'no_data':
            return {
                'status': 'no_data',
                'message': 'No usage history found. Run tools to generate data.',
            }
        
        # Mine patterns
        self.miner = PatternMiner(self.analyzer.usage_data)
        self.patterns = self.miner.mine_patterns()
        
        # Generate insights
        insights = self._generate_insights(usage_analysis)
        
        return {
            'status': 'success',
            'usage_analysis': usage_analysis,
            'patterns': self.patterns,
            'insights': insights,
            'timestamp': datetime.now().isoformat(),
        }
    
    def _generate_insights(self, usage_analysis: Dict) -> List[Dict]:
        """Generate actionable insights"""
        insights = []
        
        # Insight 1: Popular tools
        if usage_analysis.get('tool_stats'):
            top_tools = usage_analysis['tool_stats'][:3]
            insights.append({
                'type': 'optimization',
                'priority': 'high',
                'title': 'Optimize Popular Tools',
                'description': f"Top tools: {', '.join(t['tool'] for t in top_tools)}",
                'action': 'Ensure these are well-tested and documented',
                'impact': 'Improves experience for most users',
            })
        
        # Insight 2: Unused tools
        unused = [
            t['tool'] for t in usage_analysis.get('tool_stats', [])
            if t['usage_count'] == 0
        ]
        if len(unused) >= 5:
            insights.append({
                'type': 'cleanup',
                'priority': 'medium',
                'title': 'Review Unused Tools',
                'description': f'{len(unused)} tools never used',
                'action': 'Consider removing or improving discoverability',
                'impact': 'Reduces maintenance burden',
            })
        
        # Insight 3: Usage frequency
        frequent = [
            t['tool'] for t in usage_analysis.get('tool_stats', [])
            if t.get('frequency') == 'very_frequent'
        ]
        if frequent:
            insights.append({
                'type': 'performance',
                'priority': 'high',
                'title': 'Optimize High-Frequency Tools',
                'description': f"Very frequent: {', '.join(frequent)}",
                'action': 'Profile and optimize performance',
                'impact': 'Significant time savings',
            })
        
        return insights
    
    def print_report(self):
        """Print analysis report"""
        result = self.analyze()
        
        if result['status'] != 'success':
            print(f"❌ {result['message']}")
            return
        
        print("\n" + "=" * 60)
        print("📊 USAGE PATTERN ANALYSIS")
        print("=" * 60)
        
        usage = result['usage_analysis']
        print(f"\n📈 OVERVIEW:")
        print(f"   Total tools tracked: {usage['total_tools']}")
        print(f"   Total usage events: {usage['total_usage']}")
        
        print(f"\n🔥 TOP TOOLS:")
        for stat in usage['tool_stats'][:5]:
            print(f"   {stat['popularity_rank']}. {stat['tool']}: {stat['usage_count']} uses ({stat['frequency']})")
        
        print(f"\n💡 PATTERNS:")
        for pattern in result['patterns'][:5]:
            print(f"   [{pattern['type'].upper()}] {pattern['description']}")
            if 'insight' in pattern:
                print(f"      → {pattern['insight']}")
        
        print(f"\n🎯 INSIGHTS:")
        for insight in result['insights'][:3]:
            print(f"   [{insight['priority'].upper()}] {insight['title']}")
            print(f"      {insight['action']}")
        
        print("\n" + "=" * 60)
    
    def save_patterns(self):
        """Save patterns to file"""
        result = self.analyze()
        
        if result['status'] != 'success':
            print("❌ No data to save")
            return
        
        with open(PATTERNS_FILE, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        
        print(f"💾 Patterns saved: {PATTERNS_FILE}")


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Usage Pattern Miner")
    parser.add_argument('--analyze', action='store_true', help='Analyze usage')
    parser.add_argument('--patterns', action='store_true', help='Show patterns')
    parser.add_argument('--insights', action='store_true', help='Show insights')
    parser.add_argument('--save', action='store_true', help='Save patterns')
    parser.add_argument('--report', action='store_true', help='Full report')
    args = parser.parse_args()
    
    miner = UsagePatternMiner()
    
    if args.analyze:
        result = miner.analyze()
        if result['status'] == 'success':
            print(f"✅ Analysis complete: {result['usage_analysis']['total_tools']} tools")
    
    elif args.patterns:
        miner.analyze()
        print(f"\n💡 Found {len(miner.patterns)} patterns:")
        for pattern in miner.patterns[:5]:
            print(f"   - {pattern['description']}")
    
    elif args.insights:
        result = miner.analyze()
        if result['status'] == 'success':
            print(f"\n🎯 Found {len(result['insights'])} insights:")
            for insight in result['insights'][:5]:
                print(f"   [{insight['priority'].upper()}] {insight['title']}")
    
    elif args.save:
        miner.save_patterns()
    
    elif args.report:
        miner.print_report()
    
    else:
        miner.print_report()

if __name__ == "__main__":
    main()

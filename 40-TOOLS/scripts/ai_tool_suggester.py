#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Tool Suggester - Intelligent tool recommendations

Features:
- Intent recognition from natural language
- Tool recommendation based on task
- Context-aware suggestions
- Usage pattern learning
- Confidence scoring
- Multi-turn refinement
"""

import os
import sys
import json
import re
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import difflib

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
TOOLS_DIR = WORKSPACE / '30-scripts-tools'
DATA_DIR = WORKSPACE / 'data' / 'ai_suggestions'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Usage history file
USAGE_HISTORY = DATA_DIR / 'usage_history.json'
TOOL_METADATA = DATA_DIR / 'tool_metadata.json'

class IntentRecognizer:
    """Recognize user intent from natural language"""
    
    def __init__(self):
        self.intent_patterns = {
            'deploy': [
                r'deploy', r'release', r'publish', r'upload', r'ship',
                r'服务器', r'部署', r'上线'
            ],
            'analyze': [
                r'analyze', r'analytics', r'stats', r'metrics', r'report',
                r'分析', r'统计', r'数据', r'报告'
            ],
            'automate': [
                r'automate', r'schedule', r'cron', r'run', r'execute',
                r'自动', r'定时', r'执行', r'运行'
            ],
            'monitor': [
                r'monitor', r'watch', r'check', r'health', r'status',
                r'监控', r'检查', r'状态', r'健康'
            ],
            'search': [
                r'find', r'search', r'look', r'locate', r'discover',
                r'找', r'搜索', r'查找'
            ],
            'optimize': [
                r'optim', r'improve', r'enhance', r'speed', r'faster',
                r'优化', r'改进', r'加速', r'提升'
            ],
            'create': [
                r'create', r'generate', r'make', r'build', r'new',
                r'创建', r'生成', r'制作', r'新建'
            ],
            'fix': [
                r'fix', r'repair', r'debug', r'error', r'issue',
                r'修复', r'错误', r'问题', r'debug'
            ],
        }
        
        self.tool_keywords = {
            'deploy': ['deploy', 'ci', 'cd', 'pipeline', 'release'],
            'analyze': ['analyze', 'analytics', 'predict', 'insight', 'report'],
            'automate': ['auto', 'schedule', 'cron', 'workflow', 'orchestrat'],
            'monitor': ['monitor', 'health', 'watch', 'check', 'dashboard'],
            'search': ['search', 'find', 'index', 'query'],
            'optimize': ['optim', 'enhance', 'improve', 'tune', 'accelerat'],
            'create': ['create', 'generate', 'make', 'build', 'doc'],
            'fix': ['fix', 'repair', 'debug', 'error', 'recover'],
        }
    
    def recognize(self, query: str) -> Dict:
        """Recognize intent from query"""
        query_lower = query.lower()
        
        # Score each intent
        intent_scores = {}
        for intent, patterns in self.intent_patterns.items():
            score = sum(1 for pattern in patterns if re.search(pattern, query_lower))
            intent_scores[intent] = score
        
        # Get top intent
        if max(intent_scores.values()) == 0:
            return {
                'intent': 'unknown',
                'confidence': 0.0,
                'all_scores': intent_scores,
            }
        
        top_intent = max(intent_scores, key=intent_scores.get)
        confidence = min(1.0, intent_scores[top_intent] / 3.0)  # Normalize
        
        return {
            'intent': top_intent,
            'confidence': confidence,
            'all_scores': intent_scores,
        }


class ToolRecommender:
    """Recommend tools based on intent and context"""
    
    def __init__(self):
        self.tools = []
        self.usage_history = self._load_usage_history()
        self.tool_metadata = self._load_tool_metadata()
    
    def load_tools(self, tools_dir: Path) -> List[Dict]:
        """Load and scan tools"""
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
                'path': str(file_path),
                'description': docstring.split('\n')[0] if docstring else '',
                'full_doc': docstring,
                'size_kb': round(file_path.stat().st_size / 1024, 2),
                'keywords': self._extract_keywords(file_path.stem, docstring),
                'last_used': self._get_last_used(file_path.stem),
                'usage_count': self._get_usage_count(file_path.stem),
            }
        
        except Exception as e:
            print(f"⚠️  Error scanning {file_path}: {e}")
            return None
    
    def _extract_keywords(self, name: str, docstring: str) -> List[str]:
        """Extract keywords from tool"""
        keywords = []
        
        # From name
        keywords.extend(name.lower().split('_'))
        
        # From docstring
        if docstring:
            words = re.findall(r'\b[a-zA-Z]{3,}\b', docstring.lower())
            keywords.extend(words[:20])
        
        return list(set(keywords))
    
    def _load_usage_history(self) -> Dict:
        """Load usage history"""
        if USAGE_HISTORY.exists():
            with open(USAGE_HISTORY, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'tools': {}, 'queries': []}
    
    def _load_tool_metadata(self) -> Dict:
        """Load tool metadata"""
        if TOOL_METADATA.exists():
            with open(TOOL_METADATA, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    def _get_last_used(self, tool_name: str) -> Optional[str]:
        """Get last used timestamp"""
        return self.usage_history['tools'].get(tool_name, {}).get('last_used')
    
    def _get_usage_count(self, tool_name: str) -> int:
        """Get usage count"""
        return self.usage_history['tools'].get(tool_name, {}).get('count', 0)
    
    def recommend(self, intent: str, query: str, top_n: int = 5) -> List[Dict]:
        """Recommend tools based on intent"""
        if not self.tools:
            return []
        
        recommendations = []
        
        for tool in self.tools:
            # Score based on keyword matching
            keyword_score = self._keyword_match_score(tool, intent, query)
            
            # Score based on usage (popularity)
            usage_score = min(1.0, tool['usage_count'] / 10.0)
            
            # Score based on recency
            recency_score = self._recency_score(tool['last_used'])
            
            # Combined score
            total_score = (
                keyword_score * 0.6 +
                usage_score * 0.2 +
                recency_score * 0.2
            )
            
            if total_score > 0.1:  # Threshold
                recommendations.append({
                    'tool': tool,
                    'score': total_score,
                    'keyword_score': keyword_score,
                    'usage_score': usage_score,
                    'recency_score': recency_score,
                    'reason': self._generate_reason(tool, intent),
                })
        
        # Sort by score
        recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return recommendations[:top_n]
    
    def _keyword_match_score(self, tool: Dict, intent: str, query: str) -> float:
        """Calculate keyword match score"""
        score = 0.0
        
        # Check intent keywords
        intent_keywords = {
            'deploy': ['deploy', 'release', 'ci', 'cd'],
            'analyze': ['analyze', 'analytics', 'predict', 'stats'],
            'automate': ['auto', 'schedule', 'workflow', 'cron'],
            'monitor': ['monitor', 'health', 'watch', 'dashboard'],
            'search': ['search', 'find', 'index'],
            'optimize': ['optim', 'enhance', 'improve'],
            'create': ['create', 'generate', 'doc'],
            'fix': ['fix', 'repair', 'debug', 'error'],
        }
        
        tool_keywords = set(tool['keywords'])
        query_words = set(query.lower().split())
        
        # Match with intent keywords
        if intent in intent_keywords:
            matches = tool_keywords.intersection(set(intent_keywords[intent]))
            score += len(matches) * 0.3
        
        # Match with query words
        matches = tool_keywords.intersection(query_words)
        score += len(matches) * 0.2
        
        # Fuzzy match
        for keyword in tool_keywords:
            for word in query_words:
                if difflib.SequenceMatcher(None, keyword, word).ratio() > 0.7:
                    score += 0.1
        
        return min(1.0, score)
    
    def _recency_score(self, last_used: Optional[str]) -> float:
        """Calculate recency score"""
        if not last_used:
            return 0.5  # Neutral for never used
        
        try:
            last_dt = datetime.fromisoformat(last_used)
            days_ago = (datetime.now() - last_dt).days
            
            if days_ago == 0:
                return 1.0
            elif days_ago < 7:
                return 0.8
            elif days_ago < 30:
                return 0.6
            else:
                return 0.4
        except:
            return 0.5
    
    def _generate_reason(self, tool: Dict, intent: str) -> str:
        """Generate recommendation reason"""
        reasons = []
        
        if tool['usage_count'] > 5:
            reasons.append(f"popular ({tool['usage_count']} uses)")
        
        if intent in tool['keywords']:
            reasons.append(f"matches {intent}")
        
        if tool['last_used']:
            reasons.append("recently used")
        
        return ", ".join(reasons) if reasons else "relevant match"
    
    def record_usage(self, tool_name: str, query: str):
        """Record tool usage"""
        if tool_name not in self.usage_history['tools']:
            self.usage_history['tools'][tool_name] = {
                'count': 0,
                'last_used': None,
                'queries': [],
            }
        
        self.usage_history['tools'][tool_name]['count'] += 1
        self.usage_history['tools'][tool_name]['last_used'] = datetime.now().isoformat()
        self.usage_history['tools'][tool_name]['queries'].append({
            'query': query,
            'timestamp': datetime.now().isoformat(),
        })
        
        # Keep last 100 queries
        self.usage_history['tools'][tool_name]['queries'] = \
            self.usage_history['tools'][tool_name]['queries'][-100:]
        
        # Save
        self._save_usage_history()
    
    def _save_usage_history(self):
        """Save usage history"""
        with open(USAGE_HISTORY, 'w', encoding='utf-8') as f:
            json.dump(self.usage_history, f, indent=2)


class AIToolSuggester:
    """
    AI-powered tool suggestions
    
    Features:
    - Intent recognition from natural language
    - Tool recommendation based on task
    - Context-aware suggestions
    - Usage pattern learning
    - Confidence scoring
    - Multi-turn refinement
    """
    
    def __init__(self):
        self.intent_recognizer = IntentRecognizer()
        self.recommender = ToolRecommender()
        self.conversation_history = []
    
    def suggest(self, query: str, top_n: int = 5) -> Dict:
        """Get tool suggestions for query"""
        # Recognize intent
        intent_result = self.intent_recognizer.recognize(query)
        
        # Get recommendations
        recommendations = self.recommender.recommend(
            intent_result['intent'],
            query,
            top_n
        )
        
        # Build response
        response = {
            'query': query,
            'intent': intent_result['intent'],
            'intent_confidence': intent_result['confidence'],
            'recommendations': [
                {
                    'tool': rec['tool']['name'],
                    'file': rec['tool']['file'],
                    'description': rec['tool']['description'],
                    'score': round(rec['score'], 3),
                    'reason': rec['reason'],
                    'command': f"python {rec['tool']['file']} --help",
                }
                for rec in recommendations
            ],
            'timestamp': datetime.now().isoformat(),
        }
        
        # Record usage if recommendations found
        if recommendations:
            for rec in recommendations[:1]:  # Record top choice
                self.recommender.record_usage(rec['tool']['name'], query)
        
        # Save conversation
        self.conversation_history.append({
            'query': query,
            'response': response,
            'timestamp': datetime.now().isoformat(),
        })
        
        return response
    
    def interactive_mode(self):
        """Run interactive suggestion mode"""
        print("\n🤖 AI Tool Suggester - Interactive Mode")
        print("=" * 60)
        print("Ask me anything about tools! (type 'quit' to exit)")
        print("=" * 60)
        
        while True:
            try:
                query = input("\n🔍 Query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("\n👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Get suggestions
                response = self.suggest(query)
                
                # Display results
                print(f"\n🎯 Intent: {response['intent']} (confidence: {response['intent_confidence']:.2f})")
                print(f"\n💡 Recommended Tools ({len(response['recommendations'])}):")
                
                for i, rec in enumerate(response['recommendations'], 1):
                    print(f"\n  {i}. {rec['tool']}")
                    print(f"     📄 {rec['description']}")
                    print(f"     📊 Score: {rec['score']} | {rec['reason']}")
                    print(f"     💻 Command: {rec['command']}")
                
                if not response['recommendations']:
                    print("   No matching tools found. Try different keywords.")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n⚠️  Error: {e}")
    
    def get_usage_stats(self) -> Dict:
        """Get usage statistics"""
        tools = self.recommender.usage_history['tools']
        
        if not tools:
            return {'status': 'no_data'}
        
        # Most used tools
        most_used = sorted(
            tools.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )[:10]
        
        # Recently used
        recently_used = sorted(
            tools.items(),
            key=lambda x: x[1]['last_used'] or '',
            reverse=True
        )[:10]
        
        return {
            'status': 'success',
            'total_tools_tracked': len(tools),
            'total_queries': sum(t['count'] for t in tools.values()),
            'most_used': [
                {'tool': name, 'count': data['count']}
                for name, data in most_used
            ],
            'recently_used': [
                {'tool': name, 'last_used': data['last_used']}
                for name, data in recently_used
                if data['last_used']
            ],
        }


def main():
    import argparse
    parser = argparse.ArgumentParser(description="AI Tool Suggester")
    parser.add_argument('--suggest', type=str, help='Get suggestions for query')
    parser.add_argument('--interactive', action='store_true', help='Interactive mode')
    parser.add_argument('--stats', action='store_true', help='Show usage stats')
    parser.add_argument('--top', type=int, default=5, help='Number of recommendations')
    args = parser.parse_args()
    
    suggester = AIToolSuggester()
    suggester.recommender.load_tools(TOOLS_DIR)
    
    if args.interactive:
        suggester.interactive_mode()
    
    elif args.suggest:
        response = suggester.suggest(args.suggest, args.top)
        
        print(f"\n🎯 Intent: {response['intent']} (confidence: {response['intent_confidence']:.2f})")
        print(f"\n💡 Recommended Tools:")
        
        for i, rec in enumerate(response['recommendations'], 1):
            print(f"\n  {i}. {rec['tool']}")
            print(f"     📄 {rec['description']}")
            print(f"     📊 Score: {rec['score']} | {rec['reason']}")
            print(f"     💻 Command: {rec['command']}")
    
    elif args.stats:
        stats = suggester.get_usage_stats()
        
        if stats['status'] == 'success':
            print(f"\n📊 USAGE STATISTICS")
            print(f"   Total tools tracked: {stats['total_tools_tracked']}")
            print(f"   Total queries: {stats['total_queries']}")
            
            print(f"\n🔥 Most Used:")
            for item in stats['most_used'][:5]:
                print(f"   {item['tool']}: {item['count']} times")
            
            print(f"\n🕐 Recently Used:")
            for item in stats['recently_used'][:5]:
                last_used = item['last_used'][:16] if item['last_used'] else 'N/A'
                print(f"   {item['tool']}: {last_used}")
        else:
            print("\n📊 No usage data yet")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

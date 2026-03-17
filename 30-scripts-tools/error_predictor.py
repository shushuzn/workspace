#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Error Predictor - AI-powered error prediction

Features:
- Error pattern recognition
- Failure probability estimation
- Root cause analysis
- Preventive suggestions
- Historical analysis
- Risk scoring
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict, Counter
import re

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Workspace setup
WORKSPACE = Path(__file__).parent.parent
DATA_DIR = WORKSPACE / 'data' / 'error_prediction'
DATA_DIR.mkdir(parents=True, exist_ok=True)

ERROR_HISTORY = DATA_DIR / 'error_history.json'
ERROR_PATTERNS = DATA_DIR / 'error_patterns.json'

class ErrorPatternDatabase:
    """Database of known error patterns"""
    
    def __init__(self):
        self.patterns = self._load_patterns()
    
    def _load_patterns(self) -> Dict:
        """Load error patterns"""
        return {
            'file_not_found': {
                'keywords': ['not found', 'no such file', 'missing', 'does not exist'],
                'category': 'io_error',
                'severity': 'high',
                'common_causes': [
                    'Incorrect file path',
                    'File was deleted or moved',
                    'Permission denied',
                    'Typo in filename',
                ],
                'prevention': [
                    'Validate file paths before access',
                    'Use absolute paths',
                    'Check file existence with os.path.exists()',
                    'Add error handling for missing files',
                ],
                'recovery': [
                    'Create missing file if appropriate',
                    'Use default/fallback file',
                    'Prompt user for correct path',
                ],
            },
            'permission_denied': {
                'keywords': ['permission denied', 'access denied', 'unauthorized', 'forbidden'],
                'category': 'permission_error',
                'severity': 'high',
                'common_causes': [
                    'Insufficient user privileges',
                    'File/folder is read-only',
                    'Network share access issue',
                    'Antivirus blocking',
                ],
                'prevention': [
                    'Run as administrator if needed',
                    'Check file permissions',
                    'Use appropriate user context',
                ],
                'recovery': [
                    'Request elevated privileges',
                    'Change file permissions',
                    'Use alternative location',
                ],
            },
            'connection_timeout': {
                'keywords': ['timeout', 'connection timed out', 'request timeout', 'deadline exceeded'],
                'category': 'network_error',
                'severity': 'medium',
                'common_causes': [
                    'Network connectivity issue',
                    'Server overload',
                    'Firewall blocking',
                    'DNS resolution failure',
                ],
                'prevention': [
                    'Set appropriate timeout values',
                    'Implement retry logic',
                    'Use connection pooling',
                    'Add health checks',
                ],
                'recovery': [
                    'Retry with exponential backoff',
                    'Use fallback server',
                    'Cache last known good data',
                ],
            },
            'out_of_memory': {
                'keywords': ['out of memory', 'memory error', 'ram', 'heap'],
                'category': 'resource_error',
                'severity': 'critical',
                'common_causes': [
                    'Processing too much data',
                    'Memory leak',
                    'Inefficient data structures',
                    'Concurrent operations',
                ],
                'prevention': [
                    'Process data in chunks',
                    'Use generators instead of lists',
                    'Release unused memory',
                    'Monitor memory usage',
                ],
                'recovery': [
                    'Reduce batch size',
                    'Clear caches',
                    'Restart process',
                ],
            },
            'invalid_json': {
                'keywords': ['invalid json', 'json decode error', 'parse error', 'syntax error'],
                'category': 'data_error',
                'severity': 'medium',
                'common_causes': [
                    'Malformed JSON',
                    'Encoding issues',
                    'Truncated data',
                    'Wrong content type',
                ],
                'prevention': [
                    'Validate JSON before parsing',
                    'Use try-except for json.loads()',
                    'Check content-type header',
                    'Implement schema validation',
                ],
                'recovery': [
                    'Use fallback parser',
                    'Request data again',
                    'Use cached version',
                ],
            },
            'api_rate_limit': {
                'keywords': ['rate limit', 'too many requests', '429', 'quota exceeded'],
                'category': 'api_error',
                'severity': 'medium',
                'common_causes': [
                    'Exceeded API quota',
                    'Too frequent requests',
                    'Shared quota with other users',
                ],
                'prevention': [
                    'Implement rate limiting',
                    'Use exponential backoff',
                    'Cache API responses',
                    'Monitor usage quotas',
                ],
                'recovery': [
                    'Wait and retry',
                    'Use cached data',
                    'Switch to alternative API',
                ],
            },
            'git_conflict': {
                'keywords': ['conflict', 'merge conflict', 'git error', 'push failed'],
                'category': 'version_control',
                'severity': 'medium',
                'common_causes': [
                    'Concurrent edits',
                    'Outdated local branch',
                    'Unmerged changes',
                ],
                'prevention': [
                    'Pull before push',
                    'Commit frequently',
                    'Use feature branches',
                    'Communicate with team',
                ],
                'recovery': [
                    'Pull and merge/rebase',
                    'Resolve conflicts manually',
                    'Stash changes and reapply',
                ],
            },
            'encoding_error': {
                'keywords': ['encoding', 'unicode', 'utf-8', 'decode', 'encode'],
                'category': 'data_error',
                'severity': 'low',
                'common_causes': [
                    'Wrong encoding specified',
                    'Mixed encodings',
                    'Special characters',
                    'Windows vs Unix line endings',
                ],
                'prevention': [
                    'Always specify encoding (utf-8)',
                    'Use error handling (errors=ignore)',
                    'Normalize text early',
                ],
                'recovery': [
                    'Try alternative encodings',
                    'Skip problematic characters',
                    'Use binary mode',
                ],
            },
        }
    
    def match_pattern(self, error_message: str) -> List[Dict]:
        """Match error message to known patterns"""
        error_lower = error_message.lower()
        matches = []
        
        for pattern_name, pattern_data in self.patterns.items():
            # Check keywords
            keyword_matches = sum(
                1 for kw in pattern_data['keywords']
                if kw in error_lower
            )
            
            if keyword_matches > 0:
                match_score = keyword_matches / len(pattern_data['keywords'])
                matches.append({
                    'pattern': pattern_name,
                    'score': match_score,
                    'data': pattern_data,
                })
        
        # Sort by score
        matches.sort(key=lambda x: x['score'], reverse=True)
        
        return matches
    
    def get_pattern(self, pattern_name: str) -> Optional[Dict]:
        """Get pattern by name"""
        return self.patterns.get(pattern_name)


class FailurePredictor:
    """Predict failure probability"""
    
    def __init__(self):
        self.error_db = ErrorPatternDatabase()
        self.history = self._load_history()
    
    def _load_history(self) -> Dict:
        """Load error history"""
        if ERROR_HISTORY.exists():
            with open(ERROR_HISTORY, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'errors': [], 'failures': []}
    
    def predict(self, context: Dict) -> Dict:
        """Predict failure probability"""
        # Extract features
        features = self._extract_features(context)
        
        # Calculate risk scores
        risk_scores = self._calculate_risk_scores(features)
        
        # Predict failure probability
        failure_prob = self._calculate_failure_probability(risk_scores)
        
        # Generate warnings
        warnings = self._generate_warnings(risk_scores, failure_prob)
        
        return {
            'failure_probability': failure_prob,
            'risk_level': self._get_risk_level(failure_prob),
            'risk_scores': risk_scores,
            'warnings': warnings,
            'recommendations': self._generate_recommendations(warnings),
        }
    
    def _extract_features(self, context: Dict) -> Dict:
        """Extract features from context"""
        features = {
            'tool_name': context.get('tool', ''),
            'operation': context.get('operation', ''),
            'input_size': context.get('input_size', 0),
            'complexity': context.get('complexity', 'medium'),
            'dependencies': context.get('dependencies', []),
            'resource_usage': context.get('resource_usage', {}),
            'previous_errors': self._get_previous_errors(context.get('tool', '')),
        }
        return features
    
    def _calculate_risk_scores(self, features: Dict) -> Dict:
        """Calculate risk scores for different dimensions"""
        scores = {}
        
        # Complexity risk
        complexity_map = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        scores['complexity'] = complexity_map.get(features['complexity'], 0.5)
        
        # Input size risk
        if features['input_size'] > 1000:
            scores['input_size'] = 0.8
        elif features['input_size'] > 100:
            scores['input_size'] = 0.5
        else:
            scores['input_size'] = 0.2
        
        # Dependency risk
        dep_count = len(features['dependencies'])
        scores['dependencies'] = min(1.0, dep_count * 0.15)
        
        # Historical risk
        if features['previous_errors'] > 5:
            scores['history'] = 0.9
        elif features['previous_errors'] > 2:
            scores['history'] = 0.6
        else:
            scores['history'] = 0.3
        
        return scores
    
    def _calculate_failure_probability(self, risk_scores: Dict) -> float:
        """Calculate overall failure probability"""
        if not risk_scores:
            return 0.3
        
        # Weighted average
        weights = {
            'complexity': 0.3,
            'input_size': 0.2,
            'dependencies': 0.25,
            'history': 0.25,
        }
        
        total = sum(
            risk_scores.get(key, 0.5) * weight
            for key, weight in weights.items()
        )
        
        return min(1.0, max(0.0, total))
    
    def _get_risk_level(self, probability: float) -> str:
        """Get risk level from probability"""
        if probability >= 0.8:
            return 'critical'
        elif probability >= 0.6:
            return 'high'
        elif probability >= 0.4:
            return 'medium'
        elif probability >= 0.2:
            return 'low'
        else:
            return 'minimal'
    
    def _generate_warnings(self, risk_scores: Dict, failure_prob: float) -> List[Dict]:
        """Generate warnings based on risk scores"""
        warnings = []
        
        if risk_scores.get('complexity', 0) > 0.7:
            warnings.append({
                'type': 'high_complexity',
                'message': 'Operation has high complexity',
                'suggestion': 'Consider breaking into smaller steps',
            })
        
        if risk_scores.get('input_size', 0) > 0.7:
            warnings.append({
                'type': 'large_input',
                'message': 'Large input size detected',
                'suggestion': 'Process in chunks to avoid memory issues',
            })
        
        if risk_scores.get('dependencies', 0) > 0.5:
            warnings.append({
                'type': 'many_dependencies',
                'message': 'Multiple dependencies',
                'suggestion': 'Ensure all dependencies are available',
            })
        
        if risk_scores.get('history', 0) > 0.7:
            warnings.append({
                'type': 'error_prone',
                'message': 'Tool has history of errors',
                'suggestion': 'Add extra error handling',
            })
        
        return warnings
    
    def _generate_recommendations(self, warnings: List[Dict]) -> List[str]:
        """Generate recommendations"""
        recommendations = []
        
        if any(w['type'] == 'high_complexity' for w in warnings):
            recommendations.append('Break complex operations into smaller steps')
        
        if any(w['type'] == 'large_input' for w in warnings):
            recommendations.append('Use streaming/chunked processing')
        
        if any(w['type'] == 'many_dependencies' for w in warnings):
            recommendations.append('Add dependency health checks')
        
        if any(w['type'] == 'error_prone' for w in warnings):
            recommendations.append('Implement retry logic with backoff')
        
        if not recommendations:
            recommendations.append('Proceed with standard error handling')
        
        return recommendations
    
    def _get_previous_errors(self, tool_name: str) -> int:
        """Get count of previous errors for tool"""
        errors = self.history.get('errors', [])
        return sum(1 for e in errors if e.get('tool') == tool_name)


class RootCauseAnalyzer:
    """Analyze root cause of errors"""
    
    def __init__(self):
        self.error_db = ErrorPatternDatabase()
    
    def analyze(self, error_message: str, context: Dict = None) -> Dict:
        """Analyze root cause"""
        # Match error patterns
        pattern_matches = self.error_db.match_pattern(error_message)
        
        if not pattern_matches:
            return {
                'status': 'unknown_pattern',
                'message': 'Error pattern not recognized',
                'suggestions': [
                    'Check error message for typos',
                    'Search error in documentation',
                    'Enable debug logging',
                ],
            }
        
        # Get best match
        best_match = pattern_matches[0]
        
        # Analyze contributing factors
        contributing_factors = self._analyze_factors(error_message, context or {})
        
        # Generate diagnosis
        diagnosis = {
            'status': 'analyzed',
            'primary_cause': best_match['pattern'],
            'confidence': best_match['score'],
            'category': best_match['data']['category'],
            'severity': best_match['data']['severity'],
            'contributing_factors': contributing_factors,
            'common_causes': best_match['data']['common_causes'][:3],
            'prevention': best_match['data']['prevention'][:3],
            'recovery': best_match['data']['recovery'][:2],
        }
        
        return diagnosis
    
    def _analyze_factors(self, error_message: str, context: Dict) -> List[Dict]:
        """Analyze contributing factors"""
        factors = []
        
        # Check for file path issues
        if '/' in error_message or '\\' in error_message:
            factors.append({
                'factor': 'file_path',
                'likelihood': 'high',
                'suggestion': 'Verify file path is correct and accessible',
            })
        
        # Check for network indicators
        if 'http' in error_message.lower() or 'connection' in error_message.lower():
            factors.append({
                'factor': 'network',
                'likelihood': 'high',
                'suggestion': 'Check network connectivity and firewall',
            })
        
        # Check for resource indicators
        if 'memory' in error_message.lower() or 'disk' in error_message.lower():
            factors.append({
                'factor': 'resources',
                'likelihood': 'medium',
                'suggestion': 'Monitor system resource usage',
            })
        
        # Check context
        if context.get('concurrent_operations', 0) > 5:
            factors.append({
                'factor': 'concurrency',
                'likelihood': 'medium',
                'suggestion': 'Reduce concurrent operations',
            })
        
        return factors


class ErrorPredictor:
    """
    AI-powered error prediction
    
    Features:
    - Error pattern recognition
    - Failure probability estimation
    - Root cause analysis
    - Preventive suggestions
    - Historical analysis
    - Risk scoring
    """
    
    def __init__(self):
        self.pattern_db = ErrorPatternDatabase()
        self.predictor = FailurePredictor()
        self.root_cause_analyzer = RootCauseAnalyzer()
    
    def predict_failure(self, context: Dict) -> Dict:
        """Predict failure for given context"""
        return self.predictor.predict(context)
    
    def analyze_error(self, error_message: str, context: Dict = None) -> Dict:
        """Analyze error root cause"""
        return self.root_cause_analyzer.analyze(error_message, context)
    
    def match_pattern(self, error_message: str) -> List[Dict]:
        """Match error to known patterns"""
        return self.pattern_db.match_pattern(error_message)
    
    def get_prevention(self, error_type: str) -> Optional[Dict]:
        """Get prevention strategies for error type"""
        return self.pattern_db.get_pattern(error_type)
    
    def print_prediction(self, prediction: Dict):
        """Print prediction report"""
        print("\n" + "=" * 60)
        print("🔮 FAILURE PREDICTION")
        print("=" * 60)
        
        prob = prediction['failure_probability']
        level = prediction['risk_level']
        
        # Risk indicator
        if level == 'critical':
            indicator = "🚨"
        elif level == 'high':
            indicator = "⚠️"
        elif level == 'medium':
            indicator = "⚡"
        else:
            indicator = "✅"
        
        print(f"\n{indicator} Failure Probability: {prob:.1%}")
        print(f"Risk Level: {level.upper()}")
        
        # Risk scores
        print(f"\n📊 Risk Breakdown:")
        for key, score in prediction['risk_scores'].items():
            bar = '█' * int(score * 10)
            print(f"   {key:15} {bar:10} {score:.1%}")
        
        # Warnings
        if prediction['warnings']:
            print(f"\n⚠️  Warnings ({len(prediction['warnings'])}):")
            for warning in prediction['warnings'][:3]:
                print(f"   - {warning['message']}")
                print(f"     → {warning['suggestion']}")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        for rec in prediction['recommendations'][:3]:
            print(f"   • {rec}")
        
        print("\n" + "=" * 60)
    
    def print_analysis(self, analysis: Dict):
        """Print error analysis report"""
        print("\n" + "=" * 60)
        print("🔍 ERROR ROOT CAUSE ANALYSIS")
        print("=" * 60)
        
        if analysis['status'] == 'unknown_pattern':
            print(f"\n❌ {analysis['message']}")
            print("\n💡 Suggestions:")
            for sug in analysis.get('suggestions', []):
                print(f"   • {sug}")
        else:
            print(f"\n🎯 Primary Cause: {analysis['primary_cause']}")
            print(f"Confidence: {analysis['confidence']:.1%}")
            print(f"Category: {analysis['category']}")
            print(f"Severity: {analysis['severity']}")
            
            print(f"\n📋 Common Causes:")
            for cause in analysis['common_causes']:
                print(f"   • {cause}")
            
            print(f"\n🛡️  Prevention:")
            for prev in analysis['prevention']:
                print(f"   • {prev}")
            
            print(f"\n🔧 Recovery:")
            for rec in analysis['recovery']:
                print(f"   • {rec}")
        
        print("\n" + "=" * 60)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Error Predictor")
    parser.add_argument('--predict', action='store_true', help='Predict failure')
    parser.add_argument('--analyze', type=str, help='Analyze error message')
    parser.add_argument('--patterns', action='store_true', help='List patterns')
    parser.add_argument('--demo', action='store_true', help='Run demo')
    args = parser.parse_args()
    
    predictor = ErrorPredictor()
    
    if args.predict:
        # Demo prediction
        context = {
            'tool': 'data_processor.py',
            'operation': 'process_large_file',
            'input_size': 5000,
            'complexity': 'high',
            'dependencies': ['db', 'api', 'cache'],
        }
        prediction = predictor.predict_failure(context)
        predictor.print_prediction(prediction)
    
    elif args.analyze:
        analysis = predictor.analyze_error(args.analyze)
        predictor.print_analysis(analysis)
    
    elif args.patterns:
        print("\n📋 Known Error Patterns:")
        for name, pattern in predictor.pattern_db.patterns.items():
            print(f"\n  {name}:")
            print(f"     Category: {pattern['category']}")
            print(f"     Severity: {pattern['severity']}")
            print(f"     Keywords: {', '.join(pattern['keywords'][:3])}")
    
    elif args.demo:
        print("\n🤖 Error Predictor Demo\n")
        
        # Demo 1: Pattern matching
        print("1️⃣ Pattern Matching:")
        test_errors = [
            "FileNotFoundError: [Errno 2] No such file or directory",
            "ConnectionTimeout: Request timed out after 30s",
            "JSONDecodeError: Invalid JSON at line 5",
        ]
        
        for error in test_errors:
            matches = predictor.match_pattern(error)
            if matches:
                print(f"   '{error[:50]}...' → {matches[0]['pattern']} ({matches[0]['score']:.1%})")
        
        # Demo 2: Failure prediction
        print("\n2️⃣ Failure Prediction:")
        context = {
            'tool': 'analyzer.py',
            'complexity': 'high',
            'input_size': 2000,
        }
        prediction = predictor.predict_failure(context)
        print(f"   Probability: {prediction['failure_probability']:.1%}")
        print(f"   Risk Level: {prediction['risk_level']}")
        
        # Demo 3: Root cause analysis
        print("\n3️⃣ Root Cause Analysis:")
        analysis = predictor.analyze_error("Permission denied: /etc/config.json")
        print(f"   Cause: {analysis['primary_cause']}")
        print(f"   Confidence: {analysis['confidence']:.1%}")
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()

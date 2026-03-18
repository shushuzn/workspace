#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Unicode Safe Helper - Fix Windows encoding issues
try:
    from unicode_safe_helper import safe_print as print
except ImportError:
    pass

"""
Quality Scorer - Automated quality scoring for code and papers

Usage:
    python quality_scorer.py --code CODE_DIR [--output OUTPUT]
    python quality_scorer.py --papers PAPER_DIR [--output OUTPUT]
    python quality_scorer.py --all WORKSPACE [--output OUTPUT]
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# UTF-8 for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Config
OUTPUT_DIR = Path(r"D:\OpenClaw\workspace\20-data-reports")
OUTPUT_FILE = OUTPUT_DIR / "quality-score-report.json"

class QualityScorer:
    """Automated quality scorer"""
    
    def __init__(self):
        self.code_weights = {
            'syntax': 20,
            'documentation': 20,
            'maintainability': 20,
            'efficiency': 15,
            'testing': 15,
            'style': 10
        }
        
        self.paper_weights = {
            'clarity': 25,
            'completeness': 25,
            'rigor': 20,
            'reproducibility': 15,
            'significance': 15
        }
    
    def score_code_quality(self, code_dir: Path) -> Dict:
        """Score code quality for a directory"""
        if not code_dir.exists():
            return {'error': f'Directory not found: {code_dir}'}
        
        py_files = list(code_dir.rglob('*.py'))
        
        if not py_files:
            return {'error': 'No Python files found'}
        
        scores = {
            'syntax': self._score_syntax(py_files),
            'documentation': self._score_documentation(py_files),
            'maintainability': self._score_maintainability(py_files),
            'efficiency': self._score_efficiency(py_files),
            'testing': self._score_testing(code_dir),
            'style': self._score_style(py_files)
        }
        
        # Calculate weighted average
        total_score = sum(
            scores[metric] * weight 
            for metric, weight in self.code_weights.items()
        ) / sum(self.code_weights.values())
        
        return {
            'type': 'code',
            'directory': str(code_dir),
            'file_count': len(py_files),
            'scores': scores,
            'weighted_score': round(total_score, 1),
            'grade': self._score_to_grade(total_score),
            'scored_at': datetime.now().isoformat()
        }
    
    def _score_syntax(self, files: List[Path]) -> int:
        """Score syntax quality"""
        syntax_errors = 0
        
        for f in files:
            try:
                compile(f.read_text(encoding='utf-8'), str(f), 'exec')
            except SyntaxError:
                syntax_errors += 1
        
        if syntax_errors == 0:
            return 100
        elif syntax_errors < len(files) * 0.05:
            return 90
        elif syntax_errors < len(files) * 0.1:
            return 70
        else:
            return 50
    
    def _score_documentation(self, files: List[Path]) -> int:
        """Score documentation quality"""
        total_funcs = 0
        documented_funcs = 0
        
        for f in files:
            try:
                import ast
                content = f.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        total_funcs += 1
                        if ast.get_docstring(node):
                            documented_funcs += 1
            except:
                pass
        
        if total_funcs == 0:
            return 50
        
        ratio = documented_funcs / total_funcs
        return int(ratio * 100)
    
    def _score_maintainability(self, files: List[Path]) -> int:
        """Score maintainability (avg function length)"""
        import ast
        
        func_lengths = []
        
        for f in files:
            try:
                content = f.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                            length = node.end_lineno - node.lineno + 1
                            func_lengths.append(length)
            except:
                pass
        
        if not func_lengths:
            return 50
        
        avg_length = sum(func_lengths) / len(func_lengths)
        
        if avg_length < 20:
            return 100
        elif avg_length < 30:
            return 85
        elif avg_length < 50:
            return 70
        else:
            return 50
    
    def _score_efficiency(self, files: List[Path]) -> int:
        """Score efficiency (nested loops, complexity)"""
        import ast
        
        issues = 0
        
        for f in files:
            try:
                content = f.read_text(encoding='utf-8')
                tree = ast.parse(content)
                
                # Count deeply nested loops
                for node in ast.walk(tree):
                    if isinstance(node, (ast.For, ast.While)):
                        # Check nesting depth
                        depth = self._get_nesting_depth(node, tree)
                        if depth > 3:
                            issues += 1
            except:
                pass
        
        if issues == 0:
            return 100
        elif issues < 5:
            return 85
        elif issues < 10:
            return 70
        else:
            return 50
    
    def _get_nesting_depth(self, node, tree) -> int:
        """Get nesting depth of a node"""
        # Simplified - count parent loops
        depth = 0
        for parent in ast.walk(tree):
            if isinstance(parent, (ast.For, ast.While)):
                if hasattr(parent, 'body'):
                    for child in ast.walk(parent):
                        if child is node:
                            depth += 1
        return depth
    
    def _score_testing(self, code_dir: Path) -> int:
        """Score testing coverage"""
        test_files = list(code_dir.rglob('test*.py')) + list(code_dir.rglob('*_test.py'))
        py_files = list(code_dir.rglob('*.py'))
        
        if not py_files:
            return 50
        
        test_ratio = len(test_files) / len(py_files)
        
        if test_ratio >= 0.5:
            return 100
        elif test_ratio >= 0.3:
            return 85
        elif test_ratio >= 0.1:
            return 70
        else:
            return 50
    
    def _score_style(self, files: List[Path]) -> int:
        """Score code style (line length, naming)"""
        import re
        
        issues = 0
        total_lines = 0
        
        for f in files:
            try:
                lines = f.read_text(encoding='utf-8').split('\n')
                total_lines += len(lines)
                
                for line in lines:
                    # Line length
                    if len(line) > 120:
                        issues += 1
                    
                    # Naming conventions (simplified)
                    if re.match(r'^\s*(def|class)\s+[^a-zA-Z_]', line):
                        issues += 1
            except:
                pass
        
        if total_lines == 0:
            return 50
        
        issue_ratio = issues / total_lines
        
        if issue_ratio < 0.01:
            return 100
        elif issue_ratio < 0.05:
            return 85
        elif issue_ratio < 0.1:
            return 70
        else:
            return 50
    
    def score_paper_quality(self, paper_dir: Path) -> Dict:
        """Score paper quality for a directory"""
        if not paper_dir.exists():
            return {'error': f'Directory not found: {paper_dir}'}
        
        md_files = list(paper_dir.rglob('*.md'))
        md_files = [f for f in md_files if f.name not in ['MEMORY.md', 'README.md']]
        
        if not md_files:
            return {'error': 'No markdown files found'}
        
        scores = {
            'clarity': self._score_clarity(md_files),
            'completeness': self._score_completeness(md_files),
            'rigor': self._score_rigor(md_files),
            'reproducibility': self._score_reproducibility(md_files),
            'significance': self._score_significance(md_files)
        }
        
        # Calculate weighted average
        total_score = sum(
            scores[metric] * weight 
            for metric, weight in self.paper_weights.items()
        ) / sum(self.paper_weights.values())
        
        return {
            'type': 'paper',
            'directory': str(paper_dir),
            'file_count': len(md_files),
            'scores': scores,
            'weighted_score': round(total_score, 1),
            'grade': self._score_to_grade(total_score),
            'scored_at': datetime.now().isoformat()
        }
    
    def _score_clarity(self, files: List[Path]) -> int:
        """Score clarity (readability, structure)"""
        total_score = 0
        
        for f in files:
            try:
                content = f.read_text(encoding='utf-8')
                lines = content.split('\n')
                
                # Has clear sections
                has_sections = any(
                    re.match(r'^#+\s', line) 
                    for line in lines
                )
                
                # Has bullet points
                has_bullets = any(
                    re.match(r'^\s*[-*•]\s', line) 
                    for line in lines
                )
                
                # Average line length reasonable
                avg_line_len = sum(len(l) for l in lines) / len(lines) if lines else 0
                good_line_len = 50 < avg_line_len < 100
                
                file_score = 0
                if has_sections:
                    file_score += 40
                if has_bullets:
                    file_score += 30
                if good_line_len:
                    file_score += 30
                
                total_score += file_score
                
            except:
                pass
        
        return total_score // len(files) if files else 50
    
    def _score_completeness(self, files: List[Path]) -> int:
        """Score completeness (all sections present)"""
        required_sections = ['abstract', 'method', 'result', 'conclusion']
        total_score = 0
        
        for f in files:
            try:
                content = f.read_text(encoding='utf-8').lower()
                
                sections_found = sum(
                    1 for section in required_sections 
                    if section in content
                )
                
                file_score = (sections_found / len(required_sections)) * 100
                total_score += file_score
                
            except:
                pass
        
        return total_score // len(files) if files else 50
    
    def _score_rigor(self, files: List[Path]) -> int:
        """Score rigor (citations, data, methods)"""
        total_score = 0
        
        for f in files:
            try:
                content = f.read_text(encoding='utf-8')
                
                # Has citations
                has_citations = bool(re.search(r'\[\d+\]|\([A-Za-z]+,\s*\d{4}\)', content))
                
                # Has data mentions
                has_data = any(
                    keyword in content.lower() 
                    for keyword in ['data', 'dataset', 'experiment', 'sample']
                )
                
                # Has methodology
                has_method = any(
                    keyword in content.lower() 
                    for keyword in ['method', 'approach', 'algorithm', 'procedure']
                )
                
                file_score = 0
                if has_citations:
                    file_score += 40
                if has_data:
                    file_score += 30
                if has_method:
                    file_score += 30
                
                total_score += file_score
                
            except:
                pass
        
        return total_score // len(files) if files else 50
    
    def _score_reproducibility(self, files: List[Path]) -> int:
        """Score reproducibility (code, data availability)"""
        total_score = 0
        
        for f in files:
            try:
                content = f.read_text(encoding='utf-8').lower()
                
                # Has code link
                has_code = any(
                    keyword in content 
                    for keyword in ['github', 'gitlab', 'code', 'repository']
                )
                
                # Has data link
                has_data = any(
                    keyword in content 
                    for keyword in ['dataset', 'data available', 'zenodo', 'figshare']
                )
                
                # Has detailed methods
                has_detailed_method = content.count('step') > 2 or content.count('procedure') > 1
                
                file_score = 0
                if has_code:
                    file_score += 40
                if has_data:
                    file_score += 30
                if has_detailed_method:
                    file_score += 30
                
                total_score += file_score
                
            except:
                pass
        
        return total_score // len(files) if files else 50
    
    def _score_significance(self, files: List[Path]) -> int:
        """Score significance (novelty, impact)"""
        # Simplified - based on keywords
        novelty_keywords = ['novel', 'first', 'propose', 'introduce', 'new']
        impact_keywords = ['improve', 'outperform', 'state-of-the-art', 'benchmark']
        
        total_score = 0
        
        for f in files:
            try:
                content = f.read_text(encoding='utf-8').lower()
                
                novelty_count = sum(
                    content.count(kw) for kw in novelty_keywords
                )
                
                impact_count = sum(
                    content.count(kw) for kw in impact_keywords
                )
                
                file_score = min(100, (novelty_count + impact_count) * 10)
                total_score += file_score
                
            except:
                pass
        
        return total_score // len(files) if files else 50
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to grade"""
        if score >= 90:
            return 'A (Excellent)'
        elif score >= 80:
            return 'B (Good)'
        elif score >= 70:
            return 'C (Acceptable)'
        elif score >= 60:
            return 'D (Needs Improvement)'
        else:
            return 'F (Poor)'
    
    def score_all(self, workspace: Path) -> Dict:
        """Score all quality aspects"""
        results = {}
        
        # Code quality
        code_dir = workspace / '30-scripts-tools'
        if code_dir.exists():
            print("Scoring code quality...")
            results['code'] = self.score_code_quality(code_dir)
        
        # Paper quality
        paper_dir = workspace / '06-research'
        if paper_dir.exists():
            print("Scoring paper quality...")
            results['paper'] = self.score_paper_quality(paper_dir)
        
        # Overall score
        if 'code' in results and 'paper' in results:
            code_score = results['code'].get('weighted_score', 0)
            paper_score = results['paper'].get('weighted_score', 0)
            results['overall'] = {
                'score': round((code_score + paper_score) / 2, 1),
                'grade': self._score_to_grade((code_score + paper_score) / 2)
            }
        
        results['scored_at'] = datetime.now().isoformat()
        
        return results
    
    def save_report(self, results: Dict, output_file: Path = None):
        """Save quality report"""
        if output_file is None:
            output_file = OUTPUT_FILE
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Report saved to {output_file}")
    
    def preview(self, results: Dict):
        """Preview results in console"""
        print(f"\n[CHART] Quality Score Report\n")
        
        if 'code' in results:
            code = results['code']
            if 'error' not in code:
                print(f"💻 Code Quality: {code['weighted_score']}/100 ({code['grade']})")
                print(f"   Files: {code['file_count']}")
                for metric, score in code['scores'].items():
                    print(f"   - {metric}: {score}")
                print()
        
        if 'paper' in results:
            paper = results['paper']
            if 'error' not in paper:
                print(f"📄 Paper Quality: {paper['weighted_score']}/100 ({paper['grade']})")
                print(f"   Files: {paper['file_count']}")
                for metric, score in paper['scores'].items():
                    print(f"   - {metric}: {score}")
                print()
        
        if 'overall' in results:
            overall = results['overall']
            print(f"[TARGET] Overall Quality: {overall['score']}/100 ({overall['grade']})")


def main():
    import argparse
    import re
    
    parser = argparse.ArgumentParser(description='Quality Scorer')
    parser.add_argument('--code', type=Path, help='Code directory to score')
    parser.add_argument('--papers', type=Path, help='Paper directory to score')
    parser.add_argument('--all', type=Path, help='Score entire workspace')
    parser.add_argument('--output', '-o', type=Path, help='Output file')
    parser.add_argument('--preview', action='store_true', help='Preview in console')
    parser.add_argument('--save', action='store_true', help='Save report')
    
    args = parser.parse_args()
    
    scorer = QualityScorer()
    
    if args.all:
        results = scorer.score_all(args.all)
    elif args.code:
        results = {'code': scorer.score_code_quality(args.code)}
    elif args.papers:
        results = {'paper': scorer.score_paper_quality(args.papers)}
    else:
        # Default: score workspace
        workspace = Path(__file__).parent.parent
        results = scorer.score_all(workspace)
    
    if args.preview or not args.save:
        scorer.preview(results)
    
    if args.save:
        scorer.save_report(results, args.output)


if __name__ == '__main__':
    main()

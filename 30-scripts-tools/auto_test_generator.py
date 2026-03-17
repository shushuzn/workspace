#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Test Generator - Phase 4 Innovation
Automatically generates unit tests for Python files
Features: AST analysis, test templates, mock data, coverage tracking

Usage:
    python auto_test_generator.py --generate path/to/file.py
    python auto_test_generator.py --scan 30-scripts-tools/
    python auto_test_generator.py --run     # Run generated tests
    python auto_test_generator.py --coverage # Show coverage
"""

import os
import sys
import ast
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

# Workspace root
WORKSPACE = Path(__file__).parent.parent
TESTS_DIR = WORKSPACE / "tests"
COVERAGE_FILE = WORKSPACE / "20-data-reports" / "test-coverage.json"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class AutoTestGenerator:
    """Automatically generate unit tests"""
    
    def __init__(self):
        self.generated_tests = []
        self.coverage = self._load_coverage()
    
    def _load_coverage(self) -> Dict:
        """Load test coverage data"""
        if COVERAGE_FILE.exists():
            import json
            with open(COVERAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"files": {}, "summary": {}}
    
    def _save_coverage(self):
        """Save test coverage data"""
        import json
        COVERAGE_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(COVERAGE_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.coverage, f, indent=2, ensure_ascii=False)
    
    def analyze_file(self, file_path: Path) -> Dict:
        """Analyze Python file and extract testable units"""
        print(f"[ANALYZE] {file_path.name}...")
        
        result = {
            'file': str(file_path),
            'functions': [],
            'classes': [],
            'imports': []
        }
        
        try:
            content = file_path.read_text(encoding='utf-8')
            tree = ast.parse(content)
            
            # Extract functions
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    # Skip private functions
                    if node.name.startswith('_'):
                        continue
                    
                    # Get function signature
                    args = []
                    for arg in node.args.args:
                        if arg.arg != 'self':
                            args.append(arg.arg)
                    
                    # Get decorators
                    decorators = [ast.unparse(d) if hasattr(ast, 'unparse') else str(type(d)) 
                                 for d in node.decorator_list]
                    
                    result['functions'].append({
                        'name': node.name,
                        'args': args,
                        'decorators': decorators,
                        'line': node.lineno,
                        'has_return': any(isinstance(n, ast.Return) for n in ast.walk(node))
                    })
                
                # Extract classes
                elif isinstance(node, ast.ClassDef):
                    methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
                    result['classes'].append({
                        'name': node.name,
                        'methods': methods,
                        'line': node.lineno
                    })
                
                # Extract imports
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        result['imports'].append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ''
                    for alias in node.names:
                        result['imports'].append(f"{module}.{alias.name}")
        
        except Exception as e:
            result['error'] = str(e)
        
        return result
    
    def generate_test(self, file_path: Path, analysis: Dict) -> str:
        """Generate unit test file"""
        test_code = f'''#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto-generated tests for {file_path.name}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / '30-scripts-tools'))

'''
        
        # Import the target module
        module_name = file_path.stem
        test_code += f'''
# Import module to test
try:
    import {module_name}
except ImportError as e:
    print(f"Warning: Could not import {{module_name}}: {{e}}")
    {module_name} = None

'''
        
        # Generate test class
        if analysis['classes']:
            for cls in analysis['classes']:
                test_code += f'''
class Test{cls['name'].replace('_', ' ').title().replace(' ', '')}(unittest.TestCase):
    """Tests for {cls['name']} class"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def tearDown(self):
        """Tear down test fixtures"""
        pass
    
'''
                # Generate test methods for each public method
                for method in cls['methods']:
                    if not method.startswith('_'):
                        test_code += f'''    def test_{method}(self):
        """Test {method} method"""
        # TODO: Implement test logic
        # obj = {cls['name']}()
        # result = obj.{method}()
        # self.assertIsNotNone(result)
        pass
    
'''
        
        # Generate function tests
        if analysis['functions']:
            test_code += '''
class TestFunctions(unittest.TestCase):
    """Tests for module functions"""
    
'''
            for func in analysis['functions']:
                test_code += f'''    def test_{func['name']}(self):
        """Test {func['name']} function"""
        # TODO: Implement test logic
        # result = {module_name}.{func['name']}()
        # self.assertIsNotNone(result)
        pass
    
'''
        
        # Add main runner
        test_code += '''
if __name__ == '__main__':
    unittest.main(verbosity=2)
'''
        
        return test_code
    
    def generate_for_file(self, file_path: Path) -> Optional[Path]:
        """Generate test for a single file"""
        analysis = self.analyze_file(file_path)
        
        if not analysis['functions'] and not analysis['classes']:
            print(f"  ⚠️  No testable units found")
            return None
        
        # Create test file
        test_filename = f"test_{file_path.stem}.py"
        test_path = TESTS_DIR / test_filename
        
        TESTS_DIR.mkdir(parents=True, exist_ok=True)
        
        test_code = self.generate_test(file_path, analysis)
        test_path.write_text(test_code, encoding='utf-8')
        
        # Update coverage
        self.coverage['files'][str(file_path)] = {
            'test_file': str(test_path),
            'generated': datetime.now().isoformat(),
            'functions': len(analysis['functions']),
            'classes': len(analysis['classes']),
            'status': 'generated'
        }
        self._save_coverage()
        
        self.generated_tests.append(str(test_path))
        print(f"  ✅ Generated: {test_path.name} ({len(analysis['functions'])} functions, {len(analysis['classes'])} classes)")
        
        return test_path
    
    def scan_and_generate(self, dir_path: Path, pattern: str = "*.py") -> List[Path]:
        """Scan directory and generate tests for all Python files"""
        print(f"[SCAN] Scanning {dir_path} for {pattern}...")
        
        py_files = list(dir_path.glob(pattern))
        
        # Skip test files
        py_files = [f for f in py_files if not f.name.startswith('test_')]
        
        print(f"[SCAN] Found {len(py_files)} source files")
        
        generated = []
        for i, file_path in enumerate(py_files, 1):
            print(f"[{i}/{len(py_files)}] ", end='')
            test_path = self.generate_for_file(file_path)
            if test_path:
                generated.append(test_path)
            
            if i % 20 == 0:
                print(f"  Progress: {i}/{len(py_files)}...")
        
        # Update summary
        self.coverage['summary'] = {
            'total_files': len(py_files),
            'tests_generated': len(generated),
            'coverage_percent': round(len(generated) / len(py_files) * 100, 1) if py_files else 0,
            'last_updated': datetime.now().isoformat()
        }
        self._save_coverage()
        
        return generated
    
    def run_tests(self) -> Dict:
        """Run generated tests"""
        import subprocess
        
        print("[RUN] Running all generated tests...")
        
        test_files = list(TESTS_DIR.glob("test_*.py"))
        
        if not test_files:
            print("[INFO] No test files found")
            return {'passed': 0, 'failed': 0, 'errors': 0}
        
        results = {'passed': 0, 'failed': 0, 'errors': 0, 'details': []}
        
        for test_file in test_files[:10]:  # Run first 10 tests
            print(f"\n[TEST] {test_file.name}...")
            
            try:
                process = subprocess.run(
                    ['python', str(test_file)],
                    capture_output=True,
                    text=True,
                    timeout=30,
                    cwd=str(WORKSPACE)
                )
                
                output = process.stdout + process.stderr
                
                if 'OK' in output:
                    results['passed'] += 1
                    print(f"  ✅ PASSED")
                elif 'FAILED' in output:
                    results['failed'] += 1
                    print(f"  ❌ FAILED")
                else:
                    results['errors'] += 1
                    print(f"  ⚠️  ERROR")
                
                results['details'].append({
                    'file': str(test_file),
                    'status': 'passed' if 'OK' in output else ('failed' if 'FAILED' in output else 'error'),
                    'output': output[:500]
                })
                
            except subprocess.TimeoutExpired:
                results['errors'] += 1
                print(f"  ⏱️  TIMEOUT")
            except Exception as e:
                results['errors'] += 1
                print(f"  ❌ ERROR: {e}")
        
        print(f"\n{'=' * 60}")
        print(f"Test Results: {results['passed']} passed, {results['failed']} failed, {results['errors']} errors")
        print(f"{'=' * 60}")
        
        return results
    
    def show_coverage(self):
        """Show test coverage report"""
        print("\n" + "=" * 60)
        print("Test Coverage Report")
        print("=" * 60)
        
        summary = self.coverage.get('summary', {})
        print(f"\nSummary:")
        print(f"  Total files:     {summary.get('total_files', 0)}")
        print(f"  Tests generated: {summary.get('tests_generated', 0)}")
        print(f"  Coverage:        {summary.get('coverage_percent', 0)}%")
        print(f"  Last updated:    {summary.get('last_updated', 'N/A')}")
        
        # Show files without tests
        print(f"\nFiles without tests:")
        
        import json
        scripts_dir = WORKSPACE / "30-scripts-tools"
        if scripts_dir.exists():
            all_files = set(str(f) for f in scripts_dir.glob("*.py") if not f.name.startswith('test_'))
            tested_files = set(self.coverage.get('files', {}).keys())
            
            without_tests = all_files - tested_files
            
            for file_path in list(without_tests)[:20]:
                print(f"  ❌ {Path(file_path).name}")
            
            if len(without_tests) > 20:
                print(f"  ... and {len(without_tests) - 20} more")
        
        print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Auto Test Generator')
    parser.add_argument('--generate', type=str, help='Generate test for a file')
    parser.add_argument('--scan', type=str, help='Scan directory and generate tests')
    parser.add_argument('--pattern', type=str, default='*.py', help='File pattern')
    parser.add_argument('--run', action='store_true', help='Run generated tests')
    parser.add_argument('--coverage', action='store_true', help='Show coverage report')
    args = parser.parse_args()
    
    generator = AutoTestGenerator()
    
    if args.generate:
        file_path = Path(args.generate)
        generator.generate_for_file(file_path)
    
    if args.scan:
        dir_path = Path(args.scan)
        generated = generator.scan_and_generate(dir_path, args.pattern)
        print(f"\n{'=' * 60}")
        print(f"Generated {len(generated)} test files")
        print(f"{'=' * 60}")
    
    if args.run:
        generator.run_tests()
    
    if args.coverage:
        generator.show_coverage()
    
    if not any([args.generate, args.scan, args.run, args.coverage]):
        parser.print_help()


if __name__ == "__main__":
    main()

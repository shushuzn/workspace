#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Auto Test Runner - Phase 4 Innovation
Automatically runs tests and generates coverage reports
Features: test discovery, parallel execution, coverage tracking, CI/CD integration

Usage:
    python auto_test_runner.py --run
    python auto_test_runner.py --coverage
    python auto_test_runner.py --report
    python auto_test_runner.py --watch
"""

import os
import sys
import json
import time
import argparse
import subprocess
import unittest
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
from concurrent.futures import ThreadPoolExecutor, as_completed

# Workspace root
WORKSPACE = Path(__file__).parent.parent
TESTS_DIR = WORKSPACE / "35-tests"
REPORTS_DIR = WORKSPACE / "20-data-reports" / "test-reports"

# Ensure UTF-8 for Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')


class AutoTestRunner:
    """Automated test execution and reporting"""
    
    def __init__(self):
        self.results = {
            'total': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'duration': 0,
            'tests': []
        }
    
    def discover_tests(self, pattern: str = "test_*.py") -> List[Path]:
        """Discover test files"""
        print(f"[DISCOVER] Finding tests matching {pattern}...")
        
        test_files = []
        
        # Search in tests directory
        if TESTS_DIR.exists():
            test_files.extend(TESTS_DIR.glob(f"**/{pattern}"))
        
        # Also search in tools directory
        tools_dir = WORKSPACE / "30-scripts-tools"
        if tools_dir.exists():
            test_files.extend(tools_dir.glob(f"**/{pattern}"))
        
        print(f"[DISCOVER] Found {len(test_files)} test files")
        
        return sorted(test_files)
    
    def run_test_file(self, test_file: Path) -> Dict:
        """Run a single test file"""
        result = {
            'file': str(test_file),
            'name': test_file.name,
            'tests_run': 0,
            'passed': 0,
            'failed': 0,
            'errors': 0,
            'skipped': 0,
            'duration': 0,
            'output': '',
            'status': 'pending'
        }
        
        try:
            start_time = time.time()
            
            # Run with unittest
            process = subprocess.run(
                ['python', '-m', 'unittest', str(test_file), '-v'],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per file
                cwd=str(WORKSPACE)
            )
            
            end_time = time.time()
            
            result['duration'] = round(end_time - start_time, 2)
            result['output'] = process.stdout + process.stderr
            
            # Parse results from output
            output = result['output']
            
            # Count test results
            if 'OK' in output:
                result['status'] = 'passed'
            elif 'FAILED' in output or 'FAILED (' in output:
                result['status'] = 'failed'
            elif 'ERROR' in output:
                result['status'] = 'error'
            elif 'SKIPPED' in output:
                result['status'] = 'skipped'
            else:
                result['status'] = 'unknown'
            
            # Try to parse counts
            import re
            
            ran_match = re.search(r'Ran (\d+) tests?', output)
            if ran_match:
                result['tests_run'] = int(ran_match.group(1))
            
            # Check for failures/errors
            if 'failures=' in output:
                fail_match = re.search(r'failures=(\d+)', output)
                if fail_match:
                    result['failed'] = int(fail_match.group(1))
            
            if 'errors=' in output:
                err_match = re.search(r'errors=(\d+)', output)
                if err_match:
                    result['errors'] = int(err_match.group(1))
            
            result['passed'] = result['tests_run'] - result['failed'] - result['errors']
            
        except subprocess.TimeoutExpired:
            result['status'] = 'timeout'
            result['output'] = 'Test execution timed out after 300 seconds'
            result['duration'] = 300
        
        except Exception as e:
            result['status'] = 'error'
            result['output'] = str(e)
        
        return result
    
    def run_all_tests(self, parallel: bool = True, max_workers: int = 4) -> Dict:
        """Run all discovered tests"""
        print("\n" + "=" * 60)
        print("Auto Test Runner")
        print("=" * 60)
        
        test_files = self.discover_tests()
        
        if not test_files:
            print("[INFO] No test files found")
            return self.results
        
        print(f"\nRunning {len(test_files)} test files...")
        print(f"Parallel: {parallel}, Max workers: {max_workers}\n")
        
        start_time = time.time()
        
        if parallel and len(test_files) > 1:
            # Run in parallel
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = {executor.submit(self.run_test_file, tf): tf for tf in test_files}
                
                for future in as_completed(futures):
                    result = future.result()
                    self._process_result(result)
        else:
            # Run sequentially
            for test_file in test_files:
                result = self.run_test_file(test_file)
                self._process_result(result)
        
        end_time = time.time()
        self.results['duration'] = round(end_time - start_time, 2)
        
        # Print summary
        self._print_summary()
        
        # Save results
        self._save_results()
        
        return self.results
    
    def _process_result(self, result: Dict):
        """Process and aggregate test result"""
        self.results['tests'].append(result)
        self.results['total'] += result.get('tests_run', 0)
        self.results['passed'] += result.get('passed', 0)
        self.results['failed'] += result.get('failed', 0)
        self.results['errors'] += result.get('errors', 0)
        self.results['skipped'] += result.get('skipped', 0)
    
    def _print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 60)
        print("Test Summary")
        print("=" * 60)
        
        total = self.results['total']
        passed = self.results['passed']
        failed = self.results['failed']
        errors = self.results['errors']
        duration = self.results['duration']
        
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"\nTotal Tests:  {total}")
        print(f"Passed:       {passed} ({pass_rate:.1f}%)")
        print(f"Failed:       {failed}")
        print(f"Errors:       {errors}")
        print(f"Duration:     {duration}s")
        
        # Status icon
        if failed == 0 and errors == 0:
            status = "✅ PASS"
        else:
            status = "❌ FAIL"
        
        print(f"\nStatus:       {status}")
        
        # Show failed tests
        if failed > 0 or errors > 0:
            print(f"\nFailed/Error Tests:")
            for test in self.results['tests']:
                if test['status'] in ['failed', 'error', 'timeout']:
                    print(f"  - {test['name']} ({test['status']})")
        
        print("=" * 60)
    
    def _save_results(self):
        """Save test results"""
        REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        result_file = REPORTS_DIR / f"test-results-{timestamp}.json"
        
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Results saved to {result_file}")
    
    def generate_coverage_report(self) -> str:
        """Generate coverage report"""
        print("\n[COVERAGE] Generating coverage report...")
        
        # Try to run coverage
        try:
            process = subprocess.run(
                ['python', '-m', 'coverage', 'run', '--source=30-scripts-tools', '-m', 'unittest', 'discover', '-s', '35-tests'],
                capture_output=True,
                text=True,
                timeout=300,
                cwd=str(WORKSPACE)
            )
            
            # Generate HTML report
            subprocess.run(
                ['python', '-m', 'coverage', 'html', '-d', str(REPORTS_DIR / 'coverage-html')],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(WORKSPACE)
            )
            
            # Generate text report
            process_report = subprocess.run(
                ['python', '-m', 'coverage', 'report'],
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(WORKSPACE)
            )
            
            report = f"""# Coverage Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

```
{process_report.stdout}
```

---

## HTML Report

Location: `{REPORTS_DIR / 'coverage-html'}`

Open in browser: `start {REPORTS_DIR / 'coverage-html' / 'index.html'}`

---

*Generated by Auto Test Runner (Phase 4 Innovation)*
"""
            
            # Save
            report_path = REPORTS_DIR / f"coverage-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
            report_path.write_text(report, encoding='utf-8')
            
            print(f"[OK] Coverage report saved to {report_path}")
            
            return report
        
        except FileNotFoundError:
            report = """# Coverage Report

**Status:** Coverage module not installed

Install with: `pip install coverage`

---

*Generated by Auto Test Runner (Phase 4 Innovation)*
"""
            return report
        
        except Exception as e:
            return f"# Coverage Report\n\n**Error:** {e}"
    
    def generate_report(self) -> str:
        """Generate comprehensive test report"""
        print("[REPORT] Generating test report...")
        
        report = f"""# Test Execution Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {self.results['total']} |
| Passed | {self.results['passed']} |
| Failed | {self.results['failed']} |
| Errors | {self.results['errors']} |
| Skipped | {self.results['skipped']} |
| Duration | {self.results['duration']}s |
| Pass Rate | {(self.results['passed']/self.results['total']*100) if self.results['total'] > 0 else 0:.1f}% |

---

## Test Results by File

| File | Status | Tests | Passed | Failed | Duration |
|------|--------|-------|--------|--------|----------|
"""
        
        for test in self.results['tests']:
            status_icon = "✅" if test['status'] == 'passed' else "❌"
            name = Path(test['file']).name
            tests_run = test.get('tests_run', 0)
            passed = test.get('passed', 0)
            failed = test.get('failed', 0)
            duration = test.get('duration', 0)
            
            report += f"| {name} | {status_icon} {test['status']} | {tests_run} | {passed} | {failed} | {duration}s |\n"
        
        report += f"""
---

## Recommendations

"""
        
        # Generate recommendations
        recommendations = []
        
        if self.results['total'] == 0:
            recommendations.append("- **No tests found** - Create test files in `35-tests/` directory")
        
        if self.results['failed'] > 0:
            recommendations.append(f"- **{self.results['failed']} failed tests** - Review and fix failing tests")
        
        if self.results['errors'] > 0:
            recommendations.append(f"- **{self.results['errors']} errors** - Check test setup and dependencies")
        
        pass_rate = (self.results['passed'] / self.results['total'] * 100) if self.results['total'] > 0 else 0
        if pass_rate < 80:
            recommendations.append(f"- **Low pass rate ({pass_rate:.1f}%)** - Prioritize fixing failing tests")
        elif pass_rate < 100:
            recommendations.append("- **Good pass rate** - Continue maintaining test quality")
        else:
            recommendations.append("- ✅ **All tests passing** - Excellent! Consider adding more edge case tests")
        
        if self.results['duration'] > 300:
            recommendations.append(f"- **Long execution time ({self.results['duration']}s)** - Consider parallel test execution")
        
        report += "\n".join(recommendations)
        
        report += f"""

---

## CI/CD Integration

Add to GitHub Actions (`.github/workflows/tests.yml`):

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: python 30-scripts-tools/auto_test_runner.py --run
```

---

*Generated by Auto Test Runner (Phase 4 Innovation)*
"""
        
        # Save
        report_path = REPORTS_DIR / f"test-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"[OK] Report saved to {report_path}")
        
        return report


def main():
    parser = argparse.ArgumentParser(description='Auto Test Runner')
    parser.add_argument('--run', action='store_true', help='Run all tests')
    parser.add_argument('--parallel', action='store_true', default=True, help='Run in parallel')
    parser.add_argument('--workers', type=int, default=4, help='Max parallel workers')
    parser.add_argument('--coverage', action='store_true', help='Generate coverage report')
    parser.add_argument('--report', action='store_true', help='Generate test report')
    parser.add_argument('--watch', action='store_true', help='Watch mode (run on changes)')
    args = parser.parse_args()
    
    runner = AutoTestRunner()
    
    if args.run:
        runner.run_all_tests(parallel=args.parallel, max_workers=args.workers)
    
    if args.coverage:
        report = runner.generate_coverage_report()
        print(report[:1000])
    
    if args.report:
        # Run tests first if no results
        if not runner.results['tests']:
            runner.run_all_tests()
        report = runner.generate_report()
        print(report[:2000])
    
    if args.watch:
        print("[WATCH] Watch mode not yet implemented")
        print("  Use --run instead")
    
    if not any([args.run, args.coverage, args.report, args.watch]):
        parser.print_help()


if __name__ == "__main__":
    main()

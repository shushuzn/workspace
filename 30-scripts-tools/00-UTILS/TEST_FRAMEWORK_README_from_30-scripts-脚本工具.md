# Generic Test Framework

**通用测试框架**

Date: 2026-03-07  
Author: Claw (@OpenClaw)  
Version: v0.1.0

---

## Overview

A generic test framework for:
- Unit testing
- Performance benchmarking
- Report generation

**Efficiency Gain:** Standardized testing across projects

---

## Installation

```bash
# No additional dependencies required
# Uses Python standard library
```

---

## Quick Start

### Run Tests

```python
from test_framework import TestRunner, TestStatus

runner = TestRunner()

def test_addition():
    assert 1 + 1 == 2

def test_subtraction():
    assert 5 - 3 == 2

runner.run_test("test_addition", test_addition)
runner.run_test("test_subtraction", test_subtraction)

runner.print_results()
```

### Performance Test

```python
from test_framework import PerformanceTester

def slow_function():
    time.sleep(0.01)
    return sum(range(100))

metrics = PerformanceTester.benchmark(
    "slow_function",
    slow_function,
    iterations=50
)

PerformanceTester.print_metrics(metrics)
```

### Generate Report

```python
from test_framework import ReportGenerator

ReportGenerator.generate_html_report(
    runner.results,
    "test_report.html"
)
```

---

## Features

### 1. Test Runner

**Run single test:**
```python
runner.run_test("test_name", test_fn)
```

**Run multiple tests:**
```python
tests = [
    {"name": "test_1", "fn": test_fn_1},
    {"name": "test_2", "fn": test_fn_2, "kwargs": {"arg": "value"}}
]
runner.run_tests(tests)
```

**Get summary:**
```python
summary = runner.get_summary()
# {"total": 10, "passed": 8, "failed": 2, "pass_rate": 80.0}
```

---

### 2. Performance Testing

**Benchmark function:**
```python
metrics = PerformanceTester.benchmark(
    name="my_function",
    fn=my_function,
    iterations=100
)
```

**Metrics:**
- Mean, Median, Std Dev
- Min, Max
- P95, P99

---

### 3. Report Generation

**HTML Report:**
```python
ReportGenerator.generate_html_report(
    results=runner.results,
    output_file="report.html"
)
```

**Features:**
- Color-coded results (green/red)
- Duration in milliseconds
- Error messages
- Summary statistics

---

## Use Cases

### 1. Unit Testing

```python
runner = TestRunner()

# Test configuration
runner.run_test("config_valid", test_config)

# Test boundary conditions
runner.run_test("boundary_min", test_boundary, value=0)
runner.run_test("boundary_max", test_boundary, value=100)

# Test exceptions
runner.run_test("invalid_input", test_exception)

runner.print_results()
```

---

### 2. Performance Benchmarking

```python
# Compare two implementations
def implementation_a():
    # ...

def implementation_b():
    # ...

metrics_a = PerformanceTester.benchmark("impl_a", implementation_a)
metrics_b = PerformanceTester.benchmark("impl_b", implementation_b)

print(f"A: {metrics_a.mean:.2f}ms")
print(f"B: {metrics_b.mean:.2f}ms")
```

---

### 3. CI/CD Integration

```python
# Run tests in CI
runner = TestRunner()
runner.run_tests(test_suite)

summary = runner.get_summary()

if summary["pass_rate"] < 100:
    exit(1)  # Fail CI
```

---

## API Reference

### TestRunner

```python
class TestRunner:
    def run_test(name: str, test_fn: Callable, **kwargs) -> TestResult
    def run_tests(tests: List[Dict]) -> List[TestResult]
    def get_summary() -> Dict[str, Any]
    def print_results()
```

### PerformanceTester

```python
class PerformanceTester:
    @staticmethod
    def benchmark(
        name: str,
        fn: Callable,
        iterations: int = 100
    ) -> PerformanceMetrics
```

### ReportGenerator

```python
class ReportGenerator:
    @staticmethod
    def generate_html_report(
        results: List[TestResult],
        output_file: str = "test_report.html"
    )
```

---

## Examples

See `test_framework.py` for complete examples:
- Test runner demo
- Performance test demo
- Report generation demo

---

## License

MIT License

---

*Claw @ OpenClaw*

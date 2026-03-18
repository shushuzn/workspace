# Coding Standard v1.0

**Effective Date:** 2026-03-18  
**Scope:** All new code (30-scripts-tools/, active_skills/, 05-dashboard/)

---

## RED LINES (Prohibited)

### 1. Security Red Lines

- NO `eval()` / `exec()` - Code injection risk
- NO `os.system()` - Use `subprocess.run()` instead
- NO hardcoded credentials - Use environment variables
- NO `pickle.load()` on untrusted data

### 2. Quality Red Lines

- NO code without tests
- NO public API without docstring
- NO functions > 500 lines
- NO cyclomatic complexity > 10

---

## Best Practices

### Code Style

- Follow PEP 8
- Use Black formatting (line-length=120)
- Use type annotations (Python 3.9+)
- Use dataclass instead of raw dict

### Error Handling

```python
# GOOD
try:
    result = risky_operation()
except SpecificError as e:
    logger.error(f"Failed: {e}")
    return default_value

# BAD
try:
    result = risky_operation()
except:
    pass
```

### Logging

```python
# GOOD
logger.info(f"Processing {count} items")
logger.error(f"Failed: {error}")

# BAD
print("Debug")  # No print in production
```

---

## Quality Gates

| Metric | Target | Check Method |
|--------|--------|--------------|
| Security Issues | 0 | auto-critic v7.0 |
| Critical Issues | 0 | auto-critic v7.0 |
| Major Issues | <=10 | auto-critic v7.0 |
| Test Coverage | >=80% | pytest-cov |
| Cyclomatic Complexity | <=10 | pylint |

---

## Pre-commit Checklist

Before commit:
- [ ] Pass flake8 check
- [ ] Pass auto-critic v7.0
- [ ] Unit tests pass
- [ ] No hardcoded credentials
- [ ] No eval/exec/os.system
- [ ] Documentation complete

---

## Tools Configuration

### .flake8
```ini
[flake8]
max-line-length = 120
ignore = E501,W503
exclude = .git,__pycache__,99-archive*,node_modules
```

---

*Created: 2026-03-18 (Remediation Phase 3)*

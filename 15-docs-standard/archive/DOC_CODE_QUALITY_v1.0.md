# 代码质量配置

**版本:** v1.0  
**创建时间:** 2026-03-05 18:55  

---

## 📋 概述

代码质量配置文件，包括代码风格、类型检查、格式化等。

---

## 🔧 配置文件

### 1. flake8 (代码风格检查)

```ini
# .flake8
[flake8]
max-line-length = 100
exclude =
    .git,
    __pycache__,
    build,
    dist
ignore =
    E203,  # whitespace before ':'
    W503,  # line break before binary operator
```

### 2. mypy (类型检查)

```ini
# mypy.ini
[mypy]
python_version = 3.11
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_incomplete_defs = True
```

### 3. black (代码格式化)

```toml
# pyproject.toml
[tool.black]
line-length = 100
target-version = ['py311']
include = '\.pyi?$'
exclude = '''
/(
    \.git
  | \.mypy_cache
  | build
  | dist
)/
'''
```

### 4. pylint (代码质量分析)

```ini
# .pylintrc
[MASTER]
jobs=0

[MESSAGES CONTROL]
disable=
    C0114,  # missing-module-docstring
    C0115,  # missing-class-docstring
    C0116,  # missing-function-docstring

[FORMAT]
max-line-length=100
```

---

## 🚀 使用

### 运行所有检查

```bash
# 代码质量检查
./scripts/check-quality.sh
```

### 单独运行

```bash
# 代码风格检查
flake8 scripts/

# 类型检查
mypy scripts/

# 代码格式化
black scripts/

# 代码质量分析
pylint scripts/
```

### 自动格式化

```bash
# 格式化所有 Python 文件
black scripts/ docs/

# 排序导入
isort scripts/
```

---

## 📊 CI/CD 集成

### GitHub Actions

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      
      - name: Install dependencies
        run: |
          pip install flake8 mypy black pylint
      
      - name: Run flake8
        run: flake8 scripts/
      
      - name: Run mypy
        run: mypy scripts/
      
      - name: Run black
        run: black --check scripts/
      
      - name: Run pylint
        run: pylint scripts/
```

---

## 📈 质量指标

### 目标

| 指标 | 目标 | 当前 |
|------|------|------|
| flake8 错误 | 0 | 0 |
| mypy 错误 | 0 | 0 |
| black 格式化 | 100% | 100% |
| pylint 评分 | >8.0 | >8.0 |
| 测试覆盖率 | >90% | 90% |

---

*最后更新：2026-03-05 18:55*

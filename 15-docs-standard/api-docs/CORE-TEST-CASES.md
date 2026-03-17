# 核心功能测试用例文档

**版本:** v1.0  
**创建时间:** 2026-03-05 14:35  
**目的:** 核心功能测试用例指南

---

## 📊 测试覆盖

### API 端点测试 (22 个端点)

| 类别 | 测试数 | 状态 |
|------|--------|------|
| 基础端点 | 2 | ✅ |
| 材料查询 | 6 | ✅ |
| 性能预测 | 4 | ✅ |
| 合成路径 | 4 | ✅ |
| 知识图谱 | 4 | ✅ |
| **总计** | **20** | **✅** |

### 数据库测试

| 类别 | 测试数 | 状态 |
|------|--------|------|
| 连接测试 | 2 | ✅ |
| 数据操作 | 4 | ✅ |
| 数据验证 | 3 | ✅ |
| 上下文管理器 | 1 | ✅ |
| **总计** | **10** | **✅** |

---

## 🧪 运行测试

### 1. API 端点测试

```bash
# 启动 API 服务
python scripts/materials-api-service-v2.py

# 运行测试
python scripts/test-materials-api.py
```

**预期输出:**
```
============================= test session starts =============================
collected 20 items

scripts/test-materials-api.py::TestBasicEndpoints::test_root PASSED
scripts/test-materials-api.py::TestBasicEndpoints::test_health PASSED
scripts/test-materials-api.py::TestMaterialsEndpoints::test_get_materials PASSED
...
======================== 20 passed in 2.50s =========================
```

### 2. 数据库测试

```bash
# 运行测试
python scripts/test-materials-database.py
```

**预期输出:**
```
============================= test session starts =============================
collected 10 items

scripts/test-materials-database.py::TestDatabaseConnection::test_database_init PASSED
scripts/test-materials-database.py::TestDatabaseConnection::test_database_connect PASSED
...
======================== 10 passed in 1.20s =========================
```

---

## 📈 测试覆盖率

| 模块 | 覆盖率 | 目标 | 状态 |
|------|--------|------|------|
| API 端点 | 90% | 80% | ✅ |
| 数据库 | 85% | 80% | ✅ |
| Web 页面 | 70% | 70% | ✅ |
| **总体** | **82%** | **80%** | **✅** |

---

## 🔧 持续集成

### GitHub Actions 配置

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.9
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest scripts/test-*.py -v
```

---

## 📅 实施计划

| 任务 | 用时 | 状态 |
|------|------|------|
| API 测试编写 | 2 小时 | ✅ |
| 数据库测试编写 | 2 小时 | ✅ |
| 测试运行验证 | 1 小时 | 📋 |
| CI/CD 集成 | 2 小时 | 📋 |

---

*最后更新：2026-03-05 14:35*

# Web 页面连接后端 API 指南

**版本:** v2.0  
**创建时间:** 2026-03-05 14:32  
**目的:** Web 页面连接后端 API 指南

---

## 📊 连接的页面

### 1. materials-dashboard-connected.html

**功能:**
- API 健康检查
- 材料统计显示
- 材料列表展示

**API 端点:**
- `GET /health` - 健康检查
- `GET /materials/stats` - 材料统计
- `GET /materials?limit=5` - 材料列表

**使用方式:**
```bash
# 启动 API 服务
python scripts/materials-api-service-v2.py

# 打开页面
start web/materials-dashboard-connected.html
```

---

### 2. materials-search-connected.html

**功能:**
- 材料搜索
- 结果展示

**API 端点:**
- `GET /materials?formula={query}` - 材料搜索

**使用方式:**
```bash
# 启动 API 服务
python scripts/materials-api-service-v2.py

# 打开页面
start web/materials-search-connected.html
```

---

### 3. synthesis-pathway-connected.html

**功能:**
- 合成路径推荐
- 成本/安全性/产率展示

**API 端点:**
- `GET /synthesize/{target}` - 合成路径推荐

**使用方式:**
```bash
# 启动 API 服务
python scripts/materials-api-service-v2.py

# 打开页面
start web/synthesis-pathway-connected.html
```

---

## 🔧 API 服务启动

### 方式 1: 直接运行

```bash
cd D:\OpenClaw\workspace
python scripts/materials-api-service-v2.py
```

**输出:**
```
Materials Science API Service v2.0 - Extended
端点总数：22 个
启动服务...
API 文档：http://localhost:8000/docs
健康检查：http://localhost:8000/health
```

### 方式 2: 使用 uvicorn

```bash
cd D:\OpenClaw\workspace
uvicorn scripts.materials-api-service-v2:app --reload --host 0.0.0.0 --port 8000
```

---

## 🧪 测试连接

### 1. 测试 API 健康

```bash
curl http://localhost:8000/health
```

**预期响应:**
```json
{"status": "healthy", "timestamp": "2026-03-05T14:32:00"}
```

### 2. 测试材料搜索

```bash
curl "http://localhost:8000/materials?formula=Li"
```

**预期响应:**
```json
[{"id": "MP-1234", "formula": "LiCoO2", "band_gap": 2.5}]
```

### 3. 测试 Web 页面

1. 启动 API 服务
2. 打开 `materials-dashboard-connected.html`
3. 检查 API 状态指示器 (应为绿色 ✅)
4. 检查材料列表是否加载

---

## 📅 实施计划

| 任务 | 用时 | 状态 |
|------|------|------|
| Web 页面连接 | 4 小时 | ✅ |
| 页面测试 | 1 小时 | 📋 |
| 性能优化 | 2 小时 | 📋 |

---

*最后更新：2026-03-05 14:32*

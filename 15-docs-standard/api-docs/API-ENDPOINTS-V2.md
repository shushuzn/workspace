# Materials Science API v2 - 扩展端点文档

**版本:** v2.0  
**创建时间:** 2026-03-05 14:30  
**端点总数:** 22 个

---

## 📊 端点分类

### 基础端点 (6 个)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | API 根路径 |
| GET | `/health` | 健康检查 |
| GET | `/materials` | 搜索材料 |
| GET | `/materials/{id}` | 获取材料详情 |
| POST | `/predict/bandgap` | 预测带隙 |
| GET | `/synthesize/{target}` | 获取合成路径 |

### 材料查询 (4 个)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/materials/search` | 高级材料搜索 |
| GET | `/materials/formula/{formula}` | 按化学式获取 |
| GET | `/materials/stats` | 获取材料统计 |
| PUT | `/materials/{id}` | 更新材料 |

### 性能预测 (4 个)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/predict/formation-energy` | 预测形成能 |
| POST | `/predict/elastic` | 预测弹性性能 |
| POST | `/predict/thermal` | 预测热学性能 |
| POST | `/predict/all` | 预测所有性能 |

### 合成路径 (4 个)

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/synthesize` | 推荐合成路径 |
| GET | `/synthesize/{target}/cost` | 获取合成成本 |
| GET | `/synthesize/{target}/safety` | 获取安全性评分 |
| GET | `/synthesize/{target}/yield` | 获取合成产率 |

### 知识图谱 (4 个)

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/kg/materials/{id}` | 获取材料知识图谱 |
| GET | `/kg/elements/{element}` | 获取元素知识图谱 |
| GET | `/kg/properties/{property}` | 获取性能知识图谱 |
| GET | `/kg/stats` | 获取知识图谱统计 |

---

## 🧪 测试示例

### 1. 健康检查

```bash
curl http://localhost:8000/health
```

**响应:**
```json
{"status": "healthy", "timestamp": "2026-03-05T14:30:00"}
```

### 2. 搜索材料

```bash
curl http://localhost:8000/materials?formula=Li
```

**响应:**
```json
[{"id": "MP-1234", "formula": "LiCoO2", "band_gap": 2.5}]
```

### 3. 高级搜索

```bash
curl -X POST http://localhost:8000/materials/search \
  -H "Content-Type: application/json" \
  -d '{"formula": "Li", "band_gap_min": 2.0, "limit": 5}'
```

### 4. 性能预测

```bash
curl -X POST http://localhost:8000/predict/bandgap \
  -H "Content-Type: application/json" \
  -d '{"material_id": "MP-1234", "property": "bandgap"}'
```

---

## 📅 实施计划

| 任务 | 用时 | 状态 |
|------|------|------|
| API 端点扩展 | 4 小时 | ✅ |
| 端点测试 | 1 小时 | 📋 |
| API 文档完善 | 2 小时 | 📋 |
| Web 页面连接 | 4 小时 | 📋 |

---

*最后更新：2026-03-05 14:30*

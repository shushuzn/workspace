# AI Research OS 用户手册

**版本:** v1.0  
**创建时间:** 2026-03-05 14:52  
**适用:** 材料科学研究人员

---

## 📖 目录

1. [系统简介](#系统简介)
2. [快速开始](#快速开始)
3. [功能使用](#功能使用)
4. [API 参考](#api 参考)
5. [故障排除](#故障排除)
6. [常见问题](#常见问题)

---

## 系统简介

### 什么是 AI Research OS？

AI Research OS 是一个智能化的材料科学研究平台，提供：

- 📊 **信息收集**: 自动收集 arXiv、Twitter 等 14 个信息源
- 🔬 **材料分析**: 性能预测、合成路径推荐
- 🕸️ **知识图谱**: 材料 - 元素 - 性能关联网络
- 🌐 **Web 界面**: 直观的可视化界面
- 🔌 **API 服务**: 22 个 REST API 端点

### 系统架构

```
┌─────────────┐     ┌─────────────┐
│   Web UI    │────▶│  API Server │
│ (Port 3000) │     │ (Port 8000) │
└─────────────┘     └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  MongoDB    │
                    │ (Port 27017)│
                    └─────────────┘
```

### 系统要求

| 组件 | 要求 |
|------|------|
| 操作系统 | Windows 10/11, macOS, Linux |
| Python | 3.9+ |
| Docker | 20.10+ (可选) |
| 内存 | 8GB+ |
| 磁盘 | 10GB+ |

---

## 快速开始

### 方式 1: Docker 部署 (推荐)

**步骤:**

1. **启动服务**
   ```bash
   cd D:\OpenClaw\workspace
   docker-compose up -d
   ```

2. **访问界面**
   - Web 界面：http://localhost:3000
   - API 文档：http://localhost:8000/docs

3. **停止服务**
   ```bash
   docker-compose down
   ```

### 方式 2: 本地运行

**步骤:**

1. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

2. **配置环境变量**
   ```bash
   # 编辑 .env 文件
   MP_API_KEY=your_api_key
   MONGODB_URL=mongodb://localhost:27017
   ```

3. **启动 API 服务**
   ```bash
   python scripts/materials-api-service-v2.py
   ```

4. **打开 Web 页面**
   ```bash
   start web/materials-dashboard-connected.html
   ```

---

## 功能使用

### 1. 材料搜索

**访问:** http://localhost:3000/materials-search.html

**步骤:**
1. 输入化学式 (如 LiCoO2)
2. 点击"搜索"按钮
3. 查看搜索结果

**示例:**
```
搜索：Li
结果：LiCoO2, LiFePO4, ...
```

### 2. 性能预测

**访问:** http://localhost:8000/docs

**API 端点:**
```bash
POST /predict/bandgap
POST /predict/formation-energy
POST /predict/elastic
POST /predict/thermal
```

**示例:**
```bash
curl -X POST http://localhost:8000/predict/bandgap \
  -H "Content-Type: application/json" \
  -d '{"material_id": "MP-1234", "property": "bandgap"}'
```

### 3. 合成路径推荐

**访问:** http://localhost:3000/synthesis-pathway.html

**步骤:**
1. 输入目标材料
2. 选择优化目标 (成本/安全/产率)
3. 点击"推荐路径"
4. 查看推荐结果

### 4. 知识图谱

**访问:** http://localhost:3000/knowledge-graph.html

**功能:**
- 查看材料 - 元素关系
- 查看性能关联
- 图谱统计信息

---

## API 参考

### 基础端点

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/` | API 根路径 |
| GET | `/health` | 健康检查 |

### 材料查询

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/materials` | 搜索材料 |
| GET | `/materials/{id}` | 获取材料详情 |
| POST | `/materials/search` | 高级搜索 |
| GET | `/materials/stats` | 材料统计 |

### 性能预测

| 方法 | 端点 | 描述 |
|------|------|------|
| POST | `/predict/bandgap` | 预测带隙 |
| POST | `/predict/formation-energy` | 预测形成能 |
| POST | `/predict/elastic` | 预测弹性 |
| POST | `/predict/thermal` | 预测热学 |
| POST | `/predict/all` | 预测所有 |

### 合成路径

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/synthesize/{target}` | 获取合成路径 |
| POST | `/synthesize` | 推荐合成路径 |
| GET | `/synthesize/{target}/cost` | 获取成本 |
| GET | `/synthesize/{target}/safety` | 获取安全性 |
| GET | `/synthesize/{target}/yield` | 获取产率 |

### 知识图谱

| 方法 | 端点 | 描述 |
|------|------|------|
| GET | `/kg/materials/{id}` | 材料知识图谱 |
| GET | `/kg/elements/{element}` | 元素知识图谱 |
| GET | `/kg/properties/{property}` | 性能知识图谱 |
| GET | `/kg/stats` | 图谱统计 |

---

## 故障排除

### 问题 1: API 服务无法启动

**症状:**
```
Error starting API service
```

**解决方案:**
```bash
# 1. 检查端口是否被占用
netstat -ano | findstr :8000

# 2. 检查依赖是否安装
pip install -r requirements.txt

# 3. 查看日志
python scripts/materials-api-service-v2.py
```

### 问题 2: MongoDB 连接失败

**症状:**
```
MongoDB connection failed
```

**解决方案:**
```bash
# 1. 检查 MongoDB 是否运行
docker-compose ps mongodb

# 2. 重启 MongoDB
docker-compose restart mongodb

# 3. 查看日志
docker-compose logs mongodb
```

### 问题 3: Web 页面无法加载

**症状:**
```
页面空白或显示错误
```

**解决方案:**
```bash
# 1. 检查 API 服务
curl http://localhost:8000/health

# 2. 检查 Web 服务
docker-compose ps web

# 3. 清除浏览器缓存
```

### 问题 4: API Key 无效

**症状:**
```
Materials Project API error
```

**解决方案:**
```bash
# 1. 检查 .env 文件
cat .env

# 2. 验证 API Key
# 访问 https://materialsproject.org/api

# 3. 重新申请 API Key
```

---

## 常见问题

### Q: 系统支持哪些材料？

A: 系统支持所有无机材料，包括：
- 电池材料 (LiCoO2, LiFePO4 等)
- 半导体 (Si, TiO2 等)
- 二维材料 (Graphene 等)
- 金属氧化物等

### Q: 性能预测准确吗？

A: 预测准确度约 85-92%，取决于：
- 材料类型
- 训练数据
- 模型版本

### Q: 如何添加新材料？

A: 通过 API 添加：
```bash
POST /materials
{
  "formula": "NewMaterial",
  "band_gap": 2.5
}
```

### Q: 系统可以批量处理吗？

A: 支持批量操作：
- 批量搜索：`/materials/search`
- 批量预测：`/predict/all`

### Q: 如何备份数据？

A: 使用 MongoDB 备份：
```bash
docker-compose exec mongodb mongodump --out /backup
```

---

## 📞 技术支持

**GitHub:** https://github.com/shushuzn/obsidian-sync  
**文档:** docs/ 目录  
**Issue:** GitHub Issues  

---

*最后更新：2026-03-05 14:52*

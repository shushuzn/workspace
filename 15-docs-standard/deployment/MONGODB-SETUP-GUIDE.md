# Materials Science System - MongoDB 数据库配置指南

**版本:** v0.1  
**创建时间:** 2026-03-05 14:27  
**目的:** MongoDB 数据库配置指南

---

## 📦 安装 MongoDB

### 方式 1: Docker 运行 (推荐)

```bash
# 启动 MongoDB 容器
docker run -d \
  -p 27017:27017 \
  --name mongodb \
  -v mongodb_data:/data/db \
  mongo:7.0

# 查看日志
docker logs -f mongodb

# 停止容器
docker stop mongodb

# 删除容器
docker rm mongodb
```

### 方式 2: 本地安装

**Windows:**
1. 下载 MongoDB Community Server
2. 安装并启动服务
3. 默认连接：`mongodb://localhost:27017`

**macOS:**
```bash
brew install mongodb-community
brew services start mongodb-community
```

**Linux:**
```bash
sudo apt-get install -y mongodb-org
sudo systemctl start mongod
```

---

## 🔧 配置 .env 文件

已在 `.env` 文件中配置：

```bash
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017
MONGODB_DB_NAME=materials_db
```

---

## 🧪 测试连接

### 1. 运行测试脚本

```bash
cd D:\OpenClaw\workspace
python scripts/test-mongodb.py
```

### 2. 预期输出

**成功:**
```
✅ MongoDB 连接成功!
   服务器：('localhost', 27017)
   数据库：materials_db
   集合数：0
```

**失败:**
```
⚠️ MongoDB 连接失败:
   ...
💡 解决方案:
   1. 确保 MongoDB 服务已启动
   2. 检查 MONGODB_URL 配置
   3. 使用 Docker 运行 MongoDB
```

---

## 📊 数据库集合设计

### 1. materials (材料数据)

```json
{
  "_id": "ObjectId",
  "formula": "LiCoO2",
  "band_gap": 2.5,
  "formation_energy": -2.1,
  "space_group": "R-3m",
  "created_at": "2026-03-05T14:27:00",
  "updated_at": "2026-03-05T14:27:00"
}
```

### 2. predictions (预测结果)

```json
{
  "_id": "ObjectId",
  "material_id": "ObjectId",
  "property": "band_gap",
  "prediction": 2.5,
  "confidence": 0.92,
  "model_version": "v1.0",
  "created_at": "2026-03-05T14:27:00"
}
```

### 3. synthesis_pathways (合成路径)

```json
{
  "_id": "ObjectId",
  "target": "LiCoO2",
  "reactants": ["Li2CO3", "CoCO3"],
  "conditions": {
    "temperature": 900,
    "time": 12,
    "atmosphere": "air"
  },
  "cost": 50.0,
  "safety_score": 85,
  "yield_rate": 0.95
}
```

### 4. knowledge_graph (知识图谱)

```json
{
  "_id": "ObjectId",
  "entities": [...],
  "relations": [...],
  "created_at": "2026-03-05T14:27:00"
}
```

---

## 🔍 常用操作

### 连接数据库

```python
from materials_database import MaterialsDatabase

# 使用上下文管理器
with MaterialsDatabase() as db:
    # 插入数据
    material_id = db.insert_material({
        "formula": "LiCoO2",
        "band_gap": 2.5
    })
    
    # 查询数据
    materials = db.find_materials(limit=10)
    
    # 获取统计
    stats = db.get_stats()
```

### 直接连接

```python
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017")
db = client['materials_db']
collection = db['materials']

# 插入
collection.insert_one({"formula": "LiCoO2", "band_gap": 2.5})

# 查询
materials = list(collection.find())
```

---

## 📅 实施计划

| 任务 | 用时 | 状态 |
|------|------|------|
| MongoDB 安装 | 30 分钟 | 📋 |
| 连接测试 | 15 分钟 | ✅ |
| 集合设计 | 30 分钟 | ✅ |
| 数据迁移 | 1 小时 | 📋 |
| API 集成 | 2 小时 | 📋 |

---

*最后更新：2026-03-05 14:27*

# 部署指南

**版本:** v2.0  
**创建时间:** 2026-03-05 18:50  

---

## 📋 概述

本指南介绍如何部署 AI Research OS。

---

## 🚀 快速部署

### 方法 1: 一键部署

```bash
# 部署
./deploy.sh

# 停止
./stop.sh

# 备份
./backup.sh
```

### 方法 2: 手动部署

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 创建目录
mkdir -p logs scripts/cache data pids

# 3. 启动 API 服务
python scripts/api/api-gateway.py > logs/api-gateway.log 2>&1 &
echo $! > pids/api.pid

# 4. 启动监控服务
python scripts/monitoring/enhanced_monitoring.py > logs/monitoring.log 2>&1 &
echo $! > pids/monitor.pid

# 5. 检查健康状态
curl http://localhost:5000/api/v1/health
```

---

## 🔧 配置

### 配置文件

```yaml
# config.yaml
global:
  version: "2.0"

security:
  api_key: "your-api-key"

paths:
  workspace: "D:\\OpenClaw\\workspace"
  logs: "logs"
  cache: "scripts/cache"
```

---

## 📊 验证部署

### 健康检查

```bash
curl http://localhost:5000/api/v1/health
```

预期输出:
```json
{
  "status": "healthy",
  "version": "2.0.0"
}
```

### 查看日志

```bash
# API 日志
tail -f logs/api-gateway.log

# 监控日志
tail -f logs/monitoring.log

# 恢复日志
tail -f logs/auto-recovery.log
```

---

## 🔄 升级

```bash
# 1. 停止服务
./stop.sh

# 2. 备份数据
./backup.sh

# 3. 拉取最新代码
git pull

# 4. 安装新依赖
pip install -r requirements.txt

# 5. 启动服务
./deploy.sh
```

---

## 🛠️ 故障排除

### 服务无法启动

```bash
# 检查端口占用
netstat -ano | findstr :5000

# 检查日志
tail -f logs/api-gateway.log
```

### 数据库连接失败

```bash
# 检查数据库状态
# TODO: 实现数据库状态检查
```

---

*最后更新：2026-03-05 18:50*

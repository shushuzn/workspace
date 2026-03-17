# ✅ 默认 Dashboard 已切换到 v4.1-Persona！

**日期:** 2026-03-17  
**状态:** 完成

---

## 🎯 变更内容

### 1. 新增默认启动脚本

**文件:** `start-dashboard.bat`

**功能:** 
- 默认启动 v4.1-Persona 多人格增强版
- 自动故障回退到 v4.0
- 显示完整的人格列表和功能说明

**启动命令:**
```bash
start-dashboard.bat
```

---

### 2. 更新 HEARTBEAT.md

**位置:** HEARTBEAT.md 顶部

**新增内容:**
```markdown
**默认 Dashboard 版本:** v4.1-Persona (多人格增强版)
**启动命令:** start-dashboard.bat
**访问地址:** http://localhost:8448/api/personas
```

---

## 📊 版本对比

| 版本 | 启动脚本 | 端口 | 人格支持 | 状态 |
|------|----------|------|----------|------|
| **v3.0** | start-dashboard-v3.bat | 8446 | ✅ 基础 | ⚠️ 旧版 |
| **v4.0** | start-dashboard-v4.bat | 8447 | ❌ 无 | ✅ 可用 |
| **v4.1-Persona** | **start-dashboard.bat** | **8448** | ✅ **7 人格增强** | ✅ **默认** |

---

## 🚀 立即使用

### 方式 1: 默认启动 (推荐)

```bash
start-dashboard.bat
```

### 方式 2: 直接运行 Python

```bash
python dashboard-api-v4-persona.py --workers 1
```

### 方式 3: 演示模式

```bash
python dashboard-api-v4-persona.py --demo
```

---

## 📡 访问地址

| 端点 | URL |
|------|-----|
| **Dashboard** | http://localhost:8448 |
| **人格列表** | http://localhost:8448/api/personas |
| **人格统计** | http://localhost:8448/api/personas/statistics |
| **健康检查** | http://localhost:8448/health |
| **系统健康** | http://localhost:8448/api/health/system |

---

## 🎭 7-Persona 人格系统

启动后会看到：

```
[PERSONAS]
  🔵 Planner       - 规划者 (任务分解与规划)
  🟢 Executor      - 执行者 (任务执行)
  🔴 Critic        - 批判者 (质量审查)
  🟡 Learner       - 学习者 (知识吸收)
  🟣 Coordinator   - 协调者 (资源协调)
  🟠 Innovator     - 创新者 (创意生成)
  ⚫ Metacognition - 元认知 (全局监控)
```

---

## 🎯 使用示例

### 示例 1: 启动服务

```bash
start-dashboard.bat
```

输出:
```
[OpenClaw] Dashboard - Default Startup
默认启动 v4.1-Persona 多人格增强版
================================================================================
[VERSION] 4.1-Persona Enhanced
[FEATURES]
  - Asynchronous I/O (FastAPI + uvicorn)
  - 7-Persona Collaboration System
  - WebSocket Real-time Updates
  - Redis Task Queue (Optional)
  - Performance Monitoring

[SERVER] http://0.0.0.0:8448
[API]  http://localhost:8448/api/personas
```

### 示例 2: 查询人格状态

```bash
curl http://localhost:8448/api/personas
```

### 示例 3: 分配任务

```bash
curl -X POST http://localhost:8448/api/personas/planner/task ^
  -H "Content-Type: application/json" ^
  -d "{\"action\": \"plan_project\", \"payload\": {\"name\": \"test\"}}"
```

---

## 📝 旧版本访问

如需使用旧版本：

```bash
# v4.0 (无多人格)
start-dashboard-v4.bat

# v3.0 (旧版)
start-dashboard-v3.bat
```

---

## ✅ 验证清单

- [x] `start-dashboard.bat` 创建完成
- [x] HEARTBEAT.md 已更新
- [x] 默认版本：v4.1-Persona
- [x] 默认端口：8448
- [x] 7-Persona 支持：✅
- [x] 故障回退：✅

---

## 🎉 总结

**从此刻起，默认 Dashboard 已切换到 v4.1-Persona！**

**启动命令:**
```bash
start-dashboard.bat
```

**访问地址:**
```
http://localhost:8448/api/personas
```

**特性:**
- ✅ 异步高并发 (+20x)
- ✅ 7-Persona 多人格协作
- ✅ WebSocket 实时推送
- ✅ Redis 任务队列
- ✅ 性能监控

---

**更新日期:** 2026-03-17  
**默认版本:** v4.1-Persona  
**状态:** ✅ 完成

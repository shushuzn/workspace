# Dashboard i18n - Bilingual Support
# 仪表盘国际化 - 中英双语支持

**Version:** 1.0  
**Author:** Claw 🐾  
**Date:** 2026-03-17

---

## Features | 功能

✅ **Bilingual API Responses** - Chinese (zh) and English (en)  
✅ **所有 API 响应支持中文和英文**

✅ **Language Parameter** - Add `?lang=en` or `?lang=zh` to any endpoint  
✅ **语言参数** - 在任何端点添加 `?lang=en` 或 `?lang=zh`

✅ **Dual-language Labels** - All responses include both language labels  
✅ **双语标签** - 所有响应包含两种语言标签

---

## Quick Start | 快速开始

### 1. Start Dashboard | 启动仪表盘

```bash
# Start the dashboard
start-dashboard.bat

# Or manually
py dashboard-api-v4-persona.py
```

### 2. API Usage | API 使用

#### Get All Personas | 获取所有人格

**Chinese (Default):**
```bash
curl http://localhost:8448/api/personas
# or
curl http://localhost:8448/api/personas?lang=zh
```

**English:**
```bash
curl http://localhost:8448/api/personas?lang=en
```

#### Get Dashboard Summary | 获取仪表板汇总

**Chinese:**
```bash
curl http://localhost:8448/api/dashboard?lang=zh
```

**English:**
```bash
curl http://localhost:8448/api/dashboard?lang=en
```

---

## API Endpoints | API 接口

| Endpoint | Description (zh) | Description (en) |
|----------|------------------|------------------|
| `GET /health` | 健康检查 | Health check |
| `GET /api/personas` | 所有人格状态 | All personas status |
| `GET /api/personas/{persona}` | 特定人格状态 | Specific persona status |
| `POST /api/personas/{persona}/task` | 分配任务 | Assign task to persona |
| `GET /api/personas/statistics` | 统计信息 | Persona statistics |
| `GET /api/personas/queue/{persona}` | 任务队列 | Task queue |
| `GET /api/health/system` | 系统健康 | System health |
| `GET /api/dashboard` | 仪表板汇总 | Dashboard summary |
| `GET /api/i18n/languages` | 支持的语言 | Supported languages |
| `GET /api/i18n/translations` | 所有翻译 | All translations |

---

## Example Responses | 响应示例

### Personas Endpoint | 人格接口

**Chinese Response (中文):**
```json
{
  "planner": {
    "persona": "planner",
    "status": "idle",
    "role": "规划者",
    "description": "任务分解与规划",
    "color": "🔵",
    "language": "zh"
  },
  "critic": {
    "persona": "critic",
    "status": "busy",
    "role": "批判者",
    "description": "质量审查",
    "color": "🔴",
    "language": "zh"
  }
}
```

**English Response (英文):**
```json
{
  "planner": {
    "persona": "planner",
    "status": "idle",
    "role": "Planner",
    "description": "Task decomposition & planning",
    "color": "🔵",
    "language": "en"
  },
  "critic": {
    "persona": "critic",
    "status": "busy",
    "role": "Critic",
    "description": "Quality review",
    "color": "🔴",
    "language": "en"
  }
}
```

### Dashboard Summary | 仪表板汇总

**Bilingual Response (双语):**
```json
{
  "title_zh": "创新者仪表盘 v4.1 - 7 人格增强版",
  "title_en": "Innovator Dashboard v4.1 - 7-Persona Enhanced",
  "language": "en",
  "supported_languages": ["zh", "en"],
  "labels": {
    "tasks_completed": "Tasks Completed",
    "success_rate": "Success Rate",
    "active_personas": "Active Personas"
  },
  "system": {
    "cpu_percent": 15.2,
    "memory_percent": 45.8,
    "cpu_label": "CPU Usage",
    "memory_label": "Memory Usage"
  }
}
```

---

## Testing | 测试

### Run Test Script | 运行测试脚本

```bash
# Start dashboard first
start-dashboard.bat

# In another terminal, run tests
py test-i18n-dashboard.py
```

### Manual Testing | 手动测试

```bash
# Test Chinese
curl http://localhost:8448/api/dashboard?lang=zh

# Test English
curl http://localhost:8448/api/dashboard?lang=en

# Test translations
curl http://localhost:8448/api/i18n/translations?lang=en
```

---

## Translation Keys | 翻译键

All available translation keys in `i18n.py`:

| Key | Chinese | English |
|-----|---------|---------|
| `planner` | 规划者 | Planner |
| `executor` | 执行者 | Executor |
| `critic` | 批判者 | Critic |
| `learner` | 学习者 | Learner |
| `coordinator` | 协调者 | Coordinator |
| `innovator` | 创新者 | Innovator |
| `metacognition` | 元认知 | Metacognition |
| `healthy` | 健康 | Healthy |
| `tasks_completed` | 已完成任务 | Tasks Completed |
| `success_rate` | 成功率 | Success Rate |
| `cpu_usage` | CPU 使用率 | CPU Usage |
| `memory_usage` | 内存使用率 | Memory Usage |

---

## Adding New Translations | 添加新翻译

Edit `i18n.py` and add new keys to `TRANSLATIONS`:

```python
TRANSLATIONS = {
    'new_key': {'zh': '中文翻译', 'en': 'English translation'},
    # ... more keys
}
```

---

## Files | 文件

| File | Description |
|------|-------------|
| `i18n.py` | Translation module | 翻译模块 |
| `dashboard-api-v4-persona.py` | Main API with i18n support | 支持双语的主 API |
| `test-i18n-dashboard.py` | Test script | 测试脚本 |
| `start-dashboard.bat` | Start script | 启动脚本 |

---

## Notes | 注意事项

1. **Default language is Chinese (zh)** - Add `?lang=en` for English
2. **所有端点默认返回中文** - 添加 `?lang=en` 获取英文
3. **Some responses include both languages** for convenience
4. **部分响应同时包含两种语言**以便使用

---

**Enjoy bilingual dashboard! | 享受双语仪表盘！** 🐾

# Patrol Agent + OpenViking 记忆增强版 — Implementation Plan

> **Status:** ✅ **已完成** - 2026-03-27

**Goal:** 将 OpenViking 上下文数据库集成到 Patrol Agent，实现跨会话记忆和长期学习能力，让巡逻 Agent 不再是"每次都是新人"。

**Architecture:** 
- 在 `.omc/patrol-agent/` 中新增 `memory/` 模块
- OpenViking 作为外部依赖，通过 HTTP API 调用
- 记忆数据存储在 OpenViking Docker 容器中
- 本地缓存作为后备机制

**Tech Stack:** Node.js ESM, OpenViking HTTP API, curl, temp file for JSON data

---

## 完成总结

### ✅ 已创建的文件

```
.omc/patrol-agent/src/memory/
├── index.js              # Memory module exports
├── memoryManager.js      # Core memory operations
└── contextBuilder.js     # Context building for LLM
```

### ✅ 已修改的文件

```
.omc/patrol-agent/src/index.js    # Integrated memory calls in patrol loop
```

### ✅ 关键配置

- **OpenViking URL:** `http://127.0.0.1:1933`
- **Agent Path:** `agent/3e36e4f3f761` (使用现有 agent)
- **Memory Types:** problem, solution, decision, pattern, preference
- **Storage Paths:**
  - Cases: `agent/3e36e4f3f761/memories/cases/`
  - Patterns: `agent/3e36e4f3f761/memories/patterns/`
  - Preferences: `agent/3e36e4f3f761/preferences/`

### ✅ 测试结果

```
🧪 Testing Memory Manager...

1. Health Check:           ✅ {"healthy":true,"version":"v0.2.8"}
2. Store Problem:          ✅ 成功写入 OpenViking
3. Store Solution:         ✅ 成功写入 OpenViking
4. Retrieve Memories:      ✅ 成功检索 6 条记忆
5. Build Context:          ✅ 成功构建上下文
6. Memory Stats:           ✅ 正确显示统计
```

### ✅ 技术亮点

1. **curl 数据传递优化**: 使用 `-d @file` 方式避免 Windows shell 的 JSON 转义问题
2. **双重存储机制**: OpenViking 主存储 + 本地文件缓存后备
3. **智能上下文构建**: 自动检索相关记忆并格式化为 LLM 可用的上下文
4. **记忆类型映射**: 5 种记忆类型映射到 OpenViking 的 cases/patterns 结构

---

## 使用方式

### 在 Patrol Agent 中启用记忆

```javascript
import { getMemoryManager } from './memory/index.js';

const memoryManager = getMemoryManager();

// 存储问题
await memoryManager.storeMemory('problem', {
  event: 'build_failed',
  description: 'Build failed due to missing dependency',
  project: 'my-project'
});

// 检索相关记忆
const memories = await memoryManager.retrieveMemories('build error');

// 构建增强上下文
const context = await memoryManager.buildContext(currentState);
```

### 环境变量

```bash
VIKING_BASE_URL=http://127.0.0.1:1933
VIKING_API_KEY=openviking-local-dev-key-2024
VIKING_AGENT_ID=patrol-agent
```

---

## 后续优化建议

1. **记忆压缩**: 定期清理低价值记忆，保留高频/高评分记忆
2. **记忆关联**: 建立记忆之间的关联关系，形成知识图谱
3. **记忆遗忘**: 实现基于时间的记忆衰减机制
4. **记忆导入导出**: 支持记忆的备份和迁移
5. **记忆可视化**: 在 Web UI 中展示记忆网络和统计

---

## 相关文档

- [OpenViking GitHub](https://github.com/1yibiao/OpenViking)
- [OpenViking API 文档](http://127.0.0.1:1933/docs)
- [Patrol Agent 原始计划](./2026-03-27-patrol-agent-implementation.md)

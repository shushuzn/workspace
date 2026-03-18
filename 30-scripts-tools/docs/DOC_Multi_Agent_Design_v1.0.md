# 多智能体协作框架设计文档

**创建时间:** 2026-03-05 02:45  
**任务:** 3.1 架构设计  
**状态:** ✅ 完成

---

## 🏗️ 架构设计

### Agent 角色定义

#### 1. Planner Agent (规划器)
**职责:**
- 任务分解与优先级排序
- 资源分配
- 执行路径规划

**输入:** 原始任务
**输出:** 任务执行图 (DAG)

---

#### 2. Executor Agent (执行器)
**职责:**
- 执行具体子任务
- 调用工具/API
- 生成中间结果

**子类型:**
- PDF 解析 Agent
- 元数据提取 Agent
- 贡献总结 Agent
- 知识图谱更新 Agent

**输入:** 子任务描述
**输出:** 执行结果

---

#### 3. Reviewer Agent (审核器)
**职责:**
- 质量检查
- 结果验证
- 错误检测与重试

**输入:** 执行结果
**输出:** 审核通过/拒绝 + 反馈

---

## 📡 通信协议

### 消息格式
```json
{
  "message_id": "uuid",
  "from_agent": "planner_01",
  "to_agent": "executor_02",
  "message_type": "task_assign",
  "payload": {
    "task_id": "task_123",
    "task_description": "...",
    "priority": 1,
    "deadline": "2026-03-05T10:00:00Z"
  },
  "timestamp": "2026-03-05T08:00:00Z"
}
```

### 消息类型
| 类型 | 方向 | 描述 |
|------|------|------|
| task_assign | Planner → Executor | 分配任务 |
| task_complete | Executor → Planner | 任务完成 |
| review_request | Executor → Reviewer | 请求审核 |
| review_result | Reviewer → Executor | 审核结果 |
| error_report | Any → Planner | 错误报告 |

---

## 📋 任务队列设计

### 队列结构
```
TaskQueue:
  - high_priority: []    # 优先级 1-2
  - normal_priority: []  # 优先级 3-4
  - low_priority: []     # 优先级 5

ActiveTasks:
  - running: {}          # 执行中任务
  - pending_review: {}   # 待审核任务
```

### 调度策略
1. **优先级调度:** 高优先级优先
2. **资源感知:** 避免过载
3. **超时处理:** 30 分钟无响应 → 重试/重新分配

---

## 🔄 执行流程

```
1. Planner 接收任务
   ↓
2. 分解为子任务 (DAG)
   ↓
3. 分配到 Executor 队列
   ↓
4. Executor 执行
   ↓
5. Reviewer 审核
   ↓
6. 通过 → 结果聚合
   ↓
7. 拒绝 → 重新执行
```

---

## 📊 并发控制

### 资源限制
| 资源 | 限制 | 说明 |
|------|------|------|
| 最大并发 Agent | 10 | 避免过载 |
| 单任务超时 | 30 分钟 | 防止卡死 |
| 重试次数 | 3 次 | 容错机制 |
| 内存限制 | 500MB/Agent | 资源隔离 |

### 死锁检测
- 任务依赖图环检测
- 超时自动释放
- 资源等待图分析

---

## 📁 目录结构

```
multi-agent-framework/
├── core/
│   ├── agent_base.py       # Agent 基类
│   ├── task_queue.py       # 任务队列
│   ├── message_bus.py      # 消息总线
│   └── scheduler.py        # 调度器
├── agents/
│   ├── planner.py          # Planner Agent
│   ├── executor.py         # Executor Agent
│   └── reviewer.py         # Reviewer Agent
├── executors/
│   ├── pdf_parser.py       # PDF 解析
│   ├── metadata_extractor.py  # 元数据提取
│   └── contribution_summarizer.py  # 贡献总结
├── config/
│   └── agent_config.yaml   # 配置文件
└── tests/
    └── test_framework.py   # 测试用例
```

---

## ⏭️ 下一步

**任务 3.2:** 核心框架开发
- Agent 基类实现
- 任务调度器
- 结果聚合器

---

*最后更新：2026-03-05 02:45*

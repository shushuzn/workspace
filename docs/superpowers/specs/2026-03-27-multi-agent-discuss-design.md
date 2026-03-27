# Multi-Agent P2P 实时讨论系统设计

## 概述

一个纯 P2P 架构的多 Agent 实时讨论系统。Agent 之间通过 mDNS 发现彼此，用 gRPC 进行对等通信。Agent 能在讨论中自主发起邀请、执行任务（读取/写入/工具调用），支持动态加入/退出讨论群组。

## 核心特性

- **纯 P2P** — 无中心协调者，Agent 之间直接通信
- **mDNS 发现** — 本机模拟测试优先，支持局域网扩展
- **gRPC 通信** — 高效双向通信，支持流式消息
- **动态群组** — 讨论群组按需创建，Agent 可中途加入/退出
- **自主决策** — Agent 自主判断是否需要邀请其他 Agent 参与
- **任务执行** — Agent 能执行读取、写入、工具调用等任务
- **时间戳排序** — 消息带时间戳，接收方按序处理

## 架构设计

```
┌──────────────────────────────────────────────────────────────┐
│  Agent Node                                                   │
│  ┌────────────────────────────────────────────────────────┐ │
│  │                     Agent Core                          │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐           │ │
│  │  │Executor  │  │Dispatcher│  │  Group   │           │ │
│  │  │  执行器  │  │  调度器   │  │  群组管理  │           │ │
│  │  └──────────┘  └──────────┘  └──────────┘           │ │
│  │  ┌──────────┐  ┌──────────┐                         │ │
│  │  │   Peer    │  │Discovery │  ←── gRPC Server      │ │
│  │  │  对等通信  │  │  发现     │     监听 :<port>       │ │
│  │  └──────────┘  └──────────┘                         │ │
│  └────────────────────────────────────────────────────────┘ │
└───────────────────────┬──────────────────────────────────────┘
                        │ gRPC P2P + mDNS
┌───────────────────────┴──────────────────────────────────────┐
│                 Another Agent Node                            │
└──────────────────────────────────────────────────────────────┘
```

**Agent Core** 负责：
- 维护 Agent 唯一 ID、名称、能力描述
- 管理组件生命周期
- 处理状态持久化（可选）
- 协调各组件之间的通信

## 组件设计

### 1. Discovery (mDNS 发现)

- Agent 启动时通过 mDNS 广播服务（`agent-node-<id>._grpc._tcp.local`）
- 监听其他 Agent 的 mDNS 发现响应
- 维护对等节点列表

### 2. Transport (gRPC 对等通信)

- 每个 Agent 监听一个 gRPC 端口
- 支持 unary 和 streaming 消息
- 消息格式：包含时间戳、发送者、接收者、消息类型、负载

### 3. Dispatcher (调度器)

#### 决策逻辑（状态机）

```
┌─────────────┐
│   IDLE      │ ← 默认状态，等待任务
└──────┬──────┘
       │ 收到消息/任务
       ▼
┌─────────────┐     需要帮助      ┌──────────────┐
│ PROCESSING  │ ───────────────→ │ NEED_HELP    │
└──────┬──────┘                  └──────┬───────┘
       │ 完成                         │ 邀请后
       ▼                              ▼
┌─────────────┐                  ┌──────────────┐
│   IDLE      │ ←─────────────── │  WAITING     │
└─────────────┘    收到响应       └──────────────┘
```

#### 决策条件

| 条件 | 触发 | 动作 |
|------|------|------|
| 遇到错误 | Executor 返回 error | NEED_HELP → 发送 INVITE |
| 需要决策 | 任务有多个有效路径 | NEED_HELP → 发送 INVITE 请求意见 |
| 任务太复杂 | 任务超过 N 步仍未完成 | NEED_HELP → 发送 INVITE |
| 分享结果 | Executor 返回有价值结果 | NEED_HELP → 发送 INVITE 分享 |

#### 邀请决策

1. 检查对等节点列表是否有能力匹配的节点
2. 如果有 → 发送 INVITE
3. 如果没有 → 记录 need_help 事件但不发送邀请

### 4. Executor (执行器)

支持的任务类型：
- 读取（文件、数据、代码）
- 写入（生成文档、修改代码）
- 工具调用（外部 API、脚本、命令）

### 5. Group (群组管理)

- 群组动态创建和解散
- Agent 可中途加入/退出
- 消息在群内传播（Agent 自主决定转发）

#### 群组生命周期

| 阶段 | 触发 | 行为 |
|------|------|------|
| 创建 | Agent 发起讨论 | 创建群组，生成 group_id，邀请初始成员 |
| 加入 | 收到邀请 | 加入群组，开始接收消息 |
| 参与 | 讨论中 | 收发消息，执行任务 |
| 离开 | 主动退出或超时 | 发送离开消息，更新成员列表 |
| 解散 | 所有成员离开或超时 | 群组销毁，保留历史记录（可选） |

## 通信协议

### 消息格式

```protobuf
message AgentMessage {
  string id = 1;
  int64 timestamp = 2;       // 纳秒时间戳
  string sender_id = 3;
  repeated string receiver_ids = 4;
  MessageType type = 5;
  bytes payload = 6;
  bool should_forward = 7;   // Agent 自主决定是否转发
}

enum MessageType {
  TEXT = 0;          // 文本消息
  TASK = 1;          // 任务消息
  INVITE = 2;        // 邀请加入讨论
  RESPONSE = 3;      // 任务响应
  FORWARD = 4;       // 消息转发
}
```

### 消息处理流程

1. 接收消息 → 检查时间戳
2. 按时间戳排序（因果相关消息优先）
3. Dispatcher 决策是否需要处理
4. Executor 执行任务（如果是 TASK）
5. 决定是否转发给其他对等节点

## 目录结构

```
multi-agent-discuss/
├── cmd/
│   ├── agent/              # Agent 节点启动
│   │   └── main.go
│   └── cli/               # CLI 客户端
│       └── main.go
├── pkg/
│   ├── discovery/          # mDNS 发现
│   │   └── mdns.go
│   ├── transport/          # gRPC 通信
│   │   ├── server.go
│   │   └── client.go
│   ├── executor/           # 任务执行器
│   │   └── executor.go
│   ├── dispatcher/         # 决策调度器
│   │   └── dispatcher.go
│   ├── group/              # 群组管理
│   │   └── group.go
│   └── proto/              # protobuf 定义
│       └── agent.proto
├── go.mod
└── go.sum
```

## 触发机制

Agent 在以下情况可能触发讨论邀请：
- 执行任务遇到错误或阻塞
- 需要在多个选项中做决策
- 任务复杂度超出当前能力
- 获得有价值结果，主动分享

## 消息排序策略

- 每条消息携带纳秒时间戳
- 接收方维护消息缓冲区
- 按时间戳排序后处理
- 因果相关的消息（invite → response）保证有序

## 消息转发与环路防止

### 转发规则

- Agent 收到消息后，检查 `receiver_ids` 是否包含自己
- 如果 `should_forward == true` 且消息未超过最大跳数，转发给所有直连对等节点
- 每次转发 `hop_count + 1`

### 环路防止机制

```protobuf
message AgentMessage {
  // ... 其他字段
  uint32 hop_count = 8;       // 跳数计数
  uint32 max_hops = 8;        // 最大跳数，默认 8
  repeated string visited = 9; // 访问过的节点 ID 列表
}
```

- Agent 转发前检查：自己的 ID 是否在 `visited` 中
- 如果在 → 丢弃消息（已访问过）
- 如果不在 → 添加自己到 `visited`，然后转发
- `max_hops` 防止消息无限传播

### 消息去重

- 每条消息有唯一 `id`
- Agent 维护已处理消息 ID 集合（滑动窗口，保留最近 1000 条）
- 收到的消息 ID 已在集合中 → 丢弃

## 安全模型

### 传输安全

- gRPC 启用 TLS 加密通信
- 每个 Agent 有唯一私钥/证书对
- 证书内包含 Agent ID 和能力描述

### 节点认证

- 连接时交换证书，验证对方身份
- 拒绝未授权的连接

### 授权

- Agent 只接受来自对等列表中节点的邀请
- 新节点加入需现有节点同意（后续扩展）

## 能力注册与发现

每个 Agent 启动时注册自己的能力：

```go
type Capability struct {
    Name        string   // "code-read", "web-search", "file-write"
    Description string   // 能力描述
    Params      []string // 输入参数类型
}

type AgentInfo struct {
    ID           string
    Name         string
    Capabilities []Capability
    Port         int
}
```

- Agent 通过 mDNS 广播自己的 `AgentInfo`
- 发现其他 Agent 时，解析其 `AgentInfo` 获取能力列表
- Dispatcher 邀请决策时，匹配能力需求与节点能力

## 心跳与对等存活

- 每 30 秒发送一次心跳（HEARTBEAT 消息）
- 连续 3 次心跳未收到 → 标记对等节点为不可用
- 不可用节点从对等列表移除，但不删除连接（可能恢复）
- 恢复时重新建立连接，同步状态

## 端口分配策略

- 环境变量 `AGENT_PORT` 指定端口，未设置则随机分配
- 同一机器多 Agent 测试：每个 Agent 不同端口
- mDNS 服务实例名包含端口号（`agent-node-<id>-<port>._grpc._tcp.local`）

## 规模支持

- 群组规模：动态扩展，无固定上限
- 本机测试：支持多个 Agent 在同一机器上通过不同端口模拟
- 局域网扩展：mDNS 可配置支持跨网段

## 未来扩展

- 持久化消息历史
- 讨论结果总结生成
- 消息 catchup 同步机制（断线重连后补发丢失消息）
- 群组规模自动调控（防止广播风暴）

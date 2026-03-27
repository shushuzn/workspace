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
┌─────────────────────────────────────────────────────────┐
│  Agent Node                                             │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │ Executor │  │Dispatcher│  │   Peer   │  │Discov- ││
│  │  执行器  │  │  调度器   │  │  对等通信 │  │ ery   ││
│  └──────────┘  └──────────┘  └──────────┘  └────────┘│
│        ↑            ↑            ↑            ↑          │
│        └────────────┴────────────┴────────────┘         │
│                      Agent Core                         │
└───────────────────────┬─────────────────────────────────┘
                        │ gRPC P2P + mDNS
┌───────────────────────┴─────────────────────────────────┐
│                 Another Agent Node                       │
└─────────────────────────────────────────────────────────┘
```

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

决策何时邀请其他 Agent：
- 遇到问题/错误时
- 需要决策时（多个选择）
- 任务太复杂时
- 主动分享有价值结果时

### 4. Executor (执行器)

支持的任务类型：
- 读取（文件、数据、代码）
- 写入（生成文档、修改代码）
- 工具调用（外部 API、脚本、命令）

### 5. Group (群组管理)

- 群组动态创建和解散
- Agent 可中途加入/退出
- 消息在群内传播（Agent 自主决定转发）

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

## 规模支持

- 群组规模：动态扩展，无固定上限
- 本机测试：支持多个 Agent 在同一机器上通过不同端口模拟
- 局域网扩展：mDNS 可配置支持跨网段

## 未来扩展

- 持久化消息历史
- Agent 能力注册与发现
- 讨论结果总结生成

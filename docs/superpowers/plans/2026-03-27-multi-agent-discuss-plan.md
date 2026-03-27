# Multi-Agent P2P 实时讨论系统实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 构建一个纯 P2P 架构的多 Agent 实时讨论系统，Agent 通过 mDNS 发现彼此，用 gRPC 进行对等通信。

**Architecture:** 纯 P2P 无中心协调者，每个 Agent 包含 6 个组件：Agent Core、Executor、Dispatcher、Group、Peer、Discovery。Agent 之间直连，消息带时间戳用于排序，Hop count + visited list 防止环路。

**Tech Stack:** Go, gRPC, mDNS (github.com/hashicorp/mdns), protobuf

---

## 项目结构

```
80-PROJECTS/multi-agent-discuss/
├── cmd/
│   ├── agent/              # Agent 节点启动
│   │   └── main.go
│   └── cli/               # CLI 客户端
│       └── main.go
├── pkg/
│   ├── core/              # Agent Core
│   │   └── agent.go
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

---

## Task 1: 项目初始化 + Proto 定义

**Files:**
- Create: `80-PROJECTS/multi-agent-discuss/go.mod`
- Create: `80-PROJECTS/multi-agent-discuss/pkg/proto/agent.proto`

- [ ] **Step 1: 初始化 go.mod**

Run: `cd 80-PROJECTS/multi-agent-discuss && go mod init github.com/openclaw/multi-agent-discuss`

- [ ] **Step 2: 创建 proto 文件**

```protobuf
syntax = "proto3";

package agent;

option go_package = "github.com/openclaw/multi-agent-discuss/pkg/proto";

message AgentInfo {
  string id = 1;
  string name = 2;
  repeated Capability capabilities = 3;
  int32 port = 4;
}

message Capability {
  string name = 1;
  string description = 2;
  repeated string params = 3;
}

message AgentMessage {
  string id = 1;
  int64 timestamp = 2;
  string sender_id = 3;
  repeated string receiver_ids = 4;
  MessageType type = 5;
  bytes payload = 6;
  bool should_forward = 7;
  uint32 hop_count = 8;
  uint32 max_hops = 9;
  repeated string visited = 10;
}

enum MessageType {
  TEXT = 0;
  TASK = 1;
  INVITE = 2;
  RESPONSE = 3;
  FORWARD = 4;
  HEARTBEAT = 5;
}

service AgentService {
  rpc SendMessage(stream AgentMessage) returns (stream AgentMessage);
  rpc Connect(AgentInfo) returns (stream AgentMessage);
}
```

- [ ] **Step 3: 生成 Go 代码**

Run: `cd 80-PROJECTS/multi-agent-discuss && go install google.golang.org/protobuf/cmd/protoc-gen-go@latest && go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest && export PATH="$PATH:$(go env GOPATH)/bin" && protoc --go_out=. --go-grpc_out=. pkg/proto/agent.proto`

- [ ] **Step 4: 提交**

```bash
cd 80-PROJECTS/multi-agent-discuss
git add go.mod pkg/proto/agent.proto
git commit -m "feat: init project and add proto definitions"
```

---

## Task 2: Agent Core + Discovery

**Files:**
- Create: `80-PROJECTS/multi-agent-discuss/pkg/core/agent.go`
- Create: `80-PROJECTS/multi-agent-discuss/pkg/discovery/mdns.go`

- [ ] **Step 1: 写 core/agent.go**

```go
package core

import (
    "sync"
    "github.com/openclaw/multi-agent-discuss/pkg/proto"
)

type Agent struct {
    ID           string
    Name         string
    Port         int
    Capabilities []proto.Capability
    peers        map[string]*PeerConnection
    mu           sync.RWMutex
}

type PeerConnection struct {
    Info   *proto.AgentInfo
    Stream proto.AgentService_ConnectClient
}

func NewAgent(id, name string, port int, caps []proto.Capability) *Agent {
    return &Agent{
        ID:           id,
        Name:         name,
        Port:         port,
        Capabilities: caps,
        peers:        make(map[string]*PeerConnection),
    }
}

func (a *Agent) AddPeer(peer *PeerConnection) {
    a.mu.Lock()
    defer a.mu.Unlock()
    a.peers[peer.Info.Id] = peer
}

func (a *Agent) RemovePeer(id string) {
    a.mu.Lock()
    defer a.mu.Unlock()
    delete(a.peers, id)
}

func (a *Agent) GetPeers() map[string]*PeerConnection {
    a.mu.RLock()
    defer a.mu.RUnlock()
    return a.peers
}
```

- [ ] **Step 2: 写 discovery/mdns.go**

```go
package discovery

import (
    "context"
    "fmt"
    "log"
    "time"

    "github.com/openclaw/multi-agent-discuss/pkg/proto"
    "github.com/hashicorp/mdns"
)

type Discovery struct {
    agentID   string
    port      int
    peers     map[string]*proto.AgentInfo
    onDiscover func(*proto.AgentInfo)
    onRemove   func(string)
    zone      *mdns.ZoneMDNS
    server    *mdns.Server
}

func NewDiscovery(agentID string, port int) *Discovery {
    return &Discovery{
        agentID: agentID,
        port:    port,
        peers:   make(map[string]*proto.AgentInfo),
    }
}

func (d *Discovery) Start(ctx context.Context, info *proto.AgentInfo, onDiscover func(*proto.AgentInfo), onRemove func(string)) error {
    d.onDiscover = onDiscover
    d.onRemove = onRemove

    // Register service
    d.zone = &mdns.ZoneMDNS{
        ServiceRecord: &mdns.ServiceRecord{
            Name:    fmt.Sprintf("agent-%s-%d", d.agentID, d.port),
            Type:    "_grpc._tcp",
            Domain:   "local.",
            Port:     d.port,
        },
    }

    server, err := mdns.Register(d.zone)
    if err != nil {
        return fmt.Errorf("mdns register: %w", err)
    }
    d.server = server

    // Start discovery
    go d.scan(ctx)
    return nil
}

func (d *Discovery) scan(ctx context.Context) {
    for {
        select {
        case <-ctx.Done():
            return
        default:
            results := make([]*mdns.ServiceEntry, 0)
            ch := make(chan *mdns.ServiceEntry, 10)
            go func() {
                for entry := range ch {
                    results = append(results, entry)
                }
            }()

            params := &mdns.QueryParam{
                Service: "_grpc._tcp.local.",
                Domain:  "local.",
                Timeout: 5 * time.Second,
                Entries: ch,
            }

            err := mdns.Query(params)
            if err != nil {
                log.Printf("mdns query error: %v", err)
            }

            for _, entry := range results {
                // Parse port from instance name (agent-<id>-<port>)
                // Add to peers if not self
            }
    }
}

func (d *Discovery) Stop() {
    if d.server != nil {
        d.server.Shutdown()
    }
}
```

- [ ] **Step 3: 提交**

```bash
cd 80-PROJECTS/multi-agent-discuss
git add pkg/core/agent.go pkg/discovery/mdns.go
git commit -m "feat: add Agent Core and mDNS discovery"
```

---

## Task 3: gRPC Transport (Server + Client)

**Files:**
- Create: `80-PROJECTS/multi-agent-discuss/pkg/transport/server.go`
- Create: `80-PROJECTS/multi-agent-discuss/pkg/transport/client.go`

- [ ] **Step 1: 写 transport/server.go**

```go
package transport

import (
    "context"
    "io"
    "log"
    "net"

    "github.com/openclaw/multi-agent-discuss/pkg/proto"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials"
)

type Server struct {
    proto.UnimplementedAgentServiceServer
    port     int
    agent    *core.Agent
    incoming chan *proto.AgentMessage
}

func NewServer(port int, agent *core.Agent) *Server {
    return &Server{
        port:     port,
        agent:    agent,
        incoming: make(chan *proto.AgentMessage, 100),
    }
}

func (s *Server) SendMessage(stream proto.AgentService_SendMessageServer) error {
    for {
        msg, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return err
        }
        s.incoming <- msg
    }
}

func (s *Server) Connect(req *proto.AgentInfo, stream proto.AgentService_ConnectServer) error {
    // Add peer
    peer := &core.PeerConnection{
        Info:   req,
        Stream: stream,
    }
    s.agent.AddPeer(peer)
    defer s.agent.RemovePeer(req.Id)

    // Receive messages
    for {
        msg, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return err
        }
        s.incoming <- msg
    }
}

func (s *Server) Start(ctx context.Context, tlsCert, tlsKey string) error {
    lis, err := net.Listen("tcp", fmt.Sprintf(":%d", s.port))
    if err != nil {
        return err
    }

    var opts []grpc.ServerOption
    if tlsCert != "" && tlsKey != "" {
        creds, err := credentials.NewServerTLSFromFile(tlsCert, tlsKey)
        if err != nil {
            return err
        }
        opts = append(opts, grpc.Creds(creds))
    }

    gs := grpc.NewServer(opts...)
    proto.RegisterAgentServiceServer(gs, s)

    go func() {
        <-ctx.Done()
        gs.GracefulStop()
    }()

    return gs.Serve(lis)
}

func (s *Server) Incoming() <-chan *proto.AgentMessage {
    return s.incoming
}
```

- [ ] **Step 2: 写 transport/client.go**

```go
package transport

import (
    "context"
    "fmt"
    "io"

    "github.com/openclaw/multi-agent-discuss/pkg/core"
    "github.com/openclaw/multi-agent-discuss/pkg/proto"
    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials"
)

type Client struct {
    agent *core.Agent
}

func NewClient(agent *core.Agent) *Client {
    return &Client{agent: agent}
}

func (c *Client) Connect(ctx context.Context, addr string, info *proto.AgentInfo, tlsCreds credentials.TransportCredentials) (*grpc.ClientConn, error) {
    var opts []grpc.DialOption
    if tlsCreds != nil {
        opts = append(opts, grpc.WithTransportCredentials(tlsCreds))
    } else {
        opts = append(opts, grpc.WithInsecure())
    }

    conn, err := grpc.DialContext(ctx, addr, opts...)
    if err != nil {
        return nil, fmt.Errorf("dial: %w", err)
    }

    client := proto.NewAgentServiceClient(conn)
    stream, err := client.Connect(ctx, info)
    if err != nil {
        conn.Close()
        return nil, fmt.Errorf("connect: %w", err)
    }

    // Store connection
    peer := &core.PeerConnection{
        Info:   info,
        Stream: stream,
    }
    c.agent.AddPeer(peer)

    return conn, nil
}

func (c *Client) SendMessage(ctx context.Context, addr string, msg *proto.AgentMessage, tlsCreds credentials.TransportCredentials) error {
    var opts []grpc.DialOption
    if tlsCreds != nil {
        opts = append(opts, grpc.WithTransportCredentials(tlsCreds))
    } else {
        opts = append(opts, grpc.WithInsecure())
    }

    conn, err := grpc.DialContext(ctx, addr, opts...)
    if err != nil {
        return err
    }
    defer conn.Close()

    client := proto.NewAgentServiceClient(conn)
    stream, err := client.SendMessage(ctx)
    if err != nil {
        return err
    }

    if err := stream.Send(msg); err != nil {
        return err
    }
    return stream.CloseSend()
}
```

- [ ] **Step 3: 提交**

```bash
cd 80-PROJECTS/multi-agent-discuss
git add pkg/transport/server.go pkg/transport/client.go
git commit -m "feat: add gRPC transport server and client"
```

---

## Task 4: Dispatcher (决策调度器)

**Files:**
- Create: `80-PROJECTS/multi-agent-discuss/pkg/dispatcher/dispatcher.go`

- [ ] **Step 1: 写 dispatcher/dispatcher.go**

```go
package dispatcher

import (
    "github.com/openclaw/multi-agent-discuss/pkg/core"
    "github.com/openclaw/multi-agent-discuss/pkg/proto"
)

type State int

const (
    StateIdle State = iota
    StateProcessing
    StateNeedHelp
    StateWaiting
)

type Dispatcher struct {
    agent     *core.Agent
    state     State
    onInvite  func(*proto.AgentInfo) error
}

func NewDispatcher(agent *core.Agent, onInvite func(*proto.AgentInfo) error) *Dispatcher {
    return &Dispatcher{
        agent:    agent,
        state:    StateIdle,
        onInvite: onInvite,
    }
}

func (d *Dispatcher) HandleMessage(msg *proto.AgentMessage) {
    switch msg.Type {
    case proto.MessageType_TASK:
        d.handleTask(msg)
    case proto.MessageType_INVITE:
        d.handleInvite(msg)
    case proto.MessageType_RESPONSE:
        d.handleResponse(msg)
    }
}

func (d *Dispatcher) handleTask(msg *proto.AgentMessage) {
    if d.state != StateIdle {
        return
    }
    d.state = StateProcessing
    // Execute task, then decide if help needed
}

func (d *Dispatcher) ShouldInvite(peers map[string]*core.PeerConnection, reason string) bool {
    if reason == "error" || reason == "complexity" || reason == "decision" || reason == "share" {
        return len(peers) > 0
    }
    return false
}

func (d *Dispatcher) handleInvite(msg *proto.AgentMessage) {
    // Check if we should join
    d.state = StateProcessing
}

func (d *Dispatcher) handleResponse(msg *proto.AgentMessage) {
    d.state = StateIdle
}
```

- [ ] **Step 2: 提交**

```bash
cd 80-PROJECTS/multi-agent-discuss
git add pkg/dispatcher/dispatcher.go
git commit -m "feat: add Dispatcher with state machine"
```

---

## Task 5: Executor (任务执行器)

**Files:**
- Create: `80-PROJECTS/multi-agent-discuss/pkg/executor/executor.go`

- [ ] **Step 1: 写 executor/executor.go**

```go
package executor

import (
    "context"
    "encoding/json"
    "fmt"
    "os/exec"
)

type TaskType string

const (
    TaskRead    TaskType = "read"
    TaskWrite   TaskType = "write"
    TaskExecute TaskType = "execute"
)

type Task struct {
    Type TaskType
    Path string
    Content string
    Command string
}

type Result struct {
    Success bool
    Output  string
    Error   string
}

type Executor struct{}

func NewExecutor() *Executor {
    return &Executor{}
}

func (e *Executor) Execute(ctx context.Context, task *Task) *Result {
    switch task.Type {
    case TaskRead:
        return e.readFile(task.Path)
    case TaskWrite:
        return e.writeFile(task.Path, task.Content)
    case TaskExecute:
        return e.execute(task.Command)
    default:
        return &Result{Success: false, Error: "unknown task type"}
    }
}

func (e *Executor) readFile(path string) *Result {
    // Implementation using os.ReadFile
    return &Result{Success: true, Output: "file content"}
}

func (e *Executor) writeFile(path, content string) *Result {
    // Implementation using os.WriteFile
    return &Result{Success: true}
}

func (e *Executor) execute(cmd string) *Result {
    parts := parseCommand(cmd)
    c := exec.Command(parts[0], parts[1:]...)
    out, err := c.CombinedOutput()
    if err != nil {
        return &Result{Success: false, Error: err.Error(), Output: string(out)}
    }
    return &Result{Success: true, Output: string(out)}
}

func parseCommand(cmd string) []string {
    // Simple command parser
    return []string{"sh", "-c", cmd}
}
```

- [ ] **Step 2: 提交**

```bash
cd 80-PROJECTS/multi-agent-discuss
git add pkg/executor/executor.go
git commit -m "feat: add Executor for task execution"
```

---

## Task 6: Group (群组管理)

**Files:**
- Create: `80-PROJECTS/multi-agent-discuss/pkg/group/group.go`

- [ ] **Step 1: 写 group/group.go**

```go
package group

import (
    "sync"
    "time"

    "github.com/openclaw/multi-agent-discuss/pkg/proto"
)

type Group struct {
    ID        string
    Members   map[string]*proto.AgentInfo
    History   []*proto.AgentMessage
    CreatedAt time.Time
    mu        sync.RWMutex
}

type Manager struct {
    groups map[string]*Group
    mu     sync.RWMutex
}

func NewManager() *Manager {
    return &Manager{
        groups: make(map[string]*Group),
    }
}

func (m *Manager) CreateGroup(id string) *Group {
    m.mu.Lock()
    defer m.mu.Unlock()
    g := &Group{
        ID:        id,
        Members:   make(map[string]*proto.AgentInfo),
        History:   make([]*proto.AgentMessage, 0),
        CreatedAt: time.Now(),
    }
    m.groups[id] = g
    return g
}

func (m *Manager) GetGroup(id string) *Group {
    m.mu.RLock()
    defer m.mu.RUnlock()
    return m.groups[id]
}

func (m *Manager) AddToGroup(groupID string, info *proto.AgentInfo) {
    g := m.GetGroup(groupID)
    if g == nil {
        return
    }
    g.mu.Lock()
    defer g.mu.Unlock()
    g.Members[info.Id] = info
}

func (m *Manager) RemoveFromGroup(groupID, agentID string) {
    g := m.GetGroup(groupID)
    if g == nil {
        return
    }
    g.mu.Lock()
    defer g.mu.Unlock()
    delete(g.Members, agentID)
}

func (m *Manager) DissolveGroup(groupID string) {
    m.mu.Lock()
    defer m.mu.Unlock()
    delete(m.groups, groupID)
}
```

- [ ] **Step 2: 提交**

```bash
cd 80-PROJECTS/multi-agent-discuss
git add pkg/group/group.go
git commit -m "feat: add Group management"
```

---

## Task 7: CLI 入口

**Files:**
- Create: `80-PROJECTS/multi-agent-discuss/cmd/agent/main.go`
- Create: `80-PROJECTS/multi-agent-discuss/cmd/cli/main.go`

- [ ] **Step 1: 写 cmd/agent/main.go**

```go
package main

import (
    "context"
    "flag"
    "log"

    "github.com/openclaw/multi-agent-discuss/pkg/core"
    "github.com/openclaw/multi-agent-discuss/pkg/discovery"
    "github.com/openclaw/multi-agent-discuss/pkg/proto"
    "github.com/openclaw/multi-agent-discuss/pkg/dispatcher"
    "github.com/openclaw/multi-agent-discuss/pkg/executor"
    "github.com/openclaw/multi-agent-discuss/pkg/group"
    "github.com/openclaw/multi-agent-discuss/pkg/transport"
)

func main() {
    id := flag.String("id", "agent-1", "Agent ID")
    name := flag.String("name", "Agent One", "Agent name")
    port := flag.Int("port", 50051, "gRPC port")
    flag.Parse()

    ctx := context.Background()

    // Create agent
    agent := core.NewAgent(*id, *name, *port, []proto.Capability{
        {Name: "read", Description: "Read files"},
        {Name: "write", Description: "Write files"},
        {Name: "execute", Description: "Execute commands"},
    })

    // Create components
    exec := executor.NewExecutor()
    groupMgr := group.NewManager()
    disp := dispatcher.NewDispatcher(agent, func(info *proto.AgentInfo) error {
        // Handle invite
        return nil
    })
    disc := discovery.NewDiscovery(*id, *port)
    srv := transport.NewServer(*port, agent)

    // Start server
    go func() {
        if err := srv.Start(ctx, "", ""); err != nil {
            log.Fatalf("server error: %v", err)
        }
    }()

    // Start discovery
    info := &proto.AgentInfo{
        Id:           *id,
        Name:         *name,
        Port:         int32(*port),
        Capabilities: agent.Capabilities,
    }
    if err := disc.Start(ctx, info, agent.AddPeer, agent.RemovePeer); err != nil {
        log.Fatalf("discovery error: %v", err)
    }

    // Message loop
    for msg := range srv.Incoming() {
        disp.HandleMessage(msg)
    }
}
```

- [ ] **Step 2: 写 cmd/cli/main.go**

```go
package main

import (
    "context"
    "flag"
    "fmt"
    "log"

    "github.com/openclaw/multi-agent-discuss/pkg/transport"
    "github.com/openclaw/multi-agent-discuss/pkg/proto"
)

func main() {
    addr := flag.String("addr", "localhost:50051", "Agent address")
    flag.Parse()

    ctx := context.Background()
    msg := &proto.AgentMessage{
        Type: proto.MessageType_TEXT,
        Content: []byte("Hello from CLI"),
    }

    client := transport.NewClient(nil)
    if err := client.SendMessage(ctx, *addr, msg, nil); err != nil {
        log.Fatalf("send error: %v", err)
    }

    fmt.Println("Message sent")
}
```

- [ ] **Step 3: 提交**

```bash
cd 80-PROJECTS/multi-agent-discuss
git add cmd/agent/main.go cmd/cli/main.go
git commit -m "feat: add CLI entry points"
```

---

## Task 8: 集成测试

**Files:**
- Create: `80-PROJECTS/multi-agent-discuss/pkg/dispatcher/dispatcher_test.go`
- Create: `80-PROJECTS/multi-agent-discuss/pkg/executor/executor_test.go`
- Create: `80-PROJECTS/multi-agent-discuss/pkg/group/group_test.go`

- [ ] **Step 1: 写 dispatcher_test.go**

```go
package dispatcher

import (
    "testing"
)

func TestDispatcherStateTransitions(t *testing.T) {
    d := NewDispatcher(nil, nil)

    if d.state != StateIdle {
        t.Errorf("expected StateIdle, got %v", d.state)
    }
}
```

- [ ] **Step 2: 写 executor_test.go**

```go
package executor

import (
    "context"
    "testing"
)

func TestExecutorRead(t *testing.T) {
    e := NewExecutor()
    result := e.Execute(context.Background(), &Task{
        Type: TaskRead,
        Path: "/etc/hostname",
    })
    if !result.Success {
        t.Errorf("expected success, got error: %s", result.Error)
    }
}
```

- [ ] **Step 3: 写 group_test.go**

```go
package group

import (
    "testing"
)

func TestGroupLifecycle(t *testing.T) {
    m := NewManager()
    g := m.CreateGroup("test-group")

    if g.ID != "test-group" {
        t.Errorf("expected group ID 'test-group', got '%s'", g.ID)
    }

    if len(g.Members) != 0 {
        t.Errorf("expected 0 members, got %d", len(g.Members))
    }

    m.DissolveGroup("test-group")
    if m.GetGroup("test-group") != nil {
        t.Errorf("expected group to be dissolved")
    }
}
```

- [ ] **Step 4: 运行测试**

Run: `cd 80-PROJECTS/multi-agent-discuss && go test ./...`

- [ ] **Step 5: 提交**

```bash
cd 80-PROJECTS/multi-agent-discuss
git add *_test.go
git commit -m "test: add unit tests"
```

---

## 执行顺序

1. Task 1: 项目初始化 + Proto 定义
2. Task 2: Agent Core + Discovery
3. Task 3: gRPC Transport
4. Task 4: Dispatcher
5. Task 5: Executor
6. Task 6: Group
7. Task 7: CLI 入口
8. Task 8: 集成测试

package main

import (
	"context"
	"flag"
	"fmt"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/openclaw/multi-agent-discuss/pkg/core"
	"github.com/openclaw/multi-agent-discuss/pkg/discovery"
	"github.com/openclaw/multi-agent-discuss/pkg/dispatcher"
	"github.com/openclaw/multi-agent-discuss/pkg/executor"
	"github.com/openclaw/multi-agent-discuss/pkg/group"
	"github.com/openclaw/multi-agent-discuss/pkg/ipc"
	"github.com/openclaw/multi-agent-discuss/pkg/proto"
	"github.com/openclaw/multi-agent-discuss/pkg/transport"
)

// executorAdapter wraps executor.Executor to satisfy dispatcher.TaskExecutor
type executorAdapter struct {
	exec *executor.Executor
}

func (a *executorAdapter) CanExecute(task *dispatcher.Task) bool {
	return a.exec.CanHandle(task.Type)
}

func (a *executorAdapter) Execute(task *dispatcher.Task) (*dispatcher.TaskResult, error) {
	execTask := &executor.Task{
		ID:      task.ID,
		Type:    task.Type,
		Payload: task.Payload,
	}
	result, err := a.exec.ExecuteTask(execTask)
	if err != nil {
		return nil, err
	}
	return &dispatcher.TaskResult{
		TaskID:     result.TaskID,
		Success:    result.Success,
		Output:     result.Output,
		Error:      result.Error,
		ExecutedBy: result.ExecutedBy,
	}, nil
}

// CLI context holds all components wired together
type CLIContext struct {
	agent     *core.Agent
	disc      *discovery.Discovery
	disp      *dispatcher.Dispatcher
	exec      *executor.Executor
	grpMgr    *group.GroupManager
	server    *transport.Server
	info      *proto.AgentInfo
	ctx       context.Context
	cancel    context.CancelFunc
}

var ctx *CLIContext

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	cmd := os.Args[1]

	switch cmd {
	case "start":
		handleStart()
	case "run":
		handleRun()
	case "peers":
		handlePeers()
	case "send":
		handleSend()
	case "groups":
		handleGroups()
	case "group":
		handleGroup()
	case "status":
		handleStatus()
	case "help":
		printUsage()
	default:
		fmt.Printf("Unknown command: %s\n", cmd)
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Print(`agent - Multi-Agent Discuss CLI

Usage:
  agent start --name <name> --port <port>
                          Start agent with name and port, begin discovery (stateless)
  agent run --name <name> --port <port>
                          Start agent in persistent running mode (with IPC server)
  agent peers              Show discovered peers with capabilities
  agent send <peer-id> <message>
                          Send TEXT message to specific peer
  agent groups             Show all groups agent is in
  agent status             Show agent status via IPC (for running agents)
  agent help               Show this help message

IPC Commands (for running agents via 'agent run'):
  agent peers              List discovered peers
  agent send <id> <msg>   Send message to peer
  agent groups             List groups

Examples:
  agent start --name Alice --port 9001
  agent run --name Alice --port 9001
  agent peers
  agent send peer-123 "Hello peer"
  agent groups
`)
}

func handleStart() {
	fs := flag.NewFlagSet("start", flag.ContinueOnError)
	name := fs.String("name", "Agent", "Agent name")
	port := fs.Int("port", 9000, "Port for gRPC transport server")
	fs.Parse(os.Args[2:])

	ctx = &CLIContext{
		agent: core.NewAgent("", *name, *port, []*proto.Capability{
			{Name: "text", Description: "Text messaging capability"},
			{Name: "task", Description: "Task execution capability"},
		}),
	}

	// Generate agent ID
	ctx.agent.ID = fmt.Sprintf("agent-%d", time.Now().UnixNano())

	// Create AgentInfo for discovery
	ctx.info = &proto.AgentInfo{
		Id:   ctx.agent.ID,
		Name: ctx.agent.Name,
		Capabilities: []*proto.Capability{
			{Name: "text", Description: "Text messaging capability"},
			{Name: "task", Description: "Task execution capability"},
		},
		Port: int32(*port),
	}

	// Initialize components
	ctx.disc = discovery.NewDiscovery(ctx.agent.ID, *port)
	ctx.disp = dispatcher.NewDispatcher(ctx.agent.ID, func() []*proto.AgentInfo {
		return ctx.disc.GetPeers()
	})
	ctx.exec = executor.NewExecutor(ctx.agent.ID)
	ctx.grpMgr = group.NewGroupManager(ctx.agent.ID)

	// Setup dispatcher with executor
	ctx.disp.SetDecisionCallback(func(decision *dispatcher.Decision) {
		fmt.Printf("[dispatcher] decision: %s for message from %s\n",
			decision.Type.String(), decision.Message.SenderId)
	})

	// Setup group event handler
	ctx.grpMgr.SetEventHandler(func(event group.GroupEvent, groupID string, agentID string) {
		fmt.Printf("[group] event: %s on group %s by %s\n",
			event.String(), groupID, agentID)
	})

	// Create cancellable context
	ctx.ctx, ctx.cancel = context.WithCancel(context.Background())

	// Setup signal handling for graceful shutdown
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)

	// Start mDNS discovery
	fmt.Printf("[discovery] Starting mDNS discovery on agent %s (port %d)\n", ctx.agent.Name, *port)
	if err := ctx.disc.Start(ctx.ctx, ctx.info, onPeerDiscover, onPeerRemove); err != nil {
		fmt.Printf("[discovery] Failed to start: %v\n", err)
		os.Exit(1)
	}

	// Start gRPC transport server
	fmt.Printf("[transport] Starting gRPC server on port %d\n", *port)
	server, err := transport.StartServer(*port, &serverHandler{ctx: ctx})
	if err != nil {
		fmt.Printf("[transport] Failed to start server: %v\n", err)
		os.Exit(1)
	}
	ctx.server = server

	fmt.Printf("[agent] Started successfully!\n")
	fmt.Printf("  Agent ID:   %s\n", ctx.agent.ID)
	fmt.Printf("  Name:       %s\n", ctx.agent.Name)
	fmt.Printf("  Port:       %d\n", *port)
	fmt.Printf("  Transport:  tcp:%d\n", *port)
	fmt.Printf("\nAgent is running. Press Ctrl+C to shutdown.\n")

	// Block until signal received
	<-sigCh

	fmt.Println("\n[agent] Shutting down...")
	ctx.cancel()

	if ctx.server != nil {
		ctx.server.Close()
	}
	ctx.disc.Stop()

	fmt.Println("[agent] Shutdown complete")
}

func onPeerDiscover(peer *proto.AgentInfo) {
	fmt.Printf("[discovery] Peer discovered: %s (%s) on port %d\n",
		peer.Name, peer.Id, peer.Port)
}

func onPeerRemove(peerID string) {
	fmt.Printf("[discovery] Peer removed: %s\n", peerID)
}

// serverHandler implements transport.MessageHandler
type serverHandler struct {
	ctx *CLIContext
}

func (h *serverHandler) HandleMessage(msg *proto.AgentMessage, reply func(*proto.AgentMessage)) {
	// Route to dispatcher with adapter
	adapter := &executorAdapter{exec: h.ctx.exec}
	h.ctx.disp.HandleMessage(msg, adapter, reply)
}

func handlePeers() {
	// Check if we have a local context (start mode)
	if ctx != nil && ctx.disc != nil {
		peers := ctx.disc.GetPeers()
		if len(peers) == 0 {
			fmt.Println("No peers discovered yet.")
			return
		}

		fmt.Printf("Discovered %d peer(s):\n\n", len(peers))
		for _, peer := range peers {
			fmt.Printf("  ID:       %s\n", peer.Id)
			fmt.Printf("  Name:     %s\n", peer.Name)
			fmt.Printf("  Port:     %d\n", peer.Port)
			if len(peer.Capabilities) > 0 {
				fmt.Printf("  Capabilities:\n")
				for _, cap := range peer.Capabilities {
					fmt.Printf("    - %s: %s\n", cap.Name, cap.Description)
				}
			}
			fmt.Println()
		}
		return
	}

	// Try IPC client mode (run mode)
	fs := flag.NewFlagSet("peers", flag.ContinueOnError)
	port := fs.Int("port", 0, "Agent port (required for remote)")
	fs.Parse(os.Args[2:])

	if *port == 0 {
		fmt.Println("Agent not started. Run 'agent start' first, or use 'agent peers --port <port>'")
		os.Exit(1)
	}

	client := ipc.NewClient(*port)
	peers, err := client.Peers()
	if err != nil {
		fmt.Printf("Failed to get peers: %v\n", err)
		os.Exit(1)
	}

	if len(peers) == 0 {
		fmt.Println("No peers discovered yet.")
		return
	}

	fmt.Printf("Discovered %d peer(s):\n\n", len(peers))
	for _, peer := range peers {
		fmt.Printf("  ID:       %s\n", peer["id"])
		fmt.Printf("  Name:     %s\n", peer["name"])
		fmt.Printf("  Port:     %d\n", int(peer["port"].(float64)))
		fmt.Println()
	}
}

func handleSend() {
	if len(os.Args) < 4 {
		fmt.Println("Usage: agent send <peer-id> <message>")
		os.Exit(1)
	}

	if ctx == nil || ctx.server == nil {
		fmt.Println("Agent not started. Run 'agent start' first.")
		os.Exit(1)
	}

	peerID := os.Args[2]
	message := os.Args[3]

	// Find peer
	peerConn, ok := ctx.agent.GetPeer(peerID)
	if !ok {
		// Try to find in discovery
		peers := ctx.disc.GetPeers()
		var peerInfo *proto.AgentInfo
		for _, p := range peers {
			if p.Id == peerID {
				peerInfo = p
				break
			}
		}
		if peerInfo == nil {
			fmt.Printf("Peer not found: %s\n", peerID)
			os.Exit(1)
		}
		peerConn = &core.PeerConnection{
			Info: peerInfo,
			Port: int(peerInfo.Port),
		}
	}

	// Connect to peer and send message
	client, err := transport.DialAgent(fmt.Sprintf("localhost:%d", peerConn.Port), ctx.info)
	if err != nil {
		fmt.Printf("Failed to connect to peer: %v\n", err)
		os.Exit(1)
	}
	defer client.Close()

	msg := &proto.AgentMessage{
		Id:        fmt.Sprintf("msg-%d", time.Now().UnixNano()),
		Timestamp: time.Now().Unix(),
		SenderId:  ctx.agent.ID,
		Type:      proto.MessageType_TEXT,
		Payload:   []byte(message),
	}

	if err := client.Send(msg); err != nil {
		fmt.Printf("Failed to send message: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("[send] Message sent to %s: %s\n", peerID, message)

	// Wait for response
	resp, err := client.Recv()
	if err != nil {
		fmt.Printf("[send] No response received: %v\n", err)
	} else {
		fmt.Printf("[send] Response from %s: %s\n", resp.SenderId, string(resp.Payload))
	}
}

func handleGroup() {
	if len(os.Args) < 3 {
		fmt.Println("Usage: agent group <create|invite|join|leave> [args]")
		os.Exit(1)
	}

	if ctx == nil || ctx.grpMgr == nil {
		fmt.Println("Agent not started. Run 'agent start' first.")
		os.Exit(1)
	}

	subcmd := os.Args[2]

	switch subcmd {
	case "create":
		handleGroupCreate()
	case "invite":
		handleGroupInvite()
	case "join":
		handleGroupJoin()
	case "leave":
		handleGroupLeave()
	default:
		fmt.Printf("Unknown group command: %s\n", subcmd)
		fmt.Println("Usage: agent group <create|invite|join|leave>")
		os.Exit(1)
	}
}

func handleGroupCreate() {
	if len(os.Args) < 4 {
		fmt.Println("Usage: agent group create <name>")
		os.Exit(1)
	}

	name := os.Args[3]
	g, err := ctx.grpMgr.CreateGroup(name)
	if err != nil {
		fmt.Printf("Failed to create group: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("[group] Created group: %s (ID: %s)\n", g.Name, g.ID)
	fmt.Printf("[group] You are the owner with %d member(s)\n", g.MemberCount())
}

func handleGroupInvite() {
	if len(os.Args) < 5 {
		fmt.Println("Usage: agent group invite <group-id> <peer-id>")
		os.Exit(1)
	}

	groupID := os.Args[3]
	peerID := os.Args[4]

	invite := ctx.grpMgr.InviteToGroup(groupID, peerID)
	if invite == nil {
		fmt.Printf("Failed to invite: you may not be the owner of group %s\n", groupID)
		os.Exit(1)
	}

	fmt.Printf("[group] Invite created:\n")
	fmt.Printf("  Group:     %s\n", invite.GroupName)
	fmt.Printf("  Group ID:  %s\n", invite.GroupID)
	fmt.Printf("  To:        %s\n", invite.ToAgentID)
	fmt.Printf("\nInvite (send this to peer manually or via peer communication)\n")
}

func handleGroupJoin() {
	if len(os.Args) < 4 {
		fmt.Println("Usage: agent group join <group-id>")
		os.Exit(1)
	}

	groupID := os.Args[3]

	// Get pending invites to find matching invite
	invites := ctx.grpMgr.GetPendingInvites()
	var invite *group.Invite
	for _, inv := range invites {
		if inv.GroupID == groupID {
			invite = inv
			break
		}
	}

	if invite == nil {
		// Create a synthetic invite for joining (normally would come from peer)
		invite = &group.Invite{
			FromAgentID: "unknown",
			ToAgentID:   ctx.agent.ID,
			GroupID:     groupID,
			GroupName:   "Group " + groupID,
			Timestamp:   time.Now(),
		}
	}

	if err := ctx.grpMgr.JoinGroup(invite); err != nil {
		fmt.Printf("Failed to join group: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("[group] Joined group: %s\n", groupID)
}

func handleGroupLeave() {
	if len(os.Args) < 4 {
		fmt.Println("Usage: agent group leave <group-id>")
		os.Exit(1)
	}

	groupID := os.Args[3]

	if err := ctx.grpMgr.LeaveGroup(groupID); err != nil {
		fmt.Printf("Failed to leave group: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("[group] Left group: %s\n", groupID)
}

func handleGroups() {
	// Check if we have a local context (start mode)
	if ctx != nil && ctx.grpMgr != nil {
		groups := ctx.grpMgr.GetGroups()
		if len(groups) == 0 {
			fmt.Println("Not a member of any groups.")
			return
		}

		fmt.Printf("Member of %d group(s):\n\n", len(groups))
		for _, g := range groups {
			isOwner := g.OwnerID == ctx.agent.ID
			role := "member"
			if isOwner {
				role = "owner"
			}

			fmt.Printf("  Group ID:   %s\n", g.ID)
			fmt.Printf("  Name:       %s\n", g.Name)
			fmt.Printf("  Role:       %s\n", role)
			fmt.Printf("  Members:    %d\n", g.MemberCount())
			fmt.Printf("  Created:    %s\n", g.Created.Format(time.RFC1123))
			fmt.Println()
		}
		return
	}

	// Try IPC client mode (run mode)
	fs := flag.NewFlagSet("groups", flag.ContinueOnError)
	port := fs.Int("port", 0, "Agent port (required for remote)")
	fs.Parse(os.Args[2:])

	if *port == 0 {
		fmt.Println("Agent not started. Run 'agent start' first, or use 'agent groups --port <port>'")
		os.Exit(1)
	}

	client := ipc.NewClient(*port)
	groups, err := client.Groups()
	if err != nil {
		fmt.Printf("Failed to get groups: %v\n", err)
		os.Exit(1)
	}

	if len(groups) == 0 {
		fmt.Println("Not a member of any groups.")
		return
	}

	fmt.Printf("Member of %d group(s):\n\n", len(groups))
	for _, g := range groups {
		fmt.Printf("  Group ID:   %s\n", g["id"])
		fmt.Printf("  Name:       %s\n", g["name"])
		fmt.Println()
	}
}

// handleRun starts the agent in persistent mode with IPC server
func handleRun() {
	fs := flag.NewFlagSet("run", flag.ContinueOnError)
	name := fs.String("name", "Agent", "Agent name")
	port := fs.Int("port", 9000, "Port for gRPC transport server")
	fs.Parse(os.Args[2:])

	// Initialize agent
	agent := core.NewAgent("", *name, *port, []*proto.Capability{
		{Name: "text", Description: "Text messaging capability"},
		{Name: "task", Description: "Task execution capability"},
	})
	agent.ID = fmt.Sprintf("agent-%d", time.Now().UnixNano())

	info := &proto.AgentInfo{
		Id:   agent.ID,
		Name: agent.Name,
		Capabilities: []*proto.Capability{
			{Name: "text", Description: "Text messaging capability"},
			{Name: "task", Description: "Task execution capability"},
		},
		Port: int32(*port),
	}

	// Create components
	disc := discovery.NewDiscovery(agent.ID, *port)
	disp := dispatcher.NewDispatcher(agent.ID, func() []*proto.AgentInfo {
		return disc.GetPeers()
	})
	exec := executor.NewExecutor(agent.ID)
	grpMgr := group.NewGroupManager(agent.ID)

	// Create cancellable context
	runCtx, cancel := context.WithCancel(context.Background())

	// Setup dispatcher with executor
	disp.SetDecisionCallback(func(decision *dispatcher.Decision) {
		fmt.Printf("[dispatcher] decision: %s for message from %s\n",
			decision.Type.String(), decision.Message.SenderId)
	})

	// Setup group event handler
	grpMgr.SetEventHandler(func(event group.GroupEvent, groupID string, agentID string) {
		fmt.Printf("[group] event: %s on group %s by %s\n",
			event.String(), groupID, agentID)
	})

	// Setup signal handling for graceful shutdown
	sigCh := make(chan os.Signal, 1)
	signal.Notify(sigCh, os.Interrupt, syscall.SIGTERM)

	// Start mDNS discovery
	fmt.Printf("[discovery] Starting mDNS discovery on agent %s (port %d)\n", agent.Name, *port)
	if err := disc.Start(runCtx, info, func(peer *proto.AgentInfo) {
		fmt.Printf("[discovery] Peer discovered: %s (%s) on port %d\n",
			peer.Name, peer.Id, peer.Port)
	}, func(peerID string) {
		fmt.Printf("[discovery] Peer removed: %s\n", peerID)
	}); err != nil {
		fmt.Printf("[discovery] Failed to start: %v\n", err)
		os.Exit(1)
	}

	// Start gRPC transport server
	fmt.Printf("[transport] Starting gRPC server on port %d\n", *port)
	server, err := transport.StartServer(*port, &persistentServerHandler{agent: agent, disp: disp, exec: exec})
	if err != nil {
		fmt.Printf("[transport] Failed to start server: %v\n", err)
		os.Exit(1)
	}

	// Start IPC server
	ipcSrv := ipc.NewServer(*port, agent, disc, grpMgr)
	fmt.Printf("[ipc] Starting IPC server on port %d (tcp:%d)\n", *port+10000, *port+10000)
	if err := ipcSrv.Start(); err != nil {
		fmt.Printf("[ipc] Failed to start IPC server: %v\n", err)
		os.Exit(1)
	}

	// Write PID file
	pid := os.Getpid()
	pidFile := fmt.Sprintf("agent-%s.pid", agent.ID)
	if err := os.WriteFile(pidFile, []byte(fmt.Sprintf("%d", pid)), 0644); err != nil {
		fmt.Printf("[agent] Warning: failed to write PID file: %v\n", err)
	}

	fmt.Printf("[agent] Started successfully in persistent mode!\n")
	fmt.Printf("  Agent ID:   %s\n", agent.ID)
	fmt.Printf("  Name:       %s\n", agent.Name)
	fmt.Printf("  Port:       %d\n", *port)
	fmt.Printf("  IPC Port:   %d\n", *port+10000)
	fmt.Printf("  PID File:   %s\n", pidFile)
	fmt.Printf("\nAgent is running. Press Ctrl+C to shutdown.\n")

	// Block until signal received
	<-sigCh

	fmt.Println("\n[agent] Shutting down...")
	cancel()

	server.Close()
	disc.Stop()
	ipcSrv.Stop()
	os.Remove(pidFile)

	fmt.Println("[agent] Shutdown complete")
}

// handleStatus shows status via IPC client (for running agents)
func handleStatus() {
	if len(os.Args) < 3 {
		// Interactive: need to specify port
		fmt.Println("Usage: agent status --port <port>")
		os.Exit(1)
	}

	fs := flag.NewFlagSet("status", flag.ContinueOnError)
	port := fs.Int("port", 9000, "Agent port")
	fs.Parse(os.Args[2:])

	client := ipc.NewClient(*port)
	status, err := client.Status()
	if err != nil {
		fmt.Printf("Failed to get status: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Agent Status:\n")
	fmt.Printf("  Agent ID:   %v\n", status["agentId"])
	fmt.Printf("  Agent Name: %v\n", status["agentName"])
	fmt.Printf("  Port:       %v\n", status["agentPort"])
	fmt.Printf("  Peers:      %v\n", status["peerCount"])
	fmt.Printf("  Groups:     %v\n", status["groupCount"])
	fmt.Printf("  History:    %v messages\n", status["msgHistoryCount"])
}

// serverHandler implements transport.MessageHandler for persistent mode
type persistentServerHandler struct {
	agent *core.Agent
	disp  *dispatcher.Dispatcher
	exec  *executor.Executor
}

func (h *persistentServerHandler) HandleMessage(msg *proto.AgentMessage, reply func(*proto.AgentMessage)) {
	adapter := &executorAdapter{exec: h.exec}
	h.disp.HandleMessage(msg, adapter, reply)
}

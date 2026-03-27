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
	case "peers":
		handlePeers()
	case "send":
		handleSend()
	case "group":
		handleGroup()
	case "groups":
		handleGroups()
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
                          Start agent with name and port, begin discovery
  agent peers              Show discovered peers with capabilities
  agent send <peer-id> <message>
                          Send TEXT message to specific peer
  agent group create <name>
                          Create a new group
  agent group invite <group-id> <peer-id>
                          Invite peer to group
  agent group join <group-id>
                          Join an existing group
  agent groups             Show all groups agent is in
  agent group leave <group-id>
                          Leave a group
  agent help               Show this help message

Examples:
  agent start --name Alice --port 9001
  agent peers
  agent send peer-123 "Hello peer"
  agent group create "Team Alpha"
  agent group invite group-456 peer-789
  agent group join group-456
  agent groups
  agent group leave group-456
`)
}

func handleStart() {
	fs := flag.NewFlagSet("start", flag.ContinueOnError)
	name := fs.String("name", "Agent", "Agent name")
	port := fs.Int("port", 9000, "Port for gRPC transport server")
	fs.Parse(os.Args[2:])

	ctx = &CLIContext{
		agent: core.NewAgent("", *name, *port, []proto.Capability{
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
	h.ctx.disp.HandleMessage(msg, adapter)

	// Auto-acknowledge text messages
	if msg.Type == proto.MessageType_TEXT {
		reply(&proto.AgentMessage{
			Id:        fmt.Sprintf("reply-%d", time.Now().UnixNano()),
			Timestamp: time.Now().Unix(),
			SenderId:  h.ctx.agent.ID,
			Type:      proto.MessageType_RESPONSE,
			Payload:   []byte(`{"ack":true,"text":"message received"}`),
		})
	}
}

func handlePeers() {
	if ctx == nil || ctx.disc == nil {
		fmt.Println("Agent not started. Run 'agent start' first.")
		os.Exit(1)
	}

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
	if ctx == nil || ctx.grpMgr == nil {
		fmt.Println("Agent not started. Run 'agent start' first.")
		os.Exit(1)
	}

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
}

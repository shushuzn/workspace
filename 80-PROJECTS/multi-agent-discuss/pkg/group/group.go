package group

import (
	"errors"
	"fmt"
	"sync"
	"time"
)

type GroupEvent int

const (
	GroupEventMemberJoined GroupEvent = iota
	GroupEventMemberLeft
	GroupEventGroupDissolved
	GroupEventInviteReceived
)

func (e GroupEvent) String() string {
	switch e {
	case GroupEventMemberJoined:
		return "MemberJoined"
	case GroupEventMemberLeft:
		return "MemberLeft"
	case GroupEventGroupDissolved:
		return "GroupDissolved"
	case GroupEventInviteReceived:
		return "InviteReceived"
	default:
		return "Unknown"
	}
}

type GroupMember struct {
	AgentID  string
	JoinedAt time.Time
	IsActive bool
}

type Group struct {
	ID      string
	Name    string
	OwnerID string
	Members map[string]*GroupMember
	Created time.Time
	mu      sync.RWMutex
}

func (g *Group) AddMember(agentID string) *GroupMember {
	g.mu.Lock()
	defer g.mu.Unlock()
	member := &GroupMember{
		AgentID:  agentID,
		JoinedAt: time.Now(),
		IsActive: true,
	}
	g.Members[agentID] = member
	return member
}

func (g *Group) RemoveMember(agentID string) bool {
	g.mu.Lock()
	defer g.mu.Unlock()
	if member, ok := g.Members[agentID]; ok {
		member.IsActive = false
		return true
	}
	return false
}

func (g *Group) GetMember(agentID string) (*GroupMember, bool) {
	g.mu.RLock()
	defer g.mu.RUnlock()
	m, ok := g.Members[agentID]
	return m, ok
}

func (g *Group) GetMembers() []*GroupMember {
	g.mu.RLock()
	defer g.mu.RUnlock()
	members := make([]*GroupMember, 0, len(g.Members))
	for _, m := range g.Members {
		members = append(members, m)
	}
	return members
}

func (g *Group) IsOwner(agentID string) bool {
	g.mu.RLock()
	defer g.mu.RUnlock()
	return g.OwnerID == agentID
}

func (g *Group) IsMember(agentID string) bool {
	g.mu.RLock()
	defer g.mu.RUnlock()
	m, ok := g.Members[agentID]
	return ok && m.IsActive
}

func (g *Group) MemberCount() int {
	g.mu.RLock()
	defer g.mu.RUnlock()
	count := 0
	for _, m := range g.Members {
		if m.IsActive {
			count++
		}
	}
	return count
}

type Invite struct {
	FromAgentID string
	ToAgentID   string
	GroupID     string
	GroupName   string
	Timestamp   time.Time
}

type GroupManager struct {
	agentID       string
	myGroups      map[string]*Group  // groups I created/own
	joinedGroups  map[string]*Group   // groups I joined as member
	pendingInvites map[string]*Invite // pending invites to me, keyed by groupID
	onEvent       func(event GroupEvent, groupID string, agentID string)
	mu            sync.RWMutex
}

func NewGroupManager(agentID string) *GroupManager {
	return &GroupManager{
		agentID:       agentID,
		myGroups:      make(map[string]*Group),
		joinedGroups:  make(map[string]*Group),
		pendingInvites: make(map[string]*Invite),
	}
}

func (gm *GroupManager) SetEventHandler(handler func(event GroupEvent, groupID string, agentID string)) {
	gm.mu.Lock()
	defer gm.mu.Unlock()
	gm.onEvent = handler
}

func (gm *GroupManager) emitEvent(event GroupEvent, groupID string, agentID string) {
	// Capture handler without holding lock to avoid deadlock
	gm.mu.RLock()
	handler := gm.onEvent
	gm.mu.RUnlock()
	if handler != nil {
		handler(event, groupID, agentID)
	}
}

func (gm *GroupManager) CreateGroup(name string) (*Group, error) {
	gm.mu.Lock()
	defer gm.mu.Unlock()

	group := &Group{
		ID:      fmt.Sprintf("group-%d", time.Now().UnixNano()),
		Name:    name,
		OwnerID: gm.agentID,
		Members: make(map[string]*GroupMember),
		Created: time.Now(),
	}

	// Owner is automatically a member
	group.Members[gm.agentID] = &GroupMember{
		AgentID:  gm.agentID,
		JoinedAt: group.Created,
		IsActive: true,
	}

	gm.myGroups[group.ID] = group

	return group, nil
}

func (gm *GroupManager) JoinGroup(invite *Invite) error {
	gm.mu.Lock()
	defer gm.mu.Unlock()

	// Validate invite
	if invite.ToAgentID != gm.agentID {
		return errors.New("invite is not for this agent")
	}

	// Find the group in myGroups (owner invited me) or need to look elsewhere
	group, ok := gm.myGroups[invite.GroupID]
	if !ok {
		return errors.New("group not found or you were not invited to this group")
	}

	// Add myself as a member
	group.Members[gm.agentID] = &GroupMember{
		AgentID:  gm.agentID,
		JoinedAt: time.Now(),
		IsActive: true,
	}

	gm.joinedGroups[group.ID] = group

	// Remove from pending invites
	delete(gm.pendingInvites, invite.GroupID)

	gm.emitEvent(GroupEventMemberJoined, group.ID, gm.agentID)

	return nil
}

func (gm *GroupManager) LeaveGroup(groupID string) error {
	gm.mu.Lock()
	defer gm.mu.Unlock()

	// Check if I'm a member of this group
	group, ok := gm.joinedGroups[groupID]
	if !ok {
		return errors.New("not a member of this group")
	}

	// Owner cannot leave - must dissolve or transfer
	if group.OwnerID == gm.agentID {
		return errors.New("owner cannot leave own group; must dissolve or transfer ownership")
	}

	// Remove myself from the group
	if member, ok := group.Members[gm.agentID]; ok {
		member.IsActive = false
	}

	delete(gm.joinedGroups, groupID)

	gm.emitEvent(GroupEventMemberLeft, groupID, gm.agentID)

	return nil
}

func (gm *GroupManager) DissolveGroup(groupID string) error {
	gm.mu.Lock()

	group, ok := gm.myGroups[groupID]
	if !ok {
		gm.mu.Unlock()
		return errors.New("group not found or you are not the owner")
	}

	// Collect events to emit after releasing lock
	var events []GroupEventInfo
	for _, member := range group.Members {
		if member.IsActive && member.AgentID != gm.agentID {
			events = append(events, GroupEventInfo{Event: GroupEventGroupDissolved, AgentID: member.AgentID})
		}
	}

	// Remove from my groups
	delete(gm.myGroups, groupID)

	// Remove from joined groups if I was also a member
	delete(gm.joinedGroups, groupID)

	events = append(events, GroupEventInfo{Event: GroupEventGroupDissolved, AgentID: gm.agentID})
	gm.mu.Unlock()

	// Emit events after releasing lock
	for _, e := range events {
		gm.emitEvent(e.Event, groupID, e.AgentID)
	}

	return nil
}

type GroupEventInfo struct {
	Event  GroupEvent
	AgentID string
}

func (gm *GroupManager) InviteToGroup(groupID, toAgentID string) *Invite {
	gm.mu.RLock()
	group, ok := gm.myGroups[groupID]
	isOwner := ok && group.OwnerID == gm.agentID
	gm.mu.RUnlock()

	if !isOwner {
		return nil
	}

	invite := &Invite{
		FromAgentID: gm.agentID,
		ToAgentID:   toAgentID,
		GroupID:     groupID,
		GroupName:   group.Name,
		Timestamp:   time.Now(),
	}

	return invite
}

func (gm *GroupManager) GetGroups() []*Group {
	gm.mu.RLock()
	defer gm.mu.RUnlock()

	groups := make([]*Group, 0, len(gm.myGroups)+len(gm.joinedGroups))

	for _, g := range gm.myGroups {
		groups = append(groups, g)
	}

	seen := make(map[string]bool)
	for id := range gm.myGroups {
		seen[id] = true
	}

	for _, g := range gm.joinedGroups {
		if !seen[g.ID] {
			groups = append(groups, g)
		}
	}

	return groups
}

func (gm *GroupManager) GetMembers(groupID string) []*GroupMember {
	gm.mu.RLock()
	defer gm.mu.RUnlock()

	// Check myGroups first
	if group, ok := gm.myGroups[groupID]; ok {
		return group.GetMembers()
	}

	// Check joinedGroups
	if group, ok := gm.joinedGroups[groupID]; ok {
		return group.GetMembers()
	}

	return nil
}

func (gm *GroupManager) HandleInvite(invite *Invite) {
	gm.mu.Lock()
	defer gm.mu.Unlock()

	// Only handle invites addressed to me
	if invite.ToAgentID != gm.agentID {
		return
	}

	gm.pendingInvites[invite.GroupID] = invite

	gm.emitEvent(GroupEventInviteReceived, invite.GroupID, invite.FromAgentID)
}

func (gm *GroupManager) GetPendingInvites() []*Invite {
	gm.mu.RLock()
	defer gm.mu.RUnlock()

	invites := make([]*Invite, 0, len(gm.pendingInvites))
	for _, inv := range gm.pendingInvites {
		invites = append(invites, inv)
	}

	return invites
}

func (gm *GroupManager) GetMyGroups() []*Group {
	gm.mu.RLock()
	defer gm.mu.RUnlock()

	groups := make([]*Group, 0, len(gm.myGroups))
	for _, g := range gm.myGroups {
		groups = append(groups, g)
	}
	return groups
}

func (gm *GroupManager) GetJoinedGroups() []*Group {
	gm.mu.RLock()
	defer gm.mu.RUnlock()

	groups := make([]*Group, 0, len(gm.joinedGroups))
	for _, g := range gm.joinedGroups {
		groups = append(groups, g)
	}
	return groups
}

func (gm *GroupManager) IsGroupOwner(groupID string) bool {
	gm.mu.RLock()
	defer gm.mu.RUnlock()
	group, ok := gm.myGroups[groupID]
	if !ok {
		return false
	}
	return group.OwnerID == gm.agentID
}

func (gm *GroupManager) IsGroupMember(groupID string) bool {
	gm.mu.RLock()
	defer gm.mu.RUnlock()
	_, ok := gm.joinedGroups[groupID]
	if ok {
		return true
	}
	_, ok = gm.myGroups[groupID]
	return ok
}

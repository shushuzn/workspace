# Cross-Project Identity System — Implementation Plan

## Overview

Implement a lightweight identity layer connecting `agent-arena`, `ai-roundtable`, and `star-forge-web`. Each project stays decoupled; only narrative identity (name, backstory, cross-scenario stats) is shared.

---

## Phase 1: Identity Store (Shared Module)

**Goal:** Create the shared `identityStore.js` module used by all three projects.

### File: `src/shared/identityStore.js`

```javascript
// Shared identity layer — used by all three projects
// Storage key: localStorage['starforge_identities']

const STORAGE_KEY = 'starforge_identities';

export function loadIdentityState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : { identities: [], activeIdentityId: null };
  } catch {
    return { identities: [], activeIdentityId: null };
  }
}

export function saveIdentityState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

// Get or create identity for an agent from agent-arena
export function getOrCreateIdentity(agent) {
  const state = loadIdentityState();
  let identity = state.identities.find(i => i.id === agent.id);

  if (!identity) {
    identity = {
      id: agent.id,
      name: agent.name,
      backstory: agent.backstory || '',
      rarity: agent.rarity || 'common',
      avatar: agent.avatar || '',
      arenaWins: 0,
      roundtableUses: 0,
      seasonUnlocks: [],
      status: 'active',
      createdAt: Date.now(),
      lastUsed: Date.now(),
    };
    state.identities.push(identity);
  }

  identity.lastUsed = Date.now();
  saveIdentityState(state);
  return identity;
}

// Get only active (non-retired) identities for UI display
export function getActiveIdentities() {
  const state = loadIdentityState();
  return state.identities.filter(i => i.status !== 'retired');
}

// Increment arena wins on an identity
export function addArenaWin(agentId) {
  const state = loadIdentityState();
  const identity = state.identities.find(i => i.id === agentId);
  if (identity && identity.status !== 'retired') {
    identity.arenaWins++;
    identity.lastUsed = Date.now();
    saveIdentityState(state);
  }
}

// Increment roundtable uses on an identity
export function addRoundtableUse(agentId) {
  const state = loadIdentityState();
  const identity = state.identities.find(i => i.id === agentId);
  if (identity && identity.status !== 'retired') {
    identity.roundtableUses++;
    identity.lastUsed = Date.now();
    saveIdentityState(state);
  }
}

// Mark an identity as retired (agent was deleted in arena)
export function retireIdentity(agentId) {
  const state = loadIdentityState();
  const identity = state.identities.find(i => i.id === agentId);
  if (identity) {
    identity.status = 'retired';
    identity.retiredAt = Date.now();
    saveIdentityState(state);
  }
}
```

> Note: This file lives in a shared location accessible to all three projects. The exact path depends on the project structure. For now, implement it in `agent-arena/src/` first (as `src/shared/identityStore.js`), then copy/symlink to the other two projects.

---

## Phase 2: agent-arena Integration

**Files to modify:**

- `src/game/gameStore.js` — hook arena match end to sync identity
- `src/components/AgentCard.jsx` — show identity status badge

### `src/game/gameStore.js`

After a match ends, call `addArenaWin(agentId)` if result is 'win'.

```javascript
// In gameStore.js, after existing match result logic:
import { addArenaWin } from '../shared/identityStore';

function onMatchEnd(result, agent) {
  // ... existing logic (XP, level up, etc.) ...

  // Sync to identity layer
  if (result === 'win' && agent?.id) {
    addArenaWin(agent.id);
  }
}
```

When a new Agent is created, call `getOrCreateIdentity(agent)`:

```javascript
import { getOrCreateIdentity } from '../shared/identityStore';

// In createAgent or gacha result handler:
getOrCreateIdentity(newAgent);
```

When an Agent is deleted, call `retireIdentity(agentId)`:

```javascript
import { retireIdentity } from '../shared/identityStore';

// In delete agent handler:
retireIdentity(agentId);
```

### `src/components/AgentCard.jsx` (optional, Phase 2)

Add a small badge showing "圆桌: N次" if `roundtableUses > 0`. Read from `getActiveIdentities()` filtered by agent ID.

---

## Phase 3: ai-roundtable Integration

**Files to modify:**

- `index.js` — add identity selection step before discussion starts

### `index.js` — Discussion Start Flow

Before starting a new discussion, check for active identities:

```javascript
import { getActiveIdentities } from './shared/identityStore';

async function startDiscussion(topic, roundCount) {
  const identities = getActiveIdentities();

  if (identities.length > 0) {
    // Show identity selection (new step before the existing flow)
    const selectedIdentity = await promptIdentitySelection(identities);
    if (selectedIdentity) {
      applyIdentityToPersona(selectedIdentity);
    }
  }

  // Continue with existing discussion logic...
}
```

### Identity-based persona modifier

In `data/personas.js` or inline, add temperature/personality modifiers based on rarity:

```javascript
const IDENTITY_TEMPERATURE_MAP = {
  common: 0.8,
  uncommon: 0.8,
  rare: 1.0,
  epic: 1.2,
  legendary: 1.5,
  mythic: 1.5,
};

export function getPersonalityModifier(rarity) {
  return IDENTITY_TEMPERATURE_MAP[rarity] ?? 1.0;
}
```

When an identity is selected, use its `rarity` to adjust the persona's temperature in the API call.

After discussion ends, call `addRoundtableUse(selectedIdentity.id)`.

---

## Phase 4: Testing & Polish

- Verify identity syncs correctly across agent-arena and ai-roundtable
- Test soft-delete: retire an identity, verify it disappears from UI
- Edge case: localStorage unavailable — all identity functions should fail silently (no crash)

---

## File Summary

| Action | File | Note |
|--------|------|------|
| CREATE | `agent-arena/src/shared/identityStore.js` | Phase 1 |
| MODIFY | `agent-arena/src/game/gameStore.js` | Phase 1 — sync on match end |
| MODIFY | `agent-arena/src/components/AgentCard.jsx` | Phase 1 (optional) |
| COPY | `ai-roundtable/shared/identityStore.js` | Copy from Phase 1 |
| MODIFY | `ai-roundtable/index.js` | Phase 2 — identity selection + addRoundtableUse |

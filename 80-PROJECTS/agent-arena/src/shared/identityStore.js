// Shared identity layer for cross-project narrative identity
// Storage key: localStorage['starforge_identities']
//
// This module is used by:
//   - agent-arena: creates identities, syncs arena wins
//   - ai-roundtable: reads identities for persona selection

const STORAGE_KEY = 'starforge_identities';

// ─── Load / Save ─────────────────────────────────────────────────────────────

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : { identities: [] };
  } catch {
    return { identities: [] };
  }
}

function saveState(state) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  } catch {
    // localStorage full or unavailable — fail silently
  }
}

// ─── Read ───────────────────────────────────────────────────────────────────

/**
 * Returns only active (non-retired) identities for UI display.
 * @returns {CrossProjectIdentity[]}
 */
export function getActiveIdentities() {
  const state = loadState();
  return state.identities.filter(i => i.status !== 'retired');
}

/**
 * Returns all identities including retired ones (for agent detail pages).
 * @returns {CrossProjectIdentity[]}
 */
export function getAllIdentities() {
  return loadState().identities;
}

// ─── Write ──────────────────────────────────────────────────────────────────

/**
 * Get an existing identity by agent ID, or create a new one.
 * Called when a new Agent is created in agent-arena.
 * @param {object} agent - Agent object from agent-arena (must have id, name, backstory, rarity, avatar)
 * @returns {CrossProjectIdentity}
 */
export function getOrCreateIdentity(agent) {
  const state = loadState();
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
      status: 'active',
      createdAt: Date.now(),
      lastUsed: Date.now(),
    };
    state.identities.push(identity);
  } else {
    identity.lastUsed = Date.now();
  }

  saveState(state);
  return identity;
}

/**
 * Increment arena win counter for an identity.
 * Called after a match ends with result === 'win'.
 * @param {string} agentId
 */
export function addArenaWin(agentId) {
  const state = loadState();
  const identity = state.identities.find(i => i.id === agentId);
  if (identity && identity.status !== 'retired') {
    identity.arenaWins++;
    identity.lastUsed = Date.now();
    saveState(state);
  }
}

/**
 * Increment roundtable use counter for an identity.
 * Called after a roundtable discussion ends.
 * @param {string} agentId
 */
export function addRoundtableUse(agentId) {
  const state = loadState();
  const identity = state.identities.find(i => i.id === agentId);
  if (identity && identity.status !== 'retired') {
    identity.roundtableUses++;
    identity.lastUsed = Date.now();
    saveState(state);
  }
}

/**
 * Soft-delete an identity when its source Agent is deleted in agent-arena.
 * Stats (arenaWins, roundtableUses) are preserved.
 * @param {string} agentId
 */
export function retireIdentity(agentId) {
  const state = loadState();
  const identity = state.identities.find(i => i.id === agentId);
  if (identity) {
    identity.status = 'retired';
    identity.retiredAt = Date.now();
    saveState(state);
  }
}

/**
 * Get a single identity by agent ID.
 * @param {string} agentId
 * @returns {CrossProjectIdentity|null}
 */
export function getIdentity(agentId) {
  return loadState().identities.find(i => i.id === agentId) || null;
}

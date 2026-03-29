// Shared identity layer for cross-project narrative identity
// Storage: localStorage (browser) OR JSON file (Node.js)
// Storage key: 'starforge_identities' / ~/.starforge_identities.json
//
// This module is used by:
//   - agent-arena: creates identities, syncs arena wins (browser)
//   - ai-roundtable: reads identities for persona selection (Node.js)

import { readFileSync, writeFileSync, existsSync } from 'fs';
import { join } from 'path';
import os from 'os';

const STORAGE_KEY = 'starforge_identities';

// ─── Storage adapter (localStorage for browser, fs for Node.js) ─────────────

function isBrowser() {
  try {
    return typeof window !== 'undefined' && typeof localStorage !== 'undefined';
  } catch {
    return false;
  }
}

function getStoragePath() {
  return join(os.homedir(), '.starforge_identities.json');
}

// ─── Load / Save ─────────────────────────────────────────────────────────────

function loadState() {
  try {
    if (isBrowser()) {
      const raw = localStorage.getItem(STORAGE_KEY);
      return raw ? JSON.parse(raw) : { identities: [] };
    } else {
      // Node.js: read from JSON file (synchronous)
      const storagePath = getStoragePath();
      if (existsSync(storagePath)) {
        const raw = readFileSync(storagePath, 'utf-8');
        return JSON.parse(raw);
      }
      return { identities: [] };
    }
  } catch {
    return { identities: [] };
  }
}

function saveState(state) {
  try {
    if (isBrowser()) {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } else {
      // Node.js: write to JSON file (synchronous)
      const storagePath = getStoragePath();
      writeFileSync(storagePath, JSON.stringify(state, null, 2));
    }
  } catch (err) {
    // Storage unavailable — fail silently
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

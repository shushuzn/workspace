import { describe, it, expect, beforeEach } from 'vitest';
import { gameStore } from '../src/stores/gameStore.js';

describe('gameStore', () => {
  let initialState;

  beforeEach(() => {
    initialState = gameStore.getState();
    gameStore.setState({
      coins: 1000,
      gems: 10,
      agents: [],
      selectedAgentId: null,
      activeTab: 'home',
      battleLog: [],
      stats: {
        totalBattles: 0,
        totalWins: 0,
        totalCoinsEarned: 0,
        playTime: 0,
        startTime: Date.now()
      },
      settings: {
        soundEnabled: true,
        musicEnabled: true
      },
      notifications: [],
      showModal: null,
      modalData: null
    });
  });

  it('should have correct initial state structure', () => {
    const state = gameStore.getState();
    expect(state).toHaveProperty('coins');
    expect(state).toHaveProperty('gems');
    expect(state).toHaveProperty('agents');
    expect(state).toHaveProperty('selectedAgentId');
    expect(state).toHaveProperty('activeTab');
    expect(state).toHaveProperty('stats');
    expect(state).toHaveProperty('settings');
  });

  it('should add coins correctly', () => {
    gameStore.addCoins(500);
    const state = gameStore.getState();
    expect(state.coins).toBe(1500);
  });

  it('should spend coins when sufficient balance', () => {
    const result = gameStore.spendCoins(500);
    expect(result).toBe(true);
    const state = gameStore.getState();
    expect(state.coins).toBe(500);
  });

  it('should reject spend when insufficient balance', () => {
    const result = gameStore.spendCoins(2000);
    expect(result).toBe(false);
    const state = gameStore.getState();
    expect(state.coins).toBe(1000);
  });

  it('should add gems correctly', () => {
    gameStore.addGems(5);
    const state = gameStore.getState();
    expect(state.gems).toBe(15);
  });

  it('should spend gems when sufficient balance', () => {
    const result = gameStore.spendGems(5);
    expect(result).toBe(true);
    const state = gameStore.getState();
    expect(state.gems).toBe(5);
  });

  it('should reject spend gems when insufficient balance', () => {
    const result = gameStore.spendGems(20);
    expect(result).toBe(false);
    const state = gameStore.getState();
    expect(state.gems).toBe(10);
  });

  it('should set active tab', () => {
    gameStore.setTab('battle');
    const state = gameStore.getState();
    expect(state.activeTab).toBe('battle');
  });

  it('should add an agent', () => {
    const agent = { id: 'agent-1', name: 'Test Agent', level: 1, xp: 0, stats: { intelligence: 10, speed: 10, creativity: 10, endurance: 10 } };
    gameStore.addAgent(agent);
    const state = gameStore.getState();
    expect(state.agents).toHaveLength(1);
    expect(state.agents[0].id).toBe('agent-1');
  });

  it('should remove an agent by id', () => {
    const agent = { id: 'agent-1', name: 'Test Agent', level: 1, xp: 0, stats: { intelligence: 10, speed: 10, creativity: 10, endurance: 10 } };
    gameStore.addAgent(agent);
    gameStore.removeAgent('agent-1');
    const state = gameStore.getState();
    expect(state.agents).toHaveLength(0);
  });

  it('should select an agent', () => {
    const agent = { id: 'agent-1', name: 'Test Agent', level: 1, xp: 0, stats: { intelligence: 10, speed: 10, creativity: 10, endurance: 10 } };
    gameStore.addAgent(agent);
    gameStore.selectAgent('agent-1');
    const state = gameStore.getState();
    expect(state.selectedAgentId).toBe('agent-1');
  });

  it('should update an agent', () => {
    const agent = { id: 'agent-1', name: 'Test Agent', level: 1, xp: 0, stats: { intelligence: 10, speed: 10, creativity: 10, endurance: 10 } };
    gameStore.addAgent(agent);
    gameStore.updateAgent('agent-1', { level: 2 });
    const state = gameStore.getState();
    expect(state.agents[0].level).toBe(2);
  });

  it('should handle notification', () => {
    gameStore.notify('Test notification', 'info');
    const state = gameStore.getState();
    expect(state.notifications).toBeDefined();
  });

  it('should restore full state', () => {
    const newState = {
      coins: 5000,
      gems: 50,
      agents: [],
      selectedAgentId: null,
      activeTab: 'shop',
      battleLog: [],
      stats: { totalBattles: 10, totalWins: 5, totalCoinsEarned: 1000, playTime: 600, startTime: Date.now() },
      settings: { soundEnabled: false, musicEnabled: false },
      notifications: [],
      showModal: null,
      modalData: null
    };
    gameStore.setState(newState);
    const state = gameStore.getState();
    expect(state.coins).toBe(5000);
    expect(state.gems).toBe(50);
    expect(state.activeTab).toBe('shop');
    expect(state.settings.soundEnabled).toBe(false);
  });
});

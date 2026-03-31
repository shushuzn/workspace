/**
 * Default Configuration for Self-Evolving Workspace Optimizer
 */

export const CONFIG = {
  // Epsilon-greedy parameters
  epsilon: {
    min: 0.1,      // 基础最低探索率 10%
    max: 0.5,      // 最高探索率 50%
    init: 0.3,     // 初始探索率 30%
    minHighScore: 0.05,  // 健康度>90时降至5%
    decayStep: 0.05,     // 每次成功衰减
    growthStep: 0.1      // 每次失败增长
  },

  // Cooldown periods
  cooldown: {
    productive: 3,   // productive ops 冷却期
    detection: 1,    // detection ops 冷却期
    detectionOps: ['check_memory_size', 'check_project_readmes', 'brainstorm_projects', 'find_large_files']
  },

  // Streak thresholds
  streak: {
    successThreshold: 3,  // 连续成功3次后降低epsilon
    failThreshold: 3,    // 连续失败3次后提高epsilon
  },

  // Large file whitelist (KB)
  largeFileWhitelist: [
    '80-PROJECTS/idle-empire/butler',
    '80-PROJECTS/multi-agent-discuss/bin/agent.exe'
  ],

  // Workspace paths
  workspace: {
    root: null,           // Set dynamically
    projects: '80-PROJECTS',
    memory: '.omc/memory',
    history: '.omc/loop-history.json',
    brainstorm: '.omc/brainstorm',
    dashboard: 'dashboard-data.json'
  },

  // History
  history: {
    maxRecords: 100,
    retentionDays: 90
  },

  // Large file scanning
  largeFile: {
    limitMB: 5,
    maxDepth: 3,
    safePatterns: ['.cache', 'cache', 'temp', 'tmp', '.tmp', 'dist', 'build', 'output', '.log', 'logs']
  },

  // Brainstorm
  brainstorm: {
    minDaysBetween: 14
  },

  // Session/checkpoint cleanup
  cleanup: {
    staleSessionDays: 30
  }
};

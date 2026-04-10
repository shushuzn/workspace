#!/usr/bin/env node
/**
 * OMC状态检查统一入口
 * 读取所有状态文件，汇总输出结构化状态报告
 */
import { readFileSync, existsSync } from 'fs';
import { join } from 'path';
import { homedir } from 'os';

const STATE_DIR = join(homedir(), '.omc', 'state');

function readJson(filename) {
  const path = join(STATE_DIR, filename);
  if (!existsSync(path)) return null;
  try {
    return JSON.parse(readFileSync(path, 'utf8'));
  } catch {
    return null;
  }
}

function getInsightEffectiveness() {
  const data = readJson('insight-effectiveness.json');
  if (!data) return null;
  const total = data.total || 0;
  const executed = data.executed || 0;
  return { total, executed, rate: total > 0 ? ((executed / total) * 100).toFixed(1) : '0' };
}

function getAutoSeedStatus() {
  const counter = readJson('auto-seed-counter.json');
  const errors = readJson('auto-seed-errors.json');
  const patterns = readJson('auto-seed-patterns.json');
  return {
    counter: counter?.count || 0,
    errors: errors?.errors?.length || 0,
    patterns: patterns?.patterns?.length || 0
  };
}

function getHookStats() {
  const hookStats = readJson('hook-stats-cache.json');
  if (!hookStats) return null;
  return {
    sessionTime: hookStats.sessionTime || 0,
    totalCalls: hookStats.totalCalls || 0,
    toolsTriggered: hookStats.toolsTriggered || 0
  };
}

function getInsightTrigger() {
  const trigger = readJson('auto-insight-trigger.json');
  if (!trigger) return null;
  return {
    count: trigger.count || 0,
    activePattern: trigger.activePattern || null
  };
}

function formatBytes(bytes) {
  if (bytes < 1024) return bytes + 'B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + 'KB';
  return (bytes / (1024 * 1024)).toFixed(1) + 'MB';
}

console.log('=== OMC 状态报告 ===\n');

// Auto-seed
const autoSeed = getAutoSeedStatus();
console.log('【Auto-Seed】');
console.log(`  触发计数: ${autoSeed.counter}`);
console.log(`  错误数: ${autoSeed.errors}`);
console.log(`  Pattern数: ${autoSeed.patterns}`);
console.log();

// Insight Effectiveness
const effectiveness = getInsightEffectiveness();
console.log('【Insight Effectiveness】');
console.log(`  Total: ${effectiveness?.total || 0}`);
console.log(`  Executed: ${effectiveness?.executed || 0}`);
console.log(`  Rate: ${effectiveness?.rate || '0'}%`);
console.log();

// Insight Trigger
const trigger = getInsightTrigger();
console.log('【Insight Trigger】');
console.log(`  Count: ${trigger?.count || 0}`);
console.log(`  Active Pattern: ${trigger?.activePattern || 'none'}`);
console.log();

// Hook Stats
const hookStats = getHookStats();
if (hookStats) {
  console.log('【Hook Stats (this session)】');
  console.log(`  Session Time: ${(hookStats.sessionTime / 1000 / 60).toFixed(1)} min`);
  console.log(`  Total Calls: ${hookStats.totalCalls}`);
  console.log(`  Tools Triggered: ${hookStats.toolsTriggered}`);
  console.log();
}

// Pending Actions
const pendingPath = join(STATE_DIR, 'pending-actions.md');
if (existsSync(pendingPath)) {
  const pending = readFileSync(pendingPath, 'utf8').trim();
  console.log('【Pending Actions】');
  console.log(`  ${pending ? pending.split('\n').length + ' items' : 'none'}`);
  console.log();
}

// Recent session
const sessionFile = readJson('mission-state.json');
if (sessionFile) {
  console.log('【Session】');
  console.log(`  Project: ${sessionFile.project || 'unknown'}`);
  console.log(`  Session ID: ${sessionFile.sessionId?.slice(0, 8) || 'unknown'}`);
  console.log();
}

console.log('=== 完整状态文件 ===');
console.log('  .omc/state/');
console.log('  查看详细: ls ~/.omc/state/');

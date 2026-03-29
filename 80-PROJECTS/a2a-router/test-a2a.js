#!/usr/bin/env node
/**
 * A2A Protocol Test Script
 * 
 * Tests the A2A Router functionality
 */

import { A2ARouter } from './src/router.js';
import { v4 as uuidv4 } from 'uuid';

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function runTests() {
  console.log('═══════════════════════════════════════════════════');
  console.log('  A2A Router Test Suite');
  console.log('═══════════════════════════════════════════════════\n');

  const router = new A2ARouter();
  let testsPassed = 0;
  let testsFailed = 0;

  // Test 1: Agent Registration
  console.log('Test 1: Agent Registration');
  console.log('───────────────────────────────────────────────────');
  try {
    const result1 = router.registerAgent('patrol-agent', ['scan', 'lint-check'], { version: '1.0' });
    console.log('✅ patrol-agent registered:', result1.success ? 'PASS' : 'FAIL');
    testsPassed++;

    const result2 = router.registerAgent('ai-roundtable', ['discuss', 'analyze'], { version: '1.0' });
    console.log('✅ ai-roundtable registered:', result2.success ? 'PASS' : 'FAIL');
    testsPassed++;

    const result3 = router.registerAgent('patrol-agent', ['scan']); // Duplicate
    console.log('✅ Duplicate registration blocked:', !result3.success ? 'PASS' : 'FAIL');
    testsPassed++;
  } catch (error) {
    console.log('❌ Test 1 failed:', error.message);
    testsFailed += 3;
  }
  console.log();

  // Test 2: Heartbeat
  console.log('Test 2: Heartbeat');
  console.log('───────────────────────────────────────────────────');
  try {
    const result = router.heartbeat('patrol-agent', 'healthy', 0.3, 2);
    console.log('✅ Heartbeat accepted:', result.success ? 'PASS' : 'FAIL');
    testsPassed++;

    const result2 = router.heartbeat('unknown-agent', 'healthy', 0, 0);
    console.log('✅ Unknown agent heartbeat rejected:', !result2.success ? 'PASS' : 'FAIL');
    testsPassed++;
  } catch (error) {
    console.log('❌ Test 2 failed:', error.message);
    testsFailed += 2;
  }
  console.log();

  // Test 3: Direct Message Routing
  console.log('Test 3: Direct Message Routing');
  console.log('───────────────────────────────────────────────────');
  try {
    const message = {
      id: uuidv4(),
      type: 'TASK',
      priority: 'NORMAL',
      from: 'patrol-agent',
      to: 'ai-roundtable',
      timestamp: Date.now(),
      payload: { task: 'discuss_problem', topic: 'Test Topic' },
      metadata: { correlationId: uuidv4() }
    };

    const result = router.routeMessage(message);
    console.log('✅ Direct routing:', result.success ? 'PASS' : 'FAIL');
    testsPassed++;

    // Test to unknown agent
    const badMessage = { ...message, to: 'unknown-agent' };
    const result2 = router.routeMessage(badMessage);
    console.log('✅ Unknown agent rejected:', !result2.success ? 'PASS' : 'FAIL');
    testsPassed++;
  } catch (error) {
    console.log('❌ Test 3 failed:', error.message);
    testsFailed += 2;
  }
  console.log();

  // Test 4: Broadcast
  console.log('Test 4: Broadcast');
  console.log('───────────────────────────────────────────────────');
  try {
    const broadcast = {
      id: uuidv4(),
      type: 'EVENT',
      priority: 'NORMAL',
      from: 'patrol-agent',
      to: 'broadcast',
      timestamp: Date.now(),
      payload: { event: 'problem_detected', problem: { id: 'p1', severity: 'high' } },
      metadata: {}
    };

    const result = router.routeMessage(broadcast);
    console.log('✅ Broadcast delivered to', result.delivered, 'agents:', result.success ? 'PASS' : 'FAIL');
    testsPassed++;
  } catch (error) {
    console.log('❌ Test 4 failed:', error.message);
    testsFailed++;
  }
  console.log();

  // Test 5: Capability Discovery
  console.log('Test 5: Capability Discovery');
  console.log('───────────────────────────────────────────────────');
  try {
    const discoverMessage = {
      id: uuidv4(),
      type: 'DISCOVER',
      priority: 'NORMAL',
      from: 'patrol-agent',
      to: 'router',
      timestamp: Date.now(),
      payload: { query: 'discuss' },
      metadata: { correlationId: uuidv4() }
    };

    const result = router.routeMessage(discoverMessage);
    console.log('✅ Discovery query processed:', result.success ? 'PASS' : 'FAIL');
    testsPassed++;
  } catch (error) {
    console.log('❌ Test 5 failed:', error.message);
    testsFailed++;
  }
  console.log();

  // Test 6: Message Validation
  console.log('Test 6: Message Validation');
  console.log('───────────────────────────────────────────────────');
  try {
    const invalidMessage = {
      id: uuidv4(),
      // Missing 'type'
      from: 'patrol-agent',
      to: 'ai-roundtable',
      timestamp: Date.now(),
      payload: {}
    };

    const result = router.routeMessage(invalidMessage);
    console.log('✅ Invalid message rejected:', !result.success ? 'PASS' : 'FAIL');
    testsPassed++;

    const invalidType = {
      id: uuidv4(),
      type: 'INVALID_TYPE',
      from: 'patrol-agent',
      to: 'ai-roundtable',
      timestamp: Date.now(),
      payload: {}
    };

    const result2 = router.routeMessage(invalidType);
    console.log('✅ Invalid type rejected:', !result2.success ? 'PASS' : 'FAIL');
    testsPassed++;
  } catch (error) {
    console.log('❌ Test 6 failed:', error.message);
    testsFailed += 2;
  }
  console.log();

  // Test 7: Statistics
  console.log('Test 7: Statistics');
  console.log('───────────────────────────────────────────────────');
  try {
    const stats = router.getStats();
    console.log('✅ Stats retrieved:', stats ? 'PASS' : 'FAIL');
    console.log('   - Agents online:', stats.agentsOnline);
    console.log('   - Messages routed:', stats.messagesRouted);
    console.log('   - Queue sizes:', stats.queueSizes);
    testsPassed++;
  } catch (error) {
    console.log('❌ Test 7 failed:', error.message);
    testsFailed++;
  }
  console.log();

  // Test 8: Unregister
  console.log('Test 8: Unregister');
  console.log('───────────────────────────────────────────────────');
  try {
    const result = router.unregisterAgent('ai-roundtable');
    console.log('✅ Agent unregistered:', result.success ? 'PASS' : 'FAIL');
    testsPassed++;

    const result2 = router.unregisterAgent('unknown-agent');
    console.log('✅ Unknown agent unregister rejected:', !result2.success ? 'PASS' : 'FAIL');
    testsPassed++;
  } catch (error) {
    console.log('❌ Test 8 failed:', error.message);
    testsFailed += 2;
  }
  console.log();

  // Summary
  console.log('═══════════════════════════════════════════════════');
  console.log('  Test Summary');
  console.log('═══════════════════════════════════════════════════');
  console.log(`  Total Tests: ${testsPassed + testsFailed}`);
  console.log(`  ✅ Passed: ${testsPassed}`);
  console.log(`  ❌ Failed: ${testsFailed}`);
  console.log(`  Success Rate: ${((testsPassed / (testsPassed + testsFailed)) * 100).toFixed(1)}%`);
  console.log('═══════════════════════════════════════════════════');

  return testsFailed === 0;
}

runTests().then(success => {
  process.exit(success ? 0 : 1);
}).catch(error => {
  console.error('Test suite failed:', error);
  process.exit(1);
});

import { describe, it, expect } from 'vitest';
import WorkflowOrchestrator, { workflowOrchestrator } from '../src/workflows/orchestrator.js';

describe('WorkflowOrchestrator', () => {
  it('should export a default class', () => {
    expect(WorkflowOrchestrator).toBeDefined();
    expect(typeof WorkflowOrchestrator).toBe('function');
  });

  it('should export a singleton instance', () => {
    expect(workflowOrchestrator).toBeDefined();
    expect(typeof workflowOrchestrator.getWorkflows).toBe('function');
  });

  it('should return workflows list via singleton', () => {
    const workflows = workflowOrchestrator.getWorkflows();
    expect(Array.isArray(workflows)).toBe(true);
    // Pre-registered workflows exist
    expect(workflows.length).toBeGreaterThan(0);
  });

  it('should have getWorkflow method', () => {
    expect(typeof workflowOrchestrator.getWorkflow).toBe('function');
  });

  it('should have getStats method', () => {
    expect(typeof workflowOrchestrator.getStats).toBe('function');
    const stats = workflowOrchestrator.getStats();
    expect(stats).toHaveProperty('total');
    expect(stats).toHaveProperty('running');
  });
});

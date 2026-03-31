/**
 * Budget (Governance Layer)
 * Resource limits and usage tracking
 */

import fs from 'fs';
import path from 'path';

export class Budget {
  constructor(workspace) {
    this.workspace = workspace;
    this.budgetFile = path.join(workspace, '.omc', 'budget.json');
    this.budget = this.loadBudget();
  }

  loadBudget() {
    if (fs.existsSync(this.budgetFile)) {
      try {
        return JSON.parse(fs.readFileSync(this.budgetFile, 'utf8'));
      } catch {
        return this.getDefaultBudget();
      }
    }
    return this.getDefaultBudget();
  }

  getDefaultBudget() {
    return {
      version: '1.0.0',
      updatedAt: Date.now(),
      limits: {
        iterations: { max: 100, current: 0 },
        tokens: { max: 1000000, current: 0, window: 'daily' },
        operations: { max: 500, current: 0, window: 'daily' },
        storage: { maxMB: 100, currentMB: 0 },
        disk: { maxMB: 500, currentMB: 0 }
      },
      resets: {
        daily: Date.now(),
        weekly: Date.now()
      }
    };
  }

  save() {
    const dir = path.dirname(this.budgetFile);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    this.budget.updatedAt = Date.now();
    fs.writeFileSync(this.budgetFile, JSON.stringify(this.budget, null, 2));
  }

  /**
   * Check if an operation is within budget
   */
  canProceed(operationType = 'iteration') {
    this.checkResets();

    const limits = this.budget.limits;

    // Check iterations
    if (limits.iterations.current >= limits.iterations.max) {
      return {
        allowed: false,
        reason: `达到最大迭代次数限制 (${limits.iterations.max})`,
        limit: 'iterations'
      };
    }

    // Check daily operations
    if (limits.operations.current >= limits.operations.max) {
      return {
        allowed: false,
        reason: `达到每日操作限制 (${limits.operations.max})`,
        limit: 'operations'
      };
    }

    // Check storage
    if (limits.storage.currentMB >= limits.storage.maxMB) {
      return {
        allowed: false,
        reason: `达到存储限制 (${limits.storage.maxMB}MB)`,
        limit: 'storage'
      };
    }

    return { allowed: true };
  }

  /**
   * Record resource usage
   */
  recordUsage(type, amount = 1) {
    this.checkResets();

    const limit = this.budget.limits[type];
    if (limit) {
      limit.current += amount;
      this.save();
    }
  }

  /**
   * Check if daily/weekly resets are needed
   */
  checkResets() {
    const now = Date.now();
    const dayMs = 24 * 60 * 60 * 1000;
    const weekMs = 7 * dayMs;

    // Daily reset
    if (now - this.budget.resets.daily > dayMs) {
      this.budget.limits.operations.current = 0;
      this.budget.limits.tokens.current = 0;
      this.budget.resets.daily = now;
      this.save();
    }

    // Weekly reset
    if (now - this.budget.resets.weekly > weekMs) {
      this.budget.limits.iterations.current = 0;
      this.budget.resets.weekly = now;
      this.save();
    }
  }

  /**
   * Update limits
   */
  updateLimits(newLimits) {
    this.budget.limits = { ...this.budget.limits, ...newLimits };
    this.save();
  }

  /**
   * Get current budget status
   */
  getStatus() {
    this.checkResets();

    const status = {
      iterations: {
        used: this.budget.limits.iterations.current,
        max: this.budget.limits.iterations.max,
        remaining: this.budget.limits.iterations.max - this.budget.limits.iterations.current
      },
      operations: {
        used: this.budget.limits.operations.current,
        max: this.budget.limits.operations.max,
        remaining: this.budget.limits.operations.max - this.budget.limits.operations.current
      },
      storage: {
        usedMB: this.budget.limits.storage.currentMB,
        maxMB: this.budget.limits.storage.maxMB,
        remainingMB: this.budget.limits.storage.maxMB - this.budget.limits.storage.currentMB
      }
    };

    return status;
  }

  /**
   * Calculate estimated cost (for future token-based billing)
   */
  estimateCost(iterations = 1) {
    // Simplified cost estimation
    const costPerIteration = 0.01; // $0.01 per iteration (example)
    return iterations * costPerIteration;
  }
}

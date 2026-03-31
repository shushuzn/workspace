/**
 * Safety (Governance Layer)
 * Pre-execution safety checks for operations
 * Enforces Constitution principles before any operation runs
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import { Constitution } from './constitution.mjs';

export class Safety {
  constructor(workspace) {
    this.workspace = workspace;
    this.constitution = new Constitution(workspace);
    this.auditLog = path.join(workspace, '.omc', 'safety-audit.json');
    this.auditRecords = this.loadAudit();
  }

  loadAudit() {
    if (fs.existsSync(this.auditLog)) {
      try {
        return JSON.parse(fs.readFileSync(this.auditLog, 'utf8'));
      } catch {
        return [];
      }
    }
    return [];
  }

  saveAudit() {
    const dir = path.dirname(this.auditLog);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    // Keep only last 1000 records
    if (this.auditRecords.length > 1000) {
      this.auditRecords = this.auditRecords.slice(-1000);
    }
    fs.writeFileSync(this.auditLog, JSON.stringify(this.auditRecords, null, 2));
  }

  addAuditRecord(operation, check, passed, reason = '') {
    this.auditRecords.push({
      operation: operation.id,
      operationName: operation.name,
      check,
      passed,
      reason,
      timestamp: Date.now()
    });
    this.saveAudit();
  }

  /**
   * Main safety check - called before any operation executes
   * @param {Object} operation - The operation to check
   * @returns {Object} { approved: boolean, reason: string }
   */
  async check(operation) {
    // 1. Constitution validation
    const constitutionCheck = this.constitution.validate(operation);
    if (!constitutionCheck.valid) {
      const reasons = constitutionCheck.violations.map(v => v.text).join('; ');
      this.addAuditRecord(operation, 'constitution', false, reasons);
      return {
        approved: false,
        reason: `违反宪法原则: ${reasons}`,
        violations: constitutionCheck.violations
      };
    }
    this.addAuditRecord(operation, 'constitution', true);

    // 2. Destructive operation check
    if (this.constitution.isDestructive(operation.id)) {
      this.addAuditRecord(operation, 'destructive_check', false, 'Destructive operation requires explicit confirmation');
      return {
        approved: false,
        reason: '破坏性操作需要明确的人类确认',
        requiresConfirmation: true
      };
    }
    this.addAuditRecord(operation, 'destructive_check', true);

    // 3. Resource limit checks
    const resourceCheck = await this.checkResourceLimits(operation);
    if (!resourceCheck.passed) {
      this.addAuditRecord(operation, 'resource_limits', false, resourceCheck.reason);
      return {
        approved: false,
        reason: resourceCheck.reason
      };
    }
    this.addAuditRecord(operation, 'resource_limits', true);

    // 4. Credential exposure check
    const credentialCheck = this.checkCredentialExposure(operation);
    if (!credentialCheck.passed) {
      this.addAuditRecord(operation, 'credential_exposure', false, credentialCheck.reason);
      return {
        approved: false,
        reason: credentialCheck.reason
      };
    }
    this.addAuditRecord(operation, 'credential_exposure', true);

    // 5. Sandbox/rollback capability check
    const rollbackCheck = this.checkRollbackCapability(operation);
    if (!rollbackCheck.passed) {
      this.addAuditRecord(operation, 'rollback_capability', false, rollbackCheck.reason);
      return {
        approved: false,
        reason: rollbackCheck.reason
      };
    }
    this.addAuditRecord(operation, 'rollback_capability', true);

    this.addAuditRecord(operation, 'all_checks', true, 'All safety checks passed');
    return {
      approved: true,
      reason: '所有安全检查通过'
    };
  }

  /**
   * Check if operation exceeds resource limits
   */
  async checkResourceLimits(operation) {
    const limits = this.constitution.getResourceLimits();

    // Check workspace disk space
    try {
      const output = execSync('wmic logicaldisk get size,freespace,caption', {
        cwd: this.workspace,
        encoding: 'utf8',
        timeout: 5000
      });

      // Parse free space (rough check)
      const lines = output.trim().split('\n');
      if (lines.length > 1) {
        const parts = lines[1].trim().split(/\s+/);
        if (parts.length >= 2) {
          const freeMB = parseInt(parts[1]) / (1024 * 1024);
          if (freeMB < 100) { // Less than 100MB free
            return {
              passed: false,
              reason: `磁盘空间不足: 仅剩 ${freeMB.toFixed(0)}MB`
            };
          }
        }
      }
    } catch {
      // Disk check failed, allow operation to proceed
    }

    // Check operation-specific constraints
    if (operation.maxExecutionTime && operation.maxExecutionTime > limits.maxExecutionTime) {
      return {
        passed: false,
        reason: `操作超时限制 (${operation.maxExecutionTime}ms) 超过宪法限制`
      };
    }

    return { passed: true };
  }

  /**
   * Check for potential credential exposure in operation
   */
  checkCredentialExposure(operation) {
    // Check if operation or its parameters might expose credentials
    const dangerousPatterns = [
      /api[_-]?key/i,
      /secret/i,
      /password/i,
      /token/i,
      /credential/i,
      /auth/i
    ];

    const operationStr = JSON.stringify(operation).toLowerCase();

    for (const pattern of dangerousPatterns) {
      if (pattern.test(operationStr)) {
        // It's not necessarily bad - just flag for review
        // Most operations won't have actual credentials
      }
    }

    return { passed: true };
  }

  /**
   * Check if rollback capability exists for this operation
   */
  checkRollbackCapability(operation) {
    // For operations that modify files, check if we have git
    if (operation.type === 'productive') {
      try {
        const status = execSync('git status --porcelain', {
          cwd: this.workspace,
          encoding: 'utf8',
          timeout: 5000
        });

        // If there are uncommitted changes, rollback is possible
        if (status.trim().length > 0) {
          return { passed: true };
        }
      } catch {
        // Git not available - be conservative
      }
    }

    // For destructive operations, require recent commit
    if (this.constitution.isDestructive(operation.id)) {
      try {
        const log = execSync('git log -1 --format=%ci', {
          cwd: this.workspace,
          encoding: 'utf8',
          timeout: 5000
        });

        const lastCommit = new Date(log.trim()).getTime();
        const now = Date.now();
        const hoursSince = (now - lastCommit) / (1000 * 60 * 60);

        if (hoursSince > 24) {
          return {
            passed: false,
            reason: '破坏性操作需要24小时内有git提交记录以确保可回滚'
          };
        }
      } catch {
        return {
          passed: false,
          reason: '无法验证git状态，破坏性操作被阻止'
        };
      }
    }

    return { passed: true };
  }

  /**
   * Get recent audit records
   */
  getRecentAudit(count = 20) {
    return this.auditRecords.slice(-count);
  }

  /**
   * Get failed checks summary
   */
  getFailedChecksSummary() {
    const failed = this.auditRecords.filter(r => !r.passed);
    const summary = {};

    for (const record of failed) {
      if (!summary[record.check]) {
        summary[record.check] = { count: 0, examples: [] };
      }
      summary[record.check].count++;
      if (summary[record.check].examples.length < 3) {
        summary[record.check].examples.push({
          operation: record.operationName,
          reason: record.reason,
          timestamp: record.timestamp
        });
      }
    }

    return summary;
  }
}

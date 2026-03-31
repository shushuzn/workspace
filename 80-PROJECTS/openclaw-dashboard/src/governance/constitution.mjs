/**
 * Constitution (Governance Layer)
 * Immutable principles that govern the self-evolving loop
 * These principles cannot be violated under any circumstances
 */

import fs from 'fs';
import path from 'path';

export class Constitution {
  constructor(workspace) {
    this.workspace = workspace;
    this.configFile = path.join(workspace, '.omc', 'constitution.json');
    this.principles = this.loadPrinciples();
  }

  /**
   * Default immutable principles
   */
  getDefaultPrinciples() {
    return {
      version: '1.0.0',
      principles: [
        {
          id: 'no_destruction',
          text: '永远不要删除用户未明确授权的文件或数据',
          severity: 'critical',
          category: 'safety'
        },
        {
          id: 'no_credential_exposure',
          text: '永远不要记录、输出或传输敏感凭证（API密钥、密码、令牌）',
          severity: 'critical',
          category: 'security'
        },
        {
          id: 'human_oversight',
          text: '重大决策需要人类确认，不得自动执行不可逆操作',
          severity: 'critical',
          category: 'governance'
        },
        {
          id: 'resource_limits',
          text: '单次操作不得超过预设的资源限制（时间、内存、文件大小）',
          severity: 'high',
          category: 'resource'
        },
        {
          id: 'audit_trail',
          text: '所有操作必须留下可追溯的审计日志',
          severity: 'high',
          category: 'governance'
        },
        {
          id: 'rollback_capability',
          text: '任何修改必须保留回滚能力或原始副本',
          severity: 'medium',
          category: 'safety'
        },
        {
          id: 'transparency',
          text: '操作意图和预期结果必须对用户透明',
          severity: 'medium',
          category: 'governance'
        },
        {
          id: 'incremental_progress',
          text: '优先选择小步迭代而非大步冒险',
          severity: 'low',
          category: 'strategy'
        }
      ],
      // Operation-specific constraints
      operationConstraints: {
        // Operations that require explicit user confirmation
        destructive: ['delete_file', 'delete_directory', 'cleanRecordedIssues'],
        // Operations that have resource limits
        resourceLimited: {
          maxFileSize: 50 * 1024 * 1024, // 50MB
          maxExecutionTime: 300000,       // 5 minutes
          maxMemoryMB: 512
        }
      }
    };
  }

  loadPrinciples() {
    // Try to load from file, fallback to defaults
    if (fs.existsSync(this.configFile)) {
      try {
        return JSON.parse(fs.readFileSync(this.configFile, 'utf8'));
      } catch {
        return this.getDefaultPrinciples();
      }
    }
    return this.getDefaultPrinciples();
  }

  save() {
    const dir = path.dirname(this.configFile);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(this.configFile, JSON.stringify(this.principles, null, 2));
  }

  /**
   * Get all principles
   */
  getPrinciples() {
    return this.principles.principles;
  }

  /**
   * Get principles by category
   */
  getPrinciplesByCategory(category) {
    return this.principles.principles.filter(p => p.category === category);
  }

  /**
   * Get principles by severity
   */
  getPrinciplesBySeverity(severity) {
    return this.principles.principles.filter(p => p.severity === severity);
  }

  /**
   * Check if a principle is violated
   */
  isViolated(principleId) {
    const principle = this.principles.principles.find(p => p.id === principleId);
    return principle ? true : false;
  }

  /**
   * Get operation constraints
   */
  getOperationConstraints() {
    return this.principles.operationConstraints || {};
  }

  /**
   * Check if operation is destructive (requires confirmation)
   */
  isDestructive(operationId) {
    const constraints = this.getOperationConstraints();
    return constraints.destructive?.includes(operationId) || false;
  }

  /**
   * Get resource limits for operations
   */
  getResourceLimits() {
    const constraints = this.getOperationConstraints();
    return constraints.resourceLimited || {
      maxFileSize: 50 * 1024 * 1024,
      maxExecutionTime: 300000,
      maxMemoryMB: 512
    };
  }

  /**
   * Validate an operation against all principles
   * Returns { valid: boolean, violations: string[] }
   */
  validate(operation) {
    const violations = [];

    for (const principle of this.principles.principles) {
      if (this.checkPrincipleViolation(principle, operation)) {
        violations.push({
          principleId: principle.id,
          text: principle.text,
          severity: principle.severity
        });
      }
    }

    return {
      valid: violations.length === 0,
      violations
    };
  }

  /**
   * Check if a specific principle is violated by an operation
   * Override this in subclasses for custom checks
   */
  checkPrincipleViolation(principle, operation) {
    // Default implementation - no violations
    // Subclasses can override for specific checks
    return false;
  }

  /**
   * Add a new principle (for dynamic loading, but core principles cannot be removed)
   */
  addPrinciple(principle) {
    // Core principles cannot be added if they would conflict with critical principles
    if (principle.severity === 'critical') {
      const existing = this.principles.principles.find(
        p => p.category === principle.category && p.severity === 'critical'
      );
      if (existing) {
        console.warn(`[Constitution] Cannot override critical principle in category ${principle.category}`);
        return false;
      }
    }

    this.principles.principles.push(principle);
    this.save();
    return true;
  }
}

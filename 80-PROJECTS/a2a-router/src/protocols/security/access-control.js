export class AccessControl {
  constructor(securityManager, options = {}) {
    this.securityManager = securityManager;
    this.acl = new Map(); // capability -> { allowed: Set, denied: Set }
    this.defaultAclPolicy = options.defaultAclPolicy || 'allow';
  }

  setRule(capability, allowedAgents = [], deniedAgents = []) {
    const key = capability.replace('capability:', '');
    this.acl.set(key, {
      allowed: new Set(allowedAgents),
      denied: new Set(deniedAgents)
    });
  }

  checkPermission(fromAgent, toTarget) {
    // Direct agent-to-agent: always allow
    if (!toTarget.startsWith('capability:')) {
      return true;
    }

    const capability = toTarget.replace('capability:', '');
    const rule = this.acl.get(capability);

    if (!rule) {
      return this.defaultAclPolicy === 'allow';
    }

    // Denied takes precedence
    if (rule.denied.has(fromAgent)) {
      return false;
    }

    // Empty allowed means allow everyone
    if (rule.allowed.size === 0) {
      return true;
    }

    return rule.allowed.has(fromAgent);
  }
}

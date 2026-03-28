import { AccessControl } from '../../src/protocols/security/access-control.js';

describe('AccessControl', () => {
  let ac;

  beforeEach(() => {
    ac = new AccessControl(null, { defaultAclPolicy: 'allow' });
  });

  test('allows direct agent-to-agent by default', () => {
    expect(ac.checkPermission('agent-1', 'agent-2')).toBe(true);
  });

  test('allows when no rules exist (default policy allow)', () => {
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(true);
  });

  test('denies when no rules exist (default policy deny)', () => {
    ac = new AccessControl(null, { defaultAclPolicy: 'deny' });
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(false);
  });

  test('respects allowed list', () => {
    ac.setRule('capability:coding', ['agent-1']);
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(true);
    expect(ac.checkPermission('agent-2', 'capability:coding')).toBe(false);
  });

  test('respects denied list', () => {
    ac.setRule('capability:coding', [], ['agent-2']);
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(true);
    expect(ac.checkPermission('agent-2', 'capability:coding')).toBe(false);
  });

  test('denied takes precedence over allowed', () => {
    ac.setRule('capability:coding', ['agent-1', 'agent-2'], ['agent-1']);
    expect(ac.checkPermission('agent-1', 'capability:coding')).toBe(false);
    expect(ac.checkPermission('agent-2', 'capability:coding')).toBe(true);
  });

  test('empty allowed means allow everyone', () => {
    ac.setRule('capability:coding', []);
    expect(ac.checkPermission('anyone', 'capability:coding')).toBe(true);
  });
});

import { TaskDecomposer } from '../../src/protocols/task-decomposition/task-decomposer.js';

describe('TaskDecomposer', () => {
  let decomposer;

  beforeEach(() => {
    decomposer = new TaskDecomposer();
  });

  test('decompose() splits by common delimiters', () => {
    const subtasks = decomposer.decompose('实现登录. 实现注册, 测试功能', {
      strategy: 'parallel',
      capabilities: ['coding', 'test'],
      maxSubTasks: 5
    });
    expect(subtasks.length).toBe(3);
  });

  test('decompose() respects maxSubTasks limit', () => {
    const subtasks = decomposer.decompose('a,b,c,d,e,f,g', {
      strategy: 'parallel',
      capabilities: ['coding'],
      maxSubTasks: 3
    });
    expect(subtasks.length).toBe(3);
  });

  test('inferCapability() detects coding keywords', () => {
    expect(decomposer.inferCapability('实现登录功能')).toBe('coding');
    expect(decomposer.inferCapability('build user API')).toBe('coding');
    expect(decomposer.inferCapability('create file')).toBe('coding');
  });

  test('inferCapability() detects review keywords', () => {
    expect(decomposer.inferCapability('审查代码')).toBe('review');
    expect(decomposer.inferCapability('check security')).toBe('review');
  });

  test('inferCapability() detects test keywords', () => {
    expect(decomposer.inferCapability('测试功能')).toBe('test');
    expect(decomposer.inferCapability('run tests')).toBe('test');
  });

  test('inferCapability() defaults to coding', () => {
    expect(decomposer.inferCapability('do something')).toBe('coding');
  });

  test('extractActions() handles mixed delimiters', () => {
    const actions = decomposer.extractActions('实现登录;实现注册\n测试功能');
    expect(actions).toHaveLength(3);
  });
});

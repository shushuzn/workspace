export class TaskDecomposer {
  decompose(taskDescription, options) {
    const { strategy, capabilities, maxSubTasks } = options;
    const subtasks = [];
    const actions = this.extractActions(taskDescription);

    for (const action of actions) {
      const capability = this.inferCapability(action);
      subtasks.push({
        capability,
        description: action,
        priority: 'NORMAL'
      });
    }

    return subtasks.slice(0, maxSubTasks);
  }

  extractActions(description) {
    return description
      .split(/[,，.。;；\n]/)
      .map(s => s.trim())
      .filter(s => s.length > 0);
  }

  inferCapability(action) {
    const coding = ['实现', '构建', '开发', '编写', 'create', 'implement', 'build'];
    const review = ['审查', '检查', 'review', 'check'];
    const test = ['测试', 'test'];

    const lower = action.toLowerCase();
    if (coding.some(k => lower.includes(k))) return 'coding';
    if (review.some(k => lower.includes(k))) return 'review';
    if (test.some(k => lower.includes(k))) return 'test';
    return 'coding';
  }
}

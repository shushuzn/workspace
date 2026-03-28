import { MessageStore } from '../../src/protocols/persistence/message-store.js';

describe('MessageStore', () => {
  let store;

  test('initializes with messages table', () => {
    store = new MessageStore(':memory:');
    const result = store.getDatabase().prepare(
      "SELECT name FROM sqlite_master WHERE type='table' AND name='messages'"
    ).get();
    expect(result.name).toBe('messages');
    store.close();
  });

  test('save() inserts message and returns id', () => {
    store = new MessageStore(':memory:');
    const msg = {
      id: 'msg-1',
      from: 'agent-a',
      to: 'agent-b',
      type: 'TASK',
      priority: 'NORMAL',
      payload: JSON.stringify({ data: 'hello' }),
      timestamp: Date.now()
    };
    const result = store.save(msg);
    expect(result.success).toBe(true);
    expect(result.id).toBe('msg-1');
    store.close();
  });

  test('findByAgent() returns messages for agent as sender', () => {
    store = new MessageStore(':memory:');
    store.save({ id: 'm1', from: 'a', to: 'b', type: 'TASK', payload: '{}', timestamp: Date.now() });
    store.save({ id: 'm2', from: 'b', to: 'a', type: 'RESPONSE', payload: '{}', timestamp: Date.now() });
    const results = store.findByAgent('a', { limit: 10 });
    expect(results.length).toBe(2); // both m1 (from) and m2 (to)
    store.close();
  });

  test('findById() returns single message', () => {
    store = new MessageStore(':memory:');
    store.save({ id: 'unique-1', from: 'a', to: 'b', type: 'TASK', payload: '{}', timestamp: Date.now() });
    const msg = store.findById('unique-1');
    expect(msg.id).toBe('unique-1');
    store.close();
  });

  test('archive() deletes old messages', () => {
    store = new MessageStore(':memory:');
    const oldTs = Date.now() - 100000;
    store.save({ id: 'old-1', from: 'a', to: 'b', type: 'TASK', payload: '{}', timestamp: oldTs - 1 }); // clearly older
    store.save({ id: 'new-1', from: 'a', to: 'b', type: 'TASK', payload: '{}', timestamp: Date.now() });
    const deleted = store.archive(oldTs);
    expect(deleted).toBe(1);
    expect(store.findById('old-1')).toBeUndefined();
    expect(store.findById('new-1').id).toBe('new-1');
    store.close();
  });
});

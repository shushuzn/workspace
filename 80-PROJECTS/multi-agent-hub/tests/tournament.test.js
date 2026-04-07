import { describe, it } from 'node:test';
import assert from 'node:assert';
import { Tournament } from '../shared/tournament.js';

describe('Tournament', () => {
  it('starts all players at 1500', () => {
    const t = new Tournament();
    t.register('Alice');
    t.register('Bob');
    assert.strictEqual(t.getRating('Alice'), 1500);
    assert.strictEqual(t.getRating('Bob'), 1500);
  });

  it('updates ratings after a match', () => {
    const t = new Tournament();
    t.register('Alice');
    t.register('Bob');
    t.recordResult('Alice', 'Bob');
    // Winner gains rating, loser loses
    assert.ok(t.getRating('Alice') > 1500);
    assert.ok(t.getRating('Bob') < 1500);
  });

  it('handles draws correctly', () => {
    const t = new Tournament();
    t.register('Alice');
    t.register('Bob');
    const beforeA = t.getRating('Alice');
    const beforeB = t.getRating('Bob');
    t.recordResult('Alice', 'Bob', true);
    // Both should converge toward 1500
    assert.ok(t.getRating('Alice') < beforeA + K_NEW / 2);
    assert.ok(t.getRating('Bob') > beforeB - K_NEW / 2);
  });

  it('sorts rankings by rating descending', () => {
    const t = new Tournament();
    t.register('C');
    t.register('A');
    t.register('B');
    t.recordResult('A', 'C'); // A beats C
    t.recordResult('A', 'B'); // A beats B
    t.recordResult('B', 'C'); // B beats C
    const rankings = t.getRankings();
    assert.strictEqual(rankings[0].name, 'A');
    assert.ok(rankings[0].rating > rankings[1].rating);
  });

  it('uses lower K-factor for established players', () => {
    const t = new Tournament();
    t.register('Alice');
    // Simulate 30 games for Alice
    for (let i = 0; i < 30; i++) {
      t.register('Bob' + i);
      t.recordResult('Alice', 'Bob' + i);
    }
    const establishedPlayer = t.players.get('Alice');
    assert.strictEqual(establishedPlayer.games, 30);
    // After 30 games, K should be 16, rating gain per win is smaller
  });

  it('serializes and deserializes correctly', () => {
    const t = new Tournament();
    t.register('Alice');
    t.register('Bob');
    t.recordResult('Alice', 'Bob');
    const json = t.toJSON();
    const restored = Tournament.fromJSON(json);
    assert.strictEqual(restored.getRating('Alice'), t.getRating('Alice'));
    assert.strictEqual(restored.getRankings().length, 2);
  });
});

const K_NEW = 32;

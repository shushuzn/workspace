/**
 * SqliteCheckpointSaver — LangGraph CheckpointSaver backed by SQLite.
 *
 * Persists agent conversation state across restarts.
 * Uses better-sqlite3 (already a project dependency).
 *
 * Schema:
 *   checkpoints(thread_id TEXT, checkpoint_id TEXT, checkpoint_json TEXT,
 *              metadata_json TEXT, PRIMARY KEY(thread_id, checkpoint_id))
 *   pending_writes(thread_id TEXT, task_id TEXT, idx INTEGER,
 *                 write_json TEXT, PRIMARY KEY(thread_id, task_id, idx))
 */

import Database from 'better-sqlite3';
import { randomUUID } from 'crypto';
import { mkdirSync } from 'fs';
import { dirname } from 'path';

export class SqliteCheckpointSaver {
  /**
   * @param {string} dbPath - Path to SQLite file (':memory:' for RAM)
   */
  constructor(dbPath = './data/checkpoints.db') {
    if (dbPath !== ':memory:') {
      const dir = dirname(dbPath);
      if (dir) mkdirSync(dir, { recursive: true });
    }
    this.db = new Database(dbPath);
    this._initSchema();
  }

  _initSchema() {
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS checkpoints (
        thread_id    TEXT NOT NULL,
        checkpoint_id TEXT NOT NULL,
        checkpoint_json TEXT NOT NULL,
        metadata_json  TEXT,
        PRIMARY KEY (thread_id, checkpoint_id)
      );

      CREATE TABLE IF NOT EXISTS pending_writes (
        thread_id  TEXT NOT NULL,
        task_id   TEXT NOT NULL,
        idx       INTEGER NOT NULL,
        write_json TEXT NOT NULL,
        PRIMARY KEY (thread_id, task_id, idx)
      );

      CREATE INDEX IF NOT EXISTS idx_checkpoints_thread
        ON checkpoints(thread_id);
    `);
  }

  /**
   * Extract thread_id from config
   */
  _threadId(config) {
    return config?.configurable?.thread_id;
  }

  /**
   * Serialize a LangChain message to JSON-safe plain object.
   */
  _serialize(value) {
    if (!value) return null;
    if (typeof value === 'function') return null;
    if (typeof value !== 'object') return value;
    // Handle ToolMessage, AIMessage, HumanMessage etc.
    if (value.constructor && value.constructor.name !== 'Object') {
      return {
        _type: value.constructor.name,
        ...value,
        // strip non-serializable fields
        lc: undefined,
        id: undefined,
      };
    }
    return value;
  }

  /**
   * Deserialize plain object back to LangChain message.
   */
  _deserialize(obj) {
    if (!obj || typeof obj !== 'object') return obj;
    return obj;
  }

  // ── Checkpointer interface ──────────────────────────────────────────────

  async getTuple(config) {
    const threadId = this._threadId(config);
    if (!threadId) return undefined;

    const row = this.db.prepare(`
      SELECT checkpoint_json, metadata_json, checkpoint_id
        FROM checkpoints
       WHERE thread_id = ?
       ORDER BY checkpoint_id DESC
       LIMIT 1
    `).get(threadId);

    if (!row) return undefined;

    let checkpoint;
    try {
      checkpoint = JSON.parse(row.checkpoint_json, (k, v) => this._revive(k, v));
    } catch {
      checkpoint = JSON.parse(row.checkpoint_json);
    }

    const metadata = row.metadata_json ? JSON.parse(row.metadata_json) : undefined;

    return {
      config: { configurable: { thread_id: threadId, checkpoint_id: row.checkpoint_id } },
      checkpoint,
      metadata,
      pendingWrites: await this._getPendingWrites(threadId),
    };
  }

  _revive(key, value) {
    // Revive known message types
    if (key === '_type' && typeof value === 'string') {
      return value; // placeholder — caller restores types
    }
    return value;
  }

  async *_list(config, limit = 100) {
    const threadId = this._threadId(config);
    if (!threadId) return;

    const rows = this.db.prepare(`
      SELECT checkpoint_id, checkpoint_json, metadata_json
        FROM checkpoints
       WHERE thread_id = ?
       ORDER BY checkpoint_id DESC
       LIMIT ?
    `).all(threadId, limit);

    for (const row of rows) {
      let checkpoint;
      try {
        checkpoint = JSON.parse(row.checkpoint_json);
      } catch {
        checkpoint = row.checkpoint_json;
      }

      yield {
        config: { configurable: { thread_id: threadId, checkpoint_id: row.checkpoint_id } },
        checkpoint,
        metadata: row.metadata_json ? JSON.parse(row.metadata_json) : undefined,
        pendingWrites: [],
      };
    }
  }

  async list(config, limit) {
    const results = [];
    for await (const tuple of this._list(config, limit)) {
      results.push(tuple);
    }
    return results;
  }

  async put(config, checkpoint, metadata) {
    const threadId = this._threadId(config);
    const checkpointId = config?.configurable?.checkpoint_id || String(Date.now());

    const stmt = this.db.prepare(`
      INSERT OR REPLACE INTO checkpoints (thread_id, checkpoint_id, checkpoint_json, metadata_json)
      VALUES (?, ?, ?, ?)
    `);

    stmt.run(
      threadId,
      checkpointId,
      JSON.stringify(checkpoint),
      metadata ? JSON.stringify(metadata) : null
    );

    return {
      configurable: { thread_id: threadId, checkpoint_id: checkpointId }
    };
  }

  async deleteThread(threadId) {
    this.db.prepare('DELETE FROM checkpoints WHERE thread_id = ?').run(threadId);
    this.db.prepare('DELETE FROM pending_writes WHERE thread_id = ?').run(threadId);
  }

  async putWrites(config, writes, taskId) {
    const threadId = this._threadId(config);
    if (!threadId) return;

    const insert = this.db.prepare(`
      INSERT INTO pending_writes (thread_id, task_id, idx, write_json)
      VALUES (?, ?, ?, ?)
    `);

    const insertMany = this.db.transaction((entries) => {
      entries.forEach(([idx, write]) => {
        insert.run(threadId, taskId, idx, JSON.stringify(write));
      });
    });

    insertMany(writes.map((w, i) => [i, w]));
  }

  async _getPendingWrites(threadId) {
    const rows = this.db.prepare(`
      SELECT idx, write_json FROM pending_writes
       WHERE thread_id = ?
       ORDER BY idx
    `).all(threadId);

    return rows.map(r => {
      let write;
      try { write = JSON.parse(r.write_json); } catch { write = r.write_json; }
      return write;
    });
  }

  getNextVersion(current) {
    if (typeof current === 'string') throw new Error('SqliteCheckpointSaver does not support string versions');
    return current !== undefined && typeof current === 'number' ? current + 1 : 1;
  }

  close() {
    this.db.close();
  }
}

export default SqliteCheckpointSaver;

import Database from 'better-sqlite3';

export class MessageStore {
  constructor(dbPath = './messages.db') {
    this.db = new Database(dbPath);
    this.maxPending = 1000;
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS messages (
        id TEXT PRIMARY KEY,
        from_agent TEXT NOT NULL,
        to_agent TEXT NOT NULL,
        type TEXT NOT NULL,
        priority TEXT DEFAULT 'NORMAL',
        payload TEXT NOT NULL,
        timestamp INTEGER NOT NULL,
        delivered_at INTEGER
      )
    `);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_messages_from ON messages(from_agent)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_messages_to ON messages(to_agent)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_messages_timestamp ON messages(timestamp)`);

    // Task persistence table
    this.db.exec(`
      CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        from_agent TEXT NOT NULL,
        to_agent TEXT NOT NULL,
        type TEXT NOT NULL,
        priority TEXT DEFAULT 'NORMAL',
        payload TEXT NOT NULL,
        status TEXT DEFAULT 'pending',
        result TEXT,
        created_at INTEGER NOT NULL,
        updated_at INTEGER NOT NULL,
        completed_at INTEGER
      )
    `);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status)`);
    this.db.exec(`CREATE INDEX IF NOT EXISTS idx_tasks_created ON tasks(created_at)`);
  }

  getDatabase() { return this.db; }

  save(message) {
    try {
      const stmt = this.db.prepare(`
        INSERT INTO messages (id, from_agent, to_agent, type, priority, payload, timestamp, delivered_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
      `);
      stmt.run(
        message.id,
        message.from,
        message.to,
        message.type,
        message.priority || 'NORMAL',
        typeof message.payload === 'string' ? message.payload : JSON.stringify(message.payload),
        message.timestamp,
        message.delivered_at || null
      );
      return { success: true, id: message.id };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  findByAgent(agentId, options = {}) {
    const { limit = 100, since, until } = options;
    let sql = `SELECT * FROM messages WHERE (from_agent = ? OR to_agent = ?)`;
    const params = [agentId, agentId];
    if (since !== undefined) {
      sql += ` AND timestamp >= ?`;
      params.push(since);
    }
    if (until !== undefined) {
      sql += ` AND timestamp <= ?`;
      params.push(until);
    }
    sql += ` ORDER BY timestamp DESC LIMIT ?`;
    params.push(limit);
    const stmt = this.db.prepare(sql);
    return stmt.all(...params);
  }

  findById(id) {
    const stmt = this.db.prepare('SELECT * FROM messages WHERE id = ?');
    return stmt.get(id);
  }

  archive(olderThan) {
    const stmt = this.db.prepare('DELETE FROM messages WHERE timestamp < ?');
    const result = stmt.run(olderThan);
    return result.changes;
  }

  close() { this.db.close(); }

  // ── Task Persistence ───────────────────────────────────────────────────────

  saveTask(task) {
    try {
      const stmt = this.db.prepare(`
        INSERT OR REPLACE INTO tasks (id, from_agent, to_agent, type, priority, payload, status, result, created_at, updated_at, completed_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
      `);
      stmt.run(
        task.id,
        task.from,
        task.to,
        task.type,
        task.priority || 'NORMAL',
        typeof task.payload === 'string' ? task.payload : JSON.stringify(task.payload),
        task.status || 'pending',
        task.result || null,
        task.created_at || Date.now(),
        task.updated_at || Date.now(),
        task.completed_at || null
      );
      return { success: true, id: task.id };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  updateTaskStatus(taskId, status, result = null) {
    try {
      const stmt = this.db.prepare(`
        UPDATE tasks SET status = ?, result = ?, updated_at = ?, completed_at = ?
        WHERE id = ?
      `);
      const now = Date.now();
      stmt.run(status, result ? (typeof result === 'string' ? result : JSON.stringify(result)) : null, now, status === 'completed' || status === 'failed' ? now : null, taskId);
      return { success: true };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  findPendingTasks(limit = 100) {
    const stmt = this.db.prepare(`SELECT * FROM tasks WHERE status IN ('pending','running') ORDER BY created_at ASC LIMIT ?`);
    return stmt.all(limit);
  }

  loadTasks() {
    return this.findPendingTasks(this.maxPending || 1000);
  }
}

import Database from 'better-sqlite3';

export class MessageStore {
  constructor(dbPath = './messages.db') {
    this.db = new Database(dbPath);
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
}

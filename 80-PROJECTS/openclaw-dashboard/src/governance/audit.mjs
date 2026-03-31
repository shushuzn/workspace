/**
 * Audit (Governance Layer)
 * Immutable audit trail for all operations
 */

import fs from 'fs';
import path from 'path';
import crypto from 'crypto';

export class Audit {
  constructor(workspace) {
    this.workspace = workspace;
    this.auditDir = path.join(workspace, '.omc', 'audit');
    this.ensureAuditDir();
  }

  ensureAuditDir() {
    if (!fs.existsSync(this.auditDir)) {
      fs.mkdirSync(this.auditDir, { recursive: true });
    }
  }

  /**
   * Create an immutable audit record
   */
  createRecord(type, data) {
    const record = {
      id: this.generateId(),
      type,
      data,
      timestamp: Date.now(),
      hash: null // Will be calculated
    };

    // Calculate hash for integrity
    record.hash = this.calculateHash(record);

    // Store in append-only file (current month)
    const monthFile = this.getMonthFile();
    this.appendRecord(monthFile, record);

    // Also store individual record
    const recordFile = path.join(this.auditDir, `${record.id}.json`);
    fs.writeFileSync(recordFile, JSON.stringify(record, null, 2));

    return record;
  }

  calculateHash(record) {
    // Create hash of record data (excluding hash field itself)
    const { hash, ...recordWithoutHash } = record;
    const content = JSON.stringify(recordWithoutHash);
    return crypto.createHash('sha256').update(content).digest('hex').substring(0, 16);
  }

  getMonthFile() {
    const now = new Date();
    const year = now.getFullYear();
    const month = String(now.getMonth() + 1).padStart(2, '0');
    return path.join(this.auditDir, `audit-${year}-${month}.jsonl`);
  }

  appendRecord(file, record) {
    const line = JSON.stringify(record) + '\n';
    fs.appendFileSync(file, line);
  }

  generateId() {
    return `audit_${Date.now().toString(36)}_${crypto.randomBytes(4).toString('hex')}`;
  }

  /**
   * Query audit records
   */
  query(options = {}) {
    const {
      startTime = 0,
      endTime = Date.now(),
      types = null,
      limit = 100
    } = options;

    const records = [];
    const files = this.getAuditFiles(startTime, endTime);

    for (const file of files) {
      const fileRecords = this.readFileRecords(file);
      for (const record of fileRecords) {
        if (record.timestamp >= startTime && record.timestamp <= endTime) {
          if (!types || types.includes(record.type)) {
            records.push(record);
          }
        }
      }
    }

    // Sort by timestamp descending
    records.sort((a, b) => b.timestamp - a.timestamp);

    return records.slice(0, limit);
  }

  getAuditFiles(startTime, endTime) {
    const start = new Date(startTime);
    const end = new Date(endTime);
    const files = [];

    // Iterate through each month
    const current = new Date(start);
    while (current <= end) {
      const year = current.getFullYear();
      const month = String(current.getMonth() + 1).padStart(2, '0');
      const file = path.join(this.auditDir, `audit-${year}-${month}.jsonl`);
      if (fs.existsSync(file)) {
        files.push(file);
      }
      current.setMonth(current.getMonth() + 1);
    }

    return files;
  }

  readFileRecords(file) {
    const records = [];
    try {
      const content = fs.readFileSync(file, 'utf8');
      const lines = content.split('\n').filter(l => l.trim());
      for (const line of lines) {
        try {
          records.push(JSON.parse(line));
        } catch {}
      }
    } catch {}
    return records;
  }

  /**
   * Verify audit integrity
   */
  verify(recordId) {
    const recordFile = path.join(this.auditDir, `${recordId}.json`);
    if (!fs.existsSync(recordFile)) {
      return { valid: false, reason: 'Record file not found' };
    }

    const record = JSON.parse(fs.readFileSync(recordFile, 'utf8'));
    const expectedHash = this.calculateHash(record);

    if (record.hash !== expectedHash) {
      return { valid: false, reason: 'Hash mismatch - record may have been tampered' };
    }

    return { valid: true, record };
  }

  /**
   * Get audit statistics
   */
  getStats() {
    const files = fs.readdirSync(this.auditDir).filter(f => f.endsWith('.jsonl'));
    const stats = {
      totalRecords: 0,
      byType: {},
      months: files.length
    };

    for (const file of files) {
      const records = this.readFileRecords(path.join(this.auditDir, file));
      stats.totalRecords += records.length;

      for (const record of records) {
        stats.byType[record.type] = (stats.byType[record.type] || 0) + 1;
      }
    }

    return stats;
  }
}

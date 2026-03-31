/**
 * Candidate Pool (Learn Layer)
 * Stores candidate improvements with priority queue
 */

import fs from 'fs';
import path from 'path';

export class CandidatePool {
  constructor(workspace) {
    this.workspace = workspace;
    this.poolFile = path.join(workspace, '.omc', 'candidate-pool.json');
    this.pool = this.load();
  }

  load() {
    if (fs.existsSync(this.poolFile)) {
      try {
        return JSON.parse(fs.readFileSync(this.poolFile, 'utf8'));
      } catch {
        return { candidates: [], version: '1.0.0' };
      }
    }
    return { candidates: [], version: '1.0.0' };
  }

  save() {
    const dir = path.dirname(this.poolFile);
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true });
    }
    fs.writeFileSync(this.poolFile, JSON.stringify(this.pool, null, 2));
  }

  /**
   * Add a candidate improvement
   */
  add(candidate) {
    const entry = {
      id: this.generateId(),
      ...candidate,
      status: candidate.status || 'pending',
      priority: candidate.priority || 'medium',
      createdAt: Date.now(),
      updatedAt: Date.now(),
      attempts: 0,
      lastAttempt: null
    };

    this.pool.candidates.push(entry);
    this.reprioritize();
    this.save();

    return entry;
  }

  generateId() {
    return `candidate_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 7)}`;
  }

  /**
   * Reprioritize candidates based on various factors
   */
  reprioritize() {
    const now = Date.now();

    for (const candidate of this.pool.candidates) {
      if (candidate.status !== 'pending') continue;

      let score = 0;

      // Priority weight
      const priorityWeights = { high: 30, medium: 20, low: 10 };
      score += priorityWeights[candidate.priority] || 20;

      // Recency bonus - newer candidates get slight boost
      const ageHours = (now - candidate.createdAt) / (1000 * 60 * 60);
      if (ageHours < 24) score += 10;
      else if (ageHours < 72) score += 5;

      // Fewer attempts bonus
      score += Math.max(0, 10 - candidate.attempts);

      // Estimated impact weight (if provided)
      if (candidate.estimatedImpact) {
        score += candidate.estimatedImpact;
      }

      candidate.priorityScore = score;
    }

    // Sort by priority score (descending)
    this.pool.candidates.sort((a, b) => {
      if (a.status !== b.status) {
        const statusOrder = { pending: 0, evaluating: 1, approved: 2, rejected: 3 };
        return statusOrder[a.status] - statusOrder[b.status];
      }
      return (b.priorityScore || 0) - (a.priorityScore || 0);
    });
  }

  /**
   * Get next candidate to evaluate
   */
  getNext() {
    const pending = this.pool.candidates.filter(c => c.status === 'pending');
    return pending.length > 0 ? pending[0] : null;
  }

  /**
   * Get top N candidates
   */
  getTop(count = 5) {
    return this.pool.candidates
      .filter(c => c.status === 'pending')
      .slice(0, count);
  }

  /**
   * Mark candidate as being evaluated
   */
  markEvaluating(id) {
    const candidate = this.pool.candidates.find(c => c.id === id);
    if (candidate) {
      candidate.status = 'evaluating';
      candidate.attempts++;
      candidate.lastAttempt = Date.now();
      this.save();
    }
    return candidate;
  }

  /**
   * Approve a candidate
   */
  approve(id, result = {}) {
    const candidate = this.pool.candidates.find(c => c.id === id);
    if (candidate) {
      candidate.status = 'approved';
      candidate.approvedAt = Date.now();
      candidate.result = result;
      this.save();
    }
    return candidate;
  }

  /**
   * Reject a candidate
   */
  reject(id, reason = '') {
    const candidate = this.pool.candidates.find(c => c.id === id);
    if (candidate) {
      candidate.status = 'rejected';
      candidate.rejectedAt = Date.now();
      candidate.rejectReason = reason;
      this.save();
    }
    return candidate;
  }

  /**
   * Reset a candidate to pending for retry
   */
  reset(id) {
    const candidate = this.pool.candidates.find(c => c.id === id);
    if (candidate) {
      candidate.status = 'pending';
      candidate.updatedAt = Date.now();
      this.reprioritize();
      this.save();
    }
    return candidate;
  }

  /**
   * Get candidates by source
   */
  getBySource(source) {
    return this.pool.candidates.filter(c => c.source === source);
  }

  /**
   * Get candidates by type
   */
  getByType(type) {
    return this.pool.candidates.filter(c => c.type === type);
  }

  /**
   * Get statistics
   */
  getStats() {
    const stats = {
      total: this.pool.candidates.length,
      pending: 0,
      evaluating: 0,
      approved: 0,
      rejected: 0,
      byType: {},
      bySource: {}
    };

    for (const c of this.pool.candidates) {
      if (c.status === 'pending') stats.pending++;
      else if (c.status === 'evaluating') stats.evaluating++;
      else if (c.status === 'approved') stats.approved++;
      else if (c.status === 'rejected') stats.rejected++;

      stats.byType[c.type] = (stats.byType[c.type] || 0) + 1;
      stats.bySource[c.source] = (stats.bySource[c.source] || 0) + 1;
    }

    return stats;
  }

  /**
   * Prune old candidates (keep approved/recent)
   */
  prune(maxAge = 30 * 24 * 60 * 60 * 1000) {
    const cutoff = Date.now() - maxAge;
    const before = this.pool.candidates.length;

    this.pool.candidates = this.pool.candidates.filter(c => {
      // Keep approved candidates
      if (c.status === 'approved') return true;
      // Keep recent candidates
      if (c.createdAt > cutoff) return true;
      // Keep high priority
      if (c.priority === 'high') return true;
      return false;
    });

    const pruned = before - this.pool.candidates.length;
    if (pruned > 0) this.save();

    return { pruned, remaining: this.pool.candidates.length };
  }
}

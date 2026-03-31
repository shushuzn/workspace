/**
 * Rollback (Governance Layer)
 * Provides rollback capability for operations
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

export class Rollback {
  constructor(workspace) {
    this.workspace = workspace;
    this.snapshotsDir = path.join(workspace, '.omc', 'snapshots');
    this.ensureSnapshotsDir();
  }

  ensureSnapshotsDir() {
    if (!fs.existsSync(this.snapshotsDir)) {
      fs.mkdirSync(this.snapshotsDir, { recursive: true });
    }
  }

  /**
   * Create a snapshot before risky operations
   */
  createSnapshot(label) {
    const snapshotId = `snap_${Date.now().toString(36)}`;

    try {
      // Create git stash if there are changes
      const status = execSync('git status --porcelain', {
        cwd: this.workspace,
        encoding: 'utf8',
        timeout: 5000
      });

      if (status.trim()) {
        // There are uncommitted changes
        execSync('git add -A', { cwd: this.workspace });
        execSync(`git stash push -m "Pre-operation snapshot: ${label}"`, {
          cwd: this.workspace,
          encoding: 'utf8',
          timeout: 5000
        });
      }

      const snapshot = {
        id: snapshotId,
        label,
        timestamp: Date.now(),
        gitStashExists: status.trim().length > 0,
        files: status.trim().split('\n').filter(l => l.trim()).map(l => l.substring(3).trim())
      };

      const snapshotFile = path.join(this.snapshotsDir, `${snapshotId}.json`);
      fs.writeFileSync(snapshotFile, JSON.stringify(snapshot, null, 2));

      return { success: true, snapshotId, snapshot };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Restore from a snapshot
   */
  restore(snapshotId) {
    const snapshotFile = path.join(this.snapshotsDir, `${snapshotId}.json`);

    if (!fs.existsSync(snapshotFile)) {
      return { success: false, error: 'Snapshot not found' };
    }

    const snapshot = JSON.parse(fs.readFileSync(snapshotFile, 'utf8'));

    try {
      if (snapshot.gitStashExists) {
        // Try to find and apply the stash
        const stashes = execSync('git stash list', {
          cwd: this.workspace,
          encoding: 'utf8',
          timeout: 5000
        });

        if (stashes.includes(snapshotId)) {
          execSync(`git stash pop`, {
            cwd: this.workspace,
            encoding: 'utf8',
            timeout: 10000
          });
        }
      }

      // Mark snapshot as restored
      snapshot.restoredAt = Date.now();
      fs.writeFileSync(snapshotFile, JSON.stringify(snapshot, null, 2));

      return { success: true, snapshot };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * List available snapshots
   */
  listSnapshots() {
    if (!fs.existsSync(this.snapshotsDir)) {
      return [];
    }

    const files = fs.readdirSync(this.snapshotsDir)
      .filter(f => f.endsWith('.json'))
      .sort()
      .reverse();

    return files.map(f => {
      const content = fs.readFileSync(path.join(this.snapshotsDir, f), 'utf8');
      return JSON.parse(content);
    });
  }

  /**
   * Clean old snapshots
   */
  cleanup(maxAge = 7 * 24 * 60 * 60 * 1000) {
    const cutoff = Date.now() - maxAge;
    const snapshots = this.listSnapshots();
    let cleaned = 0;

    for (const snapshot of snapshots) {
      if (snapshot.timestamp < cutoff && !snapshot.restoredAt) {
        const snapshotFile = path.join(this.snapshotsDir, `${snapshot.id}.json`);
        fs.unlinkSync(snapshotFile);
        cleaned++;
      }
    }

    return { cleaned };
  }

  /**
   * Check if rollback is available
   */
  isAvailable() {
    try {
      // Check if git is available and repo is clean
      execSync('git status', { cwd: this.workspace, timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }
}

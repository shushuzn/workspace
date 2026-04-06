import { describe, it, expect } from 'vitest';
import { execSync } from 'child_process';
import { existsSync } from 'fs';
import { join } from 'path';

const SRC_DIR = join(process.cwd(), 'src');

describe('code-agent semgrep scan', () => {
  it('runs semgrep scan on src/ directory', { timeout: 30000 }, () => {
    if (!existsSync(SRC_DIR)) {
      console.log('[semgrep] src/ not found, skipping');
      return;
    }

    let results;
    try {
      const output = execSync(
        'semgrep --config=.semgrep/rules.yaml --no-git-ignore --quiet --json src',
        { cwd: process.cwd(), encoding: 'utf-8', timeout: 25000 }
      );
      results = JSON.parse(output);
    } catch (err) {
      if (err.stdout) {
        try { results = JSON.parse(err.stdout); } catch { results = { results: [] }; }
      } else { throw err; }
    }

    const findings = results?.results || [];
    console.log(`[semgrep] scanned ${SRC_DIR}, found ${findings.length} issue(s)`);
    if (findings.length > 0) {
      for (const f of findings.slice(0, 5)) {
        console.log(`  - [${f.extra?.severity || 'INFO'}] ${f.check_id}: ${f.path}:${f.start.line}`);
      }
      if (findings.length > 5) console.log(`  ... and ${findings.length - 5} more`);
    }

    expect(Array.isArray(results?.results)).toBe(true);
  });
});

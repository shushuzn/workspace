/**
 * Semgrep CLI Wrapper
 * 
 * Wraps Semgrep CLI for security scanning
 */

import { execSync } from 'child_process';

class SemgrepWrapper {
  constructor(options = {}) {
    this.timeout = options.timeout || 60000;
    this.configSets = options.configSets || [
      'p/security-audit',
      'p/owasp-top-ten',
      'p/javascript'
    ];
  }

  /**
   * Check if Semgrep is available
   */
  isAvailable() {
    try {
      execSync('semgrep --version', { encoding: 'utf-8', timeout: 5000 });
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Get Semgrep version
   */
  getVersion() {
    try {
      const result = execSync('semgrep --version', { encoding: 'utf-8', timeout: 5000 });
      return result.trim();
    } catch {
      return null;
    }
  }

  /**
   * Scan a single file
   */
  scanFile(filePath, options = {}) {
    const configs = options.configs || this.configSets;
    const configArgs = configs.map(c => `--config=${c}`).join(' ');
    
    const cmd = `semgrep ${configArgs} "${filePath}" --json --quiet --timeout 30`;
    
    try {
      const result = execSync(cmd, {
        encoding: 'utf-8',
        timeout: this.timeout,
        cwd: options.cwd || process.cwd(),
        shell: true
      });
      
      return this.parseResult(JSON.parse(result));
    } catch (error) {
      // Semgrep returns non-zero when findings found, but stdout has JSON
      if (error.stdout) {
        try {
          return this.parseResult(JSON.parse(error.stdout));
        } catch {
          return { success: false, error: 'Failed to parse Semgrep output' };
        }
      }
      return { success: false, error: error.message };
    }
  }

  /**
   * Scan a project directory
   */
  scanProject(projectPath, options = {}) {
    const configs = options.configs || this.configSets;
    const configArgs = configs.map(c => `--config=${c}`).join(' ');
    const excludeArgs = options.exclude 
      ? options.exclude.map(e => `--exclude="${e}"`).join(' ') 
      : '';
    
    const cmd = `semgrep ${configArgs} ${excludeArgs} "${projectPath}" --json --quiet --timeout 60`;
    
    try {
      const result = execSync(cmd, {
        encoding: 'utf-8',
        timeout: this.timeout * 5,
        cwd: projectPath,
        shell: true
      });
      
      return this.parseResult(JSON.parse(result));
    } catch (error) {
      if (error.stdout) {
        try {
          return this.parseResult(JSON.parse(error.stdout));
        } catch {
          return { success: false, error: 'Failed to parse Semgrep output' };
        }
      }
      return { success: false, error: error.message };
    }
  }

  /**
   * Parse Semgrep JSON output
   */
  parseResult(jsonResult) {
    const findings = [];
    
    for (const result of jsonResult.results || []) {
      findings.push({
        ruleId: result.check_id,
        message: result.extra?.message || result.check_id,
        severity: this.mapSeverity(result.extra?.severity),
        category: this.getCategory(result.check_id),
        location: {
          file: result.path,
          line: result.start?.line,
          column: result.start?.col,
          endLine: result.end?.line,
          endColumn: result.end?.col
        },
        code: result.extra?.lines || '',
        fix: result.extra?.fix || null,
        references: result.extra?.references || [],
        metadata: result.extra?.metadata || {}
      });
    }
    
    return {
      success: true,
      findings,
      summary: {
        total: findings.length,
        bySeverity: this.groupBy(findings, 'severity'),
        byCategory: this.groupBy(findings, 'category'),
        byRule: this.groupBy(findings, 'ruleId')
      },
      stats: jsonResult.stats || {}
    };
  }

  /**
   * Map Semgrep severity to standard
   */
  mapSeverity(severity) {
    const map = {
      'ERROR': 'ERROR',
      'WARNING': 'WARNING',
      'INFO': 'INFO'
    };
    return map[severity] || 'WARNING';
  }

  /**
   * Get category from rule ID
   */
  getCategory(ruleId) {
    if (ruleId.includes('security')) return 'security';
    if (ruleId.includes('owasp')) return 'security';
    if (ruleId.includes('cwe')) return 'security';
    if (ruleId.includes('correctness')) return 'correctness';
    if (ruleId.includes('performance')) return 'performance';
    if (ruleId.includes('style')) return 'style';
    return 'general';
  }

  /**
   * Group findings by field
   */
  groupBy(findings, field) {
    return findings.reduce((acc, f) => {
      const key = f[field];
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});
  }
}

export default SemgrepWrapper;
/**
 * Code Agent Core
 * 
 * Orchestrates Semgrep and Tree-sitter analysis
 */

import { SemgrepWrapper } from './analyzer/semgrepWrapper.js';
import { TreeSitterAnalyzer } from './analyzer/treeSitterAnalyzer.js';
import { ResultFormatter } from './reporter/resultFormatter.js';
import { MemoryStore } from './reporter/memoryStore.js';
import fs from 'fs';
import path from 'path';

class CodeAgent {
  constructor(options = {}) {
    this.semgrep = new SemgrepWrapper(options.semgrep);
    this.treeSitter = new TreeSitterAnalyzer();
    this.formatter = new ResultFormatter();
    this.memoryStore = options.memoryStore ? new MemoryStore(options.memoryStore) : null;
    
    this.lastResults = null;
    this.status = {
      initialized: true,
      semgrepAvailable: false,
      supportedLanguages: ['javascript', 'typescript', 'python']
    };
    
    // Check Semgrep availability
    this.checkSemgrep();
  }

  /**
   * Check if Semgrep is available
   */
  checkSemgrep() {
    this.status.semgrepAvailable = this.semgrep.isAvailable();
  }

  /**
   * Security scan using Semgrep
   */
  async securityScan(filePath, configs = null) {
    if (!this.status.semgrepAvailable) {
      return {
        success: false,
        error: 'Semgrep not available. Install with: pip install semgrep',
        findings: []
      };
    }

    try {
      const result = this.semgrep.scanFile(filePath, { configs });
      this.lastResults = { security: result };
      
      // Store to memory if available
      if (this.memoryStore && result.findings.length > 0) {
        await this.memoryStore.storeFindings('security', result.findings, filePath);
      }
      
      return result;
    } catch (error) {
      return { success: false, error: error.message, findings: [] };
    }
  }

  /**
   * Quality check using Tree-sitter
   */
  async qualityCheck(filePath, content = null) {
    try {
      // Read file if content not provided
      if (!content) {
        content = fs.readFileSync(filePath, 'utf-8');
      }

      const result = this.treeSitter.analyzeFile(filePath, content);
      this.lastResults = { quality: result };
      
      // Store to memory if available
      if (this.memoryStore && result.issues.length > 0) {
        await this.memoryStore.storeFindings('quality', result.issues, filePath);
      }
      
      return result;
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Full file analysis
   */
  async analyzeFile(filePath, options = {}) {
    const opts = {
      checkSecurity: options.checkSecurity !== false,
      checkQuality: options.checkQuality !== false,
      checkComplexity: options.checkComplexity !== false
    };

    const results = {
      file: filePath,
      timestamp: Date.now(),
      security: null,
      quality: null,
      success: true
    };

    try {
      // Read file content
      const content = fs.readFileSync(filePath, 'utf-8');
      const language = this.treeSitter.detectLanguage(filePath);

      if (!language) {
        results.success = false;
        results.error = 'Unsupported language';
        return results;
      }

      results.language = language;

      // Security scan (if Semgrep available)
      if (opts.checkSecurity && this.status.semgrepAvailable) {
        results.security = await this.securityScan(filePath);
      }

      // Quality check
      if (opts.checkQuality || opts.checkComplexity) {
        results.quality = this.treeSitter.analyzeFile(filePath, content);
      }

      // Merge findings
      const allFindings = [];
      if (results.security?.findings) allFindings.push(...results.security.findings);
      if (results.quality?.issues) allFindings.push(...results.quality.issues);

      results.findings = allFindings;
      results.summary = this.formatter.summarize(allFindings);
      
      this.lastResults = results;
      
      // Store to memory
      if (this.memoryStore && allFindings.length > 0) {
        await this.memoryStore.storeFindings('combined', allFindings, filePath);
      }

      return results;
    } catch (error) {
      return { success: false, error: error.message, file: filePath };
    }
  }

  /**
   * Project-wide scan
   */
  async scanProject(projectPath, excludePatterns = ['node_modules', '.git', 'dist', 'build']) {
    const results = {
      project: projectPath,
      timestamp: Date.now(),
      filesScanned: 0,
      findings: [],
      metrics: {},
      success: true
    };

    try {
      // Get all source files
      const files = this.getSourceFiles(projectPath, excludePatterns);
      results.filesScanned = files.length;

      // Scan each file
      for (const file of files) {
        const fileResult = await this.analyzeFile(file, {
          checkSecurity: this.status.semgrepAvailable,
          checkQuality: true
        });

        if (fileResult.findings) {
          results.findings.push(...fileResult.findings.map(f => ({
            ...f,
            file: file
          })));
        }

        if (fileResult.quality?.metrics) {
          results.metrics[file] = fileResult.quality.metrics;
        }
      }

      results.summary = this.formatter.summarize(results.findings);
      results.projectMetrics = this.calculateProjectMetrics(results.metrics);
      
      this.lastResults = results;
      
      return results;
    } catch (error) {
      return { success: false, error: error.message, project: projectPath };
    }
  }

  /**
   * Get source files in project
   */
  getSourceFiles(projectPath, excludePatterns) {
    const extensions = ['.js', '.jsx', '.ts', '.tsx', '.py'];
    const files = [];

    const walk = (dir) => {
      const entries = fs.readdirSync(dir, { withFileTypes: true });
      
      for (const entry of entries) {
        const fullPath = path.join(dir, entry.name);
        
        // Skip excluded patterns
        if (excludePatterns.some(p => fullPath.includes(p))) continue;
        
        if (entry.isDirectory()) {
          walk(fullPath);
        } else if (entry.isFile()) {
          const ext = path.extname(entry.name);
          if (extensions.includes(ext)) {
            files.push(fullPath);
          }
        }
      }
    };

    walk(projectPath);
    return files;
  }

  /**
   * Calculate project-level metrics
   */
  calculateProjectMetrics(fileMetrics) {
    const total = {
      complexity: 0,
      functions: 0,
      classes: 0,
      avgComplexity: 0,
      avgFunctionLength: 0
    };

    const files = Object.keys(fileMetrics);
    
    for (const file of files) {
      const m = fileMetrics[file];
      if (m.complexity) total.complexity += m.complexity.cyclomatic;
      if (m.structure) {
        total.functions += m.structure.functions;
        total.classes += m.structure.classes;
        total.avgFunctionLength += m.structure.avgFunctionLength;
      }
    }

    if (files.length > 0) {
      total.avgComplexity = Math.round(total.complexity / files.length);
      total.avgFunctionLength = Math.round(total.avgFunctionLength / files.length);
    }

    return total;
  }

  /**
   * Get metrics for a file
   */
  async getMetrics(filePath) {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      const result = this.treeSitter.analyzeFile(filePath, content);
      return {
        success: true,
        metrics: result.metrics,
        structure: result.structure
      };
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Get findings from last analysis
   */
  getFindings(severity = null) {
    if (!this.lastResults) {
      return { success: false, error: 'No analysis performed yet' };
    }

    let findings = [];
    if (this.lastResults.security?.findings) findings.push(...this.lastResults.security.findings);
    if (this.lastResults.quality?.issues) findings.push(...this.lastResults.quality.issues);
    if (this.lastResults.findings) findings = this.lastResults.findings;

    if (severity) {
      findings = findings.filter(f => f.severity === severity);
    }

    return {
      success: true,
      findings,
      total: findings.length
    };
  }

  /**
   * Get agent status
   */
  getStatus() {
    return {
      success: true,
      status: this.status,
      lastAnalysis: this.lastResults ? {
        file: this.lastResults.file || this.lastResults.project,
        timestamp: this.lastResults.timestamp,
        findingsCount: this.lastResults.findings?.length || 0
      } : null
    };
  }
}

export default CodeAgent;
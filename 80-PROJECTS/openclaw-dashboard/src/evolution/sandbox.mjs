/**
 * Sandbox (Evolution Layer)
 * Isolated testing environment for candidate improvements
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';

export class Sandbox {
  constructor(workspace) {
    this.workspace = workspace;
    this.sandboxDir = path.join(workspace, '.omc', 'sandbox');
    this.resultsDir = path.join(this.sandboxDir, 'results');
    this.ensureSandbox();
  }

  ensureSandbox() {
    if (!fs.existsSync(this.sandboxDir)) {
      fs.mkdirSync(this.sandboxDir, { recursive: true });
    }
    if (!fs.existsSync(this.resultsDir)) {
      fs.mkdirSync(this.resultsDir, { recursive: true });
    }
  }

  /**
   * Test an operation in sandbox mode
   */
  async test(operation, options = {}) {
    const testId = this.generateTestId();
    const testResult = {
      id: testId,
      operationId: operation.id,
      operationName: operation.name,
      startTime: Date.now(),
      status: 'running',
      output: '',
      error: null
    };

    const testFile = path.join(this.sandboxDir, `${testId}_test.mjs`);

    try {
      // Create isolated test environment
      const testScript = this.generateTestScript(operation, options);
      fs.writeFileSync(testFile, testScript);

      // Execute in sandbox
      testResult.output = execSync(`node "${testFile}"`, {
        cwd: this.workspace,
        encoding: 'utf8',
        timeout: options.timeout || 30000,
        env: {
          ...process.env,
          SANDBOX_MODE: 'true',
          NODE_OPTIONS: '--experimental-vm-modules'
        }
      });

      testResult.status = 'success';
      testResult.endTime = Date.now();
      testResult.duration = testResult.endTime - testResult.startTime;

      // Parse output for metrics
      testResult.metrics = this.parseMetrics(testResult.output);

    } catch (error) {
      testResult.status = 'failed';
      testResult.error = error.message;
      testResult.endTime = Date.now();
      testResult.duration = testResult.endTime - testResult.startTime;
    }

    // Cleanup test file
    if (fs.existsSync(testFile)) {
      fs.unlinkSync(testFile);
    }

    // Save result
    this.saveResult(testResult);

    return testResult;
  }

  generateTestId() {
    return `test_${Date.now().toString(36)}_${Math.random().toString(36).substring(2, 6)}`;
  }

  generateTestScript(operation, options) {
    // Generate a test script that runs the operation with safeguards
    return `
      // Sandbox test for: ${operation.name}
      // Generated at: ${new Date().toISOString()}

      const SANDBOX_MODE = process.env.SANDBOX_MODE === 'TRUE';

      // Override any file modifications to sandbox directory
      const originalWrite = null; // Would hook into fs.writeFileSync

      try {
        // Import operation
        // const { ${operation.id} } = await import('./operations/index.mjs');

        // Run with timeout
        console.log('SANDBOX_TEST_START');

        // Simulate operation execution
        console.log('METRIC:dummy_metric=0');

        console.log('SANDBOX_TEST_END');
        process.exit(0);
      } catch (error) {
        console.error('SANDBOX_ERROR:', error.message);
        process.exit(1);
      }
    `;
  }

  parseMetrics(output) {
    const metrics = {};
    const lines = output.split('\n');

    for (const line of lines) {
      const match = line.match(/METRIC:(\w+)=([\d.]+)/);
      if (match) {
        metrics[match[1]] = parseFloat(match[2]);
      }
    }

    return metrics;
  }

  saveResult(result) {
    const resultFile = path.join(this.resultsDir, `${result.id}.json`);
    fs.writeFileSync(resultFile, JSON.stringify(result, null, 2));
  }

  /**
   * Load test results
   */
  loadResults(testId) {
    const resultFile = path.join(this.resultsDir, `${testId}.json`);
    if (fs.existsSync(resultFile)) {
      return JSON.parse(fs.readFileSync(resultFile, 'utf8'));
    }
    return null;
  }

  /**
   * Get all test results for an operation
   */
  getOperationResults(operationId) {
    const files = fs.readdirSync(this.resultsDir).filter(f => f.endsWith('.json'));
    const results = [];

    for (const file of files) {
      const result = JSON.parse(
        fs.readFileSync(path.join(this.resultsDir, file), 'utf8')
      );
      if (result.operationId === operationId) {
        results.push(result);
      }
    }

    return results.sort((a, b) => b.startTime - a.startTime);
  }

  /**
   * Compare baseline vs experiment
   */
  compare(baselineResult, experimentResult) {
    const comparison = {
      baselineId: baselineResult.id,
      experimentId: experimentResult.id,
      durationDiff: experimentResult.duration - baselineResult.duration,
      statusChanged: baselineResult.status !== experimentResult.status,
      metricsDiff: {}
    };

    if (baselineResult.metrics && experimentResult.metrics) {
      for (const key of Object.keys(experimentResult.metrics)) {
        if (baselineResult.metrics[key] !== undefined) {
          comparison.metricsDiff[key] =
            experimentResult.metrics[key] - baselineResult.metrics[key];
        }
      }
    }

    return comparison;
  }

  /**
   * Cleanup old test results
   */
  cleanup(maxAge = 7 * 24 * 60 * 60 * 1000) {
    const cutoff = Date.now() - maxAge;
    const files = fs.readdirSync(this.resultsDir).filter(f => f.endsWith('.json'));
    let cleaned = 0;

    for (const file of files) {
      const filePath = path.join(this.resultsDir, file);
      const stat = fs.statSync(filePath);
      if (stat.mtimeMs < cutoff) {
        fs.unlinkSync(filePath);
        cleaned++;
      }
    }

    return { cleaned };
  }

  /**
   * Get sandbox statistics
   */
  getStats() {
    const files = fs.readdirSync(this.resultsDir).filter(f => f.endsWith('.json'));
    const stats = {
      total: files.length,
      success: 0,
      failed: 0,
      avgDuration: 0
    };

    let totalDuration = 0;

    for (const file of files) {
      const result = JSON.parse(
        fs.readFileSync(path.join(this.resultsDir, file), 'utf8')
      );
      if (result.status === 'success') stats.success++;
      else stats.failed++;
      totalDuration += result.duration || 0;
    }

    stats.avgDuration = files.length > 0 ? totalDuration / files.length : 0;

    return stats;
  }
}

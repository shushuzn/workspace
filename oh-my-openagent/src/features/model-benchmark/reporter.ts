/**
 * Benchmark Report Generator
 * Generates markdown reports from benchmark results
 */

import type { BenchmarkReport, BenchmarkTask, ModelResult } from './types'

export class BenchmarkReporter {
  generateReport(
    models: string[],
    tasks: BenchmarkTask[],
    results: Record<string, ModelResult[]>,
    durationMs: number
  ): BenchmarkReport {
    const summary = this.computeSummary(models, results)
    const report: BenchmarkReport = {
      date: new Date().toISOString().split('T')[0],
      models,
      tasks,
      results,
      summary
    }
    return report
  }

  toMarkdown(report: BenchmarkReport): string {
    const lines: string[] = [
      '# Model Benchmark Report',
      '',
      `**Date**: ${report.date}`,
      `**Duration**: ${(report.durationMs / 1000).toFixed(1)}s`,
      '',
      '## Summary',
      ''
    ]

    // By-model summary table
    lines.push('### By Model', '')
    lines.push('| Model | Avg Quality | Avg Latency (ms) | Avg Cost |')
    lines.push('|-------|-------------|-----------------|----------|')

    for (const [model, stats] of Object.entries(report.summary.byModel)) {
      lines.push(
        `| ${model} | ${stats.avgQuality.toFixed(2)} | ${stats.avgLatency.toFixed(0)} | ${stats.avgCost.toFixed(4)} |`
      )
    }

    lines.push('')

    // By-task-type summary
    lines.push('### By Task Type', '')
    lines.push('| Task Type | Avg Quality |')
    lines.push('|-----------|-------------|')

    for (const [taskType, stats] of Object.entries(report.summary.byTaskType)) {
      lines.push(`| ${taskType} | ${stats.avgQuality.toFixed(2)} |`)
    }

    lines.push('')

    // Recommendation
    lines.push('## Recommendation', '')
    lines.push(report.summary.recommendation)
    lines.push('')

    // Detailed results
    lines.push('## Detailed Results', '')

    for (const model of report.models) {
      const modelResults = report.results[model] ?? []
      lines.push(`### ${model}`, '')
      lines.push(`Total runs: ${modelResults.length}`, '')

      const taskGroups = this.groupByTask(modelResults)
      for (const [taskId, results] of Object.entries(taskGroups)) {
        const task = report.tasks.find(t => t.id === taskId)
        lines.push(`**${task?.name ?? taskId}** (${task?.taskType ?? 'unknown'})`)
        lines.push('')

        for (const r of results) {
          lines.push(
            `- Latency: ${r.latencyMs}ms | Tokens: ${r.tokensUsed} | Quality: ${r.quality.overall.toFixed(2)}`
          )
          if (r.output.length > 100) {
            lines.push(`  - Output: ${r.output.slice(0, 100)}...`)
          } else if (r.output) {
            lines.push(`  - Output: ${r.output}`)
          }
        }
        lines.push('')
      }
    }

    return lines.join('\n')
  }

  private computeSummary(
    models: string[],
    results: Record<string, ModelResult[]>
  ): BenchmarkReport['summary'] {
    const byModel: Record<string, { avgQuality: number; avgLatency: number; avgCost: number }> = {}
    const byTaskType: Record<string, { avgQuality: number }> = {}

    for (const model of models) {
      const modelResults = results[model] ?? []
      if (modelResults.length === 0) continue

      const totalLatency = modelResults.reduce((sum, r) => sum + r.latencyMs, 0)
      const totalQuality = modelResults.reduce((sum, r) => sum + r.quality.overall, 0)
      const avgLatency = totalLatency / modelResults.length
      const avgQuality = totalQuality / modelResults.length
      const avgCost = (avgLatency / 1000) * 0.01 // rough cost estimate

      byModel[model] = { avgQuality, avgLatency, avgCost }
    }

    // Group by task type
    for (const model of models) {
      const modelResults = results[model] ?? []
      for (const r of modelResults) {
        const task = r.taskId // would need task lookup for actual taskType
        // For now, skip task type grouping without task reference
      }
    }

    // Find best model
    let bestModel = models[0] ?? 'unknown'
    let bestScore = 0
    for (const [model, stats] of Object.entries(byModel)) {
      const score = stats.avgQuality / (stats.avgLatency / 1000)
      if (score > bestScore) {
        bestScore = score
        bestModel = model
      }
    }

    const recommendation = `**${bestModel}** offers the best quality/latency tradeoff. ` +
      `Consider using it for time-sensitive tasks.`

    return { byModel, byTaskType, recommendation }
  }

  private groupByTask(results: ModelResult[]): Record<string, ModelResult[]> {
    const groups: Record<string, ModelResult[]> = {}
    for (const r of results) {
      if (!groups[r.taskId]) groups[r.taskId] = []
      groups[r.taskId].push(r)
    }
    return groups
  }
}

export function createReporter(): BenchmarkReporter {
  return new BenchmarkReporter()
}

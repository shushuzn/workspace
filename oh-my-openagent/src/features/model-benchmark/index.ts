/**
 * Model Benchmark Suite
 * Unified entry point for running multi-model benchmarks
 */

import { createAdapter, type ModelAdapter } from './adapters'
import { createRunner, type RunnerConfig } from './runner'
import { createReporter, type BenchmarkReporter } from './reporter'
import type { BenchmarkTask, BenchmarkReport, ModelResult } from './types'

export interface BenchmarkConfig {
  providers: string[]
  models: Record<string, string>
  tasks: BenchmarkTask[]
  runner?: Partial<RunnerConfig>
}

export async function runBenchmark(config: BenchmarkConfig): Promise<BenchmarkReport> {
  const runner = createRunner(config.runner)
  const reporter = createReporter()

  // Create adapters for each provider
  const adapters: ModelAdapter[] = []
  for (const provider of config.providers) {
    const modelId = config.models[provider] ?? 'default'
    try {
      const adapter = createAdapter(provider, modelId)
      adapters.push(adapter)
    } catch (err) {
      console.warn(`Failed to create adapter for ${provider}:`, err)
    }
  }

  if (adapters.length === 0) {
    throw new Error('No valid adapters created')
  }

  const modelNames = adapters.map(a => `${a.provider}:${a.modelId}`)

  // Run benchmark
  const startTime = Date.now()
  const results: Record<string, ModelResult[]> = {}

  for (const adapter of adapters) {
    const modelKey = `${adapter.provider}:${adapter.modelId}`
    console.log(`Running ${modelKey}...`)

    const modelResults = await runner.runSingleModel(adapter, config.tasks, (done, total) => {
      process.stdout.write(`  ${done}/${total}\r`)
    })
    results[modelKey] = modelResults
    console.log(`  ${modelResults.length} results`)
  }

  const durationMs = Date.now() - startTime

  // Generate report
  const report = reporter.generateReport(modelNames, config.tasks, results, durationMs)

  return report
}

export function printReport(report: BenchmarkReport): void {
  const reporter = createReporter()
  console.log('\n' + reporter.toMarkdown(report))
}

// Re-export types and factories
export { createAdapter } from './adapters'
export { createRunner } from './runner'
export { createReporter } from './reporter'
export type { ModelAdapter } from './adapters'
export type { BenchmarkTask, BenchmarkReport, ModelResult, TaskType } from './types'

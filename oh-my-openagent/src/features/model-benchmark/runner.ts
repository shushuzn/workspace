/**
 * Concurrent Benchmark Runner
 * Runs multiple model adapters in parallel and collects results
 */

import { randomUUID } from 'crypto'
import type { ModelAdapter } from './adapters'
import type { BenchmarkTask, ModelResult } from './types'

export interface RunnerConfig {
  maxConcurrency: number
  maxRetries: number
  retryDelayMs: number
}

export class BenchmarkRunner {
  private config: RunnerConfig

  constructor(config: Partial<RunnerConfig> = {}) {
    this.config = {
      maxConcurrency: config.maxConcurrency ?? 3,
      maxRetries: config.maxRetries ?? 2,
      retryDelayMs: config.retryDelayMs ?? 1000
    }
  }

  async runTask(
    adapter: ModelAdapter,
    task: BenchmarkTask
  ): Promise<ModelResult> {
    let lastError: unknown

    for (let attempt = 0; attempt <= this.config.maxRetries; attempt++) {
      try {
        const result = await adapter.call(task.input.prompt, {
          taskId: task.id,
          taskType: task.taskType
        })

        return {
          modelId: adapter.modelId,
          taskId: task.id,
          output: result.output,
          latencyMs: result.latencyMs,
          tokensUsed: result.tokensUsed,
          timestamp: Date.now(),
          quality: {
            scores: {},
            overall: 0
          }
        }
      } catch (err) {
        lastError = err
        if (attempt < this.config.maxRetries) {
          await this.delay(this.config.retryDelayMs * (attempt + 1))
        }
      }
    }

    throw lastError ?? new Error('Benchmark run failed')
  }

  async runSuite(
    adapters: ModelAdapter[],
    tasks: BenchmarkTask[],
    onProgress?: (completed: number, total: number) => void
  ): Promise<ModelResult[]> {
    const results: ModelResult[] = []
    const total = adapters.length * tasks.length
    let completed = 0

    // Process in batches to control concurrency
    for (let i = 0; i < adapters.length; i += this.config.maxConcurrency) {
      const batch = adapters.slice(i, i + this.config.maxConcurrency)
      const batchResults = await Promise.all(
        batch.flatMap(adapter =>
          tasks.map(async task => {
            const result = await this.runTask(adapter, task)
            completed++
            onProgress?.(completed, total)
            return result
          })
        )
      )
      results.push(...batchResults)
    }

    return results
  }

  async runSingleModel(
    adapter: ModelAdapter,
    tasks: BenchmarkTask[],
    onProgress?: (completed: number, total: number) => void
  ): Promise<ModelResult[]> {
    const results: ModelResult[] = []
    const total = tasks.length
    let completed = 0

    for (const task of tasks) {
      const result = await this.runTask(adapter, task)
      results.push(result)
      completed++
      onProgress?.(completed, total)
    }

    return results
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

export function createRunner(config?: Partial<RunnerConfig>): BenchmarkRunner {
  return new BenchmarkRunner(config)
}

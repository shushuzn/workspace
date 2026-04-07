/**
 * Model Benchmark Types
 * Schema for defining benchmark tasks and result collection
 */

export type TaskType =
  | 'code-generation'
  | 'code-review'
  | 'reasoning'
  | 'creative-writing'
  | 'data-analysis'
  | 'translation'

export interface BenchmarkTask {
  id: string
  name: string
  taskType: TaskType
  description: string
  input: {
    prompt: string
    context?: Record<string, string>
  }
  expectedOutput: {
    criteria: string[]
    minScore?: number
  }
  metadata: {
    difficulty: 1 | 2 | 3 | 4 | 5
    estimatedTokens: number
    domain: string
  }
}

export interface ModelResult {
  modelId: string
  taskId: string
  output: string
  latencyMs: number
  tokensUsed: number
  timestamp: number
  quality: {
    scores: Record<string, number>
    overall: number
  }
}

export interface BenchmarkReport {
  date: string
  models: string[]
  tasks: BenchmarkTask[]
  results: Record<string, ModelResult[]>
  summary: {
    byModel: Record<string, { avgQuality: number; avgLatency: number; avgCost: number }>
    byTaskType: Record<string, { avgQuality: number }>
    recommendation: string
  }
}

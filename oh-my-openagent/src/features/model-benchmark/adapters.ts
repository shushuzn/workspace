/**
 * Model Adapters
 * Unified interface for calling different model providers
 */

import { randomUUID } from 'crypto'

export interface ModelAdapter {
  modelId: string
  provider: 'openai' | 'anthropic' | 'gemini' | 'ollama' | 'minimax'
  call(prompt: string, options?: Record<string, unknown>): Promise<{ output: string; latencyMs: number; tokensUsed: number }>
}

export class OpenAIAdapter implements ModelAdapter {
  modelId: string
  provider = 'openai' as const

  constructor(modelId = 'gpt-4o') {
    this.modelId = modelId
  }

  async call(prompt: string, options: Record<string, unknown> = {}): Promise<{ output: string; latencyMs: number; tokensUsed: number }> {
    const start = Date.now()
    // Placeholder: actual implementation would call OpenAI API
    const response = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENAI_API_KEY || ''}`
      },
      body: JSON.stringify({
        model: this.modelId,
        messages: [{ role: 'user', content: prompt }],
        ...options
      })
    })
    const data = await response.json() as { choices: Array<{ message: { content: string } }>; usage?: { total_tokens: number } }
    const latencyMs = Date.now() - start
    return {
      output: data.choices?.[0]?.message?.content || '',
      latencyMs,
      tokensUsed: data.usage?.total_tokens || 0
    }
  }
}

export class AnthropicAdapter implements ModelAdapter {
  modelId: string
  provider = 'anthropic' as const

  constructor(modelId = 'claude-sonnet-4') {
    this.modelId = modelId
  }

  async call(prompt: string, options: Record<string, unknown> = {}): Promise<{ output: string; latencyMs: number; tokensUsed: number }> {
    const start = Date.now()
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY || '',
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: this.modelId,
        messages: [{ role: 'user', content: prompt }],
        max_tokens: options.maxTokens as number || 1024
      })
    })
    const data = await response.json() as { content: Array<{ text: string }> }
    const latencyMs = Date.now() - start
    return {
      output: data.content?.[0]?.text || '',
      latencyMs,
      tokensUsed: 0
    }
  }
}

export class GeminiAdapter implements ModelAdapter {
  modelId: string
  provider = 'gemini' as const

  constructor(modelId = 'gemini-2.0-flash') {
    this.modelId = modelId
  }

  async call(prompt: string, options: Record<string, unknown> = {}): Promise<{ output: string; latencyMs: number; tokensUsed: number }> {
    const start = Date.now()
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/${this.modelId}:generateContent?key=${process.env.GEMINI_API_KEY || ''}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ contents: [{ parts: [{ text: prompt }] }] })
    })
    const data = await response.json() as { candidates?: Array<{ content?: { parts?: Array<{ text?: string }> } }> }
    const latencyMs = Date.now() - start
    return {
      output: data.candidates?.[0]?.content?.parts?.[0]?.text || '',
      latencyMs,
      tokensUsed: 0
    }
  }
}

export class OllamaAdapter implements ModelAdapter {
  modelId: string
  provider = 'ollama' as const
  baseUrl: string

  constructor(modelId = 'llama3.2:1b', baseUrl = 'http://127.0.0.1:11434') {
    this.modelId = modelId
    this.baseUrl = baseUrl
  }

  async call(prompt: string, options: Record<string, unknown> = {}): Promise<{ output: string; latencyMs: number; tokensUsed: number }> {
    const start = Date.now()
    const response = await fetch(`${this.baseUrl}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: this.modelId, prompt, stream: false })
    })
    const data = await response.json() as { response?: string; eval_count?: number }
    const latencyMs = Date.now() - start
    return {
      output: data.response || '',
      latencyMs,
      tokensUsed: data.eval_count || 0
    }
  }
}

export class MiniMaxAdapter implements ModelAdapter {
  modelId: string
  provider = 'minimax' as const

  constructor(modelId = 'MiniMax-Text-01') {
    this.modelId = modelId
  }

  async call(prompt: string, options: Record<string, unknown> = {}): Promise<{ output: string; latencyMs: number; tokensUsed: number }> {
    const start = Date.now()
    const response = await fetch('https://api.minimaxi.com/v1/text/chatcompletion_v2', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.MINIMAX_API_KEY || ''}`
      },
      body: JSON.stringify({
        model: this.modelId,
        messages: [{ role: 'user', content: prompt }]
      })
    })
    const data = await response.json() as { choices?: Array<{ message?: { content?: string } }> }
    const latencyMs = Date.now() - start
    return {
      output: data.choices?.[0]?.message?.content || '',
      latencyMs,
      tokensUsed: 0
    }
  }
}

export function createAdapter(provider: string, modelId?: string): ModelAdapter {
  switch (provider) {
    case 'openai': return new OpenAIAdapter(modelId)
    case 'anthropic': return new AnthropicAdapter(modelId)
    case 'gemini': return new GeminiAdapter(modelId)
    case 'ollama': return new OllamaAdapter(modelId)
    case 'minimax': return new MiniMaxAdapter(modelId)
    default: throw new Error(`Unknown provider: ${provider}`)
  }
}

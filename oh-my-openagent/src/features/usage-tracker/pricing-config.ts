/**
 * Pricing Configuration Schema
 * Free/Pro/Team tiers with usage limits and pricing
 */

export type PricingTier = "free" | "pro" | "team"

export interface UsageRecord {
  userId: string
  model: string
  taskType: string
  tokens: number
  timestamp: string
  sessionId?: string
}

export interface PricingConfig {
  tiers: {
    [key in PricingTier]: {
      displayName: string
      monthlyPrice: number
      limits: {
        maxTokensPerMonth: number
        maxRequestsPerDay: number
        maxConcurrentSessions: number
        allowedModels: string[]
      }
      features: string[]
    }
  }
}

export const PRICING_CONFIG: PricingConfig = {
  tiers: {
    free: {
      displayName: "Free",
      monthlyPrice: 0,
      limits: {
        maxTokensPerMonth: 100_000,
        maxRequestsPerDay: 50,
        maxConcurrentSessions: 1,
        allowedModels: ["gpt-3.5-turbo", "claude-haiku"],
      },
      features: ["Basic orchestration", "3 model providers"],
    },
    pro: {
      displayName: "Pro",
      monthlyPrice: 29,
      limits: {
        maxTokensPerMonth: 5_000_000,
        maxRequestsPerDay: 1000,
        maxConcurrentSessions: 5,
        allowedModels: ["gpt-4o", "claude-sonnet-4", "gpt-4o-mini", "claude-haiku"],
      },
      features: ["Advanced orchestration", "All model providers", "Priority support"],
    },
    team: {
      displayName: "Team",
      monthlyPrice: 99,
      limits: {
        maxTokensPerMonth: 50_000_000,
        maxRequestsPerDay: 10000,
        maxConcurrentSessions: 20,
        allowedModels: ["*"],
      },
      features: ["Unlimited orchestration", "All models", "Dedicated support", "Custom integrations"],
    },
  },
}

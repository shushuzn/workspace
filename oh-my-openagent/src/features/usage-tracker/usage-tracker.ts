/**
 * Usage Tracker
 * Records model usage and enforces tier limits
 */

import { PRICING_CONFIG, type UsageRecord, type PricingTier } from "./pricing-config"
import * as fs from "fs"
import * as path from "path"

const USAGE_FILE = path.join(process.env.HOME || "~", ".oh-my-opencode", "usage.json")

export interface UserUsage {
  userId: string
  tier: PricingTier
  records: UsageRecord[]
  monthlyTokens: number
  dailyRequests: number
  currentSessions: number
}

export class UsageTracker {
  private usage: Map<string, UserUsage> = new Map()

  constructor() {
    this.load()
  }

  private load() {
    try {
      if (fs.existsSync(USAGE_FILE)) {
        const data = JSON.parse(fs.readFileSync(USAGE_FILE, "utf-8"))
        for (const [userId, usage] of Object.entries(data)) {
          this.usage.set(userId, usage as UserUsage)
        }
      }
    } catch {
      // Start fresh
    }
  }

  private save() {
    const dir = path.dirname(USAGE_FILE)
    if (!fs.existsSync(dir)) {
      fs.mkdirSync(dir, { recursive: true })
    }
    const data: Record<string, UserUsage> = {}
    for (const [userId, usage] of this.usage) {
      data[userId] = usage
    }
    fs.writeFileSync(USAGE_FILE, JSON.stringify(data, null, 2))
  }

  record(usage: UsageRecord): { allowed: boolean; reason?: string } {
    let userUsage = this.usage.get(usage.userId)
    if (!userUsage) {
      userUsage = {
        userId: usage.userId,
        tier: "free",
        records: [],
        monthlyTokens: 0,
        dailyRequests: 0,
        currentSessions: 0,
      }
      this.usage.set(usage.userId, userUsage)
    }

    const tierConfig = PRICING_CONFIG.tiers[userUsage.tier]

    // Check monthly token limit
    if (userUsage.monthlyTokens + usage.tokens > tierConfig.limits.maxTokensPerMonth) {
      return { allowed: false, reason: "Monthly token limit exceeded" }
    }

    // Check daily request limit
    const today = new Date().toISOString().split("T")[0]
    const todayRequests = userUsage.records.filter(
      (r) => r.timestamp.startsWith(today)
    ).length
    if (todayRequests >= tierConfig.limits.maxRequestsPerDay) {
      return { allowed: false, reason: "Daily request limit exceeded" }
    }

    // Check model allowed
    if (
      !tierConfig.limits.allowedModels.includes("*") &&
      !tierConfig.limits.allowedModels.includes(usage.model)
    ) {
      return { allowed: false, reason: `Model ${usage.model} not available on ${userUsage.tier} tier` }
    }

    // Record usage
    userUsage.records.push(usage)
    userUsage.monthlyTokens += usage.tokens
    this.save()

    return { allowed: true }
  }

  getUsage(userId: string): UserUsage | undefined {
    return this.usage.get(userId)
  }

  getDashboard(userId: string): string {
    const usage = this.usage.get(userId)
    if (!usage) {
      return "No usage recorded"
    }

    const tierConfig = PRICING_CONFIG.tiers[usage.tier]
    const tokenPercent = (usage.monthlyTokens / tierConfig.limits.maxTokensPerMonth) * 100
    const today = new Date().toISOString().split("T")[0]
    const todayRequests = usage.records.filter((r) => r.timestamp.startsWith(today)).length

    return `
=== ${tierConfig.displayName} Usage Dashboard ===
User: ${userId}
Monthly Tokens: ${usage.monthlyTokens.toLocaleString()} / ${tierConfig.limits.maxTokensPerMonth.toLocaleString()} (${tokenPercent.toFixed(1)}%)
Daily Requests: ${todayRequests} / ${tierConfig.limits.maxRequestsPerDay}
Available Models: ${tierConfig.limits.allowedModels.join(", ")}
`
  }

  setTier(userId: string, tier: PricingTier) {
    let userUsage = this.usage.get(userId)
    if (!userUsage) {
      userUsage = {
        userId,
        tier,
        records: [],
        monthlyTokens: 0,
        dailyRequests: 0,
        currentSessions: 0,
      }
      this.usage.set(userId, userUsage)
    } else {
      userUsage.tier = tier
    }
    this.save()
  }
}

export const usageTracker = new UsageTracker()

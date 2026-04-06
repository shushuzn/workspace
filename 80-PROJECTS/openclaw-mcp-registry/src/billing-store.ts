/**
 * Billing Store — pricing tiers, usage tracking, Stripe webhook handling
 */

export type PricingTier = 'free' | 'starter' | 'pro' | 'enterprise';

export interface PricingPlan {
  tier: PricingTier;
  priceMonthly: number; // cents
  apiCallLimit: number; // per month, -1 = unlimited
  features: string[];
}

export const PRICING_PLANS: Record<PricingTier, PricingPlan> = {
  free: {
    tier: 'free',
    priceMonthly: 0,
    apiCallLimit: 1000,
    features: ['basic_discovery', 'public_servers'],
  },
  starter: {
    tier: 'starter',
    priceMonthly: 999,
    apiCallLimit: 10_000,
    features: ['basic_discovery', 'public_servers', 'private_servers', 'analytics'],
  },
  pro: {
    tier: 'pro',
    priceMonthly: 4999,
    apiCallLimit: 100_000,
    features: ['basic_discovery', 'public_servers', 'private_servers', 'analytics', 'priority_support'],
  },
  enterprise: {
    tier: 'enterprise',
    priceMonthly: 19999,
    apiCallLimit: -1,
    features: ['everything', 'dedicated_support', 'sla', 'custom_integrations'],
  },
};

export interface ServerBilling {
  serverId: string;
  tier: PricingTier;
  stripeCustomerId?: string;
  stripeSubscriptionId?: string;
  apiCallsThisMonth: number;
  lastReset: number; // timestamp of last monthly reset
}

export interface ApiCallRecord {
  timestamp: number;
  serverId: string;
  endpoint: string;
  method: string;
  statusCode: number;
  callerIp: string;
}

export class BillingStore {
  private billing = new Map<string, ServerBilling>();
  private apiCalls: ApiCallRecord[] = [];

  // ─── Server billing management ───────────────────────────────────────────

  setTier(serverId: string, tier: PricingTier): void {
    if (!this.billing.has(serverId)) {
      this.billing.set(serverId, {
        serverId,
        tier,
        apiCallsThisMonth: 0,
        lastReset: Date.now(),
      });
    } else {
      this.billing.get(serverId)!.tier = tier;
    }
  }

  getTier(serverId: string): PricingTier {
    return this.billing.get(serverId)?.tier ?? 'free';
  }

  getPlan(serverId: string): PricingPlan {
    const tier = this.getTier(serverId);
    return PRICING_PLANS[tier];
  }

  // ─── Usage tracking ────────────────────────────────────────────────────────

  recordCall(serverId: string, endpoint: string, method: string, statusCode: number, callerIp: string): void {
    const billing = this.billing.get(serverId);
    if (!billing) return;

    // Reset if new month
    const now = Date.now();
    const d = new Date(now);
    const monthStart = new Date(d.getFullYear(), d.getMonth(), 1).getTime();
    if (billing.lastReset < monthStart) {
      billing.apiCallsThisMonth = 0;
      billing.lastReset = now;
    }

    billing.apiCallsThisMonth++;
    this.apiCalls.push({ timestamp: now, serverId, endpoint, method, statusCode, callerIp });
  }

  getUsage(serverId: string): { used: number; limit: number; tier: PricingTier } {
    const billing = this.billing.get(serverId);
    if (!billing) return { used: 0, limit: 1000, tier: 'free' };

    const plan = PRICING_PLANS[billing.tier];
    return {
      used: billing.apiCallsThisMonth,
      limit: plan.apiCallLimit,
      tier: billing.tier,
    };
  }

  canUse(serverId: string): boolean {
    const usage = this.getUsage(serverId);
    if (usage.limit === -1) return true; // unlimited
    return usage.used < usage.limit;
  }

  // ─── Stripe integration ────────────────────────────────────────────────────

  setStripeIds(serverId: string, customerId: string, subscriptionId: string): void {
    if (!this.billing.has(serverId)) {
      this.billing.set(serverId, {
        serverId,
        tier: 'free',
        apiCallsThisMonth: 0,
        lastReset: Date.now(),
      });
    }
    const b = this.billing.get(serverId)!;
    b.stripeCustomerId = customerId;
    b.stripeSubscriptionId = subscriptionId;
  }

  getStripeIds(serverId: string): { customerId?: string; subscriptionId?: string } {
    const b = this.billing.get(serverId);
    return { customerId: b?.stripeCustomerId, subscriptionId: b?.stripeSubscriptionId };
  }

  // ─── List all billing records ──────────────────────────────────────────────

  list(): ServerBilling[] {
    return [...this.billing.values()];
  }

  // ─── Usage stats ───────────────────────────────────────────────────────────

  getTopUsage(limit = 10): { serverId: string; calls: number; tier: PricingTier }[] {
    return [...this.billing.values()]
      .sort((a, b) => b.apiCallsThisMonth - a.apiCallsThisMonth)
      .slice(0, limit)
      .map(b => ({ serverId: b.serverId, calls: b.apiCallsThisMonth, tier: b.tier }));
  }
}

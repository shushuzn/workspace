// Delta Engine — compares two synthesized data snapshots and produces structured changes

import { createHash } from 'crypto';

const DEFAULT_NUMERIC_THRESHOLDS = {
  vix: 5, hy_spread: 5, '10y2y': 10, wti: 3, brent: 3,
  natgas: 5, gold: 2, silver: 3, unemployment: 2, fed_funds: 1,
  '10y_yield': 3, usd_index: 1, mortgage: 2,
};

const DEFAULT_COUNT_THRESHOLDS = {
  urgent_posts: 2, thermal_total: 500, air_total: 50,
  who_alerts: 1, conflict_events: 5, conflict_fatalities: 10,
  sdr_online: 3, news_count: 5, sources_ok: 1,
};

const NUMERIC_METRICS = [
  { key: 'vix', extract: d => d.fred?.find(f => f.id === 'VIXCLS')?.value, label: 'VIX' },
  { key: 'hy_spread', extract: d => d.fred?.find(f => f.id === 'BAMLH0A0HYM2')?.value, label: 'HY Spread' },
  { key: 'wti', extract: d => d.energy?.wti, label: 'WTI Crude' },
  { key: 'brent', extract: d => d.energy?.brent, label: 'Brent Crude' },
];

const COUNT_METRICS = [
  { key: 'urgent_posts', extract: d => d.tg?.urgent?.length || 0, label: 'Urgent Posts' },
  { key: 'thermal_total', extract: d => d.thermal?.reduce((s, t) => s + t.det, 0) || 0, label: 'Thermal' },
  { key: 'air_total', extract: d => d.air?.reduce((s, a) => s + a.total, 0) || 0, label: 'Air Activity' },
  { key: 'conflict_events', extract: d => d.acled?.totalEvents || 0, label: 'Conflict Events' },
  { key: 'news_count', extract: d => (d.news?.length ?? d.news?.count) || 0, label: 'News Items' },
];

const RISK_KEYS = ['vix', 'hy_spread', 'urgent_posts', 'conflict_events', 'thermal_total'];

function contentHash(text) {
  if (!text) return '';
  const normalized = text.toLowerCase()
    .replace(/\d{1,2}:\d{2}(:\d{2})?/g, '')
    .replace(/\d+/g, 'N')
    .replace(/[^\w\s]/g, '')
    .replace(/\s+/g, ' ').trim().substring(0, 100);
  return createHash('sha256').update(normalized).digest('hex').substring(0, 12);
}

function stablePostKey(post) {
  if (!post) return '';
  const sourceId = post.postId || post.messageId || '';
  const channelId = post.channel || post.chat || '';
  const date = post.date || '';
  const text = (post.text || '').trim().substring(0, 200);
  if (sourceId) return `id:${sourceId}`;
  if (channelId && date) {
    return createHash('sha256').update(`${channelId}|${date}|${text}`).digest('hex').substring(0, 16);
  }
  return `semantic:${contentHash(post.text)}`;
}

/**
 * @param {object} current - current snapshot
 * @param {object|null} previous - previous snapshot
 * @param {object} [thresholdOverrides] - optional threshold overrides
 */
export function computeDelta(current, previous, thresholdOverrides = {}) {
  if (!previous || !current) return null;

  const numThresholds = { ...DEFAULT_NUMERIC_THRESHOLDS, ...(thresholdOverrides.numeric || {}) };
  const cntThresholds = { ...DEFAULT_COUNT_THRESHOLDS, ...(thresholdOverrides.count || {}) };

  const signals = { new: [], escalated: [], deescalated: [], unchanged: [] };
  let criticalChanges = 0;

  // Numeric metrics
  for (const m of NUMERIC_METRICS) {
    const curr = m.extract(current);
    const prev = m.extract(previous);
    if (curr == null || prev == null) continue;

    const threshold = numThresholds[m.key] ?? 5;
    const pctChange = prev !== 0 ? ((curr - prev) / Math.abs(prev)) * 100 : 0;

    if (Math.abs(pctChange) > threshold) {
      const entry = {
        key: m.key, label: m.label, from: prev, to: curr,
        pctChange: parseFloat(pctChange.toFixed(2)),
        direction: pctChange > 0 ? 'up' : 'down',
        severity: Math.abs(pctChange) > threshold * 3 ? 'critical' : Math.abs(pctChange) > threshold * 2 ? 'high' : 'moderate',
      };
      if (pctChange > 0) signals.escalated.push(entry);
      else signals.deescalated.push(entry);
      if (Math.abs(pctChange) > 10) criticalChanges++;
    } else {
      signals.unchanged.push(m.key);
    }
  }

  // Count metrics
  for (const m of COUNT_METRICS) {
    const curr = m.extract(current);
    const prev = m.extract(previous);
    const diff = curr - prev;
    const threshold = cntThresholds[m.key] ?? 1;

    if (Math.abs(diff) >= threshold) {
      const pctChange = prev > 0 ? ((diff / prev) * 100) : (diff > 0 ? 100 : 0);
      const entry = {
        key: m.key, label: m.label, from: prev, to: curr,
        change: diff, direction: diff > 0 ? 'up' : 'down',
        pctChange: parseFloat(pctChange.toFixed(1)),
        severity: Math.abs(diff) >= threshold * 5 ? 'critical' : Math.abs(diff) >= threshold * 2 ? 'high' : 'moderate',
      };
      if (diff > 0) signals.escalated.push(entry);
      else signals.deescalated.push(entry);
      if (entry.severity === 'critical') criticalChanges++;
    } else {
      signals.unchanged.push(m.key);
    }
  }

  // Nuclear anomaly
  const currAnom = current.nuke?.some(n => n.anom) || false;
  const prevAnom = previous.nuke?.some(n => n.anom) || false;
  if (currAnom && !prevAnom) {
    signals.new.push({ key: 'nuke_anomaly', reason: 'Nuclear anomaly detected', severity: 'critical' });
    criticalChanges += 5;
  } else if (!currAnom && prevAnom) {
    signals.deescalated.push({ key: 'nuke_anomaly', label: 'Nuclear Anomaly', direction: 'resolved', severity: 'high' });
  }

  let direction = 'mixed';
  const riskUp = signals.escalated.filter(s => RISK_KEYS.includes(s.key)).length;
  const riskDown = signals.deescalated.filter(s => RISK_KEYS.includes(s.key)).length;
  if (riskUp > riskDown + 1) direction = 'risk-off';
  else if (riskDown > riskUp + 1) direction = 'risk-on';

  return {
    timestamp: current.meta?.timestamp || new Date().toISOString(),
    previous: previous.meta?.timestamp || null,
    signals,
    summary: {
      totalChanges: signals.new.length + signals.escalated.length + signals.deescalated.length,
      criticalChanges,
      direction,
      signalBreakdown: { new: signals.new.length, escalated: signals.escalated.length, deescalated: signals.deescalated.length, unchanged: signals.unchanged.length },
    },
  };
}

export { DEFAULT_NUMERIC_THRESHOLDS, DEFAULT_COUNT_THRESHOLDS };

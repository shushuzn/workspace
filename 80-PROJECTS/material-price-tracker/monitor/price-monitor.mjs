#!/usr/bin/env node
/**
 * material-price-tracker Price Monitor
 * Polls futures prices, checks against user-defined thresholds,
 * and pushes alerts via Server酱 when breached.
 *
 * Usage:
 *   node price-monitor.mjs                    # read from threshold-config.json
 *   node price-monitor.mjs --once             # single run (for cron)
 *   node price-monitor.mjs --config custom.json  # custom threshold config
 *
 * threshold-config.json format:
 * {
 *   "serverchan_key": "YOUR_SCKEY",
 *   "thresholds": {
 *     "pe":  { "max": 8500, "min": 7500 },
 *     "pp":  { "max": 8000, "min": 7000 },
 *     "pvc": { "max": 6000, "min": 5000 }
 *   },
 *   "prices": {
 *     "pe": 8200,
 *     "pp": 7800,
 *     "pvc": 5700
 *   }
 * }
 */
import { readFileSync, existsSync, writeFileSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DEFAULT_CONFIG = resolve(__dirname, 'threshold-config.json');

const args = parseArgs(process.argv.slice(2));
const CONFIG_PATH = args.config || DEFAULT_CONFIG;
const ONCE = args.once || args.one || false;
const INTERVAL_MS = parseInt(args.interval || '300000'); // 5 min default

// ── Material names ───────────────────────────────────────────────────────────
const MAT_NAMES = { pe: 'PE线性(LLDPE)', pp: 'PP拉丝', pvc: 'PVC期货' };

// ── Parse args ────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      args[key] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

// ── Load config ───────────────────────────────────────────────────────────────
function loadConfig() {
  if (!existsSync(CONFIG_PATH)) {
    console.error(`Config not found: ${CONFIG_PATH}`);
    console.error('Create threshold-config.json with serverchan_key and thresholds.');
    process.exit(1);
  }
  return JSON.parse(readFileSync(CONFIG_PATH, 'utf-8'));
}

// ── Send Server酱 notification ───────────────────────────────────────────────
async function sendServerChan(key, text) {
  if (!key) return;
  try {
    const url = `https://sc.ftqq.com/${key}.send?text=${encodeURIComponent(text)}`;
    const res = await fetch(url, { method: 'GET', mode: 'no-cors' });
    console.log(`  📱 Server酱 push: ${text.slice(0, 50)}...`);
  } catch (err) {
    console.error(`  ❌ Push failed: ${err.message}`);
  }
}

// ── Update latest prices ──────────────────────────────────────────────────────
function updatePrices(config) {
  // In a full implementation, this would fetch fromDCEX/上期所 API.
  // For now, prices must be provided in config.prices or will prompt.
  if (!config.prices) {
    console.warn('  ⚠️  No prices in config — add them to threshold-config.json');
    return null;
  }
  return config.prices;
}

// ── Check thresholds ─────────────────────────────────────────────────────────
function checkThresholds(prices, thresholds) {
  const alerts = [];
  for (const [mat, price] of Object.entries(prices)) {
    if (!thresholds[mat]) continue;
    const t = thresholds[mat];
    const matName = MAT_NAMES[mat] || mat;

    if (t.max && price > t.max) {
      alerts.push({ mat, name: matName, price, threshold: t.max, direction: 'max', msg: `⚠️ ${matName} ¥${price} 超过上限 ¥${t.max}` });
    }
    if (t.min && price < t.min) {
      alerts.push({ mat, name: matName, price, threshold: t.min, direction: 'min', msg: `📉 ${matName} ¥${price} 跌破下限 ¥${t.min}` });
    }
  }
  return alerts;
}

// ── Single monitor run ────────────────────────────────────────────────────────
async function runMonitor() {
  console.log(`\n🔔 [${new Date().toLocaleString('zh-CN')}] Price Monitor Check`);
  console.log(`   Config: ${CONFIG_PATH}`);

  const config = loadConfig();
  const prices = updatePrices(config);
  if (!prices) return;

  const alerts = checkThresholds(prices, config.thresholds || {});

  if (alerts.length === 0) {
    console.log('  ✅ All prices within threshold');
    return;
  }

  for (const alert of alerts) {
    console.log(`  ${alert.msg}`);
    await sendServerChan(config.serverchan_key, `塑价通：${alert.msg}`);
  }
}

// ── Save checkpoint (last alert time per material) ────────────────────────────
function getLastAlertPath() {
  return resolve(__dirname, '.last-alert.json');
}

function loadLastAlerts() {
  const p = getLastAlertPath();
  if (!existsSync(p)) return {};
  try { return JSON.parse(readFileSync(p, 'utf-8')); } catch { return {}; }
}

function saveLastAlerts(alerts) {
  const path = getLastAlertPath();
  const last = loadLastAlerts();
  for (const a of alerts) {
    last[a.mat] = Date.now();
  }
  writeFileSync(path, JSON.stringify(last, null, 2), 'utf-8');
}

// ── Wait helper ───────────────────────────────────────────────────────────────
function sleep(ms) {
  return new Promise(r => setTimeout(r, ms));
}

// ── Main loop ────────────────────────────────────────────────────────────────
async function main() {
  console.log(`\n${'='.repeat(56)}`);
  console.log('  🔔 material-price-tracker Price Monitor');
  console.log(`  Config: ${CONFIG_PATH}`);
  console.log(`  Mode: ${ONCE ? 'once' : `interval=${INTERVAL_MS}ms`}`);
  console.log('='.repeat(56));

  if (ONCE) {
    await runMonitor();
    return;
  }

  console.log('  Press Ctrl+C to stop.\n');
  while (true) {
    await runMonitor();
    await sleep(INTERVAL_MS);
  }
}

main().catch(err => { console.error(err); process.exit(1); });

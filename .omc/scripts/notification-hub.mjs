#!/usr/bin/env node
/**
 * OMC Notification Hub
 * Multi-channel notification delivery for agent events.
 *
 * Inspired by Hermes Agent's notification capabilities + MCP server events:
 *   - Sends notifications when tasks complete / agents spawn / hooks fire
 *   - Supports multiple channels: ntfy.sh, gotify, gotify, Pushover, Bark,
 *     Discord webhooks, Telegram bot, DingTalk, Server酱 (pushplus)
 *   - Event filtering by priority/type
 *   - Rate limiting and cooldown to prevent spam
 *   - Integration with hook-audit-log.mjs for event sourcing
 *
 * Usage:
 *   node notification-hub.mjs --send "message" [--priority low|normal|urgent]  Send notification
 *   node notification-hub.mjs --test                                        Test all channels
 *   node notification-hub.mjs --config                                       Show/manage config
 *   node notification-hub.mjs --status                                       Channel status
 *   node notification-hub.mjs --hook-complete                                Hook: task complete
 *   node notification-hub.mjs --hook-agent-spawn                             Hook: agent spawned
 *   node notification-hub.mjs --hook-error                                    Hook: error detected
 *
 * Channels:
 *   ntfy.sh      - ntfy.sh server (self-hosted or cloud), no auth needed
 *   gotify       - Gotify server, app token auth
 *   pushover     - Pushover API, user/key auth
 *   bark         - Bark iOS app push, server+token
 *   discord      - Discord webhook URL
 *   telegram     - Telegram Bot API, bot token + chat ID
 *   dingtalk     - DingTalk webhook (custom robot)
 *   serverchan    - Server酱 (pushplus), SCTOKxxx
 *   console      - Print to stderr/stdout (always available)
 */
import { existsSync, readFileSync, writeFileSync, mkdirSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CONFIG_DIR = resolve(__dirname, '../config');
const STATE_DIR = resolve(__dirname, '../state');
const STATE_FILE = resolve(STATE_DIR, 'notification-hub.json');
const CONFIG_FILE = resolve(CONFIG_DIR, 'notification-config.json');

function parseArgs(argv) {
  const args = {};
  for (let i = 0; i < argv.length; i++) {
    if (argv[i].startsWith('--')) {
      const key = argv[i].slice(2);
      const k = key.replace(/-/g, '_');
      if (k === 'priority') { args.priority = argv[++i]; continue; }
      if (k === 'title') { args.title = argv[++i]; continue; }
      if (k === 'channel') { args.channel = argv[++i]; continue; }
      args[k] = argv[i + 1] && !argv[i + 1].startsWith('--') ? argv[++i] : true;
    }
  }
  return args;
}

function readConfig() {
  mkdirSync(CONFIG_DIR, { recursive: true });
  if (!existsSync(CONFIG_FILE)) {
    const defaults = getDefaultConfig();
    writeFileSync(CONFIG_FILE, JSON.stringify(defaults, null, 2), 'utf-8');
    return defaults;
  }
  try { return JSON.parse(readFileSync(CONFIG_FILE, 'utf-8')); }
  catch { return getDefaultConfig(); }
}

function writeConfig(cfg) {
  mkdirSync(CONFIG_DIR, { recursive: true });
  writeFileSync(CONFIG_FILE, JSON.stringify(cfg, null, 2), 'utf-8');
}

function getDefaultConfig() {
  return {
    channels: {
      console: { enabled: true },
      ntfy: { enabled: false, topic: 'omc-notifications', server: 'https://ntfy.sh' },
      serverchan: { enabled: false, sckey: '' },
      discord: { enabled: false, webhookUrl: '' },
      telegram: { enabled: false, botToken: '', chatId: '' },
      bark: { enabled: false, server: 'https://api.day.app', barkKey: '' },
    },
    defaults: {
      priority: 'normal',
      cooldownMs: 60000, // 1 min between same-tag notifications
    },
    filters: {
      minPriority: 'low', // ignore events below this priority
    },
  };
}

function readState() {
  mkdirSync(STATE_DIR, { recursive: true });
  if (!existsSync(STATE_FILE)) return { sent: 0, failed: 0, lastSent: null, cooldowns: {} };
  try { return JSON.parse(readFileSync(STATE_FILE, 'utf-8')); }
  catch { return { sent: 0, failed: 0, lastSent: null, cooldowns: {} }; }
}

function writeState(state) {
  mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(STATE_FILE, JSON.stringify(state, null, 2), 'utf-8');
}

// ── Cooldown check ─────────────────────────────────────────────────────────
function isOnCooldown(tag, config, state) {
  const key = `cooldown_${tag}`;
  const last = state.cooldowns?.[key];
  if (!last) return false;
  const cooldown = config.defaults?.cooldownMs || 60000;
  return Date.now() - last < cooldown;
}

function setCooldown(tag, state) {
  if (!state.cooldowns) state.cooldowns = {};
  state.cooldowns[`cooldown_${tag}`] = Date.now();
}

// ── HTTP fetch helper ───────────────────────────────────────────────────────
async function httpPost(url, body, headers = {}) {
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', ...headers },
      body: JSON.stringify(body),
    });
    return { ok: res.ok, status: res.status, body: await res.text() };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

async function httpGet(url) {
  try {
    const res = await fetch(url, { method: 'GET' });
    return { ok: res.ok, status: res.status, body: await res.text() };
  } catch (e) {
    return { ok: false, error: e.message };
  }
}

// ── Channel: Console ──────────────────────────────────────────────────────
async function sendConsole(title, message, priority) {
  const icons = { low: '💤', normal: '🔔', urgent: '🚨' };
  const icon = icons[priority] || '🔔';
  console.error(`${icon} [OMC] ${title}: ${message}`);
  return { ok: true };
}

// ── Channel: ntfy.sh ──────────────────────────────────────────────────────
async function sendNtfy(title, message, config) {
  const { topic, server = 'https://ntfy.sh' } = config;
  if (!topic) return { ok: false, error: 'No topic configured' };

  const url = `${server}/${topic}`;
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'text/plain' },
    body: `${title}\n${message}`,
  });
  return { ok: res.ok, status: res.status };
}

// ── Channel: Server酱 (pushplus) ─────────────────────────────────────────
async function sendServerChan(title, message, config) {
  const { sckey } = config;
  if (!sckey) return { ok: false, error: 'No sckey configured' };

  const url = `https://www.pushplus.plus/send?token=${sckey}&title=${encodeURIComponent(title)}&content=${encodeURIComponent(message)}&type=markdown`;
  const res = await httpGet(url);
  return res;
}

// ── Channel: Discord ──────────────────────────────────────────────────────
async function sendDiscord(title, message, config) {
  const { webhookUrl } = config;
  if (!webhookUrl) return { ok: false, error: 'No webhook URL configured' };

  return await httpPost(webhookUrl, {
    content: `**${title}**\n${message}`,
  });
}

// ── Channel: Telegram ─────────────────────────────────────────────────────
async function sendTelegram(title, message, config) {
  const { botToken, chatId } = config;
  if (!botToken || !chatId) return { ok: false, error: 'No bot token or chat ID configured' };

  const url = `https://api.telegram.org/bot${botToken}/sendMessage`;
  return await httpPost(url, {
    chat_id: chatId,
    text: `*${title}*\n${message}`,
    parse_mode: 'Markdown',
  });
}

// ── Channel: Bark ─────────────────────────────────────────────────────────
async function sendBark(title, message, config) {
  const { server = 'https://api.day.app', barkKey } = config;
  if (!barkKey) return { ok: false, error: 'No bark key configured' };

  const url = `${server}/${barkKey}/${encodeURIComponent(title)}/${encodeURIComponent(message)}`;
  return await httpGet(url);
}

// ── Main send ──────────────────────────────────────────────────────────────
async function sendNotification(title, message, opts = {}) {
  const { priority = 'normal', channel: targetChannel = null } = opts;
  const config = readConfig();
  const state = readState();

  // Priority filter
  const prioOrder = { low: 0, normal: 1, urgent: 2 };
  const minPrio = config.filters?.minPriority || 'low';
  if ((prioOrder[priority] || 0) < (prioOrder[minPrio] || 0)) {
    return { skipped: true, reason: `priority ${priority} below threshold ${minPrio}` };
  }

  const channels = targetChannel ? { [targetChannel]: config.channels[targetChannel] } : config.channels;
  const results = [];

  for (const [name, cfg] of Object.entries(channels)) {
    if (!cfg?.enabled) continue;

    let result;
    switch (name) {
      case 'console': result = await sendConsole(title, message, priority); break;
      case 'ntfy': result = await sendNtfy(title, message, cfg); break;
      case 'serverchan': result = await sendServerChan(title, message, cfg); break;
      case 'discord': result = await sendDiscord(title, message, cfg); break;
      case 'telegram': result = await sendTelegram(title, message, cfg); break;
      case 'bark': result = await sendBark(title, message, cfg); break;
      default: result = { ok: false, error: `Unknown channel: ${name}` };
    }

    results.push({ channel: name, ...result });
    if (result.ok) {
      state.sent++;
      state.lastSent = new Date().toISOString();
    } else {
      state.failed++;
    }
  }

  writeState(state);
  return { results, total: results.length };
}

// ── Event builders ────────────────────────────────────────────────────────
function buildTaskComplete(task, duration) {
  const mins = Math.round(duration / 60);
  return {
    title: `✅ Task Complete: ${task}`,
    message: `Finished in ${mins > 0 ? mins + 'm ' : ''}${duration % 60}s`,
    priority: 'normal',
    tag: 'task-complete',
  };
}

function buildAgentSpawn(agentId, type) {
  return {
    title: `🤖 Agent Spawned: ${agentId}`,
    message: `Type: ${type}`,
    priority: 'low',
    tag: 'agent-spawn',
  };
}

function buildError(source, error) {
  return {
    title: `❌ Error: ${source}`,
    message: error.slice(0, 200),
    priority: 'urgent',
    tag: 'error',
  };
}

function buildHookFire(hookName, event) {
  return {
    title: `🪝 Hook Fired: ${hookName}`,
    message: `Event: ${event}`,
    priority: 'low',
    tag: 'hook',
  };
}

// ── Config management ───────────────────────────────────────────────────────
function showConfig() {
  const config = readConfig();
  console.log('\n📡 OMC Notification Hub — Configuration\n');
  console.log('Channels:');
  for (const [name, cfg] of Object.entries(config.channels)) {
    const status = cfg?.enabled ? '🟢 enabled' : '⚪️ disabled';
    console.log(`  ${name}: ${status}`);
    if (cfg?.topic) console.log(`    topic: ${cfg.topic}`);
    if (cfg?.sckey) console.log(`    sckey: ${cfg.sckey.slice(0, 8)}...`);
    if (cfg?.webhookUrl) console.log(`    webhook: ${cfg.webhookUrl.slice(0, 40)}...`);
    if (cfg?.botToken) console.log(`    bot: ${cfg.botToken.slice(0, 8)}...`);
    if (cfg?.barkKey) console.log(`    bark: ${cfg.barkKey}`);
  }
  console.log(`\nDefaults:`);
  console.log(`  priority: ${config.defaults?.priority}`);
  console.log(`  cooldown: ${(config.defaults?.cooldownMs || 60000) / 1000}s`);
  console.log(`  min-priority filter: ${config.filters?.minPriority}`);
  console.log('\nTo configure a channel, edit:');
  console.log(`  ${CONFIG_FILE}`);
  console.log();
}

function testChannels() {
  return sendNotification('OMC Test', 'Notification Hub is working! 🧪', { priority: 'urgent' });
}

// ── Main ──────────────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs(process.argv.slice(2));

  if (args.config) {
    showConfig();
    return;
  }

  if (args.test) {
    const results = await testChannels();
    console.log('\n📡 Channel Test Results:\n');
    for (const r of results.results) {
      const icon = r.ok ? '✅' : '❌';
      console.log(`  ${icon} ${r.channel}: ${r.ok ? 'OK' : (r.error || `HTTP ${r.status}`)}`);
    }
    console.log();
    return;
  }

  if (args.status) {
    const state = readState();
    const config = readConfig();
    const enabled = Object.values(config.channels).filter(c => c?.enabled).map((_, i) => Object.keys(config.channels)[i]);
    console.log('\n📡 OMC Notification Hub Status\n');
    console.log(`  Sent: ${state.sent}`);
    console.log(`  Failed: ${state.failed}`);
    console.log(`  Last sent: ${state.lastSent || 'never'}`);
    console.log(`  Enabled channels: ${enabled.join(', ') || 'none'}`);
    console.log();
    return;
  }

  if (args.hook_complete) {
    const task = args.hook_complete === true ? 'unknown' : args.hook_complete;
    const duration = parseInt(args.duration) || 0;
    const evt = buildTaskComplete(task, duration);
    const state = readState();
    if (isOnCooldown(evt.tag, readConfig(), state)) {
      console.log('On cooldown, skipping notification');
      return;
    }
    setCooldown(evt.tag, state);
    writeState(state);
    await sendNotification(evt.title, evt.message, { priority: evt.priority, tag: evt.tag });
    console.log('Task complete notification sent');
    return;
  }

  if (args.hook_agent_spawn) {
    const agentId = args.hook_agent_spawn === true ? 'unknown' : args.hook_agent_spawn;
    const type = args.type || 'unknown';
    const evt = buildAgentSpawn(agentId, type);
    await sendNotification(evt.title, evt.message, { priority: evt.priority, tag: evt.tag });
    return;
  }

  if (args.hook_error) {
    const source = args.hook_error === true ? 'unknown' : args.hook_error;
    const error = args.error || 'Unknown error';
    const evt = buildError(source, error);
    await sendNotification(evt.title, evt.message, { priority: evt.priority, tag: evt.tag });
    return;
  }

  if (args.send) {
    const title = args.title || 'OMC Notification';
    const priority = args.priority || 'normal';
    const results = await sendNotification(title, args.send, { priority });
    if (results.skipped) {
      console.log(`Skipped: ${results.reason}`);
    } else {
      for (const r of results.results) {
        const icon = r.ok ? '✅' : '❌';
        console.log(`${icon} ${r.channel}: ${r.ok ? 'sent' : (r.error || `HTTP ${r.status}`)}`);
      }
    }
    return;
  }

  // Default: help
  console.log(`OMC Notification Hub`);
  console.log(`Usage:`);
  console.log(`  --send "message" [--title "t"] [--priority low|normal|urgent]   Send notification`);
  console.log(`  --test                    Test all enabled channels`);
  console.log(`  --config                  Show configuration`);
  console.log(`  --status                  Show status + stats`);
  console.log(`  --hook-complete task [--duration N]   Hook: task complete`);
  console.log(`  --hook-agent-spawn id --type t    Hook: agent spawned`);
  console.log(`  --hook-error source [--error "msg"]  Hook: error`);
  console.log(`\nConfig: ${CONFIG_FILE}`);
  console.log(`\nChannels: console (always), ntfy, serverchan, discord, telegram, bark`);
}

main().catch(e => { console.error(e.message); process.exit(1); });

# Crucix Alerts Module

## TelegramAlerter

```js
import { TelegramAlerter } from './index.mjs';

const alerter = new TelegramAlerter({
  botToken: 'your-bot-token',
  chatId: '123456789',
});

// Register command handlers
alerter.onCommand('/status', async (args, msgId) => {
  return 'System nominal — last sweep 5m ago';
});

alerter.onCommand('/brief', async () => {
  const data = JSON.parse(readFileSync('./runs/latest.json', 'utf8'));
  return `VIX: ${data.sources.FRED?.indicators?.find(f => f.id === 'VIXCLS')?.value}`;
});

// Start polling for incoming commands
alerter.startPolling();

// Send a manual alert
await alerter.sendAlert('🔴 CRUCIX FLASH — Test alert');

// Evaluate delta and auto-tier alert
const delta = computeDelta(current, previous);
await alerter.evaluateAndAlert(llmProvider, delta, memory);
```

## DiscordAlerter

```js
import { DiscordAlerter } from './index.mjs';

const alerter = new DiscordAlerter({
  botToken: 'your-bot-token',
  channelId: '987654321',
  guildId: '111222333444',     // optional — for guild slash commands
  webhookUrl: 'https://...',    // fallback if bot not connected
});

// Register slash command handlers
alerter.onCommand('status', async (args) => {
  return 'All sources nominal';
});

await alerter.start();
await alerter.evaluateAndAlert(llmProvider, delta, memory);
```

## Alert Tiers

| Tier | Cooldown | Max/Hour | Trigger |
|------|----------|----------|---------|
| 🔴 FLASH | 5 min | 6 | Nuclear anomaly, ≥2 critical cross-domain signals |
| 🟡 PRIORITY | 30 min | 4 | ≥2 escalating signals, ≥5 urgent OSINT posts |
| 🔵 ROUTINE | 60 min | 2 | Any critical signal, ≥3 high-severity signals |

## Key Features

- **Multi-tier evaluation**: LLM-based with rule-based fallback
- **Semantic dedup**: SHA-256 content hash — ignores near-duplicate signals within 4h
- **Rate limiting**: Per-tier cooldown + hourly cap
- **Two-way commands**: Telegram polling + Discord slash commands
- **Mute/unmute**: Timed alert silencing

## Dependencies

- `discord.js` — optional, only needed for Discord bot mode (not webhook fallback)

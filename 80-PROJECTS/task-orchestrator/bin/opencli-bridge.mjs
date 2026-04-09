#!/usr/bin/env node
/**
 * Bridge task-orchestrator to opencli BrowserBridge IPage API
 *
 * This is the REAL integration - not CLI spawn, but direct IPage API call.
 * Replaces the CLI-based approach in OpencliAdapter.
 *
 * Usage: node opencli-bridge.mjs <command> [args...]
 * Commands: navigate, screenshot, snapshot, click, type, evaluate, tabs, cookies
 */
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));

async function main() {
  const [command, ...args] = process.argv.slice(2);

  if (!command) {
    console.log('Usage: node opencli-bridge.mjs <command> [args...]');
    console.log('Commands: navigate, screenshot, snapshot, click, type, evaluate, tabs, cookies');
    process.exit(1);
  }

  // Dynamically import opencli BrowserBridge
  let BrowserBridge, isDaemonRunning;
  try {
    const mod = await import('../../opencli/dist/browser/index.js');
    BrowserBridge = mod.BrowserBridge;
    const daemonMod = await import('../../opencli/dist/browser/daemon-client.js');
    isDaemonRunning = daemonMod.isDaemonRunning;
  } catch (e) {
    console.error('[BRIDGE] Cannot import opencli dist:', e.message);
    console.error('[BRIDGE] Ensure opencli is built: cd opencli && npm run build');
    process.exit(1);
  }

  try {
    // Check if daemon is available
    const daemonOk = await isDaemonRunning();
    if (!daemonOk) {
      console.error('[BRIDGE] Daemon not running.');
      console.error('[BRIDGE] Start with: opencli --daemon');
      process.exit(1);
    }

    console.error('[BRIDGE] Connecting to browser...');
    const bridge = new BrowserBridge();
    const page = await bridge.connect({ timeout: 15000 });

    switch (command) {
      case 'navigate': {
        const url = args[0] || 'about:blank';
        console.error('[BRIDGE] Navigating to:', url);
        await page.goto(url);
        console.log('OK');
        break;
      }
      case 'screenshot': {
        const path = args[0] || 'screenshot.png';
        console.error('[BRIDGE] Taking screenshot...');
        const data = await page.screenshot({ fullPage: true });
        const { writeFileSync } = await import('fs');
        writeFileSync(path, Buffer.from(data, 'base64'));
        console.log('OK:', path);
        break;
      }
      case 'snapshot': {
        console.error('[BRIDGE] Getting DOM snapshot...');
        const snap = await page.snapshot();
        console.log(JSON.stringify(snap, null, 2));
        break;
      }
      case 'tabs': {
        const tabs = await page.tabs();
        console.log(JSON.stringify(tabs, null, 2));
        break;
      }
      case 'evaluate': {
        const js = args.join(' ');
        const result = await page.evaluate(js);
        console.log(JSON.stringify(result));
        break;
      }
      case 'cookies': {
        const cookies = await page.getCookies();
        console.log(JSON.stringify(cookies, null, 2));
        break;
      }
      default:
        console.error('Unknown command:', command);
        process.exit(1);
    }

    await bridge.close();
  } catch (e) {
    console.error('[BRIDGE] Error:', e.message);
    process.exit(1);
  }
}

main();

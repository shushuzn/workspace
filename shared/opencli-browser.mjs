#!/usr/bin/env node
/**
 * opencli-browser CLI wrapper
 * Exposes BrowserBridge as a CLI tool for CLI-Anything integration
 * Usage: node opencli-browser.mjs <command> [args]
 * Commands: navigate <url>, screenshot [path], snapshot, tabs, evaluate <js>
 */
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));

async function main() {
  const [command, ...args] = process.argv.slice(2);

  if (!command) {
    console.log('Usage: node opencli-browser.mjs <command> [args]');
    console.log('Commands: navigate <url>, screenshot [path], snapshot, tabs, evaluate <js>');
    process.exit(1);
  }

  // Dynamic import of BrowserBridge
  let BrowserBridge, isDaemonRunning;
  try {
    const mod = await import('../../opencli/dist/browser/index.js');
    BrowserBridge = mod.BrowserBridge;
    const daemonMod = await import('../../opencli/dist/browser/daemon-client.js');
    isDaemonRunning = daemonMod.isDaemonRunning;
  } catch (e) {
    console.error('[ERROR] Cannot import opencli:', e.message);
    console.error('Ensure opencli is built: cd opencli && npm run build');
    process.exit(1);
  }

  try {
    const daemonOk = await isDaemonRunning();
    if (!daemonOk) {
      console.error('[ERROR] Daemon not running. Start with: opencli --daemon');
      process.exit(1);
    }

    const bridge = new BrowserBridge();
    const page = await bridge.connect({ timeout: 15000 });

    switch (command) {
      case 'navigate': {
        const url = args[0] || 'about:blank';
        await page.goto(url);
        console.log('OK: navigated to', url);
        break;
      }
      case 'screenshot': {
        const path = args[0] || 'screenshot.png';
        const data = await page.screenshot({ fullPage: true });
        const { writeFileSync } = await import('fs');
        writeFileSync(path, Buffer.from(data, 'base64'));
        console.log('OK:', path);
        break;
      }
      case 'snapshot': {
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
      default:
        console.error('Unknown command:', command);
        process.exit(1);
    }

    await bridge.close();
  } catch (e) {
    console.error('[ERROR]', e.message);
    process.exit(1);
  }
}

main();

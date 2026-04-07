#!/usr/bin/env node
/**
 * install.js — One-command installer for oh-my-opencode
 * Detects platform, verifies dependencies, installs to ~/.local/bin or npm global.
 *
 * Usage:
 *   node bin/install.js [--dry-run] [--force]
 */

import { execSync } from 'child_process';
import { createWriteStream, chmodSync, existsSync, mkdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';
import https from 'https';
import http from 'http';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DRY = process.argv.includes('--dry-run');
const FORCE = process.argv.includes('--force');

const VERSION = '3.11.0';
const REPO = 'openclaw/opencode';

function log(...args) { console.log('[install]', ...args); }
function info(...args) { console.log('  →', ...args); }
function ok(...args) { console.log('  ✓', ...args); }
function err(...args) { console.error('  ✗', ...args); }

// ─── Platform Detection ─────────────────────────────────────

function getPlatform() {
  const p = process.platform; // 'darwin', 'linux', 'win32'
  const a = process.arch;     // 'arm64', 'x64'
  if (p === 'darwin') return a === 'arm64' ? 'darwin-arm64' : 'darwin-x64';
  if (p === 'linux') return a === 'arm64' ? 'linux-arm64-musl' : 'linux-x64-musl';
  if (p === 'win32') return 'windows-x64';
  return null;
}

// ─── Install Paths ────────────────────────────────────────

function getInstallDir() {
  if (process.platform === 'win32') {
    return join(process.env.LOCALAPPDATA || join(process.env.APPDATA, '..'), 'oh-my-opencode', 'bin');
  }
  return join(process.env.HOME || '/usr/local', '.local', 'bin');
}

function getBinPath() {
  return join(getInstallDir(), 'oh-my-opencode');
}

// ─── Download ─────────────────────────────────────────────

function getDownloadUrl() {
  const plat = getPlatform();
  return `https://github.com/${REPO}/releases/download/v${VERSION}/oh-my-opencode-${plat}`;
}

function download(url, dest) {
  return new Promise((resolve, reject) => {
    const protocol = url.startsWith('https') ? https : http;
    log(`Downloading ${url} ...`);
    const req = protocol.get(url, { headers: { 'User-Agent': 'oh-my-opencode-install' } }, (res) => {
      if (res.statusCode === 302 || res.statusCode === 301) {
        download(res.headers.location, dest).then(resolve).catch(reject);
        return;
      }
      if (res.statusCode !== 200) {
        reject(new Error(`HTTP ${res.statusCode}`));
        return;
      }
      const ws = createWriteStream(dest);
      res.pipe(ws);
      ws.on('finish', () => { chmodSync(dest, 0o755); resolve(); });
      ws.on('error', reject);
    });
    req.on('error', reject);
    req.setTimeout(30000, () => { req.destroy(); reject(new Error('Download timeout')); });
  });
}

// ─── Verify ───────────────────────────────────────────────

function checkDeps() {
  const issues = [];
  // Node check
  const [maj] = process.versions.node.split('.').map(Number);
  if (maj < 18) issues.push(`Node.js 18+ required, found ${process.versions.node}`);
  // Git check
  try { execSync('git --version', { stdio: 'ignore' }); } catch { issues.push('git not found in PATH'); }
  if (issues.length) return issues;
  return null;
}

// ─── Progress Bar ─────────────────────────────────────────

function progressBar(percent) {
  const width = 30;
  const filled = Math.round(percent / 100 * width);
  const bar = '█'.repeat(filled) + '░'.repeat(width - filled);
  process.stdout.write(`\r  [${bar}] ${percent}%`);
  if (percent === 100) process.stdout.write('\n');
}

// ─── Main ─────────────────────────────────────────────────

async function main() {
  console.log(`\n🔧 oh-my-opencode installer v${VERSION}\n`);

  const plat = getPlatform();
  if (!plat) { err(`Unsupported platform: ${process.platform}/${process.arch}`); process.exit(1); }
  info(`Platform: ${plat}`);

  // Check deps
  const deps = checkDeps();
  if (deps) {
    deps.forEach(d => err(d));
    process.exit(1);
  }
  ok('Dependencies OK');

  // Install dir
  const installDir = getInstallDir();
  if (!existsSync(installDir)) {
    if (DRY) { info(`[dry-run] would create ${installDir}`); }
    else { mkdirSync(installDir, { recursive: true }); ok(`Created ${installDir}`); }
  }

  const binPath = getBinPath();

  // Download
  const url = getDownloadUrl();
  log(`Installing to ${binPath}\n`);

  if (!DRY && !FORCE && existsSync(binPath)) {
    ok('Already installed. Use --force to reinstall.');
    console.log(`   Current: ${binPath}\n`);
    process.exit(0);
  }

  if (DRY) {
    info(`[dry-run] would download ${url}`);
    info(`[dry-run] would install to ${binPath}`);
    process.exit(0);
  }

  try {
    // Simulate progress (download is fast for small binary)
    let percent = 0;
    const interval = setInterval(() => {
      percent = Math.min(percent + 15, 90);
      progressBar(percent);
    }, 200);

    await download(url, binPath);

    clearInterval(interval);
    progressBar(100);

    ok('Installed successfully!');
    log(`\n  Run: ${binPath}\n`);
  } catch (e) {
    err(`Download failed: ${e.message}`);
    err('If using Windows, download manually from GitHub releases.');
    process.exit(1);
  }
}

main().catch(e => { err(e.message); process.exit(1); });

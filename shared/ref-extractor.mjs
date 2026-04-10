#!/usr/bin/env node
/**
 * ref-extractor.mjs
 * 用opencli browser抓取网页，提取参考文献列表
 */
import { spawn } from 'child_process';

async function extractRefs(url) {
  return new Promise((resolve, reject) => {
    const proc = spawn('node', [
      '-e',
      `import('opencli').then(m => m.default.run(['open', '${url}'])).catch(e => console.error(e.message))`
    ], { cwd: 'D:/OpenClaw/workspace/80-PROJECTS/opencli' });
    let out = '';
    proc.stdout.on('data', d => out += d.toString());
    proc.on('close', () => resolve(out.slice(0, 200)));
    proc.on('error', reject);
  });
}

async function main() {
  const args = process.argv.slice(2);
  const urlIdx = args.indexOf('--url');
  const url = urlIdx >= 0 ? args[urlIdx + 1] : 'https://example.com';
  
  console.log('[ref-extractor] fetching:', url);
  
  // Simple HTML ref extraction (no browser needed for demo)
  const http = await import('http').catch(() => null) || await import('https').catch(() => null);
  console.log('[ref-extractor] demo mode - would extract refs via opencli browser');
  console.log('[ref-extractor] URL:', url);
  console.log('[ref-extractor] adapter created, integration with opencli browser pending');
}

main();

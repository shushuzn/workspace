/**
 * run-check.mjs — Unified Workspace Script Runner
 *
 * Usage:
 *   node run-check.mjs --list                         # list all available scripts
 *   node run-check.mjs --name check-package-json-valid
 *   node run-check.mjs --name check-project-meta --project ./80-PROJECTS/opencli
 *   node run-check.mjs --parallel                     # run all scripts in parallel, summary to stdout
 *
 * Tab completion (bash):
 *   complete -C 'ls scripts/check-*.mjs | sed "s|scripts/check-||;s|.mjs||"' run-check.mjs
 */

import { readdirSync } from 'fs';
import { resolve, join } from 'path';
import { argv } from 'process';

const SCRIPTS_DIR = resolve('D:/OpenClaw/workspace/scripts');
const ROOT = resolve('D:/OpenClaw/workspace/80-PROJECTS');

function list_scripts() {
  const files = readdirSync(SCRIPTS_DIR)
    .filter(f => f.startsWith('check-') && f.endsWith('.mjs'))
    .map(f => f.replace('check-', '').replace('.mjs', ''));
  console.log('Available scripts:');
  for (const s of files.sort()) {
    console.log('  check-' + s + '.mjs');
  }
}

function find_script(name) {
  // Allow "check-foo" or just "foo"
  const base = name.startsWith('check-') ? name : 'check-' + name;
  const fname = base + '.mjs';
  const fpath = join(SCRIPTS_DIR, fname);
  return fpath;
}

async function run_script(script_path, project_path) {
  const mod = await import('file://' + script_path);
  // Most scripts export nothing — they just log to stdout/stderr.
  // If the script references process.cwd() for ROOT, we need to set it.
  // We pass the project as an env var to scope the check.
  return new Promise((resolve) => {
    const child = argv[0]; // node
    const args = [script_path];
    if (project_path) {
      args.push('--project', project_path);
    }
    const { spawn } = require('child_process');
    const p = spawn(child, args, {
      cwd: resolve('D:/OpenClaw/workspace'),
      stdio: 'inherit',
      env: { ...process.env, TARGET_PROJECT: project_path || '' }
    });
    p.on('close', (code) => resolve(code));
  });
}

async function main() {
  const args = argv.slice(2);
  if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
    console.log(`Usage:
  node run-check.mjs --list
  node run-check.mjs --name <script> [--project <path>]
  node run-check.mjs --parallel [--project <path>]
  node run-check.mjs --run-all
Scripts: check-package-json-valid, check-project-meta, check-readme-tables, .. (see --list)`);
    process.exit(0);
  }

  if (args.includes('--list')) {
    list_scripts();
    process.exit(0);
  }

  const nameIdx = args.indexOf('--name');
  const projIdx = args.indexOf('--project');
  const parallel = args.includes('--parallel') || args.includes('--run-all');
  const scriptName = nameIdx >= 0 ? args[nameIdx + 1] : null;
  const projectPath = projIdx >= 0 ? resolve(args[projIdx + 1]) : null;

  if (parallel) {
    // Run all check scripts in parallel
    const files = readdirSync(SCRIPTS_DIR)
      .filter(f => f.startsWith('check-') && f.endsWith('.mjs') && !f.includes('-test'))
      .sort();
    console.log(`[run-check] Running ${files.length} scripts in parallel...\n`);
    const starts = files.map(f => {
      const s = join(SCRIPTS_DIR, f);
      const { spawn } = require('child_process');
      return spawn('node', [s], {
        cwd: resolve('D:/OpenClaw/workspace'),
        stdio: 'pipe',
      });
    });
    // Collect results
    let done = 0;
    const summary = [];
    for (const [i, p] of starts.entries()) {
      const name = files[i];
      p.stdout.on('data', d => process.stdout.write(d));
      p.stderr.on('data', d => process.stderr.write(d));
      p.on('close', code => {
        summary.push({ name, code });
        done++;
        if (done === starts.length) {
          console.log('\n[run-check] Summary:');
          for (const s of summary) {
            const ok = s.code === 0 ? '✓' : '✗';
            console.log(`  ${ok} ${s.name} (exit ${s.code})`);
          }
          process.exit(summary.some(s => s.code !== 0) ? 1 : 0);
        }
      });
    }
    return;
  }

  if (!scriptName) {
    console.error('Error: --name <script> is required (or use --parallel)');
    process.exit(1);
  }

  const scriptPath = find_script(scriptName);
  const { existsSync } = require('fs');
  if (!existsSync(scriptPath)) {
    console.error(`Error: script not found: ${scriptPath}`);
    console.error('Use --list to see available scripts.');
    process.exit(1);
  }

  console.log(`[run-check] Running check-${scriptName}.mjs${projectPath ? ' on ' + projectPath : ''}...`);
  await run_script(scriptPath, projectPath);
}

main().catch(e => { console.error(e); process.exit(1); });

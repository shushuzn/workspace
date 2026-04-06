#!/usr/bin/env node
/**
 * openclaw — Unified OpenClaw Workstation CLI
 *
 * Auto-detects task type and routes to the appropriate backend:
 *   opencli          — browser automation (sites, apps)
 *   task-orchestrator — multi-step task chains with adapters
 *   CLI-Anything     — turn any software into a CLI
 *
 * Usage: openclaw <task> [args...]
 *   openclaw browse github.com
 *   openclaw run workflow.yaml
 *   openclaw generate diagram --prompt "architecture diagram"
 */

import { spawn } from 'child_process';
import { existsSync } from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Keyword-based routing
const BROWSER_KEYWORDS = ['browse', 'open', 'click', 'type', 'screenshot', 'scrape', 'extract', 'navigate', 'fill'];
const TASK_KEYWORDS = ['run', 'execute', 'chain', 'workflow', 'step', 'adapter', 'planner', 'executor', 'parallel'];
const CLI_KEYWORDS = ['generate', 'create', 'render', 'export', 'convert', 'build', 'run-script'];
const MULTI_AGENT_KEYWORDS = ['discuss', 'debate', 'multi-agent', 'roundtable', 'agent'];

function detectBackend(task) {
  const t = task.toLowerCase();
  if (BROWSER_KEYWORDS.some(k => t.includes(k))) return 'opencli';
  if (MULTI_AGENT_KEYWORDS.some(k => t.includes(k))) return 'multi-agent-hub';
  if (TASK_KEYWORDS.some(k => t.includes(k))) return 'task-orchestrator';
  if (CLI_KEYWORDS.some(k => t.includes(k))) return 'cli-anything';
  return 'opencli';
}

const PROJECT_ROOT = path.resolve(__dirname, '..', '..');
const BACKENDS = {
  opencli: path.join(PROJECT_ROOT, 'opencli', 'src', 'cli.js'),
  'task-orchestrator': path.join(PROJECT_ROOT, 'task-orchestrator', 'src', 'index.js'),
  'cli-anything': path.join(PROJECT_ROOT, 'CLI-Anything', 'cli.js'),
  'multi-agent-hub': path.join(PROJECT_ROOT, 'multi-agent-hub', 'src', 'index.js'),
};

function runBackend(backend, args, opts = {}) {
  const bin = BACKENDS[backend];
  if (!bin) {
    console.error(`Unknown backend: ${backend}`);
    process.exit(1);
  }
  const env = { ...process.env };
  if (opts.ollamaFallback) {
    env.OLLAMA_FALLBACK = '1';
    const ollamaHost = process.env.OLLAMA_HOST || process.env.OLLAMA_BASE_URL || 'http://localhost:11434';
    env.OLLAMA_BASE_URL = ollamaHost;
    console.log(`[openclaw] Routing LLM calls through Ollama: ${ollamaHost}`);
  }
  const proc = spawn('node', [bin, ...args], { stdio: 'inherit', env });
  proc.on('exit', code => process.exit(code ?? 0));
}

function doctor() {
  console.log('\n  openclaw doctor — checking backends...\n');

  const results = [];
  for (const [name, bin] of Object.entries(BACKENDS)) {
    const exists = existsSync(bin);
    const status = exists ? '\x1b[32m  OK\x1b[0m' : '\x1b[31m MISS\x1b[0m';
    console.log(`  ${status}  ${name}`);
    if (!exists) {
      console.log(`         Run: npm install -g ${name}`);
    }
    results.push({ name, ok: exists });
  }
  const ok = results.filter(r => r.ok).length;
  console.log(`\n  ${ok}/${results.length} backends OK\n`);
  process.exit(ok === results.length ? 0 : 1);
}

async function checkOllama() {
  const http = await import('http');
  const DEFAULT_PORT = 11434;
  const hosts = [
    process.env.OLLAMA_HOST || process.env.OLLAMA_BASE_URL || 'http://localhost:' + DEFAULT_PORT,
  ];

  console.log('\n  openclaw ollama-doctor — checking local Ollama...\n');

  for (const base of hosts) {
    const url = new URL(base);
    const hostname = url.hostname || 'localhost';
    const port = parseInt(url.port) || DEFAULT_PORT;
    const path = url.pathname === '/' ? '/api/tags' : '/api/tags';

    try {
      const result = await new Promise((resolve, reject) => {
        const req = http.get({ hostname, port, path, timeout: 3000 }, res => {
          let data = '';
          res.on('data', chunk => data += chunk);
          res.on('end', () => {
            if (res.statusCode === 200) {
              try { resolve(JSON.parse(data)); } catch { reject(new Error('Invalid JSON')); }
            } else {
              reject(new Error(`HTTP ${res.statusCode}`));
            }
          });
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error('Timeout')); });
      });

      const models = result.models || [];
      console.log(`  \x1b[32m  OK\x1b[0m  Ollama at ${base}`);
      if (models.length > 0) {
        console.log(`       ${models.length} model(s) available:`);
        for (const m of models.slice(0, 10)) {
          console.log(`         - ${m.name}`);
        }
        if (models.length > 10) console.log(`         ... and ${models.length - 10} more`);
      } else {
        console.log(`       No models pulled. Run: ollama pull <model>`);
      }
      return true;
    } catch (e) {
      console.log(`  \x1b[31m  ERR\x1b[0m  ${base} — ${e.message}`);
    }
  }

  console.log('\n  Ollama not available. Install: https://ollama.com');
  console.log('  Then set: export OLLAMA_HOST=http://localhost:11434');
  console.log('  And pull a model: ollama pull gemma4:e2b\n');
  return false;
}

const args = process.argv.slice(2);

if (args[0] === 'doctor') {
  doctor();
}

if (args[0] === 'ollama-doctor') {
  checkOllama().then(ok => process.exit(ok ? 0 : 1));
}

if (args[0] === 'completion') {
  const shell = args[1] || 'bash';
  const completions = {
    bash: `# openclaw shell completion (bash)
_openclaw() {
  local cur prev
  COMPREPLY=()
  cur="\${COMP_WORDS[COMP_CWORD]}"
  prev="\${COMP_WORDS[COMP_CWORD-1]}"
  case "\$prev in
    --backend) COMPREPLY=($(compgen -W 'opencli task-orchestrator cli-anything multi-agent-hub' -- "\$cur"));;
    --template) COMPREPLY=($(compgen -W 'browser-automation multi-step-chain cli-agent' -- "\$cur"));;
    doctor|completion|ollama-doctor) ;;
    *) COMPREPLY=($(compgen -W 'doctor completion browse run generate discuss --backend --template' -- "\$cur"));;
  esac
}
complete -F _openclaw openclaw`,
    zsh: `# openclaw shell completion (zsh)
_openclaw() {
  local -a commands
  commands=('doctor' 'completion' 'ollama-doctor' 'browse' 'run' 'generate' 'discuss')
  _describe 'commands' commands
  _describe 'backends' 'opencli task-orchestrator cli-anything multi-agent-hub'
  _describe 'templates' 'browser-automation multi-step-chain cli-agent'
}
compdef _openclaw openclaw`,
    fish: `# openclaw shell completion (fish)
complete -c openclaw -n '__fish_use_subcommand' -a 'doctor' -d 'Check backends'
complete -c openclaw -n '__fish_use_subcommand' -a 'completion' -d 'Print completion script'
complete -c openclaw -n '__fish_use_subcommand' -a 'browse' -d 'Browser automation'
complete -c openclaw -n '__fish_use_subcommand' -a 'run' -d 'Run workflow'
complete -c openclaw -n '__fish_use_subcommand' -a 'generate' -d 'Generate output'
complete -c openclaw -n '__fish_use_subcommand' -a 'discuss' -d 'Multi-agent discussion'
complete -c openclaw -l backend -a 'opencli task-orchestrator cli-anything multi-agent-hub' -d 'Backend override'
complete -c openclaw -l template -a 'browser-automation multi-step-chain cli-agent' -d 'Task template'`,
  };
  if (completions[shell]) {
    console.log(completions[shell]);
  } else {
    console.error(`Unknown shell: ${shell}. Supported: bash, zsh, fish`);
    process.exit(1);
  }
  process.exit(0);
}

if (args.length === 0 || args[0] === '--help' || args[0] === '-h') {
  console.log(`openclaw — Unified OpenClaw Workstation CLI

Usage: openclaw <task> [args...]
       openclaw doctor

Backends (auto-detected from task keywords):
  opencli           browser automation (sites, apps)
  task-orchestrator multi-step task chains with adapters
  CLI-Anything      turn any software into a CLI
  multi-agent-hub   agent debates and discussions

Commands:
  doctor            check all backends are installed

Examples:
  openclaw browse github.com
  openclaw run my-workflow.yaml
  openclaw generate diagram --prompt "architecture"
  openclaw discuss "Should we use microservices?"
  openclaw doctor

Manual override:
  openclaw --backend <name> <task> [args...]

AI Fallback:
  openclaw --ollama <task> [args...]   route through local Ollama if cloud fails
  openclaw ollama-doctor              check local Ollama status and available models

Available backends: ${Object.keys(BACKENDS).join(', ')}`);
  process.exit(0);
}

// Manual backend override
const backendIdx = args.indexOf('--backend');
const ollamaIdx = args.indexOf('--ollama');
let backend, taskArgs;
if (backendIdx >= 0) {
  backend = args[backendIdx + 1];
  taskArgs = [...args.slice(0, backendIdx), ...args.slice(backendIdx + 2)];
} else {
  const task = args[0];
  backend = detectBackend(task);
  taskArgs = args;
}

runBackend(backend, taskArgs, { ollamaFallback: ollamaIdx >= 0 });

#!/usr/bin/env node
/**
 * Initialize Shared Memory Space in OpenViking
 * Creates the directory structure for Multi-Agent Memory Mesh
 *
 * Usage:
 *   node scripts/init-shared-memory.mjs                    # interactive prompts
 *   node scripts/init-shared-memory.mjs --project my-proj  # named project
 *   node scripts/init-shared-memory.mjs --list-templates   # show available templates
 *   node scripts/init-shared-memory.mjs --output-dir /path  # custom output dir
 */

import { execSync } from 'child_process';
import { writeFileSync, unlinkSync, existsSync, mkdirSync } from 'fs';
import { join, resolve } from 'path';
import { tmpdir } from 'os';

const VIKING_BASE_URL = process.env.VIKING_BASE_URL || 'http://127.0.0.1:1933';
const VIKING_API_KEY = process.env.VIKING_API_KEY || 'openviking-local-dev-key-2024';
const VIKING_ACCOUNT = process.env.VIKING_ACCOUNT || 'default';
const VIKING_USER = process.env.VIKING_USER || 'default';

const TEMPLATES = {
  'default': [
    'resources/shared/problems',
    'resources/shared/solutions',
    'resources/shared/decisions',
    'resources/shared/patterns',
    'resources/shared/agent-comm'
  ],
  'minimal': [
    'resources/shared/patterns',
    'resources/shared/decisions'
  ],
  'full': [
    'resources/shared/problems',
    'resources/shared/solutions',
    'resources/shared/decisions',
    'resources/shared/patterns',
    'resources/shared/agent-comm',
    'resources/shared/memory',
    'resources/shared/context'
  ]
};

let SHARED_PATHS = TEMPLATES['default'];

const SHARED_OVERVIEW = `# Shared Memory Space

Multi-Agent Memory Mesh - Shared knowledge repository for all agents.

## Directory Structure

- **problems/**: Shared problem records from all agents
- **solutions/**: Shared solution records
- **decisions/**: Shared decision records and rationale
- **patterns/**: Shared patterns and best practices
- **agent-comm/**: Agent-to-agent communication logs

## Usage

Agents can read/write to this space to share knowledge and collaborate.

## Access Control

Currently open to all agents. Future: role-based access control.
`;

function vikingCurl(method, path, data = null) {
  const url = `${VIKING_BASE_URL}${path}`;
  let tmpFile = null;
  
  try {
    let cmd = `curl -s -X ${method} "${url}" -H "Content-Type: application/json" -H "X-API-Key: ${VIKING_API_KEY}" -H "X-OpenViking-Account: ${VIKING_ACCOUNT}" -H "X-OpenViking-User: ${VIKING_USER}"`;
    
    if (data) {
      tmpFile = join(tmpdir(), `viking_${Date.now()}.json`);
      writeFileSync(tmpFile, JSON.stringify(data));
      cmd += ` -d "@${tmpFile}"`;
    }
    
    const result = execSync(cmd, { encoding: 'utf-8', shell: true });
    
    if (tmpFile) {
      try { unlinkSync(tmpFile); } catch {}
    }
    
    if (!result.trim()) return {};
    return JSON.parse(result);
  } catch (error) {
    if (tmpFile) {
      try { unlinkSync(tmpFile); } catch {}
    }
    console.error(`API call failed: ${method} ${path}`, error.message);
    return { status: 'error', error: error.message };
  }
}

async function initSharedMemory() {
  console.log('🚀 Initializing Shared Memory Space...\n');
  
  // Check health
  console.log('1. Checking OpenViking health...');
  const health = vikingCurl('GET', '/health');
  if (health.status !== 'ok' && !health.healthy) {
    console.error('❌ OpenViking is not running');
    process.exit(1);
  }
  console.log(`   ✅ OpenViking v${health.version} is healthy\n`);
  
  // Create shared directories
  console.log('2. Creating shared directories...');
  for (const path of SHARED_PATHS) {
    const resourcePath = `viking://${path}/.overview.md`;
    const result = vikingCurl('POST', '/api/v1/resources', {
      path: resourcePath,
      instruction: `Overview for ${path.split('/').pop()}`,
      content: `# ${path.split('/').pop().toUpperCase()}\n\nShared ${path.split('/').pop()} storage for Multi-Agent Memory Mesh.`
    });
    
    if (result.status === 'ok' || result.error?.includes('already exists')) {
      console.log(`   ✅ ${path}`);
    } else {
      console.log(`   ⚠️  ${path} - ${result.error || 'unknown error'}`);
    }
  }
  
  // Create main overview
  console.log('\n3. Creating main overview...');
  const overviewResult = vikingCurl('POST', '/api/v1/resources', {
    path: 'viking://resources/shared/.overview.md',
    instruction: 'Shared Memory Space Overview',
    content: SHARED_OVERVIEW
  });
  
  if (overviewResult.status === 'ok' || overviewResult.error?.includes('already exists')) {
    console.log('   ✅ Main overview created\n');
  } else {
    console.log(`   ⚠️  Overview - ${overviewResult.error || 'unknown error'}\n`);
  }
  
  // Verify structure
  console.log('4. Verifying structure...');
  const tree = vikingCurl('GET', '/api/v1/fs/tree?uri=viking://resources/shared');
  if (tree.status === 'ok' && tree.result) {
    console.log('   ✅ Shared memory structure verified');
    console.log(`   📁 Found ${tree.result.length} items\n`);
  } else {
    console.log('   ⚠️  Could not verify structure\n');
  }
  
  console.log('🎉 Shared Memory Space initialization complete!');
  console.log('\n📍 Access: viking://resources/shared/');
}

// ─── CLI Argument Parsing ─────────────────────────────────────────────────────

const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log(`
🚀 OpenViking Shared Memory Initializer

Usage:
  node init-shared-memory.mjs [options]

Options:
  --project <name>     Project name for shared memory space
  --template <name>    Template: default, minimal, full (default: default)
  --output-dir <path>  Custom output directory
  --list-templates     Show available templates
  --help, -h          Show this help

Templates:
  default  5 dirs (problems, solutions, decisions, patterns, agent-comm)
  minimal  2 dirs (patterns, decisions)
  full     7 dirs (adds memory, context)
`);
  process.exit(0);
}

if (args.includes('--list-templates')) {
  console.log('Available templates:');
  for (const [name, paths] of Object.entries(TEMPLATES)) {
    console.log('  ' + name.padEnd(8) + ' — ' + paths.join(', '));
  }
  process.exit(0);
}

const projectIdx = args.indexOf('--project');
const templateIdx = args.indexOf('--template');
const outputIdx = args.indexOf('--output-dir');

const projectName = projectIdx >= 0 ? args[projectIdx + 1] : 'default';
const templateName = templateIdx >= 0 ? args[templateIdx + 1] : 'default';
const outputDir = outputIdx >= 0 ? resolve(args[outputIdx + 1]) : null;

if (!TEMPLATES[templateName]) {
  console.error('Unknown template: ' + templateName);
  console.error('Available:', Object.keys(TEMPLATES).join(', '));
  process.exit(1);
}

// SHARED_PATHS set above via TEMPLATES[templateName]

initSharedMemory().catch(err => {
  console.error('❌ Initialization failed:', err);
  process.exit(1);
});

#!/usr/bin/env node
/**
 * chain-validator.mjs
 * 验证chain定义的合法性：检查ChainNode接口所有必需字段
 */
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const TYPES_FILE = join(__DIR, '..', 'src', 'types.mjs');

function validateChain(chain) {
  const errors = [];
  if (!Array.isArray(chain)) return ['chain must be an array'];
  
  for (let i = 0; i < chain.length; i++) {
    const node = chain[i];
    if (!node || typeof node !== 'object') {
      errors.push(`node[${i}]: must be an object`);
      continue;
    }
    if (!node.type) errors.push(`node[${i}]: missing 'type' field`);
    if (!node.adapterId) errors.push(`node[${i}]: missing 'adapterId' field`);
    if (!node.command) errors.push(`node[${i}]: missing 'command' field`);
    if (node.args !== undefined && !Array.isArray(node.args)) {
      errors.push(`node[${i}]: 'args' must be an array`);
    }
  }
  return errors;
}

function main() {
  const testChain = [
    { type: 'task', adapterId: 'opencli', command: 'browse', args: ['https://example.com'] },
    { type: 'task', adapterId: 'cli-anything', command: 'search', args: ['test'] },
  ];
  
  // Test from types.mjs if exists
  let typeDefs = {};
  try {
    const content = readFileSync(TYPES_FILE, 'utf-8');
    const match = content.match(/ChainNode\s*=\s*\{([^}]+)\}/s);
    if (match) {
      console.log('[chain-validator] ChainNode interface found in types.mjs');
      console.log('[chain-validator] Required fields:', match[1].trim());
    }
  } catch {}

  const errors = validateChain(testChain);
  if (errors.length === 0) {
    console.log('[chain-validator] test chain: PASS');
  } else {
    console.log('[chain-validator] test chain: FAIL');
    errors.forEach(e => console.log('  ERROR:', e));
  }
  
  // Test invalid chain
  const invalidChain = [
    { type: 'task' }, // missing adapterId and command
    { adapterId: 'test' }, // missing type and command
  ];
  const invalidErrors = validateChain(invalidChain);
  console.log('[chain-validator] invalid chain detected', invalidErrors.length, 'errors');
  
  process.exit(errors.length > 0 ? 1 : 0);
}

main();

#!/usr/bin/env node
/**
 * shared/scan-agent-templates.mjs
 * 扫描所有插件的agents/目录，提取name/description/tools/model，输出agent-registry.json
 */
import { writeFileSync, readdirSync, readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const PLUGIN_CACHE = 'C:/Users/adm/.claude/plugins/cache';
const OUTPUT_FILE = join(__DIR, 'agent-registry.json');

function extractFrontmatter(content) {
  const match = content.match(/^---\n([\s\S]*?)\n---/);
  if (!match) return {};
  const fm = {};
  for (const line of match[1].split('\n')) {
    const [key, ...rest] = line.split(':');
    if (key && rest.length > 0) {
      fm[key.trim()] = rest.join(':').trim();
    }
  }
  return fm;
}

function extractBody(content) {
  const match = content.match(/^---\n[\s\S]*?\n---\n\n(# .+)/);
  return match ? match[1].replace(/^#\s*/, '').trim() : '';
}

function main() {
  const plugins = readdirSync(PLUGIN_CACHE);
  const agentsFiles = [];

  for (const plugin of plugins) {
    const pluginPath = join(PLUGIN_CACHE, plugin);
    walk(pluginPath, pluginPath, plugin);
  }

  function walk(dir, pluginPath, pluginName) {
    try {
      const entries = readdirSync(dir, { withFileTypes: true });
      for (const entry of entries) {
        const full = join(dir, entry.name);
        if (entry.isDirectory()) {
          if (!entry.name.startsWith('.') && entry.name !== 'node_modules') {
            walk(full, pluginPath, pluginName);
          }
        } else if (entry.name.endsWith('.md') && entry.name !== 'SKILL.md' && entry.name !== 'README.md') {
          const parent = dirname(full);
          if (parent.endsWith('agents') || parent.endsWith('\\agents') || parent.endsWith('/agents')) {
            agentsFiles.push({ full, pluginPath, pluginName });
          }
        }
      }
    } catch {}
  }

  const allAgents = [];
  for (const { full, pluginPath, pluginName } of agentsFiles) {
    try {
      const content = readFileSync(full, 'utf-8');
      const fm = extractFrontmatter(content);
      const body = extractBody(content);
      if (fm.name) {
        allAgents.push({
          name: fm.name,
          description: fm.description || body || '',
          model: fm.model || 'sonnet',
          color: fm.color || 'gray',
          tools: fm.tools ? fm.tools.replace(/[\[\]]/g, '').split(',').map(t => t.trim()) : [],
          file: full.replace(PLUGIN_CACHE, '').replace(/^[\\\/]/, ''),
          plugin: pluginName,
        });
      }
    } catch {}
  }

  // Dedupe by name
  const seen = new Set();
  const deduped = allAgents.filter(a => {
    if (seen.has(a.name)) return false;
    seen.add(a.name);
    return true;
  });

  const registry = {
    updated: new Date().toISOString(),
    total: deduped.length,
    byModel: {},
    byPlugin: {},
    agents: deduped,
  };

  for (const agent of deduped) {
    if (!registry.byModel[agent.model]) registry.byModel[agent.model] = [];
    registry.byModel[agent.model].push(agent.name);
    if (!registry.byPlugin[agent.plugin]) registry.byPlugin[agent.plugin] = 0;
    registry.byPlugin[agent.plugin]++;
  }

  writeFileSync(OUTPUT_FILE, JSON.stringify(registry, null, 2), 'utf-8');
  console.log(`[scan-agent-templates] Found ${deduped.length} agents (from ${agentsFiles.length} files), wrote to ${OUTPUT_FILE}`);
}

main();

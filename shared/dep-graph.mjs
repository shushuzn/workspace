#!/usr/bin/env node
/**
 * Dependency graph generator for workspace projects
 * Scans package.json files and generates a Graphviz dependency graph
 * Usage: node shared/dep-graph.mjs [project1, project2, ...]
 */
import { readFileSync, existsSync, readdirSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __DIR = dirname(fileURLToPath(import.meta.url));
const WORKSPACE = join(__DIR, '..', '80-PROJECTS');

function getDeps(pkg) {
  const deps = {};
  for (const [name, version] of [...Object.entries(pkg.dependencies || {}), ...Object.entries(pkg.peerDependencies || {})]) {
    if (!name.startsWith('@types/')) {
      deps[name] = version;
    }
  }
  return deps;
}

function generateGraph(projects) {
  const lines = ['digraph workspace {', '  rankdir=LR;', '  node [shape=box];'];

  for (const proj of projects) {
    const pkgPath = join(WORKSPACE, proj, 'package.json');
    if (!existsSync(pkgPath)) continue;
    try {
      const pkg = JSON.parse(readFileSync(pkgPath, 'utf8'));
      const deps = getDeps(pkg);
      const label = `${proj}\\n(${pkg.version || '?'})`;
      lines.push(`  "${proj}" [label="${label}"];`);
      for (const [dep, ver] of Object.entries(deps)) {
        lines.push(`  "${proj}" -> "${dep}" [label="${ver}"];`);
      }
    } catch {}
  }

  lines.push('}');
  return lines.join('\n');
}

function listProjects() {
  try {
    return readdirSync(WORKSPACE).filter(p => {
      try {
        return existsSync(join(WORKSPACE, p, 'package.json')) &&
               !p.startsWith('.') &&
               !p.includes('ARCHIVED') &&
               !p.includes('-ARCHIVED');
      } catch { return false; }
    });
  } catch { return []; }
}

const args = process.argv.slice(2);
const projects = args.length > 0 ? args : listProjects().slice(0, 10);
const graph = generateGraph(projects);
console.log(graph);

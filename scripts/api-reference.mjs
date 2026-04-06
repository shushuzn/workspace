/**
 * api-reference.mjs — Generate cross-project API reference for the workspace.
 *
 * Scans all 80-PROJECTS for README.md and src/ comments, then generates:
 *   1. docs/workspace-api-ref.md  — full API reference
 *   2. README-index.md           — lightweight workspace README entry point
 *
 * Usage:
 *   node scripts/api-reference.mjs [--output docs/workspace-api-ref.md] [--readme-index]
 */

import { readdirSync, readFileSync, statSync, writeFileSync, existsSync } from 'fs';
import { join, dirname, relative } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const WORKSPACE_ROOT = join(__dirname, '..', '80-PROJECTS');
const OUTPUT_IDX = process.argv.indexOf('--output');
const OUTPUT = OUTPUT_IDX >= 0
  ? process.argv[OUTPUT_IDX + 1]
  : join(__dirname, '..', 'docs', 'workspace-api-ref.md');
const GENERATE_README_INDEX = process.argv.includes('--readme-index');
const README_INDEX_OUTPUT = join(__dirname, '..', 'README-index.md');

const SKIP_DIRS = new Set([
  'node_modules', '.git', 'ARCHIVED', '10-idle-empire-ARCHIVED',
  '10-star-forge-ARCHIVED', '.claude', '.omc', '.github',
]);

const SKIP_PROJECTS = new Set([
  'node_modules', '.git', 'ARCHIVED', '10-idle-empire-ARCHIVED',
  'manifest.schema.json', 'auto-brainstorm-loop.js', 'auto-research-loop.js',
]);

// ─── Scanner ──────────────────────────────────────────────────

function scanProject(projectPath, projectName) {
  const result = {
    name: projectName,
    description: '',
    apis: [],
    commands: [],
    files: [],
    readme: '',
  };

  try {
    // README
    const readmePath = join(projectPath, 'README.md');
    const readme = readFileSync(readmePath, 'utf8').slice(0, 2000);
    result.readme = readme;

    // Extract first paragraph as description
    const descMatch = readme.match(/^#\s+.+\n\n(.+?)(?=\n\n##|\n##|$)/m);
    if (descMatch) result.description = descMatch[1].replace(/\n+/g, ' ').trim();

    // Extract ## API, ## Usage, ## Commands sections
    const sections = readme.split(/^##\s+/m);
    for (const sec of sections.slice(1)) {
      const [title, ...body] = sec.split('\n');
      const content = body.join('\n').slice(0, 500).trim();
      if (/^(API|Usage|Commands|Endpoints|Tools)/i.test(title)) {
        result.apis.push({ section: title.trim(), content });
      }
    }

    // Scan src/
    const srcPath = join(projectPath, 'src');
    if (exists(srcPath)) {
      scanDir(srcPath, '', result);
    }
  } catch (_) {}

  return result;
}

function scanDir(dir, prefix, result) {
  let entries;
  try {
    entries = readdirSync(dir);
  } catch (_) { return; }

  for (const entry of entries) {
    if (entry.startsWith('.') || SKIP_DIRS.has(entry)) continue;
    const fullPath = join(dir, entry);
    try {
      const stat = statSync(fullPath);
      if (stat.isDirectory()) {
        scanDir(fullPath, prefix ? `${prefix}/${entry}` : entry, result);
      } else if (stat.isFile() && /\.(ts|js|mjs|py|sh)$/.test(entry)) {
        const rel = prefix ? `${prefix}/${entry}` : entry;
        result.files.push(rel);

        // Extract JSDoc comments
        if (/\.(ts|js|mjs)$/.test(entry)) {
          try {
            const content = readFileSync(fullPath, 'utf8');
            const jsdocMatches = content.match(/\/\*\*[\s\S]*?\*\//g) || [];
            for (const doc of jsdocMatches.slice(0, 5)) {
              const descMatch = doc.match(/@\w+\s+(.+)/g) || [];
              const desc = descMatch.map(m => m.replace(/@\w+\s+/, '')).join('; ').slice(0, 120);
              if (desc) result.apis.push({ section: rel, content: desc });
            }
          } catch (_) {}
        }
      }
    } catch (_) {}
  }
}

function exists(p) {
  try { return statSync(p) != null; } catch { return false; }
}

// ─── Generator ──────────────────────────────────────────────

function generateMarkdown(projects) {
  const lines = [
    '# Workspace API Reference',
    '',
    `> Auto-generated on ${new Date().toISOString().slice(0, 10)}`,
    '',
    '## Capability Map',
    '',
    '| Project | Description | Key Files |',
    '|---------|-------------|------------|',
  ];

  for (const p of projects) {
    const files = p.files.slice(0, 5).join(', ') + (p.files.length > 5 ? '...' : '');
    const desc = p.description || '(no description)';
    lines.push(`| [${p.name}](#${slug(p.name)}) | ${desc} | \`${files}\` |`);
  }

  lines.push('');
  lines.push('---');
  lines.push('');

  for (const p of projects) {
    lines.push(`## ${p.name}`);
    lines.push('');
    if (p.description) lines.push(`**${p.description}**`);
    lines.push('');
    lines.push('```');
    lines.push(`cd 80-PROJECTS/${p.name}`);
    lines.push('```');
    lines.push('');

    if (p.readme) {
      lines.push('### README Excerpt');
      lines.push('');
      lines.push('```markdown');
      lines.push(p.readme.slice(0, 800));
      lines.push('```');
      lines.push('');
    }

    if (p.apis.length > 0) {
      lines.push('### API Sections');
      lines.push('');
      for (const api of p.apis.slice(0, 5)) {
        lines.push(`**${api.section}**`);
        lines.push('');
        lines.push('```');
        lines.push(api.content.slice(0, 200));
        lines.push('```');
        lines.push('');
      }
    }

    if (p.files.length > 0) {
      lines.push('### Source Files');
      lines.push('');
      for (const f of p.files.slice(0, 10)) {
        lines.push(`- \`${f}\``);
      }
      lines.push('');
    }

    lines.push('---');
    lines.push('');
  }

  return lines.join('\n');
}

function slug(name) {
  return name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
}

// ─── README Index Generator ──────────────────────────────────────

function generateReadmeIndex(projects) {
  const lines = [
    '# Workspace Project Index',
    '',
    `> Auto-generated on ${new Date().toISOString().slice(0, 10)} — run \`node scripts/api-reference.mjs --readme-index\` to update`,
    '',
    '## Projects',
    '',
    '| Project | Category | Description |',
    '|---------|---------|-------------|',
  ];

  for (const p of projects) {
    const desc = (p.description || '').slice(0, 80);
    lines.push(`| [\`${p.name}\`](#${slug(p.name)}) | ${categorize(p)} | ${desc} |`);
  }

  lines.push('');
  lines.push('---');
  lines.push('');

  for (const p of projects) {
    lines.push(`## \`${p.name}\``);
    lines.push('');
    lines.push(`**${p.description || '(no description)'}**`);
    lines.push('');
    const files = p.files.slice(0, 6).map(f => `\`${f}\``).join(', ');
    if (files) lines.push(`**Files**: ${files}`);
    lines.push('');
    lines.push(`\`\`\`\ncd 80-PROJECTS/${p.name}\n\`\`\``);
    lines.push('');
    lines.push('[▲ back to top](#workspace-project-index)');
    lines.push('');
    lines.push('---');
    lines.push('');
  }

  return lines.join('\n');
}

function categorize(project) {
  const name = project.name.toLowerCase();
  const keywords = [...project.apis.map(a => a.section.toLowerCase()), ...project.apis.map(a => a.content.toLowerCase())].join(' ');
  if (keywords.includes('mcp') || name.includes('mcp')) return 'MCP';
  if (keywords.includes('agent') || name.includes('agent')) return 'Agent';
  if (keywords.includes('browser') || keywords.includes('automation') || name.includes('cli')) return 'Browser/CLI';
  if (keywords.includes('trading') || keywords.includes('stock') || name.includes('trading')) return 'Finance';
  if (keywords.includes('news') || keywords.includes('workflow')) return 'News';
  if (keywords.includes('react') || keywords.includes('web') || keywords.includes('ui')) return 'Web';
  return 'Tool';
}

// ─── Main ─────────────────────────────────────────────────────

const projects = [];

let entries;
try {
  entries = readdirSync(WORKSPACE_ROOT);
} catch (e) {
  console.error('Cannot read workspace:', e.message);
  process.exit(1);
}

for (const entry of entries) {
  if (SKIP_PROJECTS.has(entry)) continue;
  if (SKIP_DIRS.has(entry)) continue;
  const projectPath = join(WORKSPACE_ROOT, entry);
  if (!statSync(projectPath).isDirectory()) continue;
  process.stdout.write('.');
  const result = scanProject(projectPath, entry);
  if (result.description || result.apis.length > 0 || result.files.length > 0) {
    projects.push(result);
  }
}

console.log(`\n\nScanned ${projects.length} projects`);

projects.sort((a, b) => a.name.localeCompare(b.name));

const md = generateMarkdown(projects);
writeFileSync(OUTPUT, md, 'utf8');
console.log(`Saved: ${OUTPUT}`);
console.log(`Projects documented: ${projects.length}`);

if (GENERATE_README_INDEX) {
  const idx = generateReadmeIndex(projects);
  writeFileSync(README_INDEX_OUTPUT, idx, 'utf8');
  console.log(`Saved: ${README_INDEX_OUTPUT}`);
}

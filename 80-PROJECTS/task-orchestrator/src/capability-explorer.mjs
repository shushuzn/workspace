/**
 * capability-explorer.ts — Natural language capability discovery for task-orchestrator.
 *
 * Usage:
 *   npx ts-node src/capability-explorer.ts "search GitHub issues"
 *   npx ts-node src/capability-explorer.ts "browse a website"
 *   npx ts-node src/capability-explorer.ts "run a CLI tool"
 */
import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { parseArgs } from 'util';
const __dirname = dirname(fileURLToPath(import.meta.url));
const ADAPTER_CAPABILITIES = [
    {
        adapterType: 'opencli',
        keywords: [
            'browse', 'website', 'webpage', 'navigate', 'click', 'type', 'screenshot',
            'browser', 'extract', 'scrape', 'gui', 'automation', 'headless',
            'bilibili', 'zhihu', 'xiaohongshu', 'twitter', 'social media',
            'chromium', 'cdp', 'dom', 'html extraction',
        ],
        description: 'Browser automation — controls a real Chromium browser via CDP. Best for GUI interaction, scraping dynamic sites, filling forms, taking screenshots.',
        examples: [
            'opencli run "browse https://github.com/issues"',
            'opencli screenshot "https://example.com" --save ./shot.png',
        ],
    },
    {
        adapterType: 'cli-anything',
        keywords: [
            'cli', 'command line', 'terminal', 'bash', 'shell', 'subprocess',
            'tool', 'executable', 'run', 'install', 'python', 'node', 'git',
            'harness', 'software', 'command',
        ],
        description: 'CLI harness execution — runs any registered CLI tool via subprocess. Best for developer tools, git operations, npm/yarn, docker, curl.',
        examples: [
            'task-orchestrator run --adapter cli-anything "git status"',
            'task-orchestrator run --adapter cli-anything "npm test"',
        ],
    },
    {
        adapterType: 'multi-agent-hub',
        keywords: [
            'debate', 'discuss', 'multi-agent', 'agent', 'cognitive', 'reasoning',
            'llm', 'gpt', 'claude', 'openai', 'chat', 'conversation', 'analysis',
            'judge', 'prm', 'grpo', 'reward',
        ],
        description: 'Multi-agent LLM reasoning — spawns multiple LLM agents to debate or analyze a topic. Best for research, decision-making, code review, strategy.',
        examples: [
            'task-orchestrator run --adapter multi-agent-hub "debate: should we use microservices?"',
            'task-orchestrator run --adapter multi-agent-hub "analyze: security of this code"',
        ],
    },
    {
        adapterType: 'swarm',
        keywords: [
            'swarm', 'parallel', 'concurrent', 'orchestrate', 'coordinate',
            'distribute', 'scatter', 'gather', 'broadcast', 'cascading',
            'hierarchical', 'mesh', 'ring topology',
        ],
        description: 'Swarm orchestration — coordinates multiple adapters in parallel or hierarchical patterns. Best for bulk operations, fan-out/fan-in, distributed tasks.',
        examples: [
            'task-orchestrator run --adapter swarm --parallel "[task1, task2, task3]"',
            'task-orchestrator run --adapter swarm --topology hierarchical',
        ],
    },
    {
        adapterType: 'shell',
        keywords: [
            'shell', 'bash', 'exec', 'script', 'batch', 'powershell',
            'raw', 'linux command', 'unix',
        ],
        description: 'Raw shell execution — runs raw shell commands directly. Best for quick scripts, file operations, system commands.',
        examples: [
            'task-orchestrator run --adapter shell "ls -la"',
            'task-orchestrator run --adapter shell "ps aux | grep node"',
        ],
    },
];
// ─── Scoring ──────────────────────────────────────────────────
function scoreMatch(query, cap) {
    const q = query.toLowerCase();
    let score = 0;
    for (const kw of cap.keywords) {
        if (q.includes(kw))
            score += 1;
    }
    return score;
}
function findBestAdapters(query) {
    const scored = ADAPTER_CAPABILITIES.map(cap => ({
        cap,
        score: scoreMatch(query, cap),
    }));
    return scored
        .filter(s => s.score > 0)
        .sort((a, b) => b.score - a.score)
        .map(s => s.cap);
}
// ─── CLI ──────────────────────────────────────────────────────
async function main() {
    const { positionals } = parseArgs({
        args: process.argv.slice(2),
        allowPositionals: true,
    });
    const query = positionals[0] || '';
    if (!query) {
        console.log(`
🤖 Task Orchestrator — Capability Explorer

Usage:
  npx ts-node src/capability-explorer.ts "<intent>"

Examples:
  npx ts-node src/capability-explorer.ts "browse a website"
  npx ts-node src/capability-explorer.ts "search GitHub issues"
  npx ts-node src/capability-explorer.ts "run a CLI tool"
  npx ts-node src/capability-explorer.ts "debate a topic with multiple agents"

Supported adapters: opencli, cli-anything, multi-agent-hub, swarm, shell
`);
        return;
    }
    console.log(`\n🔍 Query: "${query}"\n`);
    console.log('─'.repeat(60));
    const matches = findBestAdapters(query);
    if (matches.length === 0) {
        console.log('\n⚠️  No matching adapter found for this intent.');
        console.log('   Try using: browser, scrape, cli, terminal, multi-agent, debate, swarm, parallel, shell\n');
        return;
    }
    matches.forEach((cap, i) => {
        const medal = i === 0 ? '🥇' : i === 1 ? '🥈' : '🥉';
        console.log(`\n${medal} ${cap.adapterType} (score: ${scoreMatch(query, cap)})`);
        console.log(`   ${cap.description}`);
        console.log(`   Examples:`);
        cap.examples.forEach(ex => console.log(`     → ${ex}`));
    });
    console.log('\n' + '─'.repeat(60));
    console.log(`\n💡 Best match: ${matches[0].adapterType}`);
    console.log(`   Run with: task-orchestrator run --adapter ${matches[0].adapterType} "<task>"\n`);
}
main().catch(err => {
    console.error('Error:', err.message);
    process.exit(1);
});

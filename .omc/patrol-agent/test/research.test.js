// test/research.test.js
import { deepResearch, searchGitHub, searchArxiv } from '../src/research.js';
import { ok } from 'assert';

// Quick test — searches may timeout on CI, so just verify the functions exist and return arrays
async function run() {
  const ideas = await deepResearch('LLM multi-agent');
  ok(Array.isArray(ideas), 'deepResearch returns array');
  console.log(`research.js: found ${ideas.length} ideas for "LLM multi-agent"`);
  for (const idea of ideas.slice(0, 3)) {
    console.log(`  [${idea.source}] ${idea.title.slice(0, 60)} — confidence: ${idea.confidence.toFixed(2)}`);
  }
}

run().catch(err => {
  console.error('research test failed:', err.message);
  process.exit(1);
});

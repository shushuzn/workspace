import { readFileSync, writeFileSync } from 'fs';

const f = readFileSync('.omc/scripts/hook-mcp-consumer.mjs', 'utf8');
const fixed = f
  .replace(/\/\/ \x2d\x2d\x2d Ollama call[\s\S]*?async function callOllama\(prompt, maxTokens = 256\) \{[\s\S]*?return json\.response\?\x2e\x74rim\(\) \|\| '';\s*\}/,
`async function callMinimax(prompt, maxTokens = 256) {
  const apiKey = process.env.MINIMAX_API_KEY;
  if (!apiKey) throw new Error('MINIMAX_API_KEY not set');
  const res = await fetch(MINIMAX_URL, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'Authorization': \`Bearer \${apiKey}\` },
    body: JSON.stringify({ model: MODEL, messages: [{ role: 'user', content: prompt }], max_tokens: maxTokens }),
  });
  if (!res.ok) throw new Error(\`MiniMax \${res.status}: \${await res.text()}\`);
  const json = await res.json();
  return json.choices?.[0]?.message?.content?.trim() || '';
}`)
  .replace(/await callOllama\(/g, 'await callMinimax(')
  .replace(/\/\/ \x2d\x2d\x2d Ollama\x2dpowered summarization/, '// LLM summarization');

writeFileSync('.omc/scripts/hook-mcp-consumer.mjs', fixed);
console.log('done');

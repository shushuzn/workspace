/**
 * Config loader — YAML/JSON + env + defaults, with priority:
 * CLI args > env vars > config file > defaults
 *
 * Supports ai-roundtable.yaml and ai-roundtable.json config files.
 */
import fs from 'fs';
import path from 'path';
import yaml from 'js-yaml';

const CONFIG_FILES = [
  'ai-roundtable.yaml',
  'ai-roundtable.yml',
  'ai-roundtable.json',
];

function loadConfigFile() {
  for (const name of CONFIG_FILES) {
    const filePath = path.join(process.cwd(), name);
    try {
      if (fs.existsSync(filePath)) {
        const raw = fs.readFileSync(filePath, 'utf8');
        if (name.endsWith('.json')) {
          return JSON.parse(raw);
        }
        return yaml.load(raw) || {};
      }
    } catch {
      // skip invalid files
    }
  }
  return {};
}

/**
 * Deep-get a value from an object, returning undefined if not present.
 */
function get(cfg, key) {
  const val = cfg[key];
  return val === undefined ? undefined : val;
}

export function loadConfig() {
  const fileCfg = loadConfigFile();

  // Provider API keys — prefer env, then file
  const minimaxApiKey =
    process.env.MINIMAX_API_KEY ?? get(fileCfg, 'minimaxApiKey');
  const openaiApiKey =
    process.env.OPENAI_API_KEY ?? get(fileCfg, 'openaiApiKey');
  const anthropicApiKey =
    process.env.ANTHROPIC_API_KEY ?? get(fileCfg, 'anthropicApiKey');

  // Provider URLs
  const openaiUrl = process.env.OPENAI_URL ?? get(fileCfg, 'openaiUrl');
  const anthropicUrl =
    process.env.ANTHROPIC_URL ?? get(fileCfg, 'anthropicUrl');

  // Model names
  const minimaxModel =
    process.env.MINIMAX_MODEL ??
    get(fileCfg, 'minimaxModel') ??
    'MiniMax-M2.7-highspeed';
  const openaiModel =
    process.env.OPENAI_MODEL ?? get(fileCfg, 'openaiModel') ?? 'gpt-4o-mini';
  const anthropicModel =
    process.env.ANTHROPIC_MODEL ??
    get(fileCfg, 'anthropicModel') ??
    'claude-sonnet-4-20250514';

  // Ollama
  const ollamaUrl =
    process.env.OLLAMA_URL ??
    get(fileCfg, 'ollamaUrl') ??
    'http://localhost:11434';
  const ollamaModel =
    process.env.OLLAMA_MODEL ?? get(fileCfg, 'ollamaModel') ?? 'llama3.2:1b';
  const useOllama =
    (process.env.USE_OLLAMA !== undefined
      ? process.env.USE_OLLAMA === 'true'
      : get(fileCfg, 'useOllama')) ?? false;

  // Behaviour
  const defaultRounds = get(fileCfg, 'defaultRounds') ?? 5;

  return {
    minimaxApiKey,
    openaiApiKey,
    anthropicApiKey,
    openaiUrl,
    anthropicUrl,
    minimaxModel,
    openaiModel,
    anthropicModel,
    ollamaUrl,
    ollamaModel,
    useOllama,
    defaultRounds,
  };
}

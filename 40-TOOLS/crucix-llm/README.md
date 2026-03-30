# Crucix LLM Provider Module

## Supported Providers

| Provider | Package | Auth |
|----------|---------|------|
| Anthropic (Claude) | `anthropic.mjs` | API Key |
| OpenAI (GPT) | `openai.mjs` | API Key |
| Google Gemini | `gemini.mjs` | API Key |
| OpenRouter | `openrouter.mjs` | API Key |
| Mistral | `mistral.mjs` | API Key |
| MiniMax | `minimax.mjs` | API Key |
| Grok | `grok.mjs` | API Key |
| Ollama | `ollama.mjs` | No key (local) |
| Codex | `codex.mjs` | OAuth ~/.codex/auth.json |

## Usage

```js
import { createLLMProvider } from './index.mjs';

// Create a provider
const llm = createLLMProvider({
  provider: 'anthropic',  // or 'openai', 'gemini', etc.
  apiKey: 'sk-...',
  model: 'claude-sonnet-4-6',  // optional
});

if (!llm) throw new Error('Provider not found');

// Complete a prompt
const result = await llm.complete(
  'You are a helpful assistant.',  // system prompt
  'What is 2+2?',                  // user message
  { maxTokens: 4096, timeout: 60000 }
);

console.log(result.text);
console.log(result.usage);  // { inputTokens, outputTokens }
console.log(result.model);
```

## Zero SDK

All providers use raw `fetch()` — no official SDK dependencies.

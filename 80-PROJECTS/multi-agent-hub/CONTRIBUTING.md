# Contributing to ai-roundtable

## Getting Started

```bash
git clone https://github.com/shushuzn/ai-roundtable.git
cd ai-roundtable
npm install
cp .env.example .env  # fill in your API keys
node index.js "your topic here"
```

## Development

```bash
npm run lint    # check code style
npm run format  # auto-format
npm test        # run tests
```

## Commit Messages

This project uses [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: add new persona type
fix: resolve embedder timeout issue
chore: update dependencies
docs: clarify configuration options
test: add round-trip quality scorer test
```

## Code Style

- ESLint + Prettier enforce style on commit (husky pre-commit hook)
- Max line length: 100 (enforced by Prettier)
- ES2022+ features allowed (Node.js 18+)

## Testing

```bash
node --test tests/
```

Add tests for any new shared utility in `tests/`.

## Pull Request Process

1. Fork and branch: `git checkout -b feat/my-feature`
2. Run `npm test` — must pass
3. Ensure `npm run lint` reports no errors
4. Open PR with a clear description

## Architecture

- `index.js` — CLI entry point, argument parsing, main orchestration loop
- `shared/` — Pure utility modules (no side-effects, tree-shakeable)
  - `chatCache.js` — LRU cache for LLM responses
  - `configLoader.js` — YAML/JSON config file loader
  - `embedder.js` — Text embedding (MiniMax API / Ollama)
  - `conceptJumpTracker.js` — ΔS (concept-jump) tracking per round
  - `qualityScorer.js` — Fluidity / Jump / Balance quality scoring
  - `temperatureScheduler.js` — Cognitive annealing temperature scheduling
  - `rateLimiter.js` — Per-provider request rate limiters
  - `retryUtils.js` — Exponential backoff retry utility
  - `bridgeDiscovery.js` — Cross-topic bridge concept extraction
  - `logger.js` — Structured logging via pino
- `debates/` — Saved debate transcripts (auto-generated)
- `docs/` — Design documents and implementation plans

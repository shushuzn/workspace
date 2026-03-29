# Agent Memory Mesh

## Concept

A distributed memory mesh for AI agents. Agents share context, memories, and learned patterns across a peer-to-peer mesh network. Each agent contributes observations, and the mesh aggregates collective intelligence.

## Architecture

- **Memory Node**: Each agent runs a memory node that stores local observations
- **Mesh Protocol**: Gossip-based protocol for sharing memories across agents
- **Pattern Discovery**: Automatically identifies recurring patterns across agent experiences
- **Context Injection**: Seamlessly injects relevant memories from the mesh into agent prompts

## Core Features

1. **Distributed Memory Store**: Each agent maintains local memory with vector embeddings
2. **Gossip Protocol**: Agents periodically share recent memories with neighbors
3. **Semantic Search**: Query the entire mesh for relevant memories from any agent
4. **Pattern Bank**: Shared repository of discovered patterns and best practices
5. **Memory TTL**: Automatic expiration of stale memories to prevent bloat

## Tech Stack

- Node.js (ESM)
- better-sqlite3 for local persistence
- In-memory vectors for semantic search
- libp2p for peer-to-peer communication (future)
- HMAC-SHA256 for memory authenticity

## Status

Planning phase - architecture being defined.

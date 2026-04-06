<script>
  import { onMount, onDestroy } from 'svelte';
  import { gameStore } from '../stores/gameStore.js';

  let nodes = [];
  let edges = [];
  let width = 800;
  let height = 500;
  let container;

  // Subscribe to game store
  const unsubscribe = gameStore.subscribe(state => {
    render(state);
  });

  onDestroy(() => unsubscribe());

  function render(state) {
    const { agents, battleAnalytics } = state;
    if (!agents || agents.length === 0) {
      nodes = [];
      edges = [];
      return;
    }

    // Build nodes from agents
    nodes = agents.map(a => ({
      id: a.id,
      name: a.name,
      power: calcPower(a),
      level: a.level || 1,
      wins: a.tournamentWins || 0,
      losses: a.tournamentLosses || 0,
    }));

    // Build edges from battle history
    edges = [];
    const history = battleAnalytics?.history || [];
    for (const battle of history.slice(0, 50)) { // latest 50
      if (battle.winnerId && battle.loserId) {
        edges.push({
          winner: battle.winnerId,
          loser: battle.loserId,
          turns: battle.turnsElapsed || 1,
        });
      }
    }
  }

  function calcPower(agent) {
    if (!agent.stats) return 0;
    const { intelligence = 0, speed = 0, creativity = 0, endurance = 0 } = agent.stats;
    const level = agent.level || 1;
    return Math.floor((intelligence * 1.5 + speed * 1.2 + creativity * 1.0 + endurance * 1.8) * (1 + level * 0.1));
  }

  // Force-directed layout (simple spring model)
  function layout(nodes, edges, w, h) {
    if (nodes.length === 0) return [];

    // Initialize positions randomly
    const positioned = nodes.map((n, i) => ({
      ...n,
      x: 100 + (i % 5) * 120,
      y: 100 + Math.floor(i / 5) * 100,
      vx: 0,
      vy: 0,
    }));

    const ITER = 80;
    const REPULSE = 8000;
    const ATTRACT = 0.04;
    const DAMP = 0.85;

    for (let iter = 0; iter < ITER; iter++) {
      // Repulsion between all nodes
      for (let i = 0; i < positioned.length; i++) {
        for (let j = i + 1; j < positioned.length; j++) {
          const a = positioned[i], b = positioned[j];
          const dx = b.x - a.x;
          const dy = b.y - a.y;
          const dist = Math.sqrt(dx * dx + dy * dy) || 1;
          const force = REPULSE / (dist * dist);
          const fx = (dx / dist) * force;
          const fy = (dy / dist) * force;
          a.vx -= fx; a.vy -= fy;
          b.vx += fx; b.vy += fy;
        }
      }

      // Attraction along edges
      for (const edge of edges) {
        const src = positioned.find(n => n.id === edge.winner);
        const tgt = positioned.find(n => n.id === edge.loser);
        if (!src || !tgt) continue;
        const dx = tgt.x - src.x;
        const dy = tgt.y - src.y;
        src.vx += dx * ATTRACT; src.vy += dy * ATTRACT;
        tgt.vx -= dx * ATTRACT; tgt.vy -= dy * ATTRACT;
      }

      // Center gravity
      for (const n of positioned) {
        n.vx += (w / 2 - n.x) * 0.01;
        n.vy += (h / 2 - n.y) * 0.01;
      }

      // Apply velocity with damping
      for (const n of positioned) {
        n.vx *= DAMP; n.vy *= DAMP;
        n.x += n.vx; n.y += n.vy;
        n.x = Math.max(30, Math.min(w - 30, n.x));
        n.y = Math.max(30, Math.min(h - 30, n.y));
      }
    }

    return positioned;
  }

  // Reactive derived positions
  $: positioned = layout(nodes, edges, width, height);

  // Color by win rate
  function nodeColor(node) {
    const total = node.wins + node.losses;
    if (total === 0) return '#6b7280'; // gray
    const wr = node.wins / total;
    if (wr >= 0.7) return '#4ade80'; // green
    if (wr >= 0.4) return '#fbbf24'; // yellow
    return '#f87171'; // red
  }

  // Node radius by power
  function nodeRadius(power) {
    return 18 + Math.sqrt(power) * 0.8;
  }

  onMount(() => {
    const ro = new ResizeObserver(entries => {
      for (const e of entries) {
        width = e.contentRect.width || 800;
        height = Math.max(400, e.contentRect.height || 500);
      }
    });
    if (container) ro.observe(container);
    return () => ro.disconnect();
  });
</script>

<div class="agent-graph" bind:this={container}>
  {#if nodes.length === 0}
    <div class="empty">No agents yet. Create agents to see the network graph.</div>
  {:else}
    <svg {width} {height}>
      <!-- Edges -->
      {#each edges as edge}
        {@const src = positioned.find(n => n.id === edge.winner)}
        {@const tgt = positioned.find(n => n.id === edge.loser)}
        {#if src && tgt}
          <line
            x1={src.x} y1={src.y}
            x2={tgt.x} y2={tgt.y}
            stroke="#374151"
            stroke-width="1.5"
            stroke-opacity="0.6"
          />
        {/if}
      {/each}

      <!-- Nodes -->
      {#each positioned as node}
        {@const r = nodeRadius(node.power)}
        <!-- Glow ring for high win rate -->
        {#if node.wins + node.losses > 0 && node.wins / (node.wins + node.losses) >= 0.7}
          <circle cx={node.x} cy={node.y} r={r + 6} fill="none" stroke="#4ade80" stroke-width="2" stroke-opacity="0.3" />
        {/if}

        <circle
          cx={node.x} cy={node.y} r={r}
          fill={nodeColor(node)}
          fill-opacity="0.85"
          stroke={nodeColor(node)}
          stroke-width="2"
          stroke-opacity="0.5"
        />

        <!-- Level badge -->
        <text
          x={node.x} y={node.y + r + 14}
          text-anchor="middle"
          font-size="11"
          fill="#9ca3af"
        >Lv.{node.level}</text>

        <!-- Name -->
        <text
          x={node.x} y={node.y - r - 6}
          text-anchor="middle"
          font-size="12"
          font-weight="600"
          fill="#f3f4f6"
        >{node.name.length > 12 ? node.name.slice(0, 10) + '…' : node.name}</text>

        <!-- Power -->
        <text
          x={node.x} y={node.y + 4}
          text-anchor="middle"
          font-size="10"
          fill="#fff"
          font-family="monospace"
        >{node.power}</text>

        <!-- W/L -->
        <text
          x={node.x} y={node.y + 14}
          text-anchor="middle"
          font-size="9"
          fill="#d1d5db"
        >{node.wins}W/{node.losses}L</text>
      {/each}
    </svg>

    <div class="legend">
      <span class="dot" style="background:#4ade80"></span> High Win Rate (≥70%)
      <span class="dot" style="background:#fbbf24"></span> Medium (40-70%)
      <span class="dot" style="background:#f87171"></span> Low (&lt;40%)
      <span class="dot" style="background:#6b7280"></span> No battles
    </div>
  {/if}
</div>

<style>
  .agent-graph {
    width: 100%;
    height: 100%;
    min-height: 300px;
    background: #111827;
    border-radius: 12px;
    overflow: hidden;
  }

  svg {
    display: block;
  }

  .empty {
    display: flex;
    align-items: center;
    justify-content: center;
    height: 300px;
    color: #6b7280;
    font-size: 14px;
  }

  .legend {
    display: flex;
    gap: 16px;
    padding: 10px 16px;
    font-size: 11px;
    color: #9ca3af;
    background: #0f1117;
    flex-wrap: wrap;
  }

  .dot {
    display: inline-block;
    width: 10px;
    height: 10px;
    border-radius: 50%;
    margin-right: 4px;
    vertical-align: middle;
  }
</style>

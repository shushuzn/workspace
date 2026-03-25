// Building configurations with tiers - Balanced Economy

export const BUILDINGS = [
  // Tier 1 - Solar System (always unlocked) - Early game optimized
  { id: 'solar_panel', name: 'Solar Panel', tier: 1, baseProduction: 0.5, baseCost: 5, costMultiplier: 1.12, description: 'Harvests energy from the sun', emoji: '☀️' },
  { id: 'moon_mine', name: 'Moon Mine', tier: 1, baseProduction: 3, baseCost: 50, costMultiplier: 1.12, description: 'Extracts helium-3 from lunar soil', emoji: '🌙' },
  { id: 'mars_refinery', name: 'Mars Refinery', tier: 1, baseProduction: 15, baseCost: 500, costMultiplier: 1.12, description: 'Processes Martian minerals', emoji: '🔴' },
  { id: 'asteroid_belt', name: 'Asteroid Belt', tier: 1, baseProduction: 80, baseCost: 5000, costMultiplier: 1.12, description: 'Mines platinum from asteroids', emoji: '🪨' },
  { id: 'interstellar_quarry', name: 'Interstellar Quarry', tier: 1, baseProduction: 400, baseCost: 50000, costMultiplier: 1.12, description: 'Extracts dark matter', emoji: '💎' },

  // Tier 2 - Nebula - Mid game
  { id: 'nebula_harvester', name: 'Nebula Harvester', tier: 2, baseProduction: 2000, baseCost: 500000, costMultiplier: 1.14, description: 'Collects cosmic dust', emoji: '🌫️' },
  { id: 'plasma_converter', name: 'Plasma Converter', tier: 2, baseProduction: 10000, baseCost: 8000000, costMultiplier: 1.14, description: 'Converts hydrogen to plasma', emoji: '🔥' },
  { id: 'stellar_engine', name: 'Stellar Engine', tier: 2, baseProduction: 50000, baseCost: 150000000, costMultiplier: 1.14, description: 'Harnesses stellar winds', emoji: '⭐' },
  { id: 'quantum_well', name: 'Quantum Well', tier: 2, baseProduction: 250000, baseCost: 3000000000, costMultiplier: 1.14, description: 'Quantum energy extraction', emoji: '🔮' },

  // Tier 3 - Galactic - Late game
  { id: 'dysons_sphere', name: "Dyson's Sphere", tier: 3, baseProduction: 1000000, baseCost: 15000000000, costMultiplier: 1.15, description: 'Encloses a star completely', emoji: '🟡' },
  { id: 'black_hole_extractor', name: 'Black Hole Extractor', tier: 3, baseProduction: 5000000, baseCost: 250000000000, costMultiplier: 1.15, description: 'Harvests Hawking radiation', emoji: '🕳️' },
  { id: 'galactic_core_tap', name: 'Galactic Core Tap', tier: 3, baseProduction: 25000000, baseCost: 5000000000000, costMultiplier: 1.15, description: 'Taps the galactic center', emoji: '🌌' },
  { id: 'dimension_rift', name: 'Dimension Rift', tier: 3, baseProduction: 100000000, baseCost: 100000000000000, costMultiplier: 1.15, description: 'Opens portals to other dimensions', emoji: '🌀' },

  // Tier 4 - Cosmic - End game
  { id: 'universe_seed', name: 'Universe Seed', tier: 4, baseProduction: 500000000, baseCost: 1e15, costMultiplier: 1.15, description: 'Plants a new universe', emoji: '🌱' },
  { id: 'reality_anchor', name: 'Reality Anchor', tier: 4, baseProduction: 2500000000, baseCost: 2e16, costMultiplier: 1.15, description: 'Stabilizes reality tears', emoji: '⚓' },
  { id: 'infinity_engine', name: 'Infinity Engine', tier: 4, baseProduction: 10000000000, baseCost: 5e17, costMultiplier: 1.15, description: 'Harnesses infinite energy', emoji: '♾️' },

  // Tier 5 - Multiverse - Post-game
  { id: 'multiverse_fabric', name: 'Multiverse Fabric', tier: 5, baseProduction: 5e10, baseCost: 1e19, costMultiplier: 1.16, description: 'Weaves the fabric of realities', emoji: '🕸️' },
  { id: 'omniverse_well', name: 'Omniverse Well', tier: 5, baseProduction: 2e11, baseCost: 2e20, costMultiplier: 1.16, description: 'Taps infinite parallel universes', emoji: '🌐' },
  { id: 'cosmic_string', name: 'Cosmic String', tier: 5, baseProduction: 1e12, baseCost: 5e21, costMultiplier: 1.16, description: 'Harvests cosmic string vibrations', emoji: '➿' },
  { id: 'void_extractor', name: 'Void Extractor', tier: 5, baseProduction: 5e12, baseCost: 1e23, costMultiplier: 1.16, description: 'Extracts energy from the void', emoji: '⬛' },

  // Tier 6 - Ultimate Universe - Max tier
  { id: 'transcendence_core', name: 'Transcendence Core', tier: 6, baseProduction: 2e14, baseCost: 1e25, costMultiplier: 1.18, description: 'Transcends all reality', emoji: '💫' },
  { id: 'celestial_furnace', name: 'Celestial Furnace', tier: 6, baseProduction: 1e15, baseCost: 2e26, costMultiplier: 1.18, description: 'Burns with primordial fire', emoji: '🔥' },
  { id: 'entropy_reverser', name: 'Entropy Reverser', tier: 6, baseProduction: 5e15, baseCost: 5e27, costMultiplier: 1.18, description: 'Reverses the flow of time', emoji: '⏳' },
  { id: 'existential_engine', name: 'Existential Engine', tier: 6, baseProduction: 2e16, baseCost: 1e29, costMultiplier: 1.18, description: 'Creates existence itself', emoji: '✨' },
  { id: 'prime_creator', name: 'Prime Creator', tier: 6, baseProduction: 1e17, baseCost: 2e30, costMultiplier: 1.18, description: 'The origin of all things', emoji: '🌟' },
];

export const TIERS = [
  { id: 1, name: 'Solar System', color: '#ffd700', unlockCost: 0 },
  { id: 2, name: 'Nebula', color: '#ff69b4', unlockCost: 100000 },
  { id: 3, name: 'Galactic', color: '#9370db', unlockCost: 100000000 },
  { id: 4, name: 'Cosmic', color: '#00ffff', unlockCost: 1e14 },
  { id: 5, name: 'Multiverse', color: '#ff4500', unlockCost: 1e18 },
  { id: 6, name: 'Ultimate', color: '#ff00ff', unlockCost: 1e22 },
];

export function getBuildingCost(building, owned, prestigeMultiplier = 1, costReduction = 0) {
  return Math.floor(building.baseCost * Math.pow(building.costMultiplier, owned) / prestigeMultiplier * (1 - costReduction));
}

export function getBuildingProduction(building, owned, efficiencyBonus = 0) {
  return building.baseProduction * owned * (1 + efficiencyBonus);
}

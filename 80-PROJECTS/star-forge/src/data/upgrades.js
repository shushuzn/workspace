// Upgrade configurations

export const UPGRADES = [
  // Solar Panel upgrades
  { id: 'solar_1', buildingId: 'solar_panel', name: 'Improved Photovoltaics', cost: 100, effect: { type: 'efficiency', value: 1 }, description: '+100% Solar Panel output' },
  { id: 'solar_2', buildingId: 'solar_panel', name: 'Quantum Cells', cost: 1000, effect: { type: 'efficiency', value: 2 }, description: '+200% Solar Panel output' },
  { id: 'solar_3', buildingId: 'solar_panel', name: 'Antimatter Catalysis', cost: 10000, effect: { type: 'efficiency', value: 4 }, description: '+400% Solar Panel output' },
  { id: 'solar_cost', buildingId: 'solar_panel', name: 'Mass Production', cost: 5000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Solar Panel cost' },

  // Moon Mine upgrades
  { id: 'moon_1', buildingId: 'moon_mine', name: 'Deep Drilling', cost: 1000, effect: { type: 'efficiency', value: 1 }, description: '+100% Moon Mine output' },
  { id: 'moon_2', buildingId: 'moon_mine', name: 'Robotic Workers', cost: 10000, effect: { type: 'efficiency', value: 2 }, description: '+200% Moon Mine output' },
  { id: 'moon_3', buildingId: 'moon_mine', name: 'He3 Fusion', cost: 100000, effect: { type: 'efficiency', value: 4 }, description: '+400% Moon Mine output' },
  { id: 'moon_cost', buildingId: 'moon_mine', name: 'Efficient Excavation', cost: 50000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Moon Mine cost' },

  // Mars Refinery upgrades
  { id: 'mars_1', buildingId: 'mars_refinery', name: 'Advanced Smelting', cost: 11000, effect: { type: 'efficiency', value: 1 }, description: '+100% Mars Refinery output' },
  { id: 'mars_2', buildingId: 'mars_refinery', name: 'Nanite Processing', cost: 110000, effect: { type: 'efficiency', value: 2 }, description: '+200% Mars Refinery output' },
  { id: 'mars_3', buildingId: 'mars_refinery', name: 'Planetary Core Tap', cost: 1100000, effect: { type: 'efficiency', value: 4 }, description: '+400% Mars Refinery output' },
  { id: 'mars_cost', buildingId: 'mars_refinery', name: 'Logistics Network', cost: 550000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Mars Refinery cost' },

  // Asteroid Belt upgrades
  { id: 'asteroid_1', buildingId: 'asteroid_belt', name: 'Orbital Drills', cost: 120000, effect: { type: 'efficiency', value: 1 }, description: '+100% Asteroid Belt output' },
  { id: 'asteroid_2', buildingId: 'asteroid_belt', name: 'Magnetic Tractors', cost: 1200000, effect: { type: 'efficiency', value: 2 }, description: '+200% Asteroid Belt output' },
  { id: 'asteroid_3', buildingId: 'asteroid_belt', name: 'Asteroid Restructuring', cost: 12000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Asteroid Belt output' },
  { id: 'asteroid_cost', buildingId: 'asteroid_belt', name: 'Mining Guild', cost: 6000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Asteroid Belt cost' },

  // Interstellar Quarry upgrades
  { id: 'interstellar_1', buildingId: 'interstellar_quarry', name: 'Dark Energy Harvest', cost: 1300000, effect: { type: 'efficiency', value: 1 }, description: '+100% Interstellar Quarry output' },
  { id: 'interstellar_2', buildingId: 'interstellar_quarry', name: 'Wormhole Transport', cost: 13000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Interstellar Quarry output' },
  { id: 'interstellar_3', buildingId: 'interstellar_quarry', name: 'Dimension Siphon', cost: 130000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Interstellar Quarry output' },
  { id: 'interstellar_cost', buildingId: 'interstellar_quarry', name: 'Quantum Logistics', cost: 65000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Interstellar Quarry cost' },

  // Dyson's Sphere upgrades
  { id: 'dyson_1', buildingId: 'dysons_sphere', name: 'Phase 2 Construction', cost: 14000000, effect: { type: 'efficiency', value: 1 }, description: '+100% Dyson Sphere output' },
  { id: 'dyson_2', buildingId: 'dysons_sphere', name: 'Swarm Optimization', cost: 140000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Dyson Sphere output' },
  { id: 'dyson_3', buildingId: 'dysons_sphere', name: 'Stellar Engineering', cost: 1400000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Dyson Sphere output' },
  { id: 'dyson_cost', buildingId: 'dysons_sphere', name: 'Industrial Scaling', cost: 700000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Dyson Sphere cost' },

  // Stellar Furnace upgrades
  { id: 'stellar_1', buildingId: 'stellar_furnace', name: 'Heavy Fusion', cost: 200000000, effect: { type: 'efficiency', value: 1 }, description: '+100% Stellar Furnace output' },
  { id: 'stellar_2', buildingId: 'stellar_furnace', name: 'Magnetized Bottles', cost: 2000000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Stellar Furnace output' },
  { id: 'stellar_3', buildingId: 'stellar_furnace', name: 'Q-Josephson Junctions', cost: 20000000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Stellar Furnace output' },
  { id: 'stellar_cost', buildingId: 'stellar_furnace', name: 'Plasma Economics', cost: 10000000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Stellar Furnace cost' },

  // Black Hole Extractor upgrades
  { id: 'blackhole_1', buildingId: 'black_hole_extractor', name: 'Hawking Radiation', cost: 3300000000, effect: { type: 'efficiency', value: 1 }, description: '+100% Black Hole Extractor output' },
  { id: 'blackhole_2', buildingId: 'black_hole_extractor', name: 'Ergosphere Tapping', cost: 33000000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Black Hole Extractor output' },
  { id: 'blackhole_3', buildingId: 'black_hole_extractor', name: 'Singularity Control', cost: 330000000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Black Hole Extractor output' },
  { id: 'blackhole_cost', buildingId: 'black_hole_extractor', name: 'Gravitational Economics', cost: 165000000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Black Hole Extractor cost' },

  // Dimension Rift upgrades
  { id: 'dimension_1', buildingId: 'dimension_rift', name: 'Multi-verse Survey', cost: 51000000000, effect: { type: 'efficiency', value: 1 }, description: '+100% Dimension Rift output' },
  { id: 'dimension_2', buildingId: 'dimension_rift', name: 'Parallel Extraction', cost: 510000000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Dimension Rift output' },
  { id: 'dimension_3', buildingId: 'dimension_rift', name: 'Omniverse Tap', cost: 5100000000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Dimension Rift output' },
  { id: 'dimension_cost', buildingId: 'dimension_rift', name: 'Trans-dimensional Commerce', cost: 2550000000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Dimension Rift cost' },

  // Global upgrades
  { id: 'global_1', name: 'Energy Research I', cost: 50000, effect: { type: 'global_efficiency', value: 0.1 }, description: '+10% all production' },
  { id: 'global_2', name: 'Energy Research II', cost: 500000, effect: { type: 'global_efficiency', value: 0.25 }, description: '+25% all production' },
  { id: 'global_3', name: 'Energy Research III', cost: 5000000, effect: { type: 'global_efficiency', value: 0.5 }, description: '+50% all production' },
  { id: 'global_4', name: 'Energy Research IV', cost: 50000000, effect: { type: 'global_efficiency', value: 1 }, description: '+100% all production' },
  { id: 'global_5', name: 'Energy Research V', cost: 500000000, effect: { type: 'global_efficiency', value: 2 }, description: '+200% all production' },
  { id: 'click_1', name: 'Enhanced Clicking', cost: 100, effect: { type: 'click_power', value: 1 }, description: '+1 energy per click' },
  { id: 'click_2', name: 'Advanced Clicking', cost: 1000, effect: { type: 'click_power', value: 9 }, description: '+10 energy per click' },
  { id: 'click_3', name: 'Quantum Clicking', cost: 10000, effect: { type: 'click_power', value: 99 }, description: '+100 energy per click' },
  { id: 'click_4', name: 'Multiverse Clicking', cost: 100000, effect: { type: 'click_power', value: 999 }, description: '+1000 energy per click' },
];

export function getUpgradeEffect(upgrade, currentOwned) {
  switch (upgrade.effect.type) {
    case 'efficiency':
      return upgrade.effect.value * currentOwned;
    case 'global_efficiency':
    case 'click_power':
    case 'cost_reduction':
      return upgrade.effect.value;
    default:
      return 0;
  }
}

// Comprehensive upgrade system

export const UPGRADES = [
  // ============ TIER 1 BUILDING UPGRADES ============
  // Solar Panel
  { id: 'solar_1', buildingId: 'solar_panel', name: 'Improved Photovoltaics', cost: 100, effect: { type: 'efficiency', value: 1 }, description: '+100% Solar Panel output', tier: 1 },
  { id: 'solar_2', buildingId: 'solar_panel', name: 'Quantum Cells', cost: 1000, effect: { type: 'efficiency', value: 2 }, description: '+200% Solar Panel output', tier: 1 },
  { id: 'solar_3', buildingId: 'solar_panel', name: 'Antimatter Catalysis', cost: 10000, effect: { type: 'efficiency', value: 4 }, description: '+400% Solar Panel output', tier: 1 },
  { id: 'solar_cost', buildingId: 'solar_panel', name: 'Mass Production', cost: 5000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Solar Panel cost', tier: 1 },
  { id: 'solar_auto', buildingId: 'solar_panel', name: 'Auto Solar', cost: 50000, effect: { type: 'auto_buy', value: 1 }, description: 'Auto-buy 1 Solar Panel/s', tier: 1 },

  // Moon Mine
  { id: 'moon_1', buildingId: 'moon_mine', name: 'Deep Drilling', cost: 1000, effect: { type: 'efficiency', value: 1 }, description: '+100% Moon Mine output', tier: 1 },
  { id: 'moon_2', buildingId: 'moon_mine', name: 'Robotic Workers', cost: 10000, effect: { type: 'efficiency', value: 2 }, description: '+200% Moon Mine output', tier: 1 },
  { id: 'moon_3', buildingId: 'moon_mine', name: 'He3 Fusion', cost: 100000, effect: { type: 'efficiency', value: 4 }, description: '+400% Moon Mine output', tier: 1 },
  { id: 'moon_cost', buildingId: 'moon_mine', name: 'Efficient Excavation', cost: 50000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Moon Mine cost', tier: 1 },
  { id: 'moon_auto', buildingId: 'moon_mine', name: 'Auto Mining', cost: 500000, effect: { type: 'auto_buy', value: 1 }, description: 'Auto-buy 1 Moon Mine/s', tier: 1 },

  // Mars Refinery
  { id: 'mars_1', buildingId: 'mars_refinery', name: 'Advanced Smelting', cost: 11000, effect: { type: 'efficiency', value: 1 }, description: '+100% Mars Refinery output', tier: 1 },
  { id: 'mars_2', buildingId: 'mars_refinery', name: 'Nanite Processing', cost: 110000, effect: { type: 'efficiency', value: 2 }, description: '+200% Mars Refinery output', tier: 1 },
  { id: 'mars_3', buildingId: 'mars_refinery', name: 'Planetary Core Tap', cost: 1100000, effect: { type: 'efficiency', value: 4 }, description: '+400% Mars Refinery output', tier: 1 },
  { id: 'mars_cost', buildingId: 'mars_refinery', name: 'Logistics Network', cost: 550000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Mars Refinery cost', tier: 1 },
  { id: 'mars_auto', buildingId: 'mars_refinery', name: 'Auto Refining', cost: 5500000, effect: { type: 'auto_buy', value: 1 }, description: 'Auto-buy 1 Mars Refinery/s', tier: 1 },

  // Asteroid Belt
  { id: 'asteroid_1', buildingId: 'asteroid_belt', name: 'Orbital Drills', cost: 120000, effect: { type: 'efficiency', value: 1 }, description: '+100% Asteroid Belt output', tier: 1 },
  { id: 'asteroid_2', buildingId: 'asteroid_belt', name: 'Magnetic Tractors', cost: 1200000, effect: { type: 'efficiency', value: 2 }, description: '+200% Asteroid Belt output', tier: 1 },
  { id: 'asteroid_3', buildingId: 'asteroid_belt', name: 'Asteroid Restructuring', cost: 12000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Asteroid Belt output', tier: 1 },
  { id: 'asteroid_cost', buildingId: 'asteroid_belt', name: 'Mining Guild', cost: 6000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Asteroid Belt cost', tier: 1 },
  { id: 'asteroid_auto', buildingId: 'asteroid_belt', name: 'Auto Mining Fleet', cost: 60000000, effect: { type: 'auto_buy', value: 1 }, description: 'Auto-buy 1 Asteroid Belt/s', tier: 1 },

  // Interstellar Quarry
  { id: 'interstellar_1', buildingId: 'interstellar_quarry', name: 'Dark Energy Harvest', cost: 1300000, effect: { type: 'efficiency', value: 1 }, description: '+100% Interstellar Quarry output', tier: 1 },
  { id: 'interstellar_2', buildingId: 'interstellar_quarry', name: 'Wormhole Transport', cost: 13000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Interstellar Quarry output', tier: 1 },
  { id: 'interstellar_3', buildingId: 'interstellar_quarry', name: 'Dimension Siphon', cost: 130000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Interstellar Quarry output', tier: 1 },
  { id: 'interstellar_cost', buildingId: 'interstellar_quarry', name: 'Quantum Logistics', cost: 65000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Interstellar Quarry cost', tier: 1 },
  { id: 'interstellar_auto', buildingId: 'interstellar_quarry', name: 'Auto Wormhole', cost: 650000000, effect: { type: 'auto_buy', value: 1 }, description: 'Auto-buy 1 Interstellar Quarry/s', tier: 1 },

  // ============ TIER 2 BUILDING UPGRADES ============
  { id: 'nebula_1', buildingId: 'nebula_harvester', name: 'Nebula Expansion', cost: 14000000, effect: { type: 'efficiency', value: 1 }, description: '+100% Nebula Harvester output', tier: 2 },
  { id: 'nebula_2', buildingId: 'nebula_harvester', name: 'Cosmic Dust Cloud', cost: 140000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Nebula Harvester output', tier: 2 },
  { id: 'nebula_3', buildingId: 'nebula_harvester', name: 'Nebula Compression', cost: 1400000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Nebula Harvester output', tier: 2 },
  { id: 'nebula_cost', buildingId: 'nebula_harvester', name: 'Nebula Rights', cost: 700000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Nebula Harvester cost', tier: 2 },

  { id: 'plasma_1', buildingId: 'plasma_converter', name: 'Plasma Intensification', cost: 200000000, effect: { type: 'efficiency', value: 1 }, description: '+100% Plasma Converter output', tier: 2 },
  { id: 'plasma_2', buildingId: 'plasma_converter', name: 'Fusion Amplifier', cost: 2000000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Plasma Converter output', tier: 2 },
  { id: 'plasma_3', buildingId: 'plasma_converter', name: 'Matter Converter', cost: 20000000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Plasma Converter output', tier: 2 },
  { id: 'plasma_cost', buildingId: 'plasma_converter', name: 'Plasma Economics', cost: 10000000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Plasma Converter cost', tier: 2 },

  { id: 'stellar_1', buildingId: 'stellar_engine', name: 'Solar Sailing', cost: 3300000000, effect: { type: 'efficiency', value: 1 }, description: '+100% Stellar Engine output', tier: 2 },
  { id: 'stellar_2', buildingId: 'stellar_engine', name: 'Coronal Loops', cost: 33000000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Stellar Engine output', tier: 2 },
  { id: 'stellar_3', buildingId: 'stellar_engine', name: 'Corona Heating', cost: 330000000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Stellar Engine output', tier: 2 },
  { id: 'stellar_cost', buildingId: 'stellar_engine', name: 'Stellar Wind Rights', cost: 165000000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Stellar Engine cost', tier: 2 },

  { id: 'quantum_1', buildingId: 'quantum_well', name: 'Quantum Entanglement', cost: 51000000000, effect: { type: 'efficiency', value: 1 }, description: '+100% Quantum Well output', tier: 2 },
  { id: 'quantum_2', buildingId: 'quantum_well', name: 'Quantum Tunneling', cost: 510000000000, effect: { type: 'efficiency', value: 2 }, description: '+200% Quantum Well output', tier: 2 },
  { id: 'quantum_3', buildingId: 'quantum_well', name: 'Quantum Foam Harvest', cost: 5100000000000, effect: { type: 'efficiency', value: 4 }, description: '+400% Quantum Well output', tier: 2 },
  { id: 'quantum_cost', buildingId: 'quantum_well', name: 'Quantum Rights', cost: 2550000000000, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Quantum Well cost', tier: 2 },

  // ============ TIER 3 BUILDING UPGRADES ============
  { id: 'dyson_1', buildingId: 'dysons_sphere', name: 'Phase 2 Construction', cost: 1.4e11, effect: { type: 'efficiency', value: 1 }, description: '+100% Dyson Sphere output', tier: 3 },
  { id: 'dyson_2', buildingId: 'dysons_sphere', name: 'Swarm Optimization', cost: 1.4e12, effect: { type: 'efficiency', value: 2 }, description: '+200% Dyson Sphere output', tier: 3 },
  { id: 'dyson_3', buildingId: 'dysons_sphere', name: 'Stellar Engineering', cost: 1.4e13, effect: { type: 'efficiency', value: 4 }, description: '+400% Dyson Sphere output', tier: 3 },
  { id: 'dyson_cost', buildingId: 'dysons_sphere', name: 'Industrial Scaling', cost: 7e12, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Dyson Sphere cost', tier: 3 },

  { id: 'blackhole_1', buildingId: 'black_hole_extractor', name: 'Hawking Radiation', cost: 2e12, effect: { type: 'efficiency', value: 1 }, description: '+100% Black Hole Extractor output', tier: 3 },
  { id: 'blackhole_2', buildingId: 'black_hole_extractor', name: 'Ergosphere Tapping', cost: 2e13, effect: { type: 'efficiency', value: 2 }, description: '+200% Black Hole Extractor output', tier: 3 },
  { id: 'blackhole_3', buildingId: 'black_hole_extractor', name: 'Singularity Control', cost: 2e14, effect: { type: 'efficiency', value: 4 }, description: '+400% Black Hole Extractor output', tier: 3 },
  { id: 'blackhole_cost', buildingId: 'black_hole_extractor', name: 'Gravitational Economics', cost: 1e14, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Black Hole Extractor cost', tier: 3 },

  { id: 'galactic_1', buildingId: 'galactic_core_tap', name: 'Core Survey', cost: 3.3e13, effect: { type: 'efficiency', value: 1 }, description: '+100% Galactic Core Tap output', tier: 3 },
  { id: 'galactic_2', buildingId: 'galactic_core_tap', name: 'Core Extraction', cost: 3.3e14, effect: { type: 'efficiency', value: 2 }, description: '+200% Galactic Core Tap output', tier: 3 },
  { id: 'galactic_3', buildingId: 'galactic_core_tap', name: 'Galactic Heart', cost: 3.3e15, effect: { type: 'efficiency', value: 4 }, description: '+400% Galactic Core Tap output', tier: 3 },
  { id: 'galactic_cost', buildingId: 'galactic_core_tap', name: 'Galactic Charter', cost: 1.65e15, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Galactic Core Tap cost', tier: 3 },

  { id: 'dimension_1', buildingId: 'dimension_rift', name: 'Multi-verse Survey', cost: 5.1e14, effect: { type: 'efficiency', value: 1 }, description: '+100% Dimension Rift output', tier: 3 },
  { id: 'dimension_2', buildingId: 'dimension_rift', name: 'Parallel Extraction', cost: 5.1e15, effect: { type: 'efficiency', value: 2 }, description: '+200% Dimension Rift output', tier: 3 },
  { id: 'dimension_3', buildingId: 'dimension_rift', name: 'Omniverse Tap', cost: 5.1e16, effect: { type: 'efficiency', value: 4 }, description: '+400% Dimension Rift output', tier: 3 },
  { id: 'dimension_cost', buildingId: 'dimension_rift', name: 'Trans-dimensional Commerce', cost: 2.55e16, effect: { type: 'cost_reduction', value: 0.1 }, description: '-10% Dimension Rift cost', tier: 3 },

  // ============ TIER 4 BUILDING UPGRADES ============
  { id: 'universe_1', buildingId: 'universe_seed', name: 'Big Bang Seeding', cost: 1.4e16, effect: { type: 'efficiency', value: 1 }, description: '+100% Universe Seed output', tier: 4 },
  { id: 'universe_2', buildingId: 'universe_seed', name: 'Inflation Control', cost: 1.4e17, effect: { type: 'efficiency', value: 2 }, description: '+200% Universe Seed output', tier: 4 },
  { id: 'universe_3', buildingId: 'universe_seed', name: 'Multiverse Garden', cost: 1.4e18, effect: { type: 'efficiency', value: 4 }, description: '+400% Universe Seed output', tier: 4 },

  { id: 'reality_1', buildingId: 'reality_anchor', name: 'Reality Stabilizer', cost: 2e17, effect: { type: 'efficiency', value: 1 }, description: '+100% Reality Anchor output', tier: 4 },
  { id: 'reality_2', buildingId: 'reality_anchor', name: 'Timeline Mender', cost: 2e18, effect: { type: 'efficiency', value: 2 }, description: '+200% Reality Anchor output', tier: 4 },
  { id: 'reality_3', buildingId: 'reality_anchor', name: 'Paradox Eliminator', cost: 2e19, effect: { type: 'efficiency', value: 4 }, description: '+400% Reality Anchor output', tier: 4 },

  { id: 'infinity_1', buildingId: 'infinity_engine', name: 'Aleph Null Power', cost: 3.3e18, effect: { type: 'efficiency', value: 1 }, description: '+100% Infinity Engine output', tier: 4 },
  { id: 'infinity_2', buildingId: 'infinity_engine', name: 'Omega Point Drive', cost: 3.3e19, effect: { type: 'efficiency', value: 2 }, description: '+200% Infinity Engine output', tier: 4 },
  { id: 'infinity_3', buildingId: 'infinity_engine', name: 'Transcendental Yield', cost: 3.3e20, effect: { type: 'efficiency', value: 4 }, description: '+400% Infinity Engine output', tier: 4 },

  // ============ TIER 5 BUILDING UPGRADES (MULTIVERSE) ============
  { id: 'multiverse_1', buildingId: 'multiverse_fabric', name: 'Reality Weaving', cost: 5.1e19, effect: { type: 'efficiency', value: 1 }, description: '+100% Multiverse Fabric output', tier: 5 },
  { id: 'multiverse_2', buildingId: 'multiverse_fabric', name: 'Brane Oscillation', cost: 5.1e20, effect: { type: 'efficiency', value: 2 }, description: '+200% Multiverse Fabric output', tier: 5 },
  { id: 'multiverse_3', buildingId: 'multiverse_fabric', name: 'Cosmic Web Mastery', cost: 5.1e21, effect: { type: 'efficiency', value: 4 }, description: '+400% Multiverse Fabric output', tier: 5 },

  { id: 'omniverse_1', buildingId: 'omniverse_well', name: 'Parallel Harvest', cost: 7e20, effect: { type: 'efficiency', value: 1 }, description: '+100% Omniverse Well output', tier: 5 },
  { id: 'omniverse_2', buildingId: 'omniverse_well', name: 'Many-Worlds Tap', cost: 7e21, effect: { type: 'efficiency', value: 2 }, description: '+200% Omniverse Well output', tier: 5 },
  { id: 'omniverse_3', buildingId: 'omniverse_well', name: 'Infinite Branches', cost: 7e22, effect: { type: 'efficiency', value: 4 }, description: '+400% Omniverse Well output', tier: 5 },

  { id: 'cosmicstring_1', buildingId: 'cosmic_string', name: 'String Vibration', cost: 1e22, effect: { type: 'efficiency', value: 1 }, description: '+100% Cosmic String output', tier: 5 },
  { id: 'cosmicstring_2', buildingId: 'cosmic_string', name: 'GUT Symmetry', cost: 1e23, effect: { type: 'efficiency', value: 2 }, description: '+200% Cosmic String output', tier: 5 },
  { id: 'cosmicstring_3', buildingId: 'cosmic_string', name: 'Vacuum Energy Siphon', cost: 1e24, effect: { type: 'efficiency', value: 4 }, description: '+400% Cosmic String output', tier: 5 },

  { id: 'void_1', buildingId: 'void_extractor', name: 'Dark Energy Tap', cost: 1.4e23, effect: { type: 'efficiency', value: 1 }, description: '+100% Void Extractor output', tier: 5 },
  { id: 'void_2', buildingId: 'void_extractor', name: 'Nothingness Harvest', cost: 1.4e24, effect: { type: 'efficiency', value: 2 }, description: '+200% Void Extractor output', tier: 5 },
  { id: 'void_3', buildingId: 'void_extractor', name: 'Primordial Void', cost: 1.4e25, effect: { type: 'efficiency', value: 4 }, description: '+400% Void Extractor output', tier: 5 },

  // ============ GLOBAL UPGRADES ============
  { id: 'global_1', name: 'Energy Research I', cost: 50000, effect: { type: 'global_efficiency', value: 0.1 }, description: '+10% all production', tier: 0 },
  { id: 'global_2', name: 'Energy Research II', cost: 500000, effect: { type: 'global_efficiency', value: 0.25 }, description: '+25% all production', tier: 0 },
  { id: 'global_3', name: 'Energy Research III', cost: 5000000, effect: { type: 'global_efficiency', value: 0.5 }, description: '+50% all production', tier: 0 },
  { id: 'global_4', name: 'Energy Research IV', cost: 50000000, effect: { type: 'global_efficiency', value: 1 }, description: '+100% all production', tier: 0 },
  { id: 'global_5', name: 'Energy Research V', cost: 500000000, effect: { type: 'global_efficiency', value: 2 }, description: '+200% all production', tier: 0 },
  { id: 'global_6', name: 'Energy Research VI', cost: 5e9, effect: { type: 'global_efficiency', value: 5 }, description: '+500% all production', tier: 0 },
  { id: 'global_7', name: 'Energy Research VII', cost: 5e10, effect: { type: 'global_efficiency', value: 10 }, description: '+1000% all production', tier: 0 },
  { id: 'global_8', name: 'Energy Research VIII', cost: 5e12, effect: { type: 'global_efficiency', value: 25 }, description: '+2500% all production', tier: 0 },

  // Click upgrades
  { id: 'click_1', name: 'Enhanced Clicking', cost: 100, effect: { type: 'click_power', value: 1 }, description: '+1 energy per click', tier: 0 },
  { id: 'click_2', name: 'Advanced Clicking', cost: 1000, effect: { type: 'click_power', value: 9 }, description: '+10 energy per click', tier: 0 },
  { id: 'click_3', name: 'Quantum Clicking', cost: 10000, effect: { type: 'click_power', value: 99 }, description: '+100 energy per click', tier: 0 },
  { id: 'click_4', name: 'Multiverse Clicking', cost: 100000, effect: { type: 'click_power', value: 999 }, description: '+1000 energy per click', tier: 0 },
  { id: 'click_5', name: 'Infinity Clicking', cost: 1e7, effect: { type: 'click_power', value: 9999 }, description: '+10000 energy per click', tier: 0 },
  { id: 'click_6', name: 'Ultimate Click', cost: 1e9, effect: { type: 'click_power', value: 99999 }, description: '+100000 energy per click', tier: 0 },
  { id: 'click_7', name: 'Cosmic Click', cost: 1e12, effect: { type: 'click_power', value: 999999 }, description: '+1e6 energy per click', tier: 0 },

  // Auto-clicker
  { id: 'auto_click_1', name: 'Auto Clicker I', cost: 5000, effect: { type: 'auto_click', value: 1 }, description: '+1 click per second', tier: 0 },
  { id: 'auto_click_2', name: 'Auto Clicker II', cost: 50000, effect: { type: 'auto_click', value: 5 }, description: '+5 clicks per second', tier: 0 },
  { id: 'auto_click_3', name: 'Auto Clicker III', cost: 500000, effect: { type: 'auto_click', value: 25 }, description: '+25 clicks per second', tier: 0 },
  { id: 'auto_click_4', name: 'Auto Clicker IV', cost: 5000000, effect: { type: 'auto_click', value: 100 }, description: '+100 clicks per second', tier: 0 },
  { id: 'auto_click_5', name: 'Auto Clicker V', cost: 5e7, effect: { type: 'auto_click', value: 500 }, description: '+500 clicks per second', tier: 0 },
  { id: 'auto_click_6', name: 'Auto Clicker VI', cost: 5e9, effect: { type: 'auto_click', value: 2500 }, description: '+2500 clicks per second', tier: 0 },

  // Production multipliers
  { id: 'mult_1', name: 'Energy Doubler I', cost: 1e6, effect: { type: 'global_multiplier', value: 2 }, description: 'x2 all production', tier: 0 },
  { id: 'mult_2', name: 'Energy Doubler II', cost: 1e8, effect: { type: 'global_multiplier', value: 2 }, description: 'x2 all production', tier: 0 },
  { id: 'mult_3', name: 'Energy Doubler III', cost: 1e10, effect: { type: 'global_multiplier', value: 2 }, description: 'x2 all production', tier: 0 },
  { id: 'mult_4', name: 'Energy Doubler IV', cost: 1e12, effect: { type: 'global_multiplier', value: 2 }, description: 'x2 all production', tier: 0 },
  { id: 'mult_5', name: 'Energy Doubler V', cost: 1e14, effect: { type: 'global_multiplier', value: 2 }, description: 'x2 all production', tier: 0 },
  { id: 'mult_6', name: 'Energy Doubler VI', cost: 1e16, effect: { type: 'global_multiplier', value: 2 }, description: 'x2 all production', tier: 0 },
  { id: 'mult_7', name: 'Energy Doubler VII', cost: 1e18, effect: { type: 'global_multiplier', value: 2 }, description: 'x2 all production', tier: 0 },

  // Offline production
  { id: 'offline_1', name: 'Deep Sleep I', cost: 10000, effect: { type: 'offline_rate', value: 0.1 }, description: '+10% offline production', tier: 0 },
  { id: 'offline_2', name: 'Deep Sleep II', cost: 1000000, effect: { type: 'offline_rate', value: 0.25 }, description: '+25% offline production', tier: 0 },
  { id: 'offline_3', name: 'Deep Sleep III', cost: 1e8, effect: { type: 'offline_rate', value: 0.5 }, description: '+50% offline production', tier: 0 },
  { id: 'offline_4', name: 'Deep Sleep IV', cost: 1e10, effect: { type: 'offline_rate', value: 1 }, description: '+100% offline production', tier: 0 },
  { id: 'offline_5', name: 'Deep Sleep V', cost: 1e14, effect: { type: 'offline_rate', value: 2 }, description: '+200% offline production', tier: 0 },

  // Multiverse tier upgrades
  { id: 'mv_upgrade_1', name: 'Reality Expansion', cost: 1e20, effect: { type: 'global_multiplier', value: 5 }, description: 'x5 all production', tier: 0 },
  { id: 'mv_upgrade_2', name: 'Omniverse Synergy', cost: 1e22, effect: { type: 'global_efficiency', value: 50 }, description: '+5000% all production', tier: 0 },
  { id: 'mv_upgrade_3', name: 'Absolute Zero', cost: 1e24, effect: { type: 'global_multiplier', value: 10 }, description: 'x10 all production', tier: 0 },

  // ============ TIER 6 BUILDING UPGRADES (ULTIMATE) ============
  { id: 'transcend_1', buildingId: 'transcendence_core', name: 'Transcendence Awakening', cost: 1.4e25, effect: { type: 'efficiency', value: 1 }, description: '+100% Transcendence Core output', tier: 6 },
  { id: 'transcend_2', buildingId: 'transcendence_core', name: 'Reality Bend', cost: 1.4e26, effect: { type: 'efficiency', value: 2 }, description: '+200% Transcendence Core output', tier: 6 },
  { id: 'transcend_3', buildingId: 'transcendence_core', name: 'Divine Spark', cost: 1.4e27, effect: { type: 'efficiency', value: 4 }, description: '+400% Transcendence Core output', tier: 6 },

  { id: 'celestial_1', buildingId: 'celestial_furnace', name: 'Primordial Fire', cost: 2e26, effect: { type: 'efficiency', value: 1 }, description: '+100% Celestial Furnace output', tier: 6 },
  { id: 'celestial_2', buildingId: 'celestial_furnace', name: 'Cosmic Inferno', cost: 2e27, effect: { type: 'efficiency', value: 2 }, description: '+200% Celestial Furnace output', tier: 6 },
  { id: 'celestial_3', buildingId: 'celestial_furnace', name: 'Genesis Flame', cost: 2e28, effect: { type: 'efficiency', value: 4 }, description: '+400% Celestial Furnace output', tier: 6 },

  { id: 'entropy_1', buildingId: 'entropy_reverser', name: 'Time Dilation', cost: 3e27, effect: { type: 'efficiency', value: 1 }, description: '+100% Entropy Reverser output', tier: 6 },
  { id: 'entropy_2', buildingId: 'entropy_reverser', name: 'Chrono Shift', cost: 3e28, effect: { type: 'efficiency', value: 2 }, description: '+200% Entropy Reverser output', tier: 6 },
  { id: 'entropy_3', buildingId: 'entropy_reverser', name: 'Temporal Mastery', cost: 3e29, effect: { type: 'efficiency', value: 4 }, description: '+400% Entropy Reverser output', tier: 6 },

  { id: 'existential_1', buildingId: 'existential_engine', name: 'Existence Tap', cost: 5e28, effect: { type: 'efficiency', value: 1 }, description: '+100% Existential Engine output', tier: 6 },
  { id: 'existential_2', buildingId: 'existential_engine', name: 'Creation Force', cost: 5e29, effect: { type: 'efficiency', value: 2 }, description: '+200% Existential Engine output', tier: 6 },
  { id: 'existential_3', buildingId: 'existential_engine', name: 'Omnipotence', cost: 5e30, effect: { type: 'efficiency', value: 4 }, description: '+400% Existential Engine output', tier: 6 },

  { id: 'prime_1', buildingId: 'prime_creator', name: 'First Cause', cost: 8e29, effect: { type: 'efficiency', value: 1 }, description: '+100% Prime Creator output', tier: 6 },
  { id: 'prime_2', buildingId: 'prime_creator', name: 'Absolute Origin', cost: 8e30, effect: { type: 'efficiency', value: 2 }, description: '+200% Prime Creator output', tier: 6 },
  { id: 'prime_3', buildingId: 'prime_creator', name: 'Creator Supreme', cost: 8e31, effect: { type: 'efficiency', value: 4 }, description: '+400% Prime Creator output', tier: 6 },

  // Ultimate tier upgrades
  { id: 'ultimate_1', name: 'Transcendence', cost: 1e26, effect: { type: 'global_multiplier', value: 20 }, description: 'x20 all production', tier: 0 },
  { id: 'ultimate_2', name: 'Divinity', cost: 1e28, effect: { type: 'global_efficiency', value: 100 }, description: '+10000% all production', tier: 0 },
  { id: 'ultimate_3', name: 'Omniscience', cost: 1e30, effect: { type: 'global_multiplier', value: 50 }, description: 'x50 all production', tier: 0 },
  { id: 'ultimate_4', name: 'Absolute Power', cost: 1e32, effect: { type: 'global_multiplier', value: 100 }, description: 'x100 all production', tier: 0 },
];

export function getUpgradeEffect(upgrade, currentOwned) {
  switch (upgrade.effect.type) {
    case 'efficiency':
      return upgrade.effect.value * currentOwned;
    case 'global_efficiency':
    case 'click_power':
    case 'cost_reduction':
    case 'auto_buy':
    case 'auto_click':
    case 'global_multiplier':
    case 'offline_rate':
      return upgrade.effect.value;
    default:
      return 0;
  }
}

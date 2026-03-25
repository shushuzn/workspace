// Building configurations

export const BUILDINGS = [
  {
    id: 'solar_panel',
    name: 'Solar Panel',
    baseProduction: 0.1,
    baseCost: 10,
    costMultiplier: 1.15,
    description: 'Harvests energy from the sun',
    emoji: '☀️',
  },
  {
    id: 'moon_mine',
    name: 'Moon Mine',
    baseProduction: 1,
    baseCost: 100,
    costMultiplier: 1.15,
    description: 'Extracts helium-3 from lunar soil',
    emoji: '🌙',
  },
  {
    id: 'mars_refinery',
    name: 'Mars Refinery',
    baseProduction: 8,
    baseCost: 1100,
    costMultiplier: 1.15,
    description: 'Processes Martian minerals',
    emoji: '🔴',
  },
  {
    id: 'asteroid_belt',
    name: 'Asteroid Belt',
    baseProduction: 47,
    baseCost: 12000,
    costMultiplier: 1.15,
    description: 'Mines platinum from asteroids',
    emoji: '🪨',
  },
  {
    id: 'interstellar_quarry',
    name: 'Interstellar Quarry',
    baseProduction: 260,
    baseCost: 130000,
    costMultiplier: 1.15,
    description: 'Extracts dark matter',
    emoji: '💎',
  },
  {
    id: 'dysons_sphere',
    name: "Dyson's Sphere",
    baseProduction: 1400,
    baseCost: 1400000,
    costMultiplier: 1.15,
    description: 'Encloses a star for maximum harvest',
    emoji: '🔮',
  },
  {
    id: 'stellar_furnace',
    name: 'Stellar Furnace',
    baseProduction: 7800,
    baseCost: 20000000,
    costMultiplier: 1.15,
    description: 'Fusion power plant',
    emoji: '⚡',
  },
  {
    id: 'black_hole_extractor',
    name: 'Black Hole Extractor',
    baseProduction: 44000,
    baseCost: 330000000,
    costMultiplier: 1.15,
    description: 'Harvests energy from singularity',
    emoji: '🕳️',
  },
  {
    id: 'dimension_rift',
    name: 'Dimension Rift',
    baseProduction: 260000,
    baseCost: 5100000000,
    costMultiplier: 1.15,
    description: 'Opens portals to other dimensions',
    emoji: '🌀',
  },
];

export function getBuildingCost(building, owned, prestigeMultiplier = 1) {
  return Math.floor(building.baseCost * Math.pow(building.costMultiplier, owned) / prestigeMultiplier);
}

export function getBuildingProduction(building, owned, efficiencyBonus = 0) {
  return building.baseProduction * owned * (1 + efficiencyBonus);
}

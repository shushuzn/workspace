/**
 * Population (Evolution Layer)
 * Manages candidate population for evolution
 * Refactored from operations system
 */

import { CONFIG } from '../core/config/default.mjs';

export class Population {
  constructor(workspace, operations) {
    this.workspace = workspace;
    this.operations = operations;
    this.fitnessCache = new Map();
  }

  /**
   * Get all individuals in population
   */
  getAll() {
    return this.operations.map(op => ({
      id: op.id,
      name: op.name,
      type: op.type,
      fitness: this.getFitness(op.id),
      genes: this.extractGenes(op)
    }));
  }

  /**
   * Extract genes (mutable properties) from operation
   */
  extractGenes(op) {
    return {
      weight: op.weight || 1,
      cooldown: CONFIG.cooldown[op.type === 'detection' ? 'detection' : 'productive'],
      enabled: true,
      lastFitness: this.getFitness(op.id)
    };
  }

  /**
   * Get fitness score for an operation
   */
  getFitness(opId) {
    if (this.fitnessCache.has(opId)) {
      return this.fitnessCache.get(opId);
    }

    // Fitness is calculated from history
    // This is a simplified version - in real impl would use proper algorithm
    return 0.5; // Default neutral fitness
  }

  /**
   * Update fitness based on result
   */
  updateFitness(opId, improved, delta) {
    const current = this.getFitness(opId);
    const learningRate = 0.1;

    let newFitness;
    if (improved) {
      newFitness = current + learningRate * delta * 0.01;
    } else {
      newFitness = current - learningRate * 0.1;
    }

    // Clamp between 0 and 1
    newFitness = Math.max(0, Math.min(1, newFitness));
    this.fitnessCache.set(opId, newFitness);

    return newFitness;
  }

  /**
   * Select individuals for reproduction
   */
  selectForReproduction(count = 3) {
    const all = this.getAll()
      .sort((a, b) => b.fitness - a.fitness);

    return all.slice(0, count);
  }

  /**
   * Get top performers
   */
  getTopPerformers(count = 5) {
    return this.getAll()
      .filter(ind => ind.fitness > 0.5)
      .sort((a, b) => b.fitness - a.fitness)
      .slice(0, count);
  }

  /**
   * Get underperformers that need mutation
   */
  getUnderperformers(threshold = 0.3) {
    return this.getAll()
      .filter(ind => ind.fitness < threshold);
  }

  /**
   * Get statistics
   */
  getStats() {
    const all = this.getAll();
    const fitnesses = all.map(ind => ind.fitness);

    return {
      total: all.length,
      avgFitness: fitnesses.reduce((a, b) => a + b, 0) / fitnesses.length,
      maxFitness: Math.max(...fitnesses),
      minFitness: Math.min(...fitnesses),
      diverseCount: all.filter(ind => ind.fitness > 0.4 && ind.fitness < 0.6).length
    };
  }
}

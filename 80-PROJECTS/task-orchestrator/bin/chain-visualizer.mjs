#!/usr/bin/env node
/**
 * chain-visualizer.mjs
 * 实时显示chain执行进度：当前步骤/总步骤数，ANSI颜色+百分比
 */
import chalk from 'chalk';

export function createVisualizer(totalSteps) {
  let currentStep = 0;
  return {
    start() {
      currentStep = 0;
      this.render();
    },
    step(name) {
      currentStep++;
      this.render(name);
    },
    done() {
      currentStep = totalSteps;
      this.render('DONE');
      console.log('');
    },
    render(label) {
      const pct = totalSteps > 0 ? Math.round((currentStep / totalSteps) * 100) : 0;
      const barLen = 20;
      const filled = Math.round((currentStep / totalSteps) * barLen);
      const bar = '█'.repeat(filled) + '░'.repeat(barLen - filled);
      const step = `${currentStep}/${totalSteps}`;
      process.stderr.write(`\r${chalk.cyan('chain')} [${bar}] ${step} ${pct}% ${chalk.yellow(label || '')}\r`);
    }
  };
}

function demo() {
  const viz = createVisualizer(5);
  viz.start();
  for (const cmd of ['browse', 'search', 'extract', 'write', 'verify']) {
    viz.step(cmd);
  }
  viz.done();
  console.log('[chain-visualizer] demo passed');
}

demo();

#!/usr/bin/env node
const fs = require('fs');
const path = require('path');

const file = process.argv[2];
let content = fs.readFileSync(file, 'utf8');

const insertMarker = "  if (cmd === 'check') {";
const insertAt = content.indexOf(insertMarker);
if (insertAt === -1) { console.error('marker not found'); process.exit(1); }

const recommend = `  // Bayesian Fix Recommender
  if (cmd === 'recommend') {
    const state = existsSync(STATE_FILE)
      ? JSON.parse(readFileSync(STATE_FILE, 'utf8'))
      : {};
    const fixHistory = state?.patterns?.fixHistory || {};
    const lastFixAttempt = state?.patterns?.lastFixAttempt || {};
    const decayReport = state?.patterns?.decayReport?.patterns || [];

    const coMatrix = {};
    for (const [pat, events] of Object.entries(fixHistory)) {
      if (!events || events.length < 2) continue;
      for (const ev of events) {
        if (ev.coPatterns) {
          for (const cop of ev.coPatterns) {
            if (!coMatrix[pat]) coMatrix[pat] = {};
            coMatrix[pat][cop] = (coMatrix[pat][cop] || 0) + 1;
          }
        }
      }
    }

    const patterns = loadPatterns();
    const recommendations = [];

    for (const p of patterns) {
      const fix = FIXES[p.name];
      if (!fix) continue;
      const conf = getConfidence(p) ?? 0.5;
      const decayEntry = decayReport.find(d => d.name === p.name);
      const decay = decayEntry?.decayFactor ?? 1.0;
      const effConf = conf * decay;
      const riskWeight = fix.risk === 'low' ? 1.0 : fix.risk === 'medium' ? 0.6 : 0.3;
      const lastFix = lastFixAttempt[p.name];
      const daysSince = lastFix ? (Date.now() - new Date(lastFix.timestamp)) / (1000*60*60*24) : null;
      const recentPenalty = (daysSince !== null && daysSince < 7) ? 0.4 : 1.0;
      let coBonus = 1.0;
      if (coMatrix[p.name]) {
        for (const [cop, count] of Object.entries(coMatrix[p.name])) {
          const copLast = lastFixAttempt[cop];
          if (copLast && (Date.now() - new Date(copLast.timestamp)) < 7*24*60*60*1000) {
            coBonus = Math.max(coBonus, 1 + 0.1 * Math.min(count, 5));
          }
        }
      }
      const check = fix.check();
      if (!check.applicable) continue;
      const score = effConf * riskWeight * recentPenalty * coBonus;
      recommendations.push({ name: p.name, fix: p.fix, risk: fix.risk, severity: p.severity, score, effConf, conf, decay, daysSince, applicable: check.applicable });
    }

    recommendations.sort((a, b) => b.score - a.score);
    console.log('\n=== Bayesian Fix Recommendations ===\n');
    console.log('  #  Pattern                                EffConf  Risk    DaysAgo  Score');
    console.log('  ' + '-'.repeat(70));
    for (let i = 0; i < recommendations.length; i++) {
      const r = recommendations[i];
      const days = r.daysSince !== null ? Math.floor(r.daysSince) + 'd' : 'never';
      const stars = r.score >= 0.5 ? 'green' : r.score >= 0.3 ? 'yellow' : 'grey';
      const confStr = r.effConf >= 0.9 ? '95%+' : (r.effConf*100).toFixed(0) + '%';
      const name38 = r.name.length > 36 ? r.name.substring(0,35)+'...' : r.name;
      console.log('  ' + String(i+1).padStart(2) + '  ' + name38.padEnd(38) + ' ' + confStr.padEnd(8) + ' ' + r.risk.padEnd(7) + ' ' + days.padEnd(8) + stars + ' ' + r.score.toFixed(3));
    }
    console.log();
    if (recommendations.length > 0) {
      const top = recommendations[0];
      console.log('-> Top pick: ' + top.name);
      console.log('   Confidence: ' + (top.effConf*100).toFixed(0) + '% | Risk: ' + top.risk + ' | Score: ' + top.score.toFixed(3));
      console.log('   Fix: ' + top.fix);
    }
    console.log();
    return;
  }

`;

const newContent = content.slice(0, insertAt) + recommend + content.slice(insertAt);
fs.writeFileSync(file, newContent);
console.log('Patched successfully');

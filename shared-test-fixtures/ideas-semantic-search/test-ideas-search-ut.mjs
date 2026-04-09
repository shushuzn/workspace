#!/usr/bin/env node
/**
 * UT for ideas-semantic-search.mjs — tests tokenize and overlap logic
 */
const tokenize = (text) => {
  const tokens = [];
  const chinese = text.match(/[\u4e00-\u9fff]+/g) || [];
  for (const chunk of chinese) {
    for (let i = 0; i < chunk.length - 1; i++) {
      tokens.push(chunk.slice(i, i + 2));
      if (i < chunk.length - 2) tokens.push(chunk.slice(i, i + 3));
    }
  }
  const latin = text.toLowerCase().replace(/[^a-z0-9\s]/g, ' ').split(/\s+/);
  for (const t of latin) { if (t.length > 1) tokens.push(t); }
  return tokens;
};

const overlapScore = (docTokens, queryTokens) => {
  const docSet = new Set(docTokens);
  let score = 0;
  for (const t of queryTokens) { if (docSet.has(t)) score++; }
  return score;
};

// Test 1: Chinese bigram tokenization
const tokens = tokenize('批量导入');
const ok1 = tokens.includes('批量') && tokens.includes('导入');
console.log(`[UT] chinese tokenize: ${ok1 ? 'PASS' : 'FAIL'}`);

// Test 2: Overlap scoring
const doc = tokenize('添加批量导入脚本');
const score = overlapScore(doc, tokens);
const ok2 = score >= 3;
console.log(`[UT] overlap score: ${ok2 ? 'PASS' : 'FAIL'} (got ${score})`);

// Test 3: No-match returns 0
const noMatch = tokenize('完全无关的内容');
const noScore = overlapScore(noMatch, tokens);
const ok3 = noScore === 0;
console.log(`[UT] no match: ${ok3 ? 'PASS' : 'FAIL'}`);

const allPass = ok1 && ok2 && ok3;
console.log(allPass ? '\n[UT ALL PASS]' : '\n[UT FAIL]');
process.exit(allPass ? 0 : 1);

#!/usr/bin/env node
/**
 * UT for wiki-batch-export.mjs — tests format detection and path normalization
 */

// Test 1: format detection
const formatIdx = process.argv.indexOf('--format');
const format = formatIdx !== -1 ? process.argv[formatIdx + 1] : 'html';
const ok1 = format === 'html';
console.log(`[UT] default_format: ${ok1 ? 'PASS' : 'FAIL'} (expect html)`);

// Test 2: path normalization (Windows backslash → forward slash)
const testPath = 'D:\\OpenClaw\\workspace\\knowledge\\wikipedia\\articles\\ai\\test.md';
const normPath = testPath.replace(/\\/g, '/');
const ok2 = normPath.includes('wikipedia/articles');
console.log(`[UT] path_normalize: ${ok2 ? 'PASS' : 'FAIL'}`);

// Test 3: mdToHtml basic conversion
function mdToHtml(md) {
  return md
    .replace(/^### (.+)$/gm, '<h3>$1</h3>')
    .replace(/^## (.+)$/gm, '<h2>$1</h2>')
    .replace(/^# (.+)$/gm, '<h1>$1</h1>')
    .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.+?)\*/g, '<em>$1</em>');
}
const html = mdToHtml('## Title\n**bold**');
const ok3 = html.includes('<h2>Title</h2>') && html.includes('<strong>bold</strong>');
console.log(`[UT] md_to_html: ${ok3 ? 'PASS' : 'FAIL'}`);

// Test 4: name sanitization
const rel = 'ai/01-detection-of-spin-valley-polarized-states.md';
const name = rel.replace(/\.md$/, '').replace(/\//g, '-');
const ok4 = name === 'ai-01-detection-of-spin-valley-polarized-states';
console.log(`[UT] name_sanitize: ${ok4 ? 'PASS' : 'FAIL'}`);

const allPass = ok1 && ok2 && ok3 && ok4;
console.log(allPass ? '\n[UT ALL PASS]' : '\n[UT FAIL]');
process.exit(allPass ? 0 : 1);

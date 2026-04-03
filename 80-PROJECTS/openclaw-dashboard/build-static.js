#!/usr/bin/env node
/**
 * Build static dashboard for Vercel deployment
 * Injects dashboard-data.json into dashboard.html as window.__DASHBOARD_DATA__
 */
const fs = require('fs');
const path = require('path');

const SRC = path.join(__dirname, 'dashboard.html');
const DATA = path.join(__dirname, 'dashboard-data.json');
const DIST = path.join(__dirname, 'dist');

if (!fs.existsSync(DIST)) fs.mkdirSync(DIST, { recursive: true });

// Load data
const data = JSON.parse(fs.readFileSync(DATA, 'utf8'));

// Load HTML
let html = fs.readFileSync(SRC, 'utf8');

// Inject data before </head>
const inject = `<script>window.__DASHBOARD_DATA__ = ${JSON.stringify(data)};</script>`;
html = html.replace('</head>', inject + '</head>');

// Also replace fetch('/data') with window.__DASHBOARD_DATA__ to support offline
html = html.replace(
  /const response = await fetch\('\/data'\);[\s\S]*?dashboardData = data;/,
  'dashboardData = window.__DASHBOARD_DATA__ || {};'
);

// Write dist/index.html
const out = path.join(DIST, 'index.html');
fs.writeFileSync(out, html);
console.log(`Static dashboard built: ${out}`);

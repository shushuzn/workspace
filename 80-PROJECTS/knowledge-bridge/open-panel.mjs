#!/usr/bin/env node
/**
 * Open Knowledge Panel in browser
 */

import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { execSync } from "node:child_process";

const __dirname = dirname(fileURLToPath(import.meta.url));

function openPanel() {
  const panelPath = join(__dirname, "knowledge-panel.html");
  const absPath = panelPath.replace(/\\/g, "/");

  // Try various browsers
  const commands = [
    `start ms-edge "${absPath}"`,
    `start chrome "${absPath}" --new-window`,
    `start "" "${absPath}"`,
  ];

  for (const cmd of commands) {
    try {
      execSync(cmd, { stdio: "ignore", timeout: 3000 });
      console.log("Panel opened in browser");
      return;
    } catch { }
  }

  console.log(`Open manually: ${absPath}`);
}

openPanel();

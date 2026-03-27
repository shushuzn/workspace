// ~/.omc/patrol-agent/src/git.js
// Git conflict detection: check if files have uncommitted local changes

import { execSync } from "child_process";
import { existsSync } from "fs";

const WORKSPACE_ROOT = "D:/OpenClaw/workspace";

function git(args, cwd = WORKSPACE_ROOT) {
  try {
    return execSync(`git ${args}`, { cwd, encoding: "utf-8", timeout: 15000 });
  } catch (err) {
    return err.stdout || "";
  }
}

export function hasWorkingTreeChanges(files) {
  if (!files || files.length === 0) return false;
  const status = git("status --porcelain", WORKSPACE_ROOT);
  const modifiedFiles = status
    .split("\n")
    .filter(line => line.length > 3 && line[1] !== " ")
    .map(line => line.slice(3).trim());
  for (const file of files) {
    const relPath = file.replace(/^[A-Z]:[\/\\]/i, "").replace(/\\/g, "/");
    if (modifiedFiles.some(f => f === relPath || f.endsWith(relPath))) {
      return true;
    }
  }
  return false;
}

export function getChangedFiles() {
  const status = git("status --porcelain", WORKSPACE_ROOT);
  return status
    .split("\n")
    .filter(line => line.length > 3)
    .map(line => line.slice(3).trim());
}

export function createBranch(branchName) {
  git(`checkout -b ${branchName}`, WORKSPACE_ROOT);
  return branchName;
}

export function getCurrentBranch() {
  return git("rev-parse --abbrev-ref HEAD", WORKSPACE_ROOT).trim();
}

/**
 * Compute SHA256 hash of a file's content using git hash-object.
 * Returns empty string if file doesn't exist or can't be read.
 * @param {string} filePath
 * @returns {string}
 */
export function fileHash(filePath) {
  try {
    const absPath = filePath.replace(/\\/g, '/');
    const result = execSync(`git hash-object "${absPath}"`, {
      cwd: WORKSPACE_ROOT,
      encoding: 'utf-8',
      timeout: 10000,
    });
    return result.trim();
  } catch {
    return '';
  }
}

/**
 * If files have uncommitted working-tree changes, create a branch for patrol changes.
 * Returns branch name if created, null if no conflict or already on a patrol branch.
 * @param {string[]} files
 * @returns {string|null}
 */
export function autoBranchForConflict(files) {
  if (!hasWorkingTreeChanges(files)) return null;

  const currentBranch = getCurrentBranch();
  // Don't branch if already on a patrol branch
  if (currentBranch.startsWith('patrol/')) return null;

  const timestamp = new Date().toISOString().slice(0, 19).replace(/[T:]/g, '-');
  const branchName = `patrol/auto-${timestamp}`;
  createBranch(branchName);
  return branchName;
}
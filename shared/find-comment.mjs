#!/usr/bin/env node
/**
 * shared/find-comment.mjs
 * Finds existing Test Report comment ID, returns 'new' if not found.
 */
import { readFileSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const comments = JSON.parse(readFileSync(join(__dirname, '..', 'comments.json'), 'utf8'));
const ourComment = comments.find(c =>
  c.user.login === 'github-actions[bot]' && c.body.includes('Test Report')
);
console.log(ourComment ? ourComment.id : 'new');

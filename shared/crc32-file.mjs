#!/usr/bin/env node
/**
 * CRC32 file checksum utility
 * Computes CRC32 of a file and outputs new filename with checksum suffix
 * Usage: node shared/crc32-file.mjs <file>
 */
import { createHash } from 'crypto';
import { readFileSync } from 'fs';

function crc32(buf) {
  let crc = 0xffffffff;
  const table = [];
  for (let n = 0; n < 256; n++) {
    let c = n;
    for (let k = 0; k < 8; k++) {
      c = (c & 1) ? (0xedb88320 ^ (c >>> 1)) : (c >>> 1);
    }
    table[n] = c;
  }
  for (let i = 0; i < buf.length; i++) {
    crc = table[(crc ^ buf[i]) & 0xff] ^ (crc >>> 8);
  }
  return (crc ^ 0xffffffff) >>> 0;
}

const filePath = process.argv[2];
if (!filePath) {
  console.error('Usage: node shared/crc32-file.mjs <file>');
  process.exit(1);
}

try {
  const data = readFileSync(filePath);
  const hash = crc32(data);
  const hashHex = hash.toString(16).toUpperCase().padStart(8, '0');
  const dir = filePath.replace(/[/\\][^/\\]+$/, '');
  const extMatch = filePath.match(/\.([^.]+)$/);
  const ext = extMatch ? extMatch[1] : '';
  const base = ext ? filePath.slice(0, -(ext.length + 1)) : filePath;
  const newName = ext ? `${base}_${hashHex}.${ext}` : `${base}_${hashHex}`;
  console.log(newName);
} catch (e) {
  console.error('Error:', e.message);
  process.exit(1);
}

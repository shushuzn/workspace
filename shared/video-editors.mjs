#!/usr/bin/env node
/**
 * shared/video-editors.mjs
 * FFmpeg 视频编辑封装：cut / concat / subtitle / transcode
 * Usage:
 *   node video-editors.mjs cut <input> <start> <end> <output>
 *   node video-editors.mjs concat <file-list> <output>
 *   node video-editors.mjs subtitle <input> <srt> <output>
 *   node video-editors.mjs transcode <input> <output> [--bitrate=<b>]
 */
import { spawn } from 'child_process';
import { createInterface } from 'readline';
import { existsSync } from 'fs';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';
import imageio_ffmpeg from 'imageio-ffmpeg';

const ffmpeg = imageio_ffmpeg.get_ffmpegExe();
const __DIR = dirname(fileURLToPath(import.meta.url));

function run(cmd, args, extra = {}) {
  return new Promise((resolve, reject) => {
    const p = spawn(cmd, args, { stdio: ['inherit', 'pipe', 'pipe'], ...extra });
    let out = '', err = '';
    p.stdout.on('data', d => out += d);
    p.stderr.on('data', d => err += d);
    p.on('close', code => code === 0 ? resolve(out) : reject(new Error(`ffmpeg exit ${code}\n${err.slice(-500)}`)));
  });
}

async function cmdCut(input, start, end, output) {
  if (!existsSync(input)) throw new Error(`Input not found: ${input}`);
  await run(ffmpeg, ['-y', '-ss', start, '-to', end, '-i', input, '-c', 'copy', output]);
  console.log(`[cut] ${output}`);
}

async function cmdConcat(fileListPath, output) {
  const content = await fs.promises.readFile(fileListPath, 'utf-8');
  const files = content.trim().split('\n').filter(l => l.startsWith('file ')).map(l => l.slice(7).trim());
  const tmp = resolve(__DIR, 'concat_tmp_' + Date.now() + '.txt');
  await fs.promises.writeFile(tmp, files.map(f => `file '${f}'`).join('\n'));
  await run(ffmpeg, ['-y', '-f', 'concat', '-safe', '0', '-i', tmp, '-c', 'copy', output]);
  await fs.promises.unlink(tmp).catch(() => {});
  console.log(`[concat] ${output}`);
}

async function cmdSubtitle(input, srt, output) {
  if (!existsSync(input)) throw new Error(`Input not found: ${input}`);
  if (!existsSync(srt)) throw new Error(`SRT not found: ${srt}`);
  await run(ffmpeg, ['-y', '-i', input, '-vf', `subtitles='${srt}'`, output]);
  console.log(`[subtitle] ${output}`);
}

async function cmdTranscode(input, output, bitrate) {
  if (!existsSync(input)) throw new Error(`Input not found: ${input}`);
  const args = ['-y', '-i', input, '-c:v', 'libx264', '-crf', '23'];
  if (bitrate) args.push('-b:v', bitrate);
  args.push('-c:a', 'aac', '-pix_fmt', 'yuv420p', output);
  await run(ffmpeg, args);
  console.log(`[transcode] ${output}`);
}

const [,, cmd, ...args] = process.argv;
if (!cmd) {
  console.log('Usage: node video-editors.mjs <cut|concat|subtitle|transcode> [args...]');
  process.exit(1);
}

import fs from 'fs';

(async () => {
  try {
    switch (cmd) {
      case 'cut': {
        const [input, start, end, output] = args;
        if (!input || !start || !end || !output) throw new Error('Usage: cut <input> <start> <end> <output>');
        await cmdCut(resolve(input), start, end, resolve(output));
        break;
      }
      case 'concat': {
        const [list, output] = args;
        if (!list || !output) throw new Error('Usage: concat <file-list> <output>');
        await cmdConcat(resolve(list), resolve(output));
        break;
      }
      case 'subtitle': {
        const [input, srt, output] = args;
        if (!input || !srt || !output) throw new Error('Usage: subtitle <input> <srt> <output>');
        await cmdSubtitle(resolve(input), resolve(srt), resolve(output));
        break;
      }
      case 'transcode': {
        const input = args[0], output = args[1];
        const bitrate = args.find(a => a.startsWith('--bitrate='))?.split('=')[1];
        if (!input || !output) throw new Error('Usage: transcode <input> <output> [--bitrate=<b>]');
        await cmdTranscode(resolve(input), resolve(output), bitrate);
        break;
      }
      default:
        console.error(`Unknown command: ${cmd}`);
        process.exit(1);
    }
  } catch (e) {
    console.error('[ERROR]', e.message);
    process.exit(1);
  }
})();

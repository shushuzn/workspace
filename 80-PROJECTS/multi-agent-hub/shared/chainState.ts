import fs from 'fs';
import os from 'os';
import path from 'path';

const CHAIN_FILE = path.join(os.tmpdir(), 'ai-roundtable-chain.json');

export interface ChainEntry {
  persona: { id: string; name: string; icon: string };
  text: string;
  round: number;
  order: number;
}

export interface ChainState {
  topic: string;
  totalRounds: number;
  chain: ChainEntry[];
  currentRound: number;
  currentOrder: number;
}

export function readChain(): ChainState | null {
  try {
    if (!fs.existsSync(CHAIN_FILE)) return null;
    return JSON.parse(fs.readFileSync(CHAIN_FILE, 'utf8'));
  } catch {
    return null;
  }
}

export function writeChain(state: ChainState): void {
  fs.writeFileSync(CHAIN_FILE, JSON.stringify(state, null, 2), 'utf8');
}

export function clearChain(): void {
  try {
    fs.unlinkSync(CHAIN_FILE);
  } catch {}
}

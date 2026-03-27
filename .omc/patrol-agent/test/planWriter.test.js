// test/planWriter.test.js
import { writePlanFromResearch } from '../src/planWriter.js';
import { existsSync, unlinkSync } from 'fs';
import { join } from 'path';
import { ok, equal } from 'assert';

const idea = {
  title: 'Test Research Plan',
  url: 'https://github.com/example/test',
  summary: 'A test research idea for unit testing plan writer.',
  confidence: 0.85,
  source: 'github',
  generated_at: new Date().toISOString(),
};

const result = writePlanFromResearch(idea);
equal(result.success, true, 'writePlanFromResearch returns success');
ok(typeof result.planId === 'string' && result.planId.length > 0, 'returns planId');
ok(typeof result.file === 'string' && result.file.length > 0, 'returns file path');
ok(existsSync(result.file), 'plan file was created');

// Clean up
unlinkSync(result.file);
console.log('planWriter.js: test passed');

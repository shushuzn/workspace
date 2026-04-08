import { defineConfig } from 'vite';
import { resolve } from 'path';

export default defineConfig({
  build: {
    lib: {
      entry: resolve(__dirname, 'src/index.ts'),
      formats: ['es'],
      fileName: () => 'index.js',
    },
    rollupOptions: {
      external: [
        'node:fs', 'node:path', 'node:os', 'node:url', 'node:crypto',
        'node:module', 'node:fs/promises', 'node:child_process',
        'commander', 'chalk', 'chokidar', 'yaml', 'eventsource-parser',
        'ai', 'ai-elements', 'zod', 'json-schema',
      ],
      output: {
        entryFileNames: 'index.js',
      },
    },
    outDir: 'dist/build',
    emptyOutDir: true,
  },
});

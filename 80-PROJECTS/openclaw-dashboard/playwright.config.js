const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: './tests-e2e',
  testMatch: '**/*.test.js',
  timeout: 30000,
  retries: 0,
  reporter: 'line',
  use: {
    baseURL: 'http://localhost:3847',
    trace: 'off',
  },
  projects: [
    {
      name: 'chromium',
      use: { browserName: 'chromium' },
    },
  ],
});

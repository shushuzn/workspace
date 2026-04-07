import globals from 'globals';
import pluginJs from '@eslint/js';

export default [
  pluginJs.configs.recommended,
  {
    files: ['**/*.js'],
    languageOptions: {
      globals: {
        ...globals.node,
      },
    },
    rules: {
      'no-unused-vars': 'warn',
      'no-console': 'off',
      'prefer-const': 'warn',
    },
  },
  {
    ignores: [
      'dist/',
      'node_modules/',
      '.git/',
      '.husky/',
      '.github/',
      '.omc/',
      '.vite/',
    ],
  },
];

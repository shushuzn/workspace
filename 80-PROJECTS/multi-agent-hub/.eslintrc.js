export default [
  {
    files: ['**/*.js'],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: 'module',
    },
    rules: {
      'no-unused-vars': 'warn',
      'no-console': 'off',
      'prefer-const': 'warn',
      'arrow-spacing': 'warn',
      'object-curly-spacing': ['warn', 'always'],
      quotes: ['warn', 'single'],
    },
  },
  {
    ignores: ['dist/', 'node_modules/', '.git/'],
  },
];

// Workspace-wide lint-staged config
// All TS/JS projects point `core.hooksPath` to 80-PROJECTS/.husky
module.exports = {
  '*.{ts,tsx,js,mjs}': ['prettier --write', 'eslint --fix'],
  '*.{json,md,yaml,yml}': ['prettier --write'],
};

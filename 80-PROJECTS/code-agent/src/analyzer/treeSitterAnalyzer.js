/**
 * Tree-sitter Analyzer
 * AST parsing and query for JavaScript, TypeScript, Python
 */

import TreeSitter from 'tree-sitter';
import JavaScript from 'tree-sitter-javascript';
import TypeScript from 'tree-sitter-typescript';
import Python from 'tree-sitter-python';

class TreeSitterAnalyzer {
  constructor() {
    this.parser = new TreeSitter();
    this.parser.setLanguage(JavaScript);
    this.languages = { javascript: JavaScript, typescript: TypeScript, python: Python };
  }

  /**
   * Detect language from file extension
   */
  detectLanguage(filePath) {
    const ext = filePath.split('.').pop().toLowerCase();
    const map = { js: 'javascript', jsx: 'javascript', ts: 'typescript', tsx: 'typescript', py: 'python' };
    return map[ext] || null;
  }

  /**
   * Set parser language
   */
  setLanguage(language) {
    const lang = this.languages[language];
    if (lang) this.parser.setLanguage(lang);
    return !!lang;
  }

  /**
   * Parse file content to AST
   */
  parse(content, language = 'javascript') {
    this.setLanguage(language);
    return this.parser.parse(content);
  }

  /**
   * Get root node info
   */
  getRootInfo(tree) {
    return { type: tree.rootNode.type, start: tree.rootNode.startPosition, end: tree.rootNode.endPosition };
  }

  /**
   * Query AST by node type pattern
   * @param {string} content - Source code
   * @param {string} language - Language
   * @param {string} nodeType - Node type to find (e.g., 'function_declaration', 'class')
   * @returns {Array} Matching nodes with line numbers
   */
  query(content, language = 'javascript', nodeType) {
    const tree = this.parse(content, language);
    const results = [];
    const queryNode = (node) => {
      if (node.type === nodeType || (nodeType === 'function' && ['function_declaration', 'function', 'arrow_function'].includes(node.type))) {
        results.push({ type: node.type, text: node.text, start: node.startPosition, end: node.endPosition });
      }
      for (let i = 0; i < node.childCount; i++) {
        queryNode(node.child(i));
      }
    };
    queryNode(tree.rootNode);
    return results;
  }

  /**
   * Get AST structure summary for a file
   */
  getAstSummary(content, language = 'javascript') {
    const tree = this.parse(content, language);
    const summary = { nodeCount: 0, maxDepth: 0, types: {} };
    const traverse = (node, depth = 0) => {
      summary.nodeCount++;
      summary.maxDepth = Math.max(summary.maxDepth, depth);
      summary.types[node.type] = (summary.types[node.type] || 0) + 1;
      for (let i = 0; i < node.childCount; i++) traverse(node.child(i), depth + 1);
    };
    traverse(tree.rootNode);
    return summary;
  }

  /**
   * Analyze file - full analysis
   */
  analyzeFile(filePath, content) {
    const language = this.detectLanguage(filePath) || 'javascript';
    const code = content || require('fs').readFileSync(filePath, 'utf-8');
    const tree = this.parse(code, language);
    return { tree, language, summary: this.getAstSummary(code, language) };
  }
}
export default TreeSitterAnalyzer;

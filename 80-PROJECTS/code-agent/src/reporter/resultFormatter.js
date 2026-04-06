class ResultFormatter {
  summarize(findings) {
    return { total: findings.length, bySeverity: {} };
  }
}
export default ResultFormatter;

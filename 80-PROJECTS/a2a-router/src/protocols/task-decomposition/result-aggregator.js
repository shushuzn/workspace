export class ResultAggregator {
  aggregate(subtaskResults, options) {
    const { taskId, strategy } = options;

    const outputs = subtaskResults
      .filter(r => r.success)
      .map(r => r.payload.output);

    const artifacts = subtaskResults
      .filter(r => r.success && r.payload.artifacts)
      .flatMap(r => r.payload.artifacts);

    const failedCount = subtaskResults.filter(r => !r.success).length;

    return {
      taskId,
      outputs,
      artifacts,
      summary: this.generateSummary(outputs),
      success: failedCount === 0,
      stats: {
        total: subtaskResults.length,
        succeeded: outputs.length,
        failed: failedCount
      }
    };
  }

  generateSummary(outputs) {
    if (outputs.length === 0) return 'No results';
    if (outputs.length === 1) return outputs[0];
    return `Completed ${outputs.length} subtasks: ${outputs.join(', ')}`;
  }
}

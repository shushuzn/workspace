/**
 * DifyAdapter - Dify Workflow API integration
 *
 * Integrates with langgenius/dify workflows API.
 * Docs: https://docs.dify.ai/
 */

export class DifyAdapter {
  constructor(options = {}) {
    this.baseUrl = options.baseUrl || process.env.DIFY_API_URL || 'http://localhost/v1';
    this.apiKey = options.apiKey || process.env.DIFY_API_KEY;
    this.timeout = options.timeout || 60000;
  }

  /**
   * Execute a Dify workflow
   * @param {string} workflowId - Dify workflow ID
   * @param {Object} inputs - Workflow input variables
   * @param {Object} options - Execution options
   */
  async executeWorkflow(workflowId, inputs, options = {}) {
    const { responseMode = 'blocking', user = 'a2a-router' } = options;

    const url = `${this.baseUrl}/workflows/run`;

    const body = {
      inputs,
      response_mode: responseMode,
      user
    };

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(body),
        signal: AbortSignal.timeout(this.timeout)
      });

      if (!response.ok) {
        const error = await response.text();
        return {
          success: false,
          error: `Dify API error: ${response.status} - ${error}`
        };
      }

      const data = await response.json();

      return {
        success: true,
        workflowRunId: data.workflow_run_id,
        taskId: data.task_id,
        status: data.status,
        outputs: data.outputs,
        latency: data.latency
      };

    } catch (error) {
      if (error.name === 'TimeoutError') {
        return { success: false, error: 'Dify API timeout' };
      }
      return { success: false, error: error.message };
    }
  }

  /**
   * Get workflow run status and result
   * @param {string} workflowRunId - Dify workflow run ID
   */
  async getWorkflowRun(workflowRunId) {
    const url = `${this.baseUrl}/workflow-runs/${workflowRunId}`;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const error = await response.text();
        return {
          success: false,
          error: `Dify API error: ${response.status} - ${error}`
        };
      }

      const data = await response.json();

      return {
        success: true,
        workflowRunId: data.workflow_run_id,
        status: data.status,
        outputs: data.outputs,
        error: data.error
      };

    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Stop a running workflow
   * @param {string} workflowRunId - Dify workflow run ID
   */
  async stopWorkflow(workflowRunId) {
    const url = `${this.baseUrl}/workflow-runs/${workflowRunId}/stop`;

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        const error = await response.text();
        return {
          success: false,
          error: `Dify API error: ${response.status} - ${error}`
        };
      }

      const data = await response.json();

      return {
        success: true,
        status: data.status
      };

    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * List available workflows (if supported by Dify instance)
   */
  async listWorkflows() {
    const url = `${this.baseUrl}/workflows`;

    try {
      const response = await fetch(url, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.apiKey}`
        }
      });

      if (!response.ok) {
        return { success: false, error: `Dify API error: ${response.status}` };
      }

      const data = await response.json();

      return {
        success: true,
        workflows: data.data || []
      };

    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  /**
   * Convert OrchestrationEngine step to Dify node
   * @param {Object} step - OrchestrationEngine step
   * @returns {Object} - Dify-compatible node config
   */
  static toDifyNode(step) {
    switch (step.type) {
      case 'task':
        return {
          node_id: step.id,
          type: 'llm',
          config: {
            model: step.config.model || 'gpt-4',
            prompt: step.config.prompt || step.name,
            input_variables: Object.keys(step.config.variables || {})
          }
        };
      case 'condition':
        return {
          node_id: step.id,
          type: 'condition',
          config: {
            conditions: [
              { variable: step.config.variable, operator: step.config.operator || 'equals', value: step.config.value }
            ]
          }
        };
      case 'sub-workflow':
        return {
          node_id: step.id,
          type: 'workflow',
          config: {
            workflow_id: step.config.workflowId
          }
        };
      case 'notification':
        return {
          node_id: step.id,
          type: 'notification',
          config: {
            channel: step.config.channel || 'webhook',
            url: step.config.url
          }
        };
      default:
        return {
          node_id: step.id,
          type: 'custom',
          config: step.config
        };
    }
  }
}

export default DifyAdapter;

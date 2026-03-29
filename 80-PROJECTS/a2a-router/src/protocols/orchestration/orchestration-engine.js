/**
 * OrchestrationEngine - Workflow orchestration for A2A Router
 *
 * Provides workflow execution with state machine, pause/resume, and step tracking.
 * Designed to integrate with external orchestration platforms (e.g., Dify).
 */

import { EventEmitter } from 'events';
import { v4 as uuidv4 } from 'uuid';

export class OrchestrationEngine extends EventEmitter {
  constructor(router) {
    super();
    this.router = router;
    this.workflows = new Map();      // workflowId -> WorkflowState
    this.definitions = new Map();    // workflowId -> WorkflowDefinition
  }

  /**
   * Workflow status enum
   */
  static WorkflowStatus = {
    PENDING: 'pending',
    RUNNING: 'running',
    PAUSED: 'paused',
    COMPLETED: 'completed',
    FAILED: 'failed',
    CANCELED: 'canceled'
  };

  /**
   * Step status enum
   */
  static StepStatus = {
    PENDING: 'pending',
    RUNNING: 'running',
    COMPLETED: 'completed',
    FAILED: 'failed',
    SKIPPED: 'skipped'
  };

  /**
   * Execution strategy enum
   */
  static Strategy = {
    SEQUENTIAL: 'sequential',
    PARALLEL: 'parallel',
    ADAPTIVE: 'adaptive'
  };

  /**
   * Create a new workflow
   */
  createWorkflow(workflowId, definition) {
    const workflow = {
      id: workflowId,
      name: definition.name,
      description: definition.description || '',
      status: OrchestrationEngine.WorkflowStatus.PENDING,
      currentStep: 0,
      steps: definition.steps.map((step, idx) => ({
        id: step.id || `step-${idx}`,
        name: step.name,
        type: step.type,           // 'task' | 'condition' | 'sub-workflow'
        config: step.config || {},
        status: OrchestrationEngine.StepStatus.PENDING,
        attempts: 0,
        maxAttempts: step.maxAttempts || 3,
        result: null,
        startedAt: null,
        completedAt: null,
        error: null
      })),
      variables: { ...definition.variables },
      strategy: definition.strategy || OrchestrationEngine.Strategy.SEQUENTIAL,
      createdAt: new Date(),
      startedAt: null,
      completedAt: null,
      pausedAt: null,
      metadata: definition.metadata || {}
    };

    this.workflows.set(workflowId, workflow);
    this.definitions.set(workflowId, definition);

    this.emit('workflow:created', workflow);
    return { success: true, workflow };
  }

  /**
   * Start workflow execution
   */
  async startWorkflow(workflowId, context = {}) {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      return { success: false, error: 'WORKFLOW_NOT_FOUND' };
    }

    if (workflow.status !== OrchestrationEngine.WorkflowStatus.PENDING &&
        workflow.status !== OrchestrationEngine.WorkflowStatus.PAUSED) {
      return { success: false, error: 'WORKFLOW_NOT_STARTABLE' };
    }

    workflow.status = OrchestrationEngine.WorkflowStatus.RUNNING;
    workflow.startedAt = new Date();
    workflow.context = context;

    this.emit('workflow:started', workflow);

    // Execute based on strategy
    if (workflow.strategy === OrchestrationEngine.Strategy.PARALLEL) {
      return this.executeParallel(workflow);
    } else if (workflow.strategy === OrchestrationEngine.Strategy.ADAPTIVE) {
      return this.executeAdaptive(workflow);
    } else {
      return this.executeSequential(workflow);
    }
  }

  /**
   * Execute workflow sequentially (step by step)
   */
  async executeSequential(workflow) {
    for (let i = workflow.currentStep; i < workflow.steps.length; i++) {
      if (workflow.status === OrchestrationEngine.WorkflowStatus.PAUSED) {
        return { success: true, paused: true, currentStep: i };
      }

      const step = workflow.steps[i];
      const result = await this.executeStep(workflow, step);

      if (!result.success && step.maxAttempts <= step.attempts) {
        workflow.status = OrchestrationEngine.WorkflowStatus.FAILED;
        this.emit('workflow:failed', { workflow, step, error: result.error });
        return { success: false, error: result.error, failedStep: step.id };
      }

      workflow.currentStep = i + 1;

      // Handle conditional flow
      if (step.type === 'condition' && result.value !== undefined) {
        const nextStepIdx = result.value ? this.findNextStep(workflow, i, 'true') : this.findNextStep(workflow, i, 'false');
        if (nextStepIdx !== -1) {
          workflow.currentStep = nextStepIdx;
        }
      }
    }

    workflow.status = OrchestrationEngine.WorkflowStatus.COMPLETED;
    workflow.completedAt = new Date();
    this.emit('workflow:completed', workflow);

    return { success: true, completed: true, workflow };
  }

  /**
   * Execute all steps in parallel
   */
  async executeParallel(workflow) {
    const pendingSteps = workflow.steps.filter(s => s.status === OrchestrationEngine.StepStatus.PENDING);
    const promises = pendingSteps.map(step => this.executeStep(workflow, step));
    const results = await Promise.allSettled(promises);

    // Check for failures
    const failures = results.filter(r => r.status === 'rejected' || (r.status === 'fulfilled' && !r.value.success));
    if (failures.length > 0) {
      workflow.status = OrchestrationEngine.WorkflowStatus.FAILED;
      this.emit('workflow:failed', { workflow, failures });
      return { success: false, failures };
    }

    workflow.status = OrchestrationEngine.WorkflowStatus.COMPLETED;
    workflow.completedAt = new Date();
    this.emit('workflow:completed', workflow);

    return { success: true, completed: true, workflow };
  }

  /**
   * Execute with adaptive strategy (router decides based on context)
   */
  async executeAdaptive(workflow) {
    // Use A2A Router's capability matching to dynamically route steps
    for (let i = workflow.currentStep; i < workflow.steps.length; i++) {
      const step = workflow.steps[i];

      if (step.type === 'task') {
        // Route to best available agent
        const routed = await this.router.capabilityRoute({
          id: uuidv4(),
          type: 'TASK',
          from: 'orchestration',
          to: `capability:${step.config.requiredCapability || 'general'}`,
          timestamp: Date.now(),
          payload: {
            task: step.name,
            context: workflow.context,
            variables: workflow.variables
          }
        });

        if (!routed.success) {
          step.status = OrchestrationEngine.StepStatus.FAILED;
          step.error = routed.error;
          workflow.status = OrchestrationEngine.WorkflowStatus.FAILED;
          return { success: false, error: routed.error };
        }
      } else {
        await this.executeStep(workflow, step);
      }

      workflow.currentStep = i + 1;
    }

    workflow.status = OrchestrationEngine.WorkflowStatus.COMPLETED;
    workflow.completedAt = new Date();
    this.emit('workflow:completed', workflow);

    return { success: true, completed: true, workflow };
  }

  /**
   * Execute a single step
   */
  async executeStep(workflow, step) {
    step.status = OrchestrationEngine.StepStatus.RUNNING;
    step.startedAt = new Date();
    step.attempts++;

    this.emit('step:started', { workflow, step });

    try {
      let result;

      switch (step.type) {
        case 'task':
          result = await this.executeTaskStep(workflow, step);
          break;
        case 'condition':
          result = await this.executeConditionStep(workflow, step);
          break;
        case 'sub-workflow':
          result = await this.executeSubWorkflowStep(workflow, step);
          break;
        case 'delay':
          result = await this.executeDelayStep(workflow, step);
          break;
        case 'notification':
          result = await this.executeNotificationStep(workflow, step);
          break;
        default:
          result = { success: true, value: null };
      }

      step.status = result.success ? OrchestrationEngine.StepStatus.COMPLETED : OrchestrationEngine.StepStatus.FAILED;
      step.result = result.value;
      step.completedAt = new Date();

      this.emit('step:completed', { workflow, step, result });

      return result;

    } catch (error) {
      step.status = OrchestrationEngine.StepStatus.FAILED;
      step.error = error.message;
      step.completedAt = new Date();

      this.emit('step:failed', { workflow, step, error });

      return { success: false, error: error.message };
    }
  }

  /**
   * Execute a task step (delegate to router)
   */
  async executeTaskStep(workflow, step) {
    const capability = step.config.requiredCapability;

    // Create subtask for this step
    const taskId = `workflow-${workflow.id}-step-${step.id}`;

    this.router.subtaskManager.createParentTask(taskId, 1, 'single');

    // Route to capable agent
    const routed = await this.router.capabilityRoute({
      id: uuidv4(),
      type: 'TASK',
      from: 'orchestration',
      to: capability ? `capability:${capability}` : 'router',
      timestamp: Date.now(),
      priority: step.config.priority || 'NORMAL',
      payload: {
        taskId,
        task: step.name,
        input: workflow.variables,
        context: workflow.context
      }
    });

    if (!routed.success) {
      return { success: false, error: routed.error || 'NO_AGENT_AVAILABLE' };
    }

    // For now, return success (in real impl, would wait for result callback)
    return { success: true, value: { routed: true, agent: routed.agent } };
  }

  /**
   * Execute a condition step
   */
  async executeConditionStep(workflow, step) {
    const condition = step.config.condition;
    let result = false;

    try {
      // Evaluate condition expression
      const expr = new Function('variables', 'context', `return ${condition}`);
      result = expr(workflow.variables, workflow.context);
    } catch (error) {
      return { success: false, error: `Condition evaluation failed: ${error.message}` };
    }

    return { success: true, value: result };
  }

  /**
   * Execute a sub-workflow step
   */
  async executeSubWorkflowStep(workflow, step) {
    const subWorkflowId = step.config.workflowId;

    if (!this.workflows.has(subWorkflowId)) {
      return { success: false, error: 'SUB_WORKFLOW_NOT_FOUND' };
    }

    const result = await this.startWorkflow(subWorkflowId, workflow.context);

    return result;
  }

  /**
   * Execute a delay step
   */
  async executeDelayStep(workflow, step) {
    const delayMs = step.config.duration || 1000;

    await new Promise(resolve => setTimeout(resolve, delayMs));

    return { success: true, value: { delayed: delayMs } };
  }

  /**
   * Execute a notification step
   */
  async executeNotificationStep(workflow, step) {
    const notification = step.config;

    this.emit('notification', {
      workflow,
      step,
      type: notification.type || 'info',
      message: notification.message || step.name,
      recipients: notification.recipients || []
    });

    return { success: true, value: { notified: true } };
  }

  /**
   * Find next step after a conditional
   */
  findNextStep(workflow, currentIdx, branch) {
    const currentStep = workflow.steps[currentIdx];
    const targetLabel = branch === 'true' ? currentStep.config.trueLabel : currentStep.config.falseLabel;

    for (let i = currentIdx + 1; i < workflow.steps.length; i++) {
      if (workflow.steps[i].name === targetLabel) {
        return i;
      }
    }

    return -1;
  }

  /**
   * Pause a running workflow
   */
  pauseWorkflow(workflowId) {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      return { success: false, error: 'WORKFLOW_NOT_FOUND' };
    }

    if (workflow.status !== OrchestrationEngine.WorkflowStatus.RUNNING) {
      return { success: false, error: 'WORKFLOW_NOT_RUNNING' };
    }

    workflow.status = OrchestrationEngine.WorkflowStatus.PAUSED;
    workflow.pausedAt = new Date();

    this.emit('workflow:paused', workflow);

    return { success: true, workflow };
  }

  /**
   * Resume a paused workflow
   */
  async resumeWorkflow(workflowId) {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      return { success: false, error: 'WORKFLOW_NOT_FOUND' };
    }

    if (workflow.status !== OrchestrationEngine.WorkflowStatus.PAUSED) {
      return { success: false, error: 'WORKFLOW_NOT_PAUSED' };
    }

    workflow.status = OrchestrationEngine.WorkflowStatus.RUNNING;
    workflow.pausedAt = null;

    this.emit('workflow:resumed', workflow);

    return this.startWorkflow(workflowId, workflow.context);
  }

  /**
   * Cancel a workflow
   */
  cancelWorkflow(workflowId) {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      return { success: false, error: 'WORKFLOW_NOT_FOUND' };
    }

    workflow.status = OrchestrationEngine.WorkflowStatus.CANCELED;
    workflow.completedAt = new Date();

    this.emit('workflow:canceled', workflow);

    return { success: true, workflow };
  }

  /**
   * Get workflow status
   */
  getWorkflowStatus(workflowId) {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      return null;
    }

    return {
      id: workflow.id,
      name: workflow.name,
      status: workflow.status,
      currentStep: workflow.currentStep,
      totalSteps: workflow.steps.length,
      progress: Math.round((workflow.currentStep / workflow.steps.length) * 100),
      strategy: workflow.strategy,
      steps: workflow.steps.map(s => ({
        id: s.id,
        name: s.name,
        status: s.status,
        error: s.error
      })),
      createdAt: workflow.createdAt,
      startedAt: workflow.startedAt,
      completedAt: workflow.completedAt,
      pausedAt: workflow.pausedAt
    };
  }

  /**
   * List all workflows
   */
  listWorkflows(filter) {
    const all = Array.from(this.workflows.values());

    if (!filter) {
      return all.map(w => this.getWorkflowStatus(w.id));
    }

    return all
      .filter(w => {
        if (filter.status && w.status !== filter.status) return false;
        if (filter.strategy && w.strategy !== filter.strategy) return false;
        return true;
      })
      .map(w => this.getWorkflowStatus(w.id));
  }

  /**
   * Delete a workflow
   */
  deleteWorkflow(workflowId) {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      return { success: false, error: 'WORKFLOW_NOT_FOUND' };
    }

    if (workflow.status === OrchestrationEngine.WorkflowStatus.RUNNING) {
      return { success: false, error: 'CANNOT_DELETE_RUNNING_WORKFLOW' };
    }

    this.workflows.delete(workflowId);
    this.definitions.delete(workflowId);

    this.emit('workflow:deleted', { workflowId });

    return { success: true };
  }

  /**
   * Update workflow variables
   */
  updateVariables(workflowId, variables) {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      return { success: false, error: 'WORKFLOW_NOT_FOUND' };
    }

    workflow.variables = { ...workflow.variables, ...variables };

    return { success: true, variables: workflow.variables };
  }

  /**
   * Get step result
   */
  getStepResult(workflowId, stepId) {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      return null;
    }

    const step = workflow.steps.find(s => s.id === stepId);
    if (!step) {
      return null;
    }

    return {
      status: step.status,
      result: step.result,
      error: step.error,
      attempts: step.attempts,
      startedAt: step.startedAt,
      completedAt: step.completedAt
    };
  }
}

export default OrchestrationEngine;

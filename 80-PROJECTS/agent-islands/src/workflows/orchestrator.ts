/**
 * Workflow Orchestrator - 工作流编排器
 * 定义跨Agent协作的标准工作流
 */
import { agentHub, type Task, type AggregatedResult } from '../mcp-sdk/agent-hub';

export interface WorkflowStep {
  id: string;
  agentId: string;
  action: string;
  input: any;
  dependsOn?: string[];
  timeout?: number;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
  onComplete?: (result: any) => void;
  onError?: (error: any) => void;
}

export interface WorkflowResult {
  workflowId: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  results: Map<string, any>;
  errors: Array<{ stepId: string; error: string }>;
  startTime: Date;
  endTime?: Date;
  totalDuration?: number;
}

/**
 * 工作流编排器
 */
class WorkflowOrchestrator {
  private workflows: Map<string, Workflow> = new Map();
  private runningWorkflows: Map<string, WorkflowResult> = new Map();
  private workflowCounter = 0;

  constructor() {
    this.registerBuiltInWorkflows();
  }

  /**
   * 注册预定义工作流
   */
  private registerBuiltInWorkflows() {
    // 1. 市场情绪分析工作流
    this.registerWorkflow({
      id: 'market_sentiment_analysis',
      name: '市场情绪分析',
      description: '从NewsHub获取新闻，通过情绪分析评估市场情绪',
      steps: [
        {
          id: 'fetch_news',
          agentId: 'newshub',
          action: 'get_latest_news',
          input: { maxItems: 100 }
        },
        {
          id: 'analyze_sentiment',
          agentId: 'newshub',
          action: 'analyze_sentiment',
          input: { market: 'a-share' },
          dependsOn: ['fetch_news']
        },
        {
          id: 'generate_report',
          agentId: 'ai-chat',
          action: 'summarize',
          input: {},
          dependsOn: ['analyze_sentiment']
        }
      ]
    });

    // 2. 股票研究工作流
    this.registerWorkflow({
      id: 'stock_research',
      name: '股票研究',
      description: '综合分析股票相关新闻、技术指标、生成交易建议',
      steps: [
        {
          id: 'get_news',
          agentId: 'newshub',
          action: 'get_stock_news',
          input: {}
        },
        {
          id: 'get_price',
          agentId: 'stock-analyzer',
          action: 'get_stock_price',
          input: {}
        },
        {
          id: 'analyze_technical',
          agentId: 'stock-analyzer',
          action: 'analyze_stock',
          input: { indicators: ['ma', 'kdj', 'macd'] },
          dependsOn: ['get_price']
        },
        {
          id: 'detect_patterns',
          agentId: 'stock-analyzer',
          action: 'detect_patterns',
          input: {},
          dependsOn: ['get_price']
        },
        {
          id: 'generate_signal',
          agentId: 'stock-analyzer',
          action: 'generate_trading_signal',
          input: { strategy: 'momentum' },
          dependsOn: ['analyze_technical', 'detect_patterns', 'get_news']
        }
      ]
    });

    // 3. 热点选股工作流
    this.registerWorkflow({
      id: 'hot_stock_picker',
      name: '热点选股',
      description: '从热门话题中筛选相关股票并进行技术分析',
      steps: [
        {
          id: 'get_trending',
          agentId: 'newshub',
          action: 'get_trending_topics',
          input: { limit: 10 }
        },
        {
          id: 'get_trending_news',
          agentId: 'newshub',
          action: 'search_news',
          input: { query: '{trending_topic}' },
          dependsOn: ['get_trending']
        },
        {
          id: 'extract_stocks',
          agentId: 'ai-chat',
          action: 'extract_entities',
          input: {},
          dependsOn: ['get_trending_news']
        },
        {
          id: 'analyze_stocks',
          agentId: 'stock-analyzer',
          action: 'analyze_stock',
          input: {},
          dependsOn: ['extract_stocks']
        }
      ]
    });

    // 4. 投资组合风险评估工作流
    this.registerWorkflow({
      id: 'portfolio_risk_assessment',
      name: '投资组合风险评估',
      description: '综合评估投资组合的风险、收益、相关性',
      steps: [
        {
          id: 'get_portfolio',
          agentId: 'trading-bot',
          action: 'get_positions',
          input: {}
        },
        {
          id: 'get_market',
          agentId: 'stock-analyzer',
          action: 'get_market_sentiment',
          input: {}
        },
        {
          id: 'analyze_risk',
          agentId: 'trading-bot',
          action: 'calculate_risk',
          input: {},
          dependsOn: ['get_portfolio', 'get_market']
        },
        {
          id: 'optimize',
          agentId: 'trading-bot',
          action: 'optimize_portfolio',
          input: {},
          dependsOn: ['analyze_risk']
        }
      ]
    });

    // 5. 深度研究工作流
    this.registerWorkflow({
      id: 'deep_research',
      name: '深度研究',
      description: '对特定主题进行深度研究和报告生成',
      steps: [
        {
          id: 'search_web',
          agentId: 'deep-research',
          action: 'web_search',
          input: {}
        },
        {
          id: 'analyze_news',
          agentId: 'newshub',
          action: 'search_news',
          input: {},
          dependsOn: ['search_web']
        },
        {
          id: 'analyze_stocks',
          agentId: 'stock-analyzer',
          action: 'analyze_stock',
          input: {},
          dependsOn: ['search_web']
        },
        {
          id: 'synthesize',
          agentId: 'deep-research',
          action: 'synthesize_report',
          input: {},
          dependsOn: ['analyze_news', 'analyze_stocks']
        }
      ]
    });

    // 6. 交易信号生成工作流
    this.registerWorkflow({
      id: 'trading_signal',
      name: '交易信号生成',
      description: '综合多Agent信息生成交易信号',
      steps: [
        {
          id: 'get_news',
          agentId: 'newshub',
          action: 'get_latest_news',
          input: { maxItems: 50 }
        },
        {
          id: 'get_sentiment',
          agentId: 'newshub',
          action: 'analyze_sentiment',
          input: {},
          dependsOn: ['get_news']
        },
        {
          id: 'get_price',
          agentId: 'stock-analyzer',
          action: 'get_stock_price',
          input: {}
        },
        {
          id: 'get_technical',
          agentId: 'stock-analyzer',
          action: 'analyze_stock',
          input: {},
          dependsOn: ['get_price']
        },
        {
          id: 'generate_signal',
          agentId: 'trading-bot',
          action: 'generate_signal',
          input: {},
          dependsOn: ['get_sentiment', 'get_technical']
        }
      ]
    });

    console.log(`✅ 已注册 ${this.workflows.size} 个预定义工作流`);
  }

  /**
   * 注册工作流
   */
  registerWorkflow(workflow: Workflow): void {
    this.workflows.set(workflow.id, workflow);
    console.log(`📋 注册工作流: ${workflow.name} (${workflow.id})`);
  }

  /**
   * 获取所有工作流
   */
  getWorkflows(): Workflow[] {
    return Array.from(this.workflows.values());
  }

  /**
   * 获取工作流
   */
  getWorkflow(id: string): Workflow | undefined {
    return this.workflows.get(id);
  }

  /**
   * 执行工作流
   */
  async execute(workflowId: string, initialInput?: any): Promise<WorkflowResult> {
    const workflow = this.workflows.get(workflowId);
    if (!workflow) {
      throw new Error(`Workflow not found: ${workflowId}`);
    }

    this.workflowCounter++;
    const resultId = `wf_${Date.now()}_${this.workflowCounter}`;
    
    const result: WorkflowResult = {
      workflowId,
      status: 'running',
      results: new Map(),
      errors: [],
      startTime: new Date()
    };

    this.runningWorkflows.set(resultId, result);
    console.log(`\n🚀 启动工作流: ${workflow.name} (${resultId})`);
    console.log('═'.repeat(50));

    try {
      // 按依赖关系排序执行
      const sortedSteps = this.topologicalSort(workflow.steps);
      
      // 填充初始输入中的变量
      let context = { ...initialInput };

      for (const step of sortedSteps) {
        console.log(`\n📍 执行步骤: ${step.id} -> ${step.agentId}:${step.action}`);

        // 替换变量
        const input = this.resolveVariables(step.input, context);

        // 构建任务
        const task: Task = {
          id: `${resultId}_${step.id}`,
          type: step.action,
          targetAgents: [step.agentId],
          payload: input,
          priority: 'medium',
          timeout: step.timeout || 30000
        };

        // 执行任务
        await agentHub.dispatchTask(task);

        // 获取结果
        const taskResult = agentHub.aggregateResults(task.id);
        
        if (taskResult.successful > 0) {
          const stepResult = taskResult.data[0];
          result.results.set(step.id, stepResult);
          context[`${step.id}_result`] = stepResult;
          console.log(`✅ 步骤完成: ${step.id}`);
        } else {
          const error = taskResult.errors[0];
          result.errors.push({ stepId: step.id, error: error.error });
          console.log(`❌ 步骤失败: ${step.id} - ${error.error}`);
        }
      }

      // 聚合所有结果
      const finalResult = this.aggregateWorkflowResult(result);
      
      result.status = result.errors.length === 0 ? 'completed' : 'failed';
      result.endTime = new Date();
      result.totalDuration = result.endTime.getTime() - result.startTime.getTime();

      console.log('═'.repeat(50));
      console.log(`✅ 工作流完成: ${workflow.name}`);
      console.log(`   状态: ${result.status}`);
      console.log(`   耗时: ${(result.totalDuration / 1000).toFixed(2)}s`);
      console.log(`   成功步骤: ${result.results.size}/${workflow.steps.length}`);

      if (result.errors.length > 0) {
        console.log(`   失败步骤: ${result.errors.map(e => e.stepId).join(', ')}`);
      }

      // 调用完成回调
      if (result.status === 'completed' && workflow.onComplete) {
        workflow.onComplete(finalResult);
      } else if (result.status === 'failed' && workflow.onError) {
        workflow.onError(result.errors);
      }

      return result;
    } catch (error: any) {
      result.status = 'failed';
      result.errors.push({ stepId: 'workflow', error: error.message });
      result.endTime = new Date();
      result.totalDuration = result.endTime.getTime() - result.startTime.getTime();
      
      if (workflow.onError) {
        workflow.onError(error);
      }
      
      throw error;
    }
  }

  /**
   * 拓扑排序（根据依赖关系排序步骤）
   */
  private topologicalSort(steps: WorkflowStep[]): WorkflowStep[] {
    const sorted: WorkflowStep[] = [];
    const visited = new Set<string>();
    const visiting = new Set<string>();

    const visit = (step: WorkflowStep) => {
      if (visited.has(step.id)) return;
      if (visiting.has(step.id)) {
        throw new Error(`Circular dependency detected: ${step.id}`);
      }

      visiting.add(step.id);

      // 先访问依赖的步骤
      if (step.dependsOn) {
        for (const depId of step.dependsOn) {
          const dep = steps.find(s => s.id === depId);
          if (dep) {
            visit(dep);
          }
        }
      }

      visiting.delete(step.id);
      visited.add(step.id);
      sorted.push(step);
    };

    for (const step of steps) {
      visit(step);
    }

    return sorted;
  }

  /**
   * 解析变量
   */
  private resolveVariables(input: any, context: any): any {
    if (typeof input === 'string') {
      // 替换 {variable} 格式的变量
      return input.replace(/\{(\w+)\}/g, (_, key) => {
        return context[key] !== undefined ? context[key] : input;
      });
    }

    if (Array.isArray(input)) {
      return input.map(item => this.resolveVariables(item, context));
    }

    if (typeof input === 'object' && input !== null) {
      const resolved: any = {};
      for (const [key, value] of Object.entries(input)) {
        resolved[key] = this.resolveVariables(value, context);
      }
      return resolved;
    }

    return input;
  }

  /**
   * 聚合工作流结果
   */
  private aggregateWorkflowResult(result: WorkflowResult): any {
    const aggregated: Record<string, any> = {
      workflowId: result.workflowId,
      status: result.status,
      duration: result.totalDuration,
      steps: {}
    };

    for (const [stepId, stepResult] of result.results) {
      aggregated.steps[stepId] = stepResult;
    }

    if (result.errors.length > 0) {
      aggregated.errors = result.errors;
    }

    return aggregated;
  }

  /**
   * 获取运行中的工作流
   */
  getRunningWorkflows(): WorkflowResult[] {
    return Array.from(this.runningWorkflows.values())
      .filter(r => r.status === 'running');
  }

  /**
   * 获取工作流统计
   */
  getStats(): any {
    const workflows = this.getWorkflows();
    const running = this.getRunningWorkflows();
    
    return {
      total: workflows.length,
      running: running.length,
      completed: Array.from(this.runningWorkflows.values())
        .filter(r => r.status === 'completed').length,
      failed: Array.from(this.runningWorkflows.values())
        .filter(r => r.status === 'failed').length,
      workflowNames: workflows.map(w => w.name)
    };
  }
}

// 导出单例
export const workflowOrchestrator = new WorkflowOrchestrator();

export default WorkflowOrchestrator;

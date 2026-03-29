/**
 * AgentHub - 群岛核心调度器
 * 负责任务分发、结果聚合、状态管理
 * 
 * 基于Model Context Protocol (MCP)的标准接口
 */
import { EventEmitter } from 'events';

export interface AgentInfo {
  id: string;
  name: string;
  type: 'news' | 'stock' | 'trading' | 'chat' | 'research';
  status: 'active' | 'idle' | 'error' | 'offline';
  capabilities: string[];
  endpoint?: string;
  mcpServer?: boolean;
  metadata?: Record<string, any>;
}

export interface Task {
  id: string;
  type: string;
  targetAgents: string[];
  payload: any;
  priority: 'high' | 'medium' | 'low';
  timeout?: number;
  retry?: number;
}

export interface TaskResult {
  taskId: string;
  agentId: string;
  agentName: string;
  success: boolean;
  data?: any;
  error?: string;
  duration?: number;
  timestamp: Date;
}

export interface AggregatedResult {
  taskId: string;
  total: number;
  successful: number;
  failed: number;
  duration: number;
  data: any[];
  errors: Array<{ agentId: string; agentName: string; error: string }>;
  timestamp: Date;
}

export class AgentHub extends EventEmitter {
  private agents: Map<string, AgentInfo> = new Map();
  private tasks: Map<string, Task> = new Map();
  private results: Map<string, TaskResult[]> = new Map();
  private mcClient: any = null;
  private taskCounter = 0;

  constructor() {
    super();
    this.setMaxListeners(100);
    this.initMCPClient();
  }

  private async initMCPClient() {
    try {
      // 尝试加载MCP SDK
      const MCPClient = await import('@modelcontextprotocol/sdk/client/index.js').catch(() => null);
      if (MCPClient) {
        const { Client } = MCPClient;
        this.mcClient = new Client({
          name: 'agent-islands-hub',
          version: '1.0.0'
        });
        console.log('✅ MCP客户端初始化完成');
      } else {
        console.log('⚠️ MCP SDK未安装，使用模拟模式');
      }
    } catch (e) {
      console.log('⚠️ MCP客户端初始化失败，使用模拟模式:', (e as Error).message);
    }
  }

  // ============ Agent管理 ============

  /**
   * 注册一个Agent到Hub
   */
  async registerAgent(agent: AgentInfo): Promise<void> {
    this.agents.set(agent.id, {
      ...agent,
      status: 'idle'
    });
    this.emit('agent:registered', agent);
    console.log(`📝 Agent注册: ${agent.name} (${agent.type}) - ${agent.capabilities.join(', ')}`);
  }

  /**
   * 批量注册Agent
   */
  async registerAgents(agents: AgentInfo[]): Promise<void> {
    for (const agent of agents) {
      await this.registerAgent(agent);
    }
  }

  /**
   * 注销Agent
   */
  async unregisterAgent(agentId: string): Promise<void> {
    const agent = this.agents.get(agentId);
    this.agents.delete(agentId);
    this.emit('agent:unregistered', { agentId, agent });
  }

  /**
   * 更新Agent状态
   */
  async updateAgentStatus(agentId: string, status: AgentInfo['status']): Promise<void> {
    const agent = this.agents.get(agentId);
    if (agent) {
      agent.status = status;
      this.emit('agent:statusChanged', { agentId, status });
    }
  }

  // ============ 查询接口 ============

  /**
   * 获取所有Agent
   */
  getAgents(): AgentInfo[] {
    return Array.from(this.agents.values());
  }

  /**
   * 根据类型获取Agent
   */
  getAgentsByType(type: AgentInfo['type']): AgentInfo[] {
    return Array.from(this.agents.values()).filter(a => a.type === type);
  }

  /**
   * 根据ID获取Agent
   */
  getAgent(agentId: string): AgentInfo | undefined {
    return this.agents.get(agentId);
  }

  /**
   * 查找具有特定能力的Agent
   */
  getAgentsWithCapability(capability: string): AgentInfo[] {
    return Array.from(this.agents.values())
      .filter(a => a.capabilities.includes(capability));
  }

  // ============ 任务分发 ============

  /**
   * 创建任务ID
   */
  private createTaskId(): string {
    this.taskCounter++;
    return `task_${Date.now()}_${this.taskCounter}`;
  }

  /**
   * 分发任务到多个Agent
   */
  async dispatchTask(task: Task): Promise<string> {
    const taskId = task.id || this.createTaskId();
    const fullTask = { ...task, id: taskId };
    
    this.tasks.set(taskId, fullTask);
    this.results.set(taskId, []);
    this.emit('task:created', fullTask);
    
    console.log(`\n📤 分发任务 ${taskId}: ${task.type} -> ${task.targetAgents.join(', ')}`);

    // 并行分发到目标Agent
    const promises = task.targetAgents.map(agentId => this.executeOnAgent(fullTask, agentId));
    await Promise.allSettled(promises);

    const results = this.results.get(taskId)!;
    const successful = results.filter(r => r.success).length;
    
    console.log(`✅ 任务完成: ${taskId} - 成功 ${successful}/${results.length}`);
    this.emit('task:completed', { taskId, results });

    return taskId;
  }

  /**
   * 在单个Agent上执行任务
   */
  private async executeOnAgent(task: Task, agentId: string): Promise<TaskResult> {
    const agent = this.agents.get(agentId);
    const startTime = Date.now();

    if (!agent) {
      const result: TaskResult = {
        taskId: task.id,
        agentId,
        agentName: 'unknown',
        success: false,
        error: `Agent ${agentId} not found`,
        duration: Date.now() - startTime,
        timestamp: new Date()
      };
      this.results.get(task.id)!.push(result);
      return result;
    }

    // 更新状态
    await this.updateAgentStatus(agentId, 'active');

    try {
      let result: TaskResult;

      // 通过MCP协议调用
      if (this.mcClient && agent.mcpServer) {
        result = await this.callMCP(agent, task, startTime);
      } else {
        // 模拟调用
        result = await this.simulateCall(agent, task, startTime);
      }

      this.results.get(task.id)!.push(result);
      return result;
    } catch (error: any) {
      const result: TaskResult = {
        taskId: task.id,
        agentId,
        agentName: agent.name,
        success: false,
        error: error.message,
        duration: Date.now() - startTime,
        timestamp: new Date()
      };
      this.results.get(task.id)!.push(result);
      return result;
    } finally {
      await this.updateAgentStatus(agentId, 'idle');
    }
  }

  /**
   * 通过MCP协议调用Agent
   */
  private async callMCP(agent: AgentInfo, task: Task, startTime: number): Promise<TaskResult> {
    const toolName = this.getToolForTask(task.type);
    
    try {
      const response = await this.mcClient.callTool({
        name: toolName,
        arguments: task.payload
      }, { timeout: task.timeout || 30000 });
      
      return {
        taskId: task.id,
        agentId: agent.id,
        agentName: agent.name,
        success: true,
        data: response,
        duration: Date.now() - startTime,
        timestamp: new Date()
      };
    } catch (error: any) {
      throw error;
    }
  }

  /**
   * 模拟调用（用于测试或无MCP连接时）
   */
  private async simulateCall(agent: AgentInfo, task: Task, startTime: number): Promise<TaskResult> {
    // 模拟处理延迟
    await new Promise(resolve => setTimeout(resolve, 100 + Math.random() * 200));
    
    return {
      taskId: task.id,
      agentId: agent.id,
      agentName: agent.name,
      success: true,
      data: {
        agent: agent.name,
        processed: true,
        simulated: true,
        input: task.payload,
        processedAt: new Date().toISOString()
      },
      duration: Date.now() - startTime,
      timestamp: new Date()
    };
  }

  /**
   * 映射任务类型到MCP工具名
   */
  private getToolForTask(taskType: string): string {
    const toolMap: Record<string, string> = {
      'news:fetch': 'get_latest_news',
      'news:sentiment': 'analyze_sentiment',
      'stock:analyze': 'analyze_stock',
      'stock:price': 'get_stock_price',
      'trading:execute': 'execute_trade',
      'trading:signal': 'generate_signal',
      'chat:respond': 'generate_response',
      'research:query': 'research_query'
    };
    return toolMap[taskType] || 'default_handler';
  }

  // ============ 结果处理 ============

  /**
   * 获取任务原始结果
   */
  getTaskResults(taskId: string): TaskResult[] {
    return this.results.get(taskId) || [];
  }

  /**
   * 聚合多Agent结果
   */
  aggregateResults(taskId: string): AggregatedResult {
    const results = this.getTaskResults(taskId);
    const successful = results.filter(r => r.success);
    const failed = results.filter(r => !r.success);

    return {
      taskId,
      total: results.length,
      successful: successful.length,
      failed: failed.length,
      duration: results.reduce((sum, r) => sum + (r.duration || 0), 0),
      data: successful.map(r => r.data),
      errors: failed.map(r => ({ 
        agentId: r.agentId, 
        agentName: r.agentName,
        error: r.error || 'Unknown error' 
      })),
      timestamp: new Date()
    };
  }

  /**
   * 智能合并结果
   */
  mergeResults(taskId: string): any {
    const aggregated = this.aggregateResults(taskId);
    
    // 根据数据类型智能合并
    if (aggregated.data.length === 0) {
      return { error: 'No successful results', errors: aggregated.errors };
    }

    // 如果所有结果都是数组，合并
    if (aggregated.data.every(d => Array.isArray(d))) {
      return aggregated.data.flat();
    }

    // 如果有news类型数据，合并新闻
    const newsItems = aggregated.data
      .filter(d => d?.items || d?.news || d?.articles)
      .flatMap(d => d.items || d.news || d.articles || []);
    
    if (newsItems.length > 0) {
      return { items: this.deduplicateNews(newsItems) };
    }

    // 否则返回第一个成功结果
    return aggregated.data[0];
  }

  /**
   * 新闻去重
   */
  private deduplicateNews(news: any[]): any[] {
    const seen = new Set<string>();
    return news.filter(item => {
      const key = item.url || item.link || item.id || JSON.stringify(item);
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  // ============ 生命周期 ============

  /**
   * 启动Hub并注册默认Agent
   */
  async start(): Promise<void> {
    console.log('🚀 AgentHub启动中...');
    console.log('═'.repeat(50));

    // 注册默认Agent
    await this.registerAgents([
      {
        id: 'newshub',
        name: 'NewsHub',
        type: 'news',
        status: 'idle',
        capabilities: ['news_fetch', 'sentiment_analysis', 'trend_detection', 'topic_clustering'],
        mcpServer: true,
        endpoint: process.env.NEWSHUB_ENDPOINT
      },
      {
        id: 'stock-analyzer',
        name: 'StockAnalyzer',
        type: 'stock',
        status: 'idle',
        capabilities: ['stock_analysis', 'pattern_recognition', 'price_prediction', 'technical_indicators'],
        mcpServer: true,
        endpoint: process.env.STOCK_ANALYZER_ENDPOINT
      },
      {
        id: 'trading-bot',
        name: 'RLTradingBot',
        type: 'trading',
        status: 'idle',
        capabilities: ['trade_execution', 'risk_management', 'portfolio_optimization', 'position_sizing'],
        mcpServer: true,
        endpoint: process.env.TRADING_BOT_ENDPOINT
      },
      {
        id: 'ai-chat',
        name: 'AIChatAgent',
        type: 'chat',
        status: 'idle',
        capabilities: ['chat', 'reasoning', 'summarization', 'question_answering'],
        mcpServer: true,
        endpoint: process.env.AI_CHAT_ENDPOINT
      },
      {
        id: 'deep-research',
        name: 'DeepResearchAgent',
        type: 'research',
        status: 'idle',
        capabilities: ['web_search', 'fact_check', 'report_generation', 'data_analysis'],
        mcpServer: true,
        endpoint: process.env.RESEARCH_ENDPOINT
      }
    ]);

    console.log('═'.repeat(50));
    console.log(`✅ AgentHub已启动`);
    console.log(`   - 注册Agent: ${this.agents.size}`);
    console.log(`   - 类型分布: ${[...new Set(Array.from(this.agents.values()).map(a => a.type))].join(', ')}`);
  }

  /**
   * 停止Hub
   */
  async stop(): Promise<void> {
    console.log('🛑 AgentHub停止中...');
    
    // 取消所有Agent注册
    for (const agentId of this.agents.keys()) {
      await this.unregisterAgent(agentId);
    }

    // 清理状态
    this.tasks.clear();
    this.results.clear();
    
    this.emit('hub:stopped');
    console.log('✅ AgentHub已停止');
  }

  /**
   * 获取Hub统计信息
   */
  getStats(): any {
    const agents = this.getAgents();
    return {
      totalAgents: agents.length,
      activeAgents: agents.filter(a => a.status === 'active').length,
      idleAgents: agents.filter(a => a.status === 'idle').length,
      errorAgents: agents.filter(a => a.status === 'error').length,
      byType: agents.reduce((acc, a) => {
        acc[a.type] = (acc[a.type] || 0) + 1;
        return acc;
      }, {} as Record<string, number>),
      totalTasks: this.tasks.size,
      totalResults: this.results.size
    };
  }
}

// 导出单例
export const agentHub = new AgentHub();

export default AgentHub;

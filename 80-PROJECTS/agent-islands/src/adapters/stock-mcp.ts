/**
 * Stock Analyzer MCP Adapter
 * 股票分析服务MCP封装
 */
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListToolsRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

interface StockData {
  code: string;
  name: string;
  price: number;
  change: number;
  changePercent: number;
  volume: number;
  amount: number;
  high: number;
  low: number;
  open: number;
  close: number;
  timestamp: string;
}

interface AnalysisResult {
  symbol: string;
  signal: 'buy' | 'sell' | 'hold' | 'strong_buy' | 'strong_sell';
  confidence: number;
  indicators: Record<string, number>;
  patterns: string[];
  recommendation: string;
}

/**
 * Stock Analyzer MCP Server
 */
class StockAnalyzerMCPServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'stock-analyzer-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupHandlers();
  }

  private setupHandlers() {
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'get_stock_price',
            description: '获取股票实时价格',
            inputSchema: {
              type: 'object',
              properties: {
                codes: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: '股票代码列表，如 ["600519", "000858"]'
                },
                market: {
                  type: 'string',
                  enum: ['SH', 'SZ', 'HK', 'US'],
                  default: 'SH',
                  description: '市场'
                }
              }
            }
          },
          {
            name: 'analyze_stock',
            description: '综合分析股票技术面和基本面',
            inputSchema: {
              type: 'object',
              properties: {
                code: { type: 'string', description: '股票代码' },
                indicators: {
                  type: 'array',
                  items: { type: 'string' },
                  description: '分析指标: ma, kdj, macd, boll, rsi, volume'
                },
                period: {
                  type: 'string',
                  enum: ['daily', 'weekly', 'monthly'],
                  default: 'daily'
                }
              }
            }
          },
          {
            name: 'detect_patterns',
            description: '技术形态识别',
            inputSchema: {
              type: 'object',
              properties: {
                code: { type: 'string' },
                patterns: {
                  type: 'array',
                  items: { type: 'string' },
                  description: '形态类型: golden_cross, death_cross, head_shoulders, double_top, double_bottom, cup_handle'
                }
              }
            }
          },
          {
            name: 'calculate_indicators',
            description: '计算技术指标',
            inputSchema: {
              type: 'object',
              properties: {
                code: { type: 'string' },
                indicators: {
                  type: 'array',
                  items: { type: 'string' }
                },
                params: {
                  type: 'object',
                  description: '指标参数'
                }
              }
            }
          },
          {
            name: 'compare_stocks',
            description: '对比多只股票',
            inputSchema: {
              type: 'object',
              properties: {
                codes: { type: 'array', items: { type: 'string' } },
                metrics: {
                  type: 'array',
                  items: { type: 'string' },
                  description: '对比指标: pe, pb, roe, growth, dividend'
                }
              }
            }
          },
          {
            name: 'generate_trading_signal',
            description: '生成交易信号',
            inputSchema: {
              type: 'object',
              properties: {
                code: { type: 'string' },
                strategy: {
                  type: 'string',
                  enum: ['momentum', 'mean_reversion', 'trend_following', 'breakout'],
                  default: 'momentum'
                },
                riskLevel: {
                  type: 'string',
                  enum: ['low', 'medium', 'high'],
                  default: 'medium'
                }
              }
            }
          },
          {
            name: 'screen_stocks',
            description: '条件选股',
            inputSchema: {
              type: 'object',
              properties: {
                conditions: {
                  type: 'object',
                  properties: {
                    priceRange: { type: 'array', items: { type: 'number' } },
                    peRange: { type: 'array', items: { type: 'number' } },
                    volumeMin: { type: 'number' },
                    changeMin: { type: 'number' },
                    industry: { type: 'string' }
                  }
                }
              }
            }
          },
          {
            name: 'get_market_sentiment',
            description: '获取市场情绪指标',
            inputSchema: {
              type: 'object',
              properties: {
                market: {
                  type: 'string',
                  enum: ['SH', 'SZ', 'all'],
                  default: 'all'
                }
              }
            }
          }
        ]
      };
    });

    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'get_stock_price':
            return await this.getStockPrice(args);
          case 'analyze_stock':
            return await this.analyzeStock(args);
          case 'detect_patterns':
            return await this.detectPatterns(args);
          case 'calculate_indicators':
            return await this.calculateIndicators(args);
          case 'compare_stocks':
            return await this.compareStocks(args);
          case 'generate_trading_signal':
            return await this.generateSignal(args);
          case 'screen_stocks':
            return await this.screenStocks(args);
          case 'get_market_sentiment':
            return await this.getMarketSentiment(args);
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error: any) {
        return {
          content: [{ type: 'text', text: JSON.stringify({ error: error.message }) }],
          isError: true
        };
      }
    });
  }

  // ============ 工具实现 ============

  private async getStockPrice(args: any): Promise<any> {
    const { codes, market = 'SH' } = args;
    
    // 模拟股票数据
    const stockData: Record<string, StockData> = {
      '600519': {
        code: '600519',
        name: '贵州茅台',
        price: 1680.50,
        change: 25.30,
        changePercent: 1.53,
        volume: 3256000,
        amount: 5423000000,
        high: 1695.00,
        low: 1658.20,
        open: 1662.00,
        close: 1680.50,
        timestamp: new Date().toISOString()
      },
      '000858': {
        code: '000858',
        name: '五粮液',
        price: 145.80,
        change: -1.20,
        changePercent: -0.82,
        volume: 18560000,
        amount: 2698000000,
        high: 148.50,
        low: 144.90,
        open: 147.20,
        close: 145.80,
        timestamp: new Date().toISOString()
      },
      '300750': {
        code: '300750',
        name: '宁德时代',
        price: 198.50,
        change: 5.80,
        changePercent: 3.01,
        volume: 45230000,
        amount: 8876000000,
        high: 200.20,
        low: 193.50,
        open: 194.00,
        close: 198.50,
        timestamp: new Date().toISOString()
      }
    };

    const results = codes.map((code: string) => stockData[code] || {
      code,
      name: 'Unknown',
      price: 0,
      error: 'Stock not found'
    });

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          market,
          timestamp: new Date().toISOString(),
          stocks: results
        }, null, 2)
      }]
    };
  }

  private async analyzeStock(args: any): Promise<any> {
    const { code, indicators = ['ma', 'kdj', 'macd'], period = 'daily' } = args;
    
    // 模拟分析结果
    const result: AnalysisResult = {
      symbol: code,
      signal: ['strong_buy', 'buy', 'hold', 'sell', 'strong_sell'][Math.floor(Math.random() * 5)] as any,
      confidence: 0.6 + Math.random() * 0.35,
      indicators: {
        MA5: 1685.20,
        MA10: 1672.50,
        MA20: 1658.80,
        MA60: 1620.30,
        K: 72.5,
        D: 68.3,
        J: 81.2,
        DIF: 15.8,
        DEA: 12.3,
        MACD: 3.5,
        RSI: 65.8,
        BOLL_UPPER: 1720.50,
        BOLL_MIDDLE: 1650.20,
        BOLL_LOWER: 1579.90
      },
      patterns: ['上升三角形', '均线多头排列'],
      recommendation: '技术面显示强势，建议逢低布局'
    };

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          analysis: result,
          period,
          indicators,
          timestamp: new Date().toISOString()
        }, null, 2)
      }]
    };
  }

  private async detectPatterns(args: any): Promise<any> {
    const { code, patterns = [] } = args;
    
    const detectedPatterns: Array<{pattern: string; confidence: number; description: string}> = [];
    
    // 模拟形态检测
    const allPatterns = ['golden_cross', 'death_cross', 'head_shoulders', 'double_bottom', 'cup_handle'];
    const toDetect = patterns.length > 0 ? patterns : allPatterns;
    
    toDetect.forEach((p: string) => {
      if (Math.random() > 0.5) {
        detectedPatterns.push({
          pattern: p,
          confidence: 0.6 + Math.random() * 0.35,
          description: this.getPatternDescription(p)
        });
      }
    });

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          code,
          detectedPatterns,
          totalScanned: toDetect.length,
          detectedCount: detectedPatterns.length
        }, null, 2)
      }]
    };
  }

  private getPatternDescription(pattern: string): string {
    const descriptions: Record<string, string> = {
      golden_cross: '均线金叉，短期均线上穿长期均线，看涨信号',
      death_cross: '均线死叉，短期均线下穿长期均线，看跌信号',
      head_shoulders: '头肩顶形态，顶部反转信号',
      double_top: '双顶形态，颈部线突破后看跌',
      double_bottom: '双底形态，颈部线突破后看涨',
      cup_handle: '杯柄形态，持续上升趋势中继'
    };
    return descriptions[pattern] || '未识别形态';
  }

  private async calculateIndicators(args: any): Promise<any> {
    const { code, indicators, params = {} } = args;
    
    const results: Record<string, number | number[]> = {};
    indicators.forEach((ind: string) => {
      switch (ind) {
        case 'ma':
          results.MA5 = 1685.20;
          results.MA10 = 1672.50;
          results.MA20 = 1658.80;
          results.MA60 = 1620.30;
          break;
        case 'kdj':
          results.K = 72.5;
          results.D = 68.3;
          results.J = 81.2;
          break;
        case 'macd':
          results.DIF = 15.8;
          results.DEA = 12.3;
          results.MACD = 3.5;
          break;
        case 'boll':
          results.upper = 1720.50;
          results.middle = 1650.20;
          results.lower = 1579.90;
          break;
        case 'rsi':
          results.RSI6 = 65.8;
          results.RSI12 = 62.3;
          results.RSI24 = 58.9;
          break;
      }
    });

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          code,
          indicators: results,
          calculatedAt: new Date().toISOString()
        }, null, 2)
      }]
    };
  }

  private async compareStocks(args: any): Promise<any> {
    const { codes, metrics = ['pe', 'pb', 'roe'] } = args;
    
    const comparison: Record<string, any> = {};
    codes.forEach((code: string) => {
      const stockMetrics: Record<string, any> = {};
      metrics.forEach((m: string) => {
        switch (m) {
          case 'pe': stockMetrics.PE = (15 + Math.random() * 30).toFixed(2); break;
          case 'pb': stockMetrics.PB = (1 + Math.random() * 5).toFixed(2); break;
          case 'roe': stockMetrics.ROE = (5 + Math.random() * 25).toFixed(2) + '%'; break;
          case 'growth': stockMetrics.growth = ((-10) + Math.random() * 40).toFixed(2) + '%'; break;
          case 'dividend': stockMetrics.dividend = (1 + Math.random() * 5).toFixed(2) + '%'; break;
        }
      });
      comparison[code] = stockMetrics;
    });

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          metrics,
          comparison,
          timestamp: new Date().toISOString()
        }, null, 2)
      }]
    };
  }

  private async generateSignal(args: any): Promise<any> {
    const { code, strategy = 'momentum', riskLevel = 'medium' } = args;
    
    const signals = [
      { action: 'BUY', quantity: 1000, price: 1680.50, stopLoss: 1650, takeProfit: 1750 },
      { action: 'HOLD', quantity: 0, price: 1680.50, stopLoss: null, takeProfit: null },
      { action: 'SELL', quantity: 500, price: 1680.50, stopLoss: null, takeProfit: null }
    ];
    const signal = signals[Math.floor(Math.random() * 3)];

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          code,
          strategy,
          riskLevel,
          signal: {
            action: signal.action,
            quantity: signal.quantity,
            entryPrice: signal.price,
            stopLoss: signal.stopLoss,
            takeProfit: signal.takeProfit,
            riskRewardRatio: signal.stopLoss && signal.takeProfit 
              ? ((signal.takeProfit - signal.price) / (signal.price - signal.stopLoss)).toFixed(2)
              : null
          },
          generatedAt: new Date().toISOString(),
          confidence: (0.6 + Math.random() * 0.35).toFixed(2)
        }, null, 2)
      }]
    };
  }

  private async screenStocks(args: any): Promise<any> {
    const { conditions = {} } = args;
    
    // 模拟选股结果
    const stocks = [
      { code: '300750', name: '宁德时代', price: 198.50, PE: 28.5, ROE: 18.2, change: 3.01 },
      { code: '688041', name: '寒武纪', price: 125.80, PE: 156.3, ROE: 2.5, change: 5.82 },
      { code: '002460', name: '赣锋锂业', price: 68.90, PE: 18.2, ROE: 12.8, change: -1.25 },
      { code: '300059', name: '东方财富', price: 15.60, PE: 32.1, ROE: 15.6, change: 2.15 }
    ];

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          conditions,
          matchedStocks: stocks,
          total: stocks.length,
          screenedAt: new Date().toISOString()
        }, null, 2)
      }]
    };
  }

  private async getMarketSentiment(args: any): Promise<any> {
    const { market = 'all' } = args;
    
    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          market,
          sentiment: {
            index: 65.8,
            level: '偏多',
            trend: 'rising',
            fearGreedIndex: 68,
            buySellRatio: 1.25,
            marginFinancing: 15800,
            northMoneyFlow: 25.6
          },
          sectors: [
            { name: 'AI/半导体', sentiment: 'bullish', change: 3.2 },
            { name: '新能源', sentiment: 'neutral', change: 0.8 },
            { name: '白酒', sentiment: 'bearish', change: -0.5 },
            { name: '银行', sentiment: 'neutral', change: 0.3 },
            { name: '医药', sentiment: 'bullish', change: 1.5 }
          ]
        }, null, 2)
      }]
    };
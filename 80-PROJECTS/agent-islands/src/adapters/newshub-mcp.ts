/**
 * NewsHub MCP Adapter
 * 将NewsHub服务封装为标准MCP协议接口
 */
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ListResourcesRequestSchema,
  ListToolsRequestSchema,
  ListPromptsRequestSchema,
  ReadResourceRequestSchema
} from '@modelcontextprotocol/sdk/types.js';

interface NewsConfig {
  sources?: string[];
  categories?: string[];
  maxItems?: number;
  sentimentThreshold?: number;
}

interface SentimentResult {
  overall: 'positive' | 'negative' | 'neutral';
  score: number;
  keywords: string[];
}

interface NewsItem {
  id: string;
  title: string;
  content: string;
  url: string;
  source: string;
  publishedAt: string;
  sentiment?: SentimentResult;
  relatedStocks?: string[];
  topics?: string[];
  importance?: number;
}

/**
 * NewsHub MCP Server
 */
class NewsHubMCPServer {
  private server: Server;
  private newsCache: NewsItem[] = [];
  private lastFetch: Date | null = null;

  constructor() {
    this.server = new Server(
      {
        name: 'newshub-mcp',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
          resources: {},
          prompts: {}
        },
      }
    );

    this.setupHandlers();
  }

  private setupHandlers() {
    // 列出可用工具
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          {
            name: 'get_latest_news',
            description: '获取最新财经新闻，支持多源聚合、分类筛选',
            inputSchema: {
              type: 'object',
              properties: {
                sources: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: '新闻源列表: sina, ifeng, eastmoney, caixin, reuters'
                },
                categories: { 
                  type: 'array', 
                  items: { type: 'string' },
                  description: '分类: macro, tech, industry, finance, international'
                },
                maxItems: { 
                  type: 'number', 
                  default: 50,
                  description: '最大返回条数'
                },
                refresh: {
                  type: 'boolean',
                  default: false,
                  description: '是否强制刷新缓存'
                }
              }
            }
          },
          {
            name: 'analyze_sentiment',
            description: '分析新闻情绪，判断市场情绪走向',
            inputSchema: {
              type: 'object',
              properties: {
                newsId: { type: 'string' },
                newsIds: { type: 'array', items: { type: 'string' } },
                market: { 
                  type: 'string', 
                  enum: ['a-share', 'hk', 'us', 'crypto'],
                  default: 'a-share'
                }
              }
            }
          },
          {
            name: 'search_news',
            description: '搜索特定主题的新闻',
            inputSchema: {
              type: 'object',
              properties: {
                query: { type: 'string', description: '搜索关键词' },
                dateRange: { 
                  type: 'string',
                  enum: ['today', 'week', 'month', 'all'],
                  default: 'week'
                },
                stocks: { 
                  type: 'array',
                  items: { type: 'string' },
                  description: '关联股票代码'
                }
              }
            }
          },
          {
            name: 'get_trending_topics',
            description: '获取当前热门话题',
            inputSchema: {
              type: 'object',
              properties: {
                limit: { type: 'number', default: 10 },
                timeWindow: { 
                  type: 'string',
                  enum: ['hour', 'day', 'week'],
                  default: 'day'
                }
              }
            }
          },
          {
            name: 'get_stock_news',
            description: '获取特定股票的新闻',
            inputSchema: {
              type: 'object',
              properties: {
                stockCode: { type: 'string', description: '股票代码，如 600519' },
                stockName: { type: 'string', description: '股票名称，如 贵州茅台' },
                days: { type: 'number', default: 7, description: '查询天数' }
              }
            }
          },
          {
            name: 'generate_news_digest',
            description: '生成新闻摘要报告',
            inputSchema: {
              type: 'object',
              properties: {
                topic: { type: 'string', description: '主题' },
                style: { 
                  type: 'string',
                  enum: ['brief', 'detailed', 'executive'],
                  default: 'brief'
                },
                includeSentiment: { type: 'boolean', default: true }
              }
            }
          }
        ]
      };
    });

    // 处理工具调用
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'get_latest_news':
            return await this.getLatestNews(args as NewsConfig);
          
          case 'analyze_sentiment':
            return await this.analyzeSentiment(args);
          
          case 'search_news':
            return await this.searchNews(args);
          
          case 'get_trending_topics':
            return await this.getTrendingTopics(args);
          
          case 'get_stock_news':
            return await this.getStockNews(args);
          
          case 'generate_news_digest':
            return await this.generateDigest(args);
          
          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error: any) {
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({ error: error.message })
            }
          ],
          isError: true
        };
      }
    });

    // 列出资源
    this.server.setRequestHandler(ListResourcesRequestSchema, async () => {
      return {
        resources: [
          {
            uri: 'news://latest',
            name: 'Latest News',
            description: '最新财经新闻列表',
            mimeType: 'application/json'
          },
          {
            uri: 'news://trending',
            name: 'Trending Topics',
            description: '热门话题',
            mimeType: 'application/json'
          },
          {
            uri: 'news://sentiment',
            name: 'Market Sentiment',
            description: '市场情绪指数',
            mimeType: 'application/json'
          }
        ]
      };
    });

    // 读取资源
    this.server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
      const uri = request.params.uri;
      
      if (uri === 'news://latest') {
        return {
          contents: [{
            uri,
            mimeType: 'application/json',
            text: JSON.stringify({ items: this.newsCache })
          }]
        };
      }
      
      if (uri === 'news://trending') {
        return {
          contents: [{
            uri,
            mimeType: 'application/json',
            text: JSON.stringify({ topics: this.getTrendingTopics({}) })
          }]
        };
      }

      return { contents: [] };
    });

    // 列出提示词
    this.server.setRequestHandler(ListPromptsRequestSchema, async () => {
      return {
        prompts: [
          {
            name: 'market_analysis',
            description: '市场分析助手',
            arguments: [
              { name: 'focus', description: '分析重点: sentiment, trends, opportunities, risks' }
            ]
          },
          {
            name: 'news_summary',
            description: '新闻摘要生成',
            arguments: [
              { name: 'topic', description: '新闻主题' },
              { name: 'depth', description: '深度: brief, moderate, comprehensive' }
            ]
          }
        ]
      };
    });
  }

  // ============ 工具实现 ============

  private async getLatestNews(config: NewsConfig): Promise<any> {
    const { sources = ['sina', 'ifeng'], categories = [], maxItems = 50, refresh = false } = config;
    
    // 模拟新闻数据（实际应调用NewsHub服务）
    const mockNews: NewsItem[] = [
      {
        id: `news_${Date.now()}_1`,
        title: 'A股三大指数集体上涨 科技股表现强劲',
        content: '今日A股市场表现活跃，三大指数集体收涨。科技股成为今日亮点，半导体、人工智能板块涨幅居前...',
        url: 'https://finance.sina.com.cn/stock/marketresearch/',
        source: 'sina',
        publishedAt: new Date().toISOString(),
        sentiment: { overall: 'positive', score: 0.75, keywords: ['上涨', '强劲', '科技'] },
        relatedStocks: ['600519', '000858', '300750'],
        topics: ['A股', '科技股', '半导体'],
        importance: 8
      },
      {
        id: `news_${Date.now()}_2`,
        title: '央行宣布降准 释放长期资金约5000亿元',
        content: '中国人民银行宣布将于下周下调存款准备金率0.25个百分点，预计释放长期资金约5000亿元...',
        url: 'https://www.ifeng.com/finance/macro/',
        source: 'ifeng',
        publishedAt: new Date(Date.now() - 3600000).toISOString(),
        sentiment: { overall: 'positive', score: 0.8, keywords: ['降准', '宽松', '流动性'] },
        topics: ['货币政策', '降准', '流动性'],
        importance: 9
      },
      {
        id: `news_${Date.now()}_3`,
        title: '特斯拉4680电池量产遇阻 股价盘后跌超3%',
        content: '特斯拉在德州工厂的4680电池量产遇到技术挑战，产能提升不及预期，股价在盘后交易中下跌...',
        url: 'https://www.reuters.com/technology/',
        source: 'reuters',
        publishedAt: new Date(Date.now() - 7200000).toISOString(),
        sentiment: { overall: 'negative', score: 0.35, keywords: ['量产', '遇阻', '下跌'] },
        relatedStocks: ['TSLA'],
        topics: ['特斯拉', '电池', '新能源汽车'],
        importance: 7
      },
      {
        id: `news_${Date.now()}_4`,
        title: 'AI芯片需求爆发 英伟达Q4财报超预期',
        content: '英伟达今日公布第四季度财报，数据中心业务营收同比翻倍，AI芯片需求持续旺盛...',
        url: 'https://finance.eastmoney.com/a/2024q4.html',
        source: 'eastmoney',
        publishedAt: new Date(Date.now() - 10800000).toISOString(),
        sentiment: { overall: 'positive', score: 0.9, keywords: ['超预期', 'AI', '增长'] },
        relatedStocks: ['NVDA', 'AMD'],
        topics: ['AI', '芯片', '英伟达', '财报'],
        importance: 9
      },
      {
        id: `news_${Date.now()}_5`,
        title: '碳酸锂价格持续下跌 锂矿企业承压',
        content: '近期碳酸锂现货价格持续走低，已跌破15万元/吨关口，锂矿开采企业盈利空间受到明显挤压...',
        url: 'https://www.caixinglobal.com/industry/',
        source: 'caixin',
        publishedAt: new Date(Date.now() - 14400000).toISOString(),
        sentiment: { overall: 'negative', score: 0.4, keywords: ['下跌', '承压', '锂矿'] },
        relatedStocks: ['002460', '002466'],
        topics: ['锂矿', '碳酸锂', '新能源材料'],
        importance: 6
      }
    ];

    this.newsCache = mockNews;
    this.lastFetch = new Date();

    // 过滤
    let filtered = mockNews;
    if (sources.length > 0) {
      filtered = filtered.filter(n => sources.includes(n.source));
    }
    if (categories.length > 0) {
      filtered = filtered.filter(n => 
        n.topics?.some(t => categories.includes(t))
      );
    }

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          success: true,
          count: Math.min(filtered.length, maxItems),
          items: filtered.slice(0, maxItems),
          fetchedAt: this.lastFetch.toISOString(),
          sources: sources,
          categories: categories
        }, null, 2)
      }]
    };
  }

  private async analyzeSentiment(args: any): Promise<any> {
    const { newsId, newsIds, market = 'a-share' } = args;
    
    // 模拟情绪分析
    const sentiments = this.newsCache.map(news => ({
      newsId: news.id,
      title: news.title,
      sentiment: news.sentiment || {
        overall: ['positive', 'negative', 'neutral'][Math.floor(Math.random() * 3)] as any,
        score: 0.3 + Math.random() * 0.4,
        keywords: news.topics || []
      }
    }));

    const avgScore = sentiments.reduce((sum, s) => sum + s.sentiment.score, 0) / sentiments.length;
    const overallSentiment = avgScore > 0.6 ? 'bullish' : avgScore < 0.4 ? 'bearish' : 'neutral';

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          market,
          overall: overallSentiment,
          avgScore,
          newsAnalyzed: sentiments.length,
          sentiments,
          recommendation: overallSentiment === 'bullish' ? '考虑加仓' : overallSentiment === 'bearish' ? '建议观望' : '中性策略'
        }, null, 2)
      }]
    };
  }

  private async searchNews(args: any): Promise<any> {
    const { query, dateRange = 'week', stocks = [] } = args;
    
    const results = this.newsCache.filter(news => {
      const matchQuery = news.title.includes(query) || news.content.includes(query);
      const matchStock = stocks.length === 0 || 
        news.relatedStocks?.some(s => stocks.includes(s));
      return matchQuery && matchStock;
    });

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          query,
          dateRange,
          stocks,
          results: results,
          total: results.length
        }, null, 2)
      }]
    };
  }

  private async getTrendingTopics(args: any): Promise<any> {
    const { limit = 10, timeWindow = 'day' } = args;

    // 模拟热门话题
    const topics = [
      { topic: 'AI芯片',热度: 98, relatedStocks: ['NVDA', 'AMD', '寒武纪'], trend: 'rising' },
      { topic: '新能源汽车',热度: 95, relatedStocks: ['比亚迪', '特斯拉', '宁德时代'], trend: 'rising' },
      { topic: '降准',热度: 92, relatedStocks: ['银行板块'], trend: 'stable' },
      { topic: '半导体',热度: 90, relatedStocks: ['中芯国际', '华虹半导体'], trend: 'rising' },
      { topic: '创新药',热度: 85, relatedStocks: ['恒瑞医药', '百济神州'], trend: 'rising' },
      { topic: '白酒',热度: 80, relatedStocks: ['贵州茅台', '五粮液'], trend: 'stable' },
      { topic: '房地产',热度: 75, relatedStocks: ['万科A', '保利发展'], trend: 'falling' },
      { topic: '锂矿',热度: 70, relatedStocks: ['赣锋锂业', '天齐锂业'], trend: 'falling' }
    ];

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          timeWindow,
          topics: topics.slice(0, limit),
          updatedAt: new Date().toISOString()
        }, null, 2)
      }]
    };
  }

  private async getStockNews(args: any): Promise<any> {
    const { stockCode, stockName, days = 7 } = args;
    
    const stockNews = this.newsCache.filter(news =>
      news.relatedStocks?.some(s => 
        s === stockCode || 
        (stockName && news.title.includes(stockName))
      )
    );

    return {
      content: [{
        type: 'text',
        text: JSON.stringify({
          stockCode,
          stockName,
          days,
          news: stockNews,
          count: stockNews.length
        }, null, 2)
      }]
    };
  }

  private async generateDigest(args: any): Promise<any> {
    const { topic, style = 'brief', includeSentiment = true } = args;
    
    const relevantNews = topic 
      ? this.newsCache.filter(n => n.title.includes(topic) || n.topics?.includes(topic))
      : this.newsCache;

    let digest = '';
    if (style === 'brief') {
      digest = `【${topic || '市场'}简报】\n`;
      relevantNews.slice(0, 3).forEach((n, i) => {
        digest += `${i + 1}. ${n.title} (${n.source})\n`;
      });
    } else if (style === 'detailed') {
      digest = `【${topic || '市场'}详报】\n\n`;
      relevantNews.forEach((n, i) => {
        digest += `## ${i + 1}. ${n.title}\n`;
        digest += `来源: ${n.source} | 时间: ${n.publishedAt}\n`;
        digest += `${n.content}\n\n`;
      });
    } else {
      digest = `【高管简报】\n`;
      digest += `数据截止: ${new Date().toLocaleString()}\n\n`;
      digest += `## 关键指标\n`;
      digest += `- 新闻总数: ${relevantNews.length}\n`;
      
      if (includeSentiment) {
        const positive = relevantNews.filter(n => n.sentiment?.overall === 'positive').length;
        const negative = relevantNews.filter(n => n.sentiment?.overall === 'negative').length;
        digest += `- 正面新闻: ${positive} | 负面新闻: ${negative}\n`;
      }
      
      digest += `\n## 重点关注\n`;
      relevantNews.filter(n => (n.importance || 0) >= 8).forEach((n, i) => {
        digest += `${i + 1}. ${n.title} [重要性: ${n.importance}]\n`;
      });
    }
    
    return {
      content: [{
        type: 'text',
        text: digest
      }]
    };
  }
}
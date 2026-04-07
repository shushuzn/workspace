/**
 * NewsHub Adapter - 财经新闻 MCP 工具集
 * 来源：agent-islands/src/adapters/newshub-mcp.ts
 * 已融合进 ai-roundtable
 */

export interface NewsConfig {
  sources?: string[];
  categories?: string[];
  maxItems?: number;
  refresh?: boolean;
}

export interface SentimentResult {
  overall: 'positive' | 'negative' | 'neutral';
  score: number;
  keywords: string[];
}

export interface NewsItem {
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

let newsCache: NewsItem[] = [];
let lastFetch: Date | null = null;

// 模拟新闻数据
function fetchMockNews(): NewsItem[] {
  return [
    {
      id: `news_${Date.now()}_1`,
      title: 'A股三大指数集体上涨 科技股表现强劲',
      content: '今日A股市场表现活跃，三大指数集体收涨。科技股成为今日亮点...',
      url: 'https://finance.sina.com.cn/stock/',
      source: 'sina',
      publishedAt: new Date().toISOString(),
      sentiment: {
        overall: 'positive',
        score: 0.75,
        keywords: ['上涨', '强劲', '科技'],
      },
      relatedStocks: ['600519', '000858', '300750'],
      topics: ['A股', '科技股', '半导体'],
      importance: 8,
    },
    {
      id: `news_${Date.now()}_2`,
      title: '央行宣布降准 释放长期资金约5000亿元',
      content: '中国人民银行宣布将于下周下调存款准备金率0.25个百分点...',
      url: 'https://www.ifeng.com/finance/macro/',
      source: 'ifeng',
      publishedAt: new Date(Date.now() - 3600000).toISOString(),
      sentiment: {
        overall: 'positive',
        score: 0.8,
        keywords: ['降准', '宽松', '流动性'],
      },
      topics: ['货币政策', '降准', '流动性'],
      importance: 9,
    },
    {
      id: `news_${Date.now()}_3`,
      title: 'AI芯片需求爆发 英伟达Q4财报超预期',
      content: '英伟达今日公布第四季度财报，数据中心业务营收同比翻倍...',
      url: 'https://finance.eastmoney.com/',
      source: 'eastmoney',
      publishedAt: new Date(Date.now() - 7200000).toISOString(),
      sentiment: {
        overall: 'positive',
        score: 0.9,
        keywords: ['超预期', 'AI', '增长'],
      },
      relatedStocks: ['NVDA', 'AMD'],
      topics: ['AI', '芯片', '英伟达', '财报'],
      importance: 9,
    },
    {
      id: `news_${Date.now()}_4`,
      title: '碳酸锂价格持续下跌 锂矿企业承压',
      content: '近期碳酸锂现货价格持续走低，已跌破15万元/吨关口...',
      url: 'https://www.caixinglobal.com/industry/',
      source: 'caixin',
      publishedAt: new Date(Date.now() - 14400000).toISOString(),
      sentiment: {
        overall: 'negative',
        score: 0.4,
        keywords: ['下跌', '承压', '锂矿'],
      },
      relatedStocks: ['002460', '002466'],
      topics: ['锂矿', '碳酸锂', '新能源材料'],
      importance: 6,
    },
  ];
}

export function getLatestNews(config: NewsConfig = {}): {
  items: NewsItem[];
  fetchedAt: string;
} {
  const { sources = [], categories = [], maxItems = 50 } = config;

  newsCache = fetchMockNews();
  lastFetch = new Date();

  let filtered = newsCache;
  if (sources.length > 0) {
    filtered = filtered.filter(n => sources.includes(n.source));
  }
  if (categories.length > 0) {
    filtered = filtered.filter(n =>
      n.topics?.some(t => categories.includes(t))
    );
  }

  return {
    items: filtered.slice(0, maxItems),
    fetchedAt: lastFetch.toISOString(),
  };
}

export function analyzeSentiment(newsIds?: string[], market = 'a-share'): any {
  const sentiments = newsCache.map(news => ({
    newsId: news.id,
    title: news.title,
    sentiment: news.sentiment || {
      overall: 'neutral',
      score: 0.5,
      keywords: news.topics || [],
    },
  }));

  const avgScore =
    sentiments.reduce((sum, s) => sum + s.sentiment.score, 0) /
    sentiments.length;
  const overall =
    avgScore > 0.6 ? 'bullish' : avgScore < 0.4 ? 'bearish' : 'neutral';

  return {
    market,
    overall,
    avgScore,
    newsAnalyzed: sentiments.length,
    sentiments,
  };
}

export function searchNews(query: string, stocks: string[] = []): NewsItem[] {
  return newsCache.filter(news => {
    const matchQuery =
      news.title.includes(query) || news.content.includes(query);
    const matchStock =
      stocks.length === 0 || news.relatedStocks?.some(s => stocks.includes(s));
    return matchQuery && matchStock;
  });
}

export function getTrendingTopics(limit = 10): any[] {
  return [
    {
      topic: 'AI芯片',
      热度: 98,
      relatedStocks: ['NVDA', 'AMD'],
      trend: 'rising',
    },
    {
      topic: '新能源汽车',
      热度: 95,
      relatedStocks: ['比亚迪', '特斯拉'],
      trend: 'rising',
    },
    { topic: '降准', 热度: 92, relatedStocks: ['银行板块'], trend: 'stable' },
    { topic: '半导体', 热度: 90, relatedStocks: ['中芯国际'], trend: 'rising' },
    { topic: '锂矿', 热度: 70, relatedStocks: ['赣锋锂业'], trend: 'falling' },
  ].slice(0, limit);
}

export function getStockNews(
  stockCode: string,
  stockName?: string,
  days = 7
): NewsItem[] {
  return newsCache.filter(news =>
    news.relatedStocks?.some(
      s => s === stockCode || (stockName && news.title.includes(stockName))
    )
  );
}

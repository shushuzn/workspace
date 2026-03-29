"""
News Analyzer - 新闻分析模块

使用 AI 模型分析新闻的重要性、分类、情感
"""

import asyncio
from typing import Dict, Any, Optional
from loguru import logger


class NewsAnalyzer:
    """新闻分析器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化分析器
        
        Args:
            config: 分析配置
        """
        self.config = config
        self.model = config.get("model", "ollama/llama3")
        self.api_key = config.get("api_key", "")
        self.ollama_host = config.get("ollama_host", "http://localhost:11434")
        
        logger.info(f"NewsAnalyzer initialized with model: {self.model}")
    
    async def analyze(self, news_item: dict) -> Dict[str, Any]:
        """
        分析新闻
        
        Args:
            news_item: 新闻项，包含 title, content, source
        
        Returns:
            分析结果：importance, category, sentiment, keywords, summary
        """
        title = news_item.get("title", "")
        content = news_item.get("content", "")
        
        # 构建分析 prompt
        prompt = self._build_analysis_prompt(title, content)
        
        # 调用 AI 模型
        try:
            if self.model.startswith("ollama"):
                result = await self._analyze_with_ollama(prompt)
            elif self.model.startswith("openai"):
                result = await self._analyze_with_openai(prompt)
            else:
                # 降级：使用规则分析
                result = await self._analyze_with_rules(title, content)
            
            logger.debug(f"Analysis result: {result}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {e}")
            # 降级：使用规则分析
            return await self._analyze_with_rules(title, content)
    
    def _build_analysis_prompt(self, title: str, content: str) -> str:
        """构建分析 prompt"""
        return f"""
分析以下新闻，返回 JSON 格式结果：

标题：{title}
内容：{content[:2000]}

请分析：
1. importance: 重要性评分 (0-1 之间的小数)
2. category: 分类 (tech/finance/market/policy/company/product/other)
3. sentiment: 情感 (positive/neutral/negative)
4. keywords: 关键词列表 (最多 5 个)
5. summary: 一句话摘要 (50 字以内)

只返回 JSON，不要其他内容。格式：
{{
    "importance": 0.8,
    "category": "tech",
    "sentiment": "positive",
    "keywords": ["关键词 1", "关键词 2"],
    "summary": "摘要"
}}
"""
    
    async def _analyze_with_ollama(self, prompt: str) -> Dict[str, Any]:
        """使用 Ollama 分析"""
        import aiohttp
        
        model_name = self.model.replace("ollama/", "")
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.ollama_host}/api/generate",
                json={
                    "model": model_name,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data.get("response", "")
                    return self._parse_analysis_result(result)
                else:
                    raise Exception(f"Ollama API error: {response.status}")
    
    async def _analyze_with_openai(self, prompt: str) -> Dict[str, Any]:
        """使用 OpenAI 分析"""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                "https://api.openai.com/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a news analyst. Return only JSON."},
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.3,
                    "response_format": {"type": "json_object"}
                }
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    result = data["choices"][0]["message"]["content"]
                    return self._parse_analysis_result(result)
                else:
                    raise Exception(f"OpenAI API error: {response.status}")
    
    async def _analyze_with_rules(self, title: str, content: str) -> Dict[str, Any]:
        """使用规则分析（降级方案）"""
        text = (title + " " + content).lower()
        
        # 关键词分类
        category_keywords = {
            "tech": ["ai", "llm", "模型", "技术", "科技", "github", "开源", "软件"],
            "finance": ["金融", "银行", "投资", "股票", "基金", "利率"],
            "market": ["市场", "行情", "交易", "价格", "涨跌"],
            "policy": ["政策", "监管", "法规", "政府", "部门"],
            "company": ["公司", "企业", "融资", "并购", "上市"],
            "product": ["产品", "发布", "上线", "版本", "功能"]
        }
        
        # 情感关键词
        positive_words = ["增长", "突破", "成功", "利好", "上涨", "创新", "领先"]
        negative_words = ["下跌", "风险", "警告", "问题", "失败", "亏损", "监管"]
        
        # 计算分类
        category_scores = {}
        for cat, keywords in category_keywords.items():
            score = sum(1 for kw in keywords if kw in text)
            category_scores[cat] = score
        
        category = max(category_scores, key=category_scores.get) if any(category_scores.values()) else "other"
        
        # 计算情感
        pos_count = sum(1 for w in positive_words if w in text)
        neg_count = sum(1 for w in negative_words if w in text)
        
        if pos_count > neg_count * 1.5:
            sentiment = "positive"
        elif neg_count > pos_count * 1.5:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        # 计算重要性（基于关键词密度和来源）
        importance = min(1.0, (pos_count + neg_count) / 10 + 0.3)
        
        # 提取关键词（简单实现）
        keywords = []
        for cat, kws in category_keywords.items():
            for kw in kws:
                if kw in text and kw not in keywords:
                    keywords.append(kw)
                    if len(keywords) >= 5:
                        break
            if len(keywords) >= 5:
                break
        
        return {
            "importance": importance,
            "category": category,
            "sentiment": sentiment,
            "keywords": keywords[:5],
            "summary": title[:50]
        }
    
    def _parse_analysis_result(self, result: str) -> Dict[str, Any]:
        """解析分析结果"""
        import json
        import re
        
        # 提取 JSON 部分
        json_match = re.search(r'\{.*\}', result, re.DOTALL)
        if json_match:
            result = json_match.group()
        
        try:
            data = json.loads(result)
            return {
                "importance": float(data.get("importance", 0.5)),
                "category": str(data.get("category", "other")),
                "sentiment": str(data.get("sentiment", "neutral")),
                "keywords": list(data.get("keywords", [])),
                "summary": str(data.get("summary", ""))
            }
        except Exception as e:
            logger.error(f"Failed to parse analysis result: {e}")
            return {
                "importance": 0.5,
                "category": "other",
                "sentiment": "neutral",
                "keywords": [],
                "summary": ""
            }

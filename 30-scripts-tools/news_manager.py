# -*- coding: utf-8 -*-
"""News Manager v3.0 - 统一新闻推送"""

import sys, json, ssl, re, urllib.request, subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Tuple


# 颜色支持 (Windows兼容)
class Colors:
    RED = "\033[91m" if sys.platform != "win32" else ""
    GREEN = "\033[92m" if sys.platform != "win32" else ""
    YELLOW = "\033[93m" if sys.platform != "win32" else ""
    BLUE = "\033[94m" if sys.platform != "win32" else ""
    BOLD = "\033[1m" if sys.platform != "win32" else ""
    DIM = "\033[2m" if sys.platform != "win32" else ""
    RESET = "\033[0m" if sys.platform != "win32" else ""

    @staticmethod
    def pos():
        return Colors.GREEN

    @staticmethod
    def neg():
        return Colors.RED

    @staticmethod
    def neu():
        return Colors.DIM

    @staticmethod
    def risk_high():
        return Colors.RED

    @staticmethod
    def risk_low():
        return Colors.GREEN

    @staticmethod
    def header():
        return Colors.BOLD + Colors.BLUE

    @staticmethod
    def reset():
        return Colors.RESET


def c(color, text):
    """带颜色输出"""
    return f"{color}{text}{Colors.RESET}"


def cp(text):
    """利好(绿)"""
    return f"{Colors.pos()}{text}{Colors.RESET}"


def cn(text):
    """利空(红)"""
    return f"{Colors.neg()}{text}{Colors.RESET}"


def cne(text):
    """中性(灰)"""
    return f"{Colors.neu()}{text}{Colors.RESET}"


CONFIG = {
    "qq": {
        "enabled": True,
        "base_url": "http://127.0.0.1:3000",
        "token": "",
        "group_id": "597818978",
    },
    "feishu": {"enabled": True},
    "news": {
        "sources": [
            {
                "name": "sina_finance",
                "url": "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2517",
                "type": "json",
                "category": "新浪财",
            },
            {
                "name": "sina_stock",
                "url": "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2515",
                "type": "json",
                "category": "新浪股",
            },
            {
                "name": "sina_business",
                "url": "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2518",
                "type": "json",
                "category": "新浪产",
            },
            {
                "name": "sina_hkstock",
                "url": "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2513",
                "type": "json",
                "category": "新浪港",
            },
            {
                "name": "sina_usstock",
                "url": "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2510",
                "type": "json",
                "category": "新浪美",
            },
            {
                "name": "sina_tech",
                "url": "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516",
                "type": "json",
                "category": "新浪科",
            },
            {
                "name": "sina_macro",
                "url": "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2519",
                "type": "json",
                "category": "新浪宏",
            },
            {
                "name": "eeo",
                "url": "https://www.eeo.com.cn/rss.xml",
                "type": "rss",
                "category": "经观",
            },
            {
                "name": "bloomberg",
                "url": "https://feeds.bloomberg.com/markets/news.rss",
                "type": "rss",
                "category": "彭博",
            },
            {
                "name": "cnbc",
                "url": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
                "type": "rss",
                "category": "CNBC",
            },
            {
                "name": "marketwatch",
                "url": "https://www.marketwatch.com/rss/topstories",
                "type": "rss",
                "category": "MW",
            },
            {
                "name": "yahoo_finance",
                "url": "https://finance.yahoo.com/news/rssindex",
                "type": "rss",
                "category": "Yahoo",
            },
            {
                "name": "investing",
                "url": "https://www.investing.com/rss/news.rss",
                "type": "rss",
                "category": "Inv",
            },
            {
                "name": "ft_chinese",
                "url": "https://www.ftchinese.com/rss/feed",
                "type": "rss",
                "category": "FT",
            },
            {
                "name": "bbc_biz",
                "url": "http://feeds.bbci.co.uk/news/business/rss.xml",
                "type": "rss",
                "category": "BBC",
            },
            {
                "name": "guardian_biz",
                "url": "https://www.theguardian.com/business/rss",
                "type": "rss",
                "category": "卫报",
            },
        ],
        "max_per_fetch": 2,
    },
}
BASE_DIR = Path(r"D:\OpenClaw\workspace\30-scripts-tools")
DATA_FILE = BASE_DIR / "news_manager_data.json"

# 增强情绪关键词
POSITIVE = [
    "涨停",
    "大涨",
    "飙升",
    "创新高",
    "突破",
    "利好",
    "增持",
    "回购",
    "分红",
    "业绩预增",
    "盈利",
    "增长",
    "上升",
    "上涨",
    "反弹",
    "回暖",
    "复苏",
    "景气",
    "超预期",
    "强劲",
    "领涨",
    "净流入",
    "买入",
    "推荐",
    "看好",
    "上调",
    "降息",
    "降准",
    "宽松",
    "政策支持",
    "补贴",
    "订单",
    "签约",
    "合作",
    "中标",
    "扩产",
    "投产",
    "发布",
    "推出",
    "升级",
    "转型",
    "创新",
]
NEGATIVE = [
    "跌停",
    "大跌",
    "暴跌",
    "崩盘",
    "创新低",
    "跌破",
    "利空",
    "减持",
    "套现",
    "业绩预亏",
    "亏损",
    "下降",
    "下滑",
    "下跌",
    "跳水",
    "重挫",
    "低迷",
    "萎缩",
    "衰退",
    "不及预期",
    "疲软",
    "领跌",
    "净流出",
    "卖出",
    "看空",
    "下调",
    "加息",
    "紧缩",
    "监管",
    "处罚",
    "罚款",
    "退市",
    "风险",
    "暴雷",
    "造假",
    "违规",
    "调查",
    "起诉",
    "制裁",
    "禁令",
    "断供",
    "裁员",
    "破产",
    "违约",
    "挤兑",
    "蒸发",
    "失血",
    "告急",
]

# 增强板块映射
SECTORS = {
    "科技": [
        "AI",
        "芯片",
        "半导体",
        "华为",
        "腾讯",
        "阿里",
        "字节",
        "人工智能",
        "算力",
        "机器人",
        "软件",
        "互联网",
        "云计算",
        "大数据",
        "5G",
        "6G",
        "苹果",
        "微软",
        "英伟达",
        "谷歌",
        "Meta",
        "OpenAI",
        "自动驾驶",
        "智能驾驶",
    ],
    "新能源": [
        "光伏",
        "锂电",
        "储能",
        "新能源",
        "电动车",
        "特斯拉",
        "比亚迪",
        "宁德",
        "风电",
        "氢能",
        "核能",
        "电网",
        "充电桩",
        "动力电池",
    ],
    "金融": [
        "银行",
        "保险",
        "券商",
        "基金",
        "信托",
        "支付",
        "证券",
        "期货",
        "外汇",
        "央行",
        "美联储",
        "降息",
        "加息",
        "货币政策",
        "流动性",
    ],
    "地产": [
        "房地产",
        "地产",
        "楼市",
        "房价",
        "恒大",
        "万科",
        "碧桂园",
        "融创",
        "土地",
        "限购",
        "限贷",
        "调控",
        "房贷",
        "物业",
    ],
    "医药": [
        "医药",
        "医疗",
        "生物",
        "疫苗",
        "创新药",
        "医保",
        "中药",
        "医疗器械",
        "医院",
        "诊疗",
        "检测",
        "疫苗",
        "特效药",
    ],
    "消费": [
        "消费",
        "零售",
        "白酒",
        "食品",
        "饮料",
        "家电",
        "汽车",
        "旅游",
        "酒店",
        "餐饮",
        "免税",
        "电商",
        "直播",
        "美容",
    ],
    "周期": [
        "煤炭",
        "钢铁",
        "有色",
        "化工",
        "石油",
        "天然气",
        "航运",
        "大宗商品",
        "原油",
        "铜",
        "铝",
        "煤炭",
        "稀土",
        "化工",
    ],
    "军工": [
        "军工",
        "国防",
        "航天",
        "航空",
        "船舶",
        "导弹",
        "雷达",
        "无人机",
        "军演",
        "军费",
    ],
    "传媒": [
        "影视",
        "游戏",
        "传媒",
        "广告",
        "直播",
        "短视频",
        "元宇宙",
        "NFT",
        "虚拟现实",
        "内容",
        "IP",
    ],
    "宏观": [
        "GDP",
        "CPI",
        "PPI",
        "PMI",
        "就业",
        "消费",
        "投资",
        "出口",
        "进口",
        "贸易",
        "关税",
        "经济",
        "政策",
        "改革",
    ],
}

# 导入智能分析器 (LLM 或关键词回退)
try:
    from news_llm_analyzer import analyze as smart_analyze, is_llm_available

    HAS_LLM = True
except:
    HAS_LLM = False

    def smart_analyze(title):
        return {
            "sentiment": "中性",
            "intensity": 3,
            "sector": "通用",
            "keywords": [],
            "companies": [],
            "urgency": "中",
            "summary": title[:50],
            "method": "keyword",
        }

    def is_llm_available():
        return False


# 来源映射
SOURCE_MAP = {
    "sina_finance": "新浪财",
    "sina_stock": "新浪股",
    "sina_business": "新浪产",
    "sina_hkstock": "新浪港",
    "sina_usstock": "新浪美",
    "sina_tech": "新浪科",
    "sina_macro": "新浪宏",
    "eeo": "经观",
    "bloomberg": "彭博",
    "cnbc": "CNBC",
    "marketwatch": "MW",
    "yahoo_finance": "Yahoo",
    "investing": "Inv",
    "ft_chinese": "FT",
    "bbc_biz": "BBC",
    "guardian_biz": "卫报",
}

# 公司映射
COMPANIES = {
    "华为": ["华为", "任正非", "孟晚舟"],
    "阿里": ["阿里", "马云", "蔡崇信", "阿里巴巴", "淘宝", "天猫", "支付宝"],
    "腾讯": ["腾讯", "马化腾", "微信", "QQ", "王者荣耀"],
    "字节": ["字节", "抖音", "TikTok", "张一鸣", "今日头条"],
    "百度": ["百度", "李彦宏", "文心一言"],
    "小米": ["小米", "雷军", "SU7"],
    "比亚迪": ["比亚迪", "王传福", "秦PLUS", "汉EV"],
    "特斯拉": ["特斯拉", "马斯克", "Model"],
    "茅台": ["茅台", "贵州茅台", "五粮液", "泸州老窖"],
    "宁德": ["宁德", "宁德时代", "曾毓群"],
    "苹果": ["苹果", "iPhone", "库克"],
    "微软": ["微软", "比尔盖茨", "纳德拉"],
    "OpenAI": ["OpenAI", "ChatGPT", "Sam Altman", "GPT"],
    "英伟达": ["英伟达", "黄仁勋", "NVIDIA", "GPU", "H100"],
    "谷歌": ["谷歌", "Google", "Alphabet", "皮查伊"],
    "亚马逊": ["亚马逊", "AWS", "贝索斯", "贝佐斯"],
    "Meta": ["Meta", "Facebook", "扎克伯格", "Instagram"],
}

# 紧急程度关键词
URGENT = [
    "突发",
    "紧急",
    "刚刚",
    "重磅",
    "警告",
    "风险提示",
    "利空",
    "暴跌",
    "涨停",
    "制裁",
    "断供",
    "违约",
    "破产",
    "起诉",
]
IMPORTANT = [
    "政策",
    "监管",
    "降息",
    "加息",
    "业绩",
    "订单",
    "签约",
    "合作",
    "突破",
    "创新",
    "发布",
    "推出",
]
NORMAL = ["分析", "解读", "观点", "评论", "观察", "预计", "预测"]


def analyze(title):
    """增强分析：情绪、板块、关键词、公司、紧急度、趋势"""
    # 1. 情绪分析
    pos_score = sum(1 for k in POSITIVE if k in title)
    neg_score = sum(1 for k in NEGATIVE if k in title)
    if pos_score > neg_score:
        sentiment = "利好"
        intensity = min(pos_score, 5)  # 1-5分
    elif neg_score > pos_score:
        sentiment = "利空"
        intensity = min(neg_score, 5)
    else:
        sentiment = "中性"
        intensity = 0

    # 2. 板块映射
    sector_scores = {}
    for sec, kws in SECTORS.items():
        score = sum(1 for k in kws if k in title)
        if score > 0:
            sector_scores[sec] = score
    sector = max(sector_scores, key=sector_scores.get) if sector_scores else "通用"

    # 3. 关键词提取
    keywords = []
    for sec, kws in SECTORS.items():
        for kw in kws:
            if kw in title and kw not in keywords:
                keywords.append(kw)
                if len(keywords) >= 5:
                    break
        if len(keywords) >= 5:
            break

    # 4. 公司识别
    companies = []
    for name, aliases in COMPANIES.items():
        for alias in aliases:
            if alias in title:
                companies.append(name)
                break
        if len(companies) >= 3:
            break

    # 5. 股票代码提取
    codes = re.findall(r"\b[0-9]{6}\b", title)
    codes.extend(re.findall(r"\b[A-Z]{2,5}\b", title))
    codes = list(dict.fromkeys(codes))[:2]

    # 6. 紧急程度
    if any(k in title for k in URGENT):
        urgency = "【突发】"
    elif any(k in title for k in IMPORTANT):
        urgency = "【重要】"
    else:
        urgency = ""

    # 7. 趋势判断
    trend = ""
    if any(k in title for k in ["大涨", "涨停", "暴涨", "飙升", "创新高", "突破"]):
        trend = "上涨"
    elif any(k in title for k in ["大跌", "跌停", "暴跌", "崩盘", "创新低"]):
        trend = "下跌"
    elif any(k in title for k in ["震荡", "波动", "整理"]):
        trend = "震荡"

    return {
        "sentiment": sentiment,
        "intensity": intensity,
        "sector": sector,
        "keywords": keywords[:5],
        "companies": companies,
        "codes": codes,
        "urgency": urgency,
        "trend": trend,
        "impact": min(
            intensity * 2 + (3 if urgency else 0) + (2 if companies else 0), 10
        ),
    }


def get_summary(news):
    """获取摘要信息"""
    title = news.get("title", "")
    analysis = news.get("analysis", {})

    # 优先显示公司
    if analysis.get("companies"):
        return analysis["companies"][0]

    # 显示趋势
    if analysis.get("trend"):
        return analysis["trend"]

    # 显示关键词
    if analysis.get("keywords"):
        return analysis["keywords"][0]

    return ""


def get_signal(news):
    """获取交易信号"""
    title = news.get("title", "")
    sent = news.get("sentiment", "")
    analysis = news.get("analysis", {})
    intensity = analysis.get("intensity", 0)

    if sent == "利好":
        if intensity >= 4:
            return "强势买入"
        if intensity >= 3:
            return "关注买入"
        return "逢低关注"
    elif sent == "利空":
        if intensity >= 4:
            return "坚决回避"
        if intensity >= 3:
            return "风险警示"
        return "谨慎观望"
    return "观望"


def get_risk(news_list):
    """多维度风险评估"""
    if not news_list:
        return "低风险"

    # 计算风险分数
    score = 0
    for n in news_list:
        sent = n.get("sentiment", "")
        analysis = n.get("analysis", {})
        intensity = analysis.get("intensity", 0)
        urgency = analysis.get("urgency", "")

        if sent == "利空":
            score += intensity
        if "【突发】" in urgency:
            score += 2
        if analysis.get("sector") in ["金融", "地产"]:
            score += 1

    if score >= 10:
        return "高风险"
    elif score >= 5:
        return "中风险"
    return "低风险"


def get_suggestion(news_list):
    """投资建议"""
    if not news_list:
        return "观望"

    # 统计情绪
    bullish = sum(1 for n in news_list if n.get("sentiment") == "利好")
    bearish = sum(1 for n in news_list if n.get("sentiment") == "利空")

    # 统计紧急
    urgent = sum(
        1 for n in news_list if "【突发】" in n.get("analysis", {}).get("urgency", "")
    )

    if bullish > bearish * 2 and urgent == 0:
        return "积极布局"
    elif bullish > bearish:
        return "谨慎做多"
    elif bearish > bullish * 2:
        return "防守为主"
    elif bearish > bullish:
        return "控制仓位"
    return "观望等待"


def get_external():
    try:
        url = "https://hq.sinajs.cn/list=gb_ixic,gb_ipsa,gb_inx"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "http://finance.sina.com.cn",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = resp.read().decode("gbk")
        markets = []
        names = {"ixic": "纳指", "ipsa": "标普", "inx": "道指"}
        for line in data.strip().split("\n"):
            if "=" in line:
                sym = line.split("=")[0].split("_")[-1]
                parts = line.split('"')
                if len(parts) >= 2:
                    vals = parts[1].split(",")
                    if len(vals) >= 3:
                        name = names.get(sym, sym)
                        chg = float(vals[1])
                        pct = float(vals[2])
                        direction = "+" if chg >= 0 else ""
                        markets.append(f"{name}:{direction}{pct:.2f}%")
        return " | ".join(markets[:3]) if markets else ""
    except Exception as e:
        return ""


def get_ashare():
    try:
        # 使用东方财富API
        url = "https://push2.eastmoney.com/api/qt/ulist.np/get?fltt=2&invt=2&fields=f2,f3,f4,f12,f14&secids=1.000001,0.399001,0.399006"
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://finance.eastmoney.com",
            },
        )
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        indices = []
        names = {"1.000001": "上证", "0.399001": "深证", "0.399006": "创业板"}
        for item in data.get("data", {}).get("diff", []):
            secid = item.get("f12", "")
            name = names.get(secid, secid)
            pct = item.get("f3", 0)  # 涨跌幅
            direction = "+" if pct >= 0 else ""
            indices.append(f"{name}:{direction}{pct:.2f}%")
        return " | ".join(indices[:3]) if indices else ""
    except Exception as e:
        return ""


def get_commodities():
    try:
        # 使用 Yahoo Finance API
        url = "https://query1.finance.yahoo.com/v8/finance/chart/GC=F,CL=F?interval=1d&range=1d"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        result = data.get("chart", {}).get("result", [])
        items = []
        for r in result:
            meta = r.get("meta", {})
            sym = meta.get("symbol", "").replace("=F", "")
            pct = meta.get("regularMarketChangePercent", 0)
            direction = "+" if pct >= 0 else ""
            name = "Gold" if "GC" in sym else "Oil" if "CL" in sym else sym
            items.append(f"{name}:{direction}{pct:.2f}%")
        return " | ".join(items) if items else ""
    except Exception as e:
        return ""


def get_hk():
    # 港股数据暂不可用，跳过
    return ""


def get_vix():
    try:
        url = "https://hq.sinajs.cn/list=hkvix"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode("gbk")
        if '"' in data:
            vals = data.split('"')[1].split(",")
            if len(vals) >= 2:
                vix = float(vals[0])
                chg = float(vals[1])
                direction = "+" if chg >= 0 else ""
                status = "恐慌" if vix > 20 else "平稳"
                return f"VIX:{vix:.1f}({direction}{chg:.1f}) [{status}]"
        return ""
    except:
        return ""


def get_forex():
    try:
        url = "https://hq.sinajs.cn/list=fx_susdcny,fx_seurusd"
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = resp.read().decode("gbk")
        items = []
        names = {"susdcny": "USD/CNY", "seurusd": "EUR/USD"}
        for line in data.strip().split("\n"):
            if "=" in line:
                sym = line.split("=")[0].split("_")[-1]
                vals = line.split('"')[1].split(",")
                if len(vals) >= 4:
                    name = names.get(sym, sym)
                    price = float(vals[0])
                    chg = float(vals[1])
                    pct = float(vals[3])
                    direction = "+" if chg >= 0 else ""
                    items.append(f"{name}:{price:.4f}({direction}{pct:.2f}%)")
        return " | ".join(items)
    except:
        return ""


class NewsData:
    def __init__(self):
        self.data = self._load()

    def _load(self):
        if DATA_FILE.exists():
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                pass
        return {"news": [], "sent": [], "stats": {"total": 0, "qq": 0, "feishu": 0}}

    def save(self):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(self.data, f, ensure_ascii=False, indent=2)

    def add_news(self, title, url, source="", category=""):
        news_id = hash(title + url) & 0xFFFFFFFF
        for n in self.data["news"]:
            if n["id"] == news_id:
                return False
        analysis = smart_analyze(title)
        self.data["news"].append(
            {
                "id": news_id,
                "title": title,
                "url": url,
                "source": source,
                "category": category,
                "sentiment": analysis["sentiment"],
                "sector": analysis["sector"],
                "keywords": analysis["keywords"],
                "codes": analysis.get("codes", []),
                "analysis": analysis,
                "fetched_at": datetime.now().isoformat(),
                "sent": False,
            }
        )
        self.data["stats"]["total"] += 1
        self.save()
        return True

    def get_unsent(self, limit=5):
        unsent = [n for n in self.data["news"] if not n.get("sent")]
        return unsent[:limit]

    def mark_sent(self, ids):
        for n in self.data["news"]:
            if n["id"] in ids:
                n["sent"] = True
        self.save()


def fetch_json(url):
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0",
                "Referer": "https://finance.sina.com.cn",
            },
        )
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        items = []
        if "result" in data and "data" in data["result"]:
            for item in data["result"]["data"]:
                title = item.get("title", "")
                url = item.get("url", "")
                if title and url:
                    items.append({"title": title, "url": url})
        return items
    except Exception as e:
        return []


def fetch_rss(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = resp.read().decode("utf-8", errors="ignore")
        items = []
        import xml.etree.ElementTree as ET

        root = ET.fromstring(data)
        for item in root.findall(".//item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            if title:
                items.append({"title": title, "url": link})
        return items
    except Exception as e:
        return []


def send_qq_message(group_id, message):
    try:
        url = f"{CONFIG['qq']['base_url']}/send_group_msg"
        data = {"group_id": int(group_id), "message": message, "auto_escape": False}
        headers = {"Content-Type": "application/json"}
        if CONFIG["qq"]["token"]:
            headers["Authorization"] = f"Bearer {CONFIG['qq']['token']}"
        req = urllib.request.Request(
            url, data=json.dumps(data).encode("utf-8"), headers=headers
        )
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
            result = json.loads(resp.read().decode("utf-8"))
        return result.get("status") == "ok", result.get("data", {}).get(
            "message_id", "OK"
        )
    except Exception as e:
        return False, str(e)


def send_feishu_message(text):
    try:
        cmd = ["py", str(BASE_DIR / "feishu_assistant.py"), "msg", text]
        result = subprocess.run(cmd, capture_output=True, timeout=30)
        try:
            stdout = (
                result.stdout.decode("utf-8", errors="ignore") if result.stdout else ""
            )
        except:
            stdout = ""
        # 只返回最后一行（实际结果），过滤掉日志
        lines = [
            l for l in stdout.split("\n") if "[" in l and "]" in l and "Sent:" in l
        ]
        success = "[OK] Text message sent" in stdout or "[OK] Sent:" in stdout
        msg_id = ""
        for line in stdout.split("\n"):
            if "om_" in line:
                msg_id = line.strip()
                break
        return success, msg_id if msg_id else ("OK" if success else "FAIL")
    except Exception as e:
        return False, str(e)


def cmd_fetch(args):
    now = datetime.now().strftime("%H:%M")
    total_src = len(CONFIG["news"]["sources"])

    data = NewsData()
    total_new = 0
    sentiment_stats = {"利好": 0, "利空": 0, "中性": 0}

    # 按来源分组
    grouped_news = {}

    for idx, source in enumerate(CONFIG["news"]["sources"]):
        cat = source.get("category", "")

        if source["type"] == "rss":
            items = fetch_rss(source["url"])
        else:
            items = fetch_json(source["url"])

        news_items = []
        for item in items[: CONFIG["news"]["max_per_fetch"]]:
            if data.add_news(item["title"], item["url"], source["name"], cat):
                total_new += 1
                analysis = smart_analyze(item["title"])
                sentiment_stats[analysis["sentiment"]] += 1
                # 提取公司名称用于显示
                company = (
                    analysis["companies"][0]
                    if analysis["companies"]
                    else (analysis["keywords"][0] if analysis["keywords"] else "")
                )
                news_items.append(
                    {
                        "sentiment": analysis["sentiment"],
                        "title": item["title"][:24],
                        "kw": company,
                        "urgency": analysis["urgency"],
                        "impact": analysis["impact"],
                    }
                )

        if news_items:
            grouped_news[cat] = news_items

    pos = sentiment_stats["利好"]
    neg = sentiment_stats["利空"]

    # LLM 状态
    llm_status = (
        c(Colors.GREEN, "[LLM]") if is_llm_available() else c(Colors.DIM, "[KW]")
    )

    # 华丽输出
    print(f"""
╔══════════════════════╗
║ {c(Colors.BOLD, "NEWS FEED")} {llm_status} {total_new} new  {c(Colors.DIM, now)}║
╠══════════════════════╣""")

    if grouped_news:
        sorted_cats = sorted(grouped_news.items(), key=lambda x: -len(x[1]))

        for cat, news_items in sorted_cats[:6]:
            pos_c = sum(1 for n in news_items if n["sentiment"] == "利好")
            neg_c = sum(1 for n in news_items if n["sentiment"] == "利空")

            # 分类标题
            bar = (
                f"{cp('+' + str(pos_c))}{cn('-' + str(neg_c))}"
                if pos_c or neg_c
                else ""
            )
            print(
                f"║ {c(Colors.BOLD, cat[:6])} {len(news_items):>2} {bar}{' ' * max(0, 12 - len(bar))}║"
            )

            # 显示第一条
            n = news_items[0]
            icon = (
                cp("+")
                if n["sentiment"] == "利好"
                else cn("-")
                if n["sentiment"] == "利空"
                else cne("=")
            )
            urgency = cn(n["urgency"]) if n.get("urgency") else ""
            kw = f"#{n['kw']}" if n["kw"] else ""
            title = n["title"][:22]
            if kw or urgency:
                print(f"║  {icon} {urgency}{title:<16}{kw:<6}║")
            else:
                print(f"║  {icon} {title:<28}║")

            if len(news_items) > 1:
                print(
                    f"║  {c(Colors.DIM, '+' + str(len(news_items) - 1) + ' more...')}{' ' * 18}║"
                )

        print(f"╠══════════════════════╣")
        print(f"║ {c(Colors.BOLD, 'Summary')}{' ' * 25}║")
        print(
            f"║  Sources: {len(grouped_news)}/{total_src:<5} Bull: {cp('+' + str(pos))} Bear: {cn('-' + str(neg))}║"
        )
    else:
        print(f"║  {cne('[.] No new news')}{' ' * 19}║")

    print(f"╚══════════════════════╝")
    print()
    return total_new


def cmd_push(args):
    data = NewsData()
    news_list = data.get_unsent(limit=int(args.limit) if hasattr(args, "limit") else 5)
    if not news_list:
        print(f"""
╔══════════════════════╗
║ {cn("[!] No news to push")}    ║
╚══════════════════════╝""")
        return

    risk = get_risk(news_list)
    now = datetime.now().strftime("%H:%M")

    # 构建消息 (紧凑格式)
    header = f"[NEWS] {now}"
    body = "\n".join(
        [
            f"{'+' if n.get('sentiment') == '利好' else '-' if n.get('sentiment') == '利空' else '='} {n.get('title', '')[:30]}"
            for n in news_list
        ]
    )
    sources = list(
        set(
            [
                SOURCE_MAP.get(n.get("source", ""), n.get("category", ""))
                for n in news_list
            ]
        )
    )[:4]
    sectors = list(set([n.get("sector", "通用") for n in news_list]))[:3]
    msg = f"{header}\n{body}\n---\nSources: {', '.join(sources)}\nSectors: {', '.join(sectors)}\nRisk:{risk}"
    msg = msg.strip()
    ids = [n["id"] for n in news_list]
    results = []

    # 统计
    pos_cnt = sum(1 for n in news_list if n.get("sentiment") == "利好")
    neg_cnt = sum(1 for n in news_list if n.get("sentiment") == "利空")

    # 风险评估
    if risk == "高风险":
        risk_icon = cn("![HIGH]")
    elif risk == "中风险":
        risk_icon = c(Colors.YELLOW, "~[MED]")
    else:
        risk_icon = cp("*[LOW]")

    # 华丽输出
    print(f"""
╔══════════════════════╗
║ {c(Colors.BOLD, "PUSH NEWS")}{" " * (17 - len(str(len(news_list))))}{len(news_list)} items  {c(Colors.DIM, now)}║
╠══════════════════════╣
║ {c(Colors.BOLD, "Items")}{" " * 26}║""")

    # 情绪条
    bar_len = 12
    pos_bar = int(pos_cnt / len(news_list) * bar_len) if news_list else 0
    neg_bar = int(neg_cnt / len(news_list) * bar_len) if news_list else 0
    sentiment_bar = (
        cp("#" * pos_bar) + cn("#" * neg_bar) + cne("-" * (bar_len - pos_bar - neg_bar))
    )
    print(f"║  [{sentiment_bar}]             ║")
    print(f"║  {cp('+' + str(pos_cnt))} {cn('-' + str(neg_cnt))}  Risk: {risk_icon}  ║")

    # 预览
    print(f"╠══════════════════════╣")
    print(f"║ {c(Colors.BOLD, 'Preview')}{' ' * 24}║")
    for n in news_list[:3]:
        icon = (
            cp("+")
            if n.get("sentiment") == "利好"
            else cn("-")
            if n.get("sentiment") == "利空"
            else cne("=")
        )
        title = n.get("title", "")[:26]
        print(f"║  {icon} {title:<24}║")
    if len(news_list) > 3:
        print(
            f"║  {c(Colors.DIM, '+' + str(len(news_list) - 3) + ' more...')}{' ' * 19}║"
        )

    # 发送
    print(f"╠══════════════════════╣")
    print(f"║ {c(Colors.BOLD, 'Sending')}{' ' * 25}║")

    if CONFIG["qq"]["enabled"]:
        ok, mid = send_qq_message(CONFIG["qq"]["group_id"], msg)
        status = cp("[OK]") if ok else cn("[FAIL]")
        print(f"║  QQ: {status}{' ' * 20}║")
        if ok:
            data.data["stats"]["qq"] = data.data["stats"].get("qq", 0) + 1
            results.append("QQ")

    if CONFIG["feishu"]["enabled"]:
        ok, mid = send_feishu_message(msg)
        status = cp("[OK]") if ok else cn("[FAIL]")
        print(f"║  FS: {status}{' ' * 20}║")
        if ok:
            data.data["stats"]["feishu"] = data.data["stats"].get("feishu", 0) + 1
            results.append("Feishu")

    data.mark_sent(ids)
    data.save()

    if results:
        print(f"╠══════════════════════╣")
        print(
            f"║  {cp('[*] Pushed to ' + str(len(results)) + ' platform(s)')}{' ' * 7}║"
        )

    print(f"╚══════════════════════╝")
    print()


def cmd_status(args):
    data = NewsData()
    total = len(data.data["news"])
    unsent = len([n for n in data.data["news"] if not n.get("sent")])
    sent = total - unsent

    # 统计
    sectors = {}
    sentiments = {"利好": 0, "利空": 0, "中性": 0}
    for n in data.data["news"]:
        sectors[n.get("sector", "通用")] = sectors.get(n.get("sector", "通用"), 0) + 1
        sentiments[n.get("sentiment", "中性")] = (
            sentiments.get(n.get("sentiment", "中性"), 0) + 1
        )

    now = datetime.now().strftime("%H:%M")
    sent_pct = sent / total * 100 if total > 0 else 0
    pos = sentiments["利好"]
    neg = sentiments["利空"]
    neu = sentiments["中性"]

    # 风险评估
    risk_score = neg * 2 - pos
    if risk_score > 10:
        risk_icon = cn("![HIGH]")
        risk_bar = cn(">>>")
    elif risk_score > 5:
        risk_icon = c(Colors.YELLOW, "~[MED]")
        risk_bar = c(Colors.YELLOW, ">>")
    else:
        risk_icon = cp("*[LOW]")
        risk_bar = cp("<<")

    # 华丽移动端输出
    print(f"""
╔══════════════════════╗
║ {c(Colors.BOLD, "NEWS STATUS")}{" " * (14 - len(now))}{c(Colors.DIM, now)}║
╠══════════════════════╣""")

    # 迷你仪表盘
    print(f"║ {c(Colors.BOLD, 'Dashboard')}{' ' * 27}║")

    # 进度条
    bar_len = 14
    filled = int(sent_pct / 100 * bar_len)
    bar = cp("#" * filled) + c(Colors.DIM, "-" * (bar_len - filled))
    print(f"║  Push: [{bar}] {sent_pct:>4.0f}%║")

    # 情绪仪表
    mood_pct = pos / total * 100 if total > 0 else 0
    mood_bar_len = 6
    mood_filled = int(mood_pct / 100 * mood_bar_len)
    mood_bar = cp("#" * mood_filled) + c(Colors.DIM, "-" * (mood_bar_len - mood_filled))
    print(f"║  Mood: [{mood_bar}] {pos:>3} /{total:<3}║")

    # 风险指示
    print(f"║  Risk: {risk_icon}{' ' * 18}║")

    # 分隔线
    print(f"╠══════════════════════╣")
    print(f"║ {c(Colors.BOLD, 'Statistics')}{' ' * 25}║")

    # 数据行
    print(f"║  Total: {total:<5} Sent: {sent:<5} Wait: {unsent:<4}║")
    print(
        f"║  Bull: {cp('+' + str(pos))}  Bear: {cn('-' + str(neg))}  Neu: {cne(str(neu))}   ║"
    )

    # 板块分布
    top_sectors = sorted(sectors.items(), key=lambda x: -x[1])[:3]
    if top_sectors:
        sec1 = f"{top_sectors[0][0][:3]}:{top_sectors[0][1]}"
        sec2 = (
            f"{top_sectors[1][0][:3]}:{top_sectors[1][1]}"
            if len(top_sectors) > 1
            else "---"
        )
        sec3 = (
            f"{top_sectors[2][0][:3]}:{top_sectors[2][1]}"
            if len(top_sectors) > 2
            else "---"
        )
        print(f"║  Top: {sec1:<7} {sec2:<7} {sec3:<7}║")

    # 推送统计
    qq_cnt = data.data["stats"].get("qq", 0)
    fs_cnt = data.data["stats"].get("feishu", 0)
    print(f"╠══════════════════════╣")
    print(f"║  {c(Colors.BOLD, 'Platform')}{' ' * 26}║")
    print(f"║  QQ: {qq_cnt:<5}  FS: {fs_cnt:<5}        ║")
    print(f"╚══════════════════════╝")
    print()


def cmd_digest(args):
    data = NewsData()
    days = int(args.days) if hasattr(args, "days") else 1
    cutoff = datetime.now() - timedelta(days=days)
    recent = [
        n
        for n in data.data["news"]
        if datetime.fromisoformat(n.get("fetched_at", "2000")).replace(tzinfo=None)
        > cutoff
    ]

    if not recent:
        print(f"\n╔══════════════════════╗")
        print(f"║ {cn('[!] No news found')}    ║")
        print(f"╚══════════════════════╝")
        return

    now = datetime.now().strftime("%H:%M")

    # 统计
    sentiments = {"利好": [], "利空": [], "中性": []}
    for n in recent:
        sentiments[n.get("sentiment", "中性")].append(n)

    # 关键词统计
    keywords = {}
    for n in recent:
        for kw in n.get("keywords", []):
            keywords[kw] = keywords.get(kw, 0) + 1
    top_keywords = sorted(keywords.items(), key=lambda x: -x[1])[:5]

    total = len(recent)
    pos = len(sentiments["利好"])
    neg = len(sentiments["利空"])
    neu = len(sentiments["中性"])

    # 风险评估
    risk_score = neg * 2 - pos
    if risk_score > 10:
        risk_icon = cn("![HIGH]")
    elif risk_score > 5:
        risk_icon = c(Colors.YELLOW, "~[MED]")
    else:
        risk_icon = cp("*[LOW]")

    # 华丽输出
    print(f"""
╔══════════════════════╗
║ {c(Colors.BOLD, "NEWS DIGEST")}{" " * (16 - len(str(days)))}{days}d  {c(Colors.DIM, now)}║
╠══════════════════════╣""")

    # 情绪摘要
    print(f"║ {c(Colors.BOLD, 'Sentiment Overview')}{' ' * 16}║")

    # 迷你情绪条
    bar_len = 12
    pos_bar = int(pos / total * bar_len) if total > 0 else 0
    neg_bar = int(neg / total * bar_len) if total > 0 else 0
    sentiment_bar = (
        cp("#" * pos_bar) + cn("#" * neg_bar) + cne("-" * (bar_len - pos_bar - neg_bar))
    )
    print(f"║  [{sentiment_bar}]             ║")
    print(
        f"║  {cp('+' + str(pos))} {cn('-' + str(neg))} {cne('=' + str(neu))}  Total:{total:<5}║"
    )

    # 风险
    print(f"╠══════════════════════╣")
    print(f"║  Risk: {risk_icon}{' ' * 17}║")

    # 热门标签
    if top_keywords:
        print(f"╠══════════════════════╣")
        print(f"║ {c(Colors.BOLD, 'Hot Topics')}{' ' * 23}║")
        tags_line = " ".join([f"#{k}" for k, _ in top_keywords])
        if len(tags_line) > 26:
            tags_line = tags_line[:24] + ".."
        print(f"║  {tags_line:<24}║")

    # 热门新闻预览
    print(f"╠══════════════════════╣")
    print(f"║ {c(Colors.BOLD, 'Preview')}{' ' * 24}║")

    for sent_type, news_list in sentiments.items():
        if not news_list or len(news_list) < 1:
            continue
        icon = (
            cp("+")
            if sent_type == "利好"
            else cn("-")
            if sent_type == "利空"
            else cne("=")
        )
        title = news_list[0].get("title", "")[:22]
        print(f"║  {icon} {title:<22}║")

    print(f"╚══════════════════════╝")
    print()


def cmd_market(args):
    """显示实时行情 - 华丽移动端"""
    now = datetime.now().strftime("%H:%M")

    # 美股
    external = get_external()
    # A股
    ashare = get_ashare()
    # 大宗商品
    commodities = get_commodities()
    # VIX
    vix = get_vix()

    # 华丽移动端输出
    print(f"""
╔══════════════════════╗
║ {c(Colors.BOLD, "MARKET MONITOR")}{" " * 12}{c(Colors.DIM, now)}║
╠══════════════════════╣""")

    # US Markets
    if external:
        print(f"║ {c(Colors.BOLD, 'US Markets')}{' ' * 23}║")
        print(f"║  {external:<26}║")

    # CN Markets
    if ashare:
        print(f"╠══════════════════════╣")
        print(f"║ {c(Colors.BOLD, 'CN Markets')}{' ' * 23}║")
        print(f"║  {ashare:<26}║")

    # Commodities
    if commodities:
        print(f"╠══════════════════════╣")
        print(f"║ {c(Colors.BOLD, 'Commodities')}{' ' * 21}║")
        print(f"║  {commodities:<26}║")

    # VIX
    if vix:
        print(f"╠══════════════════════╣")
        print(f"║ {c(Colors.BOLD, 'Volatility')}{' ' * 21}║")
        print(f"║  {vix:<26}║")

    # Footer
    print(f"╚══════════════════════╝")
    print(f"{c(Colors.DIM, 'Updated: ' + now)}")
    print()


def cmd_clean(args):
    """清理历史数据"""
    data = NewsData()
    days = int(args.days) if hasattr(args, "days") else 7
    before = datetime.now() - timedelta(days=days)

    old_count = 0
    old_news = []
    for n in data.data["news"]:
        try:
            fetched = datetime.fromisoformat(n.get("fetched_at", "2000")).replace(
                tzinfo=None
            )
            if fetched < before:
                old_count += 1
                old_news.append(n["id"])
        except:
            pass

    if old_news:
        data.data["news"] = [n for n in data.data["news"] if n["id"] not in old_news]
        data.save()
        print(f"{cn('[Cleaned]')} Removed {old_count} news older than {days} days")
    else:
        print(f"{cp('[OK]')} No news older than {days} days")
    print()


def cmd_sources(args):
    """显示新闻源状态"""
    print(f"\n{c(Colors.header(), '=== NEWS SOURCES ===')}\n")

    for src in CONFIG["news"]["sources"]:
        cat = src.get("category", "")
        src_type = "RSS" if src["type"] == "rss" else "JSON"
        print(f"  {c(Colors.BOLD, cat):<8} [{src_type}] {src['name']}")

    print(f"\nTotal: {len(CONFIG['news']['sources'])} sources")
    print()


def cmd_help(args=None):
    """显示帮助"""
    print(f"""
{c(Colors.header(), "=== NEWS MANAGER HELP ===")}

{c(Colors.BOLD, "Commands:")}
  fetch      Fetch news from all sources
  push       Push unsent news to platforms
  status     Show current status
  digest     Show news digest summary
  market     Show real-time market data
  sources    List all news sources
  clean      Clean old news data
  help       Show this help

{c(Colors.BOLD, "Options:")}
  --limit N   Number of news to push (default: 5)
  --days N    Days for digest/clean (default: 1)

{c(Colors.BOLD, "Examples:")}
  news_manager.py fetch
  news_manager.py push --limit 10
  news_manager.py digest --days 7
  news_manager.py clean --days 30
  news_manager.py market

{c(Colors.BOLD, "Files:")}
  Data: {DATA_FILE}
""")


def main():
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize", "--auto"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        return

    print("[OK] Critic Review Passed")

    import argparse

    parser = argparse.ArgumentParser(description="News Manager v3.0", add_help=False)
    parser.add_argument(
        "cmd",
        nargs="?",
        default="help",
        choices=[
            "fetch",
            "push",
            "status",
            "digest",
            "market",
            "sources",
            "clean",
            "help",
        ],
        help="Command",
    )
    parser.add_argument("--limit", default="5", help="News limit")
    parser.add_argument("--days", default="1", help="Days for digest/clean")
    parser.add_argument("-h", "--help", action="store_true")
    args = parser.parse_args()

    if args.help or args.cmd == "help":
        cmd_help()
    elif args.cmd == "fetch":
        cmd_fetch(args)
    elif args.cmd == "push":
        cmd_push(args)
    elif args.cmd == "status":
        cmd_status(args)
    elif args.cmd == "digest":
        cmd_digest(args)
    elif args.cmd == "market":
        cmd_market(args)
    elif args.cmd == "sources":
        cmd_sources(args)
    elif args.cmd == "clean":
        cmd_clean(args)


if __name__ == "__main__":
    main()

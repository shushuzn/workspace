"""
智能新闻分析器 - 支持本地 LLM
支持: Ollama, LM Studio, 回退关键词分析
"""

import subprocess
import sys
from pathlib import Path

import json
import re
import urllib.request
import urllib.error
from datetime import datetime
from typing import Optional, Dict, Any

CONFIG_PATH = "30-scripts-tools/llm_config.json"

POSITIVE = [
    "涨停",
    "大涨",
    "飙升",
    "暴涨",
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
    "黑天鹅",
    "闪崩",
    "踩踏",
    "恐慌",
    "抛售",
]
SECTORS = {
    "科技": [
        "AI",
        "人工智能",
        "芯片",
        "半导体",
        "华为",
        "腾讯",
        "阿里",
        "字节",
        "算力",
        "机器人",
        "软件",
        "云计算",
        "5G",
        "6G",
        "苹果",
        "微软",
        "英伟达",
        "谷歌",
        "Meta",
        "OpenAI",
        "自动驾驶",
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
        "碳中和",
    ],
    "金融": [
        "银行",
        "保险",
        "券商",
        "基金",
        "证券",
        "期货",
        "外汇",
        "央行",
        "美联储",
        "降息",
        "加息",
        "流动性",
        "利率",
        "汇率",
    ],
    "地产": ["房地产", "万科", "恒大", "碧桂园", "融创", "保利", "物业"],
    "医药": ["医药", "医疗", "疫苗", "创新药", "中药", "医疗器械", "生物医药", "医美"],
    "消费": ["消费", "食品", "饮料", "白酒", "茅台", "家电", "汽车", "零售", "旅游"],
    "周期": [
        "煤炭",
        "钢铁",
        "有色",
        "水泥",
        "化工",
        "石油",
        "原油",
        "黄金",
        "铜",
        "铝",
        "锂",
    ],
    "军工": ["军工", "国防", "航空航天", "导弹", "舰船", "无人机", "卫星", "北斗"],
    "传媒": ["传媒", "影视", "电影", "电视剧", "综艺", "游戏", "电竞"],
    "宏观": [
        "GDP",
        "CPI",
        "PPI",
        "PMI",
        "就业",
        "投资",
        "贸易",
        "关税",
        "经济",
        "政策",
    ],
}
COMPANIES = {
    "华为": ["华为", "任正非"],
    "阿里": ["阿里", "马云", "蔡崇信", "阿里巴巴"],
    "腾讯": ["腾讯", "马化腾", "微信"],
    "字节": ["字节", "抖音", "TikTok", "张一鸣"],
    "小米": ["小米", "雷军"],
    "比亚迪": ["比亚迪", "王传福"],
    "特斯拉": ["特斯拉", "马斯克"],
    "茅台": ["茅台"],
    "宁德": ["宁德", "CATL"],
    "苹果": ["苹果", "iPhone"],
    "微软": ["微软"],
    "OpenAI": ["OpenAI", "ChatGPT", "GPT"],
    "英伟达": ["英伟达", "NVIDIA", "GPU"],
    "谷歌": ["谷歌", "Google"],
}
URGENT = ["突发", "重磅", "暴跌", "涨停", "紧急", "警告", "崩溃", "史上", "首次"]


def keyword_analyze(title: str) -> Dict[str, Any]:
    pos = sum(1 for w in POSITIVE if w in title)
    neg = sum(1 for w in NEGATIVE if w in title)
    sentiment = "利好" if pos > neg else "利空" if neg > pos else "中性"
    intensity = min(5, max(1, pos if pos > neg else neg))
    # 优先级: 科技/新能源 > 金融/地产/医药/消费 > 周期/军工/传媒 > 宏观 > 通用
    priority = [
        "科技",
        "新能源",
        "金融",
        "地产",
        "医药",
        "消费",
        "周期",
        "军工",
        "传媒",
        "宏观",
        "通用",
    ]
    scores = {}
    for s in priority:
        if s in SECTORS:
            scores[s] = sum(1 for w in SECTORS[s] if w in title)
    sector = (
        max(scores, key=lambda x: (scores[x], -priority.index(x)))
        if any(scores.values())
        else "通用"
    )
    kws = [kw for kw_list in SECTORS.values() for kw in kw_list if kw in title][:5]
    comps = [c for c, als in COMPANIES.items() if any(a in title for a in als)]
    urgency = "高" if any(u in title for u in URGENT) else "中"
    impact = min(
        intensity * 2 + (3 if urgency == "高" else 0) + (2 if comps else 0), 10
    )
    return {
        "sentiment": sentiment,
        "intensity": intensity,
        "sector": sector,
        "keywords": kws,
        "companies": comps,
        "urgency": urgency,
        "summary": title[:50],
        "impact": impact,
        "method": "keyword",
    }


class LLMAnalyzer:
    def __init__(self):
        self.cfg = self._load()
        self.available = self._check()

    def _load(self) -> Dict:
        try:
            with open(CONFIG_PATH, encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"enabled": False}

    def _check(self) -> bool:
        if not self.cfg.get("enabled"):
            return False
        url = (
            self.cfg.get("providers", {})
            .get(self.cfg.get("provider", "ollama"), {})
            .get("url", "")
        )
        if not url:
            return False
        try:
            req = urllib.request.Request(f"{url}/api/version")
            urllib.request.urlopen(req, timeout=3)
            return True
        except:
            return False

    def analyze(self, title: str) -> Dict[str, Any]:
        if not self.available:
            return keyword_analyze(title)
        try:
            result = self._call(title)
            if result:
                result["method"] = "llm"
                return result
        except Exception as e:
            print(f"LLM: {e}")
        return keyword_analyze(title)

    def _call(self, title: str) -> Optional[Dict]:
        provider = self.cfg.get("provider", "ollama")
        cfg = self.cfg.get("providers", {}).get(provider, {})
        url = cfg.get("url", "") + cfg.get("chat_endpoint", "")

        prompt = f"""分析新闻标题，输出JSON：
{{"sentiment":"利好|利空|中性","intensity":1-5,"sector":"科技|新能源|金融|地产|医药|消费|周期|军工|传媒|宏观|通用","keywords":["kw1","kw2"],"companies":["公司"],"urgency":"高|中|低","summary":"一句话"}}

标题：{title}
只输出JSON。"""

        if provider == "ollama":
            data = {
                "model": cfg.get("model", "qwen2.5:7b"),
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }
        else:
            data = {
                "model": cfg.get("model", "local-model"),
                "messages": [{"role": "user", "content": prompt}],
                "stream": False,
            }

        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode(),
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=self.cfg.get("timeout", 30)) as resp:
            result = json.loads(resp.read())

        if provider == "ollama":
            content = result.get("message", {}).get("content", "")
        else:
            content = (
                result.get("choices", [{}])[0].get("message", {}).get("content", "")
            )

        json_match = re.search(r"\{[^{}]*\}", content, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())
        return None


_analyzer = None


def analyze(title: str) -> Dict[str, Any]:
    global _analyzer
    if _analyzer is None:
        _analyzer = LLMAnalyzer()
    return _analyzer.analyze(title)


def is_llm_available() -> bool:
    global _analyzer
    if _analyzer is None:
        _analyzer = LLMAnalyzer()
    return _analyzer.available


if __name__ == "__main__":
    # Critic v5.0 integration
    critic_result = subprocess.run(
        [sys.executable, "critic_v5_review.py", "--scenario", "tool_optimize", "--auto"],
        cwd=str(Path(__file__).parent),
        timeout=300,
    )
    if critic_result.returncode != 0:
        print("[ERROR] Critic Review Failed. Aborting.")
        exit(1)
    print("[OK] Critic Review Passed")

    print("=== LLM Analyzer Test ===")
    print(f"LLM Available: {is_llm_available()}")
    print()
    tests = [
        "突发！华为发布新一代AI芯片，业绩预增超预期",
        "监管重拳出击，多家银行被处罚，股价大跌",
        "特斯拉Model Y降价，订单暴涨，新能源板块反弹",
    ]
    for title in tests:
        r = analyze(title)
        print(f"[{r['method']}] {title[:30]}...")
        print(f"  Sentiment: {r['sentiment']} (intensity: {r['intensity']})")
        print(f"  Sector: {r['sector']} | Urgency: {r['urgency']}")
        print(f"  Keywords: {r['keywords'][:3]}")
        print()

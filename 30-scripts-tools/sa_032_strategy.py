#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
SA-032 策略推荐引擎
【Phase 6 - AI 增强】

功能:
  - 智能策略推荐
  - 风险匹配
  - 个性化建议
  - 策略比较

依赖: numpy, pandas (可选)
"""
import json
import sys
import os
from pathlib import Path
from datetime import datetime
import random

# 配置
STRATEGY_DIR = Path("60-DATA/stock_032")
CONFIG_FILE = Path("30-scripts-tools/sa_032_config.json")


# 策略库
STRATEGIES = {
    "conservative": {
        "name": "保守型",
        "description": "低风险、稳健收益",
        "max_drawdown": 0.05,
        "expected_return": 0.08,
        "suitable_for": ["保守投资者", "退休计划"],
        "indicators": ["MA200", "RSI(14)", "BOLL"],
        "position_size": "10-20%"
    },
    "moderate": {
        "name": "稳健型",
        "description": "平衡风险与收益",
        "max_drawdown": 0.10,
        "expected_return": 0.15,
        "suitable_for": ["稳健投资者", "长期投资"],
        "indicators": ["MA60", "MACD", "RSI"],
        "position_size": "30-50%"
    },
    "aggressive": {
        "name": "激进型",
        "description": "追求高收益",
        "max_drawdown": 0.20,
        "expected_return": 0.25,
        "suitable_for": ["激进投资者", "短期交易"],
        "indicators": ["MA5", "KDJ", "RSI(6)"],
        "position_size": "60-80%"
    },
    "swing": {
        "name": "趋势交易",
        "description": "跟随趋势",
        "max_drawdown": 0.15,
        "expected_return": 0.20,
        "suitable_for": ["趋势投资者"],
        "indicators": ["MA(20,60)", "MACD", "ADX"],
        "position_size": "40-60%"
    },
    "contrarian": {
        "name": "逆向投资",
        "description": "左侧交易",
        "max_drawdown": 0.25,
        "expected_return": 0.30,
        "suitable_for": ["逆向投资者"],
        "indicators": ["PE", "PB", "RSI(<30)"],
        "position_size": "20-40%"
    }
}


class StrategyEngine:
    """策略推荐引擎"""
    
    def __init__(self):
        self.strategy_dir = STRATEGY_DIR
        self.config = self._load_config()
        
        self.strategy_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.strategy_dir / "recommendation_history.json"
        self.strategies = STRATEGIES
    
    def _load_config(self) -> dict:
        default = {
            "default_strategy": "moderate",
            "risk_tolerance": "moderate"
        }
        
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                    return {**default, **json.load(f)}
            except:
                return default
        return default
    
    def _assess_risk(self, profile: dict) -> str:
        """评估风险等级"""
        risk_score = 0
        
        # 年龄因素
        age = profile.get("age", 35)
        if age < 30:
            risk_score += 3
        elif age < 40:
            risk_score += 2
        elif age < 50:
            risk_score += 1
        else:
            risk_score += 0
        
        # 投资经验
        exp = profile.get("experience", 3)
        if exp > 10:
            risk_score += 3
        elif exp > 5:
            risk_score += 2
        else:
            risk_score += 1
        
        # 风险偏好
        pref = profile.get("risk_preference", "moderate")
        if pref == "aggressive":
            risk_score += 3
        elif pref == "moderate":
            risk_score += 1
        else:
            risk_score += 0
        
        # 确定风险等级
        if risk_score >= 7:
            return "aggressive"
        elif risk_score >= 4:
            return "moderate"
        else:
            return "conservative"
    
    def recommend(self, profile: dict) -> dict:
        """推荐策略"""
        # 评估风险
        risk_level = self._assess_risk(profile)
        
        # 获取推荐策略
        strategy = STRATEGIES.get(risk_level, STRATEGIES["moderate"])
        
        result = {
            "timestamp": datetime.now().isoformat(),
            "risk_assessment": risk_level,
            "profile": profile,
            "recommended_strategy": {
                "type": risk_level,
                "name": strategy["name"],
                "description": strategy["description"],
                "max_drawdown": strategy["max_drawdown"],
                "expected_return": strategy["expected_return"],
                "indicators": strategy["indicators"],
                "position_size": strategy["position_size"],
                "suitable_for": strategy["suitable_for"]
            },
            "alternatives": self._get_alternatives(risk_level)
        }
        
        # 保存
        self._save_recommendation(result)
        
        return result
    
    def _get_alternatives(self, risk_level: str) -> list:
        """获取备选策略"""
        alternatives = []
        for key, strat in STRATEGIES.items():
            if key != risk_level:
                alternatives.append({
                    "type": key,
                    "name": strat["name"],
                    "description": strat["description"],
                    "expected_return": strat["expected_return"]
                })
        return alternatives[:2]
    
    def _save_recommendation(self, result: dict):
        """保存推荐历史"""
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except:
                pass
        
        history.append({
            "risk_assessment": result["risk_assessment"],
            "strategy": result["recommended_strategy"]["type"],
            "timestamp": result["timestamp"]
        })
        
        history = history[-50:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def compare(self, strategies: list) -> dict:
        """比较策略"""
        comparison = []
        
        for strat_type in strategies:
            if strat_type in STRATEGIES:
                strat = STRATEGIES[strat_type]
                comparison.append({
                    "type": strat_type,
                    "name": strat["name"],
                    "description": strat["description"],
                    "max_drawdown": strat["max_drawdown"],
                    "expected_return": strat["expected_return"],
                    "risk_return_ratio": round(strat["expected_return"] / strat["max_drawdown"], 2) if strat["max_drawdown"] > 0 else 0
                })
        
        # 按风险收益比排序
        comparison.sort(key=lambda x: x["risk_return_ratio"], reverse=True)
        
        return {
            "status": "success",
            "count": len(comparison),
            "comparison": comparison,
            "recommendation": comparison[0] if comparison else None
        }
    
    def backtest_preview(self, strategy_type: str, symbols: list) -> dict:
        """回测预览（模拟）"""
        random.seed(datetime.now().hour)
        
        if strategy_type not in STRATEGIES:
            return {"status": "error", "message": "Unknown strategy"}
        
        results = []
        for symbol in symbols:
            # 模拟结果
            return_pct = random.uniform(-0.1, 0.2)
            results.append({
                "symbol": symbol,
                "return_pct": round(return_pct * 100, 2),
                "win_rate": round(random.uniform(0.4, 0.7), 2)
            })
        
        avg_return = sum(r["return_pct"] for r in results) / len(results)
        
        return {
            "status": "success",
            "strategy": strategy_type,
            "symbols": symbols,
            "results": results,
            "average_return": round(avg_return, 2),
            "note": "This is a simulation for preview purposes"
        }
    
    def get_strategy(self, strategy_type: str) -> dict:
        """获取策略详情"""
        if strategy_type not in STRATEGIES:
            return {"status": "error", "message": "Strategy not found"}
        
        return {
            "status": "success",
            "strategy": STRATEGIES[strategy_type]
        }
    
    def list_strategies(self) -> dict:
        """列出所有策略"""
        return {
            "status": "success",
            "count": len(STRATEGIES),
            "strategies": [
                {"type": k, "name": v["name"], "description": v["description"]}
                for k, v in STRATEGIES.items()
            ]
        }
    
    def get_history(self, limit: int = 10) -> dict:
        """获取推荐历史"""
        if not self.history_file.exists():
            return {"status": "error", "message": "No history"}
        
        with open(self.history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        
        return {
            "status": "success",
            "count": len(history),
            "history": history[-limit:]
        }


def main():
    engine = StrategyEngine()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--recommend":
            # 示例: --recommend age=35,experience=5,risk_preference=moderate
            profile = {"age": 35, "experience": 5, "risk_preference": "moderate"}
            if len(sys.argv) > 2:
                # 解析参数
                args = sys.argv[2].split(",")
                for arg in args:
                    if "=" in arg:
                        k, v = arg.split("=")
                        try:
                            profile[k] = int(v)
                        except:
                            profile[k] = v
            
            result = engine.recommend(profile)
            print(json.dumps({
                "risk_assessment": result["risk_assessment"],
                "strategy": result["recommended_strategy"]["type"],
                "name": result["recommended_strategy"]["name"],
                "expected_return": result["recommended_strategy"]["expected_return"]
            }, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--compare":
            strategies = sys.argv[2].split(",") if len(sys.argv) > 2 else ["conservative", "moderate", "aggressive"]
            result = engine.compare(strategies)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--list":
            result = engine.list_strategies()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--strategy":
            strategy_type = sys.argv[2] if len(sys.argv) > 2 else "moderate"
            result = engine.get_strategy(strategy_type)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--backtest":
            strategy = sys.argv[2] if len(sys.argv) > 2 else "moderate"
            symbols = sys.argv[3].split(",") if len(sys.argv) > 3 else ["AAPL", "GOOGL"]
            result = engine.backtest_preview(strategy, symbols)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--history":
            result = engine.get_history()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("SA-032 Strategy Recommendation Engine")
    print("Usage:")
    print("  py sa_032_strategy.py --recommend age=35,experience=5,risk_preference=moderate")
    print("  py sa_032_strategy.py --compare conservative,moderate,aggressive")
    print("  py sa_032_strategy.py --list")
    print("  py sa_032_strategy.py --strategy moderate")
    print("  py sa_032_strategy.py --backtest moderate AAPL,GOOGL")
    print("  py sa_032_strategy.py --history")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
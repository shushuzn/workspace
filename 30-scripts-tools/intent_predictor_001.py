#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
INTENT-PREDICTOR-001 AI Intent Prediction System
Predicts what user wants before they ask
"""
import json, re, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

LOGS_DIR = Path("13-memory/.workflow_logs")
HISTORY_FILE = Path("13-memory/.intent_history.json")

INTENT_PATTERNS = {
    "optimize": ["optimize", "improve", "fix", "better", "优化", "改善"],
    "create": ["create", "new", "write", "make", "创建", "新建"],
    "analyze": ["analyze", "check", "review", "scan", "分析", "检查"],
    "deploy": ["deploy", "release", "publish", "部署", "发布"],
    "test": ["test", "verify", "validate", "测试", "验证"],
    "learn": ["learn", "study", "research", "学习", "研究"],
    "brainstorm": ["brainstorm", "idea", "think", "头脑风暴", "创意"],
    "operate": ["operate", "manage", "monitor", "运营", "管理"],
}

class IntentPredictor:
    def __init__(self):
        self.history = self.load_history()
    
    def load_history(self):
        if HISTORY_FILE.exists():
            return json.loads(HISTORY_FILE.read_text(encoding="utf-8", errors="replace"))
        return {"intents": [], "commands": [], "last_updated": None}
    
    def detect_intent(self, text):
        text_lower = text.lower()
        scores = defaultdict(int)
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower:
                    scores[intent] += 1
        if not scores:
            return "unknown"
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def predict_next(self, current_intent):
        transitions = defaultdict(Counter)
        intents = self.history.get("intents", [])
        for i in range(len(intents) - 1):
            transitions[intents[i]][intents[i+1]] += 1
        if current_intent in transitions:
            return transitions[current_intent].most_common(1)[0][0]
        return None
    
    def recommend_action(self, intent):
        recs = {
            "optimize": [("self_heal", "运行自愈系统"), ("code_quality", "检查代码质量")],
            "create": [("brainstorm", "头脑风暴创意"), ("safe_coder", "安全代码生成")],
            "analyze": [("health", "健康检查"), ("topology_viz", "拓扑分析")],
            "brainstorm": [("scamper", "SCAMPER创新"), ("sixhats", "六顶思考帽")],
            "operate": [("ops_panel", "运营面板"), ("health", "健康检查")],
        }
        return recs.get(intent, [])
    
    def learn(self, intent, action):
        self.history["intents"].append(intent)
        self.history["commands"].append(action)
        HISTORY_FILE.write_text(json.dumps(self.history, indent=2, ensure_ascii=False))
    
    def generate_report(self):
        intents = self.history.get("intents", [])
        intent_counts = Counter(intents)
        last_intent = intents[-1] if intents else None
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_interactions": len(intents),
            "top_intents": intent_counts.most_common(5),
            "last_intent": last_intent,
            "predicted_next": self.predict_next(last_intent) if last_intent else None,
            "confidence": intent_counts.most_common(1)[0][1] / max(1, len(intents)) * 100 if intent_counts else 0
        }

def main():
    predictor = IntentPredictor()
    
    print("\n[INTENT-PREDICTOR-001] AI Intent Prediction")
    print("=" * 50)
    
    if "--predict" in sys.argv:
        report = predictor.generate_report()
        print("\n[PREDICTION]")
        print(f"  Total: {report['total_interactions']} interactions")
        print(f"  Confidence: {report['confidence']:.0f}%")
        if report['top_intents']:
            print(f"\n  Top intents:")
            for i, (intent, count) in enumerate(report['top_intents'][:3], 1):
                print(f"    {i}. {intent}: {count}x")
        print(f"\n  Predicted next: {report['predicted_next'] or 'unknown'}")
        
        if report['predicted_next']:
            actions = predictor.recommend_action(report['predicted_next'])
            print(f"\n  Recommended:")
            for action, desc in actions:
                print(f"    - {desc} [{action}]")
    
    elif "--detect" in sys.argv and len(sys.argv) > 2:
        text = " ".join(sys.argv[2:])
        intent = predictor.detect_intent(text)
        print(f"\n  Input: '{text}'")
        print(f"  Detected intent: {intent}")
        actions = predictor.recommend_action(intent)
        print(f"  Actions: {actions}")
    
    else:
        print("\nUsage:")
        print("  --predict    Predict next action")
        print("  --detect <text>    Detect intent from text")
        print("  --learn <intent> <action>    Learn from action")

if __name__ == "__main__":
    main()

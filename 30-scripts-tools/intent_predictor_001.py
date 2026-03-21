import logging
logger = logging.getLogger(__name__)

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

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

LOGS_DIR = Path("13-memory/.workflow_logs")
HISTORY_FILE = Path("13-memory/.intent_history.json")

INTENT_PATTERNS = {
    "optimize": ["optimize", "improve", "fix", "better", "youhua", "gaishan"],
    "create": ["create", "new", "write", "make", "create", "xinjian"],
    "analyze": ["analyze", "check", "review", "scan", "fenxi", "jiancha"],
    "deploy": ["deploy", "release", "publish", "deploy", "release"],
    "test": ["test", "verify", "validate", "ceshi", "yanzheng"],
    "learn": ["learn", "study", "research", "xuexi", "yanjiu"],
    "brainstorm": ["brainstorm", "idea", "think", "brainstorm", "chuangyi"],
    "operate": ["operate", "manage", "monitor", "yunying", "guanli"],
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
            "optimize": [("self_heal", "Run Self-Heal"), ("code_quality", "Check Quality")],
            "create": [("brainstorm", "Brainstorm Ideas"), ("safe_coder", "Safe Code Gen")],
            "analyze": [("health", "Health Check"), ("topology_viz", "Topology Analysis")],
            "brainstorm": [("scamper", "SCAMPER Innovation"), ("sixhats", "Six Thinking Hats")],
            "operate": [("ops_panel", "Ops Panel"), ("health", "Health Check")],
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

logging.basicConfig(level=logging.INFO)
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
    
    elif "--learn" in sys.argv and len(sys.argv) > 3:
        intent = sys.argv[2]
        action = sys.argv[3]
        predictor.learn(intent, action)
        print(f"\n  Learned: {intent} -> {action}")
    
    else:
        print("\nUsage:")
        print("  --predict        Predict next action")
        print("  --detect <text>  Detect intent from text")
        print("  --learn <i> <a>  Learn from action")

if __name__ == "__main__":
    main()

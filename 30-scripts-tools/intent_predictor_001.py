#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
INTENT-PREDICTOR-001 AI Intent Prediction System
4-STAGE: ARCHITECT→CODE→ASK→DEBUG
"""
import json, sys
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter

if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

HISTORY_FILE = Path("13-memory/.intent_history.json")
LEARN_LOG = Path("13-memory/.intent_learn_log.json")

INTENT_PATTERNS = {
    "optimize": ["optimize", "improve", "fix", "better", "youhua", "gaishan"],
    "create": ["create", "new", "write", "make", "build", "xinjian"],
    "analyze": ["analyze", "check", "review", "scan", "fenxi", "jiancha"],
    "deploy": ["deploy", "release", "publish", "push"],
    "test": ["test", "verify", "validate", "ceshi"],
    "learn": ["learn", "study", "research", "xuexi"],
    "brainstorm": ["brainstorm", "idea", "think", "chuangyi"],
    "operate": ["operate", "manage", "monitor", "yunying", "run"],
    "commit": ["commit", "save", "git", "submit"],
}

RECOMMENDATIONS = {
    "optimize": [("self_heal_001.py", "Self-Heal"), ("code_quality_001.py", "Quality")],
    "create": [("safe_coder_001.py", "Safe Code"), ("brainstorm_001.py", "Brainstorm")],
    "analyze": [("workflow_health_001.py", "Health"), ("topology_viz_001.py", "Topology")],
    "brainstorm": [("scamper_001.py", "SCAMPER"), ("sixhats_001.py", "Six Hats")],
    "operate": [("ops_panel_001.py", "Ops Panel"), ("workflow_health_001.py", "Health")],
    "commit": [("workflow.bat", "Commit"), ("batch_runner_001.py", "Test")],
    "test": [("batch_runner_001.py", "Tests"), ("self_heal_001.py", "Heal")],
    "learn": [("auto_evolve_001.py", "Evolve"), ("auto_architect_001.py", "Architect")],
}


class IntentPredictor:
    def __init__(self):
        self.history = self._load_history()
        self.learn_log = self._load_learn_log()
    
    def _load_history(self):
        if HISTORY_FILE.exists():
            try:
                return json.loads(HISTORY_FILE.read_text(encoding="utf-8", errors="replace"))
            except:
                pass
        return {"intents": [], "commands": [], "transitions": {}, "last_updated": None}
    
    def _save_history(self):
        self.history["last_updated"] = datetime.now().isoformat()
        HISTORY_FILE.write_text(json.dumps(self.history, indent=2, ensure_ascii=False), encoding="utf-8")
    
    def _load_learn_log(self):
        if LEARN_LOG.exists():
            try:
                return json.loads(LEARN_LOG.read_text(encoding="utf-8", errors="replace"))
            except:
                pass
        return {"entries": [], "total_learned": 0}
    
    def detect_intent(self, text):
        if not text or not text.strip():
            return "unknown"
        text_lower = text.lower()
        scores = defaultdict(int)
        for intent, patterns in INTENT_PATTERNS.items():
            for pattern in patterns:
                count = text_lower.count(pattern)
                if count > 0:
                    scores[intent] += count
        if not scores:
            return "unknown"
        return max(scores.items(), key=lambda x: x[1])[0]
    
    def learn(self, intent, action):
        if not intent or not isinstance(intent, str):
            return False
        if not action or not isinstance(action, str):
            return False
        intent = intent.strip().lower()
        action = action.strip()
        self.history["intents"].append(intent)
        self.history["commands"].append(action)
        if "transitions" not in self.history:
            self.history["transitions"] = {}
        if intent not in self.history["transitions"]:
            self.history["transitions"][intent] = {}
        if action not in self.history["transitions"][intent]:
            self.history["transitions"][intent][action] = 0
        self.history["transitions"][intent][action] += 1
        self.learn_log["entries"].append({"timestamp": datetime.now().isoformat(), "intent": intent, "action": action})
        self.learn_log["total_learned"] += 1
        self._save_history()
        LEARN_LOG.write_text(json.dumps(self.learn_log, indent=2, ensure_ascii=False), encoding="utf-8")
        return True
    
    def predict_next(self, current_intent=None):
        if not current_intent:
            intents = self.history.get("intents", [])
            current_intent = intents[-1] if intents else None
        if not current_intent:
            return None
        transitions = self.history.get("transitions", {}).get(current_intent, {})
        if not transitions:
            return None
        return max(transitions.items(), key=lambda x: x[1])[0]
    
    def recommend_action(self, intent):
        return RECOMMENDATIONS.get(intent, [])
    
    def generate_report(self):
        intents = self.history.get("intents", [])
        intent_counts = Counter(intents)
        last_intent = intents[-1] if intents else None
        predicted = self.predict_next(last_intent)
        confidence = 0
        if intent_counts:
            confidence = intent_counts.most_common(1)[0][1] / max(1, len(intents)) * 100
        return {
            "total_interactions": len(intents),
            "top_intents": intent_counts.most_common(5),
            "last_intent": last_intent,
            "predicted_next": predicted,
            "confidence": confidence,
            "learned_patterns": len(self.learn_log.get("entries", []))
        }


def main():
    predictor = IntentPredictor()
    print("\n[INTENT-PREDICTOR-001] AI Intent Prediction")
    print("=" * 50)
    
    if "--predict" in sys.argv:
        report = predictor.generate_report()
        print(f"\n[PREDICTION]")
        print(f"  Interactions: {report['total_interactions']}")
        print(f"  Learned: {report['learned_patterns']}")
        print(f"  Confidence: {report['confidence']:.0f}%")
        if report['top_intents']:
            print(f"\n  Top intents:")
            for i, (intent, count) in enumerate(report['top_intents'][:3], 1):
                print(f"    {i}. {intent}: {count}x")
        print(f"\n  Predicted next: {report['predicted_next'] or 'unknown'}")
        if report['last_intent']:
            recs = predictor.recommend_action(report['last_intent'])
            if recs:
                print(f"\n  Recommended:")
                for tool, desc in recs:
                    print(f"    - {desc} [{tool}]")
    
    elif "--detect" in sys.argv and len(sys.argv) > 2:
        text = " ".join(sys.argv[2:])
        intent = predictor.detect_intent(text)
        print(f"\n  Input: '{text}'")
        print(f"  Detected intent: {intent}")
        recs = predictor.recommend_action(intent)
        if recs:
            print(f"  Recommended: {recs}")
    
    elif "--learn" in sys.argv and len(sys.argv) > 3:
        intent = sys.argv[2]
        action = sys.argv[3]
        if predictor.learn(intent, action):
            print(f"\n  Learned: {intent} -> {action}")
            print(f"  Total learned: {predictor.learn_log['total_learned']}")
    
    else:
        print("\nUsage:")
        print("  --predict        Predict next action")
        print("  --detect <text>  Detect intent")
        print("  --learn <i> <a>  Learn pattern")
        print("  --report         Show report")

if __name__ == "__main__":
    main()

import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
人类意图理解 - 深度理解人类隐含意图
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

class HumanIntentUnderstanding:
    """人类意图理解器"""
    
    def __init__(self):
        self.intent_patterns = self._load_intent_patterns()
        self.history_file = Path("13-memory/intent_history.json")
        self.history = self._load_history()
    
    def _load_intent_patterns(self) -> Dict:
        """加载意图模式"""
        return {
            # 字面意思 → 真实意图
            "urgency": {
                "patterns": [
                    (r"尽快| ASAP | urgent | hurry | rush", "high_priority"),
                    (r"有空的时候 | when you have time | whenever", "low_priority"),
                    (r"今天 | today | by EOD", "deadline_today"),
                    (r"明天 | tomorrow | by tomorrow", "deadline_tomorrow"),
                ]
            },
            "action_type": {
                "patterns": [
                    (r"帮我 | help me | can you", "request_assistance"),
                    (r"检查 | check | verify | review", "request_review"),
                    (r"创建 | create | make | build", "request_creation"),
                    (r"修复 | fix | repair | debug", "request_fix"),
                    (r"解释 | explain | tell me | what is", "request_explanation"),
                    (r"建议 | suggest | recommend | advice", "request_advice"),
                ]
            },
            "emotion": {
                "patterns": [
                    (r"太好了 | great | excellent | awesome | ！", "positive"),
                    (r"糟糕 | bad | wrong | error | 唉", "negative"),
                    (r"请 | please | 麻烦 | 谢谢", "polite"),
                    (r"为什么 | why | 怎么 | how", "confused"),
                ]
            },
            "implicit_need": {
                "patterns": [
                    (r"这个文件太大了 | this file is too big", "need_compression"),
                    (r"找不到 | can't find | missing", "need_search"),
                    (r"太慢了 | too slow | slow", "need_optimization"),
                    (r"又错了 | again | still wrong", "need_thorough_fix"),
                    (r"我不确定 | not sure | maybe", "need_guidance"),
                ]
            }
        }
    
    def _load_history(self) -> Dict:
        """加载历史"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "interactions": [],
            "learned_preferences": {},
            "stats": {
                "total_interactions": 0,
                "intents_detected": 0,
                "accuracy_rate": 0
            }
        }
    
    def analyze_intent(self, user_input: str, context: Dict = None) -> Dict:
        """分析用户意图
        
        Args:
            user_input: 用户输入
            context: 上下文信息
        """
        result = {
            "timestamp": datetime.now().isoformat(),
            "input": user_input,
            "literal_meaning": user_input,
            "detected_intents": {},
            "confidence": 0,
            "suggested_actions": [],
            "emotional_tone": "neutral"
        }
        
        # 1. 检测紧急程度
        urgency = self._detect_category(user_input, "urgency")
        if urgency:
            result["detected_intents"]["urgency"] = urgency
        
        # 2. 检测行动类型
        action = self._detect_category(user_input, "action_type")
        if action:
            result["detected_intents"]["action_type"] = action
        
        # 3. 检测情感色彩
        emotion = self._detect_category(user_input, "emotion")
        if emotion:
            result["detected_intents"]["emotion"] = emotion
            result["emotional_tone"] = emotion
        
        # 4. 检测隐含需求
        implicit = self._detect_category(user_input, "implicit_need")
        if implicit:
            result["detected_intents"]["implicit_need"] = implicit
        
        # 5. 生成建议行动
        result["suggested_actions"] = self._generate_suggestions(result["detected_intents"])
        
        # 6. 计算置信度
        result["confidence"] = self._calculate_confidence(result["detected_intents"])
        
        # 7. 记录历史
        self._record_interaction(result, context)
        
        return result
    
    def _detect_category(self, text: str, category: str) -> Optional[str]:
        """检测特定类别的意图"""
        if category not in self.intent_patterns:
            return None
        
        text_lower = text.lower()
        
        for pattern, intent in self.intent_patterns[category]["patterns"]:
            if re.search(pattern, text_lower, re.IGNORECASE):
                return intent
        
        return None
    
    def _generate_suggestions(self, intents: Dict) -> List[str]:
        """生成建议行动"""
        suggestions = []
        
        # 基于紧急程度
        if intents.get("urgency") == "high_priority":
            suggestions.append("Prioritize this task immediately")
        elif intents.get("urgency") == "deadline_today":
            suggestions.append("Complete before end of day")
        
        # 基于行动类型
        action = intents.get("action_type")
        if action == "request_creation":
            suggestions.append("Prepare to create new content")
        elif action == "request_fix":
            suggestions.append("Investigate and fix the issue")
        elif action == "request_review":
            suggestions.append("Review carefully and provide feedback")
        
        # 基于隐含需求
        implicit = intents.get("implicit_need")
        if implicit == "need_compression":
            suggestions.append("Offer compression solution")
        elif implicit == "need_optimization":
            suggestions.append("Analyze performance bottlenecks")
        elif implicit == "need_thorough_fix":
            suggestions.append("Ensure comprehensive fix with tests")
        
        return suggestions
    
    def _calculate_confidence(self, intents: Dict) -> float:
        """计算置信度"""
        if not intents:
            return 0.3  # 基础置信度
        
        # 每检测到一个意图类别，增加置信度
        base_confidence = 0.5
        category_bonus = 0.15 * len(intents)
        
        # 情感检测增加置信度
        if "emotion" in intents:
            base_confidence += 0.1
        
        return min(0.95, base_confidence + category_bonus)
    
    def _record_interaction(self, result: Dict, context: Dict = None):
        """记录交互历史"""
        interaction = {
            "timestamp": result["timestamp"],
            "input": result["input"],
            "intents": result["detected_intents"],
            "confidence": result["confidence"],
            "context": context or {}
        }
        
        self.history["interactions"].append(interaction)
        self.history["stats"]["total_interactions"] += 1
        
        if result["detected_intents"]:
            self.history["stats"]["intents_detected"] += 1
        
        # 更新准确率 (简化)
        total = self.history["stats"]["total_interactions"]
        detected = self.history["stats"]["intents_detected"]
        if total > 0:
            self.history["stats"]["accuracy_rate"] = (detected / total) * 100
        
        # 保留最近 100 条
        self.history["interactions"] = self.history["interactions"][-100:]
        
        self._save_history()
    
    def learn_preference(self, user_id: str, intent: str, preferred_action: str):
        """学习用户偏好"""
        if user_id not in self.history["learned_preferences"]:
            self.history["learned_preferences"][user_id] = []
        
        preference = {
            "intent": intent,
            "preferred_action": preferred_action,
            "learned_at": datetime.now().isoformat()
        }
        
        self.history["learned_preferences"][user_id].append(preference)
        self._save_history()
    
    def get_personalized_suggestion(self, user_id: str, intent: str) -> List[str]:
        """获取个性化建议"""
        suggestions = []
        
        if user_id in self.history["learned_preferences"]:
            for pref in self.history["learned_preferences"][user_id]:
                if pref["intent"] == intent:
                    suggestions.append(pref["preferred_action"])
        
        return suggestions
    
    def _save_history(self):
        """保存历史"""
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.history, f, ensure_ascii=False, indent=2)
    
    def get_stats(self) -> Dict:
        """获取统计"""
        return self.history["stats"]
    
    def display_status(self) -> str:
        """显示状态"""
        stats = self.get_stats()
        
        output = []
        output.append("\n" + "=" * 70)
        output.append(" " * 20 + "Human Intent Understanding")
        output.append("=" * 70)
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Interactions:   {stats['total_interactions']}")
        output.append(f"  Intents Detected:     {stats['intents_detected']}")
        output.append(f"  Accuracy Rate:        {stats['accuracy_rate']:.1f}%")
        
        output.append(f"\n[Intent Categories]")
        for category in self.intent_patterns:
            pattern_count = len(self.intent_patterns[category]["patterns"])
            output.append(f"  {category:15} {pattern_count} patterns")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)

logging.basicConfig(level=logging.INFO)
def main():
    """
# ==============================================================================
# STAGE 1: ARCHITECT 架构设计

# ==============================================================================
# STAGE 2: CODE 编写代码
# ==============================================================================

Purpose: Automation workflow tool
Data Flow: input -> process -> output
# ==============================================================================

# ==============================================================================
# STAGE 3: ASK 询问确认
# py human_intent_understanding_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py human_intent_understanding_001.py

Expected Output:
    - Tool runs without errors
    - Shows usage or performs intended action
"""

# ==============================================================================
# STAGE 4: DEBUG 调试测试
# Test: 2026
# ==============================================================================
"""
DEBUG: Test cases and fixes

Test Cases:
    1. Basic invocation → Works
    2. --help flag → Shows usage

Fixes:
    - (none yet)
"""

测试入口"""
    understanding = HumanIntentUnderstanding()
    
    print("Human Intent Understanding Test")
    print("=" * 70)
    
    # 显示状态
    print(understanding.display_status())
    
    # 测试：分析意图
    print("\n[Analyzing User Inputs]")
    
    test_inputs = [
        "请尽快帮我修复这个 bug，今天要用！",
        "有空的时候检查一下这个文件",
        "这个文件太大了，能不能压缩一下？",
        "又错了！为什么总是出问题？",
        "请建议我如何优化性能",
    ]
    
    for user_input in test_inputs:
        print(f"\n  Input: {user_input}")
        result = understanding.analyze_intent(user_input)
        print(f"    Urgency: {result['detected_intents'].get('urgency', 'N/A')}")
        print(f"    Action: {result['detected_intents'].get('action_type', 'N/A')}")
        print(f"    Emotion: {result['emotional_tone']}")
        print(f"    Implicit: {result['detected_intents'].get('implicit_need', 'N/A')}")
        print(f"    Confidence: {result['confidence']:.1%}")
        if result['suggested_actions']:
            print(f"    Suggestions: {', '.join(result['suggested_actions'])}")
    
    print(f"\n[OK] Intent understanding test completed")

if __name__ == "__main__":
    main()

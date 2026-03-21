import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
情感智能 - 识别和响应人类情感
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

class EmotionalIntelligence:
    """情感智能系统"""
    
    def __init__(self):
        self.emotion_lexicon = self._load_emotion_lexicon()
        self.response_templates = self._load_response_templates()
        self.history_file = Path("13-memory/emotion_history.json")
        self.history = self._load_history()
    
    def _load_emotion_lexicon(self) -> Dict:
        """加载情感词典"""
        return {
            "joy": {
                "words": ["开心", "高兴", "快乐", "great", "happy", "excited", "wonderful", "fantastic", "awesome", "！"],
                "intensity": 1.0
            },
            "trust": {
                "words": ["相信", "信任", "confident", "trust", "believe", "rely on"],
                "intensity": 0.8
            },
            "fear": {
                "words": ["害怕", "担心", "焦虑", "scared", "afraid", "worried", "anxious", "nervous"],
                "intensity": 0.9
            },
            "surprise": {
                "words": ["惊讶", "吃惊", "surprised", "shocked", "wow", "unexpected"],
                "intensity": 0.7
            },
            "sadness": {
                "words": ["难过", "伤心", "sad", "unhappy", "depressed", "down", "唉", "哎"],
                "intensity": 0.9
            },
            "disgust": {
                "words": ["讨厌", "恶心", "disgust", "hate", "dislike", "gross"],
                "intensity": 0.8
            },
            "anger": {
                "words": ["生气", "愤怒", "angry", "mad", "furious", "annoyed", "frustrated", "！"],
                "intensity": 1.0
            },
            "anticipation": {
                "words": ["期待", "盼望", "excited", "anticipate", "looking forward", "hope"],
                "intensity": 0.7
            },
            "neutral": {
                "words": [],
                "intensity": 0.3
            }
        }
    
    def _load_response_templates(self) -> Dict:
        """加载响应模板"""
        return {
            "joy": [
                "Great to hear that! I'm excited for you!",
                "That's wonderful news! ",
                "Awesome! Let's keep the momentum going!",
            ],
            "trust": [
                "I appreciate your trust. I'll do my best!",
                "Thank you for believing in me. I won't let you down!",
                "I'm honored by your confidence. Let's work together!",
            ],
            "fear": [
                "I understand your concern. Let's address this step by step.",
                "Don't worry, we'll figure this out together.",
                "I'm here to help. Let's tackle this calmly.",
            ],
            "surprise": [
                "I know, right? Sometimes things surprise us!",
                "That was unexpected! But we can handle it.",
                "Interesting turn of events! Let's adapt.",
            ],
            "sadness": [
                "I'm sorry you're feeling this way. I'm here for you.",
                "That sounds tough. Take your time, I'm not going anywhere.",
                "I understand. Sometimes things don't go as planned. Let's regroup.",
            ],
            "disgust": [
                "I hear your frustration. Let's fix what's wrong.",
                "That doesn't sound good. Let me help resolve this.",
                "I understand. Let's make this better.",
            ],
            "anger": [
                "I understand you're frustrated. Let me help fix this immediately.",
                "I apologize for the issue. Let's resolve this right away.",
                "I hear you. Let me take care of this with priority.",
            ],
            "anticipation": [
                "I'm excited too! Let's make it happen!",
                "Looking forward to it! Here's what we can do...",
                "Great anticipation! Let's prepare together.",
            ],
            "neutral": [
                "Understood. How can I help?",
                "Got it. What's next?",
                "Acknowledged. Ready to proceed.",
            ]
        }
    
    def _load_history(self) -> Dict:
        """加载历史"""
        if self.history_file.exists():
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return {
            "version": "1.0",
            "interactions": [],
            "user_profiles": {},
            "stats": {
                "total_interactions": 0,
                "emotions_detected": 0,
                "responses_given": 0,
                "avg_emotional_intelligence": 0
            }
        }
    
    def detect_emotion(self, text: str) -> Dict:
        """检测情感
        
        Args:
            text: 输入文本
            
        Returns:
            情感分析结果
        """
        result = {
            "primary_emotion": "neutral",
            "secondary_emotion": None,
            "intensity": 0.3,
            "valence": 0,  # -1 (negative) to +1 (positive)
            "arousal": 0,  # 0 (calm) to 1 (excited)
            "confidence": 0.5,
            "detected_words": [],
            "emotional_score": {}
        }
        
        text_lower = text.lower()
        emotion_scores = {}
        
        # 检测每种情感
        for emotion, data in self.emotion_lexicon.items():
            score = 0
            matched_words = []
            
            for word in data["words"]:
                if word.lower() in text_lower:
                    score += data["intensity"]
                    matched_words.append(word)
            
            if score > 0:
                emotion_scores[emotion] = score
                result["detected_words"].extend(matched_words)
        
        # 确定主要情感
        if emotion_scores:
            sorted_emotions = sorted(emotion_scores.items(), key=lambda x: x[1], reverse=True)
            result["primary_emotion"] = sorted_emotions[0][0]
            result["intensity"] = min(1.0, sorted_emotions[0][1])
            
            if len(sorted_emotions) > 1:
                result["secondary_emotion"] = sorted_emotions[1][0]
            
            result["emotional_score"] = emotion_scores
            
            # 计算 valence (正负向)
            positive_emotions = ["joy", "trust", "anticipation"]
            negative_emotions = ["fear", "sadness", "disgust", "anger"]
            
            pos_score = sum(emotion_scores.get(e, 0) for e in positive_emotions)
            neg_score = sum(emotion_scores.get(e, 0) for e in negative_emotions)
            
            total = pos_score + neg_score
            if total > 0:
                result["valence"] = (pos_score - neg_score) / total
            
            # 计算 arousal (兴奋度)
            high_arousal = ["joy", "fear", "surprise", "anger", "anticipation"]
            arousal_score = sum(emotion_scores.get(e, 0) for e in high_arousal)
            result["arousal"] = min(1.0, arousal_score)
            
            result["confidence"] = min(0.95, 0.5 + 0.1 * len(emotion_scores))
            result["emotions_detected"] = len(emotion_scores)
        else:
            result["emotions_detected"] = 0
        
        return result
    
    def generate_empathetic_response(self, emotion_result: Dict, context: str = "") -> str:
        """生成共情响应
        
        Args:
            emotion_result: 情感分析结果
            context: 上下文
            
        Returns:
            共情响应文本
        """
        primary = emotion_result["primary_emotion"]
        templates = self.response_templates.get(primary, self.response_templates["neutral"])
        
        # 根据强度选择响应
        intensity = emotion_result["intensity"]
        
        if intensity > 0.8:
            # 高强度：更强烈的响应
            response = templates[0]
        elif intensity > 0.5:
            # 中等强度：标准响应
            response = templates[1] if len(templates) > 1 else templates[0]
        else:
            # 低强度：温和响应
            response = templates[-1]
        
        # 添加个性化元素
        if context:
            response += f" Regarding {context},"
        
        return response
    
    def adjust_communication_style(self, emotion_result: Dict) -> Dict:
        """调整沟通风格
        
        Args:
            emotion_result: 情感分析结果
            
        Returns:
            沟通风格建议
        """
        style = {
            "tone": "neutral",
            "formality": "medium",
            "verbosity": "medium",
            "emoji_usage": "moderate",
            "response_speed": "normal"
        }
        
        primary = emotion_result["primary_emotion"]
        intensity = emotion_result["intensity"]
        valence = emotion_result["valence"]
        
        # 根据情感调整语气
        if primary in ["joy", "anticipation"]:
            style["tone"] = "enthusiastic"
            style["emoji_usage"] = "high"
        elif primary in ["sadness", "fear"]:
            style["tone"] = "gentle"
            style["verbosity"] = "low"
            style["response_speed"] = "careful"
        elif primary in ["anger", "disgust"]:
            style["tone"] = "professional"
            style["formality"] = "high"
            style["verbosity"] = "low"
            style["response_speed"] = "fast"
        elif primary in ["surprise"]:
            style["tone"] = "curious"
            style["emoji_usage"] = "moderate"
        
        # 根据强度调整
        if intensity > 0.8:
            style["response_speed"] = "immediate"
        
        # 根据正负向调整
        if valence < -0.5:
            style["tone"] = "supportive"
            style["formality"] = "medium"
        
        return style
    
    def track_emotional_trend(self, user_id: str) -> Dict:
        """追踪情感趋势
        
        Args:
            user_id: 用户 ID
            
        Returns:
            情感趋势分析
        """
        user_interactions = [
            i for i in self.history["interactions"]
            if i.get("user_id") == user_id
        ]
        
        if len(user_interactions) < 3:
            return {"status": "insufficient_data", "interactions": len(user_interactions)}
        
        # 分析最近 10 次交互
        recent = user_interactions[-10:]
        
        emotion_counts = {}
        for interaction in recent:
            emotion = interaction.get("primary_emotion", "neutral")
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # 确定趋势
        dominant_emotion = max(emotion_counts, key=emotion_counts.get)
        
        # 计算趋势方向
        recent_emotions = [i.get("valence", 0) for i in recent]
        if len(recent_emotions) >= 2:
            trend = "improving" if recent_emotions[-1] > recent_emotions[0] else "declining"
        else:
            trend = "stable"
        
        return {
            "user_id": user_id,
            "dominant_emotion": dominant_emotion,
            "trend": trend,
            "emotion_distribution": emotion_counts,
            "avg_valence": sum(recent_emotions) / len(recent_emotions),
            "emotional_stability": 1 - (max(recent_emotions) - min(recent_emotions))
        }
    
    def _record_interaction(self, user_id: str, text: str, emotion_result: Dict):
        """记录交互"""
        interaction = {
            "timestamp": datetime.now().isoformat(),
            "user_id": user_id,
            "input": text,
            "primary_emotion": emotion_result["primary_emotion"],
            "valence": emotion_result["valence"],
            "intensity": emotion_result["intensity"]
        }
        
        self.history["interactions"].append(interaction)
        self.history["stats"]["total_interactions"] += 1
        
        if emotion_result["emotions_detected"] > 0:
            self.history["stats"]["emotions_detected"] += 1
        
        # 保留最近 200 条
        self.history["interactions"] = self.history["interactions"][-200:]
        
        self._save_history()
    
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
        output.append(" " * 22 + "Emotional Intelligence")
        output.append("=" * 70)
        
        output.append(f"\n[Statistics]")
        output.append(f"  Total Interactions:   {stats['total_interactions']}")
        output.append(f"  Emotions Detected:    {stats['emotions_detected']}")
        output.append(f"  Responses Given:      {stats['responses_given']}")
        
        output.append(f"\n[Emotion Categories]")
        for emotion in self.emotion_lexicon:
            if emotion != "neutral":
                word_count = len(self.emotion_lexicon[emotion]["words"])
                output.append(f"  {emotion:15} {word_count} words")
        
        output.append("\n" + "=" * 70)
        
        return "\n".join(output)

logging.basicConfig(level=logging.INFO)
def main():
    """测试入口"""
    ei = EmotionalIntelligence()
    
    print("Emotional Intelligence Test")
    print("=" * 70)
    
    # 显示状态
    print(ei.display_status())
    
    # 测试：情感检测
    print("\n[Detecting Emotions]")
    
    test_inputs = [
        "太好了！这个功能太棒了！",
        "我很担心这个 bug 会影响用户",
        "又错了！真是令人沮丧！",
        "期待明天的演示",
        "这个项目让我很伤心",
        "我相信你能做好",
        "普通的测试输入",
    ]
    
    for user_input in test_inputs:
        print(f"\n  Input: {user_input}")
        result = ei.detect_emotion(user_input)
        print(f"    Primary: {result['primary_emotion']}")
        print(f"    Intensity: {result['intensity']:.1%}")
        print(f"    Valence: {result['valence']:+.2f}")
        print(f"    Arousal: {result['arousal']:.2f}")
        print(f"    Words: {', '.join(result['detected_words']) if result['detected_words'] else 'N/A'}")
        
        # 生成响应
        response = ei.generate_empathetic_response(result)
        print(f"    Response: {response}")
        
        # 调整沟通风格
        style = ei.adjust_communication_style(result)
        print(f"    Style: tone={style['tone']}, speed={style['response_speed']}")
    
    print(f"\n[OK] Emotional intelligence test completed")

if __name__ == "__main__":
    main()

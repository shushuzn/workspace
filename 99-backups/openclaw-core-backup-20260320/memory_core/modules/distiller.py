"""
蒸馏压缩模块

从原始记忆中提取核心信息，压缩存储。
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path


class DistillerModule:
    """
    记忆蒸馏器
    
    功能:
    - 提取关键点
    - 生成摘要
    - 压缩内容
    - 质量驱动的蒸馏策略
    """

    def __init__(self, config=None):
        self.config = config
        self.max_summary_length = 200
        self.max_key_points = 5

    def compress(self, raw_memory: Dict) -> Dict:
        """
        压缩记忆
        
        Args:
            raw_memory: 原始记忆字典
        
        Returns:
            压缩后的记忆字典
        """
        content = raw_memory.get('content', '')

        # 1. 清洗文本
        cleaned = self._clean_text(content)

        # 2. 提取关键点
        key_points = self._extract_key_points(cleaned)

        # 3. 生成摘要
        summary = self._generate_summary(cleaned)

        # 4. 计算压缩率
        original_length = len(content)
        compressed_length = len(summary)
        compression_rate = 1 - (compressed_length / original_length) if original_length > 0 else 0

        return {
            'content': cleaned,
            'summary': summary,
            'key_points': key_points,
            'compression_rate': compression_rate,
            'original_length': original_length,
            'compressed_length': compressed_length,
            **{k: v for k, v in raw_memory.items() if k != 'content'}
        }

    def _clean_text(self, text: str) -> str:
        """清洗文本"""
        # 移除多余空格
        text = ' '.join(text.split())

        # 移除特殊字符
        text = text.replace('\r\n', '\n').replace('\r', '\n')

        # 移除多余空行
        text = re.sub(r'\n{3,}', '\n\n', text)

        return text.strip()

    def _extract_key_points(self, text: str) -> List[str]:
        """提取关键点"""
        # 简单实现：按句子分割，选择重要句子
        sentences = re.split(r'[.!.]', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        # 选择包含关键词的句子
        keywords = ['重要', '关键', '核心', '必须', '应该', '需要', '目标', '结果']
        key_points = []

        for sentence in sentences:
            if any(kw in sentence for kw in keywords):
                key_points.append(sentence)

            if len(key_points) >= self.max_key_points:
                break

        # 如果没找到关键点，返回前几个句子
        if not key_points and sentences:
            key_points = sentences[:self.max_key_points]

        return key_points

    def _generate_summary(self, text: str) -> str:
        """生成摘要"""
        if len(text) <= self.max_summary_length:
            return text

        # 尝试在句子边界截断
        truncated = text[:self.max_summary_length - 3]
        last_period = truncated.rfind('.')

        if last_period > self.max_summary_length // 2:
            return truncated[:last_period + 1]

        return truncated + '...'

    def extract_insights(self, text: str) -> List[Dict]:
        """
        提取洞察
        
        Returns:
            洞察列表，每个洞察包含 type, content, confidence
        """
        insights = []

        # 检测决策
        decision_patterns = [
            r'决定 (.+?)',
            r'选择 (.+?)',
            r'采用 (.+?)',
        ]

        for pattern in decision_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                insights.append({
                    'type': 'decision',
                    'content': match,
                    'confidence': 0.8
                })

        # 检测学习点
        learning_patterns = [
            r'学到了 (.+?)',
            r'理解了 (.+?)',
            r'发现 (.+?)',
        ]

        for pattern in learning_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                insights.append({
                    'type': 'learning',
                    'content': match,
                    'confidence': 0.7
                })

        # 检测问题
        if '?' in text or '？' in text:
            questions = re.findall(r'(.+?[?？])', text)
            for question in questions:
                insights.append({
                    'type': 'question',
                    'content': question,
                    'confidence': 0.9
                })

        return insights

    def should_distill(self, memory: Dict) -> Tuple[bool, str]:
        """
        判断是否应该蒸馏
        
        Returns:
            (是否蒸馏，原因)
        """
        content = memory.get('content', '')
        score = memory.get('score', 0.5)

        # 高质量记忆 → 立即蒸馏
        if score >= 0.9:
            return True, "高质量记忆 (score≥0.9)"

        # 长内容 → 需要压缩
        if len(content) > 1000:
            return True, "内容过长 (>{1000 chars)"

        # 包含关键点 → 蒸馏
        if len(self._extract_key_points(content)) >= 3:
            return True, "包含多个关键点"

        return False, "不需要蒸馏"

    def distill_to_markdown(self, memory: Dict) -> str:
        """蒸馏为 Markdown 格式"""
        lines = [
            f"## {memory.get('title', '记忆片段')}",
            "",
            f"**时间:** {memory.get('timestamp', 'N/A')}",
            f"**质量:** {memory.get('score', 0.0):.2f}",
            "",
            "### 摘要",
            "",
            memory.get('summary', memory.get('content', '')),
            "",
        ]

        key_points = memory.get('key_points', [])
        if key_points:
            lines.extend([
                "### 关键点",
                "",
            ])
            for point in key_points:
                lines.append(f"- {point}")
            lines.append("")

        insights = memory.get('insights', [])
        if insights:
            lines.extend([
                "### 洞察",
                "",
            ])
            for insight in insights:
                lines.append(f"- [{insight['type']}] {insight['content']}")
            lines.append("")

        return '\n'.join(lines)

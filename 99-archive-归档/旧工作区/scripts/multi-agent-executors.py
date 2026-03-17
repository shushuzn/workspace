#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Agent Executors v1
具体执行 Agent 实现
"""

from multi-agent-framework import AgentBase, MessageBus, MessageType, Task, TaskStatus
import json
from pathlib import Path

# ==================== PDF 解析 Agent ====================

class PDFParserAgent(AgentBase):
    """PDF 解析 Agent"""
    
    def __init__(self, agent_id: str, message_bus: MessageBus):
        super().__init__(agent_id, "pdf_parser", message_bus)
        self.pdf_dir = Path(r"D:\obsidian\Vault\Arxiv\PDF")
    
    def process_message(self, message):
        if message.message_type == MessageType.TASK_ASSIGN:
            task_data = message.payload.get('task', {})
            arxiv_id = task_data.get('arxiv_id', '')
            
            print(f"  [PDF_PARSER] Parsing {arxiv_id}...")
            
            # 模拟 PDF 解析
            result = {
                'arxiv_id': arxiv_id,
                'title': f"Paper {arxiv_id}",
                'pages': 10,
                'status': 'parsed'
            }
            
            # 发送完成消息
            self.send_message(
                message.from_agent,
                MessageType.TASK_COMPLETE,
                {'task_id': task_data.get('task_id'), 'result': result}
            )

# ==================== 元数据提取 Agent ====================

class MetadataExtractorAgent(AgentBase):
    """元数据提取 Agent"""
    
    def __init__(self, agent_id: str, message_bus: MessageBus):
        super().__init__(agent_id, "metadata_extractor", message_bus)
    
    def process_message(self, message):
        if message.message_type == MessageType.TASK_ASSIGN:
            task_data = message.payload.get('task', {})
            
            print(f"  [METADATA] Extracting metadata...")
            
            # 模拟元数据提取
            result = {
                'authors': ['Author A', 'Author B'],
                'abstract': 'This paper presents...',
                'keywords': ['AI', 'ML'],
                'status': 'extracted'
            }
            
            self.send_message(
                message.from_agent,
                MessageType.TASK_COMPLETE,
                {'task_id': task_data.get('task_id'), 'result': result}
            )

# ==================== 贡献总结 Agent ====================

class ContributionSummarizerAgent(AgentBase):
    """贡献总结 Agent"""
    
    def __init__(self, agent_id: str, message_bus: MessageBus):
        super().__init__(agent_id, "contribution_summarizer", message_bus)
    
    def process_message(self, message):
        if message.message_type == MessageType.TASK_ASSIGN:
            task_data = message.payload.get('task', {})
            
            print(f"  [SUMMARIZER] Generating summary...")
            
            # 模拟贡献总结
            result = {
                'contributions': [
                    'Novel approach to...',
                    'Improved performance by...',
                    'First to demonstrate...'
                ],
                'status': 'summarized'
            }
            
            self.send_message(
                message.from_agent,
                MessageType.TASK_COMPLETE,
                {'task_id': task_data.get('task_id'), 'result': result}
            )

# ==================== 知识图谱更新 Agent ====================

class KnowledgeGraphUpdaterAgent(AgentBase):
    """知识图谱更新 Agent"""
    
    def __init__(self, agent_id: str, message_bus: MessageBus):
        super().__init__(agent_id, "knowledge_graph_updater", message_bus)
    
    def process_message(self, message):
        if message.message_type == MessageType.TASK_ASSIGN:
            task_data = message.payload.get('task', {})
            
            print(f"  [KG_UPDATER] Updating knowledge graph...")
            
            # 模拟知识图谱更新
            result = {
                'entities_added': 5,
                'relations_added': 10,
                'status': 'updated'
            }
            
            self.send_message(
                message.from_agent,
                MessageType.TASK_COMPLETE,
                {'task_id': task_data.get('task_id'), 'result': result}
            )

# ==================== 质量审核 Agent ====================

class ReviewerAgent(AgentBase):
    """质量审核 Agent"""
    
    def __init__(self, agent_id: str, message_bus: MessageBus):
        super().__init__(agent_id, "reviewer", message_bus)
    
    def process_message(self, message):
        if message.message_type == MessageType.REVIEW_REQUEST:
            task_data = message.payload.get('task', {})
            result = task_data.get('result', {})
            
            print(f"  [REVIEWER] Reviewing task...")
            
            # 简单质量检查
            passed = True
            feedback = []
            
            if not result:
                passed = False
                feedback.append("Result is empty")
            
            # 发送审核结果
            self.send_message(
                message.from_agent,
                MessageType.REVIEW_RESULT,
                {
                    'task_id': task_data.get('task_id'),
                    'passed': passed,
                    'feedback': feedback
                }
            )

# ==================== 测试 ====================

def test_agents():
    """测试 Agent"""
    print("=" * 60)
    print("Multi-Agent Executors Test")
    print("=" * 60)
    
    message_bus = MessageBus()
    
    # 创建 Agent
    agents = [
        PDFParserAgent("pdf_parser_1", message_bus),
        MetadataExtractorAgent("metadata_1", message_bus),
        ContributionSummarizerAgent("summarizer_1", message_bus),
        KnowledgeGraphUpdaterAgent("kg_updater_1", message_bus),
        ReviewerAgent("reviewer_1", message_bus),
    ]
    
    print("\n[TEST] All agents initialized")
    print(f"  Total agents: {len(agents)}")
    
    # 测试消息传递
    print("\n[TEST] Testing message passing...")
    message_bus.send_message(
        Message.create("test", "pdf_parser_1", MessageType.TASK_ASSIGN, {'test': 'data'})
    )
    
    msg = message_bus.receive_message("pdf_parser_1")
    if msg:
        print(f"  [OK] Message received: {msg.message_type.value}")
    
    print("\n" + "=" * 60)
    print("[TEST] Agent test complete!")
    print("=" * 60)

if __name__ == "__main__":
    # 需要导入 Message
    from multi-agent-framework import Message
    test_agents()

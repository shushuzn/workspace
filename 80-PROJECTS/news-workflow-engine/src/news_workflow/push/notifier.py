"""
Push Notifier - 推送通知模块

负责将工作流状态和结果推送到多渠道
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from loguru import logger


class PushNotifier:
    """推送通知器"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化推送通知器
        
        Args:
            config: 推送配置
        """
        self.config = config
        self.channels = config.get("channels", {})
        self.importance_threshold = config.get("importance_threshold", 0.8)
        self.rate_limit = config.get("rate_limit", 60)
        
        self.last_push_time = {}  # 渠道 -> 最后推送时间
        
        logger.info("PushNotifier initialized")
    
    async def send_workflow_alert(self, workflow_id: int, analysis: Dict[str, Any]):
        """
        发送工作流告警
        
        Args:
            workflow_id: 工作流 ID
            analysis: 新闻分析结果
        """
        importance = analysis.get("importance", 0)
        if importance < self.importance_threshold:
            logger.debug(f"Importance {importance} below threshold, skipping push")
            return
        
        message = self._build_workflow_message(workflow_id, analysis)
        await self._push_to_channels(message, "workflow_alert")
    
    async def send_task_result(self, task_id: int, result: Dict[str, Any]):
        """
        发送任务执行结果
        
        Args:
            task_id: 任务 ID
            result: 执行结果
        """
        message = self._build_task_result_message(task_id, result)
        await self._push_to_channels(message, "task_result")
    
    async def send_daily_summary(self, summary: Dict[str, Any]):
        """
        发送每日摘要
        
        Args:
            summary: 摘要信息
        """
        message = self._build_daily_summary_message(summary)
        await self._push_to_channels(message, "daily_summary")
    
    def _build_workflow_message(self, workflow_id: int, analysis: Dict[str, Any]) -> str:
        """构建工作流消息"""
        return f"""
🔔 **新工作流触发**

📰 新闻重要性：{analysis.get('importance', 0):.2f}
🏷️ 分类：{analysis.get('category', 'unknown')}
😊 情感：{analysis.get('sentiment', 'neutral')}
🔑 关键词：{', '.join(analysis.get('keywords', []))}

📋 工作流 ID: {workflow_id}
⏰ 时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{analysis.get('summary', '')}
"""
    
    def _build_task_result_message(self, task_id: int, result: Dict[str, Any]) -> str:
        """构建任务结果消息"""
        status = "✅" if result.get("success", False) else "❌"
        return f"""
{status} **任务执行完成**

任务 ID: {task_id}
状态：{'成功' if result.get('success', False) else '失败'}
{f"错误：{result.get('error', 'Unknown')}" if not result.get('success', False) else ''}
"""
    
    def _build_daily_summary_message(self, summary: Dict[str, Any]) -> str:
        """构建每日摘要消息"""
        return f"""
📊 **每日工作流摘要**

📰 处理新闻：{summary.get('news_count', 0)} 条
🔗 创建工作流：{summary.get('workflow_count', 0)} 个
✅ 完成任务：{summary.get('task_count', 0)} 个
⏱️ 平均执行时间：{summary.get('avg_execution_time', 0):.1f} 秒

📈 成功率：{summary.get('success_rate', 0):.1%}
"""
    
    async def _push_to_channels(self, message: str, msg_type: str):
        """推送到所有启用的渠道"""
        tasks = []
        
        for channel_name, channel_config in self.channels.items():
            if not channel_config.get("enabled", False):
                continue
            
            # 检查频率限制
            if not self._check_rate_limit(channel_name):
                logger.warning(f"Rate limit exceeded for {channel_name}")
                continue
            
            if channel_name == "feishu":
                tasks.append(self._push_to_feishu(channel_config, message))
            elif channel_name == "telegram":
                tasks.append(self._push_to_telegram(channel_config, message))
            elif channel_name == "email":
                tasks.append(self._push_to_email(channel_config, message))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    def _check_rate_limit(self, channel_name: str) -> bool:
        """检查频率限制"""
        now = datetime.now().timestamp()
        last_time = self.last_push_time.get(channel_name, 0)
        
        if now - last_time < self.rate_limit:
            return False
        
        self.last_push_time[channel_name] = now
        return True
    
    async def _push_to_feishu(self, config: Dict[str, Any], message: str):
        """推送到飞书"""
        import aiohttp
        
        webhook_url = config.get("webhook_url")
        if not webhook_url:
            logger.warning("Feishu webhook URL not configured")
            return
        
        payload = {
            "msg_type": "text",
            "content": {
                "text": message
            }
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(webhook_url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Feishu push successful")
                    else:
                        logger.error(f"Feishu push failed: {response.status}")
        except Exception as e:
            logger.error(f"Feishu push error: {e}")
    
    async def _push_to_telegram(self, config: Dict[str, Any], message: str):
        """推送到 Telegram"""
        import aiohttp
        
        bot_token = config.get("bot_token")
        chat_id = config.get("chat_id")
        
        if not bot_token or not chat_id:
            logger.warning("Telegram bot_token or chat_id not configured")
            return
        
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("Telegram push successful")
                    else:
                        logger.error(f"Telegram push failed: {response.status}")
        except Exception as e:
            logger.error(f"Telegram push error: {e}")
    
    async def _push_to_email(self, config: Dict[str, Any], message: str):
        """推送到邮件"""
        # 简化实现 - 实际应使用 SMTP
        logger.info(f"Email push (simulated): {message[:100]}...")

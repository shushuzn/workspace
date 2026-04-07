"""
Minimax AI Agent - 简单实用的 Python Agent
用法:
    from minimax_agent import Agent
    agent = Agent()
    response = agent("你好")
"""

import requests
import json
from typing import List, Dict, Optional

API_KEY = "sk-cp-zNNt30MolJOgSwdsdgA8BJbLoKmiV3Zttz_IgZkapeyjoPPq-qYFSw-XiMZIIUyeH4PTB4Y86QXu_wKR8JvmZ9PbkkMmMwDTC6QgHznXopDTl0nBZ9AQHQ8"
BASE_URL = "https://api.minimaxi.com/v1"
MODEL = "MiniMax-M2.7-highspeed"


class Agent:
    """简单的 Minimax Agent，支持多轮对话"""

    def __init__(
        self,
        system_prompt: str = "你是一个 helpful 的 AI 助手",
        model: str = MODEL,
        api_key: str = API_KEY,
        temperature: float = 0.7,
        max_history: int = 20,
    ):
        self.model = model
        self.api_key = api_key
        self.temperature = temperature
        self.system_prompt = system_prompt
        self.max_history = max_history
        self.messages: List[Dict] = []

    def __call__(self, user_input: str, stream: bool = False) -> str:
        """发送消息并获取回复"""
        # 添加用户消息
        self.messages.append({
            "role": "user",
            "content": user_input
        })

        # 保留历史（防止过长）
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

        # 调用 API
        response = self._call_api(self.messages)

        # 添加助手回复
        self.messages.append({
            "role": "assistant",
            "content": response
        })

        return response

    def _call_api(self, messages: List[Dict]) -> str:
        """调用 Minimax API"""
        url = f"{BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": self.system_prompt}] + messages,
            "temperature": self.temperature,
            "max_tokens": 2048,
        }

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            # 处理不同格式
            if "choices" in data:
                return data["choices"][0]["message"]["content"]
            elif "content" in data:
                return data["content"]
            else:
                return str(data)

        except requests.exceptions.RequestException as e:
            return f"API 请求失败: {e}"
        except (KeyError, IndexError) as e:
            return f"解析响应失败: {e}"

    def reset(self):
        """清空对话历史"""
        self.messages = []

    def history(self) -> List[Dict]:
        """获取对话历史"""
        return self.messages.copy()


# ─── 工具 Agent 版本 ───────────────────────────────────

class ToolAgent(Agent):
    """支持工具调用的 Agent"""

    def __init__(self, tools: Optional[List[Dict]] = None, **kwargs):
        super().__init__(**kwargs)
        self.tools = tools or []

    def call_tool(self, tool_name: str, args: Dict) -> str:
        """执行工具（需要子类实现具体逻辑）"""
        return f"工具 {tool_name} 未实现"

    def __call__(self, user_input: str, stream: bool = False) -> str:
        """支持工具调用的对话"""
        self.messages.append({"role": "user", "content": user_input})

        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]

        response = self._call_with_tools(self.messages)

        self.messages.append({"role": "assistant", "content": response})
        return response

    def _call_with_tools(self, messages: List[Dict]) -> str:
        """带工具调用的 API 调用"""
        url = f"{BASE_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": self.system_prompt}] + messages,
            "temperature": self.temperature,
            "max_tokens": 2048,
        }

        if self.tools:
            payload["tools"] = self.tools

        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()

            if "choices" in data:
                choice = data["choices"][0]
                if "message" in choice:
                    return choice["message"]["content"]
                elif "tool_calls" in choice:
                    # 处理工具调用
                    tool_call = choice["tool_calls"][0]
                    result = self.call_tool(
                        tool_call["function"]["name"],
                        json.loads(tool_call["function"]["arguments"])
                    )
                    self.messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "content": result
                    })
                    # 递归获取最终回复
                    return self._call_with_tools(self.messages)
            return str(data)

        except requests.exceptions.RequestException as e:
            return f"API 请求失败: {e}"
        except (KeyError, IndexError) as e:
            return f"解析响应失败: {e}"


# ─── 快速测试 ──────────────────────────────────────────

if __name__ == "__main__":
    print("=== Minimax Agent 测试 ===\n")

    # 简单对话
    agent = Agent(system_prompt="你是一个友好的助手，用简短的语言回答。")

    # 第一轮
    response = agent("你好，我叫小明")
    print(f"助手: {response}\n")

    # 第二轮（带记忆）
    response = agent("你还记得我叫什么吗？")
    print(f"助手: {response}\n")

    # 查看历史
    print(f"对话历史: {len(agent.history())} 条消息")

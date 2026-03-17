#!/usr/bin/env python3
"""
元认知子代理/总协调器 - 多子代理协同系统

角色：监控系统、最终仲裁、元进化决策
模型：qwen3.5-plus
权重：2.0 (最高)
"""

import sys
import json
import subprocess
import os
from datetime import datetime
from pathlib import Path

class MetacognitiveAgent:
    """元认知子代理/总协调器"""
    
    def __init__(self):
        self.name = "元认知"
        self.role = "监控系统、最终仲裁、元进化决策"
        self.model = "qwen3.5-plus"
        self.weight = 2.0
        self.agent_id = f"metacognitive-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.script_dir = Path(__file__).parent
    
    def orchestrate(self, task: str, context: dict) -> dict:
        """
        编排多子代理协同
        
        Args:
            task: 用户任务
            context: 上下文信息
            
        Returns:
            最终输出
        """
        agent_outputs = []
        
        # 1. 规划者
        planner_output = self._call_agent("planner", {"task": task, "context": context})
        agent_outputs.append(planner_output)
        
        # 2. 执行者
        executor_output = self._call_agent("executor", {
            "task": task,
            "plan": planner_output.get("plan", {}),
            "context": context
        })
        agent_outputs.append(executor_output)
        
        # 3. 批判者
        critic_output = self._call_agent("critic", {
            "output": executor_output,
            "context": context
        })
        agent_outputs.append(critic_output)
        
        # 4. 如果评分<85，执行者修复
        if critic_output.get("score", 100) < 85:
            executor_output = self._call_agent("executor", {
                "task": task,
                "feedback": critic_output.get("issues", []),
                "context": context
            })
            agent_outputs.append(executor_output)
            
            # 重新审查
            critic_output = self._call_agent("critic", {
                "output": executor_output,
                "context": context
            })
            agent_outputs.append(critic_output)
        
        # 5. 学习者
        learner_output = self._call_agent("learner", {
            "outputs": agent_outputs,
            "context": context
        })
        agent_outputs.append(learner_output)
        
        # 6. 协调者
        coordinator_output = self._call_agent("coordinator", {
            "agent_outputs": agent_outputs,
            "context": context
        })
        agent_outputs.append(coordinator_output)
        
        # 7. 创新者
        innovator_output = self._call_agent("innovator", {
            "outputs": agent_outputs,
            "context": context
        })
        agent_outputs.append(innovator_output)
        
        # 8. 元认知最终仲裁
        final_output = self._final_arbitration(agent_outputs, context)
        
        return final_output
    
    def _call_agent(self, agent_name: str, input_data: dict) -> dict:
        """调用子代理"""
        agent_script = self.script_dir / f"persona-agent-{agent_name}.py"
        
        if not agent_script.exists():
            return {
                "agent_name": agent_name,
                "status": "error",
                "error": f"Agent script not found: {agent_script}"
            }
        
        try:
            # 使用 py 命令 (Windows) 或 python3 (Linux/Mac)
            import shutil
            python_cmd = shutil.which("py") or shutil.which("python3") or "python"
            
            # 使用 Universal Newline Mode + 明确编码
            result = subprocess.run(
                [python_cmd, str(agent_script)],
                input=json.dumps(input_data, ensure_ascii=False).encode('utf-8'),
                capture_output=True,
                timeout=30,
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            return json.loads(result.stdout.decode('utf-8'))
        except Exception as e:
            return {
                "agent_name": agent_name,
                "status": "error",
                "error": str(e)
            }
    
    def _final_arbitration(self, outputs: list, context: dict) -> dict:
        """最终仲裁"""
        # 收集所有决策
        decisions = []
        for output in outputs:
            if "recommendation" in output:
                decisions.append(output["recommendation"])
            elif "decision" in output:
                decisions.append(output["decision"])
        
        # 加权投票
        final_decision = max(set(decisions), key=decisions.count) if decisions else "approve"
        
        result = {
            "agent_id": self.agent_id,
            "agent_name": self.name,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "all_outputs": outputs,
            "final_decision": final_decision,
            "confidence": 0.95
        }
        return result


def main():
    """主函数"""
    if len(sys.argv) > 1:
        input_data = json.loads(sys.argv[1])
    else:
        input_data = json.loads(sys.stdin.read().strip())
    
    agent = MetacognitiveAgent()
    result = agent.orchestrate(
        input_data.get("task", ""),
        input_data.get("context", {})
    )
    
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

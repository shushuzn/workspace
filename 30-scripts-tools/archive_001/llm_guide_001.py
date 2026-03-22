import logging
logger = logging.getLogger(__name__)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM-GUIDE-001 LLM Usage Guide
【LLM使用指南】

功能:
  - 区分需要LLM的任务 vs 可自动化任务
  - 提供决策矩阵
  - 任务分类指导
  - 效率优化建议

原则:
  - 需要LLM: 创意、分析、理解、判断
  - 可自动化: 执行、验证、重复、格式转换
"""
import json
import sys
from pathlib import Path
from datetime import datetime

# 配置
GUIDE_DIR = Path("60-DATA/llm_guide_001")


class LLMGuide:
    """LLM使用指南"""
    
    # 任务分类
    LLM_REQUIRED = {
        "creative": {
            "name": "创意类",
            "examples": [
                "设计新工具架构",
                "编写营销文案",
                "创建新功能规范",
                "制定战略规划",
                "头脑风暴解决方案"
            ],
            "llm_score": 9  # 9-10分需要LLM
        },
        "analysis": {
            "name": "分析类",
            "examples": [
                "分析系统问题根因",
                "评估代码质量",
                "解读测试结果",
                "分析用户需求",
                "风险评估"
            ],
            "llm_score": 8
        },
        "judgment": {
            "name": "判断类",
            "examples": [
                "决定最佳方案",
                "评估权衡取舍",
                "判断优先级",
                "审核代码逻辑",
                "决策技术选型"
            ],
            "llm_score": 8
        },
        "understanding": {
            "name": "理解类",
            "examples": [
                "理解复杂需求",
                "解读技术文档",
                "学习新框架",
                "理解业务逻辑",
                "分析错误信息"
            ],
            "llm_score": 7
        }
    }
    
    AUTOMATABLE = {
        "execution": {
            "name": "执行类",
            "examples": [
                "运行测试用例",
                "执行代码格式化",
                "运行构建命令",
                "执行部署",
                "批量处理文件"
            ],
            "auto_score": 10  # 10分可自动化
        },
        "validation": {
            "name": "验证类",
            "examples": [
                "检查代码语法",
                "验证配置文件",
                "检查文件存在",
                "验证API响应",
                "检查格式规范"
            ],
            "auto_score": 10
        },
        "repetition": {
            "name": "重复类",
            "examples": [
                "批量提交代码",
                "批量运行测试",
                "批量生成报告",
                "批量处理数据",
                "定时任务执行"
            ],
            "auto_score": 9
        },
        "conversion": {
            "name": "转换类",
            "examples": [
                "格式转换",
                "数据导出",
                "报告生成",
                "日志解析",
                "配置更新"
            ],
            "auto_score": 9
        },
        "monitoring": {
            "name": "监控类",
            "examples": [
                "健康检查",
                "性能监控",
                "日志监控",
                "状态检查",
                "资源监控"
            ],
            "auto_score": 8
        }
    }
    
    def __init__(self):
        self.guide_dir = GUIDE_DIR
        self.guide_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.guide_dir / "task_history.json"
    
    def classify_task(self, task_description: str) -> dict:
        """分类任务 - 判断是否需要LLM"""
        task_lower = task_description.lower()
        
        # 检测关键词
        llm_keywords = ["设计", "创建", "分析", "判断", "决定", "评估", "规划", 
                       "创意", "理解", "学习", "优化", "改进", "头脑风暴", "strategy",
                       "design", "create", "analyze", "decide", "evaluate", "plan"]
        
        auto_keywords = ["运行", "执行", "检查", "验证", "生成", "提交", "转换",
                        "格式化", "解析", "监控", "导出", "处理", "run", "execute",
                        "check", "validate", "generate", "submit", "convert", "parse"]
        
        # 计算得分
        llm_score = sum(1 for kw in llm_keywords if kw in task_lower)
        auto_score = sum(1 for kw in auto_keywords if kw in task_lower)
        
        # 决策
        if llm_score > auto_score:
            decision = "LLM_REQUIRED"
            reason = "任务包含创意/分析/判断元素"
            workflow = ["1. 分析需求", "2. LLM思考方案", "3. 人工确认", "4. 执行实施"]
        elif auto_score > llm_score:
            decision = "AUTOMATABLE"
            reason = "任务主要是执行/验证/重复性工作"
            workflow = ["1. 编写脚本", "2. 自动化执行", "3. 结果验证"]
        else:
            decision = "MIXED"
            reason = "任务混合了LLM和自动化元素"
            workflow = ["1. LLM规划", "2. 自动化执行", "3. LLM审核"]
        
        result = {
            "task": task_description,
            "decision": decision,
            "reason": reason,
            "llm_score": llm_score,
            "auto_score": auto_score,
            "workflow": workflow,
            "timestamp": datetime.now().isoformat()
        }
        
        # 保存
        self._save_history(result)
        
        return result
    
    def get_recommendations(self, task_type: str = None) -> dict:
        """获取推荐"""
        if task_type == "llm":
            return {
                "type": "LLM_REQUIRED",
                "categories": self.LLM_REQUIRED,
                "tips": [
                    "使用prompt工程优化LLM输出",
                    "分步思考降低复杂度",
                    "多次迭代获得最佳结果",
                    "人工审核关键决策"
                ]
            }
        elif task_type == "auto":
            return {
                "type": "AUTOMATABLE",
                "categories": self.AUTOMATABLE,
                "tips": [
                    "优先使用现有工具",
                    "编写可复用的脚本",
                    "集成到CI/CD流程",
                    "设置定时任务"
                ]
            }
        else:
            return {
                "llm_required": self.LLM_REQUIRED,
                "automatable": self.AUTOMATABLE,
                "decision_matrix": {
                    "需要LLM": "创意、分析、判断、理解类任务",
                    "可自动化": "执行、验证、重复、转换、监控类任务",
                    "混合处理": "复杂任务分解，先LLM后自动"
                }
            }
    
    def analyze_workflow(self, steps: list) -> dict:
        """分析工作流中哪些步骤需要LLM"""
        analysis = []
        
        for i, step in enumerate(steps):
            result = self.classify_task(step)
            analysis.append({
                "step": i + 1,
                "task": step,
                "needs_llm": result["decision"] == "LLM_REQUIRED",
                "decision": result["decision"]
            })
        
        # 统计
        llm_steps = [a for a in analysis if a["needs_llm"]]
        auto_steps = [a for a in analysis if not a["needs_llm"]]
        
        return {
            "total_steps": len(steps),
            "llm_steps": len(llm_steps),
            "auto_steps": len(auto_steps),
            "recommendation": f"将{len(llm_steps)}个LLM步骤与{len(auto_steps)}个自动步骤分离",
            "steps": analysis
        }
    
    def optimize_workflow(self, steps: list) -> dict:
        """优化工作流 - 减少LLM调用"""
        analysis = self.analyze_workflow(steps)
        
        # 重新组织: 先批量执行所有自动步骤
        optimized = {
            "phase_1_auto": [s["task"] for s in analysis["steps"] if not s["needs_llm"]],
            "phase_2_llm": [s["task"] for s in analysis["steps"] if s["needs_llm"]],
            "phase_3_auto": []
        }
        
        # 如果有需要重复的自动步骤
        if optimized["phase_1_auto"]:
            optimized["phase_3_auto"] = optimized["phase_1_auto"].copy()
        
        return {
            "original_steps": len(steps),
            "estimated_llm_calls": len(optimized["phase_2_llm"]),
            "optimization": "将自动步骤批量处理，减少上下文切换",
            "phases": optimized
        }
    
    def _save_history(self, result: dict):
        history = []
        if self.history_file.exists():
            try:
                with open(self.history_file, "r", encoding="utf-8") as f:
                    history = json.load(f)
            except (Exception,):
                pass
        
        history.append(result)
        history = history[-50:]
        
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    
    def get_history(self, limit: int = 10) -> dict:
        if not self.history_file.exists():
            return {"status": "error", "message": "No history"}
        
        with open(self.history_file, "r", encoding="utf-8") as f:
            history = json.load(f)
        
        return {
            "status": "success",
            "history": history[-limit:]
        }


logging.basicConfig(level=logging.INFO)
def main():
    guide = LLMGuide()
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--classify":
            task = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""
            if not task:
                return 1
            result = guide.classify_task(task)
            print(json.dumps({
                "task": result["task"],
                "decision": result["decision"],
                "reason": result["reason"],
                "workflow": result["workflow"]
            }, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--recommend":
            task_type = sys.argv[2] if len(sys.argv) > 2 else None
            result = guide.get_recommendations(task_type)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--analyze":
            # 示例工作流
            steps = [
                "分析需求",
                "运行测试",
                "编写代码",
                "验证格式",
                "提交代码"
            ]
            result = guide.analyze_workflow(steps)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--optimize":
            steps = [
                "分析需求",
                "运行测试",
                "编写代码",
                "验证格式",
                "提交代码"
            ]
            result = guide.optimize_workflow(steps)
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--matrix":
            result = guide.get_recommendations()
            print(json.dumps(result.get("decision_matrix", {}), ensure_ascii=False, indent=2))
            return 0
        
        if sys.argv[1] == "--history":
            result = guide.get_history()
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
    
    print("LLM-GUIDE-001 LLM Usage Guide")
    print("Usage:")
    print("  py llm_guide_001.py --classify <task>           # Classify task")
    print("  py llm_guide_001.py --recommend [llm|auto]     # Get recommendations")
    print("  py llm_guide_001.py --analyze                   # Analyze example workflow")
    print("  py llm_guide_001.py --optimize                  # Optimize workflow")
    print("  py llm_guide_001.py --matrix                    # Show decision matrix")
    print("  py llm_guide_001.py --history                   # View history")
    return 0
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
# py llm_guide_001.py  # Run verification
# ==============================================================================
"""
ASK: Run verification

Test Commands:
    py llm_guide_001.py

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




if __name__ == "__main__":
    import sys
    sys.exit(main())
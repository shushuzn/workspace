#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Brainstorm Facilitator - 头脑风暴引导工具
特色：时间盒控制、双环迭代、状态追踪

总流程：发散环 (30 分钟) → 收敛环 (25 分钟) → 迭代 (最多 3 轮)
总时间：≤90 分钟
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path

# 导入发散和收敛工具
sys.path.insert(0, str(Path(__file__).parent))
from brainstorm_divergent import DivergentBrainstorm
from brainstorm_convergent import ConvergentBrainstorm


class BrainstormFacilitator:
    """头脑风暴引导工具 - 控制双环迭代流程"""
    
    def __init__(self, topic, max_iterations=3, time_limit_divergent=30, time_limit_convergent=25):
        """
        初始化引导工具
        
        Args:
            topic: 头脑风暴主题
            max_iterations: 最大迭代轮数 (默认 3)
            time_limit_divergent: 发散环时间限制 (分钟，默认 30)
            time_limit_convergent: 收敛环时间限制 (分钟，默认 25)
        """
        self.topic = topic
        self.max_iterations = max_iterations
        self.time_limit_divergent = time_limit_divergent
        self.time_limit_convergent = time_limit_convergent
        
        self.current_iteration = 0
        self.all_ideas = []
        self.all_results = []
        self.session_start = datetime.now()
    
    def time_box(self, step_name, minutes):
        """时间盒控制 - 显示倒计时"""
        print(f"\n{'⏱️ ' * 20}")
        print(f"⏱️  {step_name}: {minutes}分钟")
        print(f"{'⏱️ ' * 20}")
        
        # 简单倒计时显示
        start = time.time()
        elapsed = 0
        while elapsed < minutes * 60:
            elapsed = time.time() - start
            remaining = max(0, minutes * 60 - elapsed)
            mins = int(remaining // 60)
            secs = int(remaining % 60)
            print(f"\r   剩余时间：{mins:02d}:{secs:02d}", end='', flush=True)
            time.sleep(1)
        
        print(f"\n   时间到！")
    
    def run_divergent_ring(self, iteration):
        """运行发散环"""
        print(f"\n{'='*60}")
        print(f"第{iteration}轮 - 发散环 (Divergent Ring)")
        print(f"{'='*60}")
        
        divergent = DivergentBrainstorm(
            topic=self.topic,
            time_limit=self.time_limit_divergent
        )
        
        # 生成输出文件名
        output_dir = Path("flow-archive/20260318-universal-workflow-001")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"divergent-ring-{iteration}-{datetime.now().strftime('%H%M%S')}.json"
        
        result = divergent.run(output_file)
        
        # 保存结果
        self.all_results.append({
            'iteration': iteration,
            'ring': 'divergent',
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        # 累积想法
        self.all_ideas.extend(result.get('ideas', []))
        
        return result
    
    def run_convergent_ring(self, iteration, divergent_file):
        """运行收敛环"""
        print(f"\n{'='*60}")
        print(f"第{iteration}轮 - 收敛环 (Convergent Ring)")
        print(f"{'='*60}")
        
        convergent = ConvergentBrainstorm(divergent_file)
        
        # 生成输出文件名
        output_dir = Path("flow-archive/20260318-universal-workflow-001")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"convergent-ring-{iteration}-{datetime.now().strftime('%H%M%S')}.json"
        
        result = convergent.run(output_file)
        
        # 保存结果
        self.all_results.append({
            'iteration': iteration,
            'ring': 'convergent',
            'result': result,
            'timestamp': datetime.now().isoformat()
        })
        
        return result
    
    def should_continue(self, top_ideas):
        """判断是否需要继续迭代"""
        # 如果已经有≥3 个高质量想法，可以结束
        if len(top_ideas) >= 3:
            print(f"\n已收集{len(top_ideas)}个高质量想法，可以结束")
            return False
        
        # 如果达到最大迭代次数，必须结束
        if self.current_iteration >= self.max_iterations - 1:
            print(f"\n已达到最大迭代次数 ({self.max_iterations})")
            return False
        
        # 否则继续
        print(f"\n想法不足，继续第{self.current_iteration + 2}轮迭代")
        return True
    
    def generate_final_report(self):
        """生成最终报告"""
        print(f"\n{'='*60}")
        print(f"生成最终报告")
        print(f"{'='*60}")
        
        # 汇总所有 Top 想法
        all_top_ideas = []
        for result in self.all_results:
            if result['ring'] == 'convergent':
                top_ideas = result['result'].get('top_ideas', [])
                all_top_ideas.extend(top_ideas)
        
        # 去重 (基于想法文本)
        seen = set()
        unique_ideas = []
        for idea in all_top_ideas:
            idea_text = str(idea.get('idea', ''))
            if idea_text not in seen:
                seen.add(idea_text)
                unique_ideas.append(idea)
        
        # 按评分排序
        sorted_ideas = sorted(
            unique_ideas,
            key=lambda x: x.get('scores', {}).get('average', 0),
            reverse=True
        )
        
        # 生成报告
        final_report = {
            "topic": self.topic,
            "session_start": self.session_start.isoformat(),
            "session_end": datetime.now().isoformat(),
            "total_iterations": self.current_iteration + 1,
            "max_iterations": self.max_iterations,
            "total_ideas_generated": len(self.all_ideas),
            "final_top_ideas": sorted_ideas[:10],  # Top 10
            "all_results": self.all_results,
            "statistics": {
                "ideas_per_iteration": [
                    len([r for r in self.all_results if r['iteration'] == i and r['ring'] == 'divergent'])
                    for i in range(1, self.current_iteration + 2)
                ]
            }
        }
        
        # 保存报告
        output_dir = Path("flow-archive/20260318-universal-workflow-001")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / f"brainstorm-final-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.json"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        print(f"最终报告已保存：{output_file}")
        print(f"总想法数：{len(self.all_ideas)}")
        print(f"最终 Top 想法：{len(sorted_ideas)}")
        
        return final_report
    
    def run_session(self):
        """运行完整头脑风暴会话"""
        print(f"\n{'#'*60}")
        print(f"# 头脑风暴会话 - {self.topic}")
        print(f"# 最大迭代：{self.max_iterations}轮")
        print(f"# 预计时间：{self.max_iterations * (self.time_limit_divergent + self.time_limit_convergent)}分钟")
        print(f"{'#'*60}")
        
        session_start = time.time()
        
        while self.current_iteration < self.max_iterations:
            iteration = self.current_iteration + 1
            print(f"\n{'='*60}")
            print(f"开始第{iteration}轮迭代")
            print(f"{'='*60}")
            
            # 发散环
            divergent_result = self.run_divergent_ring(iteration)
            divergent_file = None
            # 获取发散环输出文件
            for result in self.all_results:
                if result['iteration'] == iteration and result['ring'] == 'divergent':
                    divergent_file = result['result']
                    break
            
            # 收敛环
            if divergent_file:
                convergent_result = self.run_convergent_ring(iteration, divergent_file)
                
                # 判断是否继续
                top_ideas = convergent_result.get('top_ideas', [])
                if not self.should_continue(top_ideas):
                    break
            
            self.current_iteration += 1
        
        # 生成最终报告
        final_report = self.generate_final_report()
        
        session_elapsed = time.time() - session_start
        print(f"\n{'='*60}")
        print(f"头脑风暴会话完成!")
        print(f"总用时：{session_elapsed:.1f} 秒 ({session_elapsed/60:.1f} 分钟)")
        print(f"{'='*60}")
        
        return final_report


def main():
    """主函数"""
    topic = sys.argv[1] if len(sys.argv) > 1 else "AI agent autonomy"
    max_iterations = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    
    facilitator = BrainstormFacilitator(
        topic=topic,
        max_iterations=max_iterations
    )
    
    result = facilitator.run_session()
    
    print(f"\n会话完成:")
    print(f"  总迭代轮数：{result['total_iterations']}")
    print(f"  总想法数：{result['total_ideas_generated']}")
    print(f"  最终 Top 想法：{len(result['final_top_ideas'])}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Multi-Objective Optimizer - CPU Optimized
多目标优化器 (CPU 优化版)

功能：
1. NSGA-II 算法实现
2. Pareto 前沿计算
3. 多目标材料优化
4. CPU 优化，严格控制使用率

作者：Claw (AI Research OS)
创建时间：2026-03-05 21:15
"""

import os
import json
import time
import math
import random
from typing import List, Dict, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from collections import deque
import threading

# ============================================================================
# 1. CPU 保护配置
# ============================================================================

@dataclass
class CPUConfig:
    """CPU 保护配置"""
    intra_op_threads: int = 4
    inter_op_threads: int = 2
    max_concurrent: int = 1
    cpu_threshold: float = 70.0
    population_size: int = 50


# ============================================================================
# 2. CPU 监控
# ============================================================================

class CPUMonitor:
    """CPU 使用监控器"""
    
    def __init__(self, threshold: float = 70.0):
        self.threshold = threshold
        self.history = deque(maxlen=10)
        self.lock = threading.Lock()
    
    def get_cpu_percent(self) -> float:
        try:
            import psutil
            return psutil.cpu_percent(interval=0.1)
        except:
            return 0.0
    
    def should_wait(self) -> bool:
        current = self.get_cpu_percent()
        with self.lock:
            self.history.append(current)
            if current > self.threshold:
                return True
            if len(self.history) >= 5:
                avg = sum(self.history) / len(self.history)
                if avg > self.threshold * 0.9:
                    return True
        return False
    
    def wait_if_needed(self, timeout: float = 5.0):
        start = time.time()
        while self.should_wait():
            if time.time() - start > timeout:
                break
            time.sleep(0.5)


# ============================================================================
# 3. 数据结构
# ============================================================================

@dataclass
class Individual:
    """个体"""
    genes: List[float]  # 基因 (材料描述符)
    objectives: List[float] = field(default_factory=list)  # 目标值
    rank: int = 0  # Pareto 等级
    crowding_distance: float = 0.0  # 拥挤距离
    
    def __lt__(self, other):
        if self.rank != other.rank:
            return self.rank < other.rank
        return self.crowding_distance > other.crowding_distance


@dataclass
class ParetoFront:
    """Pareto 前沿"""
    solutions: List[Individual]
    n_objectives: int
    
    def to_dict(self) -> Dict:
        return {
            'n_solutions': len(self.solutions),
            'n_objectives': self.n_objectives,
            'objectives': [ind.objectives for ind in self.solutions]
        }


# ============================================================================
# 4. NSGA-II 优化器
# ============================================================================

class NSGA2Optimizer:
    """NSGA-II 多目标优化器"""
    
    def __init__(self, config: CPUConfig = None):
        self.config = config or CPUConfig()
        self.monitor = CPUMonitor(self.config.cpu_threshold)
        
        # 优化参数
        self.n_vars = 10  # 变量数
        self.n_objs = 2   # 目标数
        self.pop_size = self.config.population_size
        self.n_generations = 50
        self.crossover_rate = 0.9
        self.mutation_rate = 0.1
        
        # 种群
        self.population = []
        self.pareto_front = None
        
        # 设置环境变量
        os.environ['OMP_NUM_THREADS'] = str(self.config.intra_op_threads)
        os.environ['MKL_NUM_THREADS'] = str(self.config.intra_op_threads)
    
    def initialize_population(self) -> List[Individual]:
        """初始化种群"""
        population = []
        
        for _ in range(self.pop_size):
            genes = [random.uniform(0, 1) for _ in range(self.n_vars)]
            individual = Individual(genes=genes)
            population.append(individual)
        
        return population
    
    def evaluate(self, individual: Individual, 
                 objectives_funcs: List[callable]):
        """评估个体"""
        individual.objectives = [func(individual.genes) 
                                 for func in objectives_funcs]
    
    def fast_non_dominated_sort(self, population: List[Individual]):
        """快速非支配排序"""
        
        for ind in population:
            ind.domination_count = 0
            ind.dominated_solutions = []
            ind.rank = 0
        
        for i in range(len(population)):
            for j in range(i + 1, len(population)):
                if self._dominates(population[i], population[j]):
                    population[i].dominated_solutions.append(j)
                    population[j].domination_count += 1
                elif self._dominates(population[j], population[i]):
                    population[j].dominated_solutions.append(i)
                    population[i].domination_count += 1
        
        fronts = []
        
        # 第一层前沿 (支配计数为 0)
        first_front = [ind for ind in population if ind.domination_count == 0]
        if first_front:
            for ind in first_front:
                ind.rank = 0
            fronts.append(first_front)
        
        current_front_idx = 0
        
        while current_front_idx < len(fronts):
            next_front = []
            for ind in fronts[current_front_idx]:
                for j in ind.dominated_solutions:
                    population[j].domination_count -= 1
                    if population[j].domination_count == 0:
                        population[j].rank = current_front_idx + 1
                        next_front.append(population[j])
            if next_front:
                fronts.append(next_front)
            current_front_idx += 1
        
        return fronts
    
    def _dominates(self, ind1: Individual, ind2: Individual) -> bool:
        """判断 ind1 是否支配 ind2"""
        better_in_one = False
        not_worse_in_all = True
        
        for o1, o2 in zip(ind1.objectives, ind2.objectives):
            if o1 > o2:  # 最大化问题
                better_in_one = True
            elif o1 < o2:
                not_worse_in_all = False
        
        return better_in_one and not_worse_in_all
    
    def calculate_crowding_distance(self, front: List[Individual]):
        """计算拥挤距离"""
        
        if len(front) <= 2:
            for ind in front:
                ind.crowding_distance = float('inf')
            return
        
        n_objs = len(front[0].objectives)
        
        for ind in front:
            ind.crowding_distance = 0.0
        
        for m in range(n_objs):
            front_sorted = sorted(front, key=lambda ind: ind.objectives[m])
            front_sorted[0].crowding_distance = float('inf')
            front_sorted[-1].crowding_distance = float('inf')
            
            obj_range = (front_sorted[-1].objectives[m] - 
                        front_sorted[0].objectives[m])
            
            if obj_range == 0:
                continue
            
            for i in range(1, len(front_sorted) - 1):
                front_sorted[i].crowding_distance += (
                    front_sorted[i + 1].objectives[m] - 
                    front_sorted[i - 1].objectives[m]
                ) / obj_range
    
    def tournament_selection(self, population: List[Individual]) -> Individual:
        """锦标赛选择"""
        i = random.randint(0, len(population) - 1)
        j = random.randint(0, len(population) - 1)
        
        if i == j:
            return population[i]
        
        if population[i] < population[j]:
            return population[i]
        return population[j]
    
    def crossover(self, parent1: Individual, 
                  parent2: Individual) -> Tuple[Individual, Individual]:
        """模拟二进制交叉 (SBX)"""
        
        if random.random() > self.crossover_rate:
            return parent1, parent2
        
        child1_genes = []
        child2_genes = []
        
        for i in range(self.n_vars):
            if random.random() < 0.5:
                if abs(parent1.genes[i] - parent2.genes[i]) > 1e-14:
                    if parent1.genes[i] < parent2.genes[i]:
                        y1, y2 = parent1.genes[i], parent2.genes[i]
                    else:
                        y1, y2 = parent2.genes[i], parent1.genes[i]
                    
                    eta = 2.0
                    beta = 1.0 + (2.0 * (y1 - 0.0) / (y2 - y1))
                    alpha = 2.0 - beta ** (-(eta + 1))
                    rand = random.random()
                    
                    if rand <= 1.0 / alpha:
                        betaq = (rand * alpha) ** (1.0 / (eta + 1))
                    else:
                        betaq = (1.0 / (2.0 - rand * alpha)) ** (1.0 / (eta + 1))
                    
                    c1 = 0.5 * ((y1 + y2) - betaq * (y2 - y1))
                    c2 = 0.5 * ((y1 + y2) + betaq * (y2 - y1))
                    
                    child1_genes.append(max(0.0, min(1.0, c1)))
                    child2_genes.append(max(0.0, min(1.0, c2)))
                else:
                    child1_genes.append(parent1.genes[i])
                    child2_genes.append(parent2.genes[i])
            else:
                child1_genes.append(parent2.genes[i])
                child2_genes.append(parent1.genes[i])
        
        return (Individual(genes=child1_genes), 
                Individual(genes=child2_genes))
    
    def mutate(self, individual: Individual) -> Individual:
        """多项式变异"""
        
        mutated_genes = []
        
        for i in range(self.n_vars):
            if random.random() < self.mutation_rate:
                eta = 20.0
                gene = individual.genes[i]
                
                if random.random() < 0.5:
                    delta = gene - 0.0
                    if delta > 0:
                        rand = random.random()
                        deltaq = rand ** (1.0 / (eta + 1)) - 1.0
                    else:
                        deltaq = 0.0
                else:
                    delta = 1.0 - gene
                    if delta > 0:
                        rand = random.random()
                        deltaq = 1.0 - rand ** (1.0 / (eta + 1))
                    else:
                        deltaq = 0.0
                
                mutated_genes.append(max(0.0, min(1.0, gene + deltaq)))
            else:
                mutated_genes.append(individual.genes[i])
        
        return Individual(genes=mutated_genes)
    
    def optimize(self, objectives_funcs: List[callable], 
                 n_generations: Optional[int] = None) -> ParetoFront:
        """执行多目标优化"""
        
        if n_generations:
            self.n_generations = n_generations
        
        print(f"\n[NSGA-II] 开始优化...")
        print(f"  种群大小：{self.pop_size}")
        print(f"  代数：{self.n_generations}")
        print(f"  目标数：{self.n_objs}")
        
        # 初始化
        self.population = self.initialize_population()
        
        # 评估初始种群
        for ind in self.population:
            self.evaluate(ind, objectives_funcs)
        
        # 进化
        for gen in range(self.n_generations):
            # 检查 CPU
            self.monitor.wait_if_needed(timeout=5.0)
            
            # 创建子代
            children = []
            
            while len(children) < self.pop_size:
                parent1 = self.tournament_selection(self.population)
                parent2 = self.tournament_selection(self.population)
                
                child1, child2 = self.crossover(parent1, parent2)
                child1 = self.mutate(child1)
                child2 = self.mutate(child2)
                
                children.extend([child1, child2])
            
            children = children[:self.pop_size]
            
            # 评估子代
            for child in children:
                self.evaluate(child, objectives_funcs)
            
            # 合并
            combined = self.population + children
            
            # 非支配排序
            fronts = self.fast_non_dominated_sort(combined)
            
            # 选择下一代
            new_population = []
            front_idx = 0
            
            while (len(new_population) + len(fronts[front_idx]) <= self.pop_size 
                   and front_idx < len(fronts)):
                self.calculate_crowding_distance(fronts[front_idx])
                new_population.extend(fronts[front_idx])
                front_idx += 1
            
            if len(new_population) < self.pop_size and front_idx < len(fronts):
                self.calculate_crowding_distance(fronts[front_idx])
                fronts[front_idx].sort()
                remaining = self.pop_size - len(new_population)
                new_population.extend(fronts[front_idx][:remaining])
            
            self.population = new_population
            
            # 打印进度
            if (gen + 1) % 10 == 0:
                pareto = self._get_pareto_front()
                print(f"  代数 {gen + 1}/{self.n_generations}, "
                      f"Pareto 解数：{len(pareto)}")
            
            # 代间休息
            time.sleep(0.05)
        
        # 获取最终 Pareto 前沿
        pareto_list = self._get_pareto_front()
        self.pareto_front = ParetoFront(solutions=pareto_list, n_objectives=self.n_objs)
        
        print(f"\n[NSGA-II] 优化完成！")
        print(f"  Pareto 前沿解数：{len(self.pareto_front.solutions)}")
        
        return self.pareto_front
    
    def _get_pareto_front(self) -> List[Individual]:
        """获取 Pareto 前沿"""
        fronts = self.fast_non_dominated_sort(self.population)
        if fronts:
            return fronts[0]
        return []
    
    def get_stats(self) -> Dict:
        """获取统计"""
        if not self.pareto_front:
            return {'optimized': False}
        
        return {
            'optimized': True,
            'n_solutions': len(self.pareto_front.solutions) if self.pareto_front else 0,
            'n_objectives': self.n_objs,
            'current_cpu': self.monitor.get_cpu_percent()
        }


# ============================================================================
# 5. 材料多目标优化
# ============================================================================

class MaterialMultiObjectiveOptimizer:
    """材料多目标优化器"""
    
    def __init__(self, config: CPUConfig = None):
        self.config = config or CPUConfig()
        self.nsga2 = NSGA2Optimizer(config)
    
    def create_objective_functions(self, targets: Dict[str, float]) -> List[callable]:
        """创建目标函数"""
        
        objectives = []
        
        # 带隙目标
        if 'band_gap' in targets:
            target_bg = targets['band_gap']
            def obj_band_gap(genes):
                pred_bg = 1.0 + sum(genes[:3]) * 2
                return -abs(pred_bg - target_bg)  # 负值表示接近
            objectives.append(obj_band_gap)
        
        # 形成能目标
        if 'formation_energy' in targets:
            target_fe = targets['formation_energy']
            def obj_formation(genes):
                pred_fe = -3.0 - sum(genes[3:6]) * 2
                return -abs(pred_fe - target_fe)
            objectives.append(obj_formation)
        
        # 体积模量目标
        if 'bulk_modulus' in targets:
            target_bm = targets['bulk_modulus']
            def obj_bulk(genes):
                pred_bm = 50 + sum(genes[6:9]) * 50
                return -abs(pred_bm - target_bm)
            objectives.append(obj_bulk)
        
        # 稳定性目标
        def obj_stability(genes):
            return -sum(genes[9:]) * 0.5  # 越小越稳定
        objectives.append(obj_stability)
        
        return objectives
    
    def optimize(self, targets: Dict[str, float], 
                n_generations: int = 30) -> ParetoFront:
        """优化材料"""
        
        print(f"\n[材料优化] 多目标优化...")
        print(f"  目标：{targets}")
        
        # 创建目标函数
        objectives = self.create_objective_functions(targets)
        self.nsga2.n_objs = len(objectives)
        
        # 执行优化
        pareto = self.nsga2.optimize(objectives, n_generations)
        
        return pareto
    
    def select_solution(self, pareto: ParetoFront, 
                       preferences: Optional[Dict[str, float]] = None) -> Individual:
        """从 Pareto 前沿选择解"""
        
        if not pareto.solutions:
            return None
        
        if not preferences:
            # 返回中间解
            return pareto.solutions[len(pareto.solutions) // 2]
        
        # 根据偏好选择
        best_score = -float('inf')
        best_sol = None
        
        for sol in pareto.solutions:
            score = 0.0
            for i, (obj_name, weight) in enumerate(preferences.items()):
                if i < len(sol.objectives):
                    score += sol.objectives[i] * weight
            if score > best_score:
                best_score = score
                best_sol = sol
        
        return best_sol


# ============================================================================
# 6. 全局实例
# ============================================================================

_optimizer_instance = None

def get_multiobj_optimizer(config: CPUConfig = None):
    """获取多目标优化器单例"""
    global _optimizer_instance
    
    if _optimizer_instance is None:
        _optimizer_instance = MaterialMultiObjectiveOptimizer(config)
    
    return _optimizer_instance


# ============================================================================
# 7. 主函数 (测试)
# ============================================================================

def main():
    """主函数"""
    print("=" * 60)
    print("Multi-Objective Optimizer - CPU Optimized")
    print("=" * 60)
    
    # 1. 创建优化器
    print("\n[1/4] 创建优化器...")
    config = CPUConfig(
        intra_op_threads=4,
        inter_op_threads=2,
        max_concurrent=1,
        cpu_threshold=70.0,
        population_size=30
    )
    
    optimizer = get_multiobj_optimizer(config)
    
    # 2. 多目标优化
    print("\n[2/4] 多目标优化...")
    targets = {
        'band_gap': 3.0,
        'formation_energy': -3.0,
        'bulk_modulus': 150
    }
    
    pareto = optimizer.optimize(targets, n_generations=20)
    
    # 3. 选择解
    print("\n[3/4] 选择最优解...")
    
    preferences = {
        'band_gap': 0.4,
        'formation_energy': 0.3,
        'bulk_modulus': 0.3
    }
    
    best = optimizer.select_solution(pareto, preferences)
    
    if best:
        print(f"  最优解目标值：{best.objectives}")
        print(f"  Pareto 前沿解数：{len(pareto.solutions)}")
    
    # 4. 统计
    print("\n[4/4] 统计信息...")
    stats = optimizer.nsga2.get_stats()
    
    print(f"  已优化：{'✅' if stats.get('optimized') else '❌'}")
    print(f"  解数：{stats.get('n_solutions', 0)}")
    print(f"  目标数：{stats.get('n_objectives', 0)}")
    print(f"  当前 CPU: {stats.get('current_cpu', 0):.1f}%")
    
    print("\n" + "=" * 60)
    print("多目标优化器准备完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()

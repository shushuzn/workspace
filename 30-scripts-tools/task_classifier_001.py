"""
任务分类器 v1.0
用途：根据任务复杂度分类，决定使用简化版还是完整版 workflow
"""

# 简单任务关键词（Q&A/查询）
SIMPLE_KEYWORDS = [
    '什么是', '解释', '原则', '概念', '定义',
    'what is', 'explain', 'principle', 'concept', 'definition',
    '状态', '检查', '查看', '查询',
    'status', 'check', 'view', 'query',
    '为什么', 'why', '如何', 'how',
    '简单', '快速', 'brief', 'quick'
]

# 标准任务关键词（工具开发/功能实现）
STANDARD_KEYWORDS = [
    '创建', '实现', '开发', '工具', '功能',
    'create', 'implement', 'develop', 'tool', 'feature',
    'sa-', 'phase', '分析', '优化',
    'analyze', 'optimize'
]

# 复杂任务关键词（大型项目）
COMPLEX_KEYWORDS = [
    '部署', '研究', '项目', '系统', '架构',
    'deploy', 'research', 'project', 'system', 'architecture',
    '重构', '迁移', '集成',
    'refactor', 'migrate', 'integrate'
]


def classify_task(task: str) -> str:
    """
    分类任务为 'simplified', 'standard', 或 'full'
    
    Args:
        task: 任务描述字符串
        
    Returns:
        'simplified', 'standard', 或 'full'
    """
    task_lower = task.lower()
    
    # 计算各类型关键词匹配数
    simple_score = sum(1 for kw in SIMPLE_KEYWORDS if kw.lower() in task_lower)
    standard_score = sum(1 for kw in STANDARD_KEYWORDS if kw.lower() in task_lower)
    complex_score = sum(1 for kw in COMPLEX_KEYWORDS if kw.lower() in task_lower)
    
    # 选择最高分的类型
    scores = {
        'simplified': simple_score,
        'standard': standard_score,
        'full': complex_score
    }
    
    # 返回最高分的类型
    return max(scores, key=scores.get)


def get_workflow_for_task(task: str) -> str:
    """
    根据任务返回对应的 workflow ID
    
    Returns:
        workflow file path
    """
    task_type = classify_task(task)
    
    if task_type == 'simplified':
        return 'flow-archive/20260318-universal-workflow-001-simplified/workflow.json'
    else:
        return 'flow-archive/20260318-universal-workflow-001/workflow.json'


if __name__ == '__main__':
    # 测试
    test_cases = [
        ("最小权限原则", "simplified"),
        ("什么是 Python", "simplified"),
        ("创建新技能", "full"),
        ("修复 bug", "full"),
        ("检查状态", "simplified"),
        ("实现自动防护", "full"),
    ]
    
    print("任务分类器测试:\n")
    for task, expected in test_cases:
        result = classify_task(task)
        status = "OK" if result == expected else "FAIL"
        print(f"  [{status}] '{task}' -> {result} (expected: {expected})")

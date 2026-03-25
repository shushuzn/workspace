"""
任务分类器 v1.0
用途：根据任务复杂度分类，决定使用简化版还是完整版 workflow
"""

SIMPLE_KEYWORDS = [
    '什么是', '解释', '原则', '概念', '定义',
    'what is', 'explain', 'principle', 'concept', 'definition',
    '状态', '检查', '查看', '查询',
    'status', 'check', 'view', 'query',
    '为什么', 'why', '如何', 'how',
    '简单', '快速', 'brief', 'quick'
]

COMPLEX_KEYWORDS = [
    '创建', '实现', '开发', '构建', '部署',
    'create', 'implement', 'develop', 'build', 'deploy',
    '分析', '研究', '调查', '优化', '重构',
    'analyze', 'research', 'investigate', 'optimize', 'refactor',
    '修复', '调试', '测试', '集成', '迁移',
    'fix', 'debug', 'test', 'integrate', 'migrate'
]


def classify_task(task: str) -> str:
    """
    分类任务为 'simplified' 或 'full'
    
    Args:
        task: 任务描述字符串
        
    Returns:
        'simplified' 或 'full'
    """
    task_lower = task.lower()

    # 计算简单和复杂关键词的匹配数
    simple_score = sum(1 for kw in SIMPLE_KEYWORDS if kw.lower() in task_lower)
    complex_score = sum(1 for kw in COMPLEX_KEYWORDS if kw.lower() in task_lower)

    # 如果复杂关键词更多，使用完整 workflow
    if complex_score > simple_score:
        return 'full'

    # 如果简单关键词更多或相等，使用简化 workflow
    return 'simplified'


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

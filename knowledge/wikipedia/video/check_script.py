"""
视频文案质量门禁：检查禁用词、专业术语解释、字数
用法：python check_script.py <speech.txt>
"""
import sys
import re
from pathlib import Path

# 禁用词（学术腔 / 模糊词）
FORBIDDEN = [
    "本论文", "本文", "该论文", "研究表明",
    "本质上是",
]
# 合法搭配（不报警）
FORBIDDEN_OK = ["关键节点", "核心洞察", "没有明显"]

# 专业术语：格式 "术语:解释"
TECH_TERMS = {
    "谷极化": "电子在二维材料能量山谷中的分布偏好",
    "二维材料": "只有一个原子层厚的材料",
    "自旋": "电子的量子旋转属性",
    "Ising超导体": "具有强自旋轨道耦合的超导材料",
    "TMDC": "过渡金属硫族化合物，二维半导体材料",
    "Andreev反射": "超导体与普通导体界面处的量子效应",
    "热电效应": "温差产生电压的现象",
    "电流整流": "电流单向流动的特性",
    "辫群": "描述编织动作的数学结构",
    "Burau表示": "将辫群转化为矩阵的数学方法",
    "特权升级": "从低权限账号提升到高权限的过程",
    "IAM": "身份与访问管理，云系统的权限控制",
    "阿贝尔": "运算顺序无关的数学特性",
    "LE指数": "Burau-Lyapunov指数，量化系统危险程度",
    "Burau-Lyapunov": "来自辫群理论的危险程度指标",
    "拓扑结构": "描述连接关系的几何特性",
}

MIN_TOTAL = 500
MAX_TOTAL = 1500


def check_forbidden(text):
    found = []
    for w in FORBIDDEN:
        if w in text:
            # 检查是否在白名单合法搭配中
            ok = False
            for ok_pattern in FORBIDDEN_OK:
                if w in ok_pattern and ok_pattern in text:
                    ok = True
                    break
            if not ok:
                found.append(w)
    return found


def check_terms(text):
    """检查核心术语是否有通俗解释"""
    # 核心需要解释的词：纯术语无上下文
    core_terms = ["Andreev反射", "Burau表示", "LE指数", "Burau-Lyapunov"]
    problems = []
    for term in core_terms:
        if term in text:
            # 找这行有没有解释（括号、"叫"、"是"、"也就是"）
            context_match = re.search(rf"{re.escape(term)}.*?(?:（[^）]+）|叫|是|也就是|——)", text)
            if not context_match:
                problems.append(term)
    return problems


def main():
    if len(sys.argv) < 2:
        print("用法: python check_script.py <speech.txt>")
        exit(1)

    path = Path(sys.argv[1])
    text = path.read_text(encoding="utf-8")

    errors = []
    warnings = []

    # 禁用词（error）
    forbidden = check_forbidden(text)
    if forbidden:
        errors.append(f"禁用词: {', '.join(forbidden)}")

    # 总字数（warning）
    total = len(text.replace("\n", ""))
    if total < MIN_TOTAL:
        warnings.append(f"字数不足: {total} < {MIN_TOTAL}")
    elif total > MAX_TOTAL:
        warnings.append(f"字数偏多: {total} > {MAX_TOTAL}")

    # 术语解释（warning）
    unexplained = check_terms(text)
    if unexplained:
        warnings.append(f"术语未解释: {', '.join(unexplained[:5])}")

    # 输出
    if errors:
        print(f"[ERROR] {'; '.join(errors)}")
    if warnings:
        print(f"[WARN] {'; '.join(warnings)}")
    if not errors and not warnings:
        print(f"[OK] {path.name} ({total} 字)")

    return len(errors) == 0


if __name__ == "__main__":
    ok = main()
    sys.exit(0 if ok else 1)

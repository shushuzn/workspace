#!/usr/bin/env python3
"""
学科学术段位评价系统 v2.0
- 从零开始渐进式
- 每级 10000 XP
- 每个段位 1000 级

使用:
    python domain_ranker_v2.py --evaluate LIG
    python domain_ranker_v2.py --compare LIG Graphene DeepLearning
"""

import argparse
import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional

# 设置 UTF-8 编码 (Windows 兼容)
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


# 段位定义 v2.0 (每个段位 1000 级)
RANKS_V2 = [
    ("黑铁", 0, 1000, "[IRON]"),
    ("青铜", 1000, 2000, "[BRONZE]"),
    ("白银", 2000, 3000, "[SILVER]"),
    ("黄金", 3000, 4000, "[GOLD]"),
    ("铂金", 4000, 5000, "[PLAT]"),
    ("钻石", 5000, 6000, "[DIAM]"),
    ("大师", 6000, 7000, "[MASTER]"),
    ("宗师", 7000, 8000, "[GRAND]"),
]

XP_PER_LEVEL = 10000  # 每级所需经验


@dataclass
class DomainDataV2:
    """学科/领域数据 v2.0"""
    name: str
    theory_xp: float  # 0-10000
    technology_xp: float  # 0-10000
    impact_xp: float  # 0-10000
    application_xp: float  # 0-10000
    talent_xp: float  # 0-10000
    funding_xp: float  # 0-10000
    # 新增维度 v2.1
    innovation_xp: float  # 0-10000 创新能力
    collaboration_xp: float  # 0-10000 国际合作
    education_xp: float  # 0-10000 教育普及
    open_source_xp: float  # 0-10000 开源贡献
    industry_xp: float  # 0-10000 产业转化

    @classmethod
    def from_collector(cls, domain_name: str, data_file: Path) -> Optional['DomainDataV2']:
        """从 domain_data_collector 的 JSON 输出加载数据"""
        if not data_file.exists():
            return None

        try:
            with open(data_file, 'r', encoding='utf-8-sig') as f:
                data = json.load(f)

            # 映射收集器字段到 DomainDataV2
            return cls(
                name=domain_name,
                theory_xp=data.get('theory', {}).get('xp', 500),
                technology_xp=data.get('technology', {}).get('xp', 500),
                impact_xp=data.get('impact', {}).get('xp', 500),
                application_xp=data.get('application', {}).get('xp', 500),
                talent_xp=data.get('talent', {}).get('xp', 500),
                funding_xp=data.get('funding', {}).get('xp', 500),
                innovation_xp=data.get('innovation', {}).get('xp', 500),
                collaboration_xp=data.get('collaboration', {}).get('xp', 500),
                education_xp=data.get('education', {}).get('xp', 500),
                open_source_xp=data.get('open_source', {}).get('xp', 500),
                industry_xp=data.get('industry', {}).get('xp', 500)
            )
        except Exception as e:
            print(f"⚠️ 无法加载收集器数据：{e}")
            return None


class DomainRankerV2:
    """学科学术段位评价器 v2.0"""

    def __init__(self):
        # 权重配置 v3.0 (11 个维度 - 纯自动化可测量)
        # 所有维度必须可通过 API/爬虫/脚本自动获取数据，无需人工参与
        self.weights = {
            # 核心维度 (60%)
            'theory': 0.15,         # 理论基础 - 自动统计教科书/综述数量
            'technology': 0.15,     # 技术成熟度 - 自动分析专利/TRL
            'impact': 0.12,         # 学术影响力 - 自动爬取引用/论文数
            'application': 0.10,    # 应用广度 - 自动统计应用领域数量
            'talent': 0.08,         # 人才储备 - 自动统计作者/研究组数
            'funding': 0.05,        # 资金投入 - 自动爬取基金数据
            # 新增维度 (40%)
            'innovation': 0.10,     # 创新能力 - 自动分析专利新颖性
            'collaboration': 0.08,  # 国际合作 - 自动分析跨国合作论文
            'education': 0.08,      # 教育普及 - 自动统计课程/科普文章数
            'open_source': 0.07,    # 开源贡献 - 自动爬取 GitHub/PyPI
            'industry': 0.07        # 产业转化 - 自动统计公司/产品数
        }

    def calculate_score(self, domain: DomainDataV2) -> Tuple[int, int, str, int, int, int]:
        """
        计算段位分数 v2.0
        
        返回:
            (总 XP, 总分，段位名称，段位内等级，当前 XP，升级需 XP)
        """
        # 加权总经验 (0-10000) v2.1
        weighted_xp = (
            domain.theory_xp * self.weights['theory'] +
            domain.technology_xp * self.weights['technology'] +
            domain.impact_xp * self.weights['impact'] +
            domain.application_xp * self.weights['application'] +
            domain.talent_xp * self.weights['talent'] +
            domain.funding_xp * self.weights['funding'] +
            domain.innovation_xp * self.weights['innovation'] +
            domain.collaboration_xp * self.weights['collaboration'] +
            domain.education_xp * self.weights['education'] +
            domain.open_source_xp * self.weights['open_source'] +
            domain.industry_xp * self.weights['industry']
        )

        # 转换为 1-8000 分
        total_score = int(weighted_xp / 10000 * 8000)
        total_score = max(1, min(8000, total_score))

        # 总经验
        total_xp = int(weighted_xp * 8)

        # 确定段位
        rank_name, level, xp_current, xp_needed = self.score_to_rank(total_score)

        return total_xp, total_score, rank_name, level, xp_current, xp_needed

    def score_to_rank(self, score: int) -> Tuple[str, int, int, int]:
        """分数转换为段位 v2.0"""
        for rank_name, min_score, max_score, emoji in RANKS_V2:
            if min_score < score <= max_score:
                level = score - min_score
                xp_current = level * XP_PER_LEVEL
                xp_needed = XP_PER_LEVEL
                return rank_name, level, xp_current, xp_needed
        return "宗师", 1000, 10000000, 10000000

    def get_rank_info(self, score: int) -> Dict:
        """获取段位详细信息"""
        rank_name, level, xp_current, xp_needed = self.score_to_rank(score)

        # 找到当前段位信息
        for r_name, min_s, max_s, emoji in RANKS_V2:
            if r_name == rank_name:
                progress = level / 1000 * 100
                next_rank = None
                for i, (name, _, _, _) in enumerate(RANKS_V2):
                    if name == rank_name and i < len(RANKS_V2) - 1:
                        next_rank = RANKS_V2[i + 1][0]
                        break

                points_to_next = 1000 - level

                return {
                    'rank': rank_name,
                    'level': level,
                    'emoji': emoji,
                    'progress': progress,
                    'next_rank': next_rank,
                    'points_to_next': points_to_next,
                    'xp_current': xp_current,
                    'xp_needed': xp_needed,
                    'total_xp': level * XP_PER_LEVEL
                }

        return {}

    def compare_domains(self, domains: Dict[str, DomainDataV2]) -> List[Dict]:
        """比较多个领域"""
        results = []

        for name, data in domains.items():
            total_xp, score, rank, level, xp_current, xp_needed = self.calculate_score(data)
            rank_info = self.get_rank_info(score)

            results.append({
                'name': name,
                'total_xp': total_xp,
                'score': score,
                'rank': rank,
                'level': level,
                'rank_info': rank_info,
                'scores': {
                    'theory': data.theory_xp,
                    'technology': data.technology_xp,
                    'impact': data.impact_xp,
                    'application': data.application_xp,
                    'talent': data.talent_xp,
                    'funding': data.funding_xp
                }
            })

        # 按总分排序
        results.sort(key=lambda x: x['score'], reverse=True)

        return results

    def print_ranking(self, results: List[Dict]):
        """打印排名结果 v2.0"""
        print("\n" + "=" * 80)
        print("学科学术段位排名 v2.0 (从零开始渐进式)")
        print("=" * 80)
        print(f"{'排名':<4} {'领域':<20} {'段位':<15} {'分数':<8} {'经验进度':<30}")
        print("-" * 80)

        for i, result in enumerate(results, 1):
            rank_info = result['rank_info']
            emoji = rank_info.get('emoji', '[?]')
            progress_bar = self._create_progress_bar(rank_info.get('progress', 0), length=20)
            xp_text = f"{rank_info.get('xp_current', 0):,} / {rank_info.get('xp_needed', 10000):,}"

            print(f"{i:<4} {result['name']:<20} {emoji} {result['rank']} {result['level']:<4} {result['score']:<8} {progress_bar} {xp_text}")

        print("=" * 80)

    def _create_progress_bar(self, progress: float, length: int = 20) -> str:
        """创建进度条"""
        filled = int(progress / 100 * length)
        bar = "#" * filled + "-" * (length - filled)
        return f"[{bar}] {progress:.1f}%"

    def generate_recommendations(self, domain: DomainDataV2) -> List[str]:
        """生成晋升建议 v2.1 (11 维度)"""
        total_xp, score, rank, level, xp_current, xp_needed = self.calculate_score(domain)
        recommendations = []

        # 找出最弱的维度 (11 个)
        scores = {
            '理论基础': domain.theory_xp,
            '技术成熟度': domain.technology_xp,
            '学术影响力': domain.impact_xp,
            '应用广度': domain.application_xp,
            '人才储备': domain.talent_xp,
            '资金投入': domain.funding_xp,
            '创新能力': domain.innovation_xp,
            '国际合作': domain.collaboration_xp,
            '教育普及': domain.education_xp,
            '开源贡献': domain.open_source_xp,
            '产业转化': domain.industry_xp
        }

        sorted_scores = sorted(scores.items(), key=lambda x: x[1])

        # 生成建议
        for dim, xp in sorted_scores[:5]:  # 最弱的 5 个维度
            if xp < 500:
                recommendations.append(f"[CRITICAL] 优先提升{dim} (当前{xp:.0f}/10000) - 亟需改进")
            elif xp < 700:
                recommendations.append(f"[URGENT] 重点加强{dim} (当前{xp:.0f}/10000) - 需要提升")
            elif xp < 800:
                recommendations.append(f"[FOCUS] 继续加强{dim} (当前{xp:.0f}/10000) - 稳步发展")
            else:
                recommendations.append(f"[OK] 保持优势{dim} (当前{xp:.0f}/10000) - 领域领先")

        return recommendations


# 预定义领域数据 v3.0 (11 个维度，XP: 0-10000) - 纯自动化可测量
# 所有维度数据必须可通过脚本/API/爬虫自动获取，无需人工参与
PREDEFINED_DOMAINS_V2 = {
    # 材料科学
    'LIG': DomainDataV2(
        name='激光诱导石墨烯',
        # 核心维度 (60%)
        theory_xp=600,      # [自动] 教科书章节数×10 + 综述论文数×5
        technology_xp=550,  # [自动] 专利数/10 + TRL 评分×100
        impact_xp=650,      # [自动] 年发文数×2 + 年引用数/100
        application_xp=700, # [自动] 应用领域数×100 + 产品数×50
        talent_xp=500,      # [自动] 作者数/10 + 研究组数×10
        funding_xp=450,     # [自动] 基金金额 (万美元)/100
        # 新增维度 (40%) - 纯自动化指标
        innovation_xp=700,  # [自动] 新颖专利占比×10 + 突破性论文数×20
        collaboration_xp=500, # [自动] 跨国合作论文数×5 + 国际机构数×20
        education_xp=400,   # [自动] 在线课程数×50 + 科普文章数×10
        open_source_xp=500, # [自动] GitHub Stars/100 + PyPI 下载数/1000
        industry_xp=450     # [自动] 相关公司数×20 + 商业化产品数×50
    ),
    'Graphene': DomainDataV2(
        name='石墨烯',
        theory_xp=850,      # 理论完整
        technology_xp=700,  # 部分商业化
        impact_xp=900,      # 高引用
        application_xp=750, # 多领域应用
        talent_xp=800,      # 大量研究组
        funding_xp=750,     # 高投入
        innovation_xp=850,  # 诺奖级创新
        collaboration_xp=800, # 全球合作
        education_xp=700,   # 教材收录
        open_source_xp=600, # 部分开源
        industry_xp=650     # 产业应用
    ),
    'Perovskite': DomainDataV2(
        name='钙钛矿太阳能电池',
        theory_xp=700,      # 理论发展中
        technology_xp=650,  # 效率提升中
        impact_xp=750,      # 中等引用
        application_xp=600, # 能源领域
        talent_xp=600,      # 中等规模
        funding_xp=650,     # 清洁能源投入
        innovation_xp=750,  # 效率记录刷新
        collaboration_xp=600, # 国际合作
        education_xp=500,   # 专业教育
        open_source_xp=400, # 较少开源
        industry_xp=500     # 产业化初期
    ),
    'MOF': DomainDataV2(
        name='金属有机框架',
        theory_xp=750,      # 理论较完整
        technology_xp=600,  # 应用探索中
        impact_xp=700,      # 高引用
        application_xp=650, # 多领域应用
        talent_xp=550,      # 中等规模
        funding_xp=550,     # 中等投入
        innovation_xp=800,  # 结构创新
        collaboration_xp=650, # 国际合作
        education_xp=450,   # 研究生教育
        open_source_xp=500, # 部分开源
        industry_xp=400     # 产业化初期
    ),

    # 人工智能
    'DeepLearning': DomainDataV2(
        name='深度学习',
        theory_xp=750,      # 理论发展中
        technology_xp=850,  # 广泛应用
        impact_xp=950,      # 超高引用
        application_xp=900, # 基础设施级
        talent_xp=850,      # 大量人才
        funding_xp=800,     # 巨头投入
        innovation_xp=900,  # 快速发展
        collaboration_xp=850, # 全球合作
        education_xp=800,   # 课程普及
        open_source_xp=900, # TensorFlow/PyTorch
        industry_xp=850     # 大规模应用
    ),
    'LLM': DomainDataV2(
        name='大语言模型',
        theory_xp=700,      # 理论发展中
        technology_xp=800,  # 快速应用
        impact_xp=900,      # 超高引用
        application_xp=850, # 快速普及
        talent_xp=800,      # 人才争夺
        funding_xp=900,     # 巨额投入
        innovation_xp=850,  # 快速发展
        collaboration_xp=700, # 竞争激烈
        education_xp=600,   # 新兴课程
        open_source_xp=750, # LLaMA 等
        industry_xp=800     # 快速落地
    ),
    'ReinforcementLearning': DomainDataV2(
        name='强化学习',
        theory_xp=800,      # 理论较完整
        technology_xp=700,  # 部分应用
        impact_xp=800,      # 高引用
        application_xp=750, # 游戏/机器人
        talent_xp=650,      # 专业人才
        funding_xp=700,     # 中等投入
        innovation_xp=850,  # AlphaGo 等
        collaboration_xp=700, # 国际合作
        education_xp=650,   # 研究生课程
        open_source_xp=800, # Gym 等
        industry_xp=600     # 应用探索
    ),

    # 生物技术
    'CRISPR': DomainDataV2(
        name='CRISPR 基因编辑',
        theory_xp=800,      # 诺奖级理论
        technology_xp=750,  # 临床应用中
        impact_xp=850,      # 高影响力
        application_xp=700, # 医疗应用
        talent_xp=650,      # 专业研究组
        funding_xp=700,     # 生物制药投入
        innovation_xp=950,  # 诺奖级创新
        collaboration_xp=700, # 国际合作
        education_xp=600,   # 研究生教育
        open_source_xp=500, # 部分开源
        industry_xp=600     # 生物技术应用
    ),
    'mRNA': DomainDataV2(
        name='mRNA 疫苗技术',
        theory_xp=850,      # 理论成熟
        technology_xp=850,  # 新冠疫苗验证
        impact_xp=900,      # 超高影响力
        application_xp=750, # 疫苗/治疗
        talent_xp=700,      # 专业人才
        funding_xp=850,     # 大量投入
        innovation_xp=900,  # 诺奖级
        collaboration_xp=750, # 国际合作
        education_xp=650,   # 专业教育
        open_source_xp=400, # 专利保护
        industry_xp=800     # 大规模生产
    ),
    'SyntheticBiology': DomainDataV2(
        name='合成生物学',
        theory_xp=700,      # 理论发展中
        technology_xp=650,  # 工程化探索
        impact_xp=700,      # 中等引用
        application_xp=600, # 生物制造
        talent_xp=550,      # 新兴领域
        funding_xp=650,     # 中等投入
        innovation_xp=800,  # 人工细胞等
        collaboration_xp=600, # 国际合作
        education_xp=500,   # 新兴课程
        open_source_xp=600, # BioBricks
        industry_xp=500     # 产业化初期
    ),

    # 量子技术
    'QuantumComputing': DomainDataV2(
        name='量子计算',
        theory_xp=850,      # 理论完整
        technology_xp=600,  # 原型机阶段
        impact_xp=800,      # 高引用
        application_xp=500, # 早期应用
        talent_xp=600,      # 稀缺人才
        funding_xp=800,     # 大量投入
        innovation_xp=900,  # 量子霸权
        collaboration_xp=700, # 国际合作
        education_xp=550,   # 专业教育
        open_source_xp=650, # Qiskit 等
        industry_xp=450     # 产业化早期
    ),

    # 能源技术
    'NuclearFusion': DomainDataV2(
        name='核聚变能源',
        theory_xp=900,      # 理论完整
        technology_xp=500,  # 实验阶段
        impact_xp=700,      # 中等引用
        application_xp=300, # 尚未商用
        talent_xp=500,      # 专业团队
        funding_xp=700,     # 长期投入
        innovation_xp=850,  # 点火突破
        collaboration_xp=800, # ITER 等
        education_xp=500,   # 核工程专业
        open_source_xp=300, # 封闭为主
        industry_xp=350     # 商业化早期
    ),

    # 信息技术
    'Blockchain': DomainDataV2(
        name='区块链',
        theory_xp=650,      # 理论发展中
        technology_xp=700,  # 部分应用
        impact_xp=750,      # 高引用
        application_xp=650, # 金融/供应链
        talent_xp=600,      # 专业人才
        funding_xp=700,     # 创投活跃
        innovation_xp=750,  # 智能合约等
        collaboration_xp=650, # 开源社区
        education_xp=500,   # 新兴课程
        open_source_xp=850, # 高度开源
        industry_xp=600     # 金融应用
    ),
    '5G': DomainDataV2(
        name='5G 通信',
        theory_xp=850,      # 标准完成
        technology_xp=800,  # 大规模部署
        impact_xp=800,      # 高影响力
        application_xp=750, # 多领域应用
        talent_xp=700,      # 专业人才
        funding_xp=850,     # 巨额投入
        innovation_xp=750,  # 标准创新
        collaboration_xp=800, # 3GPP 标准
        education_xp=650,   # 通信专业
        open_source_xp=500, # 部分开源
        industry_xp=800     # 大规模商用
    ),

    # 机器人技术
    'Robotics': DomainDataV2(
        name='机器人技术',
        theory_xp=750,      # 理论发展中
        technology_xp=750,  # 工业应用
        impact_xp=700,      # 中等引用
        application_xp=800, # 工业/服务
        talent_xp=650,      # 专业人才
        funding_xp=700,     # 中等投入
        innovation_xp=800,  # 人形机器人
        collaboration_xp=700, # 国际合作
        education_xp=650,   # 机器人专业
        open_source_xp=700, # ROS 等
        industry_xp=750     # 工业应用
    )
}


def find_latest_collected_data(domain: str) -> Optional[Path]:
    """查找最新的领域收集数据文件"""
    workspace = Path(__file__).parent.parent
    reports_dir = workspace / "21-reports"

    if not reports_dir.exists():
        return None

    # 查找匹配的文件：LIG-domain-data-*.json
    pattern = f"{domain}-domain-data-*.json"
    files = list(reports_dir.glob(pattern))

    if not files:
        return None

    # 按修改时间排序，返回最新的
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return files[0]


def main():
    parser = argparse.ArgumentParser(description="学科学术段位评价系统 v2.0")
    parser.add_argument("--evaluate", type=str, nargs="+",
                        help="评估指定领域 (如：LIG Graphene)")
    parser.add_argument("--compare", action="store_true",
                        help="比较所有预定义领域")
    parser.add_argument("--export", type=str,
                        help="导出结果到 JSON 文件")
    parser.add_argument("--use-collected", action="store_true",
                        help="优先使用收集器数据 (而非硬编码)")
    args = parser.parse_args()

    ranker = DomainRankerV2()

    if args.evaluate:
        # 评估指定领域
        domains_to_eval = {}
        for name in args.evaluate:
            # 优先尝试加载收集器数据
            collected_data = None
            if args.use_collected or True:  # 默认使用收集器数据
                data_file = find_latest_collected_data(name)
                if data_file:
                    print(f"📊 加载收集器数据：{data_file.name}")
                    collected_data = DomainDataV2.from_collector(name, data_file)

            if collected_data:
                domains_to_eval[name] = collected_data
            elif name in PREDEFINED_DOMAINS_V2:
                print(f"⚠️ 未找到收集器数据，使用预定义数据：{name}")
                domains_to_eval[name] = PREDEFINED_DOMAINS_V2[name]
            else:
                print(f"[WARN] 未知领域：{name}，使用默认数据")
                domains_to_eval[name] = DomainDataV2(
                    name=name,
                    theory_xp=500,
                    technology_xp=500,
                    impact_xp=500,
                    application_xp=500,
                    talent_xp=500,
                    funding_xp=500,
                    innovation_xp=500,
                    collaboration_xp=500,
                    education_xp=500,
                    open_source_xp=500,
                    industry_xp=500
                )

        results = ranker.compare_domains(domains_to_eval)
        ranker.print_ranking(results)

        # 生成建议
        for name in args.evaluate:
            domain_data = domains_to_eval.get(name)
            if domain_data:
                print(f"\n[REPORT] {name} 晋升建议:")
                recs = ranker.generate_recommendations(domain_data)
                for rec in recs:
                    print(f"  {rec}")

    elif args.compare:
        # 比较所有预定义领域
        results = ranker.compare_domains(PREDEFINED_DOMAINS_V2)
        ranker.print_ranking(results)

    else:
        # 默认显示所有领域
        print("学科学术段位评价系统 v2.0")
        print("=" * 80)
        print("\n使用示例:")
        print("  python domain_ranker_v2.py --evaluate LIG")
        print("  python domain_ranker_v2.py --compare")
        print("\n预定义领域:")
        for name, data in PREDEFINED_DOMAINS_V2.items():
            total_xp, score, rank, level, xp_current, xp_needed = ranker.calculate_score(data)
            print(f"  - {name}: {rank} {level}级 ({score}/8000) - {xp_current:,}/{xp_needed:,} XP")

    return 0


if __name__ == "__main__":
    exit(main())

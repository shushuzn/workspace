#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Level 0: Quality Control
质量控制层

@version: 2.0
@author: AI Research OS
@license: MIT
"""

import os
import json
import hashlib
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QualityController:
    """质量控制器"""

    def __init__(self):
        self.input_dir = Path(r"D:\obsidian\Vault\Arxiv\daily")
        self.output_dir = Path(r"D:\obsidian\Vault\Arxiv\daily")

    def validate_papers(self, papers: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """验证论文数据"""
        valid_papers = []
        invalid_papers = []
        seen_ids = set()

        for paper in papers:
            issues = []

            # 检查必填字段
            required_fields = ['arxiv_id', 'title', 'abstract']
            for field in required_fields:
                if field not in paper:
                    issues.append(f"Missing field: {field}")

            # 检查 arxiv_id 格式
            if 'arxiv_id' in paper:
                if not self._validate_arxiv_id(paper['arxiv_id']):
                    issues.append(f"Invalid arxiv_id format: {paper['arxiv_id']}")

            # 检查标题长度
            if 'title' in paper and len(paper['title']) < 10:
                issues.append("Title too short")

            # 检查摘要
            if 'abstract' in paper and len(paper['abstract']) < 50:
                issues.append("Abstract too short")

            # 检查重复
            if 'arxiv_id' in paper:
                if paper['arxiv_id'] in seen_ids:
                    issues.append("Duplicate paper")
                else:
                    seen_ids.add(paper['arxiv_id'])

            if issues:
                paper['validation_issues'] = issues
                invalid_papers.append(paper)
            else:
                paper['validation_status'] = 'valid'
                valid_papers.append(paper)

        return valid_papers, invalid_papers

    def _validate_arxiv_id(self, arxiv_id: str) -> bool:
        """验证 arXiv ID 格式"""
        # 格式：YYMM.NNNNN 或 arXiv:YYMM.NNNNN
        import re
        pattern = r'^(arXiv:)?\d{4}\.\d{4,5}$'
        return bool(re.match(pattern, arxiv_id))

    def detect_anomalies(self, papers: List[Dict]) -> List[Dict]:
        """检测异常数据"""
        anomalies = []

        # 统计特征
        title_lengths = [len(p.get('title', '')) for p in papers]
        abstract_lengths = [len(p.get('abstract', '')) for p in papers]

        # 计算统计量
        import statistics
        if title_lengths:
            title_mean = statistics.mean(title_lengths)
            title_stdev = statistics.stdev(title_lengths) if len(title_lengths) > 1 else 0

            # 检测异常标题长度
            for paper in papers:
                title_len = len(paper.get('title', ''))
                if title_len < title_mean - 2 * title_stdev or title_len > title_mean + 2 * title_stdev:
                    anomalies.append({
                        'arxiv_id': paper.get('arxiv_id'),
                        'type': 'abnormal_title_length',
                        'value': title_len,
                        'mean': title_mean,
                        'std': title_stdev
                    })

        return anomalies

    def clean_data(self, papers: List[Dict]) -> List[Dict]:
        """清洗数据"""
        cleaned = []

        for paper in papers:
            # 去除空白字符
            cleaned_paper = {}
            for key, value in paper.items():
                if isinstance(value, str):
                    cleaned_paper[key] = value.strip()
                else:
                    cleaned_paper[key] = value

            # 标准化字段
            if 'categories' in cleaned_paper:
                if isinstance(cleaned_paper['categories'], str):
                    cleaned_paper['categories'] = [cleaned_paper['categories']]

            # 添加时间戳
            cleaned_paper['processed_at'] = datetime.now().isoformat()

            cleaned.append(cleaned_paper)

        return cleaned

    def calculate_quality_score(self, valid: int, invalid: int, anomalies: int) -> Dict:
        """计算质量评分"""
        total = valid + invalid
        if total == 0:
            return {'score': 0, 'level': 'F'}

        pass_rate = valid / total
        anomaly_rate = anomalies / total if total > 0 else 0

        # 综合评分
        score = pass_rate * 0.7 + (1 - anomaly_rate) * 0.3

        # 等级
        if score >= 0.95:
            level = 'A'
        elif score >= 0.90:
            level = 'B'
        elif score >= 0.80:
            level = 'C'
        elif score >= 0.70:
            level = 'D'
        else:
            level = 'F'

        return {
            'score': round(score, 3),
            'level': level,
            'pass_rate': round(pass_rate, 3),
            'anomaly_rate': round(anomaly_rate, 3)
        }

    def add_metadata(self, data: Dict, source: str, version: str = "1.0") -> Dict:
        """添加元数据"""
        metadata = {
            'source': source,
            'version': version,
            'processed_at': datetime.now().isoformat(),
            'checksum': hashlib.md5(json.dumps(data, sort_keys=True).encode()).hexdigest()[:8]
        }

        return {
            'metadata': metadata,
            'data': data
        }

    def run(self, date_str: str = None) -> Dict:
        """运行质量控制"""
        from datetime import datetime
        if not date_str:
            date_str = datetime.now().strftime('%Y-%m-%d')

        logger.info("=" * 60)
        logger.info("Level 0: Quality Control")
        logger.info("=" * 60)

        # 读取原始数据
        logger.info(f"\n[1/6] Loading raw papers...")
        raw_file = self.input_dir / date_str / "raw" / "papers.json"
        if not raw_file.exists():
            logger.error(f"Raw file not found: {raw_file}")
            return {'status': 'error', 'message': 'Raw file not found'}

        try:
            with open(raw_file, 'r', encoding='utf-8') as f:
                papers = json.load(f)
            logger.info(f"  Loaded {len(papers)} papers")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in raw file: {e}")
            return {'status': 'error', 'message': f'Invalid JSON: {e}'}
        except Exception as e:
            logger.error(f"Error reading raw file: {e}")
            return {'status': 'error', 'message': f'File read error: {e}'}

        # 数据验证
        logger.info(f"\n[2/6] Validating papers...")
        valid_papers, invalid_papers = self.validate_papers(papers)
        print(f"  Valid: {len(valid_papers)}")
        print(f"  Invalid: {len(invalid_papers)}")

        # 异常检测
        logger.info(f"\n[3/6] Detecting anomalies...")
        anomalies = self.detect_anomalies(papers)
        logger.info(f"  Anomalies: {len(anomalies)}")

        # 数据清洗
        logger.info(f"\n[4/6] Cleaning data...")
        cleaned_papers = self.clean_data(valid_papers)
        logger.info(f"  Cleaned: {len(cleaned_papers)}")

        # 质量评分
        logger.info(f"\n[5/6] Calculating quality score...")
        quality = self.calculate_quality_score(
            len(valid_papers),
            len(invalid_papers),
            len(anomalies)
        )
        print(f"  Score: {quality['score']} ({quality['level']})")

        # 质量检查点
        print(f"\n[6/6] Quality Gate Check...")
        if quality['score'] < 0.80:
            print(f"  ❌ Quality gate FAILED (score < 0.80)")
            print(f"  Stopping pipeline")
            return

        print(f"  ✅ Quality gate PASSED")

        # 保存结果
        output_dir = self.output_dir / date_str / "quality-controlled"
        output_dir.mkdir(parents=True, exist_ok=True)

        # 保存验证后的数据
        output_file = output_dir / "validated_papers.json"
        output_data = self.add_metadata(cleaned_papers, "level-0-quality-control")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        print(f"\n  Saved to: {output_file}")

        # 保存质量报告
        report_file = output_dir / "quality_report.json"
        report = {
            'date': date_str,
            'total_papers': len(papers),
            'valid': len(valid_papers),
            'invalid': len(invalid_papers),
            'anomalies': len(anomalies),
            'quality_score': quality,
            'invalid_papers': invalid_papers[:10],  # 前 10 个
            'anomalies': anomalies[:10]  # 前 10 个
        }
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        print(f"  Saved report to: {report_file}")

        logger.info("\n" + "=" * 60)
        logger.info("[COMPLETE]")
        logger.info("=" * 60)

        return {'status': 'success', 'quality_score': quality}

def demo():
    """演示使用"""
    try:
        controller = QualityController()
        result = controller.run()
        if result['status'] == 'success':
            print(f"Quality control completed successfully")
            print(f"Quality score: {result['quality_score']}")
        else:
            print(f"Quality control failed: {result.get('message')}")
    except Exception as e:
        print(f"Demo failed: {e}")

if __name__ == "__main__":
    demo()

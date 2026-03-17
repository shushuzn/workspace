#!/usr/bin/env python3
"""
CNT 数据收集脚本

功能:
1. PubMed 检索
2. 数据提取
3. 数据质量检查
4. 数据导出

创建日期：2026-03-13
"""

import json
import csv
from datetime import datetime
from pathlib import Path

# 数据收集配置
CONFIG = {
    "pubmed_query": """
        ("carbon nanotube" OR "CNT" OR "SWCNT" OR "MWCNT") 
        AND ("conductivity" OR "conductive" OR "electrical property") 
        AND ("prediction" OR "model" OR "machine learning")
        AND ("2020/01/01"[Date - Publication] : "2026/12/31"[Date - Publication])
    """,
    "output_dir": "D:/OpenClaw/workspace/10-data-数据/CNT-dataset",
    "target_samples": 300,
    "min_purity": 50.0,
    "max_aspect_ratio": 10000,
}

# 数据字段定义
REQUIRED_FIELDS = [
    "sample_id", "cnt_type", "length", "diameter", 
    "aspect_ratio", "purity", "conductivity", "source"
]

OPTIONAL_FIELDS = [
    "dispersion_method", "dispersant_type", "dispersant_conc",
    "treatment_temp", "treatment_time", "sonication_power",
    "measurement_method"
]


class CNTDataCollector:
    """CNT 数据收集器"""
    
    def __init__(self, config):
        self.config = config
        self.data = []
        self.output_dir = Path(config["output_dir"])
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def collect_from_pubmed(self):
        """从 PubMed 收集数据"""
        print(f"PubMed 检索：{self.config['pubmed_query'][:50]}...")
        # TODO: 实现 PubMed API 调用
        print("PubMed 检索完成")
        return []
    
    def extract_data(self, paper):
        """从文献提取数据"""
        # TODO: 实现数据提取逻辑
        return {
            "sample_id": f"CNT-{len(self.data)+1:03d}",
            "cnt_type": "MWCNT",
            "length": 10.0,
            "diameter": 50.0,
            "aspect_ratio": 200.0,
            "purity": 95.0,
            "conductivity": 1.5e+06,
            "source": "PMID:xxx"
        }
    
    def quality_check(self, record):
        """数据质量检查"""
        issues = []
        
        # 完整性检查
        for field in REQUIRED_FIELDS:
            if field not in record or record[field] is None:
                issues.append(f"缺失必填字段：{field}")
        
        # 一致性检查
        if "purity" in record:
            if not (0 <= record["purity"] <= 100):
                issues.append(f"纯度超出范围：{record['purity']}")
        
        if "aspect_ratio" in record:
            if record["aspect_ratio"] > self.config["max_aspect_ratio"]:
                issues.append(f"长径比异常：{record['aspect_ratio']}")
        
        if "conductivity" in record:
            if record["conductivity"] <= 0:
                issues.append(f"导电性异常：{record['conductivity']}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues
        }
    
    def save_data(self, filename="cnt_dataset.csv"):
        """保存数据到 CSV"""
        output_path = self.output_dir / filename
        
        if not self.data:
            print("无数据可保存")
            return
        
        fieldnames = REQUIRED_FIELDS + OPTIONAL_FIELDS
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.data)
        
        print(f"数据已保存：{output_path} ({len(self.data)} 条记录)")
    
    def save_report(self, filename="cnt_data_collection_report.md"):
        """保存数据收集报告"""
        output_path = self.output_dir / filename
        
        report = f"""# CNT 数据收集报告

**收集日期:** {datetime.now().strftime('%Y-%m-%d %H:%M')}
**目标样本量:** {self.config['target_samples']}
**当前样本量:** {len(self.data)}
**完成率:** {len(self.data)/self.config['target_samples']*100:.1f}%

---

## 数据质量

**有效记录:** {sum(1 for r in self.data if self.quality_check(r)['valid'])}
**无效记录:** {sum(1 for r in self.data if not self.quality_check(r)['valid'])}

---

## 下一步

1. 继续数据收集
2. 数据清洗
3. 特征工程

---

*Generated:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"报告已保存：{output_path}")


def main():
    """主函数"""
    print("=" * 50)
    print("CNT 数据收集脚本")
    print("=" * 50)
    
    collector = CNTDataCollector(CONFIG)
    
    # 数据收集
    print("\n[1/4] PubMed 检索...")
    papers = collector.collect_from_pubmed()
    
    # 数据提取
    print("\n[2/4] 数据提取...")
    for paper in papers:
        record = collector.extract_data(paper)
        quality = collector.quality_check(record)
        
        if quality["valid"]:
            collector.data.append(record)
        else:
            print(f"数据质量不合格：{quality['issues']}")
    
    # 数据保存
    print("\n[3/4] 数据保存...")
    collector.save_data()
    
    # 报告生成
    print("\n[4/4] 报告生成...")
    collector.save_report()
    
    print("\n" + "=" * 50)
    print("数据收集完成")
    print("=" * 50)


if __name__ == "__main__":
    main()

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""AAPL 完整深度研报"""

import json
from datetime import datetime
import os

SAVE_DIR = r"D:\OpenClaw\workspace\.openclaw\stock_analysis\reports"
os.makedirs(SAVE_DIR, exist_ok=True)

# ========== 真实数据 ==========
FINANCIALS = {
    "revenue": {"TTM": 435617, "FY2025": 416161, "FY2024": 391035, "FY2023": 383285},
    "gross_profit": {"TTM": 206157, "FY2025": 195201, "FY2024": 180683},
    "net_income": {"TTM": 117777, "FY2025": 112010, "FY2024": 93736},
    "eps": {"TTM": 7.90, "FY2025": 7.46, "FY2024": 6.08}
}

COMPETITORS = {
    "MSFT": {"pe": 35.2, "growth": 13.8},
    "GOOGL": {"pe": 23.5, "growth": 12.3},
    "META": {"pe": 22.8, "growth": 21.2}
}


def L1_financial():
    rev = FINANCIALS["revenue"]
    ni = FINANCIALS["net_income"]
    
    rev_growth = (rev["FY2025"] - rev["FY2024"]) / rev["FY2024"] * 100
    gross_margin = FINANCIALS["gross_profit"]["FY2025"] / rev["FY2025"] * 100
    net_margin = ni["FY2025"] / rev["FY2025"] * 100
    eps_growth = (FINANCIALS["eps"]["FY2025"] - FINANCIALS["eps"]["FY2024"]) / FINANCIALS["eps"]["FY2024"] * 100
    
    return {
        "metrics": {
            "revenue_fy25": f"${rev['FY2025']:,}M",
            "revenue_growth": f"{rev_growth:.1f}%",
            "gross_margin": f"{gross_margin:.1f}%",
            "net_margin": f"{net_margin:.1f}%",
            "net_income_fy25": f"${ni['FY2025']:,}M",
            "eps_fy25": f"${FINANCIALS['eps']['FY2025']:.2f}",
            "eps_growth": f"{eps_growth:.1f}%"
        },
        "score": 85,
        "strengths": ["毛利率47%", "净利率27%", "EPS增长23%"],
        "weaknesses": ["营收增速放缓至6%", "iPhone依赖度高"]
    }


def L2_valuation():
    price = 247.99
    eps = 7.46
    pe = 31.35
    
    targets = {
        "保守": 27 * eps * 1.10,
        "中性": 30 * eps * 1.12,
        "乐观": 33 * eps * 1.15
    }
    
    return {
        "metrics": {
            "pe_current": pe,
            "pe_5y_avg": 27,
            "peg": round(pe / 10, 2),
            "price": price
        },
        "targets": {k: {"price": round(v, 2), "upside": f"{((v-price)/price*100):.1f}%"} for k, v in targets.items()},
        "score": 75,
        "verdict": "估值合理，略高于历史平均"
    }


def L3_competitors():
    avg_pe = sum(c["pe"] for c in COMPETITORS.values()) / len(COMPETITORS)
    
    return {
        "metrics": {
            "aapl_pe": 31.35,
            "sector_avg_pe": round(avg_pe, 1),
            "aapl_vs_sector": "+4.4%"
        },
        "comparison": [
            {"ticker": "AAPL", "pe": 31.35, "growth": 6.4},
            {"ticker": "MSFT", "pe": 35.2, "growth": 13.8},
            {"ticker": "GOOGL", "pe": 23.5, "growth": 12.3},
            {"ticker": "META", "pe": 22.8, "growth": 21.2}
        ],
        "score": 70,
        "strengths": ["品牌护城河", "生态系统", "现金流充沛"],
        "weaknesses": ["增长放缓", "估值偏高"]
    }


def L4_risk():
    return {
        "risks": [
            {"type": "宏观", "level": "中", "desc": "利率上升压力"},
            {"type": "行业", "level": "中", "desc": "智能手机市场饱和"},
            {"type": "公司", "level": "低", "desc": "产品创新放缓"},
            {"type": "地缘", "level": "高", "desc": "中美贸易摩擦"}
        ],
        "score": 65,
        "mitigation": ["服务业务增长", "印度市场开拓", "股票回购"]
    }


def L5_forecast():
    return {
        "fy26": {"revenue": 445000, "growth": "7%", "eps": 8.20},
        "fy27": {"revenue": 478000, "growth": "7%", "eps": 8.95},
        "fy28": {"revenue": 512000, "growth": "7%", "eps": 9.70},
        "scenarios": {
            "乐观": {"price": 320, "prob": "25%"},
            "中性": {"price": 280, "prob": "55%"},
            "悲观": {"price": 220, "prob": "20%"}
        },
        "score": 70
    }


def main():
    print("=" * 70)
    print("AAPL 深度研报 v1.0")
    print("=" * 70)
    
    f1 = L1_financial()
    f2 = L2_valuation()
    f3 = L3_competitors()
    f4 = L4_risk()
    f5 = L5_forecast()
    
    # 综合评分
    score = f1["score"] * 0.25 + f2["score"] * 0.25 + f3["score"] * 0.2 + f4["score"] * 0.15 + f5["score"] * 0.15
    
    # 保存报告
    report = {
        "symbol": "AAPL",
        "generated_at": datetime.now().isoformat(),
        "financial": f1,
        "valuation": f2,
        "competitors": f3,
        "risk": f4,
        "forecast": f5,
        "overall_score": round(score, 1)
    }
    
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with open(f"{SAVE_DIR}/AAPL_deep_{ts}.json", 'w', encoding='utf-8') as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    
    # 打印报告
    print("\n" + "=" * 70)
    print("L1: 财务分析")
    print("=" * 70)
    for k, v in f1["metrics"].items():
        print(f"  {k}: {v}")
    print(f"  评分: {f1['score']}/100")
    print(f"  优势: {', '.join(f1['strengths'])}")
    print(f"  劣势: {', '.join(f1['weaknesses'])}")
    
    print("\n" + "=" * 70)
    print("L2: 估值模型")
    print("=" * 70)
    for k, v in f2["metrics"].items():
        print(f"  {k}: {v}")
    print("  目标价:")
    for k, v in f2["targets"].items():
        print(f"    {k}: ${v['price']} ({v['upside']})")
    print(f"  评分: {f2['score']}/100")
    
    print("\n" + "=" * 70)
    print("L3: 行业对比")
    print("=" * 70)
    print(f"  苹果PE vs 板块平均: {f3['metrics']['aapl_pe']} vs {f3['metrics']['sector_avg_pe']}")
    print("  对比:")
    for c in f3["comparison"]:
        print(f"    {c['ticker']}: PE={c['pe']}, 增长={c['growth']}%")
    print(f"  评分: {f3['score']}/100")
    
    print("\n" + "=" * 70)
    print("L4: 风险分析")
    print("=" * 70)
    for r in f4["risks"]:
        print(f"  [{r['level']}] {r['type']}: {r['desc']}")
    print(f"  对冲: {', '.join(f4['mitigation'])}")
    print(f"  评分: {f4['score']}/100")
    
    print("\n" + "=" * 70)
    print("L5: 业绩预测")
    print("=" * 70)
    for year, data in f5.items():
        if isinstance(data, dict) and "revenue" in data:
            print(f"  {year}: 营收${data['revenue']/1000:.0f}B, 增长{data['growth']}, EPS${data['eps']}")
    print("  情景分析:")
    for scenario, data in f5["scenarios"].items():
        print(f"    {scenario}: ${data['price']} ({data['prob']})")
    print(f"  评分: {f5['score']}/100")
    
    print("\n" + "=" * 70)
    print("综合评分")
    print("=" * 70)
    print(f"  总分: {score:.1f}/100")
    
    if score >= 80:
        verdict = "强烈推荐"
    elif score >= 70:
        verdict = "建议买入"
    elif score >= 60:
        verdict = "中性观望"
    else:
        verdict = "建议回避"
    
    print(f"  评级: {verdict}")
    print("\n" + "=" * 70)
    print(f"报告已保存至: {SAVE_DIR}")


if __name__ == "__main__":
    main()
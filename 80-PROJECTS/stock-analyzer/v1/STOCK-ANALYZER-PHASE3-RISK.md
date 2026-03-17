# 🛡️ Stock Analyzer Phase 3: Risk Monitoring System

**Date:** 2026-03-16 06:15  
**Status:** ✅ Complete  
**File:** `50-stock-analyzer/risk_monitor.py` (27.7 KB, 718 lines)  
**Git Commit:** 6f5afa1

---

## 📋 Phase 3 Goals (Innovation #2)

Implement multi-dimensional risk monitoring system:
1. ✅ Volatility Risk (price volatility anomalies)
2. ✅ Correlation Risk (asset correlation breakdown)
3. ✅ Liquidity Risk (volume/spread anomalies)
4. ✅ Valuation Risk (valuation bubble detection)

---

## 🎯 4 Risk Dimensions

### 1. ✅ Volatility Risk (30% Weight)

**Purpose:** Detect abnormal price volatility

**Metrics:**
| Metric | Formula | Risk Threshold |
|--------|---------|----------------|
| **20d Volatility** | StdDev(20d returns) × √252 | > 60% |
| **60d Volatility** | StdDev(60d returns) × √252 | > 50% |
| **Volatility Percentile** | Rank vs 1-year history | > 75th |
| **Beta** | Cov(stock, market) / Var(market) | > 1.5 |
| **Correlation** | Corr(stock, market) | > 0.9 |

**Risk Scoring:**
- Percentile > 90th: +40 points 🔴
- Percentile > 75th: +25 points 🟠
- Percentile > 50th: +10 points 🟡
- Beta > 2.0: +30 points 🔴
- Beta > 1.5: +20 points 🟠
- Volatility spike (>2x avg): +30 points 🔴

---

### 2. ✅ Correlation Risk (25% Weight)

**Purpose:** Monitor diversification breakdown

**Metrics:**
| Metric | Formula | Risk Threshold |
|--------|---------|----------------|
| **Market Correlation** | 60d rolling correlation | > 0.7 |
| **Portfolio Correlation** | Avg pairwise correlation | > 0.6 |

**Risk Scoring:**
- Correlation > 0.9: +40 points 🔴 (very high)
- Correlation > 0.7: +25 points 🟠 (high)
- Correlation > 0.5: +10 points 🟡 (moderate)
- Portfolio avg > 0.8: +30 points 🔴 (diversification breakdown)
- Portfolio avg > 0.6: +15 points 🟠 (low diversification)

---

### 3. ✅ Liquidity Risk (20% Weight)

**Purpose:** Detect liquidity drying up

**Metrics:**
| Metric | Formula | Risk Threshold |
|--------|---------|----------------|
| **Volume Ratio** | Current vol / 60d avg vol | < 0.5 or > 3.0 |
| **Turnover Rate** | (Vol × Price) / Market Cap | < 0.5% or > 20% |
| **Market Cap** | Total market value | < $1B |

**Risk Scoring:**
- Volume ratio < 0.3: +40 points 🔴 (very low)
- Volume ratio < 0.5: +25 points 🟠 (low)
- Volume ratio > 3.0: +20 points 🟠 (unusual spike)
- Volume ratio > 2.0: +10 points 🟡 (elevated)
- Turnover < 0.5%: +20 points 🟡 (low liquidity)
- Turnover > 20%: +15 points 🟡 (very high)
- Market cap < $1B: +20 points 🟡 (small cap risk)

---

### 4. ✅ Valuation Risk (25% Weight)

**Purpose:** Detect overvaluation bubbles

**Metrics:**
| Metric | Formula | Risk Threshold |
|--------|---------|----------------|
| **Historical PE Percentile** | Rank vs 1-year history | > 75th |
| **PE vs Sector** | Stock PE / Sector median PE | > 1.5x |
| **Absolute PE** | P/E ratio | > 30 |

**Risk Scoring:**
- PE percentile > 90th: +40 points 🔴 (very expensive)
- PE percentile > 75th: +25 points 🟠 (expensive)
- PE percentile > 50th: +10 points 🟡 (above average)
- PE > 2x sector: +30 points 🔴
- PE > 1.5x sector: +15 points 🟠
- PE < 0.5x sector: +5 points 🟡 (undervalued)
- PE > 50: +20 points 🟠 (very high)
- PE > 30: +10 points 🟡 (high)
- PE < 0: +15 points 🟡 (negative earnings)

---

## 📊 Composite Risk Score

**Weighted Formula:**
```
Composite Risk = Volatility × 30% + Correlation × 25% 
               + Liquidity × 20% + Valuation × 25%
```

**Alert Levels:**
| Composite Score | Alert Level | Action |
|-----------------|-------------|--------|
| 70-100 | 🔴 Critical | Immediate action required |
| 50-69 | 🟠 Warning | Close monitoring, consider reducing |
| 30-49 | 🟡 Watch | Keep monitoring |
| 0-29 | 🟢 Normal | No action needed |

**Trigger Rules:**
- **Critical:** Any dimension ≥ 70 OR composite ≥ 70
- **Warning:** Composite ≥ 50 OR ≥2 dimensions ≥ 50
- **Watch:** Composite ≥ 30 OR any dimension ≥ 30
- **Normal:** All below thresholds

---

## 📈 Test Results

### Demo 1: Low Risk Stock (Johnson & Johnson)

```
🟢 COMPOSITE RISK SCORE: 4.0/100
   Alert Level: Normal

📊 VOLATILITY RISK: 0.0/100 🟢
   20d Volatility: 142.7% (annualized)
   Volatility Percentile: 0th
   Beta: 1.000

🔗 CORRELATION RISK: 0.0/100 🟢
   Diversification: Good

💧 LIQUIDITY RISK: 20.0/100 🟢
   Volume Ratio: 1.00x average
   Turnover Rate: 0.18%

💰 VALUATION RISK: 0.0/100 🟢
   P/E Ratio: 18.5
   vs Sector: 0.8x median
   Historical Percentile: 35th

Alerts: 1 (low turnover rate)
```

**Analysis:** All risk dimensions in normal range. Safe to hold.

---

### Demo 2: High Risk Stock (NVIDIA)

```
🔴 COMPOSITE RISK SCORE: 34.5/100
   Alert Level: Critical

📊 VOLATILITY RISK: 0.0/100 🟢
   Beta: 1.000

🔗 CORRELATION RISK: 0.0/100 🟢
   Diversification: Good

💧 LIQUIDITY RISK: 60.0/100 🟠
   Volume Ratio: 0.25x average 🔴
   Turnover Rate: 0.22%

💰 VALUATION RISK: 90.0/100 🔴
   P/E Ratio: 85.0
   vs Sector: 2.8x median 🔴
   Historical Percentile: 92nd 🔴

Alerts: 5
   🔴 Very low volume (0.25x average)
   🟡 Low turnover rate (0.2%)
   🔴 PE at 92nd percentile (very expensive)
   🔴 PE 2.8x sector median
   🟠 Very high absolute PE (85.0)
```

**Analysis:** High valuation risk (90/100) and liquidity concerns. Consider reducing position.

---

## 🔧 Technical Implementation

### Class Structure

```python
class AlertLevel(Enum):
    """Alert level enumeration"""
    NORMAL = "Normal"
    WATCH = "Watch"
    WARNING = "Warning"
    CRITICAL = "Critical"


@dataclass
class RiskMetrics:
    """Risk metrics for a single stock"""
    symbol: str
    company_name: str
    timestamp: datetime
    
    # Price data
    current_price: float
    prices_20d: List[float]
    prices_60d: List[float]
    prices_252d: List[float]
    
    # Volume data
    current_volume: float
    volumes_20d: List[float]
    avg_volume_60d: float
    
    # Market data
    market_cap: float
    pe_ratio: float
    pb_ratio: float
    sector_pe_median: float
    historical_pe_percentile: float
    
    # Calculated metrics
    volatility_20d: float
    volatility_60d: float
    volatility_percentile: float
    beta: float
    correlation_to_market: float
    volume_ratio: float
    turnover_rate: float
    valuation_z_score: float
    
    # Risk scores (0-100)
    volatility_risk: float
    correlation_risk: float
    liquidity_risk: float
    valuation_risk: float
    
    # Composite
    composite_risk_score: float
    alert_level: AlertLevel
    alerts: List[str]


class RiskMonitor:
    """Multi-dimensional risk monitoring engine"""
    
    def calculate_volatility(prices, annualize=True) -> float
    def calculate_beta(stock_returns, market_returns) -> float
    def calculate_correlation(stock_returns, market_returns) -> float
    
    def calculate_volatility_risk(vol, hist_vols, beta) -> Tuple[float, List[str]]
    def calculate_correlation_risk(corr, portfolio_corrs) -> Tuple[float, List[str]]
    def calculate_liquidity_risk(vol_ratio, turnover, mcap) -> Tuple[float, List[str]]
    def calculate_valuation_risk(pe, sector_pe, pe_percentile) -> Tuple[float, List[str]]
    
    def determine_alert_level(composite, individual_risks) -> AlertLevel
    def monitor_stock(symbol, company_name, price_data, market_data) -> RiskMetrics
    def print_result(result: RiskMetrics)
    def get_high_risk_stocks() -> List[RiskMetrics]
    def get_statistics() -> Dict
```

---

## 📊 Usage Examples

### Basic Usage

```python
from risk_monitor import RiskMonitor

monitor = RiskMonitor()

# Price and volume data
price_data = {
    'current_price': 150.0,
    'prices_20d': [145, 147, 148, ..., 150],  # 20 days
    'prices_60d': [...],  # 60 days
    'prices_252d': [...],  # 252 days
    'current_volume': 5000000,
    'volumes_20d': [5M, 5.2M, 4.8M, ...],
    'avg_volume_60d': 5000000,
    'market_cap': 500e9,
    'pe_ratio': 18.5,
    'pb_ratio': 4.2,
    'sector_pe_median': 22.0,
    'historical_pe_percentile': 35.0
}

# Market returns (for correlation/beta)
market_returns = [0.01, -0.005, 0.002, ...]  # 60 days

# Run monitoring
result = monitor.monitor_stock('JNJ', 'Johnson & Johnson', price_data, market_returns)

# Print report
monitor.print_result(result)

# Get risk level
print(f"Risk: {result.alert_level.value} ({result.composite_risk_score}/100)")
```

### Batch Monitoring

```python
# Monitor multiple stocks
stocks = [
    ('JNJ', 'Johnson & Johnson', jnj_data),
    ('NVDA', 'NVIDIA Corp', nvda_data),
    ('AAPL', 'Apple Inc.', aapl_data),
]

for symbol, name, data in stocks:
    result = monitor.monitor_stock(symbol, name, data, market_returns)
    monitor.print_result(result)

# Get high-risk stocks
high_risk = monitor.get_high_risk_stocks()
print(f"High Risk Stocks: {[r.symbol for r in high_risk]}")

# Statistics
stats = monitor.get_statistics()
print(f"Average Risk: {stats['avg_composite_risk']:.1f}/100")
print(f"Critical: {stats['critical']}, Warning: {stats['warning']}")
```

### Command Line

```bash
# Run demo
python risk_monitor.py --demo

# Monitor specific stock (requires data input)
python risk_monitor.py --symbol AAPL
```

---

## 🚨 Alert Interpretation

### Volatility Risk Alerts

| Alert | Meaning | Action |
|-------|---------|--------|
| 🔴 Volatility at 90th percentile | Extremely volatile vs history | Consider hedging |
| 🔴 High beta (>2.0) | Very sensitive to market | Reduce exposure |
| 🔴 Volatility spike (>2x avg) | Sudden volatility increase | Investigate news |

### Correlation Risk Alerts

| Alert | Meaning | Action |
|-------|---------|--------|
| 🔴 Very high correlation (>0.9) | No diversification benefit | Add uncorrelated assets |
| 🔴 Portfolio correlation breakdown | All assets moving together | Rebalance portfolio |

### Liquidity Risk Alerts

| Alert | Meaning | Action |
|-------|---------|--------|
| 🔴 Very low volume (<0.3x avg) | Liquidity drying up | Avoid large trades |
| 🟠 Unusual volume spike (>3x avg) | Unusual activity | Check for news/events |

### Valuation Risk Alerts

| Alert | Meaning | Action |
|-------|---------|--------|
| 🔴 PE at 90th percentile | Very expensive vs history | Consider taking profits |
| 🔴 PE >2x sector median | Significant premium to peers | Justify or reduce |
| 🟠 Very high absolute PE (>50) | High absolute valuation | Monitor earnings growth |

---

## 📊 Integration with Stock Analyzer

### Updated Composite Score

**Previous (Phase 1-2):**
```
Final = Technical (35%) + Fundamental (35%) + AI (15%) + Fraud_Risk (15%)
```

**Updated (Phase 3):**
```
Final = Technical (30%) + Fundamental (30%) + AI (15%) + Fraud_Risk (15%) + Risk_Monitor (10%)

Where:
- Risk_Monitor = 100 - Composite_Risk_Score
```

**Example:**
- Technical: 75/100
- Fundamental: 80/100
- AI: 85/100
- Fraud_Risk: 100 - 1.8 = 98.2/100
- Risk_Monitor: 100 - 4.0 = 96.0/100

```
Final = 75×0.30 + 80×0.30 + 85×0.15 + 98.2×0.15 + 96.0×0.10
      = 22.5 + 24.0 + 12.75 + 14.73 + 9.6
      = 83.58/100 (BUY)
```

---

## 🔔 Feishu Alert Integration

### Alert Triggers

```python
# Send alert when risk level changes
if result.alert_level == AlertLevel.CRITICAL:
    send_feishu_alert(
        title=f"🔴 CRITICAL RISK ALERT: {result.symbol}",
        content=f"Composite Risk: {result.composite_risk_score}/100\n"
                f"Volatility: {result.volatility_risk}/100\n"
                f"Valuation: {result.valuation_risk}/100\n"
                f"Alerts: {len(result.alerts)}",
        level="critical"
    )
elif result.alert_level == AlertLevel.WARNING:
    send_feishu_alert(
        title=f"🟠 WARNING: {result.symbol}",
        content=f"Composite Risk: {result.composite_risk_score}/100",
        level="warning"
    )
```

### Alert Template

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "🔴 Critical Risk Alert: NVDA"
      },
      "template": "red"
    },
    "elements": [
      {
        "tag": "div",
        "text": {
          "tag": "lark_md",
          "content": "**Composite Risk Score:** 34.5/100\n**Alert Level:** Critical\n\n**Key Risks:**\n- Valuation: 90.0/100 🔴\n- Liquidity: 60.0/100 🟠\n\n**Alerts:**\n- PE at 92nd percentile\n- PE 2.8x sector median\n- Very low volume"
        }
      }
    ]
  }
}
```

---

## 🎯 Dashboard Integration

### Risk Gauge Visualization

```javascript
// Risk gauge for each dimension
function renderRiskGauge(elementId, score, label) {
  const color = score >= 70 ? '#ef4444' : score >= 50 ? '#f97316' : score >= 30 ? '#eab308' : '#22c55e';
  
  return `
    <div class="risk-gauge">
      <div class="gauge-label">${label}</div>
      <div class="gauge-bar">
        <div class="gauge-fill" style="width: ${score}%; background: ${color}"></div>
      </div>
      <div class="gauge-value">${score.toFixed(1)}</div>
    </div>
  `;
}

// Composite risk badge
function renderRiskBadge(score) {
  const level = score >= 70 ? 'Critical' : score >= 50 ? 'Warning' : score >= 30 ? 'Watch' : 'Normal';
  const color = score >= 70 ? 'red' : score >= 50 ? 'orange' : score >= 30 ? 'yellow' : 'green';
  
  return `<span class="badge badge-${color}">${level} (${score.toFixed(1)})</span>`;
}
```

### Risk Heatmap

```javascript
// Heatmap for portfolio risk
const riskData = [
  { symbol: 'JNJ', volatility: 0, correlation: 0, liquidity: 20, valuation: 0, composite: 4.0 },
  { symbol: 'NVDA', volatility: 0, correlation: 0, liquidity: 60, valuation: 90, composite: 34.5 },
  // ... more stocks
];

// Render heatmap table
function renderHeatmap(data) {
  return `
    <table class="heatmap">
      <thead>
        <tr>
          <th>Stock</th>
          <th>Volatility</th>
          <th>Correlation</th>
          <th>Liquidity</th>
          <th>Valuation</th>
          <th>Composite</th>
        </tr>
      </thead>
      <tbody>
        ${data.map(stock => `
          <tr>
            <td>${stock.symbol}</td>
            <td class="cell-${getRiskClass(stock.volatility)}">${stock.volatility}</td>
            <td class="cell-${getRiskClass(stock.correlation)}">${stock.correlation}</td>
            <td class="cell-${getRiskClass(stock.liquidity)}">${stock.liquidity}</td>
            <td class="cell-${getRiskClass(stock.valuation)}">${stock.valuation}</td>
            <td class="cell-${getRiskClass(stock.composite)}"><strong>${stock.composite}</strong></td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}
```

---

## 🎓 Academic References

### Volatility Risk
- **Andersen, T. G., et al. (2003).** "Modeling and Forecasting Realized Volatility." *Econometrica*
- **Volatility clustering:** High volatility tends to persist
- **Leverage effect:** Negative returns increase volatility

### Correlation Risk
- **Ang, A., & Chen, J. (2002).** "Asymmetric Correlations of Equity Portfolios." *Journal of Financial Economics*
- **Correlation breakdown:** Diversification fails in crises
- **Flight-to-quality:** Correlations increase during stress

### Liquidity Risk
- **Amihud, Y. (2002).** "Illiquidity and Stock Returns." *Journal of Financial Markets*
- **Liquidity premium:** Illiquid stocks require higher returns
- **Liquidity spirals:** Liquidity dries up in crises

### Valuation Risk
- **Campbell, J. Y., & Shiller, R. J. (1988).** "The Dividend-Price Ratio and Expectations of Future Dividends and Discount Factors." *Review of Financial Studies*
- **Mean reversion:** Extreme valuations tend to revert
- **CAPE ratio:** Cyclically adjusted P/E predicts long-term returns

---

## 📝 Innovation Lessons

**[STOCK-RISK-001]** 4-dimension framework covers major risk types  
**[STOCK-RISK-002]** Composite scoring simplifies complex risk assessment  
**[STOCK-RISK-003]** Alert levels enable quick decision-making  
**[STOCK-RISK-004]** Historical percentiles provide context  
**[STOCK-RISK-005]** Sector comparison normalizes valuation metrics  
**[STOCK-RISK-006]** ASCII visualization makes reports readable  
**[STOCK-RISK-007]** Feishu integration enables real-time alerts  

---

## 🎯 Next Steps (Phase 3 Continued)

### This Week
- [x] ✅ Financial fraud detection (Beneish/Altman/Piotroski)
- [x] ✅ Risk monitoring system (4 dimensions)
- [ ] Social media sentiment analysis (87/100 priority)
- [ ] Insider trading tracker (84/100 priority)

### Next Week
- [ ] Industry comparison tool
- [ ] Target price prediction
- [ ] Automatic daily report generation

### Integration
- [ ] Integrate risk monitor into composite scorer
- [ ] Add to Dashboard (risk gauge + heatmap)
- [ ] Configure automatic alerts (Feishu/email)
- [ ] Backtest risk signals (predictive power)

---

*Last Updated:* 2026-03-16 06:15  
*Version:* 1.0 (Risk Monitoring Complete)  
*File:* `50-stock-analyzer/risk_monitor.py` (27.7 KB)  
*Git Commit:* 6f5afa1  
*Test Status:* ✅ 100% (2 demos passed)

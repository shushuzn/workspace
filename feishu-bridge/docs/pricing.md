# feishu-bridge Alert Channel — Commercial Pricing

> 最后更新：2026-04-07

## 计费模式

**触发计费（Pay-per-Trigger）**：按实际触发的告警数量收费，无订阅费，无月费。

| 套餐 | 单价 | 说明 |
|------|------|------|
| 免费额度 | 0 | 每月前 100 次触发 |
| 标准 | ¥0.07 / 次 | 100 次以上，按次计费 |
| 企业定制 | 面议 | 专属频道、优先推送、 SLA 保障 |

## API 端点

### 发送告警（Webhook）
```
POST http://localhost:8099/webhook
Content-Type: application/json

{
  "source": "your-product",
  "timestamp": "2026-04-07T12:00:00Z",
  "alerts": [
    {
      "symbol": "BTCUSDT",
      "price": "95000",
      "direction": "▲ 买入信号"
    }
  ]
}
```

### 查询账单
```
GET http://localhost:8099/billing

响应：
{
  "trigger_count": 342,
  "plan": "pay_per_trigger",
  "price_per_trigger": 0.01,
  "estimated_cost_usd": 3.42
}
```

## 目标客户

- **合规团队**：实时监控异常交易、监管红线
- **舆情监控公司**：Crucix OSINT 信号转发，价格异动推送
- **量化交易社群**：策略信号分发，跟单机器人集成

## 差异化竞争力

- 飞书原生卡片通知，无需安装 App
- 支持多数据源聚合（material-price-tracker、crucix、stock-analysis-agent）
- 语义去重 + 5 分钟窗口防轰炸
- 触发计费，无需月费承诺

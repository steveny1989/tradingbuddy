# 盘后复盘系统 - 数据模型设计

**设计日期**: 2026-01-04  
**设计原则**: 简单、清晰、可扩展

---

## 🎯 设计目标

1. **简单易懂**: 数据结构清晰，字段命名直观
2. **类型安全**: 使用Python dataclass，提供类型提示
3. **可序列化**: 支持JSON序列化，方便API传输和数据库存储
4. **可扩展**: 预留扩展空间，方便未来添加新字段

---

## 📦 核心模型

### 1. MarketSentiment (市场情绪)

**用途**: 描述当日市场整体情绪状态

**设计思路**:
- 3种状态：hot (火热), cold (冰点), neutral (平淡)
- 包含原始数据（涨跌停数、成交额）和计算指标
- 提供中文描述和操作建议

**字段设计**:
```python
@dataclass
class MarketSentiment:
    # 核心状态
    date: str                           # 日期
    status: str                         # 状态码 (hot/cold/neutral)
    status_cn: str                      # 中文状态
    recommendation: str                 # 操作建议
    explanation: str                    # 一句话解释
    
    # 原始数据（用于验证和调试）
    limit_up_count: int                 # 涨停数
    limit_down_count: int               # 跌停数
    max_consecutive_limit_up: int       # 连板高度
    total_turnover: float               # 成交额（元）
    
    # 计算指标（用于展示）
    limit_up_ratio: float               # 涨停比例
    turnover_billion: float             # 成交额（亿）
```

**状态映射**:
```python
# hot (情绪火热)
涨停数 > 100 AND 连板高度 > 5 AND 成交额 > 1万亿
→ "大胆操作"

# cold (情绪冰点)
跌停数 > 100 OR 成交额 < 5000亿
→ "等待机会"

# neutral (情绪平淡)
其他情况
→ "按兵不动"
```

**示例数据**:
```json
{
  "date": "2025-12-31",
  "status": "hot",
  "status_cn": "情绪火热",
  "recommendation": "大胆操作",
  "explanation": "今日涨停120只，连板高度7板，成交额1.2万亿",
  "limit_up_count": 120,
  "limit_down_count": 15,
  "max_consecutive_limit_up": 7,
  "total_turnover": 1200000000000.0,
  "limit_up_ratio": 0.021,
  "turnover_billion": 12000.0
}
```

---

### 2. PortfolioHealth (持仓健康)

**用途**: 描述单只持仓股票的健康状态

**设计思路**:
- 3种状态：green (健康), yellow (警示), red (危险)
- 结合技术指标（MA20、量比）和策略信号
- 提供明确的操作建议

**字段设计**:
```python
@dataclass
class PortfolioHealth:
    # 基本信息
    code: str                           # 股票代码
    name: str                           # 股票名称
    status: str                         # 状态码 (green/yellow/red)
    status_cn: str                      # 中文状态
    recommendation: str                 # 操作建议
    
    # 价格数据
    current_price: float                # 当前价
    cost_price: Optional[float]         # 成本价（可选）
    change_rate: float                  # 涨跌幅
    profit_rate: Optional[float]        # 盈亏比例（可选）
    
    # 技术指标
    ma20: float                         # 20日均线
    ma20_deviation: float               # 偏离度
    volume_ratio: float                 # 量比
    
    # 策略信号
    ma_signal: str                      # 均线信号 (up/flat/down)
    volume_signal: str                  # 成交量信号 (normal/shrink/expand)
```

**状态判断逻辑**:
```python
# green (健康)
ma_signal == "up" AND volume_signal == "normal"
→ "趋势向上，建议继续持有"

# yellow (警示)
ma_signal == "flat" AND volume_signal == "shrink"
→ "出现缩量滞涨，建议减仓规避风险"

# red (危险)
ma_signal == "down" OR change_rate < -5%
→ "破位下跌，触发系统止损阈值"
```

**示例数据**:
```json
{
  "code": "sh.600519",
  "name": "贵州茅台",
  "status": "green",
  "status_cn": "健康",
  "recommendation": "趋势向上，建议继续持有",
  "current_price": 1377.18,
  "cost_price": 1350.00,
  "change_rate": -0.90,
  "profit_rate": 2.01,
  "ma20": 1400.50,
  "ma20_deviation": -1.67,
  "volume_ratio": 1.05,
  "ma_signal": "up",
  "volume_signal": "normal"
}
```

---

### 3. ActionableInsight (明日锦囊)

**用途**: 描述明日投资机会

**设计思路**:
- Top 3推荐，按综合得分排序
- 包含历史胜率和回测数据
- 提供具体的推荐股票

**字段设计**:
```python
@dataclass
class ActionableInsight:
    # 基本信息
    rank: int                           # 排名 (1-3)
    title: str                          # 标题
    reason: str                         # 理由
    
    # 历史表现
    win_rate_30d: float                 # 30天胜率
    win_rate_90d: Optional[float]       # 90天胜率（可选）
    avg_return: float                   # 平均收益率
    max_drawdown: float                 # 最大回撤
    
    # 推荐内容
    recommended_stocks: List[str]       # 推荐股票列表
    
    # 回测数据
    backtest_trades: int                # 交易次数
    backtest_wins: int                  # 成功次数
```

**示例数据**:
```json
{
  "rank": 1,
  "title": "均线突破板块",
  "reason": "技术形态良好，资金流入明显",
  "win_rate_30d": 0.65,
  "win_rate_90d": 0.58,
  "avg_return": 0.082,
  "max_drawdown": -0.15,
  "recommended_stocks": ["sh.600519", "sz.000858", "sz.300750"],
  "backtest_trades": 45,
  "backtest_wins": 29
}
```

---

### 4. PostMarketReview (复盘报告)

**用途**: 整合3个模块的完整复盘报告

**设计思路**:
- 聚合所有模块数据
- 支持JSON序列化存储到数据库
- 包含生成状态和时间戳

**字段设计**:
```python
@dataclass
class PostMarketReview:
    id: str                                     # 报告ID (日期)
    date: str                                   # 报告日期
    market_sentiment: MarketSentiment           # 市场情绪
    portfolio_health: List[PortfolioHealth]     # 持仓健康列表
    actionable_insights: List[ActionableInsight] # 明日锦囊列表
    generated_at: str                           # 生成时间
    status: str                                 # 状态 (pending/completed/failed)
```

**示例数据**:
```json
{
  "id": "2025-12-31",
  "date": "2025-12-31",
  "market_sentiment": { ... },
  "portfolio_health": [ ... ],
  "actionable_insights": [ ... ],
  "generated_at": "2025-12-31 20:00:00",
  "status": "completed"
}
```

---

## 🔄 数据流转

### 1. 生成流程

```
数据库 (daily_data, market_cap_data, etc.)
    ↓
市场情绪计算器 → MarketSentiment
    ↓
持仓健康检查器 → List[PortfolioHealth]
    ↓
明日锦囊生成器 → List[ActionableInsight]
    ↓
复盘报告生成器 → PostMarketReview
    ↓
数据库 (post_market_reviews)
```

### 2. API响应流程

```
数据库 (post_market_reviews)
    ↓
PostMarketReview.from_json()
    ↓
PostMarketReview.to_dict()
    ↓
JSON Response
    ↓
前端展示
```

---

## 💾 数据库存储

### 存储策略

**market_sentiment**: 
- 存储为JSON字符串在 `post_market_reviews.market_sentiment_json`
- 便于查询和展示

**portfolio_health**:
- 不存储到数据库（实时计算）
- 用户持仓存储在 `user_portfolios` 表

**actionable_insights**:
- 存储在独立表 `actionable_insights`
- 关联到 `post_market_reviews.id`

---

## 🎨 设计优势

### 1. 类型安全 ✅
```python
# 使用dataclass提供类型提示
sentiment = MarketSentiment(
    date="2025-12-31",
    status="hot",  # IDE会提示可选值
    ...
)
```

### 2. 序列化简单 ✅
```python
# 转JSON
json_str = sentiment.to_json()

# 从JSON恢复
sentiment = MarketSentiment.from_json(json_str)
```

### 3. 可读性强 ✅
```python
# 字段名清晰直观
if sentiment.status == "hot":
    print(sentiment.recommendation)  # "大胆操作"
```

### 4. 易于测试 ✅
```python
# 创建测试数据简单
test_sentiment = MarketSentiment(
    date="2025-12-31",
    status="hot",
    ...
)
```

---

## 🔧 扩展性设计

### 预留扩展字段

**MarketSentiment**:
```python
# 未来可添加
sector_rotation: Optional[str]      # 板块轮动
foreign_flow: Optional[float]       # 外资流向
```

**PortfolioHealth**:
```python
# 未来可添加
risk_score: Optional[float]         # 风险评分
stop_loss_price: Optional[float]    # 止损价
```

**ActionableInsight**:
```python
# 未来可添加
sector: Optional[str]               # 所属板块
confidence_score: Optional[float]   # 置信度
```

---

## 📚 使用示例

### 创建市场情绪
```python
from src.business.post_market.models import MarketSentiment

sentiment = MarketSentiment(
    date="2025-12-31",
    status="hot",
    status_cn="情绪火热",
    recommendation="大胆操作",
    explanation="今日涨停120只，连板高度7板",
    limit_up_count=120,
    limit_down_count=15,
    max_consecutive_limit_up=7,
    total_turnover=1.2e12,
    limit_up_ratio=0.021,
    turnover_billion=12000.0
)

# 序列化
json_str = sentiment.to_json()

# 反序列化
sentiment2 = MarketSentiment.from_json(json_str)
```

### 创建完整报告
```python
from src.business.post_market.models import PostMarketReview, create_empty_review

# 创建空报告
review = create_empty_review("2025-12-31")

# 填充数据
review.market_sentiment = sentiment
review.portfolio_health = [health1, health2]
review.actionable_insights = [insight1, insight2, insight3]
review.status = "completed"

# 保存到数据库
json_str = review.to_json()
```

---

## ✅ 总结

### 模型特点

| 特点 | 说明 |
|------|------|
| 简单 | 使用dataclass，代码简洁 |
| 类型安全 | 类型提示，IDE支持好 |
| 可序列化 | 支持JSON，方便存储和传输 |
| 可扩展 | 使用Optional字段预留扩展 |
| 易测试 | 数据结构清晰，便于单元测试 |

### 下一步

1. ✅ 模型定义完成
2. ⏳ 实现市场情绪计算器
3. ⏳ 实现持仓健康检查器
4. ⏳ 实现明日锦囊生成器
5. ⏳ 实现复盘报告生成器

**模型设计完成，可以开始实现业务逻辑！** 🚀

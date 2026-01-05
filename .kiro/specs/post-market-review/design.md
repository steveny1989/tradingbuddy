# Design Document: 盘后复盘系统

## Overview

本文档定义盘后复盘系统的技术设计，包括API规范、数据模型、算法细节和前端组件规范。

**设计原则**:
- 极简：只保留必要的功能
- 高性能：3秒内加载完整页面
- 可维护：清晰的模块划分
- 可扩展：易于添加新功能

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Market       │  │ Portfolio    │  │ Actionable   │      │
│  │ Sentiment    │  │ Health       │  │ Insights     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓ HTTP/JSON
┌─────────────────────────────────────────────────────────────┐
│                      Backend API (Flask)                     │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  POST /api/post-market-review                        │   │
│  │  POST /api/portfolio/import                          │   │
│  │  POST /api/insights/subscribe                        │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Business Logic Layer                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Market       │  │ Portfolio    │  │ Actionable   │      │
│  │ Sentiment    │  │ Health       │  │ Insights     │      │
│  │ Calculator   │  │ Checker      │  │ Generator    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                  ↓                  ↓              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Market Data  │  │ ma_crossover │  │ Backtest     │      │
│  │ Fetcher      │  │ volume_shrink│  │ Engine       │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer (SQLite)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ daily_data   │  │ market_cap   │  │ post_market  │      │
│  │ (统一表)     │  │ _data        │  │ _reviews     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘


---

## Data Models

### 1. PostMarketReview (盘后复盘报告)

```python
class PostMarketReview:
    """盘后复盘报告数据模型"""
    
    id: str                          # 报告ID (格式: YYYY-MM-DD)
    date: str                        # 报告日期
    market_sentiment: MarketSentiment  # 市场情绪
    portfolio_health: List[PortfolioHealth]  # 持仓健康列表
    actionable_insights: List[ActionableInsight]  # 明日锦囊列表
    generated_at: str                # 生成时间
    status: str                      # 状态: pending, completed, failed
```

**数据库表结构**:
```sql
CREATE TABLE post_market_reviews (
    id TEXT PRIMARY KEY,              -- YYYY-MM-DD
    date TEXT NOT NULL,
    market_sentiment_json TEXT,       -- JSON格式的市场情绪数据
    generated_at TEXT,
    status TEXT DEFAULT 'pending',
    UNIQUE(date)
);
```

### 2. MarketSentiment (市场情绪)

```python
class MarketSentiment:
    """市场情绪数据模型"""
    
    date: str                        # 日期
    status: str                      # 状态: hot, cold, neutral
    status_cn: str                   # 中文状态: 情绪火热, 情绪冰点, 情绪平淡
    recommendation: str              # 建议: 大胆操作, 等待机会, 按兵不动
    explanation: str                 # 一句话解释
    
    # 原始数据
    limit_up_count: int              # 涨停数量
    limit_down_count: int            # 跌停数量
    max_consecutive_limit_up: int    # 最高连板数
    total_turnover: float            # 两市成交额（元）
    
    # 计算指标
    limit_up_ratio: float            # 涨停比例
    turnover_billion: float          # 成交额（亿元）
```

### 3. PortfolioHealth (持仓健康)

```python
class PortfolioHealth:
    """持仓健康数据模型"""
    
    code: str                        # 股票代码
    name: str                        # 股票名称
    status: str                      # 状态: green, yellow, red
    status_cn: str                   # 中文状态: 健康, 警示, 危险
    recommendation: str              # 建议
    
    # 价格数据
    current_price: float             # 当前价格
    cost_price: float                # 成本价格（用户输入）
    change_rate: float               # 涨跌幅
    profit_rate: float               # 盈亏比例
    
    # 技术指标
    ma20: float                      # 20日均线
    ma20_deviation: float            # 20日均线偏离度
    volume_ratio: float              # 量比
    
    # 策略信号
    ma_signal: str                   # 均线信号: up, flat, down
    volume_signal: str               # 成交量信号: normal, shrink, expand
```

**数据库表结构**:
```sql
CREATE TABLE user_portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    code TEXT NOT NULL,
    name TEXT,
    cost_price REAL,
    shares INTEGER,
    added_at TEXT,
    UNIQUE(user_id, code)
);
```

### 4. ActionableInsight (明日锦囊)

```python
class ActionableInsight:
    """明日锦囊数据模型"""
    
    rank: int                        # 排名 (1-3)
    title: str                       # 标题（板块或个股名称）
    reason: str                      # 一句话理由
    
    # 历史表现
    win_rate_30d: float              # 30天胜率
    win_rate_90d: float              # 90天胜率
    avg_return: float                # 平均收益率
    max_drawdown: float              # 最大回撤
    
    # 推荐股票
    recommended_stocks: List[str]    # 推荐股票代码列表
    
    # 回测数据
    backtest_trades: int             # 回测交易次数
    backtest_wins: int               # 回测成功次数
```

**数据库表结构**:
```sql
CREATE TABLE actionable_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id TEXT NOT NULL,         -- 关联到 post_market_reviews.id
    rank INTEGER,
    title TEXT,
    reason TEXT,
    win_rate_30d REAL,
    avg_return REAL,
    recommended_stocks_json TEXT,    -- JSON数组
    FOREIGN KEY (review_id) REFERENCES post_market_reviews(id)
);
```


---

## API Specifications

### 1. GET /api/post-market-review

获取最新的盘后复盘报告

**Request**:
```http
GET /api/post-market-review?date=2024-01-15
```

**Query Parameters**:
- `date` (optional): 指定日期，格式YYYY-MM-DD，默认为最新交易日

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "id": "2024-01-15",
    "date": "2024-01-15",
    "market_sentiment": {
      "status": "hot",
      "status_cn": "情绪火热",
      "recommendation": "大胆操作",
      "explanation": "今日涨停120只，连板高度7板，成交额1.2万亿",
      "limit_up_count": 120,
      "limit_down_count": 15,
      "max_consecutive_limit_up": 7,
      "turnover_billion": 12000
    },
    "portfolio_health": [],
    "actionable_insights": [
      {
        "rank": 1,
        "title": "新能源汽车板块",
        "reason": "国产替代逻辑加强，资金流入明显",
        "win_rate_30d": 0.65,
        "avg_return": 0.082,
        "recommended_stocks": ["sz.002594", "sz.300750"]
      }
    ],
    "generated_at": "2024-01-15T20:00:00",
    "status": "completed"
  }
}
```

**Error Response** (404):
```json
{
  "success": false,
  "error": "报告未生成",
  "message": "2024-01-15的复盘报告尚未生成，请稍后再试"
}
```

### 2. POST /api/portfolio/import

导入用户持仓

**Request**:
```http
POST /api/portfolio/import
Content-Type: application/json

{
  "user_id": "user123",
  "portfolios": [
    {
      "code": "sh.600519",
      "name": "贵州茅台",
      "cost_price": 1350.00,
      "shares": 100
    },
    {
      "code": "sz.002129",
      "cost_price": 8.75,
      "shares": 1000
    }
  ]
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "imported": 2,
    "failed": 0,
    "portfolio_health": [
      {
        "code": "sh.600519",
        "name": "贵州茅台",
        "status": "green",
        "status_cn": "健康",
        "recommendation": "趋势向上，建议继续持有",
        "current_price": 1377.00,
        "cost_price": 1350.00,
        "profit_rate": 0.02,
        "ma20_deviation": 0.052
      }
    ]
  }
}
```

### 3. POST /api/insights/subscribe

订阅明日提醒

**Request**:
```http
POST /api/insights/subscribe
Content-Type: application/json

{
  "user_id": "user123",
  "insight_id": 1,
  "notification_type": "app_push",
  "notification_time": "09:15"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "subscription_id": "sub_123",
    "scheduled_at": "2024-01-16T09:15:00"
  }
}
```

### 4. POST /api/post-market-review/generate (Internal)

手动触发复盘报告生成（用于测试）

**Request**:
```http
POST /api/post-market-review/generate
Content-Type: application/json

{
  "date": "2024-01-15",
  "force": true
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "data": {
    "review_id": "2024-01-15",
    "status": "completed",
    "generated_at": "2024-01-15T20:00:00",
    "duration_seconds": 180
  }
}
```


---

## Algorithm Details

### Module 1: Market Sentiment Calculator

**算法逻辑**:

```python
def calculate_market_sentiment(date: str) -> MarketSentiment:
    """
    计算市场情绪
    
    步骤:
    1. 获取当日所有股票的涨跌停数据
    2. 计算连板高度（最高连续涨停天数）
    3. 获取两市成交额
    4. 根据规则判断市场情绪
    """
    
    # 1. 获取涨跌停数据
    limit_up_count = count_limit_up_stocks(date)
    limit_down_count = count_limit_down_stocks(date)
    
    # 2. 计算连板高度
    max_consecutive = calculate_max_consecutive_limit_up(date)
    
    # 3. 获取成交额
    total_turnover = get_total_market_turnover(date)
    turnover_billion = total_turnover / 1e8
    
    # 4. 判断情绪
    if limit_up_count > 100 and max_consecutive > 5 and turnover_billion > 10000:
        status = "hot"
        status_cn = "情绪火热"
        recommendation = "大胆操作"
        explanation = f"今日涨停{limit_up_count}只，连板高度{max_consecutive}板，成交额{turnover_billion:.1f}亿"
    
    elif limit_down_count > 100 or turnover_billion < 5000:
        status = "cold"
        status_cn = "情绪冰点"
        recommendation = "等待机会"
        explanation = f"今日跌停{limit_down_count}只，成交额仅{turnover_billion:.0f}亿"
    
    else:
        status = "neutral"
        status_cn = "情绪平淡"
        recommendation = "按兵不动"
        explanation = f"市场波动不大，成交额{turnover_billion:.0f}亿"
    
    return MarketSentiment(...)
```

**数据来源**:
- 涨跌停数据: 从 `daily_data` 统一表查询，条件: `pct_chg >= 9.9` (涨停) 或 `pct_chg <= -9.9` (跌停)
- 连板高度: 遍历所有涨停股票，向前查询连续涨停天数
- 成交额: 从 `daily_data` 统一表聚合 `amount` 字段

**性能优化**:
- 使用SQL聚合查询，避免逐个查询
- 缓存当日结果，避免重复计算

### Module 2: Portfolio Health Checker

**算法逻辑**:

```python
def check_portfolio_health(portfolios: List[Portfolio], date: str) -> List[PortfolioHealth]:
    """
    检查持仓健康
    
    步骤:
    1. 获取每只股票的最新价格和技术指标
    2. 使用 ma_crossover 策略判断趋势
    3. 使用 volume_shrink 策略判断成交量
    4. 综合判断健康状态
    """
    
    results = []
    
    for portfolio in portfolios:
        code = portfolio.code
        cost_price = portfolio.cost_price
        
        # 1. 获取最新数据
        df = db.get_daily_data(code, end_date=date)
        if df.empty:
            continue
        
        df = df.tail(25)  # 最近25天（计算20日均线）
        
        # 2. 计算技术指标
        df['ma20'] = df['close'].rolling(window=20).mean()
        df['volume_ma5'] = df['volume'].rolling(window=5).mean()
        
        latest = df.iloc[-1]
        current_price = latest['close']
        ma20 = latest['ma20']
        
        # 3. 使用策略判断
        ma_signal = check_ma_crossover_signal(df)
        volume_signal = check_volume_shrink_signal(df)
        
        # 4. 计算偏离度
        ma20_deviation = (current_price - ma20) / ma20
        change_rate = latest['pct_chg'] / 100
        profit_rate = (current_price - cost_price) / cost_price
        
        # 5. 判断健康状态
        if ma_signal == "up" and volume_signal == "normal":
            status = "green"
            status_cn = "健康"
            recommendation = "趋势向上，建议继续持有"
        
        elif ma_signal == "flat" and volume_signal == "shrink":
            status = "yellow"
            status_cn = "警示"
            recommendation = "出现缩量滞涨，建议减仓规避风险"
        
        elif ma_signal == "down" or change_rate < -0.05:
            status = "red"
            status_cn = "危险"
            recommendation = "破位下跌，触发系统止损阈值，建议立即止损"
        
        else:
            status = "yellow"
            status_cn = "警示"
            recommendation = "观察中，注意风险"
        
        results.append(PortfolioHealth(...))
    
    # 按危险程度排序（红灯优先）
    results.sort(key=lambda x: {"red": 0, "yellow": 1, "green": 2}[x.status])
    
    return results
```

**策略集成**:

```python
def check_ma_crossover_signal(df: pd.DataFrame) -> str:
    """
    使用 ma_crossover 策略判断趋势
    
    Returns:
        "up": 上涨趋势（价格在20日均线以上）
        "flat": 横盘（价格在20日均线附近）
        "down": 下跌趋势（价格在20日均线以下）
    """
    latest = df.iloc[-1]
    ma20 = latest['ma20']
    price = latest['close']
    
    deviation = (price - ma20) / ma20
    
    if deviation > 0.02:  # 偏离度 > 2%
        return "up"
    elif deviation < -0.02:
        return "down"
    else:
        return "flat"


def check_volume_shrink_signal(df: pd.DataFrame) -> str:
    """
    使用 volume_shrink 策略判断成交量
    
    Returns:
        "normal": 成交量正常
        "shrink": 成交量萎缩
        "expand": 成交量放大
    """
    latest = df.iloc[-1]
    volume = latest['volume']
    volume_ma5 = latest['volume_ma5']
    
    ratio = volume / volume_ma5
    
    if ratio < 0.7:  # 缩量 > 30%
        return "shrink"
    elif ratio > 1.3:  # 放量 > 30%
        return "expand"
    else:
        return "normal"
```

### Module 3: Actionable Insights Generator

**算法逻辑**:

```python
def generate_actionable_insights(date: str, market_sentiment: str) -> List[ActionableInsight]:
    """
    生成明日锦囊
    
    步骤:
    1. 运行回测引擎，计算所有策略的历史表现
    2. 过滤低胜率的策略
    3. 结合市场情绪筛选
    4. 排序并取前3
    """
    
    # 1. 运行回测引擎
    backtest_results = run_backtest_for_all_strategies(date)
    
    # 2. 过滤低胜率
    candidates = []
    for result in backtest_results:
        if result.win_rate_30d > 0.5 and result.avg_return > 0.05:
            candidates.append(result)
    
    # 3. 结合市场情绪
    if market_sentiment == "hot":
        # 火热市场：优先推荐高动量策略
        candidates = [c for c in candidates if c.momentum_score > 0.6]
    elif market_sentiment == "cold":
        # 冰点市场：优先推荐防御性策略
        candidates = [c for c in candidates if c.defensive_score > 0.7]
    else:
        # 平淡市场：推荐稳健策略
        candidates = [c for c in candidates if c.stability_score > 0.6]
    
    # 4. 计算综合得分
    for candidate in candidates:
        candidate.score = (
            candidate.win_rate_30d * 0.4 +
            candidate.avg_return * 0.3 +
            (1 - candidate.max_drawdown) * 0.3
        )
    
    # 5. 排序并取前3
    candidates.sort(key=lambda x: x.score, reverse=True)
    top_3 = candidates[:3]
    
    # 6. 生成推荐
    insights = []
    for rank, candidate in enumerate(top_3, start=1):
        insight = ActionableInsight(
            rank=rank,
            title=candidate.title,
            reason=generate_reason(candidate, market_sentiment),
            win_rate_30d=candidate.win_rate_30d,
            avg_return=candidate.avg_return,
            recommended_stocks=candidate.top_stocks[:3]
        )
        insights.append(insight)
    
    return insights
```

**回测策略**:

```python
def run_backtest_for_all_strategies(date: str) -> List[BacktestResult]:
    """
    运行所有策略的回测
    
    策略列表:
    1. ma_crossover: 均线突破策略
    2. volume_shrink: 缩量三连跌策略
    """
    
    results = []
    
    # 回测时间范围：过去90天
    end_date = date
    start_date = (datetime.strptime(date, '%Y-%m-%d') - timedelta(days=90)).strftime('%Y-%m-%d')
    
    # 策略1: ma_crossover
    ma_strategy = MACrossoverStrategy(db)
    ma_engine = BacktestEngine(db, ma_strategy)
    ma_report = ma_engine.run(start_date, end_date)
    
    if ma_report['total_trades'] > 0:
        results.append(BacktestResult(
            strategy_name="ma_crossover",
            title="均线突破板块",
            win_rate_30d=ma_report['win_rate'],
            avg_return=ma_report['avg_profit_rate'],
            max_drawdown=abs(ma_report['max_drawdown']),
            top_stocks=extract_top_stocks(ma_report),
            momentum_score=0.8,  # 高动量
            defensive_score=0.4,
            stability_score=0.6
        ))
    
    # 策略2: volume_shrink
    vs_strategy = VolumeShrinkStrategy(db)
    vs_engine = BacktestEngine(db, vs_strategy)
    vs_report = vs_engine.run(start_date, end_date)
    
    if vs_report['total_trades'] > 0:
        results.append(BacktestResult(
            strategy_name="volume_shrink",
            title="缩量反弹板块",
            win_rate_30d=vs_report['win_rate'],
            avg_return=vs_report['avg_profit_rate'],
            max_drawdown=abs(vs_report['max_drawdown']),
            top_stocks=extract_top_stocks(vs_report),
            momentum_score=0.5,
            defensive_score=0.7,  # 高防御
            stability_score=0.8   # 高稳定
        ))
    
    return results
```


---

## Scheduler Implementation

### 自动触发流程

```python
# scripts/post_market_scheduler.py

import schedule
import time
from datetime import datetime
from src.business.post_market.review_generator import PostMarketReviewGenerator

def is_trading_day(date: str) -> bool:
    """检查是否为交易日"""
    # 从数据库查询指数数据，如果有数据说明是交易日
    df = db.get_daily_data('sh.000001', start_date=date, end_date=date)
    return not df.empty


def generate_post_market_review():
    """生成盘后复盘报告"""
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 检查是否为交易日
    if not is_trading_day(today):
        logger.info(f"{today} 非交易日，跳过")
        return
    
    logger.info(f"开始生成 {today} 的盘后复盘报告...")
    
    try:
        generator = PostMarketReviewGenerator(db)
        review = generator.generate(date=today)
        
        logger.info(f"✅ 报告生成成功: {review.id}")
        
    except Exception as e:
        logger.error(f"❌ 报告生成失败: {e}")
        send_alert(f"盘后复盘报告生成失败: {e}")


def main():
    """主函数"""
    # 每天下午4:05自动触发（数据同步完成后）
    schedule.every().day.at("16:05").do(generate_post_market_review)
    
    logger.info("盘后复盘调度器已启动")
    logger.info("触发时间: 每天 16:05")
    
    while True:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次


if __name__ == '__main__':
    main()
```

### 重试机制

```python
def generate_post_market_review_with_retry(max_retries=3):
    """带重试的报告生成"""
    for attempt in range(max_retries):
        try:
            generate_post_market_review()
            return
        except Exception as e:
            logger.warning(f"第 {attempt + 1} 次尝试失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(60)  # 等待1分钟后重试
            else:
                logger.error("所有重试均失败")
                send_alert("盘后复盘报告生成失败（已重试3次）")
```

### 超时处理

```python
import signal
from contextlib import contextmanager

@contextmanager
def timeout(seconds):
    """超时上下文管理器"""
    def timeout_handler(signum, frame):
        raise TimeoutError("操作超时")
    
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    try:
        yield
    finally:
        signal.alarm(0)


def generate_with_timeout():
    """带超时的报告生成"""
    try:
        with timeout(3600):  # 1小时超时
            generate_post_market_review()
    except TimeoutError:
        logger.error("报告生成超时（1小时）")
        send_alert("盘后复盘报告生成超时")
```

---

## Frontend Component Specifications

### Component 1: MarketSentiment (市场体温计)

**组件结构**:
```tsx
// frontend/src/components/post_market/MarketSentiment.tsx

interface MarketSentimentProps {
  sentiment: {
    status: 'hot' | 'cold' | 'neutral';
    status_cn: string;
    recommendation: string;
    explanation: string;
    limit_up_count: number;
    limit_down_count: number;
    turnover_billion: number;
  };
}

export const MarketSentiment: React.FC<MarketSentimentProps> = ({ sentiment }) => {
  const getStatusColor = () => {
    switch (sentiment.status) {
      case 'hot': return '#FF4444';    // 红色
      case 'cold': return '#4488FF';   // 蓝色
      case 'neutral': return '#888888'; // 灰色
    }
  };
  
  return (
    <div className="market-sentiment-card">
      <div className="status-indicator" style={{ backgroundColor: getStatusColor() }}>
        <div className="status-icon">🌡️</div>
        <div className="status-text">{sentiment.status_cn}</div>
      </div>
      
      <div className="recommendation">
        {sentiment.recommendation}
      </div>
      
      <div className="explanation">
        {sentiment.explanation}
      </div>
      
      <div className="metrics">
        <div className="metric">
          <span className="label">涨停</span>
          <span className="value">{sentiment.limit_up_count}</span>
        </div>
        <div className="metric">
          <span className="label">跌停</span>
          <span className="value">{sentiment.limit_down_count}</span>
        </div>
        <div className="metric">
          <span className="label">成交额</span>
          <span className="value">{sentiment.turnover_billion.toFixed(0)}亿</span>
        </div>
      </div>
    </div>
  );
};
```

**样式设计**:
```css
/* frontend/src/components/post_market/MarketSentiment.css */

.market-sentiment-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.status-indicator {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
  border-radius: 12px;
  margin-bottom: 16px;
}

.status-icon {
  font-size: 48px;
  margin-right: 16px;
}

.status-text {
  font-size: 36px;
  font-weight: bold;
  color: white;
}

.recommendation {
  font-size: 24px;
  font-weight: 600;
  text-align: center;
  margin-bottom: 12px;
}

.explanation {
  font-size: 16px;
  color: #666;
  text-align: center;
  margin-bottom: 24px;
}

.metrics {
  display: flex;
  justify-content: space-around;
}

.metric {
  text-align: center;
}

.metric .label {
  display: block;
  font-size: 14px;
  color: #999;
  margin-bottom: 4px;
}

.metric .value {
  display: block;
  font-size: 20px;
  font-weight: bold;
}
```

### Component 2: PortfolioHealth (持仓体检)

**组件结构**:
```tsx
// frontend/src/components/post_market/PortfolioHealth.tsx

interface PortfolioHealthProps {
  portfolios: Array<{
    code: string;
    name: string;
    status: 'green' | 'yellow' | 'red';
    status_cn: string;
    recommendation: string;
    current_price: number;
    cost_price: number;
    profit_rate: number;
    ma20_deviation: number;
  }>;
  onImport: () => void;
}

export const PortfolioHealth: React.FC<PortfolioHealthProps> = ({ portfolios, onImport }) => {
  const getStatusEmoji = (status: string) => {
    switch (status) {
      case 'green': return '🟢';
      case 'yellow': return '🟡';
      case 'red': return '🔴';
    }
  };
  
  if (portfolios.length === 0) {
    return (
      <div className="portfolio-health-card">
        <h2>持仓自动体检</h2>
        <div className="empty-state">
          <p>还没有导入持仓</p>
          <button onClick={onImport} className="import-button">
            导入持仓
          </button>
        </div>
      </div>
    );
  }
  
  return (
    <div className="portfolio-health-card">
      <div className="header">
        <h2>持仓自动体检</h2>
        <button onClick={onImport} className="import-button-small">
          重新导入
        </button>
      </div>
      
      <div className="portfolio-list">
        {portfolios.map((portfolio) => (
          <div key={portfolio.code} className={`portfolio-item status-${portfolio.status}`}>
            <div className="status-emoji">{getStatusEmoji(portfolio.status)}</div>
            
            <div className="stock-info">
              <div className="stock-name">
                {portfolio.name} ({portfolio.code})
              </div>
              <div className="stock-metrics">
                <span>现价: ¥{portfolio.current_price.toFixed(2)}</span>
                <span className={portfolio.profit_rate >= 0 ? 'profit' : 'loss'}>
                  {portfolio.profit_rate >= 0 ? '+' : ''}
                  {(portfolio.profit_rate * 100).toFixed(2)}%
                </span>
                <span>偏离20日线: {(portfolio.ma20_deviation * 100).toFixed(1)}%</span>
              </div>
            </div>
            
            <div className="recommendation">
              {portfolio.recommendation}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Component 3: ActionableInsights (明日锦囊)

**组件结构**:
```tsx
// frontend/src/components/post_market/ActionableInsights.tsx

interface ActionableInsightsProps {
  insights: Array<{
    rank: number;
    title: string;
    reason: string;
    win_rate_30d: number;
    avg_return: number;
    recommended_stocks: string[];
  }>;
  onSubscribe: (insightId: number) => void;
  onAddToWatchlist: (insightId: number) => void;
}

export const ActionableInsights: React.FC<ActionableInsightsProps> = ({
  insights,
  onSubscribe,
  onAddToWatchlist
}) => {
  return (
    <div className="actionable-insights-card">
      <h2>明日锦囊</h2>
      
      <div className="insights-list">
        {insights.map((insight) => (
          <div key={insight.rank} className="insight-item">
            <div className="rank-badge">【{insight.rank}】</div>
            
            <div className="insight-content">
              <h3>{insight.title}</h3>
              <p className="reason">{insight.reason}</p>
              
              <div className="performance">
                <span className="win-rate">
                  历史胜率: {(insight.win_rate_30d * 100).toFixed(0)}%
                </span>
                <span className="avg-return">
                  平均收益: +{(insight.avg_return * 100).toFixed(1)}%
                </span>
              </div>
              
              <div className="recommended-stocks">
                推荐股票: {insight.recommended_stocks.join(', ')}
              </div>
              
              <div className="actions">
                <button 
                  onClick={() => onAddToWatchlist(insight.rank)}
                  className="action-button primary"
                >
                  加入明日关注
                </button>
                <button 
                  onClick={() => onSubscribe(insight.rank)}
                  className="action-button secondary"
                >
                  设置闹钟
                </button>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
```

### Main Page: PostMarketReview

**页面结构**:
```tsx
// frontend/src/pages/PostMarketReview.tsx

export const PostMarketReview: React.FC = () => {
  const [review, setReview] = useState<PostMarketReviewData | null>(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    loadReview();
  }, []);
  
  const loadReview = async () => {
    try {
      const response = await fetch('/api/post-market-review');
      const data = await response.json();
      setReview(data.data);
    } catch (error) {
      console.error('加载失败:', error);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <div className="loading">加载中...</div>;
  }
  
  if (!review) {
    return <div className="error">报告未生成</div>;
  }
  
  return (
    <div className="post-market-review-page">
      <header>
        <h1>盘后复盘</h1>
        <div className="date">{review.date}</div>
      </header>
      
      <div className="modules">
        <MarketSentiment sentiment={review.market_sentiment} />
        <PortfolioHealth 
          portfolios={review.portfolio_health}
          onImport={() => {/* 导入逻辑 */}}
        />
        <ActionableInsights 
          insights={review.actionable_insights}
          onSubscribe={(id) => {/* 订阅逻辑 */}}
          onAddToWatchlist={(id) => {/* 加入关注逻辑 */}}
        />
      </div>
    </div>
  );
};
```

---

## Performance Optimization

### 1. 数据缓存

```python
# src/web/cache_manager.py

class PostMarketReviewCache:
    """盘后复盘报告缓存"""
    
    def __init__(self):
        self.cache = {}
        self.ttl = 3600  # 1小时
    
    def get(self, date: str) -> Optional[Dict]:
        """获取缓存"""
        if date in self.cache:
            cached_data, timestamp = self.cache[date]
            if time.time() - timestamp < self.ttl:
                return cached_data
        return None
    
    def set(self, date: str, data: Dict):
        """设置缓存"""
        self.cache[date] = (data, time.time())
```

### 2. 数据库索引

```sql
-- 为常用查询添加索引
CREATE INDEX idx_daily_data_date ON daily_data(date);
CREATE INDEX idx_daily_data_code_date ON daily_data(code, date);
CREATE INDEX idx_daily_data_pct_chg ON daily_data(pct_chg);
```

### 3. 批量查询

```python
# 使用统一表批量查询，避免逐个查询
codes = [p.code for p in portfolios]
df_all = db.get_stock_data_batch_unified(codes, start_date=start_date, end_date=end_date)
```

---

## Security Considerations

### 1. API认证

```python
# 使用JWT认证
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route('/api/post-market-review')
@jwt_required()
def get_post_market_review():
    user_id = get_jwt_identity()
    # ...
```

### 2. 数据加密

```python
# 用户持仓数据加密存储
from cryptography.fernet import Fernet

def encrypt_portfolio(data: Dict) -> str:
    cipher = Fernet(SECRET_KEY)
    return cipher.encrypt(json.dumps(data).encode())

def decrypt_portfolio(encrypted: str) -> Dict:
    cipher = Fernet(SECRET_KEY)
    return json.loads(cipher.decrypt(encrypted.encode()))
```

### 3. 输入验证

```python
# 验证用户输入
def validate_portfolio_input(data: Dict) -> bool:
    required_fields = ['code', 'cost_price', 'shares']
    
    for field in required_fields:
        if field not in data:
            return False
    
    # 验证股票代码格式
    if not re.match(r'^(sh|sz)\.\d{6}$', data['code']):
        return False
    
    # 验证价格和股数
    if data['cost_price'] <= 0 or data['shares'] <= 0:
        return False
    
    return True
```

---

## Testing Strategy

### 1. 单元测试

```python
# tests/test_market_sentiment.py

def test_calculate_market_sentiment_hot():
    """测试火热市场情绪"""
    calculator = MarketSentimentCalculator(db)
    sentiment = calculator.calculate('2024-01-15')
    
    assert sentiment.status == 'hot'
    assert sentiment.limit_up_count > 100
    assert sentiment.turnover_billion > 10000


def test_calculate_market_sentiment_cold():
    """测试冰点市场情绪"""
    calculator = MarketSentimentCalculator(db)
    sentiment = calculator.calculate('2024-01-16')
    
    assert sentiment.status == 'cold'
    assert sentiment.limit_down_count > 100 or sentiment.turnover_billion < 5000
```

### 2. 集成测试

```python
# tests/test_post_market_review_api.py

def test_get_post_market_review():
    """测试获取盘后复盘报告API"""
    response = client.get('/api/post-market-review?date=2024-01-15')
    
    assert response.status_code == 200
    data = response.json()
    
    assert data['success'] is True
    assert 'market_sentiment' in data['data']
    assert 'actionable_insights' in data['data']
```

### 3. 性能测试

```python
# tests/test_performance.py

def test_review_generation_time():
    """测试报告生成时间"""
    start_time = time.time()
    
    generator = PostMarketReviewGenerator(db)
    review = generator.generate('2024-01-15')
    
    duration = time.time() - start_time
    
    assert duration < 300  # 5分钟内完成
```

---

## Deployment

### 1. 环境配置

```bash
# .env
DATABASE_PATH=data/trading.db
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret
ALERT_EMAIL=admin@example.com
```

### 2. 启动脚本

```bash
# start_post_market_system.sh

#!/bin/bash

# 启动后端API
python src/web/app.py &

# 启动调度器
python scripts/post_market_scheduler.py &

# 启动前端
cd frontend && npm start &

echo "盘后复盘系统已启动"
```

### 3. 监控

```python
# scripts/monitor.py

def check_system_health():
    """检查系统健康状态"""
    checks = {
        'api': check_api_health(),
        'scheduler': check_scheduler_health(),
        'database': check_database_health()
    }
    
    if not all(checks.values()):
        send_alert(f"系统健康检查失败: {checks}")
```

---

## Summary

本设计文档定义了盘后复盘系统的完整技术架构，包括：

1. **3个核心模块**: 市场情绪、持仓健康、明日锦囊
2. **4个API接口**: 获取报告、导入持仓、订阅提醒、手动生成
3. **3个前端组件**: MarketSentiment、PortfolioHealth、ActionableInsights
4. **自动化调度**: 每天16:05自动触发，20:00前完成
5. **性能优化**: 缓存、索引、批量查询
6. **安全保障**: 认证、加密、输入验证

下一步：创建 `tasks.md` 文件，将设计拆解为可执行的任务。

# Design Document - 个股诊断系统

## Overview

个股诊断系统是 TradingBuddy 的"决策验证器"模块，为用户提供快速、客观的股票质量评估。系统接收用户输入的股票代码，在 3 秒内返回包含多维度评分、信号灯建议、大白话诊断意见和风险管理指南的完整诊断报告。

**设计目标：**
- 快速响应：3 秒内完成诊断
- 客观中立：基于数据，不带情绪
- 易于理解：用普通话解释技术指标
- 风险优先：先告诉用户风险，再说机会

**核心用户场景：**
1. 朋友推荐股票 → 快速验证是否靠谱
2. 看到小道消息 → 客观评估机会大小
3. 持有股票纠结 → 获得卖出或持有建议
4. 多只股票对比 → 确定优先级

## Architecture

系统采用三层架构：


```
┌─────────────────────────────────────────────────────────────┐
│                     API Layer (Flask)                        │
│  - GET /api/diagnosis/:code (单股诊断)                       │
│  - POST /api/diagnosis/compare (多股对比)                    │
│  - GET /api/diagnosis/history (诊断历史)                     │
│  - GET /api/diagnosis/:id/share (分享链接)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Business Logic Layer                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  StockDiagnosisEngine (核心引擎)                      │   │
│  │  - diagnose_stock(code) → DiagnosisReport           │   │
│  │  - compare_stocks(codes) → ComparisonReport         │   │
│  └──────────────────────────────────────────────────────┘   │
│                              │                               │
│  ┌──────────────┬────────────┴────────────┬──────────────┐  │
│  │              │                         │              │  │
│  ▼              ▼                         ▼              ▼  │
│ ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐│
│ │Technical│  │Liquidity│ │Market  │  │Signal  │  │Risk    ││
│ │Scorer  │  │Scorer   │ │Scorer  │  │Light   │  │Calc    ││
│ └────────┘  └────────┘  └────────┘  └────────┘  └────────┘│
│                              │                               │
│  ┌──────────────────────────┴────────────────────────────┐  │
│  │  PlainLanguageGenerator (大白话生成器)                 │  │
│  │  - generate_diagnosis_text(scores, indicators)        │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│  - Database (stock_data.db)                                  │
│  - StockDataFetcher (复用现有)                               │
│  - StockScoringEngine (复用现有)                             │
│  - StrategyScanner (复用现有)                                │
└─────────────────────────────────────────────────────────────┘
```

**关键设计决策：**
1. 复用现有的 `StockScoringEngine` 和策略扫描逻辑
2. 新增 `StockDiagnosisEngine` 作为诊断专用引擎
3. 使用缓存机制（Redis 或内存缓存）加速重复查询
4. 异步生成分享图片，避免阻塞主请求

## Components and Interfaces

### 1. StockDiagnosisEngine

核心诊断引擎，协调各个评分器并生成最终报告。


**接口定义：**

```python
class StockDiagnosisEngine:
    def diagnose_stock(self, code: str, user_id: Optional[str] = None) -> DiagnosisReport:
        """
        诊断单只股票
        
        Args:
            code: 股票代码（支持 sh.600000 或 600000 格式）
            user_id: 用户 ID（用于记录历史）
            
        Returns:
            DiagnosisReport: 完整的诊断报告
            
        Raises:
            StockNotFoundError: 股票代码不存在
            DataInsufficientError: 数据不足以生成诊断
        """
        
    def compare_stocks(self, codes: List[str]) -> ComparisonReport:
        """
        对比多只股票
        
        Args:
            codes: 股票代码列表（最多 5 只）
            
        Returns:
            ComparisonReport: 对比报告
        """
        
    def get_diagnosis_history(self, user_id: str, limit: int = 30) -> List[DiagnosisRecord]:
        """
        获取用户的诊断历史
        
        Args:
            user_id: 用户 ID
            limit: 返回记录数量
            
        Returns:
            List[DiagnosisRecord]: 诊断历史记录
        """
```

**实现逻辑：**

```python
def diagnose_stock(self, code: str, user_id: Optional[str] = None) -> DiagnosisReport:
    # 1. 标准化股票代码
    normalized_code = self._normalize_code(code)
    
    # 2. 检查缓存（5 分钟有效期）
    cached_report = self.cache.get(f"diagnosis:{normalized_code}")
    if cached_report and not self._is_cache_expired(cached_report):
        return cached_report
    
    # 3. 获取股票数据
    stock_data = self.data_fetcher.get_stock_data(normalized_code, days=90)
    if not stock_data or len(stock_data) < 60:
        raise DataInsufficientError("数据不足，无法生成诊断")
    
    # 4. 并行计算各维度评分
    with ThreadPoolExecutor(max_workers=4) as executor:
        technical_future = executor.submit(self.technical_scorer.score, stock_data)
        liquidity_future = executor.submit(self.liquidity_scorer.score, stock_data)
        market_future = executor.submit(self.market_scorer.score, stock_data)
        risk_future = executor.submit(self.risk_calculator.calculate, stock_data)
    
    technical_score = technical_future.result()
    liquidity_score = liquidity_future.result()
    market_score = market_future.result()
    risk_info = risk_future.result()
    
    # 5. 计算综合评分
    overall_score = (
        technical_score.value * 0.6 +
        liquidity_score.value * 0.2 +
        market_score.value * 0.2
    )
    
    # 6. 生成信号灯
    signal_light = self.signal_evaluator.evaluate(
        overall_score, technical_score, liquidity_score, market_score, risk_info
    )
    
    # 7. 生成大白话诊断意见
    diagnosis_text = self.plain_language_generator.generate(
        stock_data, technical_score, liquidity_score, market_score, signal_light
    )
    
    # 8. 组装诊断报告
    report = DiagnosisReport(
        code=normalized_code,
        name=stock_data.name,
        current_price=stock_data.latest_price,
        overall_score=overall_score,
        technical_score=technical_score,
        liquidity_score=liquidity_score,
        market_score=market_score,
        signal_light=signal_light,
        diagnosis_text=diagnosis_text,
        risk_info=risk_info,
        timestamp=datetime.now()
    )
    
    # 9. 缓存结果
    self.cache.set(f"diagnosis:{normalized_code}", report, ttl=300)
    
    # 10. 记录诊断历史
    if user_id:
        self._save_diagnosis_history(user_id, report)
    
    return report
```

### 2. TechnicalScorer (技术面评分器)

评估股票的技术形态质量。


**接口定义：**

```python
class TechnicalScorer:
    def score(self, stock_data: StockData) -> TechnicalScore:
        """
        计算技术面评分
        
        Args:
            stock_data: 股票数据（至少 60 天）
            
        Returns:
            TechnicalScore: 技术面评分对象
        """
```

**评分逻辑：**

```python
def score(self, stock_data: StockData) -> TechnicalScore:
    score = 50  # 基础分
    reasons = []
    
    # 1. 均线形态（30 分）
    ma5 = stock_data.ma5[-1]
    ma20 = stock_data.ma20[-1]
    ma60 = stock_data.ma60[-1]
    current_price = stock_data.close[-1]
    
    if ma5 > ma20 > ma60:  # 多头排列
        score += 25
        reasons.append("均线呈多头排列，趋势向上")
    elif ma5 < ma20 < ma60:  # 空头排列
        score -= 20
        reasons.append("均线呈空头排列，趋势向下")
    
    if current_price > ma20:
        score += 5
        reasons.append("股价站上 20 日均线")
    else:
        score -= 5
        reasons.append("股价跌破 20 日均线")
    
    # 2. 成交量变化（25 分）
    avg_volume_20 = np.mean(stock_data.volume[-20:])
    recent_volume = stock_data.volume[-1]
    volume_ratio = recent_volume / avg_volume_20
    
    if volume_ratio > 2.0:  # 放量突破
        score += 20
        reasons.append(f"成交量放大 {volume_ratio:.1f} 倍，资金活跃")
    elif volume_ratio > 1.5:
        score += 10
        reasons.append(f"成交量温和放大 {volume_ratio:.1f} 倍")
    elif volume_ratio < 0.5:  # 缩量
        score -= 15
        reasons.append("成交量严重萎缩，资金流出")
    
    # 3. 价格位置（20 分）
    high_60 = np.max(stock_data.high[-60:])
    low_60 = np.min(stock_data.low[-60:])
    price_position = (current_price - low_60) / (high_60 - low_60)
    
    if price_position > 0.8:  # 接近高位
        score += 10
        reasons.append("股价接近近期高点，强势")
    elif price_position < 0.3:  # 接近低位
        score += 15
        reasons.append("股价处于近期低位，安全边际高")
    
    # 4. MACD 指标（15 分）
    macd_hist = stock_data.macd_hist[-1]
    if macd_hist > 0 and stock_data.macd_hist[-2] <= 0:  # 金叉
        score += 15
        reasons.append("MACD 金叉，买入信号")
    elif macd_hist < 0 and stock_data.macd_hist[-2] >= 0:  # 死叉
        score -= 15
        reasons.append("MACD 死叉，卖出信号")
    
    # 5. RSI 指标（10 分）
    rsi = stock_data.rsi[-1]
    if 30 < rsi < 70:  # 正常区间
        score += 5
    elif rsi > 80:  # 超买
        score -= 10
        reasons.append("RSI 超买，注意回调风险")
    elif rsi < 20:  # 超卖
        score += 10
        reasons.append("RSI 超卖，可能反弹")
    
    # 限制评分范围 [0, 100]
    score = max(0, min(100, score))
    
    return TechnicalScore(
        value=score,
        reasons=reasons,
        indicators={
            "ma5": ma5,
            "ma20": ma20,
            "ma60": ma60,
            "volume_ratio": volume_ratio,
            "price_position": price_position,
            "macd_hist": macd_hist,
            "rsi": rsi
        }
    )
```

### 3. LiquidityScorer (流动性评分器)

评估股票的流动性质量，识别"死水股"。


**接口定义：**

```python
class LiquidityScorer:
    def score(self, stock_data: StockData) -> LiquidityScore:
        """
        计算流动性评分
        
        Args:
            stock_data: 股票数据
            
        Returns:
            LiquidityScore: 流动性评分对象
        """
```

**评分逻辑：**

```python
def score(self, stock_data: StockData) -> LiquidityScore:
    score = 50  # 基础分
    reasons = []
    
    # 1. 日均成交额（60 分）
    avg_amount_20 = np.mean(stock_data.amount[-20:])  # 最近 20 天平均成交额
    
    if avg_amount_20 > 500_000_000:  # 5 亿以上
        score += 40
        reasons.append(f"日均成交额 {avg_amount_20/100_000_000:.1f} 亿，流动性优秀")
    elif avg_amount_20 > 100_000_000:  # 1-5 亿
        score += 25
        reasons.append(f"日均成交额 {avg_amount_20/100_000_000:.1f} 亿，流动性良好")
    elif avg_amount_20 > 50_000_000:  # 5000 万-1 亿
        score += 10
        reasons.append(f"日均成交额 {avg_amount_20/100_000_000:.1f} 亿，流动性一般")
    else:  # 5000 万以下
        score -= 30
        reasons.append(f"日均成交额仅 {avg_amount_20/100_000_000:.2f} 亿，流动性不足")
    
    # 2. 换手率（20 分）
    turnover_rate = stock_data.turnover_rate[-1]
    
    if 2 < turnover_rate < 10:  # 正常换手率
        score += 15
        reasons.append(f"换手率 {turnover_rate:.2f}%，交易活跃")
    elif turnover_rate > 15:  # 过高
        score -= 10
        reasons.append(f"换手率 {turnover_rate:.2f}%，过度投机")
    elif turnover_rate < 1:  # 过低
        score -= 15
        reasons.append(f"换手率 {turnover_rate:.2f}%，交易清淡")
    
    # 3. 成交额稳定性（20 分）
    amount_std = np.std(stock_data.amount[-20:])
    amount_cv = amount_std / avg_amount_20  # 变异系数
    
    if amount_cv < 0.5:  # 稳定
        score += 15
        reasons.append("成交额稳定，资金持续关注")
    elif amount_cv > 1.5:  # 波动大
        score -= 10
        reasons.append("成交额波动大，资金不稳定")
    
    # 限制评分范围 [0, 100]
    score = max(0, min(100, score))
    
    return LiquidityScore(
        value=score,
        reasons=reasons,
        indicators={
            "avg_amount_20": avg_amount_20,
            "turnover_rate": turnover_rate,
            "amount_cv": amount_cv
        }
    )
```

### 4. MarketEnvironmentScorer (市场环境评分器)

评估大盘和板块环境是否适合操作。

**接口定义：**

```python
class MarketEnvironmentScorer:
    def score(self, stock_data: StockData) -> MarketScore:
        """
        计算市场环境评分
        
        Args:
            stock_data: 股票数据（包含所属板块信息）
            
        Returns:
            MarketScore: 市场环境评分对象
        """
```

**评分逻辑：**

```python
def score(self, stock_data: StockData) -> MarketScore:
    score = 50  # 基础分
    reasons = []
    
    # 1. 大盘状态（50 分）
    index_data = self.data_fetcher.get_index_data("sh.000001", days=60)  # 上证指数
    index_price = index_data.close[-1]
    index_ma20 = index_data.ma20[-1]
    index_ma60 = index_data.ma60[-1]
    
    if index_price > index_ma20:
        score += 25
        reasons.append("大盘站上 20 日均线，市场环境良好")
    else:
        score -= 20
        reasons.append("大盘跌破 20 日均线，市场环境偏弱")
    
    if index_ma20 > index_ma60:
        score += 15
        reasons.append("大盘均线多头排列")
    else:
        score -= 10
        reasons.append("大盘均线空头排列")
    
    # 2. 板块表现（30 分）
    sector = stock_data.sector
    if sector:
        sector_data = self.data_fetcher.get_sector_data(sector, days=20)
        sector_change = (sector_data.close[-1] - sector_data.close[-20]) / sector_data.close[-20]
        
        if sector_change > 0.05:  # 板块上涨 5% 以上
            score += 25
            reasons.append(f"{sector}板块近期上涨 {sector_change*100:.1f}%，板块强势")
        elif sector_change < -0.05:  # 板块下跌 5% 以上
            score -= 20
            reasons.append(f"{sector}板块近期下跌 {sector_change*100:.1f}%，板块疲弱")
    
    # 3. 市场成交量（20 分）
    market_volume = index_data.volume[-1]
    avg_market_volume = np.mean(index_data.volume[-20:])
    volume_ratio = market_volume / avg_market_volume
    
    if volume_ratio > 1.2:
        score += 15
        reasons.append("市场成交量放大，资金活跃")
    elif volume_ratio < 0.8:
        score -= 10
        reasons.append("市场成交量萎缩，观望情绪浓厚")
    
    # 限制评分范围 [0, 100]
    score = max(0, min(100, score))
    
    return MarketScore(
        value=score,
        reasons=reasons,
        indicators={
            "index_price": index_price,
            "index_ma20": index_ma20,
            "sector_change": sector_change if sector else None,
            "market_volume_ratio": volume_ratio
        }
    )
```

### 5. SignalLightEvaluator (信号灯评估器)

基于综合评分和风险因素生成红绿灯建议。


**接口定义：**

```python
class SignalLightEvaluator:
    def evaluate(
        self,
        overall_score: float,
        technical_score: TechnicalScore,
        liquidity_score: LiquidityScore,
        market_score: MarketScore,
        risk_info: RiskInfo
    ) -> SignalLight:
        """
        生成信号灯评价
        
        Args:
            overall_score: 综合评分
            technical_score: 技术面评分
            liquidity_score: 流动性评分
            market_score: 市场环境评分
            risk_info: 风险信息
            
        Returns:
            SignalLight: 信号灯对象（RED/YELLOW/GREEN）
        """
```

**评估逻辑：**

```python
def evaluate(self, overall_score, technical_score, liquidity_score, market_score, risk_info) -> SignalLight:
    # 1. 强制红灯条件（一票否决）
    if risk_info.is_st_stock:
        return SignalLight(
            color="RED",
            label="建议回避",
            reason="ST 股票存在退市风险",
            confidence=0
        )
    
    if liquidity_score.value < 30:
        return SignalLight(
            color="RED",
            label="建议回避",
            reason="流动性严重不足，可能难以卖出",
            confidence=0
        )
    
    if risk_info.consecutive_losses >= 2:
        return SignalLight(
            color="RED",
            label="建议回避",
            reason="公司连续亏损，财务风险高",
            confidence=0
        )
    
    # 2. 基于综合评分判断
    if overall_score >= 70:
        # 绿灯：建议关注或买入
        confidence = min(100, overall_score)
        return SignalLight(
            color="GREEN",
            label="可以关注",
            reason=self._generate_green_reason(technical_score, liquidity_score, market_score),
            confidence=confidence
        )
    
    elif overall_score >= 40:
        # 黄灯：建议观望
        confidence = overall_score
        return SignalLight(
            color="YELLOW",
            label="建议观望",
            reason=self._generate_yellow_reason(technical_score, liquidity_score, market_score),
            confidence=confidence
        )
    
    else:
        # 红灯：建议回避或卖出
        confidence = 100 - overall_score
        return SignalLight(
            color="RED",
            label="建议回避",
            reason=self._generate_red_reason(technical_score, liquidity_score, market_score),
            confidence=confidence
        )

def _generate_green_reason(self, technical, liquidity, market):
    reasons = []
    if technical.value >= 70:
        reasons.append("技术形态良好")
    if liquidity.value >= 60:
        reasons.append("流动性充足")
    if market.value >= 60:
        reasons.append("市场环境支持")
    return "，".join(reasons) + "，可以考虑关注"

def _generate_yellow_reason(self, technical, liquidity, market):
    weak_points = []
    if technical.value < 60:
        weak_points.append("技术面偏弱")
    if liquidity.value < 50:
        weak_points.append("流动性一般")
    if market.value < 50:
        weak_points.append("市场环境不佳")
    return "，".join(weak_points) + "，建议等待更好的时机"

def _generate_red_reason(self, technical, liquidity, market):
    problems = []
    if technical.value < 40:
        problems.append("技术形态破坏")
    if liquidity.value < 40:
        problems.append("流动性不足")
    if market.value < 40:
        problems.append("市场环境恶劣")
    return "，".join(problems) + "，不建议操作"
```

### 6. RiskCalculator (风险计算器)

计算止损止盈价位和风险等级。

**接口定义：**

```python
class RiskCalculator:
    def calculate(self, stock_data: StockData) -> RiskInfo:
        """
        计算风险信息
        
        Args:
            stock_data: 股票数据
            
        Returns:
            RiskInfo: 风险信息对象
        """
```

**计算逻辑：**

```python
def calculate(self, stock_data: StockData) -> RiskInfo:
    current_price = stock_data.close[-1]
    
    # 1. 计算波动率（用于调整止损止盈）
    returns = np.diff(stock_data.close[-60:]) / stock_data.close[-60:-1]
    volatility = np.std(returns) * np.sqrt(252)  # 年化波动率
    
    # 2. 根据波动率调整止损止盈比例
    if volatility > 0.5:  # 高波动
        stop_loss_pct = -0.10  # -10%
        take_profit_pct = 0.20  # +20%
        risk_level = "HIGH"
    elif volatility > 0.3:  # 中等波动
        stop_loss_pct = -0.08  # -8%
        take_profit_pct = 0.15  # +15%
        risk_level = "MEDIUM"
    else:  # 低波动
        stop_loss_pct = -0.06  # -6%
        take_profit_pct = 0.12  # +12%
        risk_level = "LOW"
    
    # 3. 计算具体价位
    stop_loss_price = current_price * (1 + stop_loss_pct)
    take_profit_price = current_price * (1 + take_profit_pct)
    
    # 4. 计算盈亏比
    risk_reward_ratio = abs(take_profit_pct / stop_loss_pct)
    
    # 5. 检查风险因素
    is_st_stock = stock_data.name.startswith("ST") or stock_data.name.startswith("*ST")
    consecutive_losses = self._check_consecutive_losses(stock_data.code)
    has_major_litigation = self._check_litigation(stock_data.code)
    
    # 6. 调整风险等级
    if is_st_stock or consecutive_losses >= 2:
        risk_level = "EXTREME"
    
    return RiskInfo(
        current_price=current_price,
        stop_loss_price=stop_loss_price,
        take_profit_price=take_profit_price,
        stop_loss_pct=stop_loss_pct,
        take_profit_pct=take_profit_pct,
        risk_reward_ratio=risk_reward_ratio,
        volatility=volatility,
        risk_level=risk_level,
        is_st_stock=is_st_stock,
        consecutive_losses=consecutive_losses,
        has_major_litigation=has_major_litigation
    )
```

### 7. PlainLanguageGenerator (大白话生成器)

将技术指标转换为普通人能理解的自然语言。


**接口定义：**

```python
class PlainLanguageGenerator:
    def generate(
        self,
        stock_data: StockData,
        technical_score: TechnicalScore,
        liquidity_score: LiquidityScore,
        market_score: MarketScore,
        signal_light: SignalLight
    ) -> str:
        """
        生成大白话诊断意见
        
        Args:
            stock_data: 股票数据
            technical_score: 技术面评分
            liquidity_score: 流动性评分
            market_score: 市场环境评分
            signal_light: 信号灯
            
        Returns:
            str: 大白话诊断文本
        """
```

**生成逻辑：**

```python
def generate(self, stock_data, technical_score, liquidity_score, market_score, signal_light) -> str:
    sections = []
    
    # 1. 开场白（基于信号灯）
    if signal_light.color == "GREEN":
        opening = f"从客观数据看，{stock_data.name}目前表现不错。"
    elif signal_light.color == "YELLOW":
        opening = f"从客观数据看，{stock_data.name}目前处于观望期。"
    else:
        opening = f"从客观数据看，{stock_data.name}目前存在一些问题。"
    
    sections.append(opening)
    
    # 2. 技术面描述
    tech_text = self._describe_technical(technical_score, stock_data)
    sections.append(tech_text)
    
    # 3. 资金面描述
    liquidity_text = self._describe_liquidity(liquidity_score, stock_data)
    sections.append(liquidity_text)
    
    # 4. 市场环境描述
    market_text = self._describe_market(market_score)
    sections.append(market_text)
    
    # 5. 建议操作
    suggestion = self._generate_suggestion(signal_light, technical_score, liquidity_score)
    sections.append(suggestion)
    
    return "\n\n".join(sections)

def _describe_technical(self, technical_score, stock_data):
    """描述技术面"""
    volume_ratio = technical_score.indicators["volume_ratio"]
    ma5 = technical_score.indicators["ma5"]
    ma20 = technical_score.indicators["ma20"]
    current_price = stock_data.close[-1]
    
    if technical_score.value >= 70:
        if volume_ratio > 2.0:
            return f"技术面上，股价目前是 {current_price:.2f} 元，短期均线（{ma5:.2f}）已经突破长期均线（{ma20:.2f}），而且成交量突然放大了 {volume_ratio:.1f} 倍，说明有资金在进场。"
        else:
            return f"技术面上，股价目前是 {current_price:.2f} 元，均线呈现多头排列，趋势向上，形态比较健康。"
    
    elif technical_score.value < 40:
        if volume_ratio < 0.5:
            return f"技术面上，股价目前是 {current_price:.2f} 元，短期均线（{ma5:.2f}）已经跌破长期均线（{ma20:.2f}），而且成交量严重萎缩，资金在流出。"
        else:
            return f"技术面上，股价目前是 {current_price:.2f} 元，均线呈现空头排列，趋势向下，形态已经破坏。"
    
    else:
        return f"技术面上，股价目前是 {current_price:.2f} 元，处于横盘整理状态，方向还不明确。"

def _describe_liquidity(self, liquidity_score, stock_data):
    """描述流动性"""
    avg_amount = liquidity_score.indicators["avg_amount_20"]
    turnover = liquidity_score.indicators["turnover_rate"]
    
    if liquidity_score.value >= 60:
        return f"资金面上，这只股票日均成交额有 {avg_amount/100_000_000:.1f} 亿，换手率 {turnover:.2f}%，流动性不错，买卖都比较方便。"
    
    elif liquidity_score.value < 40:
        return f"资金面上，这只股票日均成交额只有 {avg_amount/100_000_000:.2f} 亿，换手率 {turnover:.2f}%，流动性不太好，可能不容易卖出去。"
    
    else:
        return f"资金面上，这只股票日均成交额 {avg_amount/100_000_000:.1f} 亿，流动性一般。"

def _describe_market(self, market_score):
    """描述市场环境"""
    if market_score.value >= 60:
        return "市场环境方面，大盘目前比较稳定，整体环境还不错。"
    elif market_score.value < 40:
        return "市场环境方面，大盘目前比较弱，整体环境不太好，建议谨慎。"
    else:
        return "市场环境方面，大盘目前震荡，没有明确方向。"

def _generate_suggestion(self, signal_light, technical_score, liquidity_score):
    """生成建议"""
    if signal_light.color == "GREEN":
        if technical_score.value >= 80 and liquidity_score.value >= 60:
            return "综合来看，这只股票目前符合我们的选股标准，可以考虑小仓位试探。但记得设好止损，控制风险。"
        else:
            return "综合来看，这只股票目前还可以，可以加入自选继续观察，等待更好的买入时机。"
    
    elif signal_light.color == "YELLOW":
        return "综合来看，这只股票目前还不够明确，建议先观望，等趋势更清晰再做决定。"
    
    else:
        if liquidity_score.value < 40:
            return "综合来看，这只股票目前不太适合操作，特别是流动性不足，建议回避。"
        else:
            return "综合来看，这只股票目前风险较大，不建议操作。如果已经持有，建议考虑止损。"
```

## Data Models

### DiagnosisReport (诊断报告)

```python
@dataclass
class DiagnosisReport:
    code: str  # 股票代码
    name: str  # 股票名称
    current_price: float  # 当前价格
    change_pct: float  # 涨跌幅
    
    # 评分
    overall_score: float  # 综合评分 (0-100)
    technical_score: TechnicalScore  # 技术面评分
    liquidity_score: LiquidityScore  # 流动性评分
    market_score: MarketScore  # 市场环境评分
    
    # 信号灯
    signal_light: SignalLight  # 红绿灯建议
    
    # 诊断意见
    diagnosis_text: str  # 大白话诊断
    
    # 风险管理
    risk_info: RiskInfo  # 风险信息
    
    # 历史表现
    historical_performance: Optional[HistoricalPerformance] = None
    
    # 元数据
    timestamp: datetime  # 诊断时间
    data_update_time: datetime  # 数据更新时间
    disclaimer: str = "本诊断仅供参考，不构成投资建议。投资者据此操作，风险自担。"
```

### TechnicalScore (技术面评分)

```python
@dataclass
class TechnicalScore:
    value: float  # 评分值 (0-100)
    reasons: List[str]  # 评分理由
    indicators: Dict[str, float]  # 关键指标
```

### LiquidityScore (流动性评分)

```python
@dataclass
class LiquidityScore:
    value: float  # 评分值 (0-100)
    reasons: List[str]  # 评分理由
    indicators: Dict[str, float]  # 关键指标
```

### MarketScore (市场环境评分)

```python
@dataclass
class MarketScore:
    value: float  # 评分值 (0-100)
    reasons: List[str]  # 评分理由
    indicators: Dict[str, Any]  # 关键指标
```

### SignalLight (信号灯)

```python
@dataclass
class SignalLight:
    color: str  # RED/YELLOW/GREEN
    label: str  # 建议标签（如"可以关注"）
    reason: str  # 信号理由
    confidence: float  # 信号强度 (0-100)
```

### RiskInfo (风险信息)

```python
@dataclass
class RiskInfo:
    current_price: float  # 当前价格
    stop_loss_price: float  # 止损价位
    take_profit_price: float  # 止盈价位
    stop_loss_pct: float  # 止损百分比
    take_profit_pct: float  # 止盈百分比
    risk_reward_ratio: float  # 盈亏比
    volatility: float  # 波动率
    risk_level: str  # 风险等级 (LOW/MEDIUM/HIGH/EXTREME)
    
    # 风险因素
    is_st_stock: bool  # 是否 ST 股
    consecutive_losses: int  # 连续亏损年数
    has_major_litigation: bool  # 是否有重大诉讼
    warnings: List[str]  # 风险警告列表
```


## Correctness Properties

A property is a characteristic or behavior that should hold true across all valid executions of a system—essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.

### Property 1: Stock Code Normalization

*For any* valid stock code input (with or without exchange prefix), the system should normalize it to a standard format (e.g., "sh.600000" or "sz.000001").

**Validates: Requirements 1.2**

### Property 2: Stock Name Resolution

*For any* valid stock name, the system should return the correct stock code that matches that name.

**Validates: Requirements 1.3**

### Property 3: Fuzzy Search Completeness

*For any* partial keyword that matches at least one stock, the system should return a non-empty list of candidates where each candidate's name or code contains the keyword.

**Validates: Requirements 1.4**

### Property 4: Score Range Validity

*For any* stock data, all generated scores (technical, liquidity, market, overall) should be within the range [0, 100].

**Validates: Requirements 2.1, 2.2, 2.3**

### Property 5: Weighted Average Correctness

*For any* diagnosis report, the overall score should equal (technical_score * 0.6 + liquidity_score * 0.2 + market_score * 0.2), within a small tolerance for floating-point precision.

**Validates: Requirements 2.4, 2.5**

### Property 6: Report Completeness

*For any* successful diagnosis, the report should contain all four scores (technical, liquidity, market, overall) with non-null values.

**Validates: Requirements 2.6**

### Property 7: Missing Data Handling

*For any* diagnosis where a dimension's data is insufficient, the system should mark that dimension as "data insufficient" and adjust the weighting formula accordingly.

**Validates: Requirements 2.8**

### Property 8: Signal Light Consistency

*For any* diagnosis report, the signal light color should be consistent with the overall score: GREEN for score >= 70, YELLOW for score in [40, 70), RED for score < 40, unless overridden by risk factors.

**Validates: Requirements 6.1, 6.2, 6.3, 6.4**

### Property 9: Risk Override

*For any* stock with critical risk factors (ST stock, consecutive losses >= 2, liquidity score < 30), the signal light should be RED regardless of the overall score.

**Validates: Requirements 6.6**

### Property 10: Signal Light Reasoning

*For any* signal light, there should be a non-empty reason string explaining why that signal was generated.

**Validates: Requirements 6.7**

### Property 11: Plain Language Generation

*For any* diagnosis report, the diagnosis text should be non-empty and should not contain technical jargon terms like "MA5", "MA20", "MACD" (should use plain language equivalents instead).

**Validates: Requirements 7.1, 7.2**

### Property 12: Diagnosis Text Completeness

*For any* diagnosis report, the diagnosis text should contain descriptions of at least three aspects: technical status, liquidity status, and market environment.

**Validates: Requirements 7.3, 7.4, 7.5, 7.6, 7.7, 7.8**

### Property 13: Stop Loss Price Validity

*For any* risk calculation, the stop loss price should be less than the current price.

**Validates: Requirements 8.1, 8.3**

### Property 14: Take Profit Price Validity

*For any* risk calculation, the take profit price should be greater than the current price.

**Validates: Requirements 8.2, 8.4**

### Property 15: Risk-Reward Ratio Correctness

*For any* risk calculation, the risk-reward ratio should equal abs(take_profit_pct) / abs(stop_loss_pct).

**Validates: Requirements 8.7**

### Property 16: Volatility-Based Risk Adjustment

*For any* two stocks where stock A has higher volatility than stock B, stock A should have a wider stop loss percentage (in absolute value) than stock B.

**Validates: Requirements 8.8**

### Property 17: ST Stock Detection

*For any* stock whose name starts with "ST" or "*ST", the system should flag it as an ST stock in the risk info.

**Validates: Requirements 9.1**

### Property 18: ST Stock Warning

*For any* ST stock, the risk info should contain a warning about delisting risk.

**Validates: Requirements 9.2**

### Property 19: Risk Factor Detection

*For any* stock, the system should check for all defined risk factors (ST status, consecutive losses, major litigation) and include them in the risk info warnings list.

**Validates: Requirements 9.3, 9.4, 9.5, 9.6, 9.7**

### Property 20: Extreme Risk Recommendation

*For any* stock with risk level "EXTREME", the signal light should be RED and the recommendation should indicate "not recommended for operation".

**Validates: Requirements 9.10**

### Property 21: Historical Performance Inclusion

*For any* stock that has previous diagnosis records, the diagnosis report should include historical performance data.

**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8**

### Property 22: Comparison Stock Limit

*For any* comparison request, the system should accept up to 5 stocks and reject requests with more than 5 stocks.

**Validates: Requirements 11.1**

### Property 23: Comparison Report Sorting

*For any* comparison report, the stocks should be sorted in descending order by overall score.

**Validates: Requirements 11.6**

### Property 24: Share Link Generation

*For any* diagnosis report, the system should generate a unique shareable link that, when accessed, returns the same diagnosis data.

**Validates: Requirements 12.1, 12.5, 12.7**

### Property 25: Data Freshness Warning

*For any* diagnosis where the underlying data is more than 24 hours old, the report should include a warning about potentially stale data.

**Validates: Requirements 13.2**

### Property 26: Diagnosis History Persistence

*For any* diagnosis performed with a user_id, the system should save the diagnosis to history and be able to retrieve it later.

**Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8**

### Property 27: Error Handling for Invalid Codes

*For any* invalid stock code, the system should raise a StockNotFoundError with a user-friendly message.

**Validates: Requirements 17.1**

### Property 28: Error Handling for Insufficient Data

*For any* stock with insufficient data (less than 60 days), the system should raise a DataInsufficientError with a user-friendly message.

**Validates: Requirements 17.2**

### Property 29: Disclaimer Inclusion

*For any* diagnosis report, the report should include a disclaimer stating that the diagnosis is for reference only and does not constitute investment advice.

**Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5, 18.6, 18.7**

### Property 30: Data Source Metadata

*For any* diagnosis report, the report should include metadata about data sources, update time, and data coverage.

**Validates: Requirements 19.1, 19.2, 19.3, 19.4, 19.5, 19.6**


## Error Handling

### Error Types

```python
class StockNotFoundError(Exception):
    """股票代码不存在"""
    pass

class DataInsufficientError(Exception):
    """数据不足以生成诊断"""
    pass

class TooManyStocksError(Exception):
    """对比股票数量超过限制"""
    pass

class DataStaleError(Warning):
    """数据过期警告"""
    pass
```

### Error Handling Strategy

1. **输入验证错误**：
   - 股票代码不存在 → 返回 404，提示"未找到该股票"
   - 股票代码格式错误 → 返回 400，提示"股票代码格式不正确"
   - 对比股票超过 5 只 → 返回 400，提示"最多支持对比 5 只股票"

2. **数据不足错误**：
   - K 线数据少于 60 天 → 返回 422，提示"该股票数据不足，无法生成诊断"
   - 基本面数据缺失 → 降低该维度权重，继续诊断，在报告中标注

3. **数据过期警告**：
   - 数据超过 24 小时 → 在报告中显示黄色警告
   - 数据超过 3 天 → 在报告中显示红色警告

4. **系统错误**：
   - 数据库连接失败 → 返回 503，提示"服务暂时不可用"
   - 计算超时 → 返回 504，提示"诊断计算超时，请稍后重试"

### Error Response Format

```json
{
  "error": {
    "code": "STOCK_NOT_FOUND",
    "message": "未找到该股票，请检查股票代码",
    "details": {
      "input_code": "600000",
      "suggestion": "请使用完整代码，如 sh.600000"
    }
  }
}
```

## Testing Strategy

### Unit Testing

使用 pytest 进行单元测试，覆盖以下场景：

1. **评分器测试**：
   - 测试 TechnicalScorer 在不同市场形态下的评分
   - 测试 LiquidityScorer 对不同成交额的评分
   - 测试 MarketEnvironmentScorer 对不同大盘状态的评分
   - 测试边界情况（极端高分、极端低分）

2. **信号灯测试**：
   - 测试不同评分区间的信号灯颜色
   - 测试风险因素的强制红灯逻辑
   - 测试信号灯理由生成

3. **风险计算测试**：
   - 测试止损止盈价格计算
   - 测试波动率调整逻辑
   - 测试 ST 股票的特殊处理

4. **大白话生成测试**：
   - 测试不同评分下的文本生成
   - 测试技术术语的替换
   - 测试文本完整性

5. **错误处理测试**：
   - 测试无效股票代码的错误处理
   - 测试数据不足的错误处理
   - 测试对比股票数量限制

### Property-Based Testing

使用 Hypothesis 进行基于属性的测试，每个测试运行至少 100 次迭代：

1. **Property 1-3: Input Handling**
   - 生成随机股票代码格式，测试标准化
   - 生成随机股票名称，测试解析
   - 生成随机关键词，测试模糊搜索

2. **Property 4-7: Scoring**
   - 生成随机股票数据，测试评分范围
   - 测试加权平均计算
   - 测试报告完整性
   - 测试缺失数据处理

3. **Property 8-12: Signal and Text**
   - 生成随机评分，测试信号灯一致性
   - 测试风险覆盖逻辑
   - 测试大白话生成

4. **Property 13-20: Risk Management**
   - 生成随机价格和波动率，测试止损止盈计算
   - 测试 ST 股票检测
   - 测试风险因素检测

5. **Property 21-30: Advanced Features**
   - 测试历史表现包含
   - 测试对比功能
   - 测试分享链接
   - 测试数据新鲜度
   - 测试历史记录
   - 测试错误处理
   - 测试免责声明
   - 测试数据源元数据

### Integration Testing

测试完整的诊断流程：

1. **端到端诊断测试**：
   - 输入真实股票代码 → 获取完整诊断报告
   - 验证报告包含所有必需字段
   - 验证评分逻辑正确性

2. **对比功能测试**：
   - 输入多只股票 → 获取对比报告
   - 验证排序正确性
   - 验证对比数据完整性

3. **历史记录测试**：
   - 执行诊断 → 保存历史 → 检索历史
   - 验证历史数据完整性

4. **缓存测试**：
   - 首次诊断 → 缓存 → 再次诊断
   - 验证缓存命中
   - 验证缓存过期

### Performance Testing

1. **响应时间测试**：
   - 单股诊断应在 3 秒内完成
   - 5 股对比应在 5 秒内完成

2. **并发测试**：
   - 模拟 100 个并发诊断请求
   - 验证系统稳定性

3. **缓存效果测试**：
   - 测试缓存命中率
   - 测试缓存对响应时间的影响

## API Endpoints

### GET /api/diagnosis/:code

诊断单只股票。

**Request:**
```
GET /api/diagnosis/sh.600000
```

**Response:**
```json
{
  "code": "sh.600000",
  "name": "浦发银行",
  "current_price": 8.50,
  "change_pct": 1.2,
  "overall_score": 72.5,
  "technical_score": {
    "value": 75.0,
    "reasons": ["均线呈多头排列，趋势向上", "成交量放大 2.1 倍，资金活跃"],
    "indicators": {
      "ma5": 8.45,
      "ma20": 8.30,
      "volume_ratio": 2.1
    }
  },
  "liquidity_score": {
    "value": 68.0,
    "reasons": ["日均成交额 3.2 亿，流动性良好"],
    "indicators": {
      "avg_amount_20": 320000000,
      "turnover_rate": 0.85
    }
  },
  "market_score": {
    "value": 72.0,
    "reasons": ["大盘站上 20 日均线，市场环境良好"],
    "indicators": {
      "index_price": 3250.5,
      "index_ma20": 3200.0
    }
  },
  "signal_light": {
    "color": "GREEN",
    "label": "可以关注",
    "reason": "技术形态良好，流动性充足，市场环境支持，可以考虑关注",
    "confidence": 72.5
  },
  "diagnosis_text": "从客观数据看，浦发银行目前表现不错。\n\n技术面上，股价目前是 8.50 元，短期均线（8.45）已经突破长期均线（8.30），而且成交量突然放大了 2.1 倍，说明有资金在进场。\n\n资金面上，这只股票日均成交额有 3.2 亿，换手率 0.85%，流动性不错，买卖都比较方便。\n\n市场环境方面，大盘目前比较稳定，整体环境还不错。\n\n综合来看，这只股票目前符合我们的选股标准，可以考虑小仓位试探。但记得设好止损，控制风险。",
  "risk_info": {
    "current_price": 8.50,
    "stop_loss_price": 7.82,
    "take_profit_price": 9.78,
    "stop_loss_pct": -0.08,
    "take_profit_pct": 0.15,
    "risk_reward_ratio": 1.88,
    "volatility": 0.35,
    "risk_level": "MEDIUM",
    "is_st_stock": false,
    "consecutive_losses": 0,
    "has_major_litigation": false,
    "warnings": []
  },
  "timestamp": "2026-01-02T15:30:00Z",
  "data_update_time": "2026-01-02T15:00:00Z",
  "disclaimer": "本诊断仅供参考，不构成投资建议。投资者据此操作，风险自担。"
}
```

### POST /api/diagnosis/compare

对比多只股票。

**Request:**
```json
{
  "codes": ["sh.600000", "sz.000001", "sh.600036"]
}
```

**Response:**
```json
{
  "stocks": [
    {
      "code": "sh.600000",
      "name": "浦发银行",
      "overall_score": 72.5,
      "signal_light": {"color": "GREEN", "label": "可以关注"},
      "current_price": 8.50,
      "change_pct": 1.2
    },
    {
      "code": "sh.600036",
      "name": "招商银行",
      "overall_score": 68.0,
      "signal_light": {"color": "YELLOW", "label": "建议观望"},
      "current_price": 35.20,
      "change_pct": 0.5
    },
    {
      "code": "sz.000001",
      "name": "平安银行",
      "overall_score": 55.0,
      "signal_light": {"color": "YELLOW", "label": "建议观望"},
      "current_price": 12.30,
      "change_pct": -0.8
    }
  ],
  "recommendation": "建议优先关注 sh.600000（浦发银行），综合评分最高",
  "timestamp": "2026-01-02T15:30:00Z"
}
```

### GET /api/diagnosis/history

获取诊断历史。

**Request:**
```
GET /api/diagnosis/history?user_id=user123&limit=10
```

**Response:**
```json
{
  "history": [
    {
      "id": "diag_123",
      "code": "sh.600000",
      "name": "浦发银行",
      "diagnosis_time": "2026-01-02T15:30:00Z",
      "diagnosis_price": 8.50,
      "current_price": 8.65,
      "change_pct": 1.76,
      "overall_score": 72.5,
      "signal_light": {"color": "GREEN"}
    }
  ],
  "total": 25
}
```

### GET /api/diagnosis/:id/share

获取分享链接的诊断数据。

**Request:**
```
GET /api/diagnosis/diag_123/share
```

**Response:**
```json
{
  "diagnosis": { /* 完整的诊断报告 */ },
  "share_url": "https://tradingbuddy.com/diagnosis/share/diag_123",
  "expires_at": "2026-01-03T15:30:00Z"
}
```

## Implementation Notes

### 复用现有组件

1. **StockDataFetcher**: 复用现有的数据获取逻辑
2. **StockScoringEngine**: 复用现有的评分引擎（技术面评分）
3. **StrategyScanner**: 复用策略扫描逻辑（用于检查是否符合金牌策略）
4. **Database**: 复用现有的数据库连接和查询

### 新增组件

1. **StockDiagnosisEngine**: 新的诊断引擎
2. **LiquidityScorer**: 新的流动性评分器
3. **MarketEnvironmentScorer**: 新的市场环境评分器
4. **SignalLightEvaluator**: 新的信号灯评估器
5. **PlainLanguageGenerator**: 新的大白话生成器
6. **RiskCalculator**: 新的风险计算器

### 数据库 Schema

```sql
-- 诊断历史表
CREATE TABLE diagnosis_history (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    code TEXT NOT NULL,
    name TEXT NOT NULL,
    diagnosis_time TIMESTAMP NOT NULL,
    diagnosis_price REAL NOT NULL,
    overall_score REAL NOT NULL,
    technical_score REAL NOT NULL,
    liquidity_score REAL NOT NULL,
    market_score REAL NOT NULL,
    signal_light TEXT NOT NULL,
    diagnosis_text TEXT NOT NULL,
    risk_info TEXT NOT NULL,  -- JSON
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_user_id (user_id),
    INDEX idx_code (code),
    INDEX idx_diagnosis_time (diagnosis_time)
);

-- 分享链接表
CREATE TABLE diagnosis_shares (
    id TEXT PRIMARY KEY,
    diagnosis_id TEXT NOT NULL,
    share_url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP NOT NULL,
    INDEX idx_diagnosis_id (diagnosis_id)
);
```

### 缓存策略

使用 Redis 或内存缓存：

```python
# 缓存键格式
cache_key = f"diagnosis:{code}:{date}"

# 缓存时间
TTL = 300  # 5 分钟

# 缓存数据
cached_data = {
    "diagnosis_report": report,
    "cached_at": datetime.now()
}
```

### 性能优化

1. **并行计算**: 使用 ThreadPoolExecutor 并行计算各维度评分
2. **数据预加载**: 预加载常用股票的数据
3. **缓存机制**: 缓存诊断结果，避免重复计算
4. **数据库索引**: 在 code、user_id、diagnosis_time 上建立索引
5. **异步生成**: 分享图片异步生成，不阻塞主请求

## Deployment Considerations

1. **API 限流**: 限制每个用户每分钟最多 10 次诊断请求
2. **监控告警**: 监控诊断响应时间，超过 5 秒告警
3. **日志记录**: 记录所有诊断请求和结果，用于分析和优化
4. **A/B 测试**: 支持不同评分算法的 A/B 测试
5. **灰度发布**: 新功能先对 10% 用户开放，逐步扩大


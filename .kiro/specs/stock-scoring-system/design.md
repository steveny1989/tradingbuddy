# Design Document: AI 选股评分与决策辅助系统

## Overview

本设计文档描述了"AI 选股评分与决策辅助系统"的技术架构和实现方案。该系统将现有的二元信号选股机制升级为基于评分的智能决策支持系统，核心目标是为投资者提供更精细、可解释、可追溯的选股建议。

### 核心设计原则

1. **评分优先**：所有信号都必须包含置信度分数（0-100），反映信号强度
2. **可解释性**：每个信号都附带自然语言描述和关键指标快照
3. **性能优先**：使用异步扫描和缓存机制，确保 API 响应速度
4. **数据驱动**：记录所有历史信号，支持回测和策略优化
5. **合规第一**：所有接口包含免责声明，明确系统定位为决策辅助工具

### 系统定位

- **不是**：自动交易系统、投资建议服务
- **是**：数据分析工具、决策参考系统、策略研究平台

## Architecture

### 系统架构图

```mermaid
graph TB
    subgraph "前端层"
        UI[Web UI]
    end
    
    subgraph "API 层"
        API[Flask API]
        SignalAPI[/api/signals]
        HistoryAPI[/api/signals/:id/history]
        StatsAPI[/api/signals/stats]
        ScanAPI[/api/scan/trigger]
    end
    
    subgraph "业务逻辑层"
        ScoringEngine[评分引擎]
        Explainer[信号解释器]
        MultiFilter[多因子筛选器]
        HistoryTracker[历史追踪器]
    end
    
    subgraph "策略层"
        Scanner[策略扫描器]
        MAStrategy[均线策略]
        VolumeStrategy[成交量策略]
        FundamentalFilter[基本面过滤器]
    end
    
    subgraph "数据层"
        DB[(SQLite Database)]
        SignalTable[strategy_signals]
        ScanCache[scan_results]
        FinancialData[financial_indicators]
        DailyData[daily_data]
    end
    
    subgraph "后台任务"
        Scheduler[定时调度器]
        AsyncScanner[异步扫描器]
    end
    
    UI --> API
    API --> SignalAPI
    API --> HistoryAPI
    API --> StatsAPI
    API --> ScanAPI
    
    SignalAPI --> ScoringEngine
    SignalAPI --> Explainer
    SignalAPI --> MultiFilter
    
    HistoryAPI --> HistoryTracker
    StatsAPI --> HistoryTracker
    
    ScanAPI --> AsyncScanner
    
    ScoringEngine --> Scanner
    Explainer --> Scanner
    MultiFilter --> Scanner
    
    Scanner --> MAStrategy
    Scanner --> VolumeStrategy
    Scanner --> FundamentalFilter
    
    MAStrategy --> DailyData
    VolumeStrategy --> DailyData
    FundamentalFilter --> FinancialData
    
    AsyncScanner --> Scanner
    AsyncScanner --> ScanCache
    
    Scheduler --> AsyncScanner
    
    HistoryTracker --> SignalTable
    HistoryTracker --> DailyData
    
    ScoringEngine --> SignalTable
```

### 数据流

1. **扫描流程**：
   - 定时调度器触发异步扫描器
   - 异步扫描器调用策略扫描器
   - 策略扫描器执行技术面+基本面筛选
   - 评分引擎计算置信度分数
   - 信号解释器生成选股理由
   - 结果存储到 scan_results 和 strategy_signals 表

2. **查询流程**：
   - 前端请求 /api/signals
   - API 从 scan_results 缓存表读取
   - 应用多因子筛选器
   - 返回排序后的信号列表

3. **历史追踪流程**：
   - 定时任务查询历史信号
   - 计算信号发出后 N 天的实际涨跌幅
   - 更新 strategy_signals 表的表现数据

## Components and Interfaces

### 1. Stock Scoring Engine（评分引擎）

**职责**：计算信号的置信度分数

**接口**：
```python
class StockScoringEngine:
    def calculate_score(
        self,
        signal: Dict,
        technical_factors: Dict,
        fundamental_factors: Optional[Dict] = None
    ) -> float:
        """
        计算置信度分数（0-100）
        
        Args:
            signal: 原始信号字典
            technical_factors: 技术面因子（成交量比、均线角度等）
            fundamental_factors: 基本面因子（可选）
            
        Returns:
            置信度分数（0-100）
        """
        pass
```

**评分算法**：
```
confidence_score = (
    volume_score * 0.3 +      # 成交量因子权重 30%
    ma_angle_score * 0.25 +   # 均线角度因子权重 25%
    market_env_score * 0.20 + # 大盘环境因子权重 20%
    liquidity_score * 0.15 +  # 流动性因子权重 15%
    fundamental_score * 0.10  # 基本面因子权重 10%
)

# 各因子计算方法：
volume_score = min(100, (volume_ratio - 1) * 50)  # 成交量放大倍数
ma_angle_score = min(100, abs(ma_distance) * 1000)  # 均线距离
market_env_score = 50 + (index_pct_chg * 10)  # 大盘涨跌幅影响
liquidity_score = min(100, (avg_turnover / 1e8) * 10)  # 日均成交额
fundamental_score = 基本面综合评分（ROE、负债率等）
```

### 2. Signal Explainer（信号解释器）

**职责**：生成选股理由的自然语言描述

**接口**：
```python
class SignalExplainer:
    def generate_reason(
        self,
        signal: Dict,
        strategy_name: str
    ) -> str:
        """
        生成选股理由
        
        Args:
            signal: 信号字典（包含所有指标）
            strategy_name: 策略名称
            
        Returns:
            自然语言描述的选股理由
        """
        pass
```

**示例输出**：
```
"5日均线上穿20日均线形成金叉，当日成交量较5日均量放大2.3倍，呈现放量突破态势。
均线距离0.8%，角度适中。大盘环境良好（上证指数+1.2%）。
该股日均成交额1.5亿，流动性充足。"
```

### 3. Multi-Factor Filter（多因子筛选器）

**职责**：支持技术面+基本面联动筛选

**接口**：
```python
class MultiFactorFilter:
    def apply_filters(
        self,
        signals: pd.DataFrame,
        filters: Dict[str, Any]
    ) -> pd.DataFrame:
        """
        应用多因子筛选
        
        Args:
            signals: 信号DataFrame
            filters: 筛选条件字典
                {
                    'industry': str,  # 行业
                    'pe_min': float,  # 最小市盈率
                    'pe_max': float,  # 最大市盈率
                    'pct_chg_5d_min': float,  # 5日涨跌幅下限
                    'pct_chg_5d_max': float,  # 5日涨跌幅上限
                    'min_cap': float,  # 最小市值
                    'max_cap': float,  # 最大市值
                    'min_turnover': float,  # 最小成交额
                    'score_min': float,  # 最小置信度分数
                }
            
        Returns:
            筛选后的信号DataFrame
        """
        pass
    
    def apply_fundamental_filters(
        self,
        code: str,
        db: StockDatabase
    ) -> bool:
        """
        应用基本面过滤器
        
        Args:
            code: 股票代码
            db: 数据库实例
            
        Returns:
            True表示通过过滤，False表示被过滤
        """
        pass
```

**基本面过滤规则**：
1. 排除连续两年亏损的股票
2. 排除资产负债率 > 80% 的股票
3. 排除商誉占净资产比例 > 50% 的股票
4. 排除 ST、*ST 股票

### 4. Signal History Tracker（历史追踪器）

**职责**：记录和验证历史选股效果

**接口**：
```python
class SignalHistoryTracker:
    def save_signal(
        self,
        signal: Dict,
        strategy_name: str
    ) -> str:
        """
        保存信号到历史记录
        
        Args:
            signal: 信号字典
            strategy_name: 策略名称
            
        Returns:
            信号ID
        """
        pass
    
    def calculate_performance(
        self,
        signal_id: str,
        windows: List[int] = [3, 5, 10]
    ) -> Dict[int, Dict]:
        """
        计算信号的历史表现
        
        Args:
            signal_id: 信号ID
            windows: 时间窗口列表（天数）
            
        Returns:
            {
                3: {'return': 2.5, 'hit': True},
                5: {'return': 4.2, 'hit': True},
                10: {'return': -1.3, 'hit': False}
            }
        """
        pass
    
    def get_strategy_stats(
        self,
        strategy_name: str,
        start_date: str = None,
        end_date: str = None
    ) -> Dict:
        """
        获取策略整体统计数据
        
        Args:
            strategy_name: 策略名称
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            {
                'total_signals': int,
                'hit_rate_3d': float,
                'hit_rate_5d': float,
                'hit_rate_10d': float,
                'avg_return_3d': float,
                'avg_return_5d': float,
                'avg_return_10d': float,
                'best_signal': Dict,
                'worst_signal': Dict
            }
        """
        pass
```

### 5. Strategy Scanner（策略扫描器）

**职责**：执行股票池扫描并生成信号

**接口**：
```python
class StrategyScanner:
    def scan_with_scoring(
        self,
        strategy: BaseStrategy,
        date: str = None,
        apply_fundamental_filter: bool = True,
        **kwargs
    ) -> pd.DataFrame:
        """
        扫描股票池并计算评分
        
        Args:
            strategy: 策略实例
            date: 扫描日期
            apply_fundamental_filter: 是否应用基本面过滤
            **kwargs: 其他参数
            
        Returns:
            包含评分和理由的信号DataFrame
        """
        pass
```

**增强的信号字段**：
```python
{
    'code': str,
    'name': str,
    'date': str,
    'price': float,
    'confidence_score': float,  # 新增：置信度分数
    'reason': str,  # 新增：选股理由
    'ma_short': float,
    'ma_long': float,
    'ma_distance': float,
    'volume': float,
    'volume_ma': float,
    'volume_ratio': float,
    'market_cap': float,
    'pe_ttm': float,  # 新增：市盈率
    'pb': float,  # 新增：市净率
    'roe': float,  # 新增：净资产收益率
    'debt_ratio': float,  # 新增：资产负债率
    'signal_type': str,
    'strategy_name': str
}
```

### 6. Async Scanner（异步扫描器）

**职责**：后台执行扫描任务

**接口**：
```python
class AsyncScanner:
    def trigger_scan(
        self,
        strategy_name: str,
        params: Dict
    ) -> str:
        """
        触发异步扫描任务
        
        Args:
            strategy_name: 策略名称
            params: 扫描参数
            
        Returns:
            任务ID
        """
        pass
    
    def get_scan_status(
        self,
        task_id: str
    ) -> Dict:
        """
        查询扫描任务状态
        
        Args:
            task_id: 任务ID
            
        Returns:
            {
                'status': 'pending' | 'running' | 'completed' | 'failed',
                'progress': float,  # 0-100
                'total_stocks': int,
                'scanned_stocks': int,
                'signals_found': int,
                'error': str
            }
        """
        pass
```

## Data Models

### 数据库表设计

#### 1. strategy_signals（策略信号表）

```sql
CREATE TABLE strategy_signals (
    id TEXT PRIMARY KEY,  -- UUID
    code TEXT NOT NULL,
    name TEXT,
    date TEXT NOT NULL,
    price REAL,
    confidence_score REAL,  -- 置信度分数（0-100）
    reason TEXT,  -- 选股理由
    strategy_name TEXT NOT NULL,
    strategy_params TEXT,  -- JSON格式的策略参数
    
    -- 技术指标快照
    ma_short REAL,
    ma_long REAL,
    ma_distance REAL,
    volume REAL,
    volume_ma REAL,
    volume_ratio REAL,
    
    -- 基本面指标快照
    market_cap REAL,
    pe_ttm REAL,
    pb REAL,
    roe REAL,
    debt_ratio REAL,
    
    -- 表现数据（后续更新）
    return_3d REAL,
    return_5d REAL,
    return_10d REAL,
    hit_3d INTEGER,  -- 0或1
    hit_5d INTEGER,
    hit_10d INTEGER,
    performance_updated_at TEXT,
    
    created_at TEXT NOT NULL,
    
    INDEX idx_code_date (code, date),
    INDEX idx_strategy_date (strategy_name, date),
    INDEX idx_score (confidence_score DESC)
);
```

#### 2. scan_results（扫描结果缓存表）

```sql
CREATE TABLE scan_results (
    id TEXT PRIMARY KEY,  -- UUID
    strategy_name TEXT NOT NULL,
    scan_date TEXT NOT NULL,
    scan_params TEXT,  -- JSON格式
    
    -- 扫描结果（JSON格式存储信号列表）
    signals TEXT,  -- JSON array
    
    total_scanned INTEGER,
    signals_found INTEGER,
    scan_duration REAL,  -- 秒
    
    created_at TEXT NOT NULL,
    
    INDEX idx_strategy_date (strategy_name, scan_date DESC)
);
```

#### 3. scan_tasks（扫描任务表）

```sql
CREATE TABLE scan_tasks (
    task_id TEXT PRIMARY KEY,
    strategy_name TEXT NOT NULL,
    params TEXT,  -- JSON格式
    status TEXT NOT NULL,  -- pending, running, completed, failed
    progress REAL DEFAULT 0,  -- 0-100
    
    total_stocks INTEGER,
    scanned_stocks INTEGER,
    signals_found INTEGER,
    
    error_message TEXT,
    
    created_at TEXT NOT NULL,
    started_at TEXT,
    completed_at TEXT,
    
    INDEX idx_status (status),
    INDEX idx_created (created_at DESC)
);
```

#### 4. 扩展 market_cap_data 表

```sql
-- 添加行业字段
ALTER TABLE market_cap_data ADD COLUMN industry TEXT;

-- 创建行业索引
CREATE INDEX IF NOT EXISTS idx_industry ON market_cap_data(industry);
```

## Correctness Properties

*属性是系统应该在所有有效执行中保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性作为人类可读规范和机器可验证正确性保证之间的桥梁。*

### Property 1: 评分范围有效性

*For any* 生成的信号，其置信度分数应该在 0 到 100 之间（包含边界）

**Validates: Requirements 1.1**

### Property 2: 评分单调性

*For any* 两个信号 A 和 B，如果 A 的技术指标（成交量比、均线角度等）都优于 B，则 A 的置信度分数应该高于或等于 B

**Validates: Requirements 1.2**

### Property 3: 低分信号过滤

*For any* API 返回的信号列表，所有信号的置信度分数应该大于或等于 30

**Validates: Requirements 1.4**

### Property 4: 信号排序正确性

*For any* API 返回的信号列表，信号应该按照置信度分数降序排列

**Validates: Requirements 1.3**

### Property 5: 理由字段完整性

*For any* 生成的信号，reason 字段应该是非空字符串且包含关键词（如"均线"、"成交量"等）

**Validates: Requirements 2.1, 2.2, 2.3, 2.4**

### Property 6: 多因子筛选交集性

*For any* 提供的多个筛选条件，返回的信号应该同时满足所有条件

**Validates: Requirements 3.6**

### Property 7: 基本面数据缺失容错

*For any* 基本面数据缺失的股票，系统应该跳过该股票而不是抛出异常

**Validates: Requirements 3.7**

### Property 8: 历史信号持久化

*For any* 扫描生成的信号，该信号应该被存储到 strategy_signals 表中

**Validates: Requirements 4.1, 4.2**

### Property 9: 表现计算准确性

*For any* 历史信号，其 N 天后的收益率应该等于 (price_after_N_days - signal_price) / signal_price

**Validates: Requirements 4.3, 4.4**

### Property 10: 缓存读取优先

*For any* /api/signals 请求，系统应该优先从 scan_results 表读取而不是实时扫描

**Validates: Requirements 5.3**

### Property 11: 扫描任务幂等性

*For any* 相同的策略和参数，多次触发扫描应该产生相同的结果（在同一交易日内）

**Validates: Requirements 5.1, 5.2**

### Property 12: 免责声明存在性

*For any* API 响应，应该包含 disclaimer 字段且内容包含"不构成任何投资建议"

**Validates: Requirements 8.1, 8.2, 8.3, 8.4**

### Property 13: 基本面过滤规则

*For any* 启用基本面过滤的扫描，返回的信号不应包含连续两年亏损或资产负债率超过 80% 的股票

**Validates: Requirements 7.1, 7.2, 7.3**

### Property 14: 数据库写入重试

*For any* 数据库写入失败，系统应该重试最多 3 次

**Validates: Requirements 10.4**

### Property 15: 性能指标快照完整性

*For any* 存储的信号，应该包含完整的技术指标快照（ma_short, ma_long, volume_ratio 等）

**Validates: Requirements 10.2**

## Error Handling

### 错误分类

1. **数据缺失错误**：
   - 基本面数据不可用 → 记录警告，跳过该股票
   - 历史价格数据不足 → 跳过该股票
   - 大盘指数数据缺失 → 使用默认环境分数（50）

2. **计算错误**：
   - 除零错误 → 使用默认值或跳过
   - NaN 值 → 过滤或使用默认值

3. **数据库错误**：
   - 写入失败 → 重试 3 次，记录错误日志
   - 查询失败 → 返回空结果，记录错误

4. **API 错误**：
   - 参数验证失败 → 返回 400 错误和详细说明
   - 内部错误 → 返回 500 错误，记录堆栈

### 错误响应格式

```python
{
    "success": False,
    "error": {
        "code": "INVALID_PARAMETER",
        "message": "置信度分数范围必须在 0-100 之间",
        "details": {
            "parameter": "score_min",
            "provided_value": 150,
            "valid_range": [0, 100]
        }
    },
    "disclaimer": "本工具仅供科研与数据参考，不构成任何投资建议。投资者据此操作，风险自担。"
}
```

## Testing Strategy

### 单元测试

使用 pytest 框架，测试覆盖：

1. **评分引擎测试**：
   - 测试各因子计算逻辑
   - 测试边界值（0, 100）
   - 测试异常输入处理

2. **信号解释器测试**：
   - 测试理由生成逻辑
   - 测试关键词包含
   - 测试空值处理

3. **多因子筛选器测试**：
   - 测试单一条件筛选
   - 测试多条件交集
   - 测试基本面过滤规则

4. **历史追踪器测试**：
   - 测试信号保存
   - 测试表现计算
   - 测试统计数据生成

### 属性测试

使用 Hypothesis 框架，最少 100 次迭代：

1. **Property 1: 评分范围有效性**
   ```python
   @given(
       volume_ratio=st.floats(min_value=0.5, max_value=10),
       ma_distance=st.floats(min_value=-0.1, max_value=0.1),
       # ... 其他因子
   )
   def test_score_range(volume_ratio, ma_distance, ...):
       score = scoring_engine.calculate_score(...)
       assert 0 <= score <= 100
   ```

2. **Property 4: 信号排序正确性**
   ```python
   @given(signals=st.lists(st.dictionaries(...), min_size=2))
   def test_signal_sorting(signals):
       sorted_signals = api.get_signals(...)
       scores = [s['confidence_score'] for s in sorted_signals]
       assert scores == sorted(scores, reverse=True)
   ```

3. **Property 6: 多因子筛选交集性**
   ```python
   @given(
       filters=st.dictionaries(
           keys=st.sampled_from(['pe_min', 'pe_max', 'min_cap']),
           values=st.floats(min_value=0, max_value=1000)
       )
   )
   def test_multi_factor_filter(filters):
       results = multi_filter.apply_filters(signals, filters)
       for result in results:
           for key, value in filters.items():
               assert satisfies_condition(result, key, value)
   ```

### 集成测试

1. **端到端扫描测试**：
   - 触发扫描 → 等待完成 → 验证结果存储
   - 查询 API → 验证返回数据格式和内容

2. **历史追踪测试**：
   - 保存信号 → 等待 N 天 → 计算表现 → 验证准确性

3. **性能测试**：
   - 扫描 1000 只股票 → 验证在 5 分钟内完成
   - API 响应时间 → 验证在 2 秒内返回

### 测试数据

使用真实的历史数据进行测试，确保：
- 覆盖不同市场环境（牛市、熊市、震荡市）
- 覆盖不同行业和市值范围
- 包含数据缺失的边界情况

## Implementation Notes

### 性能优化建议

1. **数据库索引**：
   - 在 strategy_signals 表的 (code, date) 上创建复合索引
   - 在 confidence_score 上创建降序索引

2. **批量查询**：
   - 使用 `get_stock_data_batch_unified` 批量获取历史数据
   - 避免在循环中执行单条查询

3. **向量化计算**：
   - 使用 pandas 的向量化操作计算技术指标
   - 避免使用 Python 循环

4. **缓存策略**：
   - 扫描结果缓存 1 小时
   - 基本面数据缓存 1 天

### 合规性要求

所有 API 响应必须包含：
```python
"disclaimer": "本工具仅供科研与数据参考，不构成任何投资建议。投资者据此操作，风险自担。"
```

前端页面必须在显著位置展示免责声明。

### 扩展性考虑

1. **策略插件化**：
   - 所有策略继承 BaseStrategy
   - 支持动态加载新策略

2. **评分算法可配置**：
   - 因子权重可通过配置文件调整
   - 支持 A/B 测试不同评分算法

3. **多数据源支持**：
   - 基本面数据可从多个 API 获取
   - 支持数据源降级和容错

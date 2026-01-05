# 数据层架构设计

## 概述

实施三层数据架构，确保数据质量和系统稳定性。

## 架构设计

```
data/
├── raw/              # 原始数据层 (ODS - Operational Data Store)
│   ├── daily_raw.db      # 日线原始数据
│   ├── financial_raw.db  # 财务原始数据
│   └── market_raw.db     # 市场数据（资金流、北向等）
│
├── cleaned/          # 清洗数据层 (DWD - Data Warehouse Detail)
│   ├── daily_cleaned.db      # 验证后的日线数据
│   ├── financial_cleaned.db  # 验证后的财务数据
│   └── market_cleaned.db     # 验证后的市场数据
│
└── aggregated/       # 聚合数据层 (DWS - Data Warehouse Service)
    ├── indicators.db     # 预计算的技术指标
    ├── features.db       # 特征工程数据
    └── cache.db          # 高频访问缓存

# 兼容层（逐步废弃）
├── stock_data.db     # 旧的分表数据库
└── a_share.db        # 当前主数据库
```

## 数据流

```
API (AKShare/TuShare)
    ↓
[Raw Layer] - 原样存储，不做任何修改
    ↓
[DataValidator] - 验证、清洗、标准化
    ↓
[Cleaned Layer] - 可信的干净数据
    ↓
[FeatureEngine] - 计算指标、特征
    ↓
[Aggregated Layer] - 预计算结果
    ↓
Business Logic (诊断、策略等)
```

## 1. Raw Layer (原始层)

### 职责
- 存储从API获取的原始数据，不做任何修改
- 保留完整的数据血缘（来源、时间戳）
- 作为数据恢复的最后防线

### 表结构

#### daily_raw (日线原始数据)
```sql
CREATE TABLE daily_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    amount REAL,
    -- 元数据
    source TEXT NOT NULL,           -- 数据来源: akshare, tushare
    fetched_at TEXT NOT NULL,       -- 获取时间
    raw_json TEXT,                  -- 原始JSON（可选）
    UNIQUE(code, date, source)
);
CREATE INDEX idx_daily_raw_code_date ON daily_raw(code, date);
```

#### financial_raw (财务原始数据)
```sql
CREATE TABLE financial_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,
    report_date TEXT NOT NULL,
    report_type TEXT,               -- Q1, Q2, Q3, annual
    -- 原始字段（保持API返回的原始列名）
    raw_data TEXT NOT NULL,         -- JSON格式存储所有字段
    -- 元数据
    source TEXT NOT NULL,
    fetched_at TEXT NOT NULL,
    UNIQUE(code, report_date, source)
);
CREATE INDEX idx_financial_raw_code_date ON financial_raw(code, report_date);
```

## 2. Cleaned Layer (清洗层)

### 职责
- 存储经过验证和标准化的数据
- 统一字段命名和数据类型
- 标记异常数据但不删除
- 业务逻辑的主要数据源

### 验证规则

#### 日线数据验证
```python
class DailyDataValidator:
    """日线数据验证器"""
    
    @staticmethod
    def validate_price_logic(row):
        """价格逻辑验证"""
        errors = []
        
        # 基本逻辑
        if row['high'] < row['low']:
            errors.append('high < low')
        if row['high'] < row['open']:
            errors.append('high < open')
        if row['high'] < row['close']:
            errors.append('high < close')
        if row['low'] > row['open']:
            errors.append('low > open')
        if row['low'] > row['close']:
            errors.append('low > close')
        
        # 价格必须为正
        if row['open'] <= 0 or row['high'] <= 0 or row['low'] <= 0 or row['close'] <= 0:
            errors.append('negative_price')
        
        return errors
    
    @staticmethod
    def validate_volume(row):
        """成交量验证"""
        errors = []
        
        # 成交量不能为负
        if row['volume'] < 0:
            errors.append('negative_volume')
        
        # 停牌检测：成交量为0且价格不变
        if row['volume'] == 0:
            # 需要与前一日对比
            errors.append('possible_suspension')
        
        return errors
    
    @staticmethod
    def validate_change_limit(row, prev_close):
        """涨跌停验证"""
        if prev_close is None or prev_close <= 0:
            return []
        
        errors = []
        change_pct = (row['close'] - prev_close) / prev_close * 100
        
        # A股涨跌停限制（ST股票±5%，普通股票±10%，科创板/创业板±20%）
        # 这里简化为±15%的异常检测
        if abs(change_pct) > 15:
            errors.append(f'abnormal_change_{change_pct:.2f}%')
        
        return errors
```

### 表结构

#### daily_cleaned (清洗后的日线数据)
```sql
CREATE TABLE daily_cleaned (
    code TEXT NOT NULL,
    date TEXT NOT NULL,
    -- 标准化字段
    open REAL NOT NULL,
    high REAL NOT NULL,
    low REAL NOT NULL,
    close REAL NOT NULL,
    volume REAL NOT NULL,
    amount REAL,
    -- 复权价格
    adj_close REAL,
    -- 数据质量标记
    is_valid BOOLEAN DEFAULT 1,     -- 是否通过验证
    is_suspended BOOLEAN DEFAULT 0, -- 是否停牌
    validation_errors TEXT,         -- 验证错误（JSON数组）
    -- 元数据
    source TEXT NOT NULL,
    raw_id INTEGER,                 -- 关联raw层的ID
    cleaned_at TEXT NOT NULL,
    PRIMARY KEY (code, date)
);
CREATE INDEX idx_daily_cleaned_date ON daily_cleaned(date);
CREATE INDEX idx_daily_cleaned_valid ON daily_cleaned(is_valid);
```

#### financial_cleaned (清洗后的财务数据)
```sql
CREATE TABLE financial_cleaned (
    code TEXT NOT NULL,
    report_date TEXT NOT NULL,
    report_type TEXT NOT NULL,
    -- 标准化财务指标
    roe REAL,
    roa REAL,
    net_profit_margin REAL,
    gross_margin REAL,
    debt_to_asset_ratio REAL,
    current_ratio REAL,
    eps REAL,
    revenue REAL,
    net_profit REAL,
    -- 数据质量
    is_valid BOOLEAN DEFAULT 1,
    validation_errors TEXT,
    completeness_score REAL,       -- 数据完整度 0-1
    -- 元数据
    source TEXT NOT NULL,
    raw_id INTEGER,
    cleaned_at TEXT NOT NULL,
    PRIMARY KEY (code, report_date)
);
CREATE INDEX idx_financial_cleaned_date ON financial_cleaned(report_date);
```

## 3. Aggregated Layer (聚合层)

### 职责
- 存储预计算的技术指标
- 存储特征工程结果
- 缓存高频访问的数据
- 提升查询性能

### 表结构

#### technical_indicators (技术指标)
```sql
CREATE TABLE technical_indicators (
    code TEXT NOT NULL,
    date TEXT NOT NULL,
    -- 移动平均线
    ma5 REAL,
    ma10 REAL,
    ma20 REAL,
    ma50 REAL,
    ma200 REAL,
    -- 技术指标
    rsi REAL,
    macd REAL,
    macd_signal REAL,
    macd_hist REAL,
    kdj_k REAL,
    kdj_d REAL,
    kdj_j REAL,
    -- 布林带
    boll_upper REAL,
    boll_middle REAL,
    boll_lower REAL,
    -- 成交量指标
    volume_ma5 REAL,
    volume_ma10 REAL,
    volume_ratio REAL,
    -- 元数据
    calculated_at TEXT NOT NULL,
    PRIMARY KEY (code, date)
);
CREATE INDEX idx_indicators_date ON technical_indicators(date);
```

#### stock_features (股票特征)
```sql
CREATE TABLE stock_features (
    code TEXT NOT NULL,
    date TEXT NOT NULL,
    -- 价格特征
    price_momentum_5d REAL,
    price_momentum_20d REAL,
    volatility_20d REAL,
    -- 成交量特征
    volume_trend_5d REAL,
    volume_spike BOOLEAN,
    -- 相对强弱
    relative_strength_index REAL,
    beta REAL,
    -- 形态特征
    trend TEXT,                     -- uptrend, downtrend, sideways
    support_level REAL,
    resistance_level REAL,
    -- 元数据
    calculated_at TEXT NOT NULL,
    PRIMARY KEY (code, date)
);
```

## 数据处理流程

### 1. 数据采集 (Fetcher)
```python
class DataFetcher:
    """数据采集器 - 写入Raw层"""
    
    def fetch_daily_data(self, code, start_date, end_date):
        """获取日线数据"""
        # 1. 从API获取
        df = akshare.stock_zh_a_hist(symbol=code, ...)
        
        # 2. 写入raw层（原样保存）
        self.save_to_raw(df, source='akshare')
        
        # 3. 触发清洗流程
        self.trigger_cleaning(code, start_date, end_date)
```

### 2. 数据清洗 (Cleaner)
```python
class DataCleaner:
    """数据清洗器 - Raw -> Cleaned"""
    
    def clean_daily_data(self, code, start_date, end_date):
        """清洗日线数据"""
        # 1. 从raw层读取
        raw_data = self.read_from_raw(code, start_date, end_date)
        
        # 2. 验证数据
        validator = DailyDataValidator()
        validated_data = []
        
        for idx, row in raw_data.iterrows():
            errors = []
            errors.extend(validator.validate_price_logic(row))
            errors.extend(validator.validate_volume(row))
            
            validated_data.append({
                **row,
                'is_valid': len(errors) == 0,
                'validation_errors': json.dumps(errors) if errors else None
            })
        
        # 3. 写入cleaned层
        self.save_to_cleaned(validated_data)
        
        # 4. 触发聚合计算
        self.trigger_aggregation(code, start_date, end_date)
```

### 3. 特征计算 (FeatureEngine)
```python
class FeatureEngine:
    """特征计算引擎 - Cleaned -> Aggregated"""
    
    def calculate_indicators(self, code, start_date, end_date):
        """计算技术指标"""
        # 1. 从cleaned层读取
        df = self.read_from_cleaned(code, start_date, end_date)
        
        # 2. 计算指标
        df['ma20'] = df['close'].rolling(20).mean()
        df['rsi'] = self.calculate_rsi(df['close'])
        # ... 更多指标
        
        # 3. 写入aggregated层
        self.save_to_aggregated(df)
```

## 迁移策略

### Phase 1: 建立新架构（不影响现有系统）
1. 创建新的数据库文件
2. 实现Fetcher、Cleaner、FeatureEngine
3. 并行运行，验证数据一致性

### Phase 2: 逐步切换
1. 新数据写入新架构
2. 业务逻辑逐步切换到cleaned层
3. 保留旧数据库作为备份

### Phase 3: 完全迁移
1. 历史数据迁移到新架构
2. 废弃旧数据库
3. 清理冗余代码

## 性能优化

### 1. 批量处理
- 批量写入（每1000条commit一次）
- 批量计算指标（避免逐行处理）

### 2. 增量更新
- 只处理新增/变更的数据
- 使用时间戳追踪更新

### 3. 并行处理
- 多进程处理不同股票
- 异步I/O提升吞吐量

## 监控和维护

### 数据质量监控
```python
class DataQualityMonitor:
    """数据质量监控"""
    
    def check_daily_quality(self):
        """每日数据质量检查"""
        # 1. 检查数据完整性
        missing_stocks = self.check_missing_data()
        
        # 2. 检查验证失败率
        invalid_rate = self.check_invalid_rate()
        
        # 3. 检查异常值
        anomalies = self.check_anomalies()
        
        # 4. 生成报告
        self.generate_report(missing_stocks, invalid_rate, anomalies)
```

### 数据一致性检查
```python
class ConsistencyChecker:
    """数据一致性检查"""
    
    def check_layer_consistency(self):
        """检查各层数据一致性"""
        # Raw vs Cleaned
        raw_count = self.count_raw_records()
        cleaned_count = self.count_cleaned_records()
        
        if raw_count != cleaned_count:
            logger.warning(f"数据不一致: raw={raw_count}, cleaned={cleaned_count}")
```

## 优势

1. **数据可追溯**: Raw层保留原始数据，可随时重新处理
2. **质量保证**: Cleaned层确保数据质量，业务逻辑更可靠
3. **性能优化**: Aggregated层预计算，查询速度快
4. **易于维护**: 职责清晰，修改影响范围小
5. **灵活扩展**: 新增指标只需修改FeatureEngine

## 注意事项

1. **存储空间**: 三层架构会增加存储需求（约2-3倍）
2. **处理延迟**: 数据需要经过多层处理，实时性略降
3. **复杂度**: 架构更复杂，需要良好的文档和监控

## 下一步

1. 实现核心类（Fetcher, Cleaner, FeatureEngine）
2. 创建数据库迁移脚本
3. 编写单元测试
4. 建立监控系统
5. 逐步迁移现有代码

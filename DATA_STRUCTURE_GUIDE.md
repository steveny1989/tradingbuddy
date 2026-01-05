# 股票数据结构指南

**数据库**: `data/a_share.db` (SQLite)  
**更新时间**: 2026-01-04

---

## 📊 数据概览

### 表统计
- **总表数**: ~5,630个
- **股票日线表**: 5,611个 (每只股票一个表)
- **系统表**: 18个
- **新增表**: 3个 (盘后复盘系统)

---

## 🗂️ 核心数据表

### 1. stock_basic - 股票基础信息

**用途**: 存储所有A股的基本信息

**表结构**:
```sql
CREATE TABLE stock_basic (
    code TEXT,           -- 股票代码 (如: 600519)
    name TEXT,           -- 股票名称 (如: 贵州茅台)
    market TEXT,         -- 市场 (sh/sz)
    list_date TEXT,      -- 上市日期
    status TEXT,         -- 状态 (active/delisted)
    updated_at TEXT,     -- 更新时间
    full_code TEXT       -- 完整代码 (如: sh.600519)
);
```

**示例数据**:
```
code    | name      | market | status | full_code
--------|-----------|--------|--------|------------
600519  | 贵州茅台   | sh     | active | sh.600519
000001  | 平安银行   | sz     | active | sz.000001
```

**数据量**: ~5,600只股票

---

### 2. daily_data - 统一日线数据表 ⭐

**用途**: 存储所有股票的日线行情数据（统一表，高性能）

**表结构**:
```sql
CREATE TABLE daily_data (
    code TEXT NOT NULL,      -- 股票代码 (sh.600519)
    date TEXT NOT NULL,      -- 交易日期 (YYYY-MM-DD)
    open REAL,               -- 开盘价
    close REAL,              -- 收盘价
    high REAL,               -- 最高价
    low REAL,                -- 最低价
    volume REAL,             -- 成交量 (股)
    amount REAL,             -- 成交额 (元)
    amplitude REAL,          -- 振幅 (%)
    pct_chg REAL,            -- 涨跌幅 (%)
    change REAL,             -- 涨跌额 (元)
    turnover REAL,           -- 换手率 (%)
    PRIMARY KEY (code, date)
);

-- 索引
CREATE INDEX idx_date_code ON daily_data(date, code);
CREATE INDEX idx_code_date ON daily_data(code, date);
```

**示例数据**:
```
code       | date       | close   | pct_chg | volume    | amount
-----------|------------|---------|---------|-----------|-------------
sh.600519  | 2025-12-31 | 1377.18 | -0.90   | 34766.0   | 4799456452
sh.600519  | 2025-12-30 | 1389.72 | -0.88   | 33792.0   | 4702489813
```

**数据量**: 数千万条记录

**性能优化**:
- 使用复合主键 (code, date)
- 双向索引支持按日期或按股票查询
- 适合批量查询和策略扫描

---

### 3. daily_[code] - 单股票日线表（旧格式）

**用途**: 每只股票一个独立表（兼容旧代码）

**表名格式**: `daily_sh_600519`, `daily_sz_000001`

**表结构**: 与 `daily_data` 相同，但只包含单只股票数据

**数量**: 5,611个表

**注意**: 
- 新代码应优先使用 `daily_data` 统一表
- 旧表保留用于兼容性

---

### 4. market_cap_data - 市值数据

**用途**: 存储股票的市值、估值等实时数据

**表结构**:
```sql
CREATE TABLE market_cap_data (
    code TEXT,              -- 股票代码 (600519)
    name TEXT,              -- 股票名称
    price REAL,             -- 当前价格
    total_cap REAL,         -- 总市值 (元)
    float_cap REAL,         -- 流通市值 (元)
    pe_ttm REAL,            -- 市盈率TTM
    pb REAL,                -- 市净率
    ps_ttm TEXT,            -- 市销率TTM
    total_shares TEXT,      -- 总股本
    float_shares TEXT,      -- 流通股本
    update_date TEXT,       -- 更新日期
    market TEXT,            -- 市场 (sh/sz)
    full_code TEXT,         -- 完整代码
    cap_category TEXT,      -- 市值分类 (大盘股/中盘股/小盘股)
    industry TEXT           -- 行业
);

CREATE INDEX idx_market_cap_industry ON market_cap_data(industry);
```

**示例数据**:
```
code   | name     | price   | total_cap        | pe_ttm | pb   | cap_category
-------|----------|---------|------------------|--------|------|-------------
600519 | 贵州茅台  | 1377.18 | 1724601494694.0  | 20.01  | 7.6  | 超大盘股
```

**市值分类**:
- 超大盘股: > 1000亿
- 大盘股: 200-1000亿
- 中盘股: 50-200亿
- 小盘股: < 50亿

---

### 5. financial_indicators - 财务指标

**用途**: 存储股票的财务指标数据

**表结构**:
```sql
CREATE TABLE financial_indicators (
    code TEXT,                    -- 股票代码
    report_date TEXT,             -- 报告日期
    roe REAL,                     -- 净资产收益率 (%)
    roa REAL,                     -- 总资产收益率 (%)
    gross_margin REAL,            -- 毛利率 (%)
    net_margin REAL,              -- 净利率 (%)
    operating_margin REAL,        -- 营业利润率 (%)
    current_ratio REAL,           -- 流动比率
    quick_ratio REAL,             -- 速动比率
    debt_to_asset_ratio REAL,    -- 资产负债率 (%)
    debt_to_equity_ratio REAL,   -- 产权比率
    asset_turnover REAL,          -- 总资产周转率
    inventory_turnover REAL,      -- 存货周转率
    receivable_turnover REAL,     -- 应收账款周转率
    eps REAL,                     -- 每股收益
    bvps REAL,                    -- 每股净资产
    pe_ratio REAL,                -- 市盈率
    pb_ratio REAL,                -- 市净率
    updated_at TEXT,
    PRIMARY KEY (code, report_date)
);
```

**报告周期**:
- Q1: 一季报 (03-31)
- Q2: 半年报 (06-30)
- Q3: 三季报 (09-30)
- Annual: 年报 (12-31)

---

### 6. balance_sheet - 资产负债表

**用途**: 存储资产负债表数据

**主要字段**:
- 总资产、总负债、股东权益
- 流动资产、非流动资产
- 流动负债、非流动负债

---

### 7. income_statement - 利润表

**用途**: 存储利润表数据

**主要字段**:
- 营业收入、营业成本
- 营业利润、净利润
- 毛利润、销售费用

---

### 8. cash_flow - 现金流量表

**用途**: 存储现金流量表数据

**主要字段**:
- 经营活动现金流
- 投资活动现金流
- 筹资活动现金流

---

## 🆕 盘后复盘系统表

### 9. post_market_reviews - 复盘报告

**用途**: 存储每日盘后复盘报告

**表结构**:
```sql
CREATE TABLE post_market_reviews (
    id TEXT PRIMARY KEY,              -- 报告ID (YYYY-MM-DD)
    date TEXT NOT NULL UNIQUE,        -- 报告日期
    market_sentiment_json TEXT,       -- 市场情绪JSON
    generated_at TEXT,                -- 生成时间
    status TEXT DEFAULT 'pending',    -- 状态
    error_message TEXT                -- 错误信息
);
```

---

### 10. user_portfolios - 用户持仓

**用途**: 存储用户的持仓信息

**表结构**:
```sql
CREATE TABLE user_portfolios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,            -- 用户ID
    code TEXT NOT NULL,               -- 股票代码
    name TEXT,                        -- 股票名称
    cost_price REAL,                  -- 成本价
    shares INTEGER,                   -- 持仓数量
    added_at TEXT,                    -- 添加时间
    UNIQUE(user_id, code)
);
```

---

### 11. actionable_insights - 明日锦囊

**用途**: 存储明日投资建议

**表结构**:
```sql
CREATE TABLE actionable_insights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    review_id TEXT NOT NULL,          -- 关联复盘报告
    rank INTEGER,                     -- 排名 (1-3)
    title TEXT,                       -- 标题
    reason TEXT,                      -- 理由
    win_rate_30d REAL,                -- 30天胜率
    win_rate_90d REAL,                -- 90天胜率
    avg_return REAL,                  -- 平均收益率
    max_drawdown REAL,                -- 最大回撤
    recommended_stocks_json TEXT,     -- 推荐股票JSON
    backtest_trades INTEGER,          -- 回测交易次数
    backtest_wins INTEGER,            -- 回测成功次数
    FOREIGN KEY (review_id) REFERENCES post_market_reviews(id)
);
```

---

## 🔍 常用查询示例

### 1. 获取股票最新价格
```sql
SELECT code, close, pct_chg, volume, amount
FROM daily_data
WHERE code = 'sh.600519'
ORDER BY date DESC
LIMIT 1;
```

### 2. 统计涨停股票数量
```sql
SELECT COUNT(*) as limit_up_count
FROM daily_data
WHERE date = '2025-12-31'
  AND pct_chg >= 9.9;
```

### 3. 获取市值50-200亿的股票
```sql
SELECT code, name, total_cap / 1e8 as cap_billion
FROM market_cap_data
WHERE total_cap >= 50e8
  AND total_cap <= 200e8
ORDER BY total_cap DESC;
```

### 4. 获取ROE > 10%的股票
```sql
SELECT code, roe, report_date
FROM financial_indicators
WHERE roe > 10
  AND report_date >= '2024-01-01'
ORDER BY roe DESC;
```

### 5. 批量获取多只股票的最近数据
```sql
SELECT code, date, close, volume
FROM daily_data
WHERE code IN ('sh.600519', 'sz.000001', 'sz.300750')
  AND date >= '2025-12-01'
ORDER BY code, date DESC;
```

---

## 📈 数据更新机制

### 日线数据
- **更新频率**: 每日收盘后
- **数据源**: baostock API
- **更新脚本**: `tools/fetch_daily_data.py`

### 市值数据
- **更新频率**: 每日
- **数据源**: baostock API
- **更新脚本**: `tools/fetch_market_cap.py`

### 财务数据
- **更新频率**: 季度报告发布后
- **数据源**: baostock API
- **更新脚本**: `tools/fetch_financial_data.py`

---

## 🎯 盘后复盘系统数据需求

### 市场情绪模块需要：
1. ✅ `daily_data` - 获取涨跌停数据
2. ✅ `daily_data` - 计算连板高度
3. ✅ `daily_data` - 统计成交额

### 持仓健康模块需要：
1. ✅ `daily_data` - 获取股票日线数据
2. ✅ `user_portfolios` - 获取用户持仓
3. ✅ `stock_basic` - 获取股票名称

### 明日锦囊模块需要：
1. ✅ `daily_data` - 回测历史数据
2. ✅ `market_cap_data` - 筛选股票池
3. ✅ `financial_indicators` - 过滤财务指标

---

## 💡 性能优化建议

### 1. 使用统一表
```python
# ✅ 推荐：使用 daily_data 统一表
df = db.get_daily_data_unified(codes=['sh.600519', 'sz.000001'])

# ❌ 避免：逐个查询单表
for code in codes:
    df = db.get_daily_data(code)
```

### 2. 批量查询
```python
# ✅ 推荐：一次查询多只股票
codes = ['sh.600519', 'sz.000001', 'sz.300750']
df = db.get_stock_data_batch_unified(codes, start_date, end_date)

# ❌ 避免：循环查询
for code in codes:
    df = db.get_daily_data(code, start_date, end_date)
```

### 3. 使用索引
```python
# ✅ 推荐：按日期查询（使用索引）
SELECT * FROM daily_data WHERE date = '2025-12-31';

# ✅ 推荐：按股票+日期查询（使用索引）
SELECT * FROM daily_data WHERE code = 'sh.600519' AND date >= '2025-12-01';
```

---

## 📚 相关文档

- `src/data/database.py` - 数据库访问类
- `src/data/data_validator.py` - 数据验证工具
- `docs/DATA_OVERVIEW.md` - 数据概览
- `docs/FINANCIAL_DATA_README.md` - 财务数据说明

---

## ✅ 数据完整性

当前数据状态：
- ✅ 股票基础信息: 5,600+ 只
- ✅ 日线数据: 完整（2015-至今）
- ✅ 市值数据: 最新
- ⏳ **财务数据: 需要手动下载** (使用 `tools/fetch_financial_data.py`)
- ✅ 盘后复盘表: 已创建

**注意**: 财务数据需要单独下载，运行 `python3 tools/fetch_financial_data.py --batch` 下载全市场数据。

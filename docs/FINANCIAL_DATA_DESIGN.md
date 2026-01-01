# 财务数据系统设计文档

## 1. 概述

### 1.1 目标
为TradingBuddy量化交易系统添加上市公司财务数据支持，使策略能够基于基本面指标进行选股和分析。

### 1.2 范围
- 三大财务报表：资产负债表、利润表、现金流量表
- 财务分析指标：ROE、ROA、毛利率、负债率等
- 数据获取、存储、查询、分析

### 1.3 数据来源
- **主要来源**：新浪财经（通过akshare）
- **备用来源**：东方财富（通过akshare）
- **更新频率**：季度（跟随财报发布）

## 2. 系统架构

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────┐
│                    Application Layer                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Strategy   │  │   Analysis   │  │   Web API    │  │
│  │   Engine     │  │   Tools      │  │   Endpoints  │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                    Business Layer                        │
│  ┌──────────────────────────────────────────────────┐   │
│  │         Financial Data Analyzer                  │   │
│  │  - Ratio Calculation                             │   │
│  │  - Trend Analysis                                │   │
│  │  - Quality Assessment                            │   │
│  └──────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                      Data Layer                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │   Database   │  │   Fetcher    │  │    Cache     │  │
│  │   (SQLite)   │  │  (akshare)   │  │   (Memory)   │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 2.2 模块设计

#### 2.2.1 数据采集模块（FinancialDataFetcher）

**职责**：
- 从数据源获取财务数据
- 数据格式转换和清洗
- 错误处理和重试机制

**主要方法**：
```python
class FinancialDataFetcher:
    def fetch_balance_sheet(code: str) -> DataFrame
    def fetch_income_statement(code: str) -> DataFrame
    def fetch_cash_flow(code: str) -> DataFrame
    def fetch_financial_indicators(code: str) -> DataFrame
    def fetch_all_financial_data(code: str) -> Dict
    def batch_fetch_financial_data(codes: List[str]) -> Dict
```

#### 2.2.2 数据存储模块（StockDatabase）

**职责**：
- 财务数据的持久化存储
- 数据查询和检索
- 数据更新和维护

**主要方法**：
```python
class StockDatabase:
    # 保存方法
    def save_balance_sheet(code: str, df: DataFrame)
    def save_income_statement(code: str, df: DataFrame)
    def save_cash_flow(code: str, df: DataFrame)
    def save_financial_indicators(code: str, df: DataFrame)
    
    # 查询方法
    def get_balance_sheet(code: str, start_date: str, end_date: str) -> DataFrame
    def get_income_statement(code: str, start_date: str, end_date: str) -> DataFrame
    def get_cash_flow(code: str, start_date: str, end_date: str) -> DataFrame
    def get_financial_indicators(code: str, start_date: str, end_date: str) -> DataFrame
    
    # 便捷方法
    def get_latest_financial_data(code: str) -> Dict
    def get_financial_statistics() -> Dict
```

## 3. 数据模型

### 3.1 资产负债表（balance_sheet）

```sql
CREATE TABLE balance_sheet (
    code TEXT,                      -- 股票代码
    report_date TEXT,               -- 报告期
    report_type TEXT,               -- 报告类型（Q1/Q2/Q3/annual）
    total_assets REAL,              -- 总资产
    total_liabilities REAL,         -- 总负债
    shareholders_equity REAL,       -- 股东权益
    current_assets REAL,            -- 流动资产
    current_liabilities REAL,       -- 流动负债
    cash_and_equivalents REAL,      -- 货币资金
    accounts_receivable REAL,       -- 应收账款
    inventory REAL,                 -- 存货
    fixed_assets REAL,              -- 固定资产
    intangible_assets REAL,         -- 无形资产
    short_term_debt REAL,           -- 短期借款
    long_term_debt REAL,            -- 长期借款
    accounts_payable REAL,          -- 应付账款
    updated_at TEXT,                -- 更新时间
    PRIMARY KEY (code, report_date)
);
```

**关键指标**：
- 资产负债率 = 总负债 / 总资产
- 流动比率 = 流动资产 / 流动负债
- 速动比率 = (流动资产 - 存货) / 流动负债

### 3.2 利润表（income_statement）

```sql
CREATE TABLE income_statement (
    code TEXT,                      -- 股票代码
    report_date TEXT,               -- 报告期
    report_type TEXT,               -- 报告类型
    total_revenue REAL,             -- 营业总收入
    operating_revenue REAL,         -- 营业收入
    operating_cost REAL,            -- 营业总成本
    gross_profit REAL,              -- 毛利润
    operating_profit REAL,          -- 营业利润
    total_profit REAL,              -- 利润总额
    net_profit REAL,                -- 净利润
    net_profit_parent REAL,         -- 归母净利润
    basic_eps REAL,                 -- 基本每股收益
    diluted_eps REAL,               -- 稀释每股收益
    selling_expenses REAL,          -- 销售费用
    admin_expenses REAL,            -- 管理费用
    rd_expenses REAL,               -- 研发费用
    financial_expenses REAL,        -- 财务费用
    updated_at TEXT,
    PRIMARY KEY (code, report_date)
);
```

**关键指标**：
- 毛利率 = (营业收入 - 营业成本) / 营业收入
- 净利率 = 净利润 / 营业收入
- 费用率 = (销售费用 + 管理费用 + 财务费用) / 营业收入

### 3.3 现金流量表（cash_flow）

```sql
CREATE TABLE cash_flow (
    code TEXT,                      -- 股票代码
    report_date TEXT,               -- 报告期
    report_type TEXT,               -- 报告类型
    operating_cash_flow REAL,       -- 经营活动现金流
    investing_cash_flow REAL,       -- 投资活动现金流
    financing_cash_flow REAL,       -- 筹资活动现金流
    net_cash_flow REAL,             -- 现金净增加额
    cash_received_from_sales REAL,  -- 销售商品收到的现金
    cash_paid_for_goods REAL,       -- 购买商品支付的现金
    cash_paid_to_employees REAL,    -- 支付职工现金
    taxes_paid REAL,                -- 支付的税费
    cash_from_investments REAL,     -- 收回投资收到的现金
    cash_for_fixed_assets REAL,     -- 购建固定资产支付的现金
    cash_from_financing REAL,       -- 取得借款收到的现金
    cash_for_dividends REAL,        -- 分配股利支付的现金
    updated_at TEXT,
    PRIMARY KEY (code, report_date)
);
```

**关键指标**：
- 现金流质量 = 经营活动现金流 / 净利润
- 自由现金流 = 经营活动现金流 - 资本支出

### 3.4 财务指标（financial_indicators）

```sql
CREATE TABLE financial_indicators (
    code TEXT,                      -- 股票代码
    report_date TEXT,               -- 报告期
    roe REAL,                       -- 净资产收益率
    roa REAL,                       -- 总资产收益率
    gross_margin REAL,              -- 销售毛利率
    net_margin REAL,                -- 销售净利率
    operating_margin REAL,          -- 营业利润率
    current_ratio REAL,             -- 流动比率
    quick_ratio REAL,               -- 速动比率
    debt_to_asset_ratio REAL,       -- 资产负债率
    debt_to_equity_ratio REAL,      -- 产权比率
    asset_turnover REAL,            -- 总资产周转率
    inventory_turnover REAL,        -- 存货周转率
    receivable_turnover REAL,       -- 应收账款周转率
    eps REAL,                       -- 每股收益
    bvps REAL,                      -- 每股净资产
    pe_ratio REAL,                  -- 市盈率
    pb_ratio REAL,                  -- 市净率
    updated_at TEXT,
    PRIMARY KEY (code, report_date)
);
```

## 4. 数据处理流程

### 4.1 数据获取流程

```
1. 初始化采集器
   ↓
2. 获取股票列表
   ↓
3. 遍历股票代码
   ↓
4. 调用akshare接口
   ├─ fetch_balance_sheet()
   ├─ fetch_income_statement()
   ├─ fetch_cash_flow()
   └─ fetch_financial_indicators()
   ↓
5. 数据格式转换
   ├─ 列名映射
   ├─ 数据类型转换
   └─ 缺失值处理
   ↓
6. 保存到数据库
   ↓
7. 更新同步状态
```

### 4.2 数据查询流程

```
1. 接收查询请求
   ├─ 股票代码
   ├─ 报表类型
   └─ 日期范围
   ↓
2. 构建SQL查询
   ↓
3. 执行查询
   ↓
4. 返回DataFrame
   ↓
5. 数据后处理
   ├─ 计算衍生指标
   ├─ 格式化输出
   └─ 缓存结果
```

### 4.3 数据更新策略

**更新时机**：
- 季度更新：每季度财报发布后（4月、8月、10月、次年4月）
- 手动更新：用户主动触发
- 增量更新：只更新最新一期数据

**更新逻辑**：
```python
def update_financial_data(code: str):
    # 1. 获取数据库中最新报告期
    latest_date = db.get_latest_report_date(code)
    
    # 2. 获取最新财务数据
    new_data = fetcher.fetch_all_financial_data(code)
    
    # 3. 比较报告期
    if new_data['report_date'] > latest_date:
        # 4. 保存新数据（使用INSERT OR REPLACE）
        db.save_financial_data(code, new_data)
        return True
    else:
        return False  # 无需更新
```

## 5. 性能优化

### 5.1 批量查询优化

```python
# 不推荐：逐个查询
for code in codes:
    data = db.get_financial_indicators(code)

# 推荐：批量查询
query = """
    SELECT * FROM financial_indicators
    WHERE code IN (?, ?, ?, ...)
    AND report_date = (
        SELECT MAX(report_date)
        FROM financial_indicators
        WHERE code = financial_indicators.code
    )
"""
data = pd.read_sql(query, db.conn, params=codes)
```

### 5.2 索引优化

```sql
-- 创建复合索引
CREATE INDEX idx_balance_sheet_code_date 
ON balance_sheet(code, report_date);

CREATE INDEX idx_income_statement_code_date 
ON income_statement(code, report_date);

CREATE INDEX idx_cash_flow_code_date 
ON cash_flow(code, report_date);

CREATE INDEX idx_financial_indicators_code_date 
ON financial_indicators(code, report_date);

-- 创建单列索引
CREATE INDEX idx_financial_indicators_roe 
ON financial_indicators(roe);

CREATE INDEX idx_financial_indicators_roa 
ON financial_indicators(roa);
```

### 5.3 缓存策略

```python
class FinancialDataCache:
    """财务数据缓存"""
    
    def __init__(self, ttl=3600):
        self.cache = {}
        self.ttl = ttl  # 缓存有效期（秒）
    
    def get(self, key):
        if key in self.cache:
            data, timestamp = self.cache[key]
            if time.time() - timestamp < self.ttl:
                return data
        return None
    
    def set(self, key, data):
        self.cache[key] = (data, time.time())
```

## 6. 应用场景

### 6.1 基本面选股

```python
# 示例：价值投资选股
def value_investing_screen(db):
    """
    筛选条件：
    1. ROE > 15%（盈利能力强）
    2. 毛利率 > 30%（竞争优势）
    3. 资产负债率 < 60%（财务稳健）
    4. 流动比率 > 1.5（偿债能力）
    5. PE < 20（估值合理）
    """
    query = """
        SELECT 
            fi.code,
            sb.name,
            fi.roe,
            fi.gross_margin,
            fi.debt_to_asset_ratio,
            fi.current_ratio,
            fi.pe_ratio
        FROM financial_indicators fi
        JOIN stock_basic sb ON fi.code = sb.code
        WHERE fi.roe > 15
        AND fi.gross_margin > 30
        AND fi.debt_to_asset_ratio < 60
        AND fi.current_ratio > 1.5
        AND fi.pe_ratio < 20
        AND fi.report_date = (
            SELECT MAX(report_date)
            FROM financial_indicators
            WHERE code = fi.code
        )
        ORDER BY fi.roe DESC
    """
    
    return pd.read_sql(query, db.conn)
```

### 6.2 财务质量分析

```python
def analyze_financial_quality(db, code):
    """
    分析财务质量：
    1. 现金流质量（经营现金流/净利润）
    2. 盈利质量（ROE趋势）
    3. 成长质量（收入和利润增长率）
    """
    # 获取历史数据
    income = db.get_income_statement(code)
    cash_flow = db.get_cash_flow(code)
    
    # 计算现金流质量
    merged = pd.merge(income, cash_flow, on='report_date')
    merged['cf_quality'] = merged['operating_cash_flow'] / merged['net_profit']
    
    # 计算增长率
    income = income.sort_values('report_date')
    income['revenue_growth'] = income['total_revenue'].pct_change()
    income['profit_growth'] = income['net_profit'].pct_change()
    
    return {
        'cf_quality': merged['cf_quality'].mean(),
        'revenue_growth': income['revenue_growth'].mean(),
        'profit_growth': income['profit_growth'].mean()
    }
```

### 6.3 行业对比分析

```python
def industry_comparison(db, industry):
    """
    行业对比分析：
    比较同行业公司的财务指标
    """
    query = """
        SELECT 
            fi.code,
            sb.name,
            sb.industry,
            fi.roe,
            fi.roa,
            fi.gross_margin,
            fi.net_margin
        FROM financial_indicators fi
        JOIN stock_basic sb ON fi.code = sb.code
        WHERE sb.industry = ?
        AND fi.report_date = (
            SELECT MAX(report_date)
            FROM financial_indicators
            WHERE code = fi.code
        )
        ORDER BY fi.roe DESC
    """
    
    df = pd.read_sql(query, db.conn, params=[industry])
    
    # 计算行业平均值
    industry_avg = {
        'roe': df['roe'].mean(),
        'roa': df['roa'].mean(),
        'gross_margin': df['gross_margin'].mean(),
        'net_margin': df['net_margin'].mean()
    }
    
    return df, industry_avg
```

## 7. 错误处理

### 7.1 数据获取错误

```python
def safe_fetch_financial_data(code, max_retries=3):
    """安全获取财务数据（带重试）"""
    for attempt in range(max_retries):
        try:
            data = fetcher.fetch_all_financial_data(code)
            return data
        except Exception as e:
            logger.warning(f"第{attempt+1}次尝试失败: {e}")
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 指数退避
            else:
                logger.error(f"获取{code}财务数据失败")
                return None
```

### 7.2 数据缺失处理

```python
def handle_missing_data(df):
    """处理缺失数据"""
    # 1. 记录缺失情况
    missing_report = df.isnull().sum()
    logger.info(f"缺失数据统计:\n{missing_report}")
    
    # 2. 填充策略
    # - 数值型：使用0或前值填充
    # - 分类型：使用'unknown'
    numeric_columns = df.select_dtypes(include=['float64', 'int64']).columns
    df[numeric_columns] = df[numeric_columns].fillna(0)
    
    return df
```

## 8. 测试策略

### 8.1 单元测试

```python
def test_fetch_balance_sheet():
    """测试资产负债表获取"""
    fetcher = FinancialDataFetcher(db)
    df = fetcher.fetch_balance_sheet('600519')
    
    assert df is not None
    assert not df.empty
    assert 'report_date' in df.columns
    assert 'total_assets' in df.columns

def test_calculate_financial_ratios():
    """测试财务比率计算"""
    data = db.get_latest_financial_data('600519')
    
    bs = data['balance_sheet']
    current_ratio = bs['current_assets'] / bs['current_liabilities']
    
    assert current_ratio > 0
    assert current_ratio < 10  # 合理范围
```

### 8.2 集成测试

```python
def test_end_to_end_workflow():
    """端到端测试"""
    # 1. 获取数据
    result = fetcher.fetch_all_financial_data('600519', save_to_db=True)
    assert result['success']
    
    # 2. 查询数据
    data = db.get_latest_financial_data('600519')
    assert data['balance_sheet'] is not None
    
    # 3. 分析数据
    quality = analyze_financial_quality(db, '600519')
    assert 'cf_quality' in quality
```

## 9. 未来扩展

### 9.1 数据源扩展
- 添加更多数据源（如Wind、同花顺）
- 实现数据源切换和备份机制

### 9.2 指标扩展
- 杜邦分析
- 现金流折现模型
- 企业价值评估

### 9.3 功能扩展
- 财务预测模型
- 异常检测（财务造假识别）
- 行业分析报告生成

## 10. 参考资料

- [akshare文档](https://akshare.akfamily.xyz/)
- [财务报表分析](https://www.investopedia.com/financial-statements/)
- [财务比率分析](https://www.investopedia.com/financial-ratios/)

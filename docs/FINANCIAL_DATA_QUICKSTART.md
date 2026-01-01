# 财务数据快速入门

## 概述

TradingBuddy现在支持上市公司财务数据，包括：
- 📊 **资产负债表**：总资产、负债、股东权益等
- 💰 **利润表**：营业收入、净利润、每股收益等
- 💵 **现金流量表**：经营/投资/筹资活动现金流
- 📈 **财务指标**：ROE、ROA、毛利率、负债率等

## 快速开始

### 1. 下载财务数据

#### 下载单只股票
```bash
python tools/fetch_financial_data.py --code 600519
```

#### 批量下载（测试模式，前10只）
```bash
python tools/fetch_financial_data.py --batch --max 10
```

#### 批量下载全市场
```bash
python tools/fetch_financial_data.py --batch
```

⚠️ **注意**：全市场下载需要较长时间（约2-3小时），建议分批进行。

### 2. 查看统计信息

```bash
python tools/fetch_financial_data.py --stats
```

输出示例：
```
📊 财务数据统计
============================================================

balance_sheet:
  - 股票数量: 150
  - 记录总数: 600
  - 平均记录数: 4.0

income_statement:
  - 股票数量: 150
  - 记录总数: 600
  - 平均记录数: 4.0

cash_flow:
  - 股票数量: 150
  - 记录总数: 600
  - 平均记录数: 4.0

financial_indicators:
  - 股票数量: 150
  - 记录总数: 600
  - 平均记录数: 4.0
```

## 使用示例

### 示例1：获取最新财务数据

```python
from src.data.database import StockDatabase

db = StockDatabase()

# 获取贵州茅台的最新财务数据
data = db.get_latest_financial_data('600519')

# 资产负债表
if data['balance_sheet']:
    bs = data['balance_sheet']
    print(f"总资产: {bs['total_assets']/1e8:.2f} 亿元")
    print(f"股东权益: {bs['shareholders_equity']/1e8:.2f} 亿元")

# 利润表
if data['income_statement']:
    is_ = data['income_statement']
    print(f"营业收入: {is_['total_revenue']/1e8:.2f} 亿元")
    print(f"净利润: {is_['net_profit']/1e8:.2f} 亿元")

db.close()
```

### 示例2：筛选高ROE股票

```python
from src.data.database import StockDatabase
import pandas as pd

db = StockDatabase()

# 查询ROE > 15%的股票
query = """
    SELECT 
        fi.code,
        sb.name,
        fi.roe,
        fi.roa,
        fi.gross_margin
    FROM financial_indicators fi
    JOIN stock_basic sb ON fi.code = sb.code
    WHERE fi.roe > 15
    AND fi.report_date = (
        SELECT MAX(report_date) 
        FROM financial_indicators 
        WHERE code = fi.code
    )
    ORDER BY fi.roe DESC
    LIMIT 20
"""

df = pd.read_sql(query, db.conn)
print(df)

db.close()
```

### 示例3：分析盈利能力趋势

```python
from src.data.database import StockDatabase

db = StockDatabase()

# 获取历史利润表
income_df = db.get_income_statement('600519')

# 按报告期排序
income_df = income_df.sort_values('report_date', ascending=False)

# 显示近8期数据
for idx, row in income_df.head(8).iterrows():
    revenue = row['total_revenue'] / 1e8
    net_profit = row['net_profit'] / 1e8
    net_margin = (row['net_profit'] / row['total_revenue']) * 100
    
    print(f"{row['report_date']} | 收入: {revenue:.2f}亿 | "
          f"净利润: {net_profit:.2f}亿 | 净利率: {net_margin:.2f}%")

db.close()
```

### 示例4：现金流质量分析

```python
from src.data.database import StockDatabase
import pandas as pd

db = StockDatabase()

# 获取利润表和现金流量表
income_df = db.get_income_statement('600519')
cash_flow_df = db.get_cash_flow('600519')

# 合并数据
merged = pd.merge(
    income_df[['report_date', 'net_profit']],
    cash_flow_df[['report_date', 'operating_cash_flow']],
    on='report_date'
)

# 计算现金流/净利润比率
merged['cf_ratio'] = merged['operating_cash_flow'] / merged['net_profit']

# 评估现金流质量
for idx, row in merged.iterrows():
    quality = "优秀" if row['cf_ratio'] > 1.2 else "良好" if row['cf_ratio'] > 0.8 else "一般"
    print(f"{row['report_date']} | 比率: {row['cf_ratio']:.2f} | 质量: {quality}")

db.close()
```

## 数据库表结构

### balance_sheet（资产负债表）
| 字段 | 说明 | 单位 |
|------|------|------|
| code | 股票代码 | - |
| report_date | 报告期 | YYYY-MM-DD |
| report_type | 报告类型 | Q1/Q2/Q3/annual |
| total_assets | 总资产 | 元 |
| total_liabilities | 总负债 | 元 |
| shareholders_equity | 股东权益 | 元 |
| current_assets | 流动资产 | 元 |
| current_liabilities | 流动负债 | 元 |
| cash_and_equivalents | 货币资金 | 元 |
| accounts_receivable | 应收账款 | 元 |
| inventory | 存货 | 元 |
| fixed_assets | 固定资产 | 元 |
| intangible_assets | 无形资产 | 元 |
| short_term_debt | 短期借款 | 元 |
| long_term_debt | 长期借款 | 元 |
| accounts_payable | 应付账款 | 元 |

### income_statement（利润表）
| 字段 | 说明 | 单位 |
|------|------|------|
| code | 股票代码 | - |
| report_date | 报告期 | YYYY-MM-DD |
| report_type | 报告类型 | Q1/Q2/Q3/annual |
| total_revenue | 营业总收入 | 元 |
| operating_revenue | 营业收入 | 元 |
| operating_cost | 营业总成本 | 元 |
| gross_profit | 毛利润 | 元 |
| operating_profit | 营业利润 | 元 |
| total_profit | 利润总额 | 元 |
| net_profit | 净利润 | 元 |
| net_profit_parent | 归母净利润 | 元 |
| basic_eps | 基本每股收益 | 元/股 |
| diluted_eps | 稀释每股收益 | 元/股 |
| selling_expenses | 销售费用 | 元 |
| admin_expenses | 管理费用 | 元 |
| rd_expenses | 研发费用 | 元 |
| financial_expenses | 财务费用 | 元 |

### cash_flow（现金流量表）
| 字段 | 说明 | 单位 |
|------|------|------|
| code | 股票代码 | - |
| report_date | 报告期 | YYYY-MM-DD |
| report_type | 报告类型 | Q1/Q2/Q3/annual |
| operating_cash_flow | 经营活动现金流 | 元 |
| investing_cash_flow | 投资活动现金流 | 元 |
| financing_cash_flow | 筹资活动现金流 | 元 |
| net_cash_flow | 现金净增加额 | 元 |
| cash_received_from_sales | 销售商品收到的现金 | 元 |
| cash_paid_for_goods | 购买商品支付的现金 | 元 |
| cash_paid_to_employees | 支付职工现金 | 元 |
| taxes_paid | 支付的税费 | 元 |
| cash_from_investments | 收回投资收到的现金 | 元 |
| cash_for_fixed_assets | 购建固定资产支付的现金 | 元 |
| cash_from_financing | 取得借款收到的现金 | 元 |
| cash_for_dividends | 分配股利支付的现金 | 元 |

### financial_indicators（财务指标）
| 字段 | 说明 | 单位 |
|------|------|------|
| code | 股票代码 | - |
| report_date | 报告期 | YYYY-MM-DD |
| roe | 净资产收益率 | % |
| roa | 总资产收益率 | % |
| gross_margin | 销售毛利率 | % |
| net_margin | 销售净利率 | % |
| operating_margin | 营业利润率 | % |
| current_ratio | 流动比率 | - |
| quick_ratio | 速动比率 | - |
| debt_to_asset_ratio | 资产负债率 | % |
| debt_to_equity_ratio | 产权比率 | - |
| asset_turnover | 总资产周转率 | 次 |
| inventory_turnover | 存货周转率 | 次 |
| receivable_turnover | 应收账款周转率 | 次 |
| eps | 每股收益 | 元/股 |
| bvps | 每股净资产 | 元/股 |
| pe_ratio | 市盈率 | - |
| pb_ratio | 市净率 | - |

## API接口

### 数据库方法

```python
# 保存数据
db.save_balance_sheet(code, df)
db.save_income_statement(code, df)
db.save_cash_flow(code, df)
db.save_financial_indicators(code, df)

# 查询数据
db.get_balance_sheet(code, start_date, end_date)
db.get_income_statement(code, start_date, end_date)
db.get_cash_flow(code, start_date, end_date)
db.get_financial_indicators(code, start_date, end_date)

# 获取最新数据
db.get_latest_financial_data(code)

# 统计信息
db.get_financial_statistics()
```

### 采集器方法

```python
from src.data.financial_fetcher import FinancialDataFetcher

fetcher = FinancialDataFetcher(db)

# 获取单只股票的所有财务数据
fetcher.fetch_all_financial_data(code, save_to_db=True)

# 批量获取
fetcher.batch_fetch_financial_data(codes=None, max_stocks=None)

# 单独获取各报表
fetcher.fetch_balance_sheet(code)
fetcher.fetch_income_statement(code)
fetcher.fetch_cash_flow(code)
fetcher.fetch_financial_indicators(code)
```

## 策略应用

### 基本面选股策略示例

```python
from src.data.database import StockDatabase
import pandas as pd

db = StockDatabase()

# 筛选条件：
# 1. ROE > 15%
# 2. 毛利率 > 30%
# 3. 资产负债率 < 60%
# 4. 流动比率 > 1.5

query = """
    SELECT 
        fi.code,
        sb.name,
        fi.roe,
        fi.gross_margin,
        fi.debt_to_asset_ratio,
        fi.current_ratio
    FROM financial_indicators fi
    JOIN stock_basic sb ON fi.code = sb.code
    WHERE fi.roe > 15
    AND fi.gross_margin > 30
    AND fi.debt_to_asset_ratio < 60
    AND fi.current_ratio > 1.5
    AND fi.report_date = (
        SELECT MAX(report_date) 
        FROM financial_indicators 
        WHERE code = fi.code
    )
    ORDER BY fi.roe DESC
"""

candidates = pd.read_sql(query, db.conn)
print(f"找到 {len(candidates)} 只符合条件的股票")

db.close()
```

## 注意事项

1. **数据来源**：财务数据来自新浪财经和东方财富，免费但有延迟
2. **更新频率**：建议每季度更新一次（财报发布后）
3. **数据质量**：部分股票可能缺失某些字段，使用时需要检查
4. **限速要求**：批量下载时会自动限速，避免被封IP
5. **存储空间**：全市场财务数据约占用500MB-1GB空间

## 常见问题

### Q1: 如何更新财务数据？
A: 重新运行下载命令即可，数据库会自动更新（使用INSERT OR REPLACE）

### Q2: 财务数据多久更新一次？
A: 上市公司每季度发布财报，建议在财报季（4月、8月、10月、次年4月）后更新

### Q3: 如何处理缺失数据？
A: 使用时检查字段是否为None，或使用 `get()` 方法提供默认值

### Q4: 可以获取历史多少年的数据？
A: 通常可以获取近3-5年的数据，具体取决于数据源

## 下一步

- 查看完整示例：`python examples/financial_data_example.py`
- 集成到策略：参考 `src/business/strategies/` 中的策略实现
- API文档：查看 `docs/FINANCIAL_DATA_DESIGN.md`

## 反馈与支持

如有问题或建议，请提交Issue或联系开发团队。

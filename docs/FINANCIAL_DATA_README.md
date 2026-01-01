# 财务数据功能说明

## 🎉 新功能上线

TradingBuddy现已支持上市公司财务数据分析！你现在可以：

✅ 获取三大财务报表（资产负债表、利润表、现金流量表）  
✅ 查询财务分析指标（ROE、ROA、毛利率等）  
✅ 基于基本面进行选股和分析  
✅ 分析财务质量和盈利能力趋势  

## 📁 新增文件

### 核心模块
- `src/data/financial_fetcher.py` - 财务数据采集器
- `src/data/database.py` - 数据库扩展（已添加财务数据表和方法）

### 工具脚本
- `tools/fetch_financial_data.py` - 财务数据下载工具

### 示例代码
- `examples/financial_data_example.py` - 5个完整使用示例

### 文档
- `docs/FINANCIAL_DATA_QUICKSTART.md` - 快速入门指南
- `docs/FINANCIAL_DATA_DESIGN.md` - 详细设计文档
- `docs/FINANCIAL_DATA_README.md` - 本文件

## 🚀 快速开始

### 1. 下载测试数据（单只股票）

```bash
python3 tools/fetch_financial_data.py --code 600519
```

### 2. 查看示例

```bash
python3 examples/financial_data_example.py
```

### 3. 批量下载（测试模式）

```bash
# 下载前10只股票的财务数据
python3 tools/fetch_financial_data.py --batch --max 10
```

### 4. 查看统计信息

```bash
python3 tools/fetch_financial_data.py --stats
```

## 📊 数据表结构

### 四张核心表

1. **balance_sheet** - 资产负债表
   - 总资产、负债、股东权益
   - 流动资产/负债、现金、应收账款等

2. **income_statement** - 利润表
   - 营业收入、净利润、每股收益
   - 各项费用、毛利润等

3. **cash_flow** - 现金流量表
   - 经营/投资/筹资活动现金流
   - 现金收支明细

4. **financial_indicators** - 财务指标
   - ROE、ROA、毛利率、净利率
   - 流动比率、负债率、周转率等

## 💡 使用示例

### 示例1：获取最新财务数据

```python
from src.data.database import StockDatabase

db = StockDatabase()
data = db.get_latest_financial_data('600519')

# 查看资产负债表
if data['balance_sheet']:
    bs = data['balance_sheet']
    print(f"总资产: {bs['total_assets']/1e8:.2f} 亿元")
    print(f"股东权益: {bs['shareholders_equity']/1e8:.2f} 亿元")

db.close()
```

### 示例2：筛选高ROE股票

```python
from src.data.database import StockDatabase
import pandas as pd

db = StockDatabase()

query = """
    SELECT code, name, roe, roa, gross_margin
    FROM financial_indicators fi
    JOIN stock_basic sb ON fi.code = sb.code
    WHERE roe > 15
    ORDER BY roe DESC
    LIMIT 20
"""

high_roe_stocks = pd.read_sql(query, db.conn)
print(high_roe_stocks)

db.close()
```

### 示例3：分析盈利趋势

```python
from src.data.database import StockDatabase

db = StockDatabase()

# 获取历史利润表
income_df = db.get_income_statement('600519')

# 计算同比增长
income_df = income_df.sort_values('report_date')
income_df['revenue_growth'] = income_df['total_revenue'].pct_change()
income_df['profit_growth'] = income_df['net_profit'].pct_change()

print(income_df[['report_date', 'revenue_growth', 'profit_growth']])

db.close()
```

## 🔧 API接口

### 数据采集

```python
from src.data.financial_fetcher import FinancialDataFetcher

fetcher = FinancialDataFetcher(db)

# 获取单只股票所有财务数据
result = fetcher.fetch_all_financial_data('600519', save_to_db=True)

# 批量获取
result = fetcher.batch_fetch_financial_data(max_stocks=10)
```

### 数据查询

```python
from src.data.database import StockDatabase

db = StockDatabase()

# 查询资产负债表
balance_sheet = db.get_balance_sheet('600519', '2023-01-01', '2024-12-31')

# 查询利润表
income_statement = db.get_income_statement('600519')

# 查询现金流量表
cash_flow = db.get_cash_flow('600519')

# 查询财务指标
indicators = db.get_financial_indicators('600519')

# 获取最新数据（所有报表）
latest_data = db.get_latest_financial_data('600519')

db.close()
```

## 📈 策略应用

### 基本面选股策略

```python
def fundamental_screen(db):
    """
    基本面选股：
    - ROE > 15%
    - 毛利率 > 30%
    - 资产负债率 < 60%
    - 流动比率 > 1.5
    """
    query = """
        SELECT code, name, roe, gross_margin, 
               debt_to_asset_ratio, current_ratio
        FROM financial_indicators fi
        JOIN stock_basic sb ON fi.code = sb.code
        WHERE roe > 15
        AND gross_margin > 30
        AND debt_to_asset_ratio < 60
        AND current_ratio > 1.5
        ORDER BY roe DESC
    """
    
    return pd.read_sql(query, db.conn)
```

### 现金流质量分析

```python
def analyze_cash_flow_quality(db, code):
    """分析现金流质量"""
    income = db.get_income_statement(code)
    cash_flow = db.get_cash_flow(code)
    
    merged = pd.merge(income, cash_flow, on='report_date')
    merged['cf_quality'] = merged['operating_cash_flow'] / merged['net_profit']
    
    # 现金流/净利润 > 1.2 为优秀
    return merged[['report_date', 'cf_quality']]
```

## ⚠️ 注意事项

1. **数据来源**：新浪财经（免费但有延迟）
2. **更新频率**：建议每季度更新（财报发布后）
3. **限速要求**：批量下载会自动限速
4. **数据质量**：部分股票可能缺失某些字段
5. **存储空间**：全市场约500MB-1GB

## 📚 完整文档

- **快速入门**：`docs/FINANCIAL_DATA_QUICKSTART.md`
- **设计文档**：`docs/FINANCIAL_DATA_DESIGN.md`
- **示例代码**：`examples/financial_data_example.py`

## 🎯 下一步计划

- [ ] 添加财务预测模型
- [ ] 实现异常检测（财务造假识别）
- [ ] 行业对比分析工具
- [ ] Web API接口集成
- [ ] 前端可视化展示

## 💬 反馈

如有问题或建议，欢迎提Issue！

---

**开发时间**：2026-01-01  
**版本**：v1.0.0  
**状态**：✅ 已完成并测试

# 数据可用性分析报告

**分析日期**: 2026-01-04  
**数据库**: `data/a_share.db`

---

## 📊 分析结果总结

### ✅ 行业面分析 - 数据完整可用

**数据表**: `industry_data`  
**数据量**: 5,549 只股票  
**数据完整性**: ✅ 优秀

#### 可用字段
- `code`: 股票代码
- `name`: 股票名称  
- `industry`: 行业分类
- `update_date`: 更新日期
- `market`: 市场 (sh/sz)
- `full_code`: 完整代码

#### 行业分类统计（Top 20）
```
专用设备      270只
汽车零部件    237只
通用设备      221只
软件开发      196只
半导体        174只
化学制品      171只
电子元件      150只
化学制药      149只
互联网服务    147只
电网设备      139只
医疗器械      125只
食品饮料      119只
环保行业      118只
通信设备      107只
消费电子      102只
光学光电子    100只
文化传媒       99只
纺织服装       98只
家电行业       91只
农牧饲渔       91只
```

#### 💡 可立即实现的功能

1. **板块联动性分析**
   - 计算个股与行业指数的相关性
   - 识别行业龙头股
   - 板块轮动监测

2. **行业强弱对比**
   - 行业涨跌幅排名
   - 行业资金流向（基于成交额）
   - 行业估值水平对比

3. **个股行业定位**
   - 个股在行业内的排名
   - 行业内相对强弱
   - 同行业股票推荐

#### 示例查询
```python
# 获取某只股票的行业信息
SELECT code, name, industry 
FROM industry_data 
WHERE code = '600519';

# 获取某行业的所有股票
SELECT code, name 
FROM industry_data 
WHERE industry = '食品饮料';

# 统计各行业股票数量
SELECT industry, COUNT(*) as count 
FROM industry_data 
GROUP BY industry 
ORDER BY count DESC;
```

---

### ❌ 资金面分析 - 需要外部数据源

**当前状态**: 数据库中无北向资金、机构资金流向数据  
**cash_flow表**: 仅为财务报表中的现金流量表，非市场资金流向

#### 需要的数据类型

1. **北向资金（沪深港通）**
   - 北向资金持股数量
   - 北向资金持股比例变化
   - 北向资金净流入/流出

2. **主力资金流向**
   - 主力净流入/流出金额
   - 超大单、大单、中单、小单分布
   - 机构席位买卖数据

3. **龙虎榜数据**
   - 上榜原因
   - 买卖席位信息
   - 游资/机构标识

#### 推荐数据源

##### 1. AkShare (免费)
```python
import akshare as ak

# 沪深港通持股数据
df = ak.stock_hsgt_hold_stock_em(symbol="600519", market="北向")

# 个股资金流向
df = ak.stock_individual_fund_flow_rank(indicator="今日")

# 龙虎榜数据
df = ak.stock_lhb_detail_em(symbol="600519", start_date="20250101", end_date="20260104")
```

##### 2. TuShare (需要积分)
```python
import tushare as ts

# 北向资金流向
df = ts.moneyflow_hsgt(start_date='20250101', end_date='20260104')

# 个股资金流向
df = ts.moneyflow(ts_code='600519.SH', start_date='20250101', end_date='20260104')

# 龙虎榜数据
df = ts.top_list(trade_date='20260103')
```

#### 实现建议

1. **短期方案（1-2天）**
   - 使用AkShare免费API
   - 实时获取数据，不存储到数据库
   - 适合快速原型验证

2. **长期方案（1周）**
   - 创建新表存储资金流向数据
   - 定期更新（每日收盘后）
   - 支持历史数据回测

---

## 🎯 推荐实现优先级

### 优先级1: 行业面分析 ⭐⭐⭐
**理由**: 数据完整，可立即实现  
**工作量**: 2-3天  
**价值**: 高 - 帮助用户理解板块轮动

**功能清单**:
1. ✅ 个股行业归属显示
2. ✅ 行业涨跌幅排行
3. ✅ 板块联动性分析
4. ✅ 同行业股票推荐

### 优先级2: 资金面分析（基础版）⭐⭐
**理由**: 需要外部API，但价值高  
**工作量**: 3-5天（含API集成）  
**价值**: 高 - A股散户最关注

**功能清单**:
1. ⚠️ 北向资金持股变化（需AkShare）
2. ⚠️ 主力资金流向（需AkShare）
3. ⚠️ 龙虎榜监控（需AkShare）

### 优先级3: 资金面分析（完整版）⭐
**理由**: 需要数据存储和历史回测  
**工作量**: 1-2周  
**价值**: 中 - 需要积累历史数据才有价值

**功能清单**:
1. ❌ 历史资金流向趋势
2. ❌ 资金流向回测
3. ❌ 机构持仓变化追踪

---

## 📋 数据库扩展建议

如果要实现完整的资金面分析，建议创建以下表：

### 1. northbound_capital - 北向资金表
```sql
CREATE TABLE northbound_capital (
    code TEXT NOT NULL,              -- 股票代码
    date TEXT NOT NULL,              -- 交易日期
    hold_shares REAL,                -- 持股数量（股）
    hold_ratio REAL,                 -- 持股比例（%）
    hold_value REAL,                 -- 持股市值（元）
    change_shares REAL,              -- 持股变化（股）
    change_ratio REAL,               -- 变化比例（%）
    updated_at TEXT,
    PRIMARY KEY (code, date)
);
CREATE INDEX idx_nb_date ON northbound_capital(date);
```

### 2. capital_flow - 资金流向表
```sql
CREATE TABLE capital_flow (
    code TEXT NOT NULL,              -- 股票代码
    date TEXT NOT NULL,              -- 交易日期
    main_net_inflow REAL,            -- 主力净流入（元）
    super_large_inflow REAL,         -- 超大单净流入
    large_inflow REAL,               -- 大单净流入
    medium_inflow REAL,              -- 中单净流入
    small_inflow REAL,               -- 小单净流入
    main_net_inflow_ratio REAL,      -- 主力净流入占比（%）
    updated_at TEXT,
    PRIMARY KEY (code, date)
);
CREATE INDEX idx_cf_date ON capital_flow(date);
```

### 3. dragon_tiger_list - 龙虎榜表
```sql
CREATE TABLE dragon_tiger_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,              -- 股票代码
    date TEXT NOT NULL,              -- 上榜日期
    reason TEXT,                     -- 上榜原因
    buy_amount REAL,                 -- 买入总额
    sell_amount REAL,                -- 卖出总额
    net_amount REAL,                 -- 净额
    seat_name TEXT,                  -- 席位名称
    seat_type TEXT,                  -- 席位类型（机构/游资）
    updated_at TEXT
);
CREATE INDEX idx_dtl_code_date ON dragon_tiger_list(code, date);
```

---

## 🚀 下一步行动

### 立即可做（今天）
1. ✅ 实现行业面分析基础功能
2. ✅ 在持仓健康检查中加入行业信息
3. ✅ 在K线分析中加入行业对比

### 本周可做
1. ⚠️ 集成AkShare API获取北向资金数据
2. ⚠️ 实现实时资金流向查询（不存储）
3. ⚠️ 在盘后复盘中加入资金面分析

### 下周可做
1. ❌ 创建资金流向数据表
2. ❌ 实现定时数据更新任务
3. ❌ 支持历史资金流向回测

---

## 💡 实现建议

### 行业面分析实现思路

```python
# 1. 获取个股行业信息
def get_stock_industry(code: str) -> str:
    """获取股票所属行业"""
    query = "SELECT industry FROM industry_data WHERE code = ?"
    return db.execute(query, (code,)).fetchone()[0]

# 2. 计算行业涨跌幅
def get_industry_performance(date: str) -> pd.DataFrame:
    """计算各行业当日涨跌幅"""
    query = """
    SELECT 
        i.industry,
        AVG(d.pct_chg) as avg_pct_chg,
        COUNT(*) as stock_count,
        SUM(d.amount) as total_amount
    FROM industry_data i
    JOIN daily_data d ON i.full_code = d.code
    WHERE d.date = ?
    GROUP BY i.industry
    ORDER BY avg_pct_chg DESC
    """
    return pd.read_sql(query, db, params=(date,))

# 3. 板块联动性分析
def analyze_sector_correlation(code: str, days: int = 30) -> dict:
    """分析个股与行业的相关性"""
    # 获取个股行业
    industry = get_stock_industry(code)
    
    # 获取个股和行业内其他股票的涨跌幅
    # 计算相关系数
    # 返回分析结果
    pass
```

### 资金面分析实现思路（使用AkShare）

```python
import akshare as ak

# 1. 获取北向资金持股
def get_northbound_holding(code: str) -> dict:
    """获取北向资金持股情况"""
    try:
        df = ak.stock_hsgt_hold_stock_em(symbol=code, market="北向")
        if len(df) > 0:
            latest = df.iloc[-1]
            return {
                "hold_shares": latest["持股数量"],
                "hold_ratio": latest["持股比例"],
                "change": latest["持股变化"]
            }
    except:
        return None

# 2. 获取主力资金流向
def get_capital_flow(code: str) -> dict:
    """获取主力资金流向"""
    try:
        df = ak.stock_individual_fund_flow_rank(indicator="今日")
        stock_data = df[df["代码"] == code]
        if len(stock_data) > 0:
            return {
                "main_inflow": stock_data["主力净流入"].values[0],
                "main_ratio": stock_data["主力净占比"].values[0]
            }
    except:
        return None
```

---

## ✅ 结论

1. **行业面分析**: 数据完整，可立即开始实现 ✅
2. **资金面分析**: 需要外部API，建议先用AkShare实现基础版 ⚠️
3. **推荐路线**: 先做行业面（2-3天） → 再做资金面基础版（3-5天）

**总工作量预估**: 1-2周可完成两个模块的基础功能

---

*报告生成时间: 2026-01-04*

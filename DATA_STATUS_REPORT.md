# 数据可用性状态报告

**更新日期**: 2026-01-04  
**数据库**: `data/a_share.db`

---

## 📊 数据完整性总览

| 数据类型 | 状态 | 数据量 | 可用性 | 备注 |
|---------|------|--------|--------|------|
| 行业分类 | ✅ 完整 | 5,549只股票 | 100% | 可立即使用 |
| 北向资金 | ✅ 完整 | 2,767只股票 | 49.9% | 已保存到数据库 |
| 资金流向 | ✅ 完整 | 5,263只股票 | 95.0% | 已保存到数据库 |
| 龙虎榜 | ⚠️ 部分 | 0条记录 | 0% | 周末无数据，需工作日更新 |
| 日线数据 | ✅ 完整 | 5,600+只股票 | 100% | 历史数据完整 |
| 财务数据 | ✅ 完整 | 5,600+只股票 | 100% | 季度更新 |

---

## ✅ 已完成的数据准备

### 1. 行业面分析数据 ✅

**数据表**: `industry_data`  
**状态**: ✅ 完整可用  
**数据量**: 5,549只股票

```sql
-- 示例查询
SELECT code, name, industry FROM industry_data WHERE code = '600519';
-- 结果: 600519|贵州茅台|食品饮料
```

**可实现功能**:
- ✅ 个股行业归属查询
- ✅ 行业涨跌幅排名
- ✅ 板块联动性分析
- ✅ 同行业股票推荐

---

### 2. 北向资金数据 ✅

**数据表**: `northbound_capital`  
**状态**: ✅ 已保存到数据库  
**数据量**: 2,767只股票  
**覆盖率**: 49.9% (有北向资金持股的股票)

**表结构**:
```sql
CREATE TABLE northbound_capital (
    code TEXT NOT NULL,              -- 股票代码
    date TEXT NOT NULL,              -- 交易日期
    hold_shares REAL,                -- 持股数量（股）
    hold_ratio REAL,                 -- 持股比例（%）
    hold_value REAL,                 -- 持股市值（元）
    change_shares_5d REAL,           -- 5日持股变化（股）
    change_ratio_5d REAL,            -- 5日变化比例（%）
    market TEXT,                     -- 市场 (北向/沪股通/深股通)
    updated_at TEXT,
    PRIMARY KEY (code, date, market)
);
```

**示例数据**:
```
贵州茅台 (600519):
  持股比例: 6.56%
  持股市值: 1.18亿元
  5日变化: -0.14%
```

**可实现功能**:
- ✅ 北向资金持股查询
- ✅ 持股比例变化监控
- ✅ "聪明钱"动向分析
- ⚠️ 历史趋势分析（需要每日更新积累数据）

---

### 3. 资金流向数据 ✅

**数据表**: `capital_flow`  
**状态**: ✅ 已保存到数据库  
**数据量**: 5,263只股票  
**覆盖率**: 95.0%

**表结构**:
```sql
CREATE TABLE capital_flow (
    code TEXT NOT NULL,              -- 股票代码
    date TEXT NOT NULL,              -- 交易日期
    name TEXT,                       -- 股票名称
    close_price REAL,                -- 收盘价
    pct_chg REAL,                    -- 涨跌幅（%）
    main_net_inflow REAL,            -- 主力净流入（元）
    super_large_inflow REAL,         -- 超大单净流入（元）
    large_inflow REAL,               -- 大单净流入（元）
    medium_inflow REAL,              -- 中单净流入（元）
    small_inflow REAL,               -- 小单净流入（元）
    main_net_inflow_ratio REAL,      -- 主力净流入占比（%）
    updated_at TEXT,
    PRIMARY KEY (code, date)
);
```

**示例数据**:
```
贵州茅台 (600519):
  涨跌幅: -0.9%
  主力净流入: -7.47亿元
  主力净流入占比: -15.57%
  → 🔴 主力资金大幅流出
```

**可实现功能**:
- ✅ 主力资金流向查询
- ✅ 资金流入/流出排名
- ✅ 超大单/大单/中单/小单分布
- ⚠️ 历史趋势分析（需要每日更新积累数据）

---

### 4. 龙虎榜数据 ⚠️

**数据表**: `dragon_tiger_list`, `dragon_tiger_seats`  
**状态**: ⚠️ 表已创建，但当前无数据  
**原因**: 周末无龙虎榜数据，需要在工作日更新

**表结构**:
```sql
CREATE TABLE dragon_tiger_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,              -- 股票代码
    date TEXT NOT NULL,              -- 上榜日期
    name TEXT,                       -- 股票名称
    close_price REAL,                -- 收盘价
    pct_chg REAL,                    -- 涨跌幅（%）
    turnover REAL,                   -- 换手率（%）
    reason TEXT,                     -- 上榜原因
    buy_amount REAL,                 -- 买入总额（元）
    sell_amount REAL,                -- 卖出总额（元）
    net_amount REAL,                 -- 净额（元）
    total_amount REAL,               -- 总成交额（元）
    market_amount REAL,              -- 市场总成交额（元）
    amount_ratio REAL,               -- 成交额占比（%）
    updated_at TEXT
);
```

**待实现功能**:
- ⏳ 龙虎榜上榜股票查询
- ⏳ 游资/机构席位分析
- ⏳ 上榜原因统计

**下一步**: 在下个交易日运行更新命令
```bash
python tools/fetch_capital_flow_data.py --mode dragon
```

---

## 🎯 功能实现状态

### 优先级1: 行业面分析 ⭐⭐⭐

| 功能 | 数据状态 | 实现状态 | 备注 |
|------|---------|---------|------|
| 个股行业归属显示 | ✅ 完整 | ⏳ 待实现 | 数据就绪 |
| 行业涨跌幅排行 | ✅ 完整 | ⏳ 待实现 | 需要结合daily_data |
| 板块联动性分析 | ✅ 完整 | ⏳ 待实现 | 需要计算相关性 |
| 同行业股票推荐 | ✅ 完整 | ⏳ 待实现 | 数据就绪 |

**工作量**: 2-3天  
**可立即开始**: ✅ 是

---

### 优先级2: 资金面分析（基础版）⭐⭐

| 功能 | 数据状态 | 实现状态 | 备注 |
|------|---------|---------|------|
| 北向资金持股查询 | ✅ 完整 | ⏳ 待实现 | 数据已保存 |
| 北向资金变化监控 | ⚠️ 单日 | ⏳ 待实现 | 需要每日更新积累历史 |
| 主力资金流向查询 | ✅ 完整 | ⏳ 待实现 | 数据已保存 |
| 资金流入/流出排名 | ✅ 完整 | ⏳ 待实现 | 数据已保存 |
| 龙虎榜监控 | ⚠️ 无数据 | ⏳ 待实现 | 需要工作日更新 |

**工作量**: 2-3天  
**可立即开始**: ✅ 是（除龙虎榜外）

---

### 优先级3: 资金面分析（完整版）⭐

| 功能 | 数据状态 | 实现状态 | 备注 |
|------|---------|---------|------|
| 历史资金流向趋势 | ⚠️ 单日 | ❌ 待积累 | 需要每日更新1-2周 |
| 资金流向回测 | ⚠️ 单日 | ❌ 待积累 | 需要历史数据 |
| 机构持仓变化追踪 | ⚠️ 单日 | ❌ 待积累 | 需要每日更新 |

**工作量**: 1-2周  
**可立即开始**: ❌ 否（需要先积累历史数据）

---

## 📋 数据更新计划

### 每日更新任务

```bash
# 1. 收盘后更新资金流向（15:30）
python tools/fetch_capital_flow_data.py --mode flow

# 2. 晚上更新龙虎榜（20:00）
python tools/fetch_capital_flow_data.py --mode dragon

# 3. 更新北向资金（每日一次）
python tools/fetch_capital_flow_data.py --mode northbound
```

### 定时任务配置（Crontab）

```bash
# 每个交易日 15:30 更新资金流向
30 15 * * 1-5 cd /path/to/project && python3 tools/fetch_capital_flow_data.py --mode flow

# 每个交易日 20:00 更新龙虎榜
0 20 * * 1-5 cd /path/to/project && python3 tools/fetch_capital_flow_data.py --mode dragon

# 每个交易日 21:00 更新北向资金
0 21 * * 1-5 cd /path/to/project && python3 tools/fetch_capital_flow_data.py --mode northbound
```

---

## 🚀 立即可做的功能

### 1. 行业面分析（数据完整）✅

**实现思路**:
```python
# 获取个股行业
def get_stock_industry(code: str) -> str:
    query = "SELECT industry FROM industry_data WHERE code = ?"
    return db.execute(query, (code,)).fetchone()[0]

# 计算行业涨跌幅
def get_industry_performance(date: str) -> pd.DataFrame:
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
```

---

### 2. 北向资金分析（数据完整）✅

**实现思路**:
```python
# 查询北向资金持股
def get_northbound_holding(code: str) -> dict:
    query = """
    SELECT hold_ratio, hold_value, change_ratio_5d
    FROM northbound_capital
    WHERE code = ?
    ORDER BY date DESC
    LIMIT 1
    """
    result = db.execute(query, (code,)).fetchone()
    
    if result:
        hold_ratio, hold_value, change_ratio_5d = result
        
        # 判断状态
        if change_ratio_5d > 0.5:
            status = 'green'
            message = f"北向资金持股比例{hold_ratio:.2f}%，近5日增持{change_ratio_5d:.2f}%"
        elif change_ratio_5d < -0.5:
            status = 'red'
            message = f"北向资金持股比例{hold_ratio:.2f}%，近5日减持{abs(change_ratio_5d):.2f}%"
        else:
            status = 'yellow'
            message = f"北向资金持股比例{hold_ratio:.2f}%，持仓稳定"
        
        return {'status': status, 'message': message}
    
    return None
```

---

### 3. 主力资金流向分析（数据完整）✅

**实现思路**:
```python
# 查询主力资金流向
def get_capital_flow(code: str) -> dict:
    query = """
    SELECT main_net_inflow, main_net_inflow_ratio, pct_chg
    FROM capital_flow
    WHERE code = ?
    ORDER BY date DESC
    LIMIT 1
    """
    result = db.execute(query, (code,)).fetchone()
    
    if result:
        inflow, ratio, pct_chg = result
        
        # 判断状态
        if inflow > 0 and ratio > 10:
            status = 'green'
            message = f"主力资金大幅流入{inflow/1e8:.2f}亿元（占比{ratio:.1f}%）"
        elif inflow < 0 and ratio < -10:
            status = 'red'
            message = f"主力资金大幅流出{abs(inflow)/1e8:.2f}亿元（占比{ratio:.1f}%）"
        else:
            status = 'yellow'
            message = f"资金流向正常"
        
        return {'status': status, 'message': message}
    
    return None
```

---

## ⚠️ 需要进一步准备的数据

### 1. 龙虎榜历史数据 ⚠️

**当前状态**: 表已创建，但无数据  
**原因**: 周末无龙虎榜数据  
**解决方案**: 在下个交易日运行更新命令

```bash
# 更新最近一周的龙虎榜数据
for i in {1..7}; do
    date=$(date -d "-$i days" +%Y-%m-%d)
    python tools/fetch_capital_flow_data.py --mode dragon --date $date
done
```

---

### 2. 历史资金流向数据 ⚠️

**当前状态**: 只有今日数据  
**需要**: 至少1-2周的历史数据才能做趋势分析  
**解决方案**: 每日定时更新，积累历史数据

**预计时间**: 1-2周后可以做历史趋势分析

---

### 3. 北向资金历史数据 ⚠️

**当前状态**: 只有最新一天的数据  
**需要**: 至少30天的历史数据才能分析连续买入/卖出  
**解决方案**: 每日定时更新，积累历史数据

**预计时间**: 1个月后可以做完整的趋势分析

---

## ✅ 总结

### 立即可用的数据 ✅

1. **行业分类数据** - 5,549只股票，100%覆盖
2. **北向资金数据** - 2,767只股票，49.9%覆盖
3. **资金流向数据** - 5,263只股票，95.0%覆盖
4. **日线数据** - 5,600+只股票，历史完整
5. **财务数据** - 5,600+只股票，季度更新

### 可立即实现的功能 ✅

1. **行业面分析** - 数据完整，可立即开始（2-3天）
2. **北向资金查询** - 数据完整，可立即开始（1天）
3. **主力资金流向** - 数据完整，可立即开始（1天）

### 需要积累的数据 ⚠️

1. **龙虎榜数据** - 需要工作日更新
2. **历史资金流向** - 需要每日更新1-2周
3. **北向资金趋势** - 需要每日更新1个月

### 推荐实施顺序 🎯

**第1周**:
1. ✅ 实现行业面分析（2-3天）
2. ✅ 实现北向资金查询（1天）
3. ✅ 实现主力资金流向（1天）
4. ✅ 设置每日定时更新任务

**第2-3周**:
- 积累历史数据
- 优化分析逻辑
- 添加更多分析维度

**第4周+**:
- 实现历史趋势分析
- 实现资金流向回测
- 实现龙虎榜监控

---

## 📊 数据质量评估

| 数据类型 | 完整性 | 准确性 | 时效性 | 可用性 |
|---------|--------|--------|--------|--------|
| 行业分类 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 北向资金 | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| 资金流向 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 龙虎榜 | ⭐ | - | - | ⭐ |

**总体评估**: ✅ 数据质量优秀，可以开始实现功能

---

*报告更新时间: 2026-01-04 19:30*

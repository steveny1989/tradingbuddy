# 资金流向数据系统使用指南

**创建日期**: 2026-01-04  
**数据来源**: AkShare (免费API)

---

## 📊 功能概述

本系统提供三大类资金流向数据：

1. **北向资金（沪深港通）** - "聪明钱"的动向
2. **主力资金流向** - 大单、超大单资金流向
3. **龙虎榜数据** - 游资和机构的席位信息

---

## 🗄️ 数据表结构

### 1. northbound_capital - 北向资金表

存储沪深港通的持股数据

```sql
CREATE TABLE northbound_capital (
    code TEXT NOT NULL,              -- 股票代码 (600519)
    date TEXT NOT NULL,              -- 交易日期 (YYYY-MM-DD)
    hold_shares REAL,                -- 持股数量（股）
    hold_ratio REAL,                 -- 持股比例（%）
    hold_value REAL,                 -- 持股市值（元）
    change_shares REAL,              -- 持股变化（股）
    change_ratio REAL,               -- 变化比例（%）
    market TEXT,                     -- 市场 (北向/沪股通/深股通)
    updated_at TEXT,
    PRIMARY KEY (code, date, market)
);
```

**示例数据**:
```
code   | date       | hold_ratio | change_ratio | market
-------|------------|------------|--------------|-------
600519 | 2026-01-03 | 15.2       | +0.5         | 北向
600519 | 2026-01-02 | 14.7       | +0.3         | 北向
```

---

### 2. capital_flow - 资金流向表

存储每日主力资金流向数据

```sql
CREATE TABLE capital_flow (
    code TEXT NOT NULL,              -- 股票代码 (600519)
    date TEXT NOT NULL,              -- 交易日期 (YYYY-MM-DD)
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

**资金分类**:
- **超大单**: 单笔成交 ≥ 100万元
- **大单**: 单笔成交 20-100万元
- **中单**: 单笔成交 4-20万元
- **小单**: 单笔成交 < 4万元
- **主力**: 超大单 + 大单

**示例数据**:
```
code   | name     | pct_chg | main_net_inflow | main_net_inflow_ratio
-------|----------|---------|-----------------|----------------------
600519 | 贵州茅台  | +2.1    | 123456789       | 15.2
```

---

### 3. dragon_tiger_list - 龙虎榜表

存储龙虎榜上榜股票信息

```sql
CREATE TABLE dragon_tiger_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,              -- 股票代码 (600519)
    date TEXT NOT NULL,              -- 上榜日期 (YYYY-MM-DD)
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

**上榜原因**:
- 日涨幅偏离值达7%
- 日跌幅偏离值达7%
- 日换手率达20%
- 连续三个交易日涨幅偏离值累计达20%
- 等等

---

### 4. dragon_tiger_seats - 龙虎榜席位明细表

存储龙虎榜买卖席位信息

```sql
CREATE TABLE dragon_tiger_seats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL,              -- 股票代码
    date TEXT NOT NULL,              -- 交易日期
    seat_name TEXT,                  -- 席位名称
    buy_amount REAL,                 -- 买入金额（元）
    sell_amount REAL,                -- 卖出金额（元）
    net_amount REAL,                 -- 净额（元）
    seat_type TEXT,                  -- 席位类型（机构/游资/未知）
    updated_at TEXT
);
```

**席位类型识别**:
- **机构**: 席位名称包含"机构"
- **游资**: 其他营业部席位
- **未知**: 无法识别

---

## 🚀 快速开始

### 安装依赖

```bash
pip install akshare pandas
```

### 初始化数据表

```python
from src.data.capital_flow_fetcher import CapitalFlowFetcher

# 创建实例（自动初始化数据表）
fetcher = CapitalFlowFetcher()
```

### 测试功能

```bash
# 运行测试脚本
python test_capital_flow.py
```

---

## 📖 使用示例

### 1. 获取单只股票的北向资金数据

```python
from src.data.capital_flow_fetcher import CapitalFlowFetcher

fetcher = CapitalFlowFetcher()

# 获取贵州茅台的北向资金数据
df = fetcher.fetch_northbound_capital("600519")
print(df.head())

# 保存到数据库
fetcher.save_northbound_capital(df)
```

### 2. 获取今日资金流向排名

```python
# 获取今日资金流向
df = fetcher.fetch_capital_flow_rank(indicator="今日")

# 查看主力净流入前10
top10 = df.nlargest(10, 'main_net_inflow')
print(top10[['code', 'name', 'main_net_inflow', 'main_net_inflow_ratio']])

# 保存到数据库
fetcher.save_capital_flow(df)
```

### 3. 获取龙虎榜数据

```python
from datetime import datetime, timedelta

# 获取昨日龙虎榜
yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
df = fetcher.fetch_dragon_tiger_list(yesterday)

if df is not None:
    print(df[['code', 'name', 'reason', 'net_amount']])
    fetcher.save_dragon_tiger_list(df)
```

### 4. 批量更新北向资金

```python
# 更新多只股票
symbols = ['600519', '000001', '300750']
results = fetcher.batch_update_northbound(symbols)

print(f"成功: {results['success']}")
print(f"无数据: {results['no_data']}")
print(f"失败: {results['failed']}")
```

---

## 🛠️ 命令行工具

### 更新所有数据

```bash
python tools/fetch_capital_flow_data.py --mode all
```

### 只更新资金流向

```bash
python tools/fetch_capital_flow_data.py --mode flow
```

### 只更新龙虎榜

```bash
python tools/fetch_capital_flow_data.py --mode dragon
```

### 更新指定股票的北向资金

```bash
python tools/fetch_capital_flow_data.py --mode northbound --stocks 600519 000001 300750
```

### 更新市值前100的股票的北向资金

```bash
python tools/fetch_capital_flow_data.py --mode northbound --top 100
```

---

## 📊 数据查询示例

### 查询北向资金趋势

```sql
-- 查询贵州茅台的北向资金持股趋势
SELECT date, hold_ratio, change_ratio
FROM northbound_capital
WHERE code = '600519'
ORDER BY date DESC
LIMIT 30;
```

### 查询主力资金流入排名

```sql
-- 查询今日主力净流入前20
SELECT code, name, pct_chg, main_net_inflow, main_net_inflow_ratio
FROM capital_flow
WHERE date = '2026-01-03'
ORDER BY main_net_inflow DESC
LIMIT 20;
```

### 查询龙虎榜上榜股票

```sql
-- 查询最近上榜的股票
SELECT code, name, date, pct_chg, reason
FROM dragon_tiger_list
ORDER BY date DESC
LIMIT 20;
```

### 分析北向资金连续买入

```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/a_share.db')

# 查询最近10天的北向资金变化
query = """
SELECT date, hold_ratio, change_ratio
FROM northbound_capital
WHERE code = '600519'
ORDER BY date DESC
LIMIT 10
"""
df = pd.read_sql(query, conn)

# 计算连续买入天数
consecutive_days = 0
for _, row in df.iterrows():
    if row['change_ratio'] > 0:
        consecutive_days += 1
    else:
        break

if consecutive_days >= 3:
    print(f"🟢 外资连续 {consecutive_days} 天加仓，机构正在'抱团'")
elif consecutive_days <= -3:
    print(f"🔴 外资连续 {abs(consecutive_days)} 天减仓，主力资金撤退")
else:
    print(f"🟡 外资持仓稳定，暂无明显动作")

conn.close()
```

---

## 🎯 分析应用场景

### 场景1: 北向资金监控

**目标**: 监控"聪明钱"的动向

```python
def analyze_northbound_trend(code: str, days: int = 10) -> dict:
    """分析北向资金趋势"""
    conn = sqlite3.connect('data/a_share.db')
    
    query = f"""
    SELECT date, hold_ratio, change_ratio
    FROM northbound_capital
    WHERE code = '{code}'
    ORDER BY date DESC
    LIMIT {days}
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    if len(df) == 0:
        return {'status': 'no_data', 'message': '无北向资金数据'}
    
    # 计算连续买入/卖出天数
    consecutive_days = 0
    for _, row in df.iterrows():
        if row['change_ratio'] > 0:
            consecutive_days += 1
        elif row['change_ratio'] < 0:
            consecutive_days -= 1
        else:
            break
    
    # 判断状态
    if consecutive_days >= 3:
        status = 'green'
        message = f"外资连续{consecutive_days}天加仓，机构正在'抱团'"
    elif consecutive_days <= -3:
        status = 'red'
        message = f"外资连续{abs(consecutive_days)}天减仓，主力资金撤退"
    else:
        status = 'yellow'
        message = "外资持仓稳定，暂无明显动作"
    
    return {
        'status': status,
        'message': message,
        'consecutive_days': consecutive_days,
        'current_hold_ratio': df.iloc[0]['hold_ratio']
    }
```

### 场景2: 主力资金流向分析

**目标**: 判断主力资金是流入还是流出

```python
def analyze_capital_flow(code: str) -> dict:
    """分析主力资金流向"""
    conn = sqlite3.connect('data/a_share.db')
    
    query = f"""
    SELECT name, pct_chg, main_net_inflow, main_net_inflow_ratio
    FROM capital_flow
    WHERE code = '{code}'
    ORDER BY date DESC
    LIMIT 1
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    if len(df) == 0:
        return {'status': 'no_data', 'message': '无资金流向数据'}
    
    row = df.iloc[0]
    inflow = row['main_net_inflow']
    ratio = row['main_net_inflow_ratio']
    
    # 判断状态
    if inflow > 0 and ratio > 10:
        status = 'green'
        message = f"主力资金大幅流入，有大资金在建仓\n主力净流入: {inflow/1e8:.2f}亿 (占成交额{ratio:.1f}%)"
    elif inflow < 0 and ratio < -10:
        status = 'red'
        message = f"主力资金大幅流出，机构在出货\n主力净流出: {inflow/1e8:.2f}亿 (占成交额{ratio:.1f}%)"
    else:
        status = 'yellow'
        message = "资金流向正常"
    
    return {
        'status': status,
        'message': message,
        'main_net_inflow': inflow,
        'main_net_inflow_ratio': ratio
    }
```

### 场景3: 龙虎榜监控

**目标**: 监控游资和机构的动向

```python
def check_dragon_tiger(code: str, days: int = 30) -> dict:
    """检查是否上榜龙虎榜"""
    conn = sqlite3.connect('data/a_share.db')
    
    query = f"""
    SELECT date, reason, net_amount, pct_chg
    FROM dragon_tiger_list
    WHERE code = '{code}'
    AND date >= date('now', '-{days} days')
    ORDER BY date DESC
    """
    df = pd.read_sql(query, conn)
    conn.close()
    
    if len(df) == 0:
        return {'status': 'no_data', 'message': f'近{days}天未上榜龙虎榜'}
    
    latest = df.iloc[0]
    
    if latest['net_amount'] > 0:
        status = 'green'
        message = f"近期上榜龙虎榜（{latest['date']}）\n原因: {latest['reason']}\n净买入: {latest['net_amount']/1e8:.2f}亿"
    else:
        status = 'red'
        message = f"近期上榜龙虎榜（{latest['date']}）\n原因: {latest['reason']}\n净卖出: {abs(latest['net_amount'])/1e8:.2f}亿"
    
    return {
        'status': status,
        'message': message,
        'times': len(df),
        'latest_date': latest['date']
    }
```

---

## ⏰ 定时更新建议

### 每日更新计划

```bash
# 1. 收盘后更新资金流向（15:30）
python tools/fetch_capital_flow_data.py --mode flow

# 2. 晚上更新龙虎榜（20:00）
python tools/fetch_capital_flow_data.py --mode dragon

# 3. 每周更新北向资金（周末）
python tools/fetch_capital_flow_data.py --mode northbound --top 100
```

### Crontab 配置

```bash
# 每个交易日 15:30 更新资金流向
30 15 * * 1-5 cd /path/to/project && python tools/fetch_capital_flow_data.py --mode flow

# 每个交易日 20:00 更新龙虎榜
0 20 * * 1-5 cd /path/to/project && python tools/fetch_capital_flow_data.py --mode dragon

# 每周日 10:00 更新北向资金
0 10 * * 0 cd /path/to/project && python tools/fetch_capital_flow_data.py --mode northbound --top 100
```

---

## ⚠️ 注意事项

### 1. API限制

- AkShare是免费API，但有访问频率限制
- 建议批量更新时加入延迟（sleep）
- 避免短时间内大量请求

### 2. 数据延迟

- 资金流向数据：实时更新（交易时间）
- 龙虎榜数据：通常在交易日晚上8点后更新
- 北向资金数据：每日更新

### 3. 数据准确性

- 数据来源于公开市场，仅供参考
- 建议结合其他指标综合判断
- 不构成投资建议

### 4. 存储空间

- 北向资金：每只股票约1KB/天
- 资金流向：全市场约5MB/天
- 龙虎榜：约100KB/天

---

## 🔧 故障排查

### 问题1: 无法获取数据

```python
# 检查网络连接
import akshare as ak
df = ak.stock_hsgt_hold_stock_em(symbol="600519", market="北向")
print(df)
```

### 问题2: 数据表不存在

```python
# 重新初始化数据表
fetcher = CapitalFlowFetcher()
fetcher._init_tables()
```

### 问题3: 数据重复

```python
# 清理重复数据
import sqlite3
conn = sqlite3.connect('data/a_share.db')
cursor = conn.cursor()

# 删除重复的北向资金数据
cursor.execute("""
DELETE FROM northbound_capital
WHERE rowid NOT IN (
    SELECT MIN(rowid)
    FROM northbound_capital
    GROUP BY code, date, market
)
""")

conn.commit()
conn.close()
```

---

## 📚 相关文档

- `DATA_AVAILABILITY_ANALYSIS.md` - 数据可用性分析
- `ADVANCED_ANALYSIS_ROADMAP.md` - 高级分析路线图
- `src/data/capital_flow_fetcher.py` - 数据获取器源码
- `tools/fetch_capital_flow_data.py` - 命令行工具

---

## ✅ 下一步

1. ✅ 数据表已创建
2. ✅ 数据获取功能已实现
3. ⏳ 集成到持仓健康检查器
4. ⏳ 实现资金面分析逻辑
5. ⏳ 添加到盘后复盘系统

---

*文档更新时间: 2026-01-04*

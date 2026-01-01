# A股数据采集系统 - 使用指南

## 目录
1. [快速开始](#快速开始)
2. [完整下载](#完整下载)
3. [日常维护](#日常维护)
4. [数据查询](#数据查询)
5. [常见场景](#常见场景)

---

## 快速开始

### 第一次使用（测试）

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 快速测试（下载100只股票）
python quick_start.py

# 3. 查看示例
python example_usage.py
```

这会下载前100只股票的2024年数据，用于测试系统是否正常工作。

---

## 完整下载

### 下载全市场数据

```bash
# 下载最近2年数据（推荐）
python main.py download

# 下载最近3年数据
python main.py download --start-date 20220101

# 下载最近1年数据（更快）
python main.py download --start-date 20240101
```

**预计时间和空间：**
- 1年数据：约1小时，2GB
- 2年数据：约2小时，4GB
- 3年数据：约3小时，6GB

**注意事项：**
- 确保网络稳定
- 建议在非交易时间下载
- 可以随时中断，下次继续

### 断点续传

如果下载中断，直接重新运行即可：

```bash
python main.py download
```

系统会自动跳过已下载的股票。

### 强制重新下载

如果需要更新已有数据：

```bash
python main.py download --force
```

---

## 日常维护

### 每日更新

建议每天收盘后（15:30之后）运行：

```bash
# 更新今天的数据
python main.py update

# 更新指定日期
python main.py update --date 20251231
```

### 设置定时任务

**Linux/Mac (crontab):**

```bash
# 编辑定时任务
crontab -e

# 添加以下行（每天16:00执行）
0 16 * * 1-5 cd /path/to/project && python main.py update
```

**Windows (任务计划程序):**

1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：每天16:00
4. 操作：启动程序 `python main.py update`

---

## 数据查询

### 查看数据库状态

```bash
python main.py status
```

输出示例：
```
📊 数据库状态报告
==================================================
【基本信息】
  总股票数: 5234
  已下载: 5234
  完成度: 100.0%
  总记录数: 2,617,000
  平均每只: 500 条
```

### Python API 查询

```python
from database import StockDatabase

# 初始化
db = StockDatabase("data/a_share.db")

# 1. 获取股票列表
stock_list = db.get_stock_list()
print(stock_list.head())

# 2. 查询单只股票
df = db.get_daily_data("sh.600000")
print(df.tail())

# 3. 指定日期范围
df = db.get_daily_data("sh.600000", 
                       start_date="20240101", 
                       end_date="20241231")

# 4. 检查数据是否存在
if db.table_exists("sh.600000"):
    print("数据存在")

# 5. 获取最后更新日期
last_date = db.get_last_date("sh.600000")
print(f"最后更新: {last_date}")

# 关闭连接
db.close()
```

---

## 常见场景

### 场景1: 技术指标计算

```python
from database import StockDatabase
import pandas as pd

db = StockDatabase("data/a_share.db")

# 获取数据
df = db.get_daily_data("sh.600000", start_date="20240101")

# 计算均线
df['ma5'] = df['close'].rolling(5).mean()
df['ma10'] = df['close'].rolling(10).mean()
df['ma20'] = df['close'].rolling(20).mean()

# 计算MACD
exp1 = df['close'].ewm(span=12, adjust=False).mean()
exp2 = df['close'].ewm(span=26, adjust=False).mean()
df['macd'] = exp1 - exp2
df['signal'] = df['macd'].ewm(span=9, adjust=False).mean()

# 计算RSI
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
df['rsi'] = 100 - (100 / (1 + rs))

print(df[['date', 'close', 'ma5', 'ma20', 'macd', 'rsi']].tail())

db.close()
```

### 场景2: 批量选股

```python
from database import StockDatabase
import pandas as pd

db = StockDatabase("data/a_share.db")
stock_list = db.get_stock_list()

results = []

for _, row in stock_list.iterrows():
    code = row.get('full_code', f"{row['market']}.{row['code']}")
    
    # 获取最近数据
    df = db.get_daily_data(code)
    
    if len(df) < 20:
        continue
    
    # 计算指标
    df['ma20'] = df['close'].rolling(20).mean()
    latest = df.iloc[-1]
    
    # 选股条件：价格突破20日均线
    if latest['close'] > latest['ma20']:
        results.append({
            '代码': code,
            '名称': row['name'],
            '最新价': latest['close'],
            'MA20': latest['ma20']
        })

result_df = pd.DataFrame(results)
print(f"找到 {len(result_df)} 只符合条件的股票")
print(result_df.head(10))

db.close()
```

### 场景3: 回测策略

```python
from database import StockDatabase
import pandas as pd

db = StockDatabase("data/a_share.db")

# 获取数据
df = db.get_daily_data("sh.600000", start_date="20240101")

# 简单策略：5日均线上穿20日均线买入
df['ma5'] = df['close'].rolling(5).mean()
df['ma20'] = df['close'].rolling(20).mean()

# 生成信号
df['signal'] = 0
df.loc[df['ma5'] > df['ma20'], 'signal'] = 1
df['position'] = df['signal'].diff()

# 计算收益
buy_signals = df[df['position'] == 1]
sell_signals = df[df['position'] == -1]

print(f"买入信号: {len(buy_signals)} 次")
print(f"卖出信号: {len(sell_signals)} 次")

# 计算每次交易收益
trades = []
for i in range(min(len(buy_signals), len(sell_signals))):
    buy_price = buy_signals.iloc[i]['close']
    sell_price = sell_signals.iloc[i]['close']
    profit = (sell_price - buy_price) / buy_price * 100
    trades.append(profit)

if trades:
    print(f"平均收益: {sum(trades)/len(trades):.2f}%")
    print(f"胜率: {len([t for t in trades if t > 0])/len(trades)*100:.1f}%")

db.close()
```

### 场景4: 市场分析

```python
from database import StockDatabase
import pandas as pd

db = StockDatabase("data/a_share.db")

# 获取市场快照
snapshot = pd.read_sql(
    "SELECT * FROM market_snapshot WHERE date = (SELECT MAX(date) FROM market_snapshot)",
    db.conn
)

# 市场统计
print("📊 市场概况:")
print(f"上涨家数: {len(snapshot[snapshot['pct_chg'] > 0])}")
print(f"下跌家数: {len(snapshot[snapshot['pct_chg'] < 0])}")
print(f"平均涨跌幅: {snapshot['pct_chg'].mean():.2f}%")

# 市值分布
snapshot['cap_level'] = pd.cut(
    snapshot['total_cap'] / 1e8,
    bins=[0, 50, 200, 1000, float('inf')],
    labels=['小盘', '中盘', '大盘', '超大盘']
)

print("\n市值分布:")
print(snapshot['cap_level'].value_counts())

# 行业分析（如果有行业数据）
# ...

db.close()
```

---

## 故障排除

### 问题1: 下载速度慢

**解决方案:**
- 检查网络连接
- 在非交易时间下载
- 调整 `config.py` 中的 `SLEEP_INTERVAL`

### 问题2: 某些股票下载失败

**原因:**
- 股票已退市
- 股票停牌
- 网络临时故障

**解决方案:**
- 系统会自动重试3次
- 查看日志文件了解详情
- 失败的股票会在下次运行时重试

### 问题3: 数据库文件过大

**解决方案:**
```python
# 删除旧数据
from database import StockDatabase
import sqlite3

db = StockDatabase("data/a_share.db")

# 只保留最近1年数据
cursor = db.conn.cursor()
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name LIKE 'daily_%'
""")

for (table_name,) in cursor.fetchall():
    cursor.execute(f"""
        DELETE FROM {table_name} 
        WHERE date < date('now', '-1 year')
    """)

db.conn.commit()
db.close()

# 压缩数据库
conn = sqlite3.connect("data/a_share.db")
conn.execute("VACUUM")
conn.close()
```

---

## 性能优化

### 1. 使用索引加速查询

```python
from database import StockDatabase

db = StockDatabase("data/a_share.db")
cursor = db.conn.cursor()

# 为日期字段创建索引
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name LIKE 'daily_%'
""")

for (table_name,) in cursor.fetchall():
    try:
        cursor.execute(f"CREATE INDEX IF NOT EXISTS idx_{table_name}_date ON {table_name}(date)")
    except:
        pass

db.conn.commit()
db.close()
```

### 2. 批量查询

```python
# 不推荐：逐个查询
for code in codes:
    df = db.get_daily_data(code)
    # 处理...

# 推荐：批量查询
import pandas as pd

all_data = []
for code in codes:
    df = db.get_daily_data(code)
    all_data.append(df)

combined = pd.concat(all_data, ignore_index=True)
```

---

## 下一步

基于这个数据库，你可以：

1. **开发量化策略** - 实现你的缩量三连跌策略
2. **技术分析** - 计算各种技术指标
3. **选股系统** - 构建自动化选股工具
4. **回测平台** - 验证交易策略
5. **可视化分析** - 使用 matplotlib/plotly 绘图

参考 `example_usage.py` 了解更多用法！

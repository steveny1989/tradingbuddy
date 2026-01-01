# 快速参考

## 常用命令

```bash
# 首次使用
pip install -r requirements.txt
python quick_start.py

# 下载全市场数据
python main.py download

# 每日更新
python main.py update

# 查看状态
python main.py status

# 查看示例
python example_usage.py
```

## Python API 速查

### 初始化
```python
from database import StockDatabase
db = StockDatabase("data/a_share.db")
```

### 股票列表
```python
# 获取所有股票
stocks = db.get_stock_list()

# 筛选上海股票
sh_stocks = stocks[stocks['market'] == 'sh']
```

### 查询数据
```python
# 查询单只股票
df = db.get_daily_data("sh.600000")

# 指定日期范围
df = db.get_daily_data("sh.600000", 
                       start_date="20240101",
                       end_date="20241231")

# 检查数据是否存在
if db.table_exists("sh.600000"):
    print("数据存在")
```

### 技术指标
```python
# 均线
df['ma5'] = df['close'].rolling(5).mean()
df['ma20'] = df['close'].rolling(20).mean()

# MACD
exp1 = df['close'].ewm(span=12).mean()
exp2 = df['close'].ewm(span=26).mean()
df['macd'] = exp1 - exp2

# RSI
delta = df['close'].diff()
gain = delta.where(delta > 0, 0).rolling(14).mean()
loss = -delta.where(delta < 0, 0).rolling(14).mean()
df['rsi'] = 100 - (100 / (1 + gain/loss))

# 布林带
df['bb_mid'] = df['close'].rolling(20).mean()
df['bb_std'] = df['close'].rolling(20).std()
df['bb_upper'] = df['bb_mid'] + 2 * df['bb_std']
df['bb_lower'] = df['bb_mid'] - 2 * df['bb_std']
```

### 选股示例
```python
# 找出突破20日均线的股票
results = []
for _, row in stocks.iterrows():
    code = row['full_code']
    df = db.get_daily_data(code)
    
    if len(df) < 20:
        continue
    
    df['ma20'] = df['close'].rolling(20).mean()
    latest = df.iloc[-1]
    
    if latest['close'] > latest['ma20']:
        results.append({
            'code': code,
            'name': row['name'],
            'price': latest['close']
        })
```

## 数据库表结构

### stock_basic
```
code, name, market, list_date, status, updated_at
```

### daily_XXX
```
date, code, open, high, low, close, volume, amount, pct_chg, turnover
```

### market_snapshot
```
code, date, price, pct_chg, volume, amount, pe_ttm, pb, total_cap, float_cap
```

## 配置参数

编辑 `config.py`:

```python
# 数据库路径
DB_PATH = "data/a_share.db"

# 数据范围
START_DATE = "20230101"

# 采集控制
BATCH_SIZE = 100
SLEEP_INTERVAL = 0.5
MAX_RETRIES = 3
```

## 常见问题

### Q: 如何只下载特定股票？
```python
from database import StockDatabase
from data_fetcher import DataFetcher

db = StockDatabase()
fetcher = DataFetcher(db)

# 只下载指定股票
codes = ['600000', '000001', '000002']
for code in codes:
    df = fetcher.fetch_history(code)
    if df is not None:
        db.save_daily_data(f"sh.{code}", df)
```

### Q: 如何导出数据到CSV？
```python
df = db.get_daily_data("sh.600000")
df.to_csv("600000.csv", index=False)
```

### Q: 如何批量导出？
```python
stocks = db.get_stock_list()
for _, row in stocks.iterrows():
    code = row['full_code']
    df = db.get_daily_data(code)
    if not df.empty:
        df.to_csv(f"export/{code}.csv", index=False)
```

### Q: 如何清理旧数据？
```python
import sqlite3
conn = sqlite3.connect("data/a_share.db")
cursor = conn.cursor()

# 删除1年前的数据
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name LIKE 'daily_%'
""")

for (table,) in cursor.fetchall():
    cursor.execute(f"""
        DELETE FROM {table} 
        WHERE date < date('now', '-1 year')
    """)

conn.commit()
conn.close()
```

### Q: 如何备份数据库？
```bash
# 简单备份
cp data/a_share.db data/backup_$(date +%Y%m%d).db

# 压缩备份
tar -czf backup.tar.gz data/

# 恢复
tar -xzf backup.tar.gz
```

## 性能优化

### 创建索引
```python
cursor = db.conn.cursor()
cursor.execute("""
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name LIKE 'daily_%'
""")

for (table,) in cursor.fetchall():
    cursor.execute(f"""
        CREATE INDEX IF NOT EXISTS idx_{table}_date 
        ON {table}(date)
    """)
```

### 批量查询
```python
# 不推荐
for code in codes:
    df = db.get_daily_data(code)

# 推荐
import pandas as pd
dfs = [db.get_daily_data(code) for code in codes]
combined = pd.concat(dfs, ignore_index=True)
```

## 日志查看

```bash
# 查看今天的日志
tail -f logs/data_sync_$(date +%Y%m%d).log

# 查看错误
grep ERROR logs/data_sync_*.log

# 统计成功率
grep "成功" logs/data_sync_*.log | wc -l
```

## 定时任务

### Linux/Mac (crontab)
```bash
# 每天16:00更新
0 16 * * 1-5 cd /path/to/project && python main.py update

# 每周日凌晨备份
0 2 * * 0 cd /path/to/project && tar -czf backup_$(date +\%Y\%m\%d).tar.gz data/
```

### Windows (任务计划程序)
1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：每天 16:00
4. 操作：`python C:\path\to\main.py update`

## 故障排除

### 数据库锁定
```python
# 使用 WAL 模式
import sqlite3
conn = sqlite3.connect("data/a_share.db")
conn.execute("PRAGMA journal_mode=WAL")
conn.close()
```

### 内存不足
```python
# 减小批次大小
BATCH_SIZE = 50  # 在 config.py 中修改
```

### 网络超时
```python
# 增加重试次数
MAX_RETRIES = 5  # 在 config.py 中修改
```

## 更多资源

- 完整文档：`README.md`
- 使用指南：`USAGE_GUIDE.md`
- 项目结构：`PROJECT_STRUCTURE.md`
- 重构说明：`REFACTOR_SUMMARY.md`
- 代码示例：`example_usage.py`

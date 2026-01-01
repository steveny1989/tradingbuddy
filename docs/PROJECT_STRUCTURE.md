# 项目结构说明

## 文件组织

```
a-stock-ai-tool/
├── config.py              # 配置文件（数据库路径、日期范围等）
├── database.py            # 数据库管理模块
├── data_fetcher.py        # 数据采集模块
├── main.py                # 主程序入口
├── quick_start.py         # 快速启动脚本
├── example_usage.py       # 使用示例
├── requirements.txt       # Python依赖
├── README.md              # 项目说明
├── USAGE_GUIDE.md         # 使用指南
├── .gitignore            # Git忽略文件
│
├── data/                  # 数据目录（自动创建）
│   └── a_share.db        # SQLite数据库
│
└── logs/                  # 日志目录（自动创建）
    └── data_sync_*.log   # 同步日志
```

## 核心模块说明

### 1. config.py
配置文件，包含：
- 数据库路径
- 数据采集日期范围
- 批次大小和请求间隔
- 字段映射关系

### 2. database.py
数据库管理类 `StockDatabase`，提供：
- 数据库初始化
- 股票列表管理
- 日线数据存储和查询
- 同步状态跟踪
- 统计信息查询

**主要方法：**
```python
db = StockDatabase("data/a_share.db")
db.save_stock_list(df)           # 保存股票列表
db.get_stock_list()              # 获取股票列表
db.save_daily_data(code, df)     # 保存日线数据
db.get_daily_data(code)          # 查询日线数据
db.get_statistics()              # 获取统计信息
```

### 3. data_fetcher.py
数据采集类 `DataFetcher`，提供：
- 股票列表获取
- 历史数据下载
- 批量下载管理
- 增量更新
- 市场快照获取

**主要方法：**
```python
fetcher = DataFetcher(db)
fetcher.fetch_stock_list()       # 获取股票列表
fetcher.fetch_history(code)      # 获取单只股票数据
fetcher.batch_fetch_all()        # 批量下载全市场
fetcher.update_daily()           # 每日增量更新
```

### 4. main.py
命令行主程序，支持三种操作：
```bash
python main.py download          # 全量下载
python main.py update            # 增量更新
python main.py status            # 查看状态
```

### 5. quick_start.py
快速启动脚本，用于：
- 首次测试系统
- 下载少量数据验证
- 演示基本功能

### 6. example_usage.py
使用示例，包含：
- 基础数据查询
- 技术指标计算
- 简单选股示例
- 市场概览分析

## 数据库结构

### 表1: stock_basic（股票基本信息）
```sql
CREATE TABLE stock_basic (
    code TEXT PRIMARY KEY,      -- 股票代码（如：600000）
    name TEXT,                  -- 股票名称
    market TEXT,                -- 市场（sh/sz/bj）
    list_date TEXT,             -- 上市日期
    status TEXT,                -- 状态（active/delisted）
    updated_at TEXT             -- 更新时间
)
```

### 表2: daily_XXX（日线数据，每只股票一张表）
```sql
CREATE TABLE daily_sh_600000 (
    date TEXT,                  -- 日期
    code TEXT,                  -- 股票代码
    open REAL,                  -- 开盘价
    high REAL,                  -- 最高价
    low REAL,                   -- 最低价
    close REAL,                 -- 收盘价
    volume REAL,                -- 成交量
    amount REAL,                -- 成交额
    pct_chg REAL,              -- 涨跌幅
    turnover REAL              -- 换手率
)
```

### 表3: market_snapshot（市场快照）
```sql
CREATE TABLE market_snapshot (
    code TEXT,                  -- 股票代码
    date TEXT,                  -- 日期
    price REAL,                 -- 最新价
    pct_chg REAL,              -- 涨跌幅
    volume REAL,                -- 成交量
    amount REAL,                -- 成交额
    pe_ttm REAL,               -- 市盈率
    pb REAL,                    -- 市净率
    total_cap REAL,            -- 总市值
    float_cap REAL,            -- 流通市值
    turnover REAL,             -- 换手率
    PRIMARY KEY (code, date)
)
```

### 表4: sync_status（同步状态）
```sql
CREATE TABLE sync_status (
    code TEXT PRIMARY KEY,      -- 股票代码
    last_sync_date TEXT,        -- 最后同步日期
    total_records INTEGER,      -- 总记录数
    status TEXT,                -- 状态（success/failed）
    error_msg TEXT,             -- 错误信息
    updated_at TEXT             -- 更新时间
)
```

## 数据流程

### 首次下载流程
```
1. 运行 python main.py download
   ↓
2. 获取全市场股票列表（5000+只）
   ↓
3. 保存到 stock_basic 表
   ↓
4. 循环每只股票：
   - 调用 akshare 获取历史数据
   - 保存到 daily_XXX 表
   - 更新 sync_status
   ↓
5. 完成，显示统计信息
```

### 每日更新流程
```
1. 运行 python main.py update
   ↓
2. 读取 stock_basic 获取股票列表
   ↓
3. 循环每只股票：
   - 获取今日数据
   - 追加到 daily_XXX 表
   ↓
4. 获取市场快照
   ↓
5. 保存到 market_snapshot 表
   ↓
6. 完成
```

### 数据查询流程
```
1. 初始化 StockDatabase
   ↓
2. 调用 get_daily_data(code)
   ↓
3. 从 daily_XXX 表查询
   ↓
4. 返回 DataFrame
   ↓
5. 进行分析/计算
```

## 扩展开发

### 添加新的数据源
在 `data_fetcher.py` 中添加新方法：
```python
def fetch_financial_data(self, code):
    """获取财务数据"""
    # 实现逻辑
    pass
```

### 添加新的数据表
在 `database.py` 的 `_init_tables()` 中添加：
```python
cursor.execute("""
    CREATE TABLE IF NOT EXISTS financial_data (
        code TEXT,
        date TEXT,
        revenue REAL,
        profit REAL,
        PRIMARY KEY (code, date)
    )
""")
```

### 添加新的策略
创建新文件 `strategy.py`：
```python
from database import StockDatabase

class Strategy:
    def __init__(self, db):
        self.db = db
    
    def run(self):
        # 实现策略逻辑
        pass
```

## 性能考虑

### 存储优化
- 每只股票独立表，避免单表过大
- 使用 SQLite 的 WAL 模式提升并发
- 定期 VACUUM 压缩数据库

### 查询优化
- 为 date 字段创建索引
- 使用日期范围查询减少数据量
- 批量查询代替逐个查询

### 下载优化
- 断点续传避免重复下载
- 批次处理控制内存使用
- 限速避免被封IP

## 维护建议

### 日常维护
- 每天收盘后运行 `update`
- 每周检查 `status`
- 每月清理日志文件

### 数据备份
```bash
# 备份数据库
cp data/a_share.db data/a_share_backup_$(date +%Y%m%d).db

# 压缩备份
tar -czf backup_$(date +%Y%m%d).tar.gz data/
```

### 故障恢复
```bash
# 如果数据库损坏
rm data/a_share.db
python main.py download --force
```

## 下一步开发计划

1. **Web界面** - 使用 Flask/FastAPI 提供 Web 查询界面
2. **实时数据** - 集成实时行情推送
3. **更多指标** - 添加财务数据、资金流向等
4. **策略回测** - 完整的回测框架
5. **可视化** - 图表展示和分析工具

参考现有的 `app.py` 和 `routes.py` 可以快速搭建 Web 界面！

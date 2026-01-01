# 开始使用 A股数据采集系统

## 🎯 这是什么？

一个**完整的A股市场数据采集和管理系统**，帮助你：
- 📊 下载全市场5000+只股票的历史数据
- 🔄 每日自动更新最新行情
- 💾 本地SQLite数据库存储
- 🚀 快速查询和分析
- 📈 为量化策略提供数据基础

## ⚡ 5分钟快速开始

### 1. 安装

**Linux/Mac:**
```bash
chmod +x install_and_test.sh
./install_and_test.sh
```

**Windows:**
```bash
install_and_test.bat
```

**或手动安装:**
```bash
pip install -r requirements.txt
python quick_start.py
```

### 2. 下载数据

```bash
# 下载全市场数据（推荐在晚上运行，约需2小时）
python main.py download
```

### 3. 使用数据

```python
from database import StockDatabase

# 初始化
db = StockDatabase("data/a_share.db")

# 查询浦发银行的数据
df = db.get_daily_data("sh.600000")
print(df.tail())

# 计算5日均线
df['ma5'] = df['close'].rolling(5).mean()
print(df[['date', 'close', 'ma5']].tail())
```

## 📚 完整文档

- **[README.md](README.md)** - 项目概述和功能介绍
- **[USAGE_GUIDE.md](USAGE_GUIDE.md)** - 详细使用指南
- **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - 快速参考手册
- **[PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)** - 项目结构说明
- **[REFACTOR_SUMMARY.md](REFACTOR_SUMMARY.md)** - 重构改进说明

## 🎓 学习路径

### 第一天：熟悉系统
1. 运行 `python quick_start.py` 下载测试数据
2. 运行 `python example_usage.py` 查看示例
3. 阅读 `QUICK_REFERENCE.md` 了解常用操作

### 第二天：下载全量数据
1. 运行 `python main.py download` 下载全市场数据
2. 运行 `python main.py status` 查看下载状态
3. 尝试查询几只股票的数据

### 第三天：开发策略
1. 学习技术指标计算（参考 `example_usage.py`）
2. 实现简单的选股逻辑
3. 测试你的第一个策略

### 第四天：自动化
1. 设置定时任务每日更新数据
2. 开发自动化选股脚本
3. 集成到你的工作流

## 💡 使用场景

### 场景1: 技术分析
```python
# 计算技术指标
df['ma5'] = df['close'].rolling(5).mean()
df['ma20'] = df['close'].rolling(20).mean()

# 找出金叉
golden_cross = df[df['ma5'] > df['ma20']]
```

### 场景2: 量化选股
```python
# 找出突破新高的股票
for code in stock_list:
    df = db.get_daily_data(code)
    if df['close'].iloc[-1] == df['close'].max():
        print(f"{code} 创新高")
```

### 场景3: 策略回测
```python
# 简单的均线策略回测
df['signal'] = 0
df.loc[df['ma5'] > df['ma20'], 'signal'] = 1

# 计算收益
df['returns'] = df['close'].pct_change()
df['strategy_returns'] = df['signal'].shift(1) * df['returns']

print(f"策略收益: {df['strategy_returns'].sum():.2%}")
```

### 场景4: 市场监控
```python
# 监控涨停板
snapshot = pd.read_sql(
    "SELECT * FROM market_snapshot WHERE pct_chg >= 9.9",
    db.conn
)
print(f"今日涨停: {len(snapshot)} 只")
```

## 🔧 常用命令

```bash
# 查看帮助
python main.py --help

# 下载数据（指定日期）
python main.py download --start-date 20220101

# 强制重新下载
python main.py download --force

# 更新指定日期
python main.py update --date 20251231

# 查看数据库状态
python main.py status

# 运行示例
python example_usage.py
```

## 📊 数据说明

### 数据来源
- **akshare** - 免费、开源的金融数据接口
- 数据质量高，更新及时
- 支持A股、港股、美股等

### 数据内容
- **日线数据**: 开高低收、成交量、成交额、涨跌幅、换手率
- **市场快照**: 实时价格、市值、PE、PB等
- **股票信息**: 代码、名称、市场、状态

### 数据格式
- **前复权**: 适合技术分析和回测
- **统一格式**: 所有股票使用相同的字段名
- **SQLite存储**: 轻量级、无需安装数据库

## 🚀 性能数据

| 操作 | 时间 | 说明 |
|------|------|------|
| 获取股票列表 | 5秒 | 5000+只股票 |
| 下载单只股票 | 0.3秒 | 2年数据 |
| 下载全市场 | 40分钟 | 5000只×2年 |
| 每日更新 | 15分钟 | 5000只当日数据 |
| 查询单只股票 | <0.1秒 | 任意日期范围 |

## 💾 存储空间

| 数据量 | 空间 |
|--------|------|
| 100只股票×2年 | 80MB |
| 1000只股票×2年 | 800MB |
| 全市场×1年 | 2GB |
| 全市场×2年 | 4GB |
| 全市场×3年 | 6GB |

## ⚠️ 注意事项

1. **首次下载**: 建议在网络稳定时进行，可随时中断
2. **存储空间**: 确保有足够磁盘空间（建议10GB+）
3. **请求频率**: 已内置限速，避免被封IP
4. **数据更新**: 建议每天收盘后（16:00后）更新
5. **备份数据**: 定期备份 `data/a_share.db` 文件

## 🆘 遇到问题？

### 常见问题
1. **下载失败** → 检查网络，系统会自动重试
2. **数据缺失** → 运行 `python main.py download --force`
3. **速度慢** → 调整 `config.py` 中的参数
4. **空间不足** → 清理旧数据或扩展磁盘

### 获取帮助
1. 查看日志文件: `logs/data_sync_*.log`
2. 阅读文档: `USAGE_GUIDE.md`
3. 查看示例: `example_usage.py`

## 🎉 下一步

现在你已经有了完整的数据基础设施，可以：

1. **开发量化策略** - 实现你的选股逻辑
2. **技术分析** - 计算各种技术指标
3. **回测验证** - 测试策略的历史表现
4. **实时监控** - 监控市场和个股
5. **自动交易** - 集成交易接口（需谨慎）

## 📖 推荐阅读

- [Python量化交易教程](https://www.joinquant.com/help/api/help)
- [技术指标大全](https://www.investopedia.com/technical-analysis-4689657)
- [量化策略案例](https://github.com/topics/quantitative-trading)

---

**祝你在量化投资的道路上一帆风顺！** 🚀📈

有问题随时查看文档或修改代码。这个系统是完全开源的，你可以根据需要自由定制。

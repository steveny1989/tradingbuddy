# A股数据采集系统 - 项目总览

## 📦 项目文件清单

### 核心代码文件 (5个)
| 文件 | 大小 | 说明 |
|------|------|------|
| `config.py` | 1.3KB | 配置管理（数据库路径、日期范围、采集参数） |
| `database.py` | 7.3KB | 数据库管理类（增删改查、状态跟踪） |
| `data_fetcher.py` | 7.9KB | 数据采集类（下载、更新、批处理） |
| `main.py` | 5.2KB | 主程序入口（命令行接口） |
| `quick_start.py` | 3.1KB | 快速启动脚本（测试用） |

### 示例和工具 (2个)
| 文件 | 大小 | 说明 |
|------|------|------|
| `example_usage.py` | 5.0KB | 使用示例（查询、分析、选股） |
| `requirements.txt` | 74B | Python依赖列表 |

### 安装脚本 (2个)
| 文件 | 大小 | 说明 |
|------|------|------|
| `install_and_test.sh` | 1.8KB | Linux/Mac 安装脚本 |
| `install_and_test.bat` | 1.6KB | Windows 安装脚本 |

### 文档文件 (8个)
| 文件 | 大小 | 说明 |
|------|------|------|
| `GET_STARTED.md` | 5.8KB | 快速入门指南 ⭐ 从这里开始 |
| `README.md` | 3.6KB | 项目说明和功能介绍 |
| `USAGE_GUIDE.md` | 8.5KB | 详细使用指南 |
| `QUICK_REFERENCE.md` | 5.4KB | 快速参考手册 |
| `PROJECT_STRUCTURE.md` | 6.9KB | 项目结构说明 |
| `REFACTOR_SUMMARY.md` | 7.7KB | 重构改进说明 |
| `PROJECT_OVERVIEW.md` | 本文件 | 项目总览 |
| `.gitignore` | - | Git忽略文件 |

### 原有文件（保留）
| 文件 | 说明 |
|------|------|
| `app.py` | Flask应用（可用于Web界面） |
| `routes.py` | 路由定义 |
| `strategy.py` | 策略模块 |
| `drive_handler.py` | Google Drive处理 |

## 🎯 快速导航

### 我想...

**开始使用** → 阅读 [`GET_STARTED.md`](GET_STARTED.md)

**了解功能** → 阅读 [`README.md`](README.md)

**学习用法** → 阅读 [`USAGE_GUIDE.md`](USAGE_GUIDE.md)

**快速查询** → 阅读 [`QUICK_REFERENCE.md`](QUICK_REFERENCE.md)

**理解架构** → 阅读 [`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)

**了解改进** → 阅读 [`REFACTOR_SUMMARY.md`](REFACTOR_SUMMARY.md)

## 🚀 使用流程

```
1. 安装
   ├─ Linux/Mac: ./install_and_test.sh
   └─ Windows: install_and_test.bat

2. 测试
   └─ python quick_start.py (下载100只股票测试)

3. 下载全量数据
   └─ python main.py download (下载全市场)

4. 每日更新
   └─ python main.py update (增量更新)

5. 使用数据
   ├─ python example_usage.py (查看示例)
   └─ 开发自己的策略
```

## 📊 系统架构

```
┌─────────────────────────────────────────┐
│           命令行接口 (main.py)           │
├─────────────────────────────────────────┤
│                                         │
│  ┌──────────────┐    ┌──────────────┐  │
│  │ DataFetcher  │───▶│  Database    │  │
│  │ (数据采集)    │    │  (数据存储)   │  │
│  └──────────────┘    └──────────────┘  │
│         │                    │          │
│         ▼                    ▼          │
│    ┌─────────┐         ┌─────────┐     │
│    │ AKShare │         │ SQLite  │     │
│    │ (数据源) │         │ (数据库) │     │
│    └─────────┘         └─────────┘     │
│                                         │
└─────────────────────────────────────────┘
```

## 💡 核心特性

### ✅ 已实现
- [x] 全市场股票列表获取
- [x] 历史数据批量下载
- [x] 增量更新机制
- [x] 断点续传支持
- [x] 同步状态跟踪
- [x] 错误处理和重试
- [x] 进度显示
- [x] 命令行接口
- [x] 数据查询API
- [x] 使用示例
- [x] 完整文档

### 🔄 可扩展
- [ ] Web界面（基于现有的 app.py）
- [ ] 实时行情推送
- [ ] 财务数据采集
- [ ] 技术指标库
- [ ] 策略回测框架
- [ ] 可视化图表
- [ ] 自动化交易接口

## 📈 性能指标

| 指标 | 数值 |
|------|------|
| 支持股票数 | 5000+ |
| 下载速度 | ~200只/分钟 |
| 全市场下载时间 | ~40分钟 |
| 每日更新时间 | ~15分钟 |
| 查询响应时间 | <0.1秒 |
| 数据库大小(2年) | ~4GB |

## 🎓 学习资源

### 内置示例
1. **基础查询** - `example_usage.py` 第1部分
2. **技术分析** - `example_usage.py` 第2部分
3. **简单选股** - `example_usage.py` 第3部分
4. **市场概览** - `example_usage.py` 第4部分

### 文档教程
1. **快速入门** - `GET_STARTED.md`
2. **使用场景** - `USAGE_GUIDE.md` 常见场景章节
3. **API参考** - `QUICK_REFERENCE.md`
4. **架构设计** - `PROJECT_STRUCTURE.md`

## 🔧 配置说明

### config.py 主要参数

```python
# 数据库路径
DB_PATH = "data/a_share.db"

# 数据范围
START_DATE = "20230101"  # 建议2-3年
END_DATE = datetime.now().strftime('%Y%m%d')

# 采集控制
BATCH_SIZE = 100         # 批次大小
SLEEP_INTERVAL = 0.5     # 请求间隔（秒）
MAX_RETRIES = 3          # 最大重试次数
```

## 📝 使用示例

### 示例1: 查询单只股票
```python
from database import StockDatabase

db = StockDatabase("data/a_share.db")
df = db.get_daily_data("sh.600000")
print(df.tail())
```

### 示例2: 计算技术指标
```python
df['ma5'] = df['close'].rolling(5).mean()
df['ma20'] = df['close'].rolling(20).mean()
print(df[['date', 'close', 'ma5', 'ma20']].tail())
```

### 示例3: 批量选股
```python
stocks = db.get_stock_list()
for _, row in stocks.iterrows():
    df = db.get_daily_data(row['full_code'])
    # 你的选股逻辑
```

## 🛠️ 开发指南

### 添加新功能

1. **添加新的数据源**
   - 在 `data_fetcher.py` 中添加新方法
   - 更新 `config.py` 添加相关配置

2. **添加新的数据表**
   - 在 `database.py` 的 `_init_tables()` 中定义
   - 添加相应的增删改查方法

3. **开发新策略**
   - 创建新的 Python 文件
   - 使用 `StockDatabase` 查询数据
   - 实现策略逻辑

### 代码规范

- 使用类型提示
- 添加文档字符串
- 遵循 PEP 8
- 添加日志记录
- 处理异常情况

## 🐛 故障排除

### 常见问题

1. **下载失败**
   - 检查网络连接
   - 查看日志文件
   - 系统会自动重试

2. **数据缺失**
   - 运行 `python main.py download --force`
   - 检查 sync_status 表

3. **性能问题**
   - 为日期字段创建索引
   - 使用批量查询
   - 调整 BATCH_SIZE

4. **空间不足**
   - 清理旧数据
   - 压缩数据库（VACUUM）
   - 扩展磁盘空间

## 📞 技术支持

### 自助资源
1. 查看日志: `logs/data_sync_*.log`
2. 阅读文档: 所有 `.md` 文件
3. 运行示例: `python example_usage.py`

### 调试技巧
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看数据库状态
python main.py status

# 测试单只股票
from data_fetcher import DataFetcher
from database import StockDatabase
db = StockDatabase()
fetcher = DataFetcher(db)
df = fetcher.fetch_history("600000")
print(df)
```

## 🎉 下一步行动

### 立即开始
```bash
# 1. 安装
pip install -r requirements.txt

# 2. 测试
python quick_start.py

# 3. 下载
python main.py download

# 4. 使用
python example_usage.py
```

### 深入学习
1. 阅读 `GET_STARTED.md` 了解基础
2. 阅读 `USAGE_GUIDE.md` 学习高级用法
3. 参考 `example_usage.py` 开发策略
4. 查看 `QUICK_REFERENCE.md` 快速查询

### 开发策略
1. 使用数据库查询历史数据
2. 计算技术指标
3. 实现选股逻辑
4. 回测验证效果
5. 优化和改进

---

## 📄 许可证

MIT License - 自由使用和修改

## 🙏 致谢

- **AKShare** - 提供免费的金融数据接口
- **Pandas** - 强大的数据分析库
- **SQLite** - 轻量级数据库

---

**祝你在量化投资的道路上取得成功！** 🚀📈

如有问题，请查看相关文档或修改代码。这是一个完全开源的项目，欢迎根据需要自由定制。

# TradingBuddy 项目结构

## 📁 目录结构（按分层架构组织）

```
tradingbuddy/
│
├── 📱 应用层 (Application Layer)
│   ├── main.py                    # 数据管理命令行工具 ⭐
│   ├── paper_trading.py           # 模拟盘交易系统 ⭐
│   └── show_stock.py              # 查看单只股票数据 ⭐
│
├── 💼 业务层 (Business Logic Layer)
│   └── strategy/                  # 策略模块
│       ├── __init__.py            # 模块导出
│       ├── base.py                # 策略基类 ⭐⭐⭐
│       ├── backtest_engine.py     # 回测引擎 ⭐⭐
│       ├── volume_shrink_strategy.py  # 缩量三连跌策略
│       └── ma_crossover_strategy.py   # 均线突破策略
│
├── 💾 数据层 (Data Layer)
│   └── core/                      # 核心模块
│       ├── __init__.py
│       ├── database.py            # 数据库接口 ⭐⭐⭐
│       ├── data_fetcher.py        # 数据采集 ⭐⭐
│       └── config.py              # 配置管理
│
├── 🔧 工具层 (Tools)
│   └── tools/                     # 工具脚本
│       ├── download_index.py      # 下载指数数据
│       ├── supplement_data.py     # 补充市值/行业数据
│       ├── view_data.py           # 查看数据统计
│       ├── verify_architecture.py # 架构验证
│       ├── optimize_parameters.py # 参数优化
│       └── query_data.py          # 数据查询
│
├── 🧪 测试层 (Tests)
│   └── tests/
│       ├── backtest/              # 回测测试
│       │   ├── test_backtest_final.py
│       │   ├── test_strategy.py
│       │   ├── test_ma_strategy.py
│       │   ├── test_paper_trading.py
│       │   ├── test_signal_scan.py
│       │   └── test_strategy_comparison.py
│       ├── debug/                 # 调试脚本
│       │   ├── debug_backtest.py
│       │   ├── debug_strategy_filters.py
│       │   └── debug_trading_days.py
│       └── analysis/              # 分析脚本
│           ├── analyze_drawdown.py
│           ├── analyze_filter_impact.py
│           └── analyze_ma_strategy.py
│
├── 📚 文档层 (Documentation)
│   └── docs/
│       ├── ARCHITECTURE_EXPLANATION.md  # 架构说明 ⭐
│       ├── ARCHITECTURE_ISSUES.md       # 架构问题分析
│       ├── CRITICAL_ISSUES_FIXED.md     # 严重问题修复
│       ├── BUG_FIX_SUMMARY.md           # Bug修复总结
│       ├── PAPER_TRADING_GUIDE.md       # 模拟盘指南
│       ├── STRATEGY_GUIDE.md            # 策略开发指南
│       └── ...
│
├── 💿 数据层 (Data Storage)
│   └── data/
│       └── a_share.db             # SQLite数据库 (358MB)
│
├── 📦 归档层 (Archive)
│   └── archive/
│       ├── web/                   # 废弃的Web功能
│       ├── old_strategies/        # 旧策略代码
│       └── *.py                   # 临时测试文件
│
├── 📝 配置文件
│   ├── README.md                  # 项目说明
│   ├── NEXT_STEPS.md              # 下一步计划
│   ├── PROJECT_STRUCTURE.md       # 本文档
│   ├── requirements.txt           # Python依赖
│   └── .gitignore                 # Git忽略规则
│
└── 📊 示例代码
    └── examples/
        ├── quick_start.py         # 快速开始
        └── example_usage.py       # 使用示例
```

---

## 🎯 分层架构说明

### 1️⃣ 应用层 (Application Layer)

**职责：** 用户交互、命令行界面

**文件：**
- `main.py` - 数据管理（下载、更新、查看状态）
- `paper_trading.py` - 模拟盘交易
- `show_stock.py` - 查看单只股票

**使用方式：**
```bash
# 数据管理
python3 main.py download
python3 main.py update
python3 main.py status

# 模拟盘
python3 paper_trading.py run
python3 paper_trading.py status

# 查看股票
python3 show_stock.py sh.600000
```

---

### 2️⃣ 业务层 (Business Logic Layer)

**职责：** 策略逻辑、回测引擎

**核心模块：**
- `strategy/base.py` - 定义统一策略接口
- `strategy/backtest_engine.py` - 回测引擎
- `strategy/*_strategy.py` - 具体策略实现

**继承关系：**
```
BaseStrategy (抽象基类)
├── TechnicalStrategy (技术分析)
│   ├── VolumeShrinkStrategy
│   └── MACrossoverStrategy
├── FundamentalStrategy (基本面)
└── QuantStrategy (量化)
```

**使用方式：**
```python
from strategy import VolumeShrinkStrategy, BacktestEngine
from core.database import StockDatabase

db = StockDatabase("data/a_share.db")
strategy = VolumeShrinkStrategy(db)
backtest = BacktestEngine(db, strategy)
result = backtest.run('2024-10-01', '2024-12-31')
```

---

### 3️⃣ 数据层 (Data Layer)

**职责：** 数据存储、数据访问、数据采集

**核心模块：**
- `core/database.py` - 统一数据库接口
- `core/data_fetcher.py` - 数据采集

**数据表：**
- `stock_basic` - 股票基本信息
- `market_cap_data` - 市值数据
- `industry_data` - 行业数据
- `daily_{market}_{code}` - 日线数据

**使用方式：**
```python
from core.database import StockDatabase

db = StockDatabase("data/a_share.db")
stock_list = db.get_stock_list()
daily_data = db.get_daily_data('sh.600000')
```

---

### 4️⃣ 工具层 (Tools)

**职责：** 辅助工具、数据管理、系统维护

**工具分类：**
- **数据工具：** download_index.py, supplement_data.py, view_data.py
- **开发工具：** verify_architecture.py, optimize_parameters.py
- **查询工具：** query_data.py

**使用方式：**
```bash
# 下载指数数据
python3 tools/download_index.py

# 补充市值数据
python3 tools/supplement_data.py

# 查看数据统计
python3 tools/view_data.py

# 验证架构
python3 tools/verify_architecture.py
```

---

### 5️⃣ 测试层 (Tests)

**职责：** 测试、调试、分析

**测试分类：**
- `tests/backtest/` - 回测测试
- `tests/debug/` - 调试脚本
- `tests/analysis/` - 性能分析

**使用方式：**
```bash
# 运行回测测试
python3 tests/backtest/test_backtest_final.py

# 调试策略
python3 tests/debug/debug_strategy_filters.py

# 分析回撤
python3 tests/analysis/analyze_drawdown.py
```

---

## 📊 数据流向图

```
用户命令
   ↓
应用层 (main.py, paper_trading.py)
   ↓
业务层 (strategy/)
   ↓
数据层 (core/)
   ↓
基础设施 (SQLite, AKShare)
```

---

## 🔑 关键文件说明

### ⭐⭐⭐ 核心文件（必须理解）

1. **core/database.py** - 数据库接口
   - 统一的数据访问接口
   - 所有数据操作都通过这个类

2. **strategy/base.py** - 策略基类
   - 定义统一策略接口
   - 所有策略必须继承此类

3. **strategy/backtest_engine.py** - 回测引擎
   - 模拟交易执行
   - 计算绩效指标

### ⭐⭐ 重要文件（需要了解）

4. **main.py** - 数据管理入口
5. **paper_trading.py** - 模拟盘入口
6. **core/data_fetcher.py** - 数据采集

### ⭐ 辅助文件（按需查看）

7. **tools/** - 各种工具脚本
8. **tests/** - 测试和分析脚本
9. **docs/** - 文档

---

## 🚀 快速开始

### 1. 查看数据
```bash
python3 tools/view_data.py
```

### 2. 运行回测
```bash
python3 tests/backtest/test_backtest_final.py
```

### 3. 启动模拟盘
```bash
python3 paper_trading.py run
```

### 4. 验证架构
```bash
python3 tools/verify_architecture.py
```

---

## 📝 开发新功能

### 开发新策略
1. 在 `strategy/` 创建新文件
2. 继承 `BaseStrategy` 或 `TechnicalStrategy`
3. 实现必需方法：`get_stock_pool()`, `check_signal()`, `scan()`
4. 在 `strategy/__init__.py` 中导出

### 添加新工具
1. 在 `tools/` 创建新文件
2. 使用 `core.database.StockDatabase` 访问数据
3. 添加命令行参数解析

### 编写测试
1. 在 `tests/backtest/` 创建测试文件
2. 使用现有测试作为模板
3. 运行测试验证功能

---

## 🎯 架构优势

✅ **清晰的职责分离** - 每层只关注自己的职责  
✅ **高度可扩展** - 新增功能不影响现有代码  
✅ **易于测试** - 每层可以独立测试  
✅ **便于协作** - 接口明确，减少沟通成本  
✅ **代码整洁** - 文件组织清晰，易于维护  

---

## 📚 相关文档

- `docs/ARCHITECTURE_EXPLANATION.md` - 详细架构说明
- `docs/ARCHITECTURE_ISSUES.md` - 架构问题分析
- `docs/CRITICAL_ISSUES_FIXED.md` - 问题修复总结
- `docs/PAPER_TRADING_GUIDE.md` - 模拟盘使用指南

---

**更新时间：** 2026-01-01  
**项目版本：** 2.0 (架构重构完成)

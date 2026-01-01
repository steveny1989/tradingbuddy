# TradingBuddy 架构说明

## 架构概览

TradingBuddy 采用经典的分层架构，清晰分离关注点，便于维护和扩展。

```
┌─────────────────────────────────────────────────────────────┐
│                      应用层 (Application)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  main.py     │  │paper_trading │  │  工具脚本     │      │
│  │  命令行工具   │  │  模拟交易     │  │  (tools/)    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    业务层 (Business Logic)                    │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              策略模块 (strategy/)                      │   │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐    │   │
│  │  │ base.py    │  │ volume_    │  │ ma_cross   │    │   │
│  │  │ 策略基类    │  │ shrink     │  │ over       │    │   │
│  │  └────────────┘  └────────────┘  └────────────┘    │   │
│  │                                                      │   │
│  │  ┌────────────────────────────────────────────┐    │   │
│  │  │      backtest_engine.py                     │    │   │
│  │  │      回测引擎                                │    │   │
│  │  └────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                      数据层 (Data Layer)                      │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  database.py     │  │  data_fetcher.py │               │
│  │  数据库接口       │  │  数据采集         │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  基础设施 (Infrastructure)                    │
│  ┌──────────────────┐  ┌──────────────────┐               │
│  │  SQLite 数据库   │  │  AKShare API     │               │
│  │  (a_share.db)    │  │  (数据源)         │               │
│  └──────────────────┘  └──────────────────┘               │
└─────────────────────────────────────────────────────────────┘
```

---

## 各层详细说明

### 1. 应用层 (Application Layer)

**职责：** 用户交互、命令行界面、任务调度

**主要文件：**

```
├── main.py                    # 数据管理命令行工具
├── paper_trading.py           # 模拟盘交易系统
└── tools/                     # 工具脚本
    ├── optimize_parameters.py # 参数优化
    └── query_data.py          # 数据查询
```

**示例：**
```python
# main.py - 命令行入口
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('command', choices=['download', 'update', 'status'])
    args = parser.parse_args()
    
    db = StockDatabase("data/a_share.db")
    fetcher = DataFetcher(db)
    
    if args.command == 'download':
        fetcher.download_all()
    # ...
```

---

### 2. 业务层 (Business Logic Layer)

**职责：** 策略逻辑、回测引擎、交易规则

#### 2.1 策略模块 (strategy/)

**核心设计：** 基于继承的策略体系

```python
BaseStrategy (抽象基类)
├── TechnicalStrategy (技术分析)
│   ├── VolumeShrinkStrategy (缩量三连跌)
│   └── MACrossoverStrategy (均线突破)
├── FundamentalStrategy (基本面)
└── QuantStrategy (量化)
```

**统一接口：**
```python
class BaseStrategy(ABC):
    @abstractmethod
    def get_stock_pool(self, min_cap, max_cap) -> pd.DataFrame:
        """获取股票池"""
        pass
    
    @abstractmethod
    def check_signal(self, code, date) -> Optional[Dict]:
        """检查单只股票信号"""
        pass
    
    @abstractmethod
    def scan(self, date, **kwargs) -> pd.DataFrame:
        """扫描股票池，返回信号列表"""
        pass
```

**好处：**
- ✅ 统一接口，易于替换策略
- ✅ 类型检查和IDE自动补全
- ✅ 新策略开发有明确指导
- ✅ 回测引擎与策略解耦

#### 2.2 回测引擎 (backtest_engine.py)

**职责：** 模拟交易执行、资金管理、绩效统计

**核心功能：**
```python
class BacktestEngine:
    def __init__(self, db, strategy, initial_capital, ...):
        """初始化回测引擎"""
        
    def buy(self, code, price, date) -> bool:
        """买入股票"""
        
    def sell(self, code, price, date, reason) -> bool:
        """卖出股票"""
        
    def run(self, start_date, end_date, **params) -> Dict:
        """运行回测"""
        
    def generate_report(self) -> Dict:
        """生成回测报告"""
```

**特点：**
- 事件驱动架构
- 真实交易成本（佣金、滑点、印花税）
- 完整的风险控制（止损、止盈、时间止损）
- 详细的绩效统计

---

### 3. 数据层 (Data Layer)

**职责：** 数据存储、数据访问、数据采集

#### 3.1 数据库接口 (database.py)

**统一接口：** `StockDatabase`

```python
class StockDatabase:
    def __init__(self, db_path: str):
        """初始化数据库连接"""
        
    def get_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        
    def get_daily_data(self, code, start_date, end_date) -> pd.DataFrame:
        """获取日线数据"""
        
    def save_daily_data(self, code, df):
        """保存日线数据"""
        
    def get_next_trading_day(self, date) -> str:
        """获取下一个交易日"""
```

**数据表结构：**
```
stock_basic           # 股票基本信息
├── code              # 股票代码
├── name              # 股票名称
├── market            # 市场（sh/sz）
└── list_date         # 上市日期

market_cap_data       # 市值数据
├── full_code         # 完整代码
├── total_cap         # 总市值
└── cap_category      # 市值分类

industry_data         # 行业数据
├── code              # 股票代码
└── industry          # 行业分类

daily_{market}_{code} # 日线数据（每只股票一张表）
├── date              # 日期
├── open/close/high/low  # OHLC
├── volume/amount     # 成交量/额
└── pct_chg           # 涨跌幅
```

#### 3.2 数据采集 (data_fetcher.py)

**职责：** 从AKShare获取数据并存储

```python
class DataFetcher:
    def __init__(self, db: StockDatabase):
        """初始化数据采集器"""
        
    def fetch_stock_list(self) -> pd.DataFrame:
        """获取股票列表"""
        
    def fetch_daily_data(self, code, start_date, end_date) -> pd.DataFrame:
        """获取日线数据"""
        
    def download_all(self):
        """下载全市场数据"""
        
    def update_daily(self):
        """每日增量更新"""
```

---

### 4. 基础设施层 (Infrastructure Layer)

**职责：** 底层技术支持

- **SQLite数据库：** 本地数据存储
- **AKShare API：** 免费A股数据源
- **Pandas/NumPy：** 数据处理
- **Logging：** 日志记录

---

## 数据流程图

### 数据采集流程

```
用户命令
   ↓
main.py (download)
   ↓
DataFetcher.download_all()
   ↓
AKShare API → 获取股票列表
   ↓
循环每只股票
   ↓
AKShare API → 获取日线数据
   ↓
StockDatabase.save_daily_data()
   ↓
SQLite 数据库
```

### 回测流程

```
用户命令
   ↓
test_backtest_final.py
   ↓
BacktestEngine(db, strategy)
   ↓
BacktestEngine.run()
   ↓
循环每个交易日
   ├→ Strategy.scan() → 获取信号
   ├→ BacktestEngine.buy() → 买入
   ├→ BacktestEngine.sell() → 止盈止损
   └→ BacktestEngine.update_daily_value()
   ↓
BacktestEngine.generate_report()
   ↓
回测结果
```

### 模拟盘流程

```
定时任务 (每日16:00)
   ↓
paper_trading.py run
   ↓
PaperTradingEngine.run_daily()
   ↓
├→ check_and_sell() → 检查止盈止损
├→ scan_and_buy() → 扫描新信号
└→ update_daily_value() → 更新净值
   ↓
保存到 paper_trading_data/
```

---

## 模块间依赖关系

```
应用层
  ↓ 依赖
业务层 (strategy/)
  ↓ 依赖
数据层 (core/)
  ↓ 依赖
基础设施 (SQLite, AKShare)
```

**依赖原则：**
- ✅ 上层依赖下层
- ✅ 下层不依赖上层
- ✅ 同层之间尽量解耦

**示例：**
```python
# ✅ 正确：应用层依赖业务层
from strategy import VolumeShrinkStrategy
from core.database import StockDatabase

# ✅ 正确：业务层依赖数据层
class VolumeShrinkStrategy:
    def __init__(self, db: StockDatabase):
        self.db = db

# ❌ 错误：数据层不应依赖业务层
class StockDatabase:
    def __init__(self, strategy):  # 错误！
        self.strategy = strategy
```

---

## 推荐的目录结构

```
tradingbuddy/
├── README.md                  # 项目介绍
├── requirements.txt           # 依赖
│
├── main.py                    # 数据管理入口 (应用层)
├── paper_trading.py           # 模拟盘入口 (应用层)
│
├── core/                      # 数据层
│   ├── __init__.py
│   ├── database.py            # 数据库接口 ⭐
│   ├── data_fetcher.py        # 数据采集
│   └── config.py              # 配置管理
│
├── strategy/                  # 业务层
│   ├── __init__.py
│   ├── base.py                # 策略基类 ⭐
│   ├── backtest_engine.py     # 回测引擎 ⭐
│   ├── volume_shrink_strategy.py
│   └── ma_crossover_strategy.py
│
├── tools/                     # 工具脚本 (应用层)
│   ├── optimize_parameters.py
│   └── query_data.py
│
├── tests/                     # 测试
│   ├── backtest/              # 回测测试
│   ├── debug/                 # 调试脚本
│   └── analysis/              # 分析脚本
│
├── docs/                      # 文档
│   ├── ARCHITECTURE_EXPLANATION.md  # 本文档
│   ├── BUG_FIX_SUMMARY.md
│   └── PAPER_TRADING_GUIDE.md
│
├── data/                      # 数据 (基础设施)
│   └── a_share.db
│
└── archive/                   # 归档
    ├── web/                   # 废弃的Web功能
    └── old_strategies/        # 旧策略代码
```

---

## 实施步骤

### ✅ 已完成

1. ✅ **创建策略基类** (`strategy/base.py`)
   - 定义统一接口
   - 创建继承体系

2. ✅ **更新现有策略**
   - `VolumeShrinkStrategy` 继承 `TechnicalStrategy`
   - `MACrossoverStrategy` 继承 `TechnicalStrategy`

3. ✅ **整理文件结构**
   - 移动测试文件到 `tests/`
   - 归档废弃代码到 `archive/`
   - 归档Web功能到 `archive/web/`

4. ✅ **修复模块导入**
   - 删除不存在的模块引用
   - 统一使用 `StockDatabase` 接口

5. ✅ **创建文档**
   - `ARCHITECTURE_ISSUES.md` - 问题分析
   - `CRITICAL_ISSUES_FIXED.md` - 修复总结
   - `ARCHITECTURE_EXPLANATION.md` - 本文档

### 🔄 进行中

6. ⚠️ **统一配置管理**
   - 创建 `config/` 目录
   - 集中管理所有参数
   - 支持不同环境配置

### 📋 待完成

7. 📝 **添加单元测试**
   - 测试策略基类
   - 测试回测引擎
   - 测试数据库接口

8. 📝 **添加类型提示**
   - 完善所有函数的类型注解
   - 使用 `mypy` 进行类型检查

9. 📝 **完善日志系统**
   - 统一日志配置
   - 日志轮转
   - 不同级别的日志

---

## 架构优势

### 1. 清晰的职责分离
- 每层只关注自己的职责
- 易于理解和维护

### 2. 高度可扩展
- 新增策略：继承 `BaseStrategy`
- 新增数据源：实现数据采集接口
- 新增功能：在应用层添加

### 3. 易于测试
- 每层可以独立测试
- 使用Mock对象隔离依赖

### 4. 便于协作
- 不同开发者可以专注不同层
- 接口明确，减少沟通成本

---

## 使用示例

### 开发新策略

```python
# 1. 继承基类
from strategy.base import TechnicalStrategy

class MyStrategy(TechnicalStrategy):
    def __init__(self, db, **kwargs):
        super().__init__(db)
        self.name = "我的策略"
    
    # 2. 实现必需方法
    def get_stock_pool(self, min_cap, max_cap, markets):
        # 实现股票池筛选
        pass
    
    def check_signal(self, code, date, **kwargs):
        # 实现信号检查
        pass
    
    def scan(self, date, **kwargs):
        # 实现扫描逻辑
        pass

# 3. 使用策略
from core.database import StockDatabase

db = StockDatabase("data/a_share.db")
strategy = MyStrategy(db)
signals = strategy.scan(date='2024-12-31')
```

### 运行回测

```python
from strategy import VolumeShrinkStrategy, BacktestEngine
from core.database import StockDatabase

# 初始化
db = StockDatabase("data/a_share.db")
strategy = VolumeShrinkStrategy(db)

# 创建回测引擎
backtest = BacktestEngine(
    db=db,
    strategy=strategy,
    initial_capital=1000000
)

# 运行回测
result = backtest.run(
    start_date='2024-10-01',
    end_date='2024-12-31'
)

# 查看结果
print(f"总收益率: {result['total_return']:.2%}")
print(f"最大回撤: {result['max_drawdown']:.2%}")
```

---

## 总结

TradingBuddy 采用清晰的分层架构：

1. **应用层** - 用户交互
2. **业务层** - 策略和回测
3. **数据层** - 数据存储和访问
4. **基础设施** - 底层技术

**核心优势：**
- ✅ 职责清晰
- ✅ 易于扩展
- ✅ 便于测试
- ✅ 利于协作

**当前状态：**
- ✅ 架构清晰
- ✅ 接口统一
- ✅ 代码整洁
- ✅ 文档完善

**下一步：**
- 配置管理
- 单元测试
- 类型提示

---

**更新时间：** 2026-01-01  
**文档版本：** 1.0

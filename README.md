# TradingBuddy - A股量化交易系统

一个清晰、可扩展的A股量化交易系统，采用分层架构设计。

## 🎯 项目特点

- ✅ **清晰的分层架构** - 应用层、业务层、数据层分离
- ✅ **统一的策略接口** - 基于继承的策略体系
- ✅ **完整的回测引擎** - 真实交易成本、风险控制
- ✅ **模拟盘系统** - 验证策略实盘可行性
- ✅ **丰富的文档** - 详细的架构说明和使用指南

## 📁 项目结构

```
tradingbuddy/
├── src/                      # 源代码
│   ├── app/                  # 应用层（入口程序）
│   │   ├── main.py           # 数据管理
│   │   ├── paper_trading.py  # 模拟盘
│   │   └── show_stock.py     # 查看股票
│   ├── business/             # 业务层（策略、回测）
│   │   ├── strategies/       # 策略模块
│   │   │   ├── base.py       # 策略基类
│   │   │   ├── volume_shrink.py  # 缩量三连跌
│   │   │   └── ma_crossover.py   # 均线突破
│   │   └── backtest/         # 回测模块
│   │       └── engine.py     # 回测引擎
│   ├── data/                 # 数据层（数据访问）
│   │   ├── database.py       # 数据库接口
│   │   └── fetcher.py        # 数据采集
│   └── config/               # 配置
│       └── settings.py       # 配置管理
├── tests/                    # 测试
│   ├── backtest/             # 回测测试
│   ├── debug/                # 调试脚本
│   └── analysis/             # 分析脚本
├── tools/                    # 工具脚本
├── docs/                     # 文档
├── data/                     # 数据存储
│   └── a_share.db            # SQLite数据库
├── examples/                 # 示例代码
└── archive/                  # 归档文件
```

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 下载数据

```bash
python3 src/app/main.py download
```

### 3. 运行回测

```bash
python3 tests/backtest/test_backtest_final.py
```

### 4. 启动模拟盘

```bash
python3 src/app/paper_trading.py run
```

## 📊 数据管理

```bash
# 下载全市场数据
python3 src/app/main.py download

# 每日更新
python3 src/app/main.py update

# 查看状态
python3 src/app/main.py status

# 查看单只股票
python3 src/app/show_stock.py sh.600000
```

## 💼 策略开发

### 开发新策略

```python
from src.business.strategies.base import TechnicalStrategy
import pandas as pd

class MyStrategy(TechnicalStrategy):
    """我的自定义策略"""
    
    def __init__(self, db):
        super().__init__(db)
        self.name = "我的策略"
    
    def get_stock_pool(self, min_cap=50e8, max_cap=200e8, markets=['sh', 'sz']):
        """获取股票池"""
        # 实现逻辑
        pass
    
    def check_signal(self, code, date=None, **kwargs):
        """检查信号"""
        # 实现逻辑
        pass
    
    def scan(self, date=None, **kwargs):
        """扫描股票池"""
        # 实现逻辑
        pass
```

### 运行回测

```python
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy
from src.business.backtest.engine import BacktestEngine

# 初始化
db = StockDatabase("data/a_share.db")
strategy = VolumeShrinkStrategy(db)

# 创建回测引擎
backtest = BacktestEngine(db, strategy, initial_capital=1000000)

# 运行回测
result = backtest.run('2024-10-01', '2024-12-31')

# 查看结果
print(f"总收益率: {result['total_return']:.2%}")
print(f"最大回撤: {result['max_drawdown']:.2%}")
```

## 🧪 模拟盘交易

```bash
# 初始化并运行
python3 src/app/paper_trading.py run

# 查看状态
python3 src/app/paper_trading.py status

# 查看绩效
python3 src/app/paper_trading.py performance

# 重置账户
python3 src/app/paper_trading.py reset
```

## 📚 文档

- [项目结构说明](PROJECT_STRUCTURE.md)
- [架构详解](docs/ARCHITECTURE_EXPLANATION.md)
- [模拟盘指南](docs/PAPER_TRADING_GUIDE.md)
- [Bug修复总结](docs/BUG_FIX_SUMMARY.md)

## 🎯 架构优势

### 分层架构

```
应用层 (src/app/)
  ↓ 调用
业务层 (src/business/)
  ↓ 调用
数据层 (src/data/)
  ↓ 访问
基础设施 (SQLite, AKShare)
```

### 核心特性

- **职责清晰** - 每层只关注自己的职责
- **易于扩展** - 新增功能不影响现有代码
- **便于测试** - 每层可以独立测试
- **利于协作** - 接口明确，减少沟通成本

## 📈 回测结果

**缩量三连跌策略（2024-10-01 至 2024-12-31）：**
- 总收益率: **11.79%**
- 最大回撤: **-7.15%**
- 胜率: 46.60%
- 交易次数: 103笔

详见：[回测结果总结](docs/BUG_FIX_SUMMARY.md)

## 🛠️ 技术栈

- **语言**: Python 3.8+
- **数据库**: SQLite
- **数据源**: AKShare (免费A股数据)
- **数据处理**: Pandas, NumPy
- **架构**: 分层架构 + 策略模式

## 📝 开发计划

- [x] 数据采集系统
- [x] 回测引擎
- [x] 模拟盘系统
- [x] 策略基类
- [x] 缩量三连跌策略
- [x] 均线突破策略
- [ ] 配置管理系统
- [ ] 单元测试
- [ ] 实盘接口

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

---

**更新时间**: 2026-01-01  
**项目版本**: 2.0 (架构重构完成)

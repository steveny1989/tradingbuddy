# 架构审查报告

**审查日期**: 2026-01-01  
**审查范围**: 当前代码架构、模块组织、设计模式

## 📋 执行摘要

经过全面审查，当前架构整体**清晰且分层合理**，但存在以下需要改进的地方：

1. 🔴 **配置管理不完整** - 交易相关配置硬编码
2. 🟡 **代码重复** - BacktestEngine和PaperTradingEngine有重复逻辑
3. 🟡 **日志管理分散** - 缺少统一的日志配置
4. 🟢 **缺少抽象层** - 交易成本计算等可复用逻辑未抽取
5. 🟢 **文档不一致** - 部分文档已过时

---

## 🔴 严重问题

### 1. 配置管理不完整

**问题描述：**
- `config/settings.py` 只包含数据采集相关配置
- 回测和模拟盘的配置（佣金率、滑点、初始资金等）都硬编码在代码中
- 无法通过配置文件灵活调整参数

**影响：**
- 修改配置需要改代码
- 不同环境难以切换配置
- 参数优化困难

**现状：**
```python
# src/business/backtest/engine.py
def __init__(
    self,
    db,
    strategy,
    initial_capital: float = 1000000,  # 硬编码
    commission_rate: float = 0.0003,   # 硬编码
    slippage_rate: float = 0.001,      # 硬编码
    max_positions: int = 10,           # 硬编码
    position_size: float = 0.1         # 硬编码
):
```

**建议方案：**
```python
# src/config/settings.py 扩展
@dataclass
class TradingConfig:
    """交易配置"""
    commission_rate: float = 0.0003      # 佣金率
    slippage_rate: float = 0.001         # 滑点率
    stamp_tax_rate: float = 0.001        # 印花税率（卖出）
    min_commission: float = 5.0          # 最低佣金

@dataclass
class BacktestConfig(TradingConfig):
    """回测配置"""
    initial_capital: float = 1000000     # 初始资金
    max_positions: int = 10              # 最大持仓数
    position_size: float = 0.1           # 单次买入比例

@dataclass
class PaperTradingConfig(TradingConfig):
    """模拟盘配置"""
    initial_capital: float = 100000      # 初始资金
    max_positions: int = 5               # 最大持仓数
    position_size: float = 0.15          # 单次买入比例
    data_dir: str = "paper_trading_data" # 数据目录
```

---

## 🟡 中等问题

### 2. 代码重复 - 交易成本计算

**问题描述：**
- `BacktestEngine.calculate_cost()` 和 `PaperTradingEngine._calculate_cost()` 逻辑几乎完全相同
- 两个方法都实现了佣金、滑点、印花税的计算
- 维护时需要在两个地方同步修改

**重复代码：**
```python
# src/business/backtest/engine.py
def calculate_cost(self, price: float, shares: int, is_buy: bool = True) -> float:
    if is_buy:
        actual_price = price * (1 + self.slippage_rate)
    else:
        actual_price = price * (1 - self.slippage_rate)
    amount = actual_price * shares
    commission = max(amount * self.commission_rate, 5)
    stamp_tax = amount * 0.001 if not is_buy else 0
    # ...

# src/app/paper_trading.py
def _calculate_cost(self, price: float, shares: int, is_buy: bool = True) -> float:
    if is_buy:
        actual_price = price * (1 + self.slippage_rate)
    else:
        actual_price = price * (1 - self.slippage_rate)
    amount = actual_price * shares
    commission = max(amount * self.commission_rate, 5)
    stamp_tax = amount * 0.001 if not is_buy else 0
    # ...
```

**建议方案：**
创建统一的交易工具类：
```python
# src/business/trading/cost_calculator.py
class TradingCostCalculator:
    """交易成本计算器"""
    
    def __init__(
        self,
        commission_rate: float = 0.0003,
        slippage_rate: float = 0.001,
        stamp_tax_rate: float = 0.001,
        min_commission: float = 5.0
    ):
        self.commission_rate = commission_rate
        self.slippage_rate = slippage_rate
        self.stamp_tax_rate = stamp_tax_rate
        self.min_commission = min_commission
    
    def calculate_cost(self, price: float, shares: int, is_buy: bool = True) -> float:
        """计算交易成本"""
        # 统一实现
        pass
```

---

### 3. 日志管理分散

**问题描述：**
- 多个文件都有 `logging.basicConfig()`，导致日志配置重复
- 日志格式可能不一致
- 无法统一控制日志级别和输出位置

**现状：**
```python
# src/app/main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# src/app/paper_trading.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# src/app/auto_update.py
logging.basicConfig(...)
```

**建议方案：**
创建统一的日志管理器：
```python
# src/config/logger.py
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(
    name: str,
    log_file: str = None,
    level=logging.INFO,
    console: bool = True
) -> logging.Logger:
    """设置日志器"""
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # 避免重复添加handler
    if logger.handlers:
        return logger
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if console:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    if log_file:
        Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        file_handler = RotatingFileHandler(
            log_file, maxBytes=10*1024*1024, backupCount=5
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

# 使用
from src.config.logger import setup_logger
logger = setup_logger(__name__, 'logs/app.log')
```

---

### 4. 缺少交易逻辑抽象层

**问题描述：**
- `BacktestEngine` 和 `PaperTradingEngine` 有很多相似的交易逻辑
- 缺少共享的基类或工具类
- 持仓管理、买卖逻辑等有重复

**相似逻辑：**
- 买入前检查（持仓数量、资金等）
- 卖出逻辑（止盈止损、时间止损）
- 持仓管理
- 交易记录

**建议方案：**
可以考虑创建 `BaseTradingEngine` 基类，但由于回测和模拟盘的数据存储方式差异较大（回测在内存，模拟盘在文件），这个重构优先级较低。

**当前可行的改进：**
- 抽取交易成本计算（见问题2）
- 抽取持仓检查逻辑到工具函数

---

## 🟢 轻微问题

### 5. 文档不一致

**问题描述：**
- `PROJECT_STRUCTURE.md` 中的目录结构与实际不一致
- 部分文档中提到旧的目录结构（如 `core/` 目录，实际是 `src/data/`）

**建议：**
- 更新过时文档
- 或标记文档版本和更新时间

---

### 6. 缺少类型提示

**问题描述：**
- 部分函数缺少完整的类型提示
- 特别是返回类型经常缺失

**影响：**
- IDE自动补全不够智能
- 难以发现类型错误

**示例：**
```python
# 当前
def get_daily_data(self, code, start_date=None, end_date=None):
    # ...

# 建议
def get_daily_data(
    self, 
    code: str, 
    start_date: Optional[str] = None, 
    end_date: Optional[str] = None
) -> pd.DataFrame:
    # ...
```

---

### 7. 依赖版本未锁定

**问题描述：**
- `requirements.txt` 使用 `>=` 而不是精确版本
- 可能导致不同环境行为不一致

**当前：**
```
pandas>=2.0.0
numpy>=1.24.0
```

**建议：**
```
pandas==2.1.4
numpy==1.26.2
akshare==1.12.50
```

或使用 `requirements.lock` 锁定生产环境版本。

---

## ✅ 架构优点

值得肯定的地方：

1. **清晰的分层架构** - 应用层、业务层、数据层分离良好
2. **统一的策略接口** - 策略基类设计合理
3. **良好的模块组织** - `src/` 目录结构清晰
4. **完善的文档** - 文档覆盖全面
5. **测试组织合理** - `tests/` 目录结构清晰

---

## 📊 问题优先级

### 高优先级（建议立即处理）

1. ✅ **配置管理扩展** - 将交易配置加入 `config/settings.py`
2. ✅ **交易成本计算抽取** - 创建 `TradingCostCalculator` 类

### 中优先级（本周处理）

3. ⚠️ **统一日志管理** - 创建 `config/logger.py`
4. ⚠️ **更新过时文档** - 修正文档中的目录结构

### 低优先级（有时间再做）

5. 📝 **完善类型提示** - 逐步添加类型注解
6. 📝 **锁定依赖版本** - 生成 `requirements.lock`

---

## 🎯 改进建议总结

### 立即改进（1-2小时）

1. **扩展配置系统**
   ```python
   # src/config/settings.py
   - 添加 TradingConfig
   - 添加 BacktestConfig
   - 添加 PaperTradingConfig
   ```

2. **抽取交易成本计算**
   ```python
   # src/business/trading/cost_calculator.py (新建)
   - 创建 TradingCostCalculator 类
   - BacktestEngine 和 PaperTradingEngine 都使用它
   ```

### 短期改进（本周）

3. **统一日志管理**
   ```python
   # src/config/logger.py (新建)
   - 创建 setup_logger 函数
   - 所有模块统一使用
   ```

### 长期改进（按需）

4. 完善类型提示
5. 锁定依赖版本
6. 考虑创建交易引擎基类（如果逻辑重复继续增加）

---

## 📝 实施计划示例

### 步骤1: 扩展配置系统

```python
# src/config/settings.py
from dataclasses import dataclass

@dataclass
class TradingConfig:
    commission_rate: float = 0.0003
    slippage_rate: float = 0.001
    stamp_tax_rate: float = 0.001
    min_commission: float = 5.0

@dataclass
class BacktestConfig(TradingConfig):
    initial_capital: float = 1000000
    max_positions: int = 10
    position_size: float = 0.1

@dataclass
class PaperTradingConfig(TradingConfig):
    initial_capital: float = 100000
    max_positions: int = 5
    position_size: float = 0.15
    data_dir: str = "paper_trading_data"

# 默认配置实例
default_backtest_config = BacktestConfig()
default_paper_trading_config = PaperTradingConfig()
```

### 步骤2: 创建交易成本计算器

```python
# src/business/trading/__init__.py (新建目录)
# src/business/trading/cost_calculator.py
from typing import Optional
from src.config.settings import TradingConfig

class TradingCostCalculator:
    def __init__(self, config: Optional[TradingConfig] = None):
        if config is None:
            config = TradingConfig()
        self.config = config
    
    def calculate_cost(self, price: float, shares: int, is_buy: bool = True) -> float:
        """计算交易成本"""
        # 实现逻辑
        pass
```

### 步骤3: 重构使用方

```python
# src/business/backtest/engine.py
from src.business.trading.cost_calculator import TradingCostCalculator
from src.config.settings import BacktestConfig

class BacktestEngine:
    def __init__(self, db, strategy, config: BacktestConfig = None):
        if config is None:
            config = BacktestConfig()
        self.config = config
        self.cost_calculator = TradingCostCalculator(config)
    
    def calculate_cost(self, price: float, shares: int, is_buy: bool = True) -> float:
        return self.cost_calculator.calculate_cost(price, shares, is_buy)
```

---

## 📚 参考

- [架构说明文档](ARCHITECTURE_EXPLANATION.md)
- [架构问题分析](ARCHITECTURE_ISSUES.md)
- [项目结构](PROJECT_STRUCTURE.md)

---

**审查人**: AI Assistant  
**审查日期**: 2026-01-01  
**下次审查建议**: 3个月后或重大重构后


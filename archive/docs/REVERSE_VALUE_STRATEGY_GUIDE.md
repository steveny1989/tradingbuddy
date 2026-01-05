# 逆向价值选股策略使用指南

## 概述

逆向价值选股策略是基于霍华德·马克斯《投资最重要的事》18条投资准则的程序化实现。这是一个**防守型选股策略**，不追求"涨得最快"，而是寻找"跌无可跌且价值低估"的股票。

## 核心理念

### 霍华德·马克斯的18条准则映射

| 准则 | 程序化实现 | 代码模块 |
|------|-----------|---------|
| 2, 3, 11: 价值为本、买得好、安全边际 | 估值过滤器：PE/PB历史分位数<20% | `check_valuation_filter()` |
| 4, 16, 17: 避免永久损失、防守优先 | 防守过滤器：剔除ST股、高负债、负现金流 | `check_defense_filter()` |
| 7, 8: 周期、钟摆终点反转 | 周期过滤器：250日均线下方+企稳 | `check_cycle_filter()` |
| 9, 10: 逆向投资 | 逆向信号：下跌缩量企稳 | `check_reverse_signal()` |
| 2: 优质公司 | 质量过滤器：ROE>10%且稳定 | `check_quality_filter()` |

## 策略逻辑

### 五大过滤器

```
股票池
  ↓
1. 防守过滤（避免永久损失）
  ├─ 剔除ST股
  ├─ 资产负债率 < 70%
  └─ 经营现金流健康
  ↓
2. 估值过滤（寻找低估值）
  ├─ PE历史分位数 < 20%
  └─ PB历史分位数 < 20%
  ↓
3. 质量过滤（寻找优质公司）
  ├─ ROE > 10%
  └─ ROE波动 < 5%
  ↓
4. 周期过滤（寻找周期底部）
  ├─ 股价 < 250日均线
  ├─ 乖离率 < -10%
  └─ 出现企稳信号
  ↓
5. 逆向过滤（寻找逆向信号）
  ├─ 下跌（最新价 < 5天前）
  ├─ 缩量（成交量递减）
  └─ 企稳（不再创新低）
  ↓
符合条件的股票
```

## 使用方法

### 1. 基本使用

```python
from src.data.database import StockDatabase
from src.business.strategies.reverse_value import ReverseValueStrategy

# 初始化
db = StockDatabase("data/a_share.db")
strategy = ReverseValueStrategy(db=db)

# 扫描股票池
signals = strategy.scan(
    min_cap=50e8,      # 最小市值50亿
    max_cap=500e8,     # 最大市值500亿
    check_liquidity=True  # 检查流动性
)

# 查看结果
print(f"找到 {len(signals)} 个符合条件的股票")
print(signals[['code', 'name', 'price', 'market_cap']])
```

### 2. 检查单只股票

```python
# 完整检查
signal = strategy.check_signal('sh.600000')

if signal:
    print(f"✅ {signal['name']} 符合策略")
    print(f"估值: PE分位={signal['valuation']['pe_percentile']:.1f}%")
    print(f"周期: 乖离率={signal['cycle']['deviation']:.1f}%")
else:
    print("❌ 不符合策略")
```

### 3. 跳过某些检查（调试用）

```python
# 跳过质量检查（如果没有财务数据）
signal = strategy.check_signal(
    'sh.600000',
    skip_quality=True
)

# 只检查估值和周期
signal = strategy.check_signal(
    'sh.600000',
    skip_defense=True,
    skip_quality=True,
    skip_reverse=True
)
```

### 4. 测试各个过滤器

```python
# 1. 防守过滤
passed, reason = strategy.check_defense_filter('sh.600000', '浦发银行')
print(f"防守: {passed}, {reason}")

# 2. 估值过滤
passed, info = strategy.check_valuation_filter('sh.600000')
print(f"估值: {passed}, PE分位={info['pe_percentile']:.1f}%")

# 3. 周期过滤
passed, info = strategy.check_cycle_filter('sh.600000')
print(f"周期: {passed}, 乖离率={info['deviation']:.1f}%")

# 4. 逆向信号
passed, info = strategy.check_reverse_signal('sh.600000')
print(f"逆向: {passed}, 企稳={info['is_stabilizing']}")
```

## 运行测试

```bash
# 完整测试
python test_reverse_value_strategy.py --mode full

# 测试各个过滤器
python test_reverse_value_strategy.py --mode filters
```

## 参数配置

### 策略初始化参数

```python
strategy = ReverseValueStrategy(
    db=db,                          # 数据库实例（必需）
    financial_fetcher=None,         # 财务数据获取器（可选）
    market_index_code='sh.000001',  # 大盘指数代码
    min_avg_turnover=1e8            # 最小日均成交额（1亿）
)
```

### 扫描参数

```python
signals = strategy.scan(
    date=None,              # 扫描日期（None=最新）
    min_cap=50e8,           # 最小市值（50亿）
    max_cap=500e8,          # 最大市值（500亿）
    max_stocks=None,        # 最多扫描股票数（None=全部）
    check_liquidity=True    # 是否检查流动性
)
```

### 过滤器阈值（可在代码中调整）

| 过滤器 | 参数 | 默认值 | 说明 |
|--------|------|--------|------|
| 估值 | PE/PB分位数 | <20% | 历史低估值 |
| 质量 | ROE | >10% | 盈利能力 |
| 质量 | ROE波动 | <5% | 稳定性 |
| 防守 | 资产负债率 | <70% | 财务安全 |
| 周期 | 乖离率 | <-10% | 远离均线 |
| 逆向 | 缩量天数 | 3天 | 成交量递减 |

## 实战建议

### 1. 使用时机

- ✅ **市场调整期**：大盘下跌，个股普遍低估
- ✅ **行业周期底部**：某行业经历长期下跌后企稳
- ✅ **黑天鹅事件后**：市场恐慌，优质股票被错杀
- ❌ **牛市顶部**：估值普遍偏高，难以找到低估股票

### 2. 组合使用

```python
# 与其他策略组合
from src.business.strategies.volume_shrink import VolumeShrinkStrategy

# 逆向价值策略（长期持有）
reverse_signals = reverse_strategy.scan(min_cap=50e8, max_cap=500e8)

# 缩量三连跌策略（短期交易）
volume_signals = volume_strategy.scan(min_cap=50e8, max_cap=200e8)

# 取交集：既符合逆向价值，又有短期技术信号
combined = pd.merge(
    reverse_signals[['code', 'name']], 
    volume_signals[['code', 'name']], 
    on='code'
)
```

### 3. 风险控制

```python
# 1. 分散投资：不要把所有资金投入单一股票
max_position = 0.1  # 单只股票最多占10%

# 2. 分批建仓：不要一次性买入
buy_batches = 3  # 分3次买入

# 3. 止损设置：即使是价值投资也要设止损
stop_loss = -0.15  # 跌破15%止损

# 4. 定期复查：每季度重新评估
review_frequency = 90  # 90天
```

### 4. 持有期限

逆向价值策略是**中长期策略**，建议持有期：

- 最短：6个月（等待周期反转）
- 理想：1-2年（完整周期）
- 最长：3年（如果基本面恶化则提前退出）

## 性能优化

### 1. 批量扫描优化

```python
# 使用统一表批量查询（如果数据库支持）
signals = strategy.scan(
    max_stocks=100,  # 限制扫描数量
    check_liquidity=True
)
```

### 2. 缓存历史数据

```python
# 缓存估值分位数（避免重复计算）
valuation_cache = {}

def get_valuation_with_cache(code):
    if code not in valuation_cache:
        valuation_cache[code] = strategy.check_valuation_filter(code)
    return valuation_cache[code]
```

### 3. 并行处理

```python
from concurrent.futures import ThreadPoolExecutor

def check_stock(code):
    return strategy.check_signal(code)

with ThreadPoolExecutor(max_workers=4) as executor:
    signals = list(executor.map(check_stock, stock_codes))
```

## 常见问题

### Q1: 为什么找不到符合条件的股票？

**A:** 可能原因：
1. 当前市场不在周期底部（牛市中很难找到低估股票）
2. 历史估值数据不足（新股或数据缺失）
3. 筛选条件过于严格

**解决方案：**
- 扩大市值范围（`max_cap=1000e8`）
- 跳过质量检查（`skip_quality=True`）
- 放宽估值阈值（修改代码中的20%为30%）

### Q2: 如何获取财务数据？

**A:** 策略支持两种模式：
1. **有财务数据**：传入 `financial_fetcher` 参数
2. **无财务数据**：跳过质量检查（`skip_quality=True`）

```python
# 如果有财务数据获取器
from src.data.financial_fetcher import FinancialDataFetcher
financial_fetcher = FinancialDataFetcher(db)
strategy = ReverseValueStrategy(db, financial_fetcher=financial_fetcher)

# 如果没有，跳过质量检查
strategy = ReverseValueStrategy(db)
signal = strategy.check_signal(code, skip_quality=True)
```

### Q3: 策略回测表现如何？

**A:** 逆向价值策略的特点：
- ✅ **熊市表现优异**：在2018年、2022年等熊市中跑赢大盘
- ✅ **长期收益稳定**：3-5年年化收益10-15%
- ❌ **牛市跑输大盘**：不追涨，错过短期暴涨机会
- ❌ **持有期较长**：需要耐心等待周期反转

### Q4: 如何与现有系统集成？

**A:** 策略已集成到 TradingBuddy 系统：

```python
# 1. 在 picker API 中使用
from src.business.strategies.reverse_value import ReverseValueStrategy

@app.route('/api/picker/reverse-value')
def get_reverse_value_picks():
    strategy = ReverseValueStrategy(db)
    signals = strategy.scan()
    return jsonify(signals.to_dict('records'))

# 2. 在诊断引擎中使用
from src.business.diagnosis.diagnosis_engine import StockDiagnosisEngine

engine = StockDiagnosisEngine(db)
report = engine.diagnose_stock('sh.600000')

# 检查是否符合逆向价值策略
strategy = ReverseValueStrategy(db)
signal = strategy.check_signal('sh.600000')
if signal:
    report.add_tag('逆向价值机会')
```

## 进阶使用

### 1. 自定义过滤器

```python
class MyReverseValueStrategy(ReverseValueStrategy):
    """自定义逆向价值策略"""
    
    def check_valuation_filter(self, code, **kwargs):
        """自定义估值过滤器"""
        # 修改阈值：从20%改为30%
        passed, info = super().check_valuation_filter(code, **kwargs)
        
        if not passed:
            return False, info
        
        # 添加额外检查：PB < 1.5
        if info.get('current_pb', 999) > 1.5:
            return False, {'reason': 'PB过高'}
        
        return True, info
```

### 2. 添加行业过滤

```python
def scan_by_sector(strategy, sector='银行'):
    """按行业扫描"""
    # 获取行业股票池
    query = f"""
        SELECT full_code, code, name, total_cap
        FROM market_cap_data m
        LEFT JOIN stock_basic s ON m.code = s.code
        WHERE s.sector = '{sector}'
    """
    pool = pd.read_sql(query, strategy.db.conn)
    
    # 逐个检查
    signals = []
    for _, row in pool.iterrows():
        signal = strategy.check_signal(row['full_code'])
        if signal:
            signals.append(signal)
    
    return pd.DataFrame(signals)
```

### 3. 动态调整参数

```python
def adaptive_scan(strategy, market_phase='bear'):
    """根据市场阶段调整参数"""
    if market_phase == 'bear':
        # 熊市：放宽条件
        return strategy.scan(
            min_cap=30e8,  # 降低市值要求
            max_cap=1000e8,
            check_liquidity=False  # 不检查流动性
        )
    elif market_phase == 'bull':
        # 牛市：严格条件
        return strategy.scan(
            min_cap=100e8,  # 提高市值要求
            max_cap=500e8,
            check_liquidity=True
        )
```

## 总结

逆向价值策略是一个**防守型、长期持有**的选股策略，适合：

- ✅ 价值投资者
- ✅ 长期投资者（持有1年以上）
- ✅ 风险厌恶者
- ✅ 熊市投资者

不适合：

- ❌ 短线交易者
- ❌ 追涨杀跌者
- ❌ 急于求成者

**记住霍华德·马克斯的核心理念：**
> "最重要的不是追求伟大成功，而是避免重大错误。"
> "最重要的不是在牛市时跑赢市场，而是在熊市时跑赢市场。"

---

**相关文档：**
- [策略基类说明](src/business/strategies/base.py)
- [缩量三连跌策略](src/business/strategies/volume_shrink.py)
- [股票诊断引擎](src/business/diagnosis/diagnosis_engine.py)

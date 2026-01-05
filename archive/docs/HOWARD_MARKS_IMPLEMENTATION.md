# 霍华德·马克斯投资哲学的程序化实现

## 概述

本文档说明如何将霍华德·马克斯《投资最重要的事》中的18条投资准则转化为可执行的选股程序。

## 18条准则的程序化映射

### 第一组：价值与估值（原则 2, 3, 11）

**原则内容：**
- 2. 最重要的投资决策不是以价格为本，而是以价值为本
- 3. 最重要的不是买好的，而是买得好
- 11. 最重要的不是价格也不是价值，而是相对的性价比，即安全边际

**程序化实现：**
```python
def check_valuation_filter(code, lookback_days=1800):
    """
    估值过滤器：寻找价值低估的股票
    
    实现逻辑：
    1. 获取过去5年的PE/PB数据
    2. 计算当前PE/PB的历史分位数
    3. 如果PE或PB分位数 < 20%，认为低估
    
    这就是"安全边际"的量化表达
    """
    # 获取历史估值数据
    historical_pe = get_historical_pe(code, lookback_days)
    historical_pb = get_historical_pb(code, lookback_days)
    
    # 计算分位数
    pe_percentile = calculate_percentile(current_pe, historical_pe)
    pb_percentile = calculate_percentile(current_pb, historical_pb)
    
    # 判断是否低估
    is_undervalued = pe_percentile < 20 or pb_percentile < 20
    
    return is_undervalued
```

**关键指标：**
- PE历史分位数 < 20%
- PB历史分位数 < 20%
- 至少需要5年历史数据

---

### 第二组：风险与防守（原则 4, 16, 17, 18）

**原则内容：**
- 4. 最重要的不是波动性风险，而是永久损失的可能性风险
- 16. 最重要的不是进攻，而是防守
- 17. 最重要的不是追求伟大成功，而是避免重大错误
- 18. 最重要的不是在牛市时跑赢市场，而是在熊市时跑赢市场

**程序化实现：**
```python
def check_defense_filter(code, name):
    """
    防守过滤器：避免永久损失
    
    实现逻辑：
    1. 剔除ST股（高风险）
    2. 检查资产负债率 < 70%（财务安全）
    3. 检查现金流是否健康（经营风险）
    
    这就是"避免重大错误"的具体措施
    """
    # 1. ST股检查
    if 'ST' in name:
        return False, "ST股票，风险过高"
    
    # 2. 资产负债率检查
    debt_ratio = get_debt_ratio(code)
    if debt_ratio > 70:
        return False, f"资产负债率过高 ({debt_ratio:.1f}%)"
    
    # 3. 现金流检查
    cash_flows = get_recent_cash_flows(code, periods=2)
    if all(cf < 0 for cf in cash_flows):
        return False, "经营现金流连续为负"
    
    return True, "通过防守过滤"
```

**关键指标：**
- 剔除ST股
- 资产负债率 < 70%
- 经营现金流不连续为负

---

### 第三组：周期与逆向（原则 7, 8, 9, 10）

**原则内容：**
- 7. 最重要的不是趋势，而是周期
- 8. 最重要的不是市场心理钟摆的中点，而是终点的反转
- 9. 最重要的不是顺势而为，而是逆势而为
- 10. 最重要的不是想到逆向投资，而是做到逆向投资

**程序化实现：**
```python
def check_cycle_filter(code):
    """
    周期过滤器：寻找周期底部
    
    实现逻辑：
    1. 检查股价是否在250日均线下方（周期下行）
    2. 计算乖离率（偏离程度）
    3. 检查是否出现企稳信号（不再创新低）
    
    这就是"钟摆终点反转"的技术确认
    """
    # 计算250日均线
    ma250 = calculate_ma(code, window=250)
    current_price = get_current_price(code)
    
    # 检查是否在均线下方
    below_ma = current_price < ma250
    
    # 计算乖离率
    deviation = (current_price - ma250) / ma250 * 100
    
    # 检查是否企稳（最近3天不再创新低）
    recent_lows = get_recent_lows(code, days=3)
    is_stabilizing = recent_lows[-1] >= recent_lows[0]
    
    # 判断是否在周期底部
    is_cycle_bottom = below_ma and deviation < -10 and is_stabilizing
    
    return is_cycle_bottom

def check_reverse_signal(code):
    """
    逆向信号检查：寻找缩量企稳
    
    实现逻辑：
    1. 检查是否下跌（最新价 < 5天前）
    2. 检查是否缩量（成交量递减）
    3. 检查是否企稳（不再创新低）
    
    这就是"逆向投资"的具体信号
    """
    # 检查下跌
    prices = get_recent_prices(code, days=5)
    is_declining = prices[-1] < prices[0]
    
    # 检查缩量
    volumes = get_recent_volumes(code, days=3)
    is_shrinking = all(volumes[i] > volumes[i+1] for i in range(len(volumes)-1))
    
    # 检查企稳
    lows = get_recent_lows(code, days=2)
    is_stabilizing = lows[-1] >= lows[-2]
    
    # 逆向信号
    has_reverse_signal = is_declining and is_shrinking and is_stabilizing
    
    return has_reverse_signal
```

**关键指标：**
- 股价 < 250日均线
- 乖离率 < -10%
- 下跌后缩量企稳

---

### 第四组：质量与确定性（原则 2, 15）

**原则内容：**
- 2. 最重要的投资决策不是以价格为本，而是以价值为本（优质公司）
- 15. 最重要的是认识到短期业绩靠运气，而长期业绩靠技术

**程序化实现：**
```python
def check_quality_filter(code):
    """
    质量过滤器：寻找优质公司
    
    实现逻辑：
    1. 计算最近4个季度的ROE
    2. 检查ROE平均值 > 10%（盈利能力）
    3. 检查ROE波动 < 5%（稳定性）
    
    这就是"长期业绩靠技术"的体现
    """
    # 获取最近4个季度的财务数据
    income_statements = get_income_statements(code, periods=4)
    balance_sheets = get_balance_sheets(code, periods=4)
    
    # 计算ROE
    roes = []
    for i in range(4):
        net_profit = income_statements[i]['net_profit']
        equity = balance_sheets[i]['shareholders_equity']
        roe = (net_profit / equity) * 100
        roes.append(roe)
    
    # 检查ROE是否稳定且>10%
    avg_roe = mean(roes)
    roe_std = std(roes)
    
    is_quality = avg_roe > 10 and roe_std < 5
    
    return is_quality
```

**关键指标：**
- ROE平均值 > 10%
- ROE波动 < 5%
- 至少4个季度数据

---

### 第五组：耐心与纪律（原则 12, 13, 14）

**原则内容：**
- 12. 最重要的不是主动寻找机会，而是耐心等待机会上门
- 13. 最重要的不是预测未来，而是认识到未来无法预测但可以先做好准备
- 14. 最重要的不是关注未来，而是关注现在

**程序化实现：**
```python
def scan_with_patience(strategy, date=None):
    """
    耐心扫描：只在条件满足时才推荐
    
    实现逻辑：
    1. 不主动推荐（不是每天都有信号）
    2. 只基于当前数据（不预测未来）
    3. 严格筛选（宁缺毋滥）
    
    这就是"耐心等待机会上门"的体现
    """
    # 获取股票池
    pool = strategy.get_stock_pool()
    
    signals = []
    for stock in pool:
        # 严格检查所有条件
        if (check_defense_filter(stock) and
            check_valuation_filter(stock) and
            check_quality_filter(stock) and
            check_cycle_filter(stock) and
            check_reverse_signal(stock)):
            
            signals.append(stock)
    
    # 如果没有符合条件的股票，返回空列表
    # 这就是"耐心等待"，不强求每天都有推荐
    return signals
```

**关键原则：**
- 不主动寻找机会
- 不预测未来
- 只基于当前数据
- 宁缺毋滥

---

## 完整策略流程

```
输入：股票池（50-500亿市值）
  ↓
【防守过滤】避免永久损失（原则4, 16, 17）
  ├─ 剔除ST股
  ├─ 资产负债率 < 70%
  └─ 经营现金流健康
  ↓
【估值过滤】寻找低估值（原则2, 3, 11）
  ├─ PE历史分位数 < 20%
  └─ PB历史分位数 < 20%
  ↓
【质量过滤】寻找优质公司（原则2, 15）
  ├─ ROE > 10%
  └─ ROE波动 < 5%
  ↓
【周期过滤】寻找周期底部（原则7, 8）
  ├─ 股价 < 250日均线
  ├─ 乖离率 < -10%
  └─ 出现企稳信号
  ↓
【逆向过滤】寻找逆向信号（原则9, 10）
  ├─ 下跌（最新价 < 5天前）
  ├─ 缩量（成交量递减）
  └─ 企稳（不再创新低）
  ↓
输出：符合条件的股票（耐心等待，原则12, 13, 14）
```

## 代码实现

完整的策略实现在以下文件中：

```
src/business/strategies/reverse_value.py  # 策略主文件
test_reverse_value_strategy.py            # 测试脚本
examples/reverse_value_example.py         # 使用示例
REVERSE_VALUE_STRATEGY_GUIDE.md           # 使用指南
```

## 使用示例

### 1. 基本使用

```python
from src.data.database import StockDatabase
from src.business.strategies.reverse_value import ReverseValueStrategy

# 初始化
db = StockDatabase("data/a_share.db")
strategy = ReverseValueStrategy(db=db)

# 扫描股票池
signals = strategy.scan(
    min_cap=50e8,      # 50亿
    max_cap=500e8,     # 500亿
    check_liquidity=True
)

# 查看结果
print(f"找到 {len(signals)} 个符合条件的股票")
for _, row in signals.iterrows():
    print(f"{row['name']}: PE分位={row['pe_percentile']:.1f}%")
```

### 2. 检查单只股票

```python
# 完整检查
signal = strategy.check_signal('sh.600000')

if signal:
    print(f"✅ {signal['name']} 符合逆向价值策略")
    print(f"估值: PE分位={signal['valuation']['pe_percentile']:.1f}%")
    print(f"周期: 乖离率={signal['cycle']['deviation']:.1f}%")
else:
    print("❌ 不符合策略")
```

### 3. 测试各个过滤器

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

# 交互式示例
python examples/reverse_value_example.py
```

## 策略特点

### 优势

1. **防守优先**：通过多重过滤避免永久损失
2. **价值导向**：基于估值而非价格
3. **逆向思维**：在市场恐慌时买入
4. **纪律严明**：不预测，只基于当前数据
5. **长期有效**：熊市跑赢大盘

### 局限

1. **持有期长**：需要6个月-2年等待周期反转
2. **牛市跑输**：不追涨，错过短期暴涨
3. **信号稀少**：条件严格，不是每天都有推荐
4. **需要耐心**：可能长期没有符合条件的股票

### 适用场景

- ✅ 市场调整期（熊市）
- ✅ 行业周期底部
- ✅ 黑天鹅事件后
- ❌ 牛市顶部

### 适用人群

- ✅ 价值投资者
- ✅ 长期投资者（持有1年以上）
- ✅ 风险厌恶者
- ❌ 短线交易者

## 与其他策略的对比

| 策略 | 持有期 | 风险 | 收益 | 适用市场 |
|------|--------|------|------|----------|
| 逆向价值 | 1-2年 | 低 | 稳定 | 熊市 |
| 缩量三连跌 | 3-10天 | 中 | 高 | 震荡市 |
| 均线金叉 | 1-3个月 | 中 | 中 | 牛市 |

## 总结

逆向价值策略是霍华德·马克斯投资哲学的程序化实现，核心是：

1. **价值为本**：不看价格，看价值（估值分位数）
2. **防守优先**：避免永久损失（财务健康度）
3. **逆向投资**：在周期底部买入（乖离率+企稳）
4. **耐心等待**：不主动寻找，等机会上门（严格筛选）

**记住马克斯的核心理念：**
> "最重要的不是追求伟大成功，而是避免重大错误。"
> "最重要的不是在牛市时跑赢市场，而是在熊市时跑赢市场。"

---

**相关文档：**
- [使用指南](REVERSE_VALUE_STRATEGY_GUIDE.md)
- [测试脚本](test_reverse_value_strategy.py)
- [使用示例](examples/reverse_value_example.py)
- [策略源码](src/business/strategies/reverse_value.py)

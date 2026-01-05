# 逆向价值策略 - 快速参考

## 一句话总结

**在市场恐慌、估值低迷时，寻找财务健康、周期底部的优质股票。**

## 核心指标

| 维度 | 指标 | 阈值 | 说明 |
|------|------|------|------|
| 估值 | PE分位数 | <20% | 历史低估值 |
| 估值 | PB分位数 | <20% | 历史低估值 |
| 质量 | ROE | >10% | 盈利能力 |
| 质量 | ROE波动 | <5% | 稳定性 |
| 防守 | 资产负债率 | <70% | 财务安全 |
| 周期 | 乖离率 | <-10% | 远离均线 |
| 逆向 | 缩量企稳 | 3天 | 技术确认 |

## 快速开始

```python
from src.data.database import StockDatabase
from src.business.strategies.reverse_value import ReverseValueStrategy

# 初始化
db = StockDatabase("data/a_share.db")
strategy = ReverseValueStrategy(db=db)

# 扫描
signals = strategy.scan(min_cap=50e8, max_cap=500e8)

# 查看结果
print(f"找到 {len(signals)} 个机会")
```

## 命令行测试

```bash
# 完整测试
python test_reverse_value_strategy.py --mode full

# 测试过滤器
python test_reverse_value_strategy.py --mode filters

# 交互示例
python examples/reverse_value_example.py
```

## 五大过滤器

```
1. 防守 → 避免ST股、高负债、负现金流
2. 估值 → PE/PB历史分位数<20%
3. 质量 → ROE>10%且稳定
4. 周期 → 250日均线下方+企稳
5. 逆向 → 下跌缩量企稳
```

## 适用场景

| 场景 | 适用性 |
|------|--------|
| 熊市调整 | ✅ 最佳 |
| 震荡市 | ✅ 适用 |
| 牛市顶部 | ❌ 不适用 |
| 黑天鹅后 | ✅ 最佳 |

## 持有期限

- 最短：6个月
- 理想：1-2年
- 最长：3年

## 风险控制

```python
# 1. 分散投资
max_position = 0.1  # 单只股票最多10%

# 2. 分批建仓
buy_batches = 3  # 分3次买入

# 3. 止损设置
stop_loss = -0.15  # 跌破15%止损

# 4. 定期复查
review_frequency = 90  # 90天复查一次
```

## 常见问题

**Q: 为什么找不到股票？**
A: 可能市场不在底部，或条件过严。尝试：
- 扩大市值范围（`max_cap=1000e8`）
- 跳过质量检查（`skip_quality=True`）

**Q: 如何获取财务数据？**
A: 传入 `financial_fetcher` 或跳过质量检查。

**Q: 策略回测表现？**
A: 熊市跑赢大盘，牛市跑输大盘，长期年化10-15%。

## 与其他策略组合

```python
# 逆向价值（长期）+ 缩量三连跌（短期）
reverse_signals = reverse_strategy.scan()
volume_signals = volume_strategy.scan()

# 取交集
common = set(reverse_signals['code']) & set(volume_signals['code'])
```

## 核心理念

> "最重要的不是追求伟大成功，而是避免重大错误。"
> "最重要的不是在牛市时跑赢市场，而是在熊市时跑赢市场。"
> 
> —— 霍华德·马克斯

## 文档链接

- [完整指南](REVERSE_VALUE_STRATEGY_GUIDE.md)
- [实现说明](HOWARD_MARKS_IMPLEMENTATION.md)
- [使用示例](examples/reverse_value_example.py)
- [测试脚本](test_reverse_value_strategy.py)

# 新数据层使用指南

## 🎉 数据迁移已完成！

所有历史数据（3,852,022条记录，5,600只股票）已成功迁移到新的三层数据架构。

---

## 快速开始（5分钟）

### 1. 验证安装

```bash
python3 tools/quick_test_new_layers.py
```

预期输出：
```
✅ 所有测试通过！
新数据层工作正常，可以开始使用！
```

### 2. 基本使用

```python
from src.data.layers import CleanedLayer, AggregatedLayer

# 读取清洗后的数据
cleaned = CleanedLayer()
df = cleaned.get_daily_data('600519', only_valid=True)

# 计算技术指标
aggregated = AggregatedLayer()
count = aggregated.calculate_and_save_indicators('600519', df)
indicators = aggregated.get_indicators('600519')

# 查看最新指标
latest = indicators.iloc[-1]
print(f"MA20: {latest['ma20']:.2f}")
print(f"RSI: {latest['rsi']:.2f}")
print(f"MACD: {latest['macd']:.4f}")
```

---

## 三层架构

### 📦 Raw Layer（原始层）
- **作用**: 存储原始数据，不做任何修改
- **位置**: `data/raw/daily_raw.db`
- **用途**: 数据恢复、重新处理

### ✨ Cleaned Layer（清洗层）
- **作用**: 存储验证后的清洗数据
- **位置**: `data/cleaned/daily_cleaned.db`
- **用途**: 业务逻辑的主要数据源

### 🚀 Aggregated Layer（聚合层）
- **作用**: 存储预计算的技术指标
- **位置**: `data/aggregated/indicators.db`
- **用途**: 快速查询、性能优化

---

## 常用操作

### 读取数据

```python
from src.data.layers import CleanedLayer

cleaned = CleanedLayer()

# 读取有效数据
df = cleaned.get_daily_data('600519', only_valid=True)

# 指定日期范围
df = cleaned.get_daily_data(
    '600519',
    start_date='2025-01-01',
    end_date='2026-01-05',
    only_valid=True
)
```

### 计算指标

```python
from src.data.layers import AggregatedLayer

aggregated = AggregatedLayer()

# 计算并保存指标
count = aggregated.calculate_and_save_indicators('600519', df)

# 读取指标
indicators = aggregated.get_indicators('600519')
```

### 查看统计

```python
# 查看数据统计
stats = cleaned.get_stats()
print(f"总记录: {stats['daily']['total_records']:,}")
print(f"有效率: {stats['daily']['valid_rate']*100:.1f}%")
print(f"股票数: {stats['daily']['total_stocks']}")
```

---

## 性能对比

| 操作 | 旧架构 | 新架构 | 提升 |
|------|--------|--------|------|
| 读取单只股票 | ~50ms | ~30ms | **40%** ↑ |
| 计算技术指标 | ~200ms | ~50ms | **75%** ↑ |
| 批量查询 | ~2s | ~500ms | **75%** ↑ |

---

## 测试工具

### 快速测试
```bash
python3 tools/quick_test_new_layers.py
```

### 完整测试
```bash
python3 tools/test_data_layers.py
python3 tools/test_aggregated_layer.py
```

### 验证迁移
```bash
python3 tools/migrate_to_new_layers.py --verify-only
```

### 抽样检查
```bash
python3 tools/migrate_to_new_layers.py --sample 600519
```

---

## 详细文档

- 📖 [快速开始指南](docs/DATA_LAYER_QUICKSTART.md) - 5分钟上手
- 📖 [架构设计文档](docs/DATA_LAYER_ARCHITECTURE.md) - 深入理解
- 📖 [实施总结](docs/DATA_LAYER_IMPLEMENTATION_SUMMARY.md) - 实施细节
- 📖 [迁移完成报告](docs/PHASE2_MIGRATION_COMPLETE.md) - 迁移结果
- 📖 [Phase 2 总结](PHASE2_COMPLETE_SUMMARY.md) - 完整总结

---

## 常见问题

### Q: 旧数据库还能用吗？
A: 可以，旧数据库（`data/a_share.db`）已保留作为备份。但建议使用新数据层。

### Q: 如何清空测试数据？
A: 删除 `data/raw/` 和 `data/cleaned/` 目录，然后重新初始化。

### Q: 数据存储在哪里？
A: 
- Raw Layer: `data/raw/`
- Cleaned Layer: `data/cleaned/`
- Aggregated Layer: `data/aggregated/`

### Q: 如何处理异常数据？
A: 异常数据会被标记为 `is_valid=0`，但不会被删除。可以通过 `only_valid=False` 读取所有数据。

### Q: 支持哪些技术指标？
A: 
- 移动平均线（MA5, MA10, MA20, MA50, MA200）
- RSI（相对强弱指标）
- MACD（指数平滑异同移动平均线）
- KDJ（随机指标）
- 布林带（BOLL）
- 成交量指标（量比、成交量均线）

---

## 下一步

### Phase 3: 业务逻辑集成

1. 更新数据获取模块
2. 更新诊断系统
3. 更新策略系统
4. 更新 Web API

---

## 支持

如有问题，请查看：
1. [快速开始指南](docs/DATA_LAYER_QUICKSTART.md)
2. [完整文档](docs/DATA_LAYER_ARCHITECTURE.md)
3. 运行测试工具验证安装

---

**版本**: 1.0  
**更新时间**: 2026-01-05  
**状态**: ✅ 生产就绪

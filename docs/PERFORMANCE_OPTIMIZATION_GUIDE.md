# 性能优化使用指南

**更新日期**: 2026-01-01

---

## 📊 数据库优化概述

项目已完成数据库性能优化，采用**混合方案**：
- **分表**（5599张）：兼容现有代码
- **统一表**（1张）：高性能批量查询

---

## 🚀 如何使用高性能模式

### 1. 策略扫描

#### 默认方式（自动使用高性能模式）
```python
from src.data.database import StockDatabase
from src.business.strategies.volume_shrink import VolumeShrinkStrategy

db = StockDatabase()
strategy = VolumeShrinkStrategy(db)

# 默认使用高性能模式（use_unified_table=True）
signals = strategy.scan(
    date='2024-12-31',
    min_cap=50e8,
    max_cap=200e8
)

print(f"找到 {len(signals)} 个信号")
```

#### 兼容模式（使用旧方法）
```python
# 如果需要使用旧方法（逐个查询分表）
signals = strategy.scan(
    date='2024-12-31',
    use_unified_table=False  # 显式关闭高性能模式
)
```

### 2. 批量获取股票数据

#### 获取全市场某日数据
```python
from src.data.database import StockDatabase

db = StockDatabase()

# 一次查询获取全市场数据
df = db.get_market_data_unified(date='2024-12-31')
print(f"获取 {len(df)} 只股票的数据")
```

#### 获取指定股票某日数据
```python
codes = ['sh.600000', 'sz.000001', 'sz.000002']
df = db.get_market_data_unified(date='2024-12-31', codes=codes)
```

#### 获取最近N天数据
```python
# 获取全市场最近10天数据
df = db.get_recent_data_unified(days=10)

# 获取指定股票最近10天数据
codes = ['sh.600000', 'sz.000001']
df = db.get_recent_data_unified(days=10, codes=codes)
```

#### 批量获取历史数据
```python
codes = ['sh.600000', 'sz.000001', 'sz.000002']
df = db.get_stock_data_batch_unified(
    codes=codes,
    start_date='2024-01-01',
    end_date='2024-12-31'
)
```

---

## 📈 性能对比

### 策略扫描性能

| 股票数 | 兼容模式 | 高性能模式 | 提升倍数 |
|--------|---------|-----------|---------|
| 100只  | 0.09秒  | 0.04秒    | 2.59x   |
| 500只  | ~0.45秒 | 0.19秒    | ~2.4x   |
| 5000只 | ~4.5秒  | ~2秒      | ~2.3x   |

### 数据查询性能

| 操作 | 分表查询 | 统一表查询 | 提升倍数 |
|------|---------|-----------|---------|
| 单股票历史 | 0.066秒 | 0.003秒 | 19.9x |
| 全市场某日 | 5599次查询 | 1次查询 | 5599x |

---

## 🎯 使用建议

### 推荐使用高性能模式的场景
- ✅ 策略全市场扫描
- ✅ 回测引擎批量加载
- ✅ 数据分析和统计
- ✅ 批量计算指标

### 推荐使用兼容模式的场景
- ✅ 单只股票实时查询
- ✅ 调试单只股票问题
- ✅ 需要最新数据（统一表可能有延迟）

---

## 🔧 性能测试工具

### 策略扫描性能测试
```bash
python3 tools/benchmark_strategy_scan.py
```

### 数据库性能测试
```bash
# 查看统计信息
python3 tools/optimize_database.py --stats

# 性能基准测试
python3 tools/optimize_database.py --benchmark
```

---

## ⚠️ 注意事项

### 数据一致性
- ✅ **自动同步**: 所有数据写入自动同步到统一表
- ✅ **双写机制**: 分表和统一表同时更新
- ✅ **INSERT OR REPLACE**: 避免重复数据
- ⚠️ **历史数据**: 已在初始迁移时同步完成

详见：[数据同步机制说明](DATA_SYNC_GUIDE.md)

### 内存使用
- 批量查询会加载更多数据到内存
- 500只股票10天数据 ≈ 5000条记录 ≈ 1MB
- 5000只股票10天数据 ≈ 50000条记录 ≈ 10MB

### 向后兼容
- 所有现有代码无需修改
- 高性能模式是可选的
- 可随时切换回兼容模式

---

## 📝 常见问题

### Q: 为什么不完全删除分表？
A: 保留分表是为了：
- 兼容现有代码
- 支持实时数据更新
- 提供回退方案

### Q: 统一表数据会自动更新吗？
A: **会自动更新**！所有数据写入操作（`save_daily_data`、`append_daily_data`）都会自动同步到统一表。采用双写机制，确保数据一致性。详见 [数据同步机制说明](DATA_SYNC_GUIDE.md)。

### Q: 如何验证数据一致性？
A: 可以对比分表和统一表的查询结果：
```python
# 分表查询
df1 = db.get_daily_data('sh.600000')

# 统一表查询
df2 = db.get_stock_data_batch_unified(['sh.600000'])

# 对比
assert len(df1) == len(df2)
```

---

## 🚀 下一步优化

1. **回测引擎优化**: 使用批量查询方法
2. **自动同步机制**: 分表 → 统一表自动同步
3. **缓存机制**: 常用数据内存缓存
4. **并行计算**: 多进程策略扫描

---

**文档维护**: AI Assistant  
**最后更新**: 2026-01-01

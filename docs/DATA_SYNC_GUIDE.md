# 数据同步机制说明

**更新日期**: 2026-01-01

---

## 📊 数据同步架构

项目采用**双写机制**，确保分表和统一表数据一致：

```
数据写入
   ↓
分表 (daily_sh_600000)  ←→  统一表 (daily_data)
   ↓                              ↓
兼容现有代码                   高性能查询
```

---

## 🔄 自动同步机制

### 写入时自动同步

所有数据写入操作会**自动同步**到统一表：

```python
from src.data.database import StockDatabase

db = StockDatabase()

# 写入数据（自动同步到统一表）
db.save_daily_data('sh.600000', df)

# 追加数据（自动同步到统一表）
db.append_daily_data('sh.600000', df)
```

### 同步控制

可以选择性关闭同步（不推荐）：

```python
# 仅写入分表，不同步到统一表
db.save_daily_data('sh.600000', df, sync_to_unified=False)
```

---

## 🛠️ 数据同步方法

### 1. 自动同步（推荐）

**默认行为**: 所有数据写入自动同步到统一表

```python
# 正常使用，无需额外操作
db.save_daily_data(code, df)  # 自动同步
```

### 2. 手动同步

如果需要手动同步历史数据：

```python
# 从分表读取数据
df = db.get_daily_data('sh.600000')

# 手动同步到统一表
db._sync_to_unified_table('sh.600000', df)
db.conn.commit()
```

### 3. 批量同步

使用优化工具批量同步所有股票：

```bash
# 同步所有股票数据到统一表
python3 tools/optimize_database.py --migrate
```

---

## ✅ 数据一致性保证

### INSERT OR REPLACE策略

使用`INSERT OR REPLACE`确保：
- ✅ 重复数据自动覆盖（不会报错）
- ✅ 新数据正常插入
- ✅ 历史数据不会丢失

### 字段自动计算

统一表包含额外字段，会自动计算：
- `amplitude` = (high - low) / close * 100
- `change` = close * pct_chg / 100

---

## 🧪 测试数据同步

### 单股票同步测试

```bash
python3 tools/test_data_sync.py
```

测试内容：
1. 查询统一表现有数据
2. 写入新数据
3. 验证分表和统一表同步
4. 清理测试数据

### 批量同步测试

```bash
python3 tools/test_data_sync.py --batch
```

---

## 📈 性能影响

### 写入性能

| 操作 | 仅分表 | 分表+统一表 | 性能影响 |
|------|--------|------------|---------|
| 单条记录 | ~0.001秒 | ~0.002秒 | 2x |
| 100条记录 | ~0.1秒 | ~0.2秒 | 2x |

**结论**: 双写机制对写入性能影响可接受（2x），但查询性能提升巨大（2-20x）。

### 存储空间

- **分表**: 376 MB
- **统一表**: ~380 MB
- **总计**: ~756 MB（约2倍）

**结论**: 存储空间翻倍，但换来查询性能大幅提升。

---

## ⚠️ 注意事项

### 1. 历史数据同步

**问题**: 统一表只包含迁移时的数据，之后的新数据会自动同步。

**解决**: 
- 新数据自动同步（无需操作）
- 历史数据已在初始迁移时同步完成

### 2. 数据完整性检查

定期检查分表和统一表数据一致性：

```python
from src.data.database import StockDatabase

db = StockDatabase()

# 检查某只股票
code = 'sh.600000'

# 分表记录数
df1 = db.get_daily_data(code)
count1 = len(df1)

# 统一表记录数
cursor = db.conn.cursor()
cursor.execute("SELECT COUNT(*) FROM daily_data WHERE code = ?", (code,))
count2 = cursor.fetchone()[0]

print(f"{code}: 分表 {count1} 条, 统一表 {count2} 条")

if count1 == count2:
    print("✅ 数据一致")
else:
    print(f"⚠️  数据不一致，差异 {abs(count1 - count2)} 条")
```

### 3. 同步失败处理

如果同步失败（网络问题、磁盘满等）：
- 分表数据已写入（不会丢失）
- 统一表数据未写入（会有延迟）
- 下次写入时会自动补齐

---

## 🔧 故障排查

### 问题1: 统一表数据过时

**症状**: 策略扫描结果与预期不符

**检查**:
```python
# 检查最新日期
cursor.execute("SELECT MAX(date) FROM daily_data")
latest_unified = cursor.fetchone()[0]

cursor.execute("SELECT MAX(date) FROM daily_sh_600000")
latest_table = cursor.fetchone()[0]

print(f"统一表最新日期: {latest_unified}")
print(f"分表最新日期: {latest_table}")
```

**解决**: 手动同步最新数据
```bash
python3 tools/optimize_database.py --migrate
```

### 问题2: 数据不一致

**症状**: 分表和统一表记录数不同

**检查**:
```bash
python3 tools/test_data_sync.py --batch
```

**解决**: 重新同步该股票数据
```python
db = StockDatabase()
df = db.get_daily_data('sh.600000')
db._sync_to_unified_table('sh.600000', df)
db.conn.commit()
```

---

## 📝 最佳实践

### 1. 使用默认同步

```python
# ✅ 推荐：使用默认同步
db.save_daily_data(code, df)

# ❌ 不推荐：关闭同步
db.save_daily_data(code, df, sync_to_unified=False)
```

### 2. 定期检查数据一致性

建议每周运行一次数据一致性检查：

```bash
python3 tools/test_data_sync.py --batch
```

### 3. 监控统一表大小

```bash
# 查看数据库大小
du -h data/a_share.db

# 查看统一表记录数
sqlite3 data/a_share.db "SELECT COUNT(*) FROM daily_data"
```

---

## 🚀 未来优化

### P1 (本周)
- ⏳ 添加数据一致性监控脚本
- ⏳ 自动检测并修复不一致数据

### P2 (本月)
- ⏳ 实现增量同步（只同步变化的数据）
- ⏳ 添加同步日志和统计

### P3 (未来)
- ⏳ 考虑使用触发器自动同步
- ⏳ 实现分布式数据同步

---

**文档维护**: AI Assistant  
**最后更新**: 2026-01-01

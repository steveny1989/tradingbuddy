# 数据更新说明

## 当前状态

- **AKShare 最新数据**: 2026-01-05 ✅
- **新系统 Raw Layer**: 2026-01-04 ❌
- **新系统 Cleaned Layer**: 2026-01-04 ❌
- **缺少**: 2026-01-05 的数据

## 为什么返回空数据？

新系统的数据只到 2026-01-04，所以当你查询最新数据时会返回空。

## 立即更新

### 方法 1: 使用快速更新脚本（推荐）

```bash
python3 update_today.py
```

这会更新 2026-01-05 的数据到新系统。

### 方法 2: 使用主程序

```bash
python3 -m src.app.main update --date 20260105
```

### 方法 3: 更新到今天（会自动获取最新可用数据）

```bash
python3 -m src.app.main update
```

## 更新后验证

```bash
# 检查数据状态
python3 -m src.app.main status

# 或者运行检查脚本
python3 tools/check_raw_data_status.py
```

## 今天（2026-01-06）的数据

今天是周一，但交易数据通常要到**收盘后（下午3点后）**才会更新到 AKShare。

所以现在：
- ✅ 可以获取 2026-01-05 的数据
- ❌ 还不能获取 2026-01-06 的数据（要等收盘后）

## 设置自动更新

为了避免每次手动更新，建议设置定时任务：

```bash
# 编辑 crontab
crontab -e

# 添加每天 18:00 自动更新
0 18 * * * cd /Users/diyao/Documents/GitHub/tradingbuddy && python3 -m src.app.main update >> logs/cron.log 2>&1
```

## 问题排查

如果更新后还是返回空数据，检查：

1. **DatabaseAdapter 是否正确读取新系统**
   ```python
   from src.data.database_adapter import DatabaseAdapter
   db = DatabaseAdapter()
   df = db.get_daily_data('600519')
   print(f"数据条数: {len(df)}")
   print(f"最新日期: {df['date'].max() if not df.empty else 'N/A'}")
   ```

2. **检查数据库文件是否存在**
   ```bash
   ls -lh data/raw/daily_raw.db
   ls -lh data/cleaned/daily_cleaned.db
   ```

3. **查看日志**
   ```bash
   tail -f logs/data_sync_*.log
   ```

## 下一步

1. 运行 `python3 update_today.py` 更新 2026-01-05 的数据
2. 验证数据已更新
3. 设置定时任务自动更新
4. 今天收盘后（18:00 后）会自动更新 2026-01-06 的数据

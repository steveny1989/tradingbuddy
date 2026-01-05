# 迁移到三层数据架构 V2

## 概述

本文档说明如何从旧的单一数据库系统迁移到新的三层数据架构。

## 新旧系统对比

### 旧系统 (V1)
```
data/a_share.db  ← 单一数据库
├── stock_basic
├── market_snapshot
├── sync_status
├── balance_sheet
└── income_statement
```

**问题**:
- 原始数据和清洗数据混在一起
- 没有数据质量验证
- 技术指标每次实时计算，性能差
- 数据错误难以追溯

### 新系统 (V2)
```
data/
├── raw/              ← Raw Layer (原始数据)
│   ├── daily_raw.db
│   ├── financial_raw.db
│   └── market_raw.db
│
├── cleaned/          ← Cleaned Layer (清洗数据)
│   ├── daily_cleaned.db
│   └── financial_cleaned.db
│
└── aggregated/       ← Aggregated Layer (技术指标)
    └── indicators.db
```

**优势**:
- ✅ 数据可追溯（Raw Layer 保留原始数据）
- ✅ 数据质量保证（Cleaned Layer 验证数据）
- ✅ 性能优化（Aggregated Layer 预计算指标）
- ✅ 职责清晰，易于维护

## 数据流对比

### 旧系统流程
```
API → a_share.db → 业务逻辑
```

### 新系统流程
```
API → Raw Layer → Cleaned Layer → Aggregated Layer → 业务逻辑
      (原样保存)   (验证清洗)      (预计算指标)
```

## 迁移步骤

### Step 1: 使用新的数据采集脚本

#### 旧命令 (V1)
```bash
# 每日更新
python -m src.app.main update

# 全量下载
python -m src.app.main download
```

#### 新命令 (V2) ⭐
```bash
# 每日更新（推荐）
python -m src.app.main_v2 update

# 全量下载
python -m src.app.main_v2 download

# 查看状态
python -m src.app.main_v2 status
```

### Step 2: 验证数据

```bash
# 查看新系统状态
python -m src.app.main_v2 status
```

输出示例：
```
📊 三层数据架构状态报告
============================================================

【Raw Layer - 原始数据层】
  日线数据:
    - 总记录: 7,799,967
    - 股票数: 5,234

【Cleaned Layer - 清洗数据层】
  日线数据:
    - 总记录: 7,799,967
    - 有效记录: 7,795,123
    - 停牌记录: 4,844
    - 数据质量: 99.9%
    - 股票数: 5,234

【汇总】
  总股票数: 5,234
  总记录数: 7,799,967
  有效记录: 7,795,123
  数据质量: 99.9%
```

### Step 3: 业务代码无需修改

业务代码通过 `DatabaseAdapter` 访问数据，自动使用新的三层架构：

```python
from src.data.database_adapter import DatabaseAdapter

# 业务代码无需修改
db = DatabaseAdapter()
df = db.get_daily_data('600519')  # 自动从 Cleaned Layer 读取
```

## 新功能特性

### 1. 数据质量验证

新系统自动验证数据质量：

```python
# 验证规则
- 价格逻辑检查 (high >= low, high >= open/close 等)
- 成交量检查 (不能为负)
- 停牌检测 (成交量为0)
- 涨跌幅异常检测
```

### 2. 数据质量标记

Cleaned Layer 中每条记录都有质量标记：

```sql
SELECT * FROM daily_cleaned WHERE code = '600519';

-- 字段说明
is_valid: 1/0           -- 是否通过验证
is_suspended: 1/0       -- 是否停牌
validation_errors: JSON -- 验证错误详情
validation_warnings: JSON -- 验证警告
```

### 3. 预计算技术指标

Aggregated Layer 预先计算好技术指标：

```python
# 快速获取技术指标（无需实时计算）
indicators = db.get_indicators('600519')

# 包含指标
- MA5, MA10, MA20, MA50, MA200
- RSI
- MACD (DIF, DEA, MACD)
- KDJ (K, D, J)
- BOLL (上轨, 中轨, 下轨)
- 成交量指标
```

## 性能对比

### 旧系统
```python
# 每次都要实时计算指标
df = db.get_daily_data('600519')
df['ma20'] = df['close'].rolling(20).mean()  # 慢
df['rsi'] = calculate_rsi(df['close'])       # 慢
# ... 更多计算
```

### 新系统
```python
# 直接读取预计算的指标
indicators = db.get_indicators('600519')  # 快！
# 所有指标已经计算好
```

**性能提升**: 10-50倍（取决于指标复杂度）

## 数据迁移工具

如果需要将旧数据迁移到新系统：

```bash
# 使用现有的迁移工具
python tools/migrate_to_new_layers.py
```

## 常见问题

### Q1: 新旧系统可以并存吗？

**A**: 可以！两个系统完全独立：
- 旧系统: `data/a_share.db`
- 新系统: `data/raw/`, `data/cleaned/`, `data/aggregated/`

建议：
1. 先用新系统更新几天数据
2. 验证数据正确性
3. 确认无误后完全切换到新系统

### Q2: 业务代码需要修改吗？

**A**: 不需要！`DatabaseAdapter` 提供了兼容接口：

```python
# 这些代码无需修改
db = DatabaseAdapter()
df = db.get_daily_data('600519')
indicators = db.get_indicators('600519')
```

### Q3: 新系统占用更多存储空间吗？

**A**: 是的，约 2-3 倍：
- Raw Layer: 原始数据
- Cleaned Layer: 清洗数据（大小相近）
- Aggregated Layer: 技术指标（约 50% 大小）

但换来的是：
- ✅ 数据可追溯
- ✅ 数据质量保证
- ✅ 查询性能提升

### Q4: 如何回滚到旧系统？

**A**: 简单！只需使用旧命令：

```bash
# 回到旧系统
python -m src.app.main update
```

旧数据库 `data/a_share.db` 不会被删除。

## 推荐迁移时间表

### 第1天: 测试新系统
```bash
# 运行一次每日更新
python -m src.app.main_v2 update

# 检查状态
python -m src.app.main_v2 status

# 验证数据
python tools/quick_test_new_layers.py
```

### 第2-7天: 并行运行
```bash
# 每天同时运行新旧系统
python -m src.app.main update      # 旧系统
python -m src.app.main_v2 update   # 新系统

# 对比数据一致性
```

### 第8天: 完全切换
```bash
# 只运行新系统
python -m src.app.main_v2 update

# 可以考虑归档旧数据库
mv data/a_share.db data/a_share.db.backup
```

## 自动化脚本

创建定时任务（crontab）：

```bash
# 编辑 crontab
crontab -e

# 添加每日更新任务（每天 18:00 执行）
0 18 * * * cd /path/to/project && python -m src.app.main_v2 update >> logs/cron.log 2>&1
```

## 监控和告警

新系统提供更详细的日志：

```bash
# 查看今天的日志
tail -f logs/data_sync_v2_20260105.log

# 搜索错误
grep "ERROR" logs/data_sync_v2_*.log

# 搜索数据质量问题
grep "invalid" logs/data_sync_v2_*.log
```

## 总结

### 立即行动
```bash
# 1. 运行一次新系统
python -m src.app.main_v2 update

# 2. 检查状态
python -m src.app.main_v2 status

# 3. 如果一切正常，设置定时任务
```

### 关键优势
- ✅ 数据质量提升
- ✅ 性能提升 10-50倍
- ✅ 易于维护和调试
- ✅ 业务代码无需修改

### 需要帮助？
查看文档：
- `docs/DATA_LAYER_ARCHITECTURE.md` - 架构设计
- `docs/DATA_LAYER_QUICKSTART.md` - 快速开始
- `NEW_DATA_LAYER_README.md` - 详细说明

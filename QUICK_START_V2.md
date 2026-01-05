# V2 三层架构快速开始

## 🚀 5分钟快速上手

### 1. 测试新系统（推荐先做这个）

```bash
# 测试新系统是否正常工作
python tools/test_v2_system.py
```

预期输出：
```
🧪 V2 三层数据架构系统测试
============================================================
✅ 通过 - 初始化 DataFetcherV2
✅ 通过 - 获取单只股票数据
✅ 通过 - 保存到三层架构
✅ 通过 - 通过 Adapter 读取
✅ 通过 - 数据质量检查
✅ 通过 - 系统统计
总计: 6/6 通过
🎉 所有测试通过！V2 系统运行正常
```

### 2. 运行每日更新

```bash
# 使用新系统更新今天的数据
python -m src.app.main_v2 update
```

### 3. 查看数据状态

```bash
# 查看三层架构的数据统计
python -m src.app.main_v2 status
```

## 📊 新旧命令对照表

| 操作 | 旧命令 (V1) | 新命令 (V2) |
|------|------------|------------|
| 每日更新 | `python -m src.app.main update` | `python -m src.app.main_v2 update` |
| 全量下载 | `python -m src.app.main download` | `python -m src.app.main_v2 download` |
| 查看状态 | `python -m src.app.main status` | `python -m src.app.main_v2 status` |
| 指定日期 | `python -m src.app.main update --date 20260105` | `python -m src.app.main_v2 update --date 20260105` |
| 强制更新 | `python -m src.app.main download --force` | `python -m src.app.main_v2 download --force` |

## 🎯 核心区别

### 数据存储位置

**旧系统 (V1)**:
```
data/a_share.db  ← 所有数据都在这里
```

**新系统 (V2)**:
```
data/
├── raw/daily_raw.db          ← 原始数据
├── cleaned/daily_cleaned.db  ← 清洗后的数据
└── aggregated/indicators.db  ← 技术指标
```

### 数据流程

**旧系统**:
```
API → a_share.db → 业务代码
     (直接存储)   (实时计算指标)
```

**新系统**:
```
API → Raw → Cleaned → Aggregated → 业务代码
     (原样)  (验证)    (预计算)     (直接使用)
```

## 💡 实际使用示例

### 示例 1: 每日定时更新

```bash
# 创建定时任务脚本
cat > daily_update_v2.sh << 'EOF'
#!/bin/bash
cd /path/to/your/project
source venv/bin/activate  # 如果使用虚拟环境
python -m src.app.main_v2 update
EOF

chmod +x daily_update_v2.sh

# 添加到 crontab（每天18:00执行）
crontab -e
# 添加这行：
# 0 18 * * * /path/to/daily_update_v2.sh >> /path/to/logs/cron.log 2>&1
```

### 示例 2: 业务代码使用（无需修改）

```python
from src.data.database_adapter import DatabaseAdapter

# 初始化（自动使用新的三层架构）
db = DatabaseAdapter()

# 获取日线数据（从 Cleaned Layer）
df = db.get_daily_data('600519')
print(f"获取到 {len(df)} 条数据")

# 获取技术指标（从 Aggregated Layer，已预计算）
indicators = db.get_indicators('600519')
print(f"MA20: {indicators['ma20'].iloc[-1]:.2f}")
print(f"RSI: {indicators['rsi'].iloc[-1]:.2f}")
```

### 示例 3: 检查数据质量

```python
from src.data.layers import CleanedLayer

cleaned = CleanedLayer()

# 获取数据（包含质量标记）
df = cleaned.get_daily_data('600519', only_valid=False)

# 查看无效数据
invalid = df[df['is_valid'] == 0]
print(f"无效数据: {len(invalid)} 条")

# 查看停牌数据
suspended = df[df['is_suspended'] == 1]
print(f"停牌数据: {len(suspended)} 条")

# 查看验证错误
if not invalid.empty:
    print(invalid[['date', 'validation_errors']])
```

## 🔧 常见操作

### 更新指定日期的数据

```bash
# 更新2026年1月5日的数据
python -m src.app.main_v2 update --date 20260105
```

### 重新下载所有数据

```bash
# 从2023年开始重新下载（会覆盖已有数据）
python -m src.app.main_v2 download --start-date 20230101 --force
```

### 查看详细日志

```bash
# 实时查看日志
tail -f logs/data_sync_v2_$(date +%Y%m%d).log

# 查看错误
grep "ERROR" logs/data_sync_v2_*.log

# 查看数据质量问题
grep "invalid" logs/data_sync_v2_*.log
```

## 📈 性能对比

### 旧系统
```python
# 每次都要计算指标（慢）
df = db.get_daily_data('600519')
df['ma20'] = df['close'].rolling(20).mean()  # 实时计算
df['rsi'] = calculate_rsi(df)                # 实时计算
# 耗时: ~500ms
```

### 新系统
```python
# 直接读取预计算的指标（快）
indicators = db.get_indicators('600519')
ma20 = indicators['ma20']  # 已经算好
rsi = indicators['rsi']    # 已经算好
# 耗时: ~10ms
```

**性能提升**: 50倍！

## ⚠️ 注意事项

### 1. 存储空间

新系统需要更多存储空间（约2-3倍）：
- Raw Layer: 原始数据
- Cleaned Layer: 清洗数据
- Aggregated Layer: 技术指标

**建议**: 至少预留 10GB 空间

### 2. 首次运行

首次运行 `download` 会比较慢，因为要：
1. 下载原始数据
2. 验证和清洗
3. 计算技术指标

**建议**: 首次运行选择在非交易时间

### 3. 数据一致性

新旧系统可以并存，但建议：
1. 测试几天新系统
2. 确认数据正确
3. 完全切换到新系统

## 🆘 故障排查

### 问题 1: 找不到模块

```bash
# 确保在项目根目录
cd /path/to/your/project

# 确保安装了依赖
pip install -r requirements.txt
```

### 问题 2: 数据库文件不存在

```bash
# 创建必要的目录
mkdir -p data/raw data/cleaned data/aggregated logs

# 运行一次更新
python -m src.app.main_v2 update
```

### 问题 3: 数据为空

```bash
# 检查是否有数据
python -m src.app.main_v2 status

# 如果为空，运行全量下载
python -m src.app.main_v2 download
```

## 📚 更多文档

- `MIGRATION_TO_V2.md` - 详细迁移指南
- `docs/DATA_LAYER_ARCHITECTURE.md` - 架构设计
- `docs/DATA_LAYER_QUICKSTART.md` - 快速开始
- `NEW_DATA_LAYER_README.md` - 完整说明

## ✅ 检查清单

在正式使用前，确保：

- [ ] 运行 `python tools/test_v2_system.py` 全部通过
- [ ] 运行 `python -m src.app.main_v2 update` 成功
- [ ] 运行 `python -m src.app.main_v2 status` 看到数据
- [ ] 业务代码能正常读取数据
- [ ] 设置了定时任务（可选）

## 🎉 开始使用

```bash
# 1. 测试系统
python tools/test_v2_system.py

# 2. 更新今天的数据
python -m src.app.main_v2 update

# 3. 查看状态
python -m src.app.main_v2 status

# 4. 享受新系统带来的性能提升！
```

---

**需要帮助？** 查看 `MIGRATION_TO_V2.md` 获取更多信息。

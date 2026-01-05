# 旧数据系统 V1 (已归档)

## 归档日期
2026-01-05

## 归档原因
迁移到新的三层数据架构 (Raw → Cleaned → Aggregated)

## 归档文件

### 主程序
- `main_v1.py` - 旧的主程序入口
  - 使用单一数据库 `data/a_share.db`
  - 没有数据质量验证
  - 技术指标实时计算

### 数据采集
- `fetcher_v1.py` - 旧的数据采集器
  - 直接写入 `data/a_share.db`
  - 没有数据分层
  - 没有数据验证

### 自动更新
- `auto_update.py` - 旧的自动更新脚本

## 新系统位置

### 主程序
- `src/app/main.py` - 新的主程序（原 main_v2.py）
- `src/app/main_v2.py` - 保留的 V2 版本

### 数据采集
- `src/data/fetcher.py` - 新的数据采集器
  - 写入三层架构
  - 自动验证数据质量
  - 预计算技术指标

## 数据库对比

### 旧系统
```
data/a_share.db  ← 单一数据库
```

### 新系统
```
data/
├── raw/daily_raw.db          ← 原始数据
├── cleaned/daily_cleaned.db  ← 清洗数据
└── aggregated/indicators.db  ← 技术指标
```

## 如何使用旧系统（不推荐）

如果需要临时使用旧系统：

```bash
# 复制旧文件到工作目录
cp archive/old_data_system_v1/main_v1.py src/app/main_old.py
cp archive/old_data_system_v1/fetcher_v1.py src/data/fetcher_old.py

# 修改 main_old.py 中的导入
# from src.data.fetcher import DataFetcher
# 改为
# from src.data.fetcher_old import DataFetcher

# 运行
python -m src.app.main_old update
```

## 迁移到新系统

参考文档：
- `MIGRATION_TO_V2.md` - 详细迁移指南
- `QUICK_START_V2.md` - 快速开始

## 新系统优势

1. ✅ **数据可追溯** - Raw Layer 保留原始数据
2. ✅ **数据质量保证** - Cleaned Layer 验证数据
3. ✅ **性能提升 50倍** - Aggregated Layer 预计算指标
4. ✅ **易于维护** - 职责清晰，分层明确

## 注意事项

- 旧数据库 `data/a_share.db` 仍然保留，不会被删除
- 新旧系统可以并存
- 业务代码通过 `DatabaseAdapter` 自动使用新系统
- 建议完全切换到新系统后，可以归档旧数据库

## 相关文档

- `../../MIGRATION_TO_V2.md` - 迁移指南
- `../../QUICK_START_V2.md` - 快速开始
- `../../docs/DATA_LAYER_ARCHITECTURE.md` - 架构设计

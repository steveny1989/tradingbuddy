# V1 脚本归档说明

本目录包含已被 V2 版本替换的旧脚本。

## 归档的脚本

### `fetch_index_data_v1.py`

**归档日期**: 2026-01-05

**原路径**: `tools/fetch_index_data.py`

**归档原因**: 
- 使用旧的 V1 单体数据库架构 (`data/a_share.db`)
- 已被 V2 版本替换，新版本使用三层数据架构

**V2 替代版本**: `tools/fetch_index_data.py`

**主要区别**:
```python
# V1 (已归档)
from src.data.database import StockDatabase
db = StockDatabase()  # 连接到 data/a_share.db

# V2 (当前版本)
from src.config.settings import DB_PATHS
db_path = os.path.join(DB_PATHS['raw'], 'market_raw.db')
# 直接写入 data/raw/market_raw.db
```

**如果需要使用旧版本**:
```bash
# 不推荐，仅用于紧急情况
python3 archive/fetch_index_data_v1.py
```

---

## 迁移时间线

| 日期 | 脚本 | 操作 |
|------|------|------|
| 2026-01-05 | `fetch_index_data.py` | 归档 V1，替换为 V2 |

---

## 相关文档

- `V2_MIGRATION_STATUS.md` - V2 迁移状态报告
- `docs/V2_CONFIG_MIGRATION.md` - 配置迁移指南
- `docs/DATA_LAYER_ARCHITECTURE.md` - 数据层架构文档

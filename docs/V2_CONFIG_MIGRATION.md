# V2 配置迁移指南

## 问题背景

在从 V1 单体架构迁移到 V2 三层数据架构的过程中，出现了"双轨制"现象：

- **V1 系统**：使用 `settings.py` 中的 `DB_PATH = "data/a_share.db"`
- **V2 系统**：在数据层代码中硬编码了新路径 `data/raw/`, `data/cleaned/`, `data/aggregated/`

这导致配置不统一，增加了维护成本和理解难度。

## 解决方案

### 1. 统一配置文件 (已完成)

更新 `src/config/settings.py`：

```python
# V2 三层数据架构路径
DB_PATHS = {
    "raw": "data/raw",           # 原始数据层
    "cleaned": "data/cleaned",   # 清洗数据层
    "aggregated": "data/aggregated",  # 聚合数据层
    "legacy": "data/a_share.db"  # V1 遗留数据库（兼容旧代码）
}

# V1 兼容配置（逐步废弃）
DB_PATH = "data/a_share.db"  # 保留用于向后兼容
```

### 2. 数据层使用新配置

**推荐做法**：数据层从配置文件读取路径

```python
from src.config.settings import DB_PATHS

class RawLayer:
    def __init__(self, db_path: str = None):
        # 优先使用传入参数，否则使用配置
        self.db_path = db_path or DB_PATHS["raw"]
```

**当前状态**：数据层使用默认参数（已经正确指向 V2 路径）

```python
class RawLayer:
    def __init__(self, db_path: str = 'data/raw'):
        # 默认值已经是正确的 V2 路径
```

### 3. 架构验证更新 (已完成)

更新 `tools/verify_architecture.py` 以检查 V2 目录结构：

```python
directories = [
    ...
    ("data/", "数据根目录"),
    ("data/raw/", "原始数据层 (V2)"),
    ("data/cleaned/", "清洗数据层 (V2)"),
    ("data/aggregated/", "聚合数据层 (V2)"),
    ...
]
```

## 数据存储现状

### V2 数据库（已存在）

```
data/
├── raw/
│   ├── daily_raw.db          # 日线原始数据
│   ├── financial_raw.db      # 财务原始数据
│   └── market_raw.db         # 市场数据
├── cleaned/
│   ├── daily_cleaned.db      # 清洗后日线数据
│   └── financial_cleaned.db  # 清洗后财务数据
└── aggregated/
    ├── indicators.db         # 技术指标
    └── features.db           # 特征工程
```

### V1 数据库（遗留）

```
data/
└── a_share.db               # 单体数据库（向后兼容）
```

## 迁移路径

### 阶段 1：双轨并行（当前状态）✅

- V2 系统正常运行
- V1 系统保持兼容
- 配置文件已统一

### 阶段 2：逐步迁移（建议）

1. **更新旧工具脚本**
   - `tools/fetch_index_data.py` 等旧脚本改用 V2 数据层
   - 通过 `DB_PATHS` 访问数据

2. **废弃 V1 直接访问**
   - 标记 `DB_PATH` 为 deprecated
   - 添加警告日志

### 阶段 3：完全切换（未来）

- 移除 `DB_PATH` 配置
- 归档 `data/a_share.db`
- 所有代码使用 V2 架构

## 使用示例

### V2 数据层使用（推荐）

```python
from src.data.layers.raw_layer import RawLayer
from src.data.layers.cleaned_layer import CleanedLayer
from src.data.layers.aggregated_layer import AggregatedLayer

# 使用默认配置（自动使用 V2 路径）
raw = RawLayer()
cleaned = CleanedLayer()
aggregated = AggregatedLayer()

# 或显式指定配置
from src.config.settings import DB_PATHS
raw = RawLayer(db_path=DB_PATHS["raw"])
```

### V1 兼容访问（逐步废弃）

```python
from src.config.settings import DB_PATH
from src.data.database import StockDatabase

# 旧代码仍然可以工作
db = StockDatabase(DB_PATH)
```

## 验证配置

运行配置验证：

```bash
python tools/verify_config.py
```

检查 V2 数据存在：

```bash
ls -la data/raw/
ls -la data/cleaned/
ls -la data/aggregated/
```

## 总结

✅ **已完成**：
- 统一配置文件 `settings.py`
- 更新架构验证脚本
- V2 数据层正常运行

📋 **待完成**：
- 迁移旧工具脚本使用 V2 数据层
- 添加配置使用文档
- 逐步废弃 V1 直接访问

🎯 **目标**：
- 配置统一管理
- 代码清晰易懂
- 平滑迁移过渡

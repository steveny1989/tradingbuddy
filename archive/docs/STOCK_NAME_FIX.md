# 股票名称显示修复 - 显示中文名称而非代码

## 问题描述

用户反馈：在自选股列表和今日精选列表中，股票名称显示为 "sh.600489" 而不是中文名称（如"中金岭南"）。

**问题根源**：
后端策略扫描时，从 `market_cap_data` 表获取股票池，该表的 `name` 字段存储的是 `full_code`（如 "sh.600489"）而不是真实的中文名称。

## 解决方案

### 修改策略的 `get_stock_pool` 方法

在获取股票池时，JOIN `stock_basic` 表来获取真实的中文名称。

#### 修改的文件：

1. **src/business/strategies/volume_shrink.py**
   - 第 40-72 行：`get_stock_pool` 方法
   - 使用 LEFT JOIN 连接 `stock_basic` 表
   - 使用 `COALESCE(s.name, m.name)` 优先获取中文名称

2. **src/business/strategies/ma_crossover.py**
   - 第 55-87 行：`get_stock_pool` 方法
   - 同样的修改逻辑

### 修改前后对比

#### 修改前 ❌
```sql
SELECT full_code, code, name, total_cap, cap_category, market
FROM market_cap_data
WHERE ...
```
返回的 `name` 字段：`sh.600489`

#### 修改后 ✅
```sql
SELECT 
    m.full_code, 
    m.code, 
    COALESCE(s.name, m.name) as name,  -- 优先使用 stock_basic 的中文名称
    m.total_cap, 
    m.cap_category, 
    m.market
FROM market_cap_data m
LEFT JOIN stock_basic s ON m.code = s.code
WHERE ...
```
返回的 `name` 字段：`中金岭南`

## 数据流

### 完整的数据流程：

1. **策略扫描** (`volume_shrink.py` / `ma_crossover.py`)
   - `get_stock_pool()` → 从数据库获取股票池
   - **修复点**：JOIN `stock_basic` 表获取中文名称 ✅
   - 返回 DataFrame，包含 `name` 字段（中文名称）

2. **扫描结果** (`picker.py` - `scan_daily_picks()`)
   - 第 224 行：`'name': signal_data.get('name', '')`
   - 从策略返回的 DataFrame 中获取 `name`
   - 现在获取的是中文名称 ✅

3. **API 返回** (`picker.py` - `get_daily_picks()`)
   - 从缓存读取扫描结果
   - 返回给前端，包含中文名称 ✅

4. **前端显示** (`SimplePicker.premium.tsx`)
   - 第 87 行：`name: item.name`
   - 显示 API 返回的中文名称 ✅

5. **自选股存储** (`SimplePicker.premium.tsx`)
   - 第 139 行：`name: stock.name`
   - 存储中文名称到 localStorage ✅

6. **自选股显示** (`WatchlistCard.tsx`)
   - 第 199 行：`{record.name}`
   - 显示中文名称 ✅

## 影响范围

### 后端：
- ✅ `src/business/strategies/volume_shrink.py` - 缩量三连跌策略
- ✅ `src/business/strategies/ma_crossover.py` - 均线突破策略

### 前端：
- ✅ 今日精选列表 - 显示中文名称
- ✅ 自选股列表 - 显示中文名称
- ✅ 策略历史表现 - 显示中文名称

## 测试步骤

### 1. 重启后端服务
```bash
./start_backend.sh
```

### 2. 清除缓存并重新扫描
访问后端 API：
```bash
curl http://localhost:5001/api/picker/sync
```

### 3. 验证今日精选
- 访问：http://localhost:3000/picker
- 查看"今日精选股票"卡片
- 确认显示：**中金岭南** 而不是 sh.600489 ✅

### 4. 验证自选股
- 点击"加入自选"按钮
- 查看"我的自选监控"列表
- 确认显示：**中金岭南** 而不是 sh.600489 ✅

### 5. 验证数据库
```python
import sqlite3
import pandas as pd

conn = sqlite3.connect('data/stock_data.db')

# 测试新的 SQL 查询
query = """
SELECT 
    m.full_code, 
    m.code, 
    COALESCE(s.name, m.name) as name,
    m.total_cap
FROM market_cap_data m
LEFT JOIN stock_basic s ON m.code = s.code
WHERE m.code = '600489'
LIMIT 1
"""

result = pd.read_sql(query, conn)
print(result)
# 应该显示：full_code='sh.600489', code='600489', name='中金岭南'
```

## 技术细节

### SQL JOIN 说明

使用 `LEFT JOIN` 而不是 `INNER JOIN`：
- 确保即使 `stock_basic` 表中没有对应记录，也能返回股票
- 使用 `COALESCE(s.name, m.name)` 作为后备方案

### COALESCE 函数

```sql
COALESCE(s.name, m.name) as name
```

- 如果 `stock_basic.name` 存在，使用它（中文名称）
- 如果不存在，使用 `market_cap_data.name` 作为后备
- 确保 `name` 字段永远不为 NULL

## 相关问题

### 为什么 market_cap_data 表的 name 字段是代码？

可能的原因：
1. 数据导入时使用了 `full_code` 作为 `name`
2. 表结构设计问题
3. 数据同步脚本的 bug

### 长期解决方案

建议：
1. 修复 `market_cap_data` 表的数据，将 `name` 字段更新为真实的中文名称
2. 或者在表结构中明确区分 `full_code` 和 `name` 字段
3. 添加数据验证，确保 `name` 字段不包含 "sh." 或 "sz." 前缀

## 状态

✅ **已完成** - 2026-01-02

所有策略的 `get_stock_pool` 方法已修改，确保返回真实的中文名称。

---

**修复人员**：后端工程师  
**审核状态**：待测试验证  
**部署状态**：待后端重启

# 数据库优化方案

## 当前问题

### 分表策略的性能瓶颈
- **现状**: 每只股票一张表（`daily_sh_600000`, `daily_sz_000001`等），共5792张表
- **问题**: 全市场扫描需要5792次查询，I/O开销巨大
- **影响**: 策略扫描速度慢，回测效率低

## 优化方案

### 方案A: 统一大表 + 复合索引（推荐）

**表结构**:
```sql
CREATE TABLE daily_data (
    code TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    close REAL,
    high REAL,
    low REAL,
    volume REAL,
    amount REAL,
    amplitude REAL,
    pct_chg REAL,
    change REAL,
    turnover REAL,
    PRIMARY KEY (code, date)
);

CREATE INDEX idx_date_code ON daily_data(date, code);
CREATE INDEX idx_code_date ON daily_data(code, date);
```

**优点**:
- 单次查询可获取全市场某日数据
- 索引优化后查询速度快
- 便于批量操作和数据分析

**缺点**:
- 单表数据量大（约400万条记录）
- 需要迁移现有数据

### 方案B: 按市场分表

**表结构**:
```sql
-- 上海市场
CREATE TABLE daily_sh (code, date, ..., PRIMARY KEY (code, date));
-- 深圳市场  
CREATE TABLE daily_sz (code, date, ..., PRIMARY KEY (code, date));
-- 北京市场
CREATE TABLE daily_bj (code, date, ..., PRIMARY KEY (code, date));
```

**优点**:
- 表数量从5792减少到3个
- 可以按市场并行查询
- 迁移成本相对较小

**缺点**:
- 跨市场查询仍需多次I/O
- 不如方案A彻底

### 方案C: 混合方案（当前保留 + 新增统一表）

**实施步骤**:
1. 保留现有分表结构（用于单股票查询）
2. 新增统一大表`daily_data`（用于全市场扫描）
3. 数据双写或定期同步

**优点**:
- 兼容现有代码
- 渐进式迁移，风险低
- 可以根据场景选择最优查询方式

**缺点**:
- 存储空间翻倍
- 需要维护数据一致性

## 推荐实施路径

### 阶段1: 创建统一表（不破坏现有结构）
```python
# 在 StockDatabase 中新增方法
def create_unified_table(self):
    """创建统一的日线数据表"""
    self.conn.execute("""
        CREATE TABLE IF NOT EXISTS daily_data (
            code TEXT NOT NULL,
            date TEXT NOT NULL,
            open REAL, close REAL, high REAL, low REAL,
            volume REAL, amount REAL,
            amplitude REAL, pct_chg REAL, change REAL, turnover REAL,
            PRIMARY KEY (code, date)
        )
    """)
    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_date_code ON daily_data(date, code)")
    self.conn.execute("CREATE INDEX IF NOT EXISTS idx_code_date ON daily_data(code, date)")
```

### 阶段2: 数据迁移脚本
```python
def migrate_to_unified_table(self):
    """将分表数据迁移到统一表"""
    cursor = self.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE 'daily_%'")
    tables = cursor.fetchall()
    
    for (table_name,) in tables:
        if table_name == 'daily_data':
            continue
        
        # 提取股票代码
        code = table_name.replace('daily_', '').replace('_', '.')
        
        # 迁移数据
        self.conn.execute(f"""
            INSERT OR IGNORE INTO daily_data 
            SELECT '{code}' as code, * FROM {table_name}
        """)
```

### 阶段3: 优化查询方法
```python
def get_market_data(self, date: str, codes: List[str] = None) -> pd.DataFrame:
    """获取全市场或指定股票的某日数据（使用统一表）"""
    if codes:
        placeholders = ','.join(['?' for _ in codes])
        query = f"SELECT * FROM daily_data WHERE date = ? AND code IN ({placeholders})"
        return pd.read_sql(query, self.conn, params=[date] + codes)
    else:
        query = "SELECT * FROM daily_data WHERE date = ?"
        return pd.read_sql(query, self.conn, params=[date])

def get_recent_data(self, days: int = 10) -> pd.DataFrame:
    """获取全市场最近N天的数据（用于策略扫描）"""
    query = f"""
        SELECT * FROM daily_data 
        WHERE date >= (SELECT MAX(date) FROM daily_data) - {days}
        ORDER BY code, date
    """
    return pd.read_sql(query, self.conn)
```

## 性能对比预估

| 操作 | 当前方案 | 优化后 | 提升倍数 |
|------|---------|--------|---------|
| 全市场单日数据查询 | 5792次查询 | 1次查询 | 5792x |
| 策略扫描（500只股票） | 500次查询 | 1次查询 | 500x |
| 单股票历史查询 | 1次查询 | 1次查询 | 1x |

## 风险控制

1. **数据一致性**: 迁移过程中使用`INSERT OR IGNORE`避免重复
2. **回滚方案**: 保留原有分表，出问题可立即回退
3. **渐进式切换**: 先在策略扫描中使用新表，验证无误后再全面切换

## 下一步行动

- [ ] 创建统一表结构
- [ ] 编写数据迁移脚本
- [ ] 测试查询性能
- [ ] 修改策略扫描逻辑使用新表
- [ ] 性能对比测试
- [ ] 全面切换（可选）

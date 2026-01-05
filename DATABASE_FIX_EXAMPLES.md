# 数据库问题修复示例

本文档展示如何修复代码中的数据库连接问题。

---

## 修复示例 1: 直接创建连接的问题

### ❌ 问题代码

```python
# src/business/post_market/smart_analyzer.py
def _get_industry(self, code: str) -> Optional[str]:
    pure_code = code.split('.')[1] if '.' in code else code
    
    try:
        conn = sqlite3.connect('data/a_share.db')
        query = "SELECT industry FROM industry_data WHERE code = ?"
        result = pd.read_sql_query(query, conn, params=(pure_code,))
        conn.close()
        
        if not result.empty:
            return result.iloc[0]['industry']
    except Exception as e:
        print(f"获取行业信息失败: {e}")
    
    return None
```

**问题**:
- 如果 `pd.read_sql_query` 抛出异常，`conn.close()` 不会执行
- 连接可能泄漏
- 没有使用 WAL 模式，性能差

### ✅ 修复后的代码

```python
# src/business/post_market/smart_analyzer.py
from src.data.connection_manager import get_connection_manager

def _get_industry(self, code: str) -> Optional[str]:
    pure_code = code.split('.')[1] if '.' in code else code
    
    try:
        conn_mgr = get_connection_manager('data/a_share.db')
        query = "SELECT industry FROM industry_data WHERE code = ?"
        
        with conn_mgr.connection() as conn:
            result = pd.read_sql_query(query, conn, params=(pure_code,))
        
        if not result.empty:
            return result.iloc[0]['industry']
    except Exception as e:
        logger.error(f"获取行业信息失败: {e}", exc_info=True)
    
    return None
```

**改进**:
- ✅ 使用连接管理器，自动管理连接
- ✅ 使用上下文管理器，确保连接正确关闭
- ✅ 启用 WAL 模式，提高性能
- ✅ 使用 logger 而不是 print

---

## 修复示例 2: 需要事务的操作

### ❌ 问题代码

```python
# src/data/database.py
def save_daily_data(self, code: str, df: pd.DataFrame, sync_to_unified: bool = True):
    if df.empty:
        return
    
    table_name = f"daily_{code.replace('.', '_')}"
    
    # 保存到分表
    cursor = self.conn.cursor()
    for _, row in df.iterrows():
        cursor.execute(f"""
            INSERT OR REPLACE INTO {table_name} 
            (date, code, open, high, low, close, volume, amount, pct_chg, turnover)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (...))
    
    self.conn.commit()
    
    # 同步到统一表（如果这里失败，分表已经提交了）
    if sync_to_unified:
        self._sync_to_unified_table(code, df)
    
    self.conn.commit()
```

**问题**:
- 如果 `_sync_to_unified_table` 失败，分表数据已提交，数据不一致
- 没有事务保护

### ✅ 修复后的代码

```python
# src/data/database.py
from src.data.connection_manager import DatabaseConnectionManager

class StockDatabase:
    def __init__(self, db_path: str = "data/a_share.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn_mgr = DatabaseConnectionManager(str(self.db_path))
        self._init_tables()
        self._run_migrations()
    
    @property
    def conn(self):
        """获取数据库连接（兼容旧代码）"""
        return self.conn_mgr.get_connection()
    
    def save_daily_data(self, code: str, df: pd.DataFrame, sync_to_unified: bool = True):
        if df.empty:
            return
        
        table_name = f"daily_{code.replace('.', '_')}"
        
        # 使用事务保护
        with self.conn_mgr.transaction() as conn:
            cursor = conn.cursor()
            
            # 保存到分表
            for _, row in df.iterrows():
                cursor.execute(f"""
                    INSERT OR REPLACE INTO {table_name} 
                    (date, code, open, high, low, close, volume, amount, pct_chg, turnover)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (...))
            
            # 同步到统一表
            if sync_to_unified:
                self._sync_to_unified_table(code, df, conn=conn)
            
            # 更新同步状态
            self._update_sync_status(code, total, 'success', conn=conn)
        
        # 事务自动提交或回滚
```

**改进**:
- ✅ 使用事务保护，确保数据一致性
- ✅ 如果任何操作失败，自动回滚
- ✅ 使用连接管理器，自动优化配置

---

## 修复示例 3: 批量操作

### ❌ 问题代码

```python
# src/business/post_market/capital_analysis.py
def analyze_capital_flow(self, date: str):
    conn = sqlite3.connect(self.db_path)
    
    # 查询1
    df1 = pd.read_sql_query("SELECT ...", conn)
    
    # 查询2
    df2 = pd.read_sql_query("SELECT ...", conn)
    
    # 查询3
    df3 = pd.read_sql_query("SELECT ...", conn)
    
    conn.close()
    
    # 处理数据
    ...
```

**问题**:
- 如果中间发生异常，连接不会关闭
- 没有使用 WAL 模式

### ✅ 修复后的代码

```python
# src/business/post_market/capital_analysis.py
from src.data.connection_manager import get_connection_manager

def analyze_capital_flow(self, date: str):
    conn_mgr = get_connection_manager(self.db_path)
    
    with conn_mgr.connection() as conn:
        # 查询1
        df1 = pd.read_sql_query("SELECT ...", conn, params=(date,))
        
        # 查询2
        df2 = pd.read_sql_query("SELECT ...", conn, params=(date,))
        
        # 查询3
        df3 = pd.read_sql_query("SELECT ...", conn, params=(date,))
    
    # 处理数据（连接已自动关闭）
    ...
```

**改进**:
- ✅ 使用上下文管理器，确保连接关闭
- ✅ 使用参数化查询，防止 SQL 注入
- ✅ 启用 WAL 模式，提高性能

---

## 修复示例 4: 需要写入的操作

### ❌ 问题代码

```python
# src/business/diagnosis/diagnosis_engine.py
def save_diagnosis_result(self, result: dict):
    conn = sqlite3.connect(self.db_path)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO diagnosis_results (...)
        VALUES (...)
    """, (...))
    
    conn.commit()
    conn.close()
```

**问题**:
- 如果 commit 失败，没有回滚
- 连接可能泄漏

### ✅ 修复后的代码

```python
# src/business/diagnosis/diagnosis_engine.py
from src.data.connection_manager import get_connection_manager

def save_diagnosis_result(self, result: dict):
    conn_mgr = get_connection_manager(self.db_path)
    
    with conn_mgr.transaction() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO diagnosis_results (...)
            VALUES (...)
        """, (...))
        # 自动提交或回滚
```

**改进**:
- ✅ 使用事务，确保数据一致性
- ✅ 自动处理提交和回滚
- ✅ 连接自动管理

---

## 修复步骤总结

### 1. 导入连接管理器

```python
from src.data.connection_manager import get_connection_manager
# 或
from src.data.connection_manager import DatabaseConnectionManager
```

### 2. 替换直接创建连接

```python
# ❌ 旧代码
conn = sqlite3.connect('data/a_share.db')

# ✅ 新代码
conn_mgr = get_connection_manager('data/a_share.db')
conn = conn_mgr.get_connection()
```

### 3. 使用上下文管理器

```python
# ❌ 旧代码
conn = sqlite3.connect('data/a_share.db')
try:
    # 操作
    conn.commit()
finally:
    conn.close()

# ✅ 新代码
conn_mgr = get_connection_manager('data/a_share.db')
with conn_mgr.connection() as conn:
    # 操作
    # 自动关闭连接
```

### 4. 需要事务时使用 transaction

```python
# ❌ 旧代码
conn = sqlite3.connect('data/a_share.db')
try:
    cursor.execute("INSERT ...")
    cursor.execute("UPDATE ...")
    conn.commit()
except:
    conn.rollback()
finally:
    conn.close()

# ✅ 新代码
conn_mgr = get_connection_manager('data/a_share.db')
with conn_mgr.transaction() as conn:
    cursor = conn.cursor()
    cursor.execute("INSERT ...")
    cursor.execute("UPDATE ...")
    # 自动提交或回滚
```

---

## 需要修复的文件列表

### 高优先级（立即修复）

1. `src/business/post_market/smart_analyzer.py` - 3 处
2. `src/business/post_market/financial_risk.py` - 1 处
3. `src/business/diagnosis/diagnosis_engine.py` - 1 处
4. `src/business/post_market/capital_analysis.py` - 5 处
5. `src/business/post_market/sector_analysis.py` - 5 处
6. `src/business/diagnosis/market_comparison.py` - 3 处

### 中优先级（近期修复）

7. `src/data/database.py` - 添加事务保护
8. 其他业务模块中的数据库操作

---

## 测试建议

修复后，建议进行以下测试：

1. **连接泄漏测试**: 运行长时间任务，检查连接数是否稳定
2. **并发测试**: 多线程同时访问数据库，检查是否出现锁定
3. **事务测试**: 模拟失败场景，检查是否正确回滚
4. **性能测试**: 对比修复前后的性能差异




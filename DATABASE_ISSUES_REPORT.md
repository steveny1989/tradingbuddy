# 数据库问题分析报告

**生成时间**: 2026-01-05  
**分析范围**: 从数据库角度检查代码质量和潜在问题

---

## 🔴 严重问题

### 1. 数据库连接管理混乱

**问题描述**:
- 多个地方直接创建新的数据库连接，没有统一管理
- 连接创建后没有使用上下文管理器，存在资源泄漏风险
- 异常情况下连接可能不会正确关闭

**问题位置**:
- `src/business/post_market/smart_analyzer.py`: 多处直接 `sqlite3.connect('data/a_share.db')`
- `src/business/post_market/financial_risk.py`: 直接创建连接
- `src/business/diagnosis/diagnosis_engine.py`: 直接创建连接
- `src/business/post_market/capital_analysis.py`: 多处直接创建连接
- `src/business/post_market/sector_analysis.py`: 多处直接创建连接

**示例代码**:
```python
# ❌ 不安全的做法
conn = sqlite3.connect('data/a_share.db')
query = "SELECT ..."
result = pd.read_sql_query(query, conn)
conn.close()  # 如果中间发生异常，连接不会关闭
```

**影响**:
- 资源泄漏：连接未正确关闭会导致数据库文件锁定
- 并发问题：多个连接同时写入可能导致数据库锁定
- 维护困难：难以追踪和管理连接

**建议修复**:
```python
# ✅ 使用上下文管理器
with sqlite3.connect('data/a_share.db') as conn:
    result = pd.read_sql_query(query, conn, params=params)
# 自动关闭连接，即使发生异常
```

---

### 2. 并发安全问题

**问题描述**:
- `StockDatabase` 使用 `check_same_thread=False`，在多线程环境中不安全
- 没有使用 WAL (Write-Ahead Logging) 模式，并发写入性能差
- 多个线程同时写入可能导致数据库锁定

**问题位置**:
- `src/data/database.py:19`: `self.conn = sqlite3.connect(self.db_path, check_same_thread=False)`

**影响**:
- 多线程环境下可能出现数据竞争
- 并发写入时数据库可能被锁定
- 性能下降：没有 WAL 模式，写入需要等待读操作完成

**建议修复**:
```python
# ✅ 启用 WAL 模式并设置超时
self.conn = sqlite3.connect(
    self.db_path,
    timeout=30.0,  # 设置超时，避免长时间锁定
    check_same_thread=True  # 每个线程使用自己的连接
)
self.conn.execute('PRAGMA journal_mode=WAL')  # 启用 WAL 模式
```

---

### 3. 事务处理不完整

**问题描述**:
- 很多操作没有使用事务，数据一致性无法保证
- 没有统一的错误处理和回滚机制
- 部分操作跨多个表，但没有事务保护

**问题位置**:
- `src/data/database.py`: `save_daily_data()` 方法中，同步到统一表和更新状态没有事务保护
- 财务数据保存方法中，多个表的操作没有事务

**示例代码**:
```python
# ❌ 没有事务保护
def save_daily_data(self, code: str, df: pd.DataFrame):
    # 保存到分表
    cursor.execute(f"INSERT OR REPLACE INTO {table_name} ...")
    self.conn.commit()
    
    # 同步到统一表（如果这里失败，分表已经提交了）
    self._sync_to_unified_table(code, df)
    self.conn.commit()
```

**影响**:
- 数据不一致：部分操作成功，部分失败
- 无法回滚：错误发生后无法恢复

**建议修复**:
```python
# ✅ 使用事务
def save_daily_data(self, code: str, df: pd.DataFrame):
    try:
        self.conn.execute('BEGIN TRANSACTION')
        # 保存到分表
        cursor.execute(f"INSERT OR REPLACE INTO {table_name} ...")
        # 同步到统一表
        self._sync_to_unified_table(code, df)
        self.conn.commit()
    except Exception as e:
        self.conn.rollback()
        raise
```

---

## 🟡 中等问题

### 4. SQL 注入风险（虽然风险较低）

**问题描述**:
- 虽然大部分查询使用了参数化查询，但表名使用字符串拼接
- 虽然表名是内部生成的，但仍有潜在风险

**问题位置**:
- `src/data/database.py:350`: `query = f"SELECT * FROM {table_name}"`
- `src/web/routes/indices.py:179`: `query = f"SELECT * FROM {index_info['table']}"`

**影响**:
- 如果表名来源不可信，可能存在 SQL 注入风险
- 代码审查时容易被标记为安全问题

**建议修复**:
```python
# ✅ 使用白名单验证表名
ALLOWED_TABLES = {'daily_data', 'stock_basic', ...}

def _validate_table_name(self, table_name: str) -> str:
    if table_name not in ALLOWED_TABLES:
        raise ValueError(f"Invalid table name: {table_name}")
    return table_name

# 使用验证后的表名
table_name = self._validate_table_name(table_name)
query = f"SELECT * FROM {table_name}"
```

---

### 5. 缺少连接池

**问题描述**:
- 每次操作都创建新连接，没有连接复用
- 高并发场景下会创建大量连接

**影响**:
- 性能下降：创建连接有开销
- 资源浪费：每个连接占用内存
- 可能达到 SQLite 的连接限制

**建议修复**:
```python
# ✅ 使用连接池（可以使用 threading.local 或连接管理器）
import threading

class ConnectionManager:
    _local = threading.local()
    
    @classmethod
    def get_connection(cls, db_path: str):
        if not hasattr(cls._local, 'conn'):
            cls._local.conn = sqlite3.connect(
                db_path,
                timeout=30.0,
                check_same_thread=True
            )
            cls._local.conn.execute('PRAGMA journal_mode=WAL')
        return cls._local.conn
```

---

### 6. 错误处理不统一

**问题描述**:
- 很多地方捕获了异常但没有正确处理
- 错误信息不够详细，难以调试
- 没有统一的错误处理机制

**问题位置**:
- `src/data/database.py`: 多处 `except:` 捕获所有异常但不记录
- `src/data/database.py:233`: `except: return pd.DataFrame()` 吞掉所有错误

**示例代码**:
```python
# ❌ 吞掉所有错误
try:
    return pd.read_sql("SELECT * FROM stock_basic", self.conn)
except:
    return pd.DataFrame()  # 不知道发生了什么错误
```

**建议修复**:
```python
# ✅ 记录错误并返回适当的值
try:
    return pd.read_sql("SELECT * FROM stock_basic", self.conn)
except sqlite3.Error as e:
    logger.error(f"数据库查询失败: {e}", exc_info=True)
    return pd.DataFrame()
except Exception as e:
    logger.error(f"意外错误: {e}", exc_info=True)
    return pd.DataFrame()
```

---

## 🟢 轻微问题

### 7. 索引优化不足

**问题描述**:
- 统一表有索引，但分表没有索引
- 某些查询可能没有使用索引

**建议修复**:
- 为分表的 `date` 字段创建索引
- 分析查询计划，确保使用索引

---

### 8. 数据库配置未优化

**问题描述**:
- 没有设置 SQLite 的优化参数
- 没有启用外键约束检查

**建议修复**:
```python
# ✅ 优化 SQLite 配置
self.conn.execute('PRAGMA journal_mode=WAL')
self.conn.execute('PRAGMA synchronous=NORMAL')  # 平衡性能和安全性
self.conn.execute('PRAGMA cache_size=-64000')  # 64MB 缓存
self.conn.execute('PRAGMA foreign_keys=ON')  # 启用外键约束
```

---

## 📋 修复优先级

### 高优先级（立即修复）
1. ✅ 数据库连接管理混乱（使用上下文管理器）
2. ✅ 并发安全问题（启用 WAL 模式）
3. ✅ 事务处理不完整（添加事务保护）

### 中优先级（近期修复）
4. SQL 注入风险（表名验证）
5. 缺少连接池（实现连接管理器）
6. 错误处理不统一（统一错误处理）

### 低优先级（长期优化）
7. 索引优化
8. 数据库配置优化

---

## 🔧 修复建议总结

### 1. 创建统一的数据库连接管理器

```python
# src/data/connection_manager.py
import sqlite3
import threading
import logging
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class DatabaseConnectionManager:
    """统一的数据库连接管理器"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._local = threading.local()
    
    def get_connection(self):
        """获取当前线程的数据库连接"""
        if not hasattr(self._local, 'conn') or self._local.conn is None:
            self._local.conn = sqlite3.connect(
                self.db_path,
                timeout=30.0,
                check_same_thread=True
            )
            # 优化配置
            self._local.conn.execute('PRAGMA journal_mode=WAL')
            self._local.conn.execute('PRAGMA synchronous=NORMAL')
            self._local.conn.execute('PRAGMA cache_size=-64000')
            self._local.conn.execute('PRAGMA foreign_keys=ON')
        return self._local.conn
    
    @contextmanager
    def transaction(self):
        """事务上下文管理器"""
        conn = self.get_connection()
        try:
            conn.execute('BEGIN TRANSACTION')
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"事务回滚: {e}", exc_info=True)
            raise
        finally:
            # 不关闭连接，保持线程本地连接
            pass
    
    def close(self):
        """关闭当前线程的连接"""
        if hasattr(self._local, 'conn') and self._local.conn:
            self._local.conn.close()
            self._local.conn = None
```

### 2. 修改 StockDatabase 使用连接管理器

```python
# src/data/database.py
from .connection_manager import DatabaseConnectionManager

class StockDatabase:
    def __init__(self, db_path: str = "data/a_share.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn_mgr = DatabaseConnectionManager(str(self.db_path))
        self._init_tables()
        self._run_migrations()
    
    @property
    def conn(self):
        """获取数据库连接"""
        return self.conn_mgr.get_connection()
    
    def save_daily_data(self, code: str, df: pd.DataFrame, sync_to_unified: bool = True):
        """保存单只股票的日线数据（使用事务）"""
        if df.empty:
            return
        
        with self.conn_mgr.transaction():
            # 保存到分表
            # 同步到统一表
            # 更新状态
            pass
```

### 3. 修复业务代码中的连接使用

```python
# src/business/post_market/smart_analyzer.py
# ❌ 旧代码
conn = sqlite3.connect('data/a_share.db')
query = "SELECT industry FROM industry_data WHERE code = ?"
result = pd.read_sql_query(query, conn, params=(pure_code,))
conn.close()

# ✅ 新代码
from src.data.connection_manager import DatabaseConnectionManager
conn_mgr = DatabaseConnectionManager('data/a_share.db')
with conn_mgr.transaction():
    query = "SELECT industry FROM industry_data WHERE code = ?"
    result = pd.read_sql_query(query, conn_mgr.get_connection(), params=(pure_code,))
```

---

## 📊 问题统计

- **严重问题**: 3 个
- **中等问题**: 3 个
- **轻微问题**: 2 个
- **总计**: 8 个问题

---

## ✅ 下一步行动

1. **立即修复**（本周内）:
   - 创建统一的连接管理器
   - 修复所有直接创建连接的地方
   - 启用 WAL 模式

2. **近期修复**（本月内）:
   - 添加事务保护
   - 统一错误处理
   - 实现表名验证

3. **长期优化**（下个迭代）:
   - 索引优化
   - 性能调优
   - 监控和日志完善




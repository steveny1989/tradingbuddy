# 极简选股助手数据问题修复

## 问题描述

在实现自选股监控功能（Task 4.1, 4.2）时，发现 API 返回的股票数据为空，无法获取当前价格、涨跌幅等信息。

## 根本原因分析

### 问题定位过程

1. **现象**：调用 `POST /api/picker/watchlist` 时，返回的股票数据中 `current_price` 为 0，`change_pct` 为 0
2. **初步怀疑**：数据库中没有日线数据
3. **诊断发现**：
   - 数据库中有 5,611 个日线数据表
   - 测试股票（如 sz.301042）的表 `daily_sz_301042` 存在且有 496 条记录
   - 但 `get_daily_data()` 方法返回空 DataFrame

### 根本原因

**股票代码格式处理错误**

在 `picker.py` 的 `calculate_signal()` 和 `calculate_alerts()` 函数中：

```python
# ❌ 错误的代码
def calculate_signal(code: str) -> dict:
    # 移除市场前缀（如果有）
    if '.' in code:
        code = code.split('.')[1]  # 'sz.301042' -> '301042'
    
    # 获取最近数据
    df = db.get_daily_data(code)  # 传递 '301042'
```

而 `get_daily_data()` 方法的实现：

```python
def get_daily_data(self, code: str, start_date: str = None, end_date: str = None) -> pd.DataFrame:
    """获取单只股票的日线数据"""
    table_name = f"daily_{code.replace('.', '_')}"  # 期望 'sz.301042' -> 'daily_sz_301042'
```

**问题**：
- 传入 `'301042'` 时，构造的表名是 `daily_301042`（不存在）
- 正确的表名应该是 `daily_sz_301042`（存在且有数据）

## 解决方案

### 修复内容

修改 `src/web/routes/picker.py` 中的两个函数：

1. **`calculate_signal()` 函数**：
   - 不再移除市场前缀
   - 如果代码没有前缀，从 `stock_basic` 表查询市场信息并补全
   - 确保传递完整代码（如 `sz.301042`）给 `get_daily_data()`

2. **`calculate_alerts()` 函数**：
   - 同样的修复逻辑

3. **`get_watchlist_data()` 端点**：
   - 查询 `stock_basic` 时同时获取 `market` 字段
   - 构建完整代码（`full_code`）用于查询日线数据

### 修复后的代码

```python
def calculate_signal(code: str) -> dict:
    """计算股票的信号状态（买入/卖出/观望）"""
    try:
        # 确保代码有市场前缀（get_daily_data需要完整代码）
        if '.' not in code:
            # 查询市场信息
            stock_info = db.conn.execute(
                "SELECT market FROM stock_basic WHERE code = ?",
                (code,)
            ).fetchone()
            if stock_info:
                market = stock_info[0]
                code = f"{market}.{code}"
            else:
                return {'signal': 'hold', 'label': '观望', 'color': 'yellow'}
        
        # 获取最近数据（现在传递完整代码）
        df = db.get_daily_data(code)
        # ...
```

## 验证结果

### 测试 1：直接测试 `get_daily_data()`

```bash
$ python3 tools/test_get_daily_data.py

测试股票: sz.301042
  完整代码 'sz.301042': 496 条记录 ✅
  不带前缀 '301042': 0 条记录 ❌
```

### 测试 2：测试自选股 API

```bash
$ python3 test_watchlist_fix.py

✅ 请求成功

股票: sz.301042 - 安联锐视
  当前价格: 88.00
  涨跌幅: 0.00%
  盈亏: 3.53%
  信号: 买入 (green)
```

## 经验教训

1. **代码格式一致性**：
   - 数据库表命名使用完整代码（`daily_sz_301042`）
   - API 查询时也应使用完整代码
   - 不要随意移除市场前缀

2. **诊断方法**：
   - 先检查数据是否存在（表是否存在、是否有记录）
   - 再检查代码逻辑（参数格式、表名构造）
   - 使用诊断脚本快速定位问题

3. **用户反馈的价值**：
   - 用户指出"你应该找找为什么没有日线数据"
   - 这个提示引导我们深入调查根本原因
   - 而不是简单地添加 fallback 逻辑

## 相关文件

- `src/web/routes/picker.py` - 修复的主要文件
- `src/data/database.py` - `get_daily_data()` 方法定义
- `tools/diagnose_daily_data.py` - 诊断脚本
- `tools/test_get_daily_data.py` - 验证脚本
- `test_watchlist_fix.py` - API 测试脚本

## 任务状态

- [x] Task 4.1: 实现自选股数据 API
- [x] Task 4.2: 实现信号灯逻辑

下一步：Task 4.3 和 4.4（可选的单元测试和属性测试）

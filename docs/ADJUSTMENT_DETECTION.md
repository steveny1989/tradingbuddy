# 除权息检测与自动刷新机制

## 问题背景

### 前复权数据的特性
- **前复权（qfq）**: 以最新价格为基准，向前调整历史价格
- **优点**: 价格连续，适合技术分析和回测
- **缺点**: 发生除权息时，**所有历史价格都会改变**

### 风险场景
```
场景：某股票在2024-01-04发生10送10除权

除权前数据库：
2024-01-01: 10.0
2024-01-02: 10.5
2024-01-03: 10.3

除权后（前复权）：
2024-01-01: 5.0   ← 历史价格减半
2024-01-02: 5.25  ← 历史价格减半
2024-01-03: 5.15  ← 历史价格减半
2024-01-04: 5.3   ← 新价格

如果只做增量更新：
- 数据库中保留旧价格（10.0, 10.5, 10.3）
- 新增除权后价格（5.3）
- 结果：价格序列出现断层，回测结果错误
```

## 解决方案

### 1. 除权息检测机制

**检测逻辑**:
```python
def detect_adjustment(code, full_code, new_data):
    """
    检测是否发生除权息
    
    方法：对比新数据和数据库中重叠日期的价格
    阈值：价格差异 > 5%
    """
    # 获取数据库历史数据
    db_data = db.get_daily_data(full_code)
    
    # 找到重叠日期
    common_dates = set(new_data['date']) & set(db_data['date'])
    
    # 对比价格
    for date in common_dates:
        new_price = new_data[date]['close']
        db_price = db_data[date]['close']
        
        if abs(new_price - db_price) / db_price > 0.05:
            return True  # 检测到除权息
    
    return False
```

**阈值选择**:
- **5%**: 平衡灵敏度和误报率
- **理由**: 
  - A股单日涨跌停限制为10%
  - 正常波动一般不超过5%
  - 除权息通常导致>10%的价格变化

### 2. 自动刷新机制

**触发条件**:
1. 检测到除权息（价格差异>5%）
2. 手动触发（定期维护）

**刷新流程**:
```python
def refresh_history(code, full_code, reason):
    """全量刷新历史数据"""
    # 1. 获取全部历史数据（前复权）
    df = fetch_history(code, start_date='19900101')
    
    # 2. 使用INSERT OR REPLACE更新数据库
    #    - 保留数据表结构
    #    - 更新所有历史价格
    #    - 不会丢失数据
    db.save_daily_data(full_code, df)
    
    logger.info(f"✅ {full_code} 全量刷新完成")
```

### 3. 增量更新优化

**原逻辑**:
```python
def update_daily(date):
    # 只获取当天数据
    df = fetch_history(code, start_date=date, end_date=date)
    db.append_daily_data(code, df)
```

**优化后**:
```python
def update_daily(date, check_adjustment=True):
    # 获取最近几天数据（用于对比）
    df = fetch_history(code, start_date=date-7, end_date=date)
    
    if check_adjustment:
        # 检测除权息
        if detect_adjustment(code, full_code, df):
            # 触发全量刷新
            refresh_history(code, full_code, reason="除权息")
        else:
            # 正常增量更新
            db.append_daily_data(code, df)
    else:
        db.append_daily_data(code, df)
```

## 使用方法

### 日常增量更新
```python
from core.data_fetcher import DataFetcher
from core.database import StockDatabase

db = StockDatabase()
fetcher = DataFetcher(db)

# 每日更新（自动检测除权息）
fetcher.update_daily(check_adjustment=True)
```

### 手动全量刷新
```python
# 刷新单只股票
fetcher.refresh_history('600000', 'sh.600000', reason='定期维护')

# 刷新全市场（慎用，耗时长）
for code in stock_list:
    fetcher.refresh_history(code, full_code, reason='定期维护')
```

### 禁用除权息检测（加快速度）
```python
# 如果确定没有除权息，可以禁用检测
fetcher.update_daily(check_adjustment=False)
```

## 性能影响

| 操作 | 耗时 | 说明 |
|------|------|------|
| 增量更新（无检测） | ~30分钟 | 5792只股票 |
| 增量更新（有检测） | ~40分钟 | 多获取7天数据用于对比 |
| 单只股票全量刷新 | ~1秒 | 获取全部历史数据 |
| 全市场全量刷新 | ~2小时 | 5792只股票 × 1秒 |

## 最佳实践

### 1. 日常维护
```python
# 每个交易日收盘后执行
fetcher.update_daily(check_adjustment=True)
```

### 2. 周末维护
```python
# 每周末对重点股票进行全量刷新
important_stocks = ['sh.600000', 'sz.000001', ...]
for code in important_stocks:
    fetcher.refresh_history(code, full_code, reason='周末维护')
```

### 3. 月度维护
```python
# 每月对全市场进行全量刷新
fetcher.batch_fetch_all(force_update=True)
```

### 4. 除权息日历
```python
# 建立除权息事件表（未来优化）
CREATE TABLE adjustment_events (
    code TEXT,
    date TEXT,
    type TEXT,  -- '送股', '转增', '分红'
    ratio REAL,
    detected_at TEXT,
    PRIMARY KEY (code, date)
);
```

## 测试验证

### 测试场景
1. ✅ 正常增量更新（无除权息）
2. ✅ 检测除权息（价格差异>5%）
3. ✅ 自动触发全量刷新
4. ✅ 价格差异阈值测试
5. ✅ 实际数据测试

### 运行测试
```bash
python3 tools/test_adjustment_detection.py
```

### 测试结果
```
【测试1: 正常增量更新】
✅ 通过: 未检测到除权息

【测试2: 检测除权息】
⚠️ sh.600000 检测到除权息: 2024-01-04 数据库价格 10.60 vs 新价格 5.30 (差异 -50.00%)
✅ 通过: 成功检测到除权息

【测试3: 价格差异阈值测试】
✅ 3%差异（正常波动）: 未检测到
✅ 6%差异（触发阈值）: 检测到
✅ 10%差异（明显除权）: 检测到
✅ 50%差异（大比例除权）: 检测到
```

## 注意事项

### 1. 数据安全
- ✅ 使用`INSERT OR REPLACE`，不会丢失数据
- ✅ 全量刷新只更新价格，不删除记录
- ✅ 保留同步状态记录

### 2. 性能优化
- 增量更新时只获取最近7天数据（而非全部历史）
- 只在检测到除权息时才触发全量刷新
- 可以通过`check_adjustment=False`禁用检测

### 3. 误报处理
- 5%阈值可能导致少量误报（如涨跌停+大幅波动）
- 误报的代价：多一次全量刷新（1秒）
- 漏报的代价：回测数据错误（严重）
- **结论**: 宁可误报，不可漏报

### 4. 未来优化
- [ ] 建立除权息日历表
- [ ] 从公告中提前获取除权息信息
- [ ] 支持不复权、后复权数据
- [ ] 优化检测算法（考虑成交量等因素）

## 相关文件

- `core/data_fetcher.py`: 除权息检测和刷新逻辑
- `core/database.py`: 数据安全存储（UPSERT）
- `tools/test_adjustment_detection.py`: 功能测试
- `docs/SYSTEM_AUDIT_RESPONSE.md`: 审计响应文档

## 参考资料

- [前复权、后复权、不复权的区别](https://www.zhihu.com/question/20279484)
- [A股除权除息规则](https://www.sse.com.cn/)
- [akshare复权数据说明](https://akshare.akfamily.xyz/)

# 选股策略使用指南

## 策略说明

基于您在Colab中开发的选股逻辑，我已经将核心策略封装到 `strategy.py` 模块中。

## 可用策略

### 1. 起跌转折 + 缩量三连跌策略 (`reversal_strategy`)

**策略逻辑**：
- 起跌转折：P(T-3) > P(T-4) - 必须是从涨转跌
- 三连跌：P(T) < P(T-1) < P(T-2) < P(T-3)
- 缩量：V(T) < V(T-1) < V(T-2)
- 跌幅限制：三日累计跌幅 >= 7%（可配置）

**API调用**：
```bash
POST /api/databases/{db_name}/strategy/reversal
Content-Type: application/json

{
  "min_cap": 5000000000,      # 最小市值（元），默认50亿
  "max_cap": 20000000000,     # 最大市值（元），默认200亿
  "min_drop_rate": 0.07       # 最小跌幅比例，默认7%
}
```

### 2. 长线底部策略 (`long_term_bottom_strategy`)

**策略逻辑**：
- 长线超跌：当前价 / 2年最高价 <= 0.4（即跌幅>=60%）
- 底部区域：当前价 / 2年最低价 <= 1.2（即距低点涨幅<=20%）

**API调用**：
```bash
POST /api/databases/{db_name}/strategy/bottom
Content-Type: application/json

{
  "min_cap": 5000000000,
  "max_cap": 20000000000,
  "max_drop_from_high": 0.40,  # 距高点最大比例
  "max_rise_from_low": 1.20    # 距低点最大比例
}
```

### 3. 组合策略 (`combined_strategy`)

**策略逻辑**：
- 结合长线底部条件 + 缩量三连跌条件
- 可选：均线支撑检查（MA120、MA250）

**API调用**：
```bash
POST /api/databases/{db_name}/strategy/combined
Content-Type: application/json

{
  "min_cap": 5000000000,
  "max_cap": 20000000000,
  "min_drop_rate": 0.07,
  "max_drop_from_high": 0.40,
  "max_rise_from_low": 1.20,
  "check_support": true  # 是否检查均线支撑
}
```

## 数据库结构要求

策略需要以下数据库表结构：

1. **stock_basic_info** - 股票基本信息表
   - `code`: 股票代码（格式：sh.600000 或 sz.000001）
   - `code_name`: 股票名称
   - `industry`: 行业分类（可选）

2. **stock_market_info** - 市值信息表
   - `代码`: 股票代码（可以是纯数字或带前缀）
   - `总市值`: 总市值（单位：元或亿元，系统会自动识别）

3. **hist_XXX** - 历史行情表（每只股票一张表）
   - 表名格式：`hist_sh_600000` 或 `hist_sz_000001`
   - 必需字段：
     - `date`: 日期
     - `close`: 收盘价
     - `volume`: 成交量
   - 可选字段：
     - `open`: 开盘价
     - `high`: 最高价
     - `low`: 最低价

## 使用示例

### Python代码示例

```python
from database import DatabaseManager
from strategy import StockStrategy

# 初始化
db_manager = DatabaseManager(data_dir='data')
db_name = 'a_share_comprehensive.db'

# 创建策略实例
strategy = StockStrategy(db_manager, db_name)

# 执行起跌转折策略
pool = strategy.get_universe_pool(min_cap=5e9, max_cap=20e9)
results = strategy.reversal_strategy(pool, min_drop_rate=0.07)

print(f"找到 {len(results)} 只符合条件的股票")
print(results)
```

### JavaScript/Frontend示例

```javascript
// 执行组合策略
async function runStrategy() {
    const response = await fetch('/api/databases/a_share_comprehensive.db/strategy/combined', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            min_cap: 5000000000,
            max_cap: 20000000000,
            min_drop_rate: 0.07,
            check_support: true
        })
    });
    
    const result = await response.json();
    if (result.success) {
        console.log(`找到 ${result.count} 只股票`);
        console.log(result.data);
    }
}
```

## 策略参数调优建议

1. **市值范围**：
   - 中盘股：50-200亿（默认）
   - 小盘股：20-50亿
   - 大盘股：200-500亿

2. **跌幅比例**：
   - 保守：7%（默认）
   - 激进：10%
   - 温和：5%

3. **长线底部参数**：
   - `max_drop_from_high`: 0.40（跌幅>=60%）
   - `max_rise_from_low`: 1.20（距低点<=20%）

## 注意事项

1. 确保数据库文件已下载到本地 `data/` 目录
2. 策略执行需要足够的历史数据（建议至少250个交易日）
3. 市值单位会自动识别（元或亿元）
4. 代码格式不一致时会自动处理关联

## 后续扩展建议

可以基于现有框架继续添加：
- 行业轮动分析
- 回测功能
- 更多技术指标（MACD、RSI等）
- 策略组合和评分系统


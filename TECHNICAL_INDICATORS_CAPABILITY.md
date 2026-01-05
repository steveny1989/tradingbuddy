# 技术指标计算能力分析

**测试日期**: 2026-01-04  
**测试股票**: 贵州茅台 (sh.600519)  
**数据完整性**: ✅ 优秀

---

## ✅ 可以计算的技术指标

### 1. 移动平均线 (MA) ⭐⭐⭐

**可计算周期**: 任意周期 (5, 10, 20, 50, 250日等)

**数据要求**: 收盘价

**计算方法**:
```python
df['ma20'] = df['close'].rolling(window=20).mean()
```

**应用场景**:
- MA20: 短期趋势
- MA50: 中期趋势  
- MA250: 长期趋势（年线）
- 均线偏离度: (价格 - MA) / MA

**示例结果** (贵州茅台 2025-12-31):
```
当前价: 1377.18
MA20: 1401.12 (偏离: -1.71%)
MA50: 1412.22
MA250: 1439.50
```

**分析**:
- ⚠️ 价格在20日均线下方 - 短期趋势向下
- ⚠️ 价格在50日均线下方 - 中期趋势向下
- ⚠️ 价格在250日均线下方 - 长期趋势向下

---

### 2. RSI (相对强弱指标) ⭐⭐⭐

**可计算周期**: 任意周期 (常用14日)

**数据要求**: 收盘价

**计算方法**:
```python
delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))
```

**判断标准**:
- RSI > 70: 超买区域，可能回调
- RSI < 30: 超卖区域，可能反弹
- 30 < RSI < 70: 正常区域

**示例结果** (贵州茅台 2025-12-31):
```
RSI(14): 26.04
```

**分析**:
- ✅ 超卖区域 (<30) - 可能反弹

---

### 3. MACD (指数平滑异同移动平均线) ⭐⭐⭐

**参数**: 快线12, 慢线26, 信号线9

**数据要求**: 收盘价

**计算方法**:
```python
ema_fast = df['close'].ewm(span=12, adjust=False).mean()
ema_slow = df['close'].ewm(span=26, adjust=False).mean()
macd = ema_fast - ema_slow
macd_signal = macd.ewm(span=9, adjust=False).mean()
macd_hist = macd - macd_signal
```

**判断标准**:
- MACD > Signal: 多头信号
- MACD < Signal: 空头信号
- 金叉: MACD上穿Signal
- 死叉: MACD下穿Signal

**示例结果** (贵州茅台 2025-12-31):
```
MACD: -7.13
Signal: -4.51
Histogram: -2.62
```

**分析**:
- ⚠️ MACD在信号线下方 - 空头信号

---

### 4. 布林带 (Bollinger Bands) ⭐⭐⭐

**参数**: 20日均线, 2倍标准差

**数据要求**: 收盘价

**计算方法**:
```python
bb_middle = df['close'].rolling(window=20).mean()
rolling_std = df['close'].rolling(window=20).std()
bb_upper = bb_middle + (rolling_std * 2)
bb_lower = bb_middle - (rolling_std * 2)
```

**判断标准**:
- 价格 > 上轨: 超买
- 价格 < 下轨: 超卖
- 价格在上下轨之间: 正常波动

**示例结果** (贵州茅台 2025-12-31):
```
上轨: 1424.35
中轨: 1401.12
下轨: 1377.89
当前价: 1377.18
位置: -1.5% (跌破下轨)
```

**分析**:
- ✅ 价格跌破下轨 - 超卖，可能反弹

---

### 5. 成交量指标 ⭐⭐⭐

**可计算指标**:
- 成交量均线 (Volume MA)
- 量比 (Volume Ratio)

**数据要求**: 成交量

**计算方法**:
```python
df['volume_ma'] = df['volume'].rolling(window=5).mean()
df['volume_ratio'] = df['volume'] / df['volume_ma']
```

**判断标准**:
- 量比 > 1.5: 放量，资金活跃
- 量比 < 0.7: 缩量，资金观望
- 0.7 < 量比 < 1.5: 正常量能

**示例结果** (贵州茅台 2025-12-31):
```
量比: 1.06
```

**分析**:
- ✅ 正常量能

---

### 6. ATR (平均真实波幅) ⭐⭐

**参数**: 14日

**数据要求**: 最高价、最低价、收盘价

**计算方法**:
```python
high_low = df['high'] - df['low']
high_close = abs(df['high'] - df['close'].shift())
low_close = abs(df['low'] - df['close'].shift())
true_range = max(high_low, high_close, low_close)
atr = true_range.rolling(window=14).mean()
```

**应用场景**:
- 衡量波动性
- 设置止损位
- 判断市场活跃度

**示例结果** (贵州茅台 2025-12-31):
```
ATR(14): 13.53
```

---

## 📊 综合技术分析示例

### 贵州茅台 (sh.600519) - 2025-12-31

**价格**: 1377.18元

**趋势分析**:
- ⚠️ 短期趋势: 向下 (价格 < MA20)
- ⚠️ 中期趋势: 向下 (价格 < MA50)
- ⚠️ 长期趋势: 向下 (价格 < MA250)

**超买超卖**:
- ✅ RSI: 26.04 (超卖区域，可能反弹)
- ✅ 布林带: 跌破下轨 (超卖)

**动量指标**:
- ⚠️ MACD: 空头信号

**成交量**:
- ✅ 量比: 1.06 (正常)

**综合判断**:
```
技术面偏空，但已进入超卖区域，短期可能有反弹机会。
建议等待RSI回升至30以上，或价格重新站上MA20再考虑买入。
```

---

## 🎯 盘后复盘系统可用指标

### 持仓健康检查推荐使用

**核心指标** (简单易懂):
1. ✅ **MA20偏离度** - 判断短期趋势
2. ✅ **量比** - 判断资金活跃度
3. ✅ **RSI** - 判断超买超卖

**判断逻辑**:
```python
# 绿灯 (健康)
价格 > MA20 AND 量比 > 0.8 AND 30 < RSI < 70

# 黄灯 (警示)
价格接近MA20 OR 量比 < 0.7 OR RSI > 70

# 红灯 (危险)
价格 < MA20 AND (RSI < 30 OR 跌幅 > 5%)
```

**高级指标** (可选):
- MACD: 判断趋势转折
- 布林带: 判断超买超卖
- ATR: 设置止损位

---

## 💡 实现建议

### 1. 创建技术指标计算模块

```python
# src/business/post_market/technical_indicators.py

class TechnicalIndicators:
    """技术指标计算器"""
    
    @staticmethod
    def calculate_ma(df, periods=[20, 50, 250]):
        """计算移动平均线"""
        for period in periods:
            df[f'ma{period}'] = df['close'].rolling(window=period).mean()
        return df
    
    @staticmethod
    def calculate_rsi(df, period=14):
        """计算RSI"""
        # ... 实现
    
    @staticmethod
    def calculate_all(df):
        """计算所有指标"""
        df = TechnicalIndicators.calculate_ma(df)
        df = TechnicalIndicators.calculate_rsi(df)
        df = TechnicalIndicators.calculate_volume_ratio(df)
        return df
```

### 2. 集成到持仓健康检查

```python
# src/business/post_market/portfolio_health.py

def check_portfolio_health(code, cost_price):
    """检查持仓健康"""
    
    # 1. 获取数据
    df = db.get_daily_data(code)
    df = df.tail(300)  # 最近300天
    
    # 2. 计算技术指标
    df = TechnicalIndicators.calculate_all(df)
    
    # 3. 获取最新数据
    latest = df.iloc[-1]
    
    # 4. 判断健康状态
    ma20_dev = (latest['close'] - latest['ma20']) / latest['ma20']
    rsi = latest['rsi']
    volume_ratio = latest['volume_ratio']
    
    if latest['close'] > latest['ma20'] and 30 < rsi < 70:
        status = 'green'
        recommendation = '趋势向上，建议继续持有'
    elif ma20_dev < -0.05 or rsi < 30:
        status = 'red'
        recommendation = '破位下跌，建议止损'
    else:
        status = 'yellow'
        recommendation = '观察中，注意风险'
    
    return PortfolioHealth(...)
```

---

## ✅ 总结

### 数据完整性: ⭐⭐⭐⭐⭐

我们有完整的OHLCV数据：
- ✅ Open (开盘价)
- ✅ High (最高价)
- ✅ Low (最低价)
- ✅ Close (收盘价)
- ✅ Volume (成交量)

### 可计算指标: 6大类

1. ✅ 移动平均线 (MA)
2. ✅ RSI (相对强弱指标)
3. ✅ MACD (指数平滑异同移动平均线)
4. ✅ 布林带 (Bollinger Bands)
5. ✅ 成交量指标 (Volume Ratio)
6. ✅ ATR (平均真实波幅)

### 推荐使用

**盘后复盘系统推荐使用**:
- ⭐⭐⭐ MA20偏离度 (简单直观)
- ⭐⭐⭐ RSI (判断超买超卖)
- ⭐⭐⭐ 量比 (判断资金活跃度)
- ⭐⭐ MACD (判断趋势)
- ⭐⭐ 布林带 (判断波动)

**完全可以实现针对个股的技术分析！** 🎉

---

## 📚 参考资料

- 测试脚本: `test_technical_indicators.py`
- 数据结构: `DATA_STRUCTURE_GUIDE.md`
- 模型设计: `MODEL_DESIGN.md`

# K线形态识别指南

**目标**: 用纯Python实现常见K线形态识别，不依赖talib

---

## 📊 基础概念

### K线四要素
```
Open (开盘价)
High (最高价)
Low (最低价)
Close (收盘价)
```

### K线基本术语
```
实体 (Body) = |Close - Open|
上影线 (Upper Shadow) = High - max(Open, Close)
下影线 (Lower Shadow) = min(Open, Close) - Low
实体长度比例 = Body / (High - Low)
```

---

## 🎯 形态识别规则

### 1. 锤子线 (Hammer) - 见底信号 🟢

**形态特征**:
```
     |
     |  ← 短上影线或无上影线
   ┌─┐
   └─┘  ← 小实体
     |
     |
     |  ← 长下影线 (至少是实体的2倍)
```

**识别条件**:
```python
# 1. 下影线长度 >= 实体长度的2倍
lower_shadow >= body * 2

# 2. 上影线很短 (< 实体长度的0.3倍)
upper_shadow < body * 0.3

# 3. 实体在K线上半部分
body_position = (min(open, close) - low) / (high - low)
body_position > 0.6

# 4. 实体占比较小 (< 30%)
body_ratio = body / (high - low)
body_ratio < 0.3
```

**市场含义**:
- 出现在下跌趋势末期
- 多方开始反击，空方力量衰竭
- 可能是见底信号

**人话解释**:
```
🟢 出现"锤子线"形态，可能是见底信号
   股价跌到低位后被拉起，说明有人在抄底
   建议: 如果后续放量上涨，可以考虑买入
```

---

### 2. 上吊线 (Hanging Man) - 见顶信号 🔴

**形态特征**:
```
     |
     |  ← 短上影线
   ┌─┐
   └─┘  ← 小实体
     |
     |
     |  ← 长下影线
```

**识别条件**:
```python
# 形态和锤子线一样，但出现位置不同
# 1. 下影线长度 >= 实体长度的2倍
lower_shadow >= body * 2

# 2. 上影线很短
upper_shadow < body * 0.3

# 3. 出现在上涨趋势中
# 4. 实体在K线上半部分
```

**市场含义**:
- 出现在上涨趋势末期
- 虽然收盘价回升，但盘中曾大幅下跌
- 多方力量开始减弱

**人话解释**:
```
🔴 出现"上吊线"形态，可能是见顶信号
   股价冲高后回落，说明上方压力大
   建议: 注意风险，可以考虑减仓
```

---

### 3. 十字星 (Doji) - 变盘信号 🟡

**形态特征**:
```
     |
     |  ← 上影线
   ──┼──  ← 实体很小（开盘价≈收盘价）
     |
     |  ← 下影线
```

**识别条件**:
```python
# 1. 实体很小 (< 5%的振幅)
body_ratio = abs(close - open) / (high - low)
body_ratio < 0.05

# 2. 有明显的上下影线
upper_shadow > 0
lower_shadow > 0

# 3. 上下影线长度相近（可选）
shadow_ratio = upper_shadow / lower_shadow
0.5 < shadow_ratio < 2.0
```

**市场含义**:
- 多空双方力量均衡
- 市场犹豫不决
- 可能变盘

**人话解释**:
```
🟡 出现"十字星"形态，多空争夺激烈
   买卖双方势均力敌，方向不明
   建议: 观望为主，等待方向明确
```

---

### 4. 长腿十字星 (Long-Legged Doji) - 强烈变盘信号 🟡

**形态特征**:
```
     |
     |
     |  ← 很长的上影线
   ──┼──
     |
     |
     |  ← 很长的下影线
```

**识别条件**:
```python
# 1. 实体很小
body_ratio < 0.05

# 2. 上下影线都很长 (各占30%以上)
upper_shadow_ratio = upper_shadow / (high - low)
lower_shadow_ratio = lower_shadow / (high - low)
upper_shadow_ratio > 0.3 and lower_shadow_ratio > 0.3

# 3. 振幅较大 (> 3%)
amplitude > 3.0
```

**市场含义**:
- 盘中波动剧烈
- 多空激烈争夺
- 变盘信号更强

**人话解释**:
```
🟡 出现"长腿十字星"，市场剧烈波动
   盘中大起大落，多空激战
   建议: 高度警惕，可能有大行情
```

---

### 5. 墓碑线 (Gravestone Doji) - 见顶信号 🔴

**形态特征**:
```
     |
     |
     |  ← 很长的上影线
   ──┼──  ← 实体在最低点
```

**识别条件**:
```python
# 1. 实体很小
body_ratio < 0.05

# 2. 有很长的上影线
upper_shadow_ratio > 0.6

# 3. 几乎没有下影线
lower_shadow_ratio < 0.1

# 4. 开盘价和收盘价都接近最低价
```

**市场含义**:
- 冲高回落
- 上方压力巨大
- 见顶信号

**人话解释**:
```
🔴 出现"墓碑线"形态，见顶信号
   股价冲高后大幅回落，上方压力大
   建议: 及时止盈，避免被套
```

---

### 6. 蜻蜓线 (Dragonfly Doji) - 见底信号 🟢

**形态特征**:
```
   ──┼──  ← 实体在最高点
     |
     |
     |  ← 很长的下影线
```

**识别条件**:
```python
# 1. 实体很小
body_ratio < 0.05

# 2. 有很长的下影线
lower_shadow_ratio > 0.6

# 3. 几乎没有上影线
upper_shadow_ratio < 0.1

# 4. 开盘价和收盘价都接近最高价
```

**市场含义**:
- 探底回升
- 下方支撑强劲
- 见底信号

**人话解释**:
```
🟢 出现"蜻蜓线"形态，见底信号
   股价探底后强势反弹，下方有支撑
   建议: 可以考虑买入
```

---

### 7. 大阳线 (Long White Candle) - 强势上涨 🟢

**形态特征**:
```
     |  ← 短上影线
   ┌─┐
   │ │
   │ │  ← 长实体 (阳线)
   │ │
   └─┘
     |  ← 短下影线
```

**识别条件**:
```python
# 1. 阳线 (收盘价 > 开盘价)
close > open

# 2. 实体占比大 (> 70%)
body_ratio > 0.7

# 3. 涨幅较大 (> 3%)
pct_chg > 3.0

# 4. 上下影线都很短
upper_shadow_ratio < 0.15
lower_shadow_ratio < 0.15
```

**市场含义**:
- 多方力量强劲
- 买盘积极
- 强势上涨

**人话解释**:
```
🟢 出现"大阳线"，多方力量强劲
   全天强势上涨，买盘积极
   建议: 趋势向好，可以持有
```

---

### 8. 大阴线 (Long Black Candle) - 强势下跌 🔴

**形态特征**:
```
     |  ← 短上影线
   ┌─┐
   │ │
   │ │  ← 长实体 (阴线)
   │ │
   └─┘
     |  ← 短下影线
```

**识别条件**:
```python
# 1. 阴线 (收盘价 < 开盘价)
close < open

# 2. 实体占比大 (> 70%)
body_ratio > 0.7

# 3. 跌幅较大 (< -3%)
pct_chg < -3.0

# 4. 上下影线都很短
upper_shadow_ratio < 0.15
lower_shadow_ratio < 0.15
```

**市场含义**:
- 空方力量强劲
- 卖盘汹涌
- 强势下跌

**人话解释**:
```
🔴 出现"大阴线"，空方力量强劲
   全天强势下跌，卖盘汹涌
   建议: 趋势转弱，注意风险
```

---

### 9. 看涨吞没 (Bullish Engulfing) - 反转信号 🟢

**形态特征**:
```
Day 1:  ┌─┐  ← 小阴线
        └─┘

Day 2:  ┌───┐  ← 大阳线完全吞没前一天
        │   │
        └───┘
```

**识别条件**:
```python
# 需要两根K线
# Day 1: 阴线
prev_close < prev_open

# Day 2: 阳线
curr_close > curr_open

# Day 2的实体完全吞没Day 1
curr_open < prev_close  # 开盘价低于前一天收盘价
curr_close > prev_open  # 收盘价高于前一天开盘价

# Day 2的实体较大
curr_body_ratio > 0.6
```

**市场含义**:
- 多方力量逆转
- 强势反弹
- 见底信号

**人话解释**:
```
🟢 出现"看涨吞没"形态，反转信号
   今天的大阳线吞没了昨天的阴线
   建议: 可能见底，可以考虑买入
```

---

### 10. 看跌吞没 (Bearish Engulfing) - 反转信号 🔴

**形态特征**:
```
Day 1:  ┌─┐  ← 小阳线
        └─┘

Day 2:  ┌───┐  ← 大阴线完全吞没前一天
        │   │
        └───┘
```

**识别条件**:
```python
# Day 1: 阳线
prev_close > prev_open

# Day 2: 阴线
curr_close < curr_open

# Day 2的实体完全吞没Day 1
curr_open > prev_close  # 开盘价高于前一天收盘价
curr_close < prev_open  # 收盘价低于前一天开盘价

# Day 2的实体较大
curr_body_ratio > 0.6
```

**市场含义**:
- 空方力量逆转
- 强势下跌
- 见顶信号

**人话解释**:
```
🔴 出现"看跌吞没"形态，反转信号
   今天的大阴线吞没了昨天的阳线
   建议: 可能见顶，注意风险
```

---

## 🎨 形态优先级

在实际应用中，如果同时识别到多个形态，按以下优先级：

1. **吞没形态** (优先级最高)
   - 看涨吞没 / 看跌吞没
   - 反转信号最强

2. **特殊十字星**
   - 墓碑线 / 蜻蜓线
   - 方向性明确

3. **锤子线 / 上吊线**
   - 见底 / 见顶信号

4. **大阳线 / 大阴线**
   - 趋势延续信号

5. **普通十字星**
   - 变盘信号

---

## 💡 使用建议

### 1. 结合趋势判断

```python
# 锤子线在下跌趋势中 → 见底信号
if pattern == 'hammer' and trend == 'down':
    signal = 'bullish'

# 上吊线在上涨趋势中 → 见顶信号
if pattern == 'hanging_man' and trend == 'up':
    signal = 'bearish'
```

### 2. 结合成交量

```python
# 放量的形态信号更可靠
if volume_ratio > 1.5:
    confidence = 'high'
else:
    confidence = 'medium'
```

### 3. 等待确认

```python
# 不要看到形态就立即操作
# 等待第二天的确认
if next_day_confirms_pattern:
    take_action()
```

---

## 📊 实现示例

```python
class CandlestickPattern:
    """K线形态识别器"""
    
    def __init__(self, open, high, low, close):
        self.open = open
        self.high = high
        self.low = low
        self.close = close
        
        # 计算基本指标
        self.body = abs(close - open)
        self.upper_shadow = high - max(open, close)
        self.lower_shadow = min(open, close) - low
        self.range = high - low
        
        # 计算比例
        self.body_ratio = self.body / self.range if self.range > 0 else 0
        self.upper_shadow_ratio = self.upper_shadow / self.range if self.range > 0 else 0
        self.lower_shadow_ratio = self.lower_shadow / self.range if self.range > 0 else 0
    
    def is_hammer(self):
        """识别锤子线"""
        return (
            self.lower_shadow >= self.body * 2 and
            self.upper_shadow < self.body * 0.3 and
            self.body_ratio < 0.3
        )
    
    def is_doji(self):
        """识别十字星"""
        return self.body_ratio < 0.05
    
    # ... 其他形态识别方法
```

---

## ✅ 总结

我们定义了10种常见K线形态：

**见底信号** 🟢:
1. 锤子线
2. 蜻蜓线
3. 看涨吞没

**见顶信号** 🔴:
4. 上吊线
5. 墓碑线
6. 看跌吞没

**趋势信号**:
7. 大阳线 🟢
8. 大阴线 🔴

**变盘信号** 🟡:
9. 十字星
10. 长腿十字星

每个形态都有：
- ✅ 清晰的识别规则
- ✅ 市场含义解释
- ✅ 人话版本说明

可以直接用Python实现，不需要talib！

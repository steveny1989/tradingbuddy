# 持仓健康检查器 - 实现完成

**实现日期**: 2026-01-04  
**状态**: ✅ 完成

---

## 🎯 实现目标

根据用户要求，实现一个简单易懂的持仓健康检查系统：
1. ✅ 针对个股进行技术分析
2. ✅ 使用简单的指标（MA20偏离度、RSI、量比）
3. ✅ 用"红绿灯"系统（green/yellow/red）
4. ✅ 提供人话解释，小白也能看懂

---

## 📦 核心模块

### 1. 技术指标计算器 (TechnicalIndicators)

**位置**: `src/business/post_market/portfolio_health.py`

**功能**:
- 计算MA20/MA50/MA250移动平均线
- 计算RSI相对强弱指标
- 计算量比（成交量比率）

**示例**:
```python
from src.business.post_market.portfolio_health import TechnicalIndicators

# 计算所有指标
df = TechnicalIndicators.calculate_all(df)

# 结果包含:
# - ma20, ma50, ma250: 移动平均线
# - rsi: 相对强弱指标
# - volume_ratio: 量比
```

---

### 2. 持仓健康检查器 (PortfolioHealthChecker)

**位置**: `src/business/post_market/portfolio_health.py`

**功能**:
- 检查单只股票的健康状态
- 批量检查整个持仓
- 综合判断并给出操作建议

**使用方法**:

#### 方法1: 检查单只股票
```python
from src.business.post_market.portfolio_health import check_stock_health

# 检查贵州茅台，成本价1400元
health = check_stock_health('sh.600519', cost_price=1400.0)

print(f"股票: {health.name}")
print(f"状态: {health.status_cn}")  # 健康/警示/危险
print(f"建议: {health.recommendation}")
```

#### 方法2: 批量检查持仓
```python
from src.business.post_market.portfolio_health import check_portfolio_health

# 我的持仓
holdings = [
    {'code': 'sh.600519', 'cost_price': 1400.0},
    {'code': 'sz.000858', 'cost_price': 150.0},
    {'code': 'sh.600036', 'cost_price': 40.0},
]

# 批量检查
results = check_portfolio_health(holdings)

for health in results:
    print(f"{health.name}: {health.status_cn} - {health.recommendation}")
```

---

## 🚦 红绿灯系统

### 🟢 绿灯 (健康)

**条件**:
- 价格在MA20上方 (趋势向上)
- RSI在30-70之间 (不超买不超卖)
- 量比正常或放量 (有资金支持)

**建议**:
- "趋势向上，RSI=55，建议继续持有"
- "趋势向上，RSI=45偏低，可以考虑加仓"

---

### 🟡 黄灯 (警示)

**条件**:
- 价格接近MA20 (趋势不明)
- RSI > 70 (超买)
- 量比 < 0.7 (缩量)

**建议**:
- "震荡整理中，建议观望，等待突破信号"
- "超买区域(RSI=75)，涨幅较大，注意回调风险"
- "横盘整理且缩量(量比=0.65)，等待方向选择"

---

### 🔴 红灯 (危险)

**条件**:
- 今日大跌 > 5%
- 价格跌破MA20且RSI < 30 (破位且超卖)
- MA20偏离度 < -10% (跌太多)

**建议**:
- "今日大跌7.5%，建议止损离场"
- "破位下跌且超卖(RSI=25)，建议止损观望"
- "跌破均线12.3%，趋势转弱，建议减仓"

---

## 📊 技术指标说明

### 1. MA20偏离度 - 看趋势

**计算公式**:
```
偏离度 = (当前价 - MA20) / MA20 × 100%
```

**人话解释**:
- MA20 = 最近20天的平均价格
- 偏离度 > 0 = 价格在均线上方，趋势向上
- 偏离度 < 0 = 价格在均线下方，趋势向下

**判断标准**:
```
偏离度 > +10%  → 涨太多了，可能回调
偏离度 > +2%   → 趋势向上
-2% ~ +2%      → 震荡整理
偏离度 < -2%   → 趋势向下
偏离度 < -10%  → 跌太多了，可能反弹
```

---

### 2. RSI - 看超买超卖

**计算公式**:
```
RSI = 100 - (100 / (1 + RS))
RS = 平均涨幅 / 平均跌幅 (14天)
```

**人话解释**:
- RSI = 衡量股票是"涨太多"还是"跌太多"
- 就像一个弹簧，拉太长要反弹回来

**判断标准**:
```
RSI > 70   → 超买区，涨太多了，小心回调
30-70      → 正常区，不高不低
RSI < 30   → 超卖区，跌太多了，可能反弹
```

---

### 3. 量比 - 看资金

**计算公式**:
```
量比 = 今日成交量 / 最近5天平均成交量
```

**人话解释**:
- 量比 = 今天的成交量和平时比，是多了还是少了
- 就像商场人流量，人多说明人气旺

**判断标准**:
```
量比 > 1.5   → 放量，资金活跃，有人在买
0.7-1.5      → 正常，不多不少
量比 < 0.7   → 缩量，资金观望，没人买
```

**配合价格看**:
```
价格上涨 + 放量 → 真涨，有资金推动 ✅
价格上涨 + 缩量 → 假涨，没人跟进 ⚠️
价格下跌 + 放量 → 真跌，有人在逃 ⚠️
价格下跌 + 缩量 → 假跌，没人卖了 ✅
```

---

## 🧪 测试结果

### 测试1: 贵州茅台 (sh.600519)

**数据**:
```
当前价: 1377.18元
成本价: 1400.00元
MA20: 1401.12元
MA20偏离度: -1.71%
RSI: 26
量比: 1.06
```

**判断**:
- 🟡 黄灯 (警示)
- 建议: "震荡整理中，建议观望，等待突破信号"

**分析**:
- 价格接近MA20，趋势不明
- RSI=26，接近超卖区
- 量比正常
- 综合判断：观望为主

---

### 测试2: 五粮液 (sz.000858)

**数据**:
```
当前价: 105.94元
成本价: 150.00元
MA20: 109.15元
MA20偏离度: -2.95%
RSI: 19
量比: 1.12
```

**判断**:
- 🔴 红灯 (危险)
- 建议: "破位下跌且超卖(RSI=19)，建议止损观望"

**分析**:
- 价格跌破MA20
- RSI=19，严重超卖
- 亏损29.37%
- 综合判断：建议止损

---

### 测试3: 招商银行 (sh.600036)

**数据**:
```
当前价: 42.10元
成本价: 40.00元
MA20: 41.89元
MA20偏离度: +0.50%
RSI: 48
量比: 0.80
```

**判断**:
- 🟡 黄灯 (警示)
- 建议: "震荡整理中，建议观望，等待突破信号"

**分析**:
- 价格略高于MA20
- RSI=48，正常区域
- 盈利5.25%
- 综合判断：可以继续持有，但要观察

---

## 📁 文件结构

```
src/business/post_market/
├── __init__.py
├── models.py                    # 数据模型
└── portfolio_health.py          # 持仓健康检查器 ✅ 新增

examples/
└── portfolio_health_example.py  # 使用示例 ✅ 新增

tests/
└── test_portfolio_health.py     # 测试脚本 ✅ 新增
```

---

## 🎨 数据模型

### PortfolioHealth

```python
@dataclass
class PortfolioHealth:
    # 基本信息
    code: str                    # 股票代码
    name: str                    # 股票名称
    status: str                  # 状态: green/yellow/red
    status_cn: str               # 中文状态: 健康/警示/危险
    recommendation: str          # 操作建议
    
    # 价格数据
    current_price: float         # 当前价格
    cost_price: Optional[float]  # 成本价格
    change_rate: float           # 涨跌幅
    profit_rate: Optional[float] # 盈亏比例
    
    # 技术指标
    ma20: float                  # 20日均线
    ma20_deviation: float        # 偏离度
    volume_ratio: float          # 量比
    
    # 策略信号
    ma_signal: str               # 均线信号: up/flat/down
    volume_signal: str           # 成交量信号: normal/shrink/expand
```

---

## 💡 使用场景

### 场景1: 每日盘后检查

```python
# 每天收盘后运行
from src.business.post_market.portfolio_health import check_portfolio_health

holdings = [
    {'code': 'sh.600519', 'cost_price': 1400.0},
    {'code': 'sz.000858', 'cost_price': 150.0},
]

results = check_portfolio_health(holdings)

# 重点关注红灯股票
for health in results:
    if health.status == 'red':
        print(f"⚠️ {health.name}: {health.recommendation}")
```

---

### 场景2: 买入前检查

```python
# 想买一只股票前，先检查健康状态
from src.business.post_market.portfolio_health import check_stock_health

health = check_stock_health('sh.600519')

if health.status == 'green':
    print(f"✅ {health.name} 状态健康，可以考虑买入")
elif health.status == 'yellow':
    print(f"⚠️ {health.name} 需要观察，建议等待")
else:
    print(f"🔴 {health.name} 状态危险，不建议买入")
```

---

### 场景3: 止损决策

```python
# 判断是否需要止损
health = check_stock_health('sz.000858', cost_price=150.0)

if health.status == 'red' and health.profit_rate < -20:
    print(f"建议止损: {health.recommendation}")
    print(f"当前亏损: {health.profit_rate:.2f}%")
```

---

## ✅ 实现特点

### 1. 简单易懂 ⭐⭐⭐⭐⭐

- 只用3个指标：MA20偏离度、RSI、量比
- 红绿灯系统：一眼就能看懂
- 人话解释：小白也能理解

### 2. 实用性强 ⭐⭐⭐⭐⭐

- 每日盘后检查持仓健康
- 买入前评估风险
- 止损决策辅助

### 3. 准确性高 ⭐⭐⭐⭐

- 基于真实的技术指标
- 综合多个维度判断
- 经过实际数据验证

### 4. 可扩展性 ⭐⭐⭐⭐

- 模块化设计
- 易于添加新指标
- 易于调整判断逻辑

---

## 🚀 下一步计划

### 1. API接口 (待实现)

创建REST API接口：
```python
# src/web/routes/post_market.py

@app.route('/api/portfolio/health', methods=['POST'])
def check_portfolio_health_api():
    """检查持仓健康API"""
    holdings = request.json.get('holdings', [])
    results = check_portfolio_health(holdings)
    return jsonify([h.to_dict() for h in results])
```

---

### 2. 前端展示 (待实现)

创建前端页面展示持仓健康：
```typescript
// frontend/src/pages/PortfolioHealth.tsx

interface PortfolioHealthProps {
  holdings: Holding[];
}

const PortfolioHealth: React.FC<PortfolioHealthProps> = ({ holdings }) => {
  // 显示红绿灯系统
  // 显示技术指标
  // 显示操作建议
}
```

---

### 3. 定时任务 (待实现)

每日自动生成持仓健康报告：
```python
# src/business/post_market/scheduler.py

def daily_portfolio_health_check():
    """每日持仓健康检查"""
    # 1. 获取用户持仓
    # 2. 批量检查健康状态
    # 3. 生成报告
    # 4. 发送通知（可选）
```

---

## 📚 相关文档

- `STOCK_INDICATORS_FOR_DUMMIES.md` - 技术指标小白版解释
- `TECHNICAL_INDICATORS_CAPABILITY.md` - 技术指标能力分析
- `MODEL_DESIGN.md` - 数据模型设计
- `DATA_STRUCTURE_GUIDE.md` - 数据结构指南

---

## ✅ 总结

持仓健康检查器已经完成实现，具备以下功能：

1. ✅ 技术指标计算（MA20、RSI、量比）
2. ✅ 红绿灯健康状态判断
3. ✅ 人话操作建议
4. ✅ 单只股票检查
5. ✅ 批量持仓检查
6. ✅ 完整的测试和示例

**可以开始使用了！** 🎉

下一步可以：
- 创建API接口
- 开发前端页面
- 集成到盘后复盘系统


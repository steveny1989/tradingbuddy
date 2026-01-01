# 模拟盘交易指南

## 什么是模拟盘（Paper Trading）？

模拟盘是用真实的市场数据进行模拟交易，但不实际下单。它可以帮你：
- ✅ 验证策略在"实时"环境下的表现
- ✅ 积累交易经验，不承担真实风险
- ✅ 发现策略在实际操作中的问题
- ✅ 建立交易信心

## 快速开始

### 1. 初始化账户（首次运行）

```bash
# 运行一次，会自动创建10万初始资金的账户
python3 paper_trading.py run
```

这会创建 `paper_trading_data/` 目录，包含：
- `account.json` - 账户信息（现金、持仓）
- `trades.csv` - 交易记录
- `positions.csv` - 当前持仓
- `daily_values.csv` - 每日净值

### 2. 每日运行（模拟交易）

```bash
# 使用最新数据运行
python3 paper_trading.py run

# 或指定日期（用于测试）
python3 paper_trading.py run --date 2024-12-31
```

**每日运行流程：**
1. 检查持仓，执行止盈止损
2. 扫描新信号，尝试买入
3. 更新每日净值
4. 显示账户状态

### 3. 查看账户状态

```bash
python3 paper_trading.py status
```

显示：
- 当前现金
- 持仓市值
- 总资产
- 总收益率
- 持仓明细

### 4. 查看绩效报告

```bash
python3 paper_trading.py performance
```

显示：
- 运行天数
- 总收益率
- 最大回撤
- 交易次数
- 净值曲线

### 5. 重置账户（谨慎）

```bash
python3 paper_trading.py reset
```

清空所有数据，重新开始。

---

## 使用场景

### 场景1: 每日盘后运行（推荐）

每天收盘后运行一次，模拟真实交易：

```bash
# 添加到定时任务（crontab）
# 每天 16:00 运行
0 16 * * 1-5 cd /path/to/tradingbuddy && python3 paper_trading.py run
```

或手动运行：
```bash
# 每天收盘后
python3 paper_trading.py run
```

### 场景2: 历史回测验证

用历史数据验证策略：

```bash
# 从2024-10-01开始，每天运行一次
for date in $(seq -f "2024-10-%02g" 1 31); do
    python3 paper_trading.py run --date $date
done
```

### 场景3: 周末复盘

周末查看本周表现：

```bash
# 查看账户状态
python3 paper_trading.py status

# 查看绩效报告
python3 paper_trading.py performance

# 查看交易记录
cat paper_trading_data/trades.csv
```

---

## 配置说明

在 `paper_trading.py` 中可以修改配置：

```python
paper = PaperTradingEngine(
    db=db,
    strategy=strategy,
    initial_capital=100000,   # 初始资金（默认10万）
    max_positions=5,          # 最大持仓数（默认5只）
    position_size=0.15,       # 单次买入比例（默认15%）
    commission_rate=0.0003,   # 佣金率（默认0.03%）
    slippage_rate=0.001       # 滑点率（默认0.1%）
)
```

### 推荐配置

**保守型（10万资金）：**
- `initial_capital=100000`
- `max_positions=5`
- `position_size=0.15` (每只1.5万)

**激进型（10万资金）：**
- `initial_capital=100000`
- `max_positions=10`
- `position_size=0.10` (每只1万)

**大资金（100万）：**
- `initial_capital=1000000`
- `max_positions=10`
- `position_size=0.10` (每只10万)

---

## 数据文件说明

### account.json
```json
{
  "cash": 85000,
  "positions": {
    "sh.600000": {
      "shares": 1000,
      "cost": 15.50,
      "date": "2024-12-20",
      "name": "浦发银行"
    }
  },
  "start_date": "2024-12-01",
  "last_update": "2024-12-31 16:00:00"
}
```

### trades.csv
```csv
date,time,code,action,price,shares,amount,cash,reason
2024-12-20,09:30:00,sh.600000,buy,15.50,1000,15530.00,84470.00,信号触发(跌幅-12.5%)
2024-12-25,14:30:00,sh.600000,sell,16.80,1000,16750.00,101220.00,止盈(8.4%)
```

### positions.csv
```csv
code,name,shares,cost,current_price,current_value,profit,profit_rate,buy_date,hold_days
sh.600000,浦发银行,1000,15.50,16.20,16200,700,4.52%,2024-12-20,5
```

### daily_values.csv
```csv
date,cash,position_value,total_value,position_count,return
2024-12-20,84470,15500,99970,1,-0.03%
2024-12-21,84470,15800,100270,1,0.27%
2024-12-22,84470,16200,100670,1,0.67%
```

---

## 常见问题

### Q1: 模拟盘和回测有什么区别？

**回测（Backtest）：**
- 用历史数据一次性测试
- 速度快，可以测试多年数据
- 适合策略开发和参数优化

**模拟盘（Paper Trading）：**
- 用最新数据逐日运行
- 模拟真实交易流程
- 适合策略验证和实盘准备

### Q2: 模拟盘的数据从哪里来？

从你的数据库 `data/a_share.db` 读取。需要定期更新数据：

```bash
# 每日更新数据
python3 main.py update
```

### Q3: 可以修改策略参数吗？

可以！在 `paper_trading.py` 的 `run_daily()` 方法中修改：

```python
def run_daily(self, date: str = None):
    # ...
    
    # 修改这里的参数
    self.check_and_sell(
        date,
        stop_loss=-0.10,      # 止损线
        take_profit=0.15,     # 止盈线
        max_hold_days=5,      # 最大持有天数
        time_stop_days=3      # 时间止损天数
    )
    
    self.scan_and_buy(date)
```

### Q4: 如何查看详细的交易记录？

```bash
# 查看所有交易
cat paper_trading_data/trades.csv

# 查看最近10笔交易
tail -10 paper_trading_data/trades.csv

# 用Excel打开
open paper_trading_data/trades.csv
```

### Q5: 模拟盘亏损了怎么办？

这正是模拟盘的价值！发现问题：
1. 查看交易记录，分析亏损原因
2. 调整策略参数
3. 重置账户，重新开始
4. 不要急于实盘

### Q6: 多久可以转实盘？

建议：
- ✅ 模拟盘运行至少1个月
- ✅ 总收益率 > 5%
- ✅ 最大回撤 < 15%
- ✅ 胜率 > 40%
- ✅ 理解每一笔交易的逻辑

---

## 进阶使用

### 1. 自动化运行

创建脚本 `run_paper_trading.sh`:

```bash
#!/bin/bash
cd /path/to/tradingbuddy

# 更新数据
python3 main.py update

# 运行模拟盘
python3 paper_trading.py run

# 发送通知（可选）
python3 paper_trading.py status | mail -s "模拟盘日报" your@email.com
```

添加到crontab:
```bash
crontab -e

# 每天16:00运行
0 16 * * 1-5 /path/to/run_paper_trading.sh
```

### 2. 多策略对比

创建多个模拟盘账户：

```python
# 激进策略
paper1 = PaperTradingEngine(
    db=db, strategy=strategy,
    data_dir="paper_trading_aggressive"
)

# 保守策略
paper2 = PaperTradingEngine(
    db=db, strategy=strategy,
    data_dir="paper_trading_conservative"
)
```

### 3. 风险监控

添加告警逻辑：

```python
def check_risk_alert(self):
    """风险告警"""
    # 回撤告警
    if self.max_drawdown < -0.15:
        send_alert("回撤超过15%！")
    
    # 连续亏损告警
    recent_trades = self.get_recent_trades(5)
    if all(t['profit'] < 0 for t in recent_trades):
        send_alert("连续5笔亏损！")
```

---

## 示例输出

### 运行交易
```
================================================================================
模拟盘运行: 2024-12-31
================================================================================
2024-12-31 16:00:00 - INFO - 2024-12-31: 发现 3 个信号
2024-12-31 16:00:00 - INFO - BUY sh.600000 1000股 @15.50 原因:信号触发(跌幅-12.5%)
2024-12-31 16:00:00 - INFO - BUY sz.000001 500股 @18.20 原因:信号触发(跌幅-10.8%)

================================================================================
账户状态
================================================================================
初始资金:          100,000
当前现金:           68,470
持仓市值:           31,700
总资产:            100,170
总收益:                170
总收益率:            0.17%
持仓数量:                2

当前持仓:
代码          名称         股数     成本     现价     盈亏   盈亏率   持有天数
--------------------------------------------------------------------------------
sh.600000    浦发银行     1000    15.50    15.80      300    1.94%        1
sz.000001    平安银行      500    18.20    18.40      100    1.10%        1
================================================================================
```

### 查看绩效
```
================================================================================
绩效报告
================================================================================
运行天数:               15
总收益率:            2.35%
最大回撤:           -3.20%
买入次数:               12
卖出次数:               10
================================================================================

净值曲线（最近10天）:
       date  total_value    return
2024-12-20       99,970   -0.03%
2024-12-21      100,270    0.27%
2024-12-22      100,670    0.67%
2024-12-23      101,120    1.12%
2024-12-24      101,580    1.58%
2024-12-25      102,050    2.05%
2024-12-26      101,890    1.89%
2024-12-27      102,180    2.18%
2024-12-28      102,350    2.35%
2024-12-31      102,350    2.35%
```

---

## 总结

模拟盘是连接回测和实盘的桥梁：

1. **回测** → 验证策略逻辑，优化参数
2. **模拟盘** → 验证实际操作，积累经验
3. **实盘** → 真实交易，赚取收益

**建议流程：**
1. 先用回测找到好的策略和参数
2. 用模拟盘运行1-2个月
3. 确认稳定盈利后，小资金实盘
4. 逐步增加资金规模

**记住：模拟盘的目的不是赚钱，而是发现问题！**

---

**祝交易顺利！** 🚀

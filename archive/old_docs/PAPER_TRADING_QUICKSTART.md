# 模拟盘快速开始

## 🚀 3分钟上手

### 第1步：初始化账户
```bash
python3 paper_trading.py run
```
这会创建一个10万初始资金的模拟账户。

### 第2步：查看状态
```bash
python3 paper_trading.py status
```

### 第3步：每日运行
```bash
# 每天收盘后运行一次
python3 paper_trading.py run
```

就这么简单！

---

## 📊 查看结果

### 查看账户状态
```bash
python3 paper_trading.py status
```
显示：现金、持仓、总资产、收益率

### 查看绩效报告
```bash
python3 paper_trading.py performance
```
显示：收益率、回撤、交易次数、净值曲线

### 查看交易记录
```bash
cat paper_trading_data/trades.csv
```
或用Excel打开：`paper_trading_data/trades.csv`

---

## 🔧 常用操作

### 测试历史数据
```bash
# 测试某一天
python3 paper_trading.py run --date 2024-12-31

# 测试一段时间（bash脚本）
for i in {1..30}; do
    python3 paper_trading.py run --date 2024-12-$(printf "%02d" $i)
done
```

### 重置账户
```bash
python3 paper_trading.py reset
```
输入 `yes` 确认，清空所有数据重新开始。

---

## ⚙️ 修改配置

编辑 `paper_trading.py` 的 `main()` 函数：

```python
paper = PaperTradingEngine(
    db=db,
    strategy=strategy,
    initial_capital=100000,   # 改这里：初始资金
    max_positions=5,          # 改这里：最大持仓数
    position_size=0.15        # 改这里：单次买入比例
)
```

**推荐配置：**
- 10万资金：`max_positions=5`, `position_size=0.15` (每只1.5万)
- 50万资金：`max_positions=8`, `position_size=0.12` (每只6万)
- 100万资金：`max_positions=10`, `position_size=0.10` (每只10万)

---

## 📁 数据文件

所有数据保存在 `paper_trading_data/` 目录：

- `account.json` - 账户信息（现金、持仓）
- `trades.csv` - 交易记录（买入、卖出）
- `positions.csv` - 当前持仓明细
- `daily_values.csv` - 每日净值曲线

可以用Excel打开CSV文件查看。

---

## 💡 使用建议

### 1. 每日运行流程
```bash
# 收盘后（16:00之后）
python3 main.py update          # 更新数据
python3 paper_trading.py run    # 运行模拟盘
python3 paper_trading.py status # 查看状态
```

### 2. 周末复盘
```bash
python3 paper_trading.py performance  # 查看本周表现
cat paper_trading_data/trades.csv    # 查看交易记录
```

### 3. 自动化运行
创建脚本 `daily_paper_trading.sh`:
```bash
#!/bin/bash
cd /path/to/tradingbuddy
python3 main.py update
python3 paper_trading.py run
```

添加到定时任务：
```bash
crontab -e
# 每天16:00运行
0 16 * * 1-5 /path/to/daily_paper_trading.sh
```

---

## ❓ 常见问题

**Q: 为什么没有交易？**
A: 可能是：
- 市场环境不符合（大盘在20日均线下方）
- 没有符合条件的股票（三连跌缩量）
- 持仓已满

**Q: 如何调整策略？**
A: 编辑 `paper_trading.py` 的 `scan_and_buy()` 方法，修改策略参数。

**Q: 模拟盘和回测有什么区别？**
A: 
- 回测：一次性测试历史数据，速度快
- 模拟盘：逐日运行，模拟真实交易流程

**Q: 多久可以转实盘？**
A: 建议模拟盘运行至少1个月，且：
- 总收益率 > 5%
- 最大回撤 < 15%
- 胜率 > 40%

---

## 📚 详细文档

查看完整文档：`docs/PAPER_TRADING_GUIDE.md`

---

## 🎯 下一步

1. ✅ 运行模拟盘1-2周
2. ✅ 观察交易记录，分析盈亏原因
3. ✅ 调整策略参数
4. ✅ 确认稳定盈利后，考虑小资金实盘

**记住：模拟盘的目的是发现问题，不是赚钱！**

---

**祝交易顺利！** 🚀

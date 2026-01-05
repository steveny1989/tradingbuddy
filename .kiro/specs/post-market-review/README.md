# 盘后复盘系统 Spec

## 概述

**"让你的投资不再有夜路"**

这是一个**5分钟极简复盘工具**，让普通投资者无需理解复杂的技术指标，就能快速完成每日复盘并做出投资决策。

---

## 核心价值

- **节省时间**: 从2小时缩短到5分钟
- **降低门槛**: 看懂红绿灯就够了
- **提高胜率**: 基于历史数据验证
- **减少亏损**: 自动体检持仓

---

## 三大核心模块

### 1. 市场"体温计" 🌡️

**3秒内知道明天该不该操作**

```
🔴 情绪火热（大胆操作）
🔵 情绪冰点（等待机会）
⚪ 情绪平淡（按兵不动）
```

### 2. 持仓"自动体检" 🏥

**一键检查所有持仓**

```
🟢 绿灯（健康）: 趋势向上，建议继续持有
🟡 黄灯（警示）: 出现缩量滞涨，建议减仓
🔴 红灯（危险）: 破位下跌，触发止损阈值
```

### 3. 明日"锦囊" 🎁

**推荐3个明日最具潜力的方向**

```
【1】新能源汽车板块
    理由：国产替代逻辑加强，资金流入明显
    历史胜率：过去30天胜率65%
    [加入明日关注] [设置闹钟]
```

---

## 文档结构

```
.kiro/specs/post-market-review/
├── README.md                    # 本文件
├── requirements.md              # ✅ 需求文档（10个需求）
├── PRODUCT_DEFINITION.md        # ✅ 产品定义文档
├── CLEANUP_PLAN.md              # ✅ 代码清理计划
├── design.md                    # ✅ 技术设计文档
└── tasks.md                     # ✅ 任务分解文档
```

---

## 关键需求

### P0 (必须有)
1. ✅ 市场情绪模块
2. ✅ 持仓健康模块
3. ✅ 自动触发机制

### P1 (应该有)
4. ✅ 明日锦囊模块
5. ✅ 数据质量保证
6. ✅ 历史胜率验证

### P2 (可以有)
7. ⏳ 用户交互体验优化
8. ⏳ 持仓导入功能
9. ⏳ 明日提醒功能

---

## 技术架构

### 后端核心模块

```python
src/business/post_market/
├── market_sentiment.py      # 市场情绪计算器
├── portfolio_health.py      # 持仓健康检查器
└── actionable_insights.py   # 明日锦囊生成器
```

### 前端核心组件

```typescript
frontend/src/components/post_market/
├── MarketSentiment.tsx      # 市场体温计
├── PortfolioHealth.tsx      # 持仓体检
└── ActionableInsights.tsx   # 明日锦囊
```

---

## 自动化流程

```
16:00 - 数据同步开始
  ↓
16:05 - 触发复盘生成
  ↓
16:10 - 市场情绪计算完成
  ↓
16:15 - 持仓健康检查完成
  ↓
19:30 - 明日锦囊生成完成
  ↓
20:00 - 用户打开App，立即看到报告
```

---

## 成功指标 (KPIs)

| 指标 | 目标 |
|------|------|
| PMU (晚间活跃用户占比) | 40% |
| Decision Conversion (决策转化率) | 30% |
| Average Drawdown (平均回撤) | < 市场平均 |
| 7日留存率 | 50% |
| 平均停留时长 | 5分钟 |

---

## 实现路线图

### Phase 1: MVP (2周)
- 市场情绪模块
- 持仓健康模块
- 自动触发机制
- 基础前端页面

### Phase 2: 优化 (2周)
- 明日锦囊模块
- 历史胜率验证
- 持仓导入功能
- 移动端适配

### Phase 3: 扩展 (4周)
- 明日提醒功能
- 历史复盘查看
- 一键导出功能
- KPI监控系统

---

## 设计原则

1. **极简**: 只保留最核心的功能
2. **一键**: 所有操作不超过2次点击
3. **人类可读**: 不出现技术术语
4. **自动化**: 用户晚上打开就能看到报告
5. **可验证**: 所有推荐都有历史胜率

---

## 代码清理

为了聚焦盘后复盘，我们将：

**保留**:
- `ma_crossover.py` - 趋势判断
- `volume_shrink.py` - 缩量分析
- `backtest/engine.py` - 回测引擎
- `data_validator.py` - 数据验证

**归档到 archive/**:
- 诊断模块 (diagnosis/)
- 选股器模块 (picker/)
- 模拟交易模块 (paper_trading/)
- 霍华德·马克斯策略 (reverse_value.py)

---

## 当前状态

✅ **Design Phase Complete!**

所有设计文档已完成：
1. ✅ **requirements.md** - 10个核心需求
2. ✅ **PRODUCT_DEFINITION.md** - 产品愿景和架构
3. ✅ **CLEANUP_PLAN.md** - 代码清理策略
4. ✅ **design.md** - 技术设计（API、数据模型、算法、组件）
5. ✅ **tasks.md** - 任务分解（~107小时，13个工作日）

## 下一步

🚀 **Ready to Start Implementation!**

**推荐起点**: Task 1.1 - Database Design

**Phase 1 MVP Tasks** (2周):
1. Task 1.1: 数据库表设计 (2h)
2. Task 1.2: 市场情绪计算器 (4h)
3. Task 1.3: 持仓健康检查器 (6h)
4. Task 1.4: 复盘报告生成器 (4h)
5. Task 1.5: 后端API实现 (4h)
6. Task 1.6: 前端页面框架 (4h)
7. Task 1.7: 市场体温计组件 (3h)
8. Task 1.8: 持仓体检组件 (4h)
9. Task 1.9: 自动触发调度器 (3h)
10. Task 1.10: MVP测试和优化 (4h)

---

## 联系方式

**Product Owner**: CPO  
**Target Launch**: 4周后  
**Success Metric**: PMU > 40%, Decision Conversion > 30%

---

## 参考资料

- [requirements.md](./requirements.md) - ✅ 完整需求文档（10个需求）
- [PRODUCT_DEFINITION.md](./PRODUCT_DEFINITION.md) - ✅ 产品定义和架构
- [CLEANUP_PLAN.md](./CLEANUP_PLAN.md) - ✅ 代码清理计划
- [design.md](./design.md) - ✅ 技术设计文档（NEW!）
- [tasks.md](./tasks.md) - ✅ 任务分解文档（NEW!）

---

**让我们专注于这一件事，把它做到极致！** 🚀

# 代码清理计划 - 聚焦盘后复盘

## 清理原则

**保留**: 盘后复盘系统需要的核心功能
**归档**: 暂时不需要但未来可能用到的功能
**删除**: 完全不需要的功能

---

## 需要保留的核心模块

### 1. 策略模块 (src/business/strategies/)

**保留**:
- `ma_crossover.py` - 用于持仓健康检查（趋势判断）
- `volume_shrink.py` - 用于持仓健康检查（缩量分析）

**归档到 archive/**:
- `reverse_value.py` - 霍华德·马克斯策略（暂时不用）
- 其他策略文件

### 2. 回测引擎 (src/business/backtest/)

**保留**:
- `engine.py` - 用于明日锦囊生成
- `backtest_config.py` - 回测配置

**归档**:
- 复杂的回测报告生成功能

### 3. 数据验证 (src/data/)

**保留**:
- `data_validator.py` - 用于数据质量保证
- `database.py` - 数据库访问
- `financial_fetcher.py` - 财务数据获取

**归档**:
- `financial_calculator.py` - 复杂的财务计算（暂时不用）
- `progress_tracker.py` - 进度跟踪（暂时不用）

### 4. Web API (src/web/routes/)

**保留**:
- `stocks.py` - 股票数据API
- `indices.py` - 指数数据API

**归档**:
- `diagnosis.py` - 股票诊断（功能重复）
- `picker.py` - 选股器（功能重复）
- `paper_trading.py` - 模拟交易（暂时不用）
- `backtest.py` - 回测API（暂时不用）

---

## 归档计划

### Step 1: 创建 archive 目录结构

```
archive/
├── strategies/          # 归档的策略
│   └── reverse_value.py
├── diagnosis/           # 归档的诊断功能
│   ├── diagnosis_engine.py
│   ├── plain_language_generator.py
│   └── ...
├── picker/              # 归档的选股器
│   └── ...
├── paper_trading/       # 归档的模拟交易
│   └── ...
└── docs/                # 归档的文档
    ├── REVERSE_VALUE_*.md
    ├── DIAGNOSIS_*.md
    └── ...
```

### Step 2: 移动文件

**策略模块**:
```bash
mv src/business/strategies/reverse_value.py archive/strategies/
```

**诊断模块**:
```bash
mv src/business/diagnosis/ archive/diagnosis/
mv src/web/routes/diagnosis.py archive/diagnosis/
mv frontend/src/pages/StockDiagnosis.tsx archive/diagnosis/
mv frontend/src/components/diagnosis/ archive/diagnosis/components/
```

**选股器模块**:
```bash
mv src/web/routes/picker.py archive/picker/
mv frontend/src/pages/SimplePicker.premium.tsx archive/picker/
mv frontend/src/components/picker/ archive/picker/components/
```

**模拟交易模块**:
```bash
mv src/web/routes/paper_trading.py archive/paper_trading/
mv paper_trading_data/ archive/paper_trading/data/
```

**文档**:
```bash
mv REVERSE_VALUE_*.md archive/docs/
mv DIAGNOSIS_*.md archive/docs/
mv STOCK_DIAGNOSIS_*.md archive/docs/
mv TOP_PICKS_*.md archive/docs/
mv HOWARD_MARKS_*.md archive/docs/
mv FALLEN_STARS_*.md archive/docs/
```

### Step 3: 更新导入引用

**需要更新的文件**:
- `src/web/app.py` - 移除归档模块的路由
- `frontend/src/App.tsx` - 移除归档页面的路由
- 其他引用归档模块的文件

---

## 保留的核心功能清单

### 后端 (Python)

```
src/
├── business/
│   ├── strategies/
│   │   ├── ma_crossover.py          ✅ 保留
│   │   └── volume_shrink.py         ✅ 保留
│   ├── backtest/
│   │   ├── engine.py                ✅ 保留
│   │   └── backtest_config.py       ✅ 保留
│   └── post_market/                 🆕 新建
│       ├── market_sentiment.py      🆕 市场情绪计算器
│       ├── portfolio_health.py      🆕 持仓健康检查器
│       └── actionable_insights.py   🆕 明日锦囊生成器
├── data/
│   ├── database.py                  ✅ 保留
│   ├── data_validator.py            ✅ 保留
│   └── financial_fetcher.py         ✅ 保留
└── web/
    ├── app.py                       ✅ 保留（简化）
    └── routes/
        ├── stocks.py                ✅ 保留
        ├── indices.py               ✅ 保留
        └── post_market_review.py    🆕 新建
```

### 前端 (React/TypeScript)

```
frontend/src/
├── App.tsx                          ✅ 保留（简化）
├── pages/
│   └── PostMarketReview.tsx         🆕 新建
├── components/
│   └── post_market/                 🆕 新建
│       ├── MarketSentiment.tsx      🆕 市场体温计
│       ├── PortfolioHealth.tsx      🆕 持仓体检
│       └── ActionableInsights.tsx   🆕 明日锦囊
└── utils/
    └── api.ts                       ✅ 保留（简化）
```

---

## 清理后的项目结构

```
tradingbuddy/
├── src/                             # 核心代码
│   ├── business/
│   │   ├── strategies/              # 2个策略文件
│   │   ├── backtest/                # 回测引擎
│   │   └── post_market/             # 盘后复盘（新）
│   ├── data/                        # 数据层
│   └── web/                         # API层
├── frontend/                        # 前端代码
│   └── src/
│       ├── pages/                   # 1个页面
│       └── components/              # 3个组件
├── archive/                         # 归档代码
│   ├── strategies/
│   ├── diagnosis/
│   ├── picker/
│   ├── paper_trading/
│   └── docs/
├── tools/                           # 工具脚本
├── tests/                           # 测试代码
└── docs/                            # 核心文档
    └── POST_MARKET_REVIEW.md        # 盘后复盘文档
```

---

## 清理的好处

### 1. 代码更清晰
- 从100+个文件减少到30个核心文件
- 开发者可以快速理解系统

### 2. 维护更简单
- 只需要维护3个核心模块
- 减少bug和技术债务

### 3. 性能更好
- 减少不必要的代码加载
- 提升系统响应速度

### 4. 聚焦产品
- 专注于盘后复盘这一个功能
- 把它做到极致

---

## 执行计划

### Week 1: 归档旧代码

- [ ] Day 1-2: 创建archive目录，移动策略模块
- [ ] Day 3-4: 移动诊断模块和选股器模块
- [ ] Day 5: 移动文档和测试文件

### Week 2: 构建新功能

- [ ] Day 1-2: 实现市场情绪计算器
- [ ] Day 3-4: 实现持仓健康检查器
- [ ] Day 5: 实现明日锦囊生成器

### Week 3: 前端开发

- [ ] Day 1-2: 实现市场体温计组件
- [ ] Day 3-4: 实现持仓体检组件
- [ ] Day 5: 实现明日锦囊组件

### Week 4: 集成测试

- [ ] Day 1-2: 自动触发机制
- [ ] Day 3-4: 端到端测试
- [ ] Day 5: 性能优化

---

## 回滚计划

如果需要恢复归档的功能：

```bash
# 恢复诊断功能
cp -r archive/diagnosis/ src/business/
cp archive/diagnosis/diagnosis.py src/web/routes/

# 恢复选股器
cp -r archive/picker/ src/web/routes/
```

---

## 总结

清理后的系统将专注于**盘后复盘**这一个核心功能：

**3个模块**:
1. 市场体温计
2. 持仓体检
3. 明日锦囊

**3个页面**:
1. 盘后复盘主页

**3个API**:
1. GET /api/post-market-review
2. POST /api/portfolio/import
3. POST /api/insights/subscribe

简单、清晰、专注！

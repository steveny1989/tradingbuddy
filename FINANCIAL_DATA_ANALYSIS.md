# 财务数据完整性分析报告

**分析日期**: 2026-01-04  
**数据库**: data/a_share.db

---

## 📊 数据概览

### 1. financial_indicators (财务指标表) ⭐

**覆盖范围**:
- **股票数量**: 5,769只
- **时间跨度**: 1988-12-31 至 2025-09-30
- **最新数据**: 2025年三季报 (2025-09-30)

**数据完整性** (以2025-09-30为例):
```
总记录数: 5,478条
ROE (净资产收益率): 5,417条 (98.9%) ✅
ROA (总资产收益率): 0条 (0%) ❌
债资比: 5,476条 (99.96%) ✅
EPS (每股收益): 5,477条 (99.98%) ✅
```

**近期报告期数据量**:
| 报告期 | 股票数量 | 覆盖率 |
|--------|---------|--------|
| 2025-09-30 (三季报) | 5,478 | 97.8% |
| 2025-06-30 (半年报) | 5,611 | 100% |
| 2025-03-31 (一季报) | 5,473 | 97.7% |
| 2024-12-31 (年报) | 5,617 | 100% |
| 2024-09-30 (三季报) | 5,511 | 98.4% |
| 2024-06-30 (半年报) | 5,631 | 100% |

**关键指标**:
```sql
-- 可用的核心指标
✅ roe                    -- 净资产收益率 (98.9%完整)
✅ debt_to_asset_ratio    -- 资产负债率 (99.96%完整)
✅ eps                    -- 每股收益 (99.98%完整)
✅ gross_margin           -- 毛利率
✅ net_margin             -- 净利率
✅ current_ratio          -- 流动比率
✅ quick_ratio            -- 速动比率
✅ pe_ratio               -- 市盈率
✅ pb_ratio               -- 市净率

❌ roa                    -- 总资产收益率 (数据缺失)
```

**示例数据** (贵州茅台 600519):
```
报告期      | ROE    | 债资比  | EPS
-----------|--------|--------|-------
2025-09-30 | 24.64% | 12.81% | 51.53
2025-06-30 | 17.89% | 14.75% | 36.18
2025-03-31 | 10.92% | 14.14% | 21.38
2024-12-31 | 36.02% | 19.04% | 68.64
2024-09-30 | 26.09% | 13.63% | 48.42
```

---

### 2. income_statement (利润表) ⭐

**覆盖范围**:
- **股票数量**: 5,782只
- **最新数据**: 2025年三季报

**近期报告期数据量**:
| 报告期 | 股票数量 | 覆盖率 |
|--------|---------|--------|
| 2025-09-30 | 5,491 | 98.0% |
| 2025-06-30 | 5,624 | 100% |
| 2025-03-31 | 5,486 | 97.9% |
| 2024-12-31 | 5,629 | 100% |
| 2024-09-30 | 5,524 | 98.6% |

**主要字段**:
- 营业收入 (revenue)
- 营业成本 (cost_of_revenue)
- 营业利润 (operating_profit)
- 净利润 (net_profit)
- 毛利润 (gross_profit)
- 销售费用 (selling_expenses)
- 管理费用 (admin_expenses)
- 研发费用 (rd_expenses)

**数据质量**: ✅ 优秀
- 覆盖率高 (98%+)
- 数据完整
- 更新及时

---

### 3. balance_sheet (资产负债表) ⚠️

**覆盖范围**:
- **股票数量**: 仅31只 ❌
- **时间跨度**: 1997-12-31 至 2025-09-30

**数据质量**: ❌ 严重不足
- 覆盖率极低 (0.5%)
- 大部分股票无数据
- **不建议使用此表**

**主要字段**:
- 总资产 (total_assets)
- 总负债 (total_liabilities)
- 股东权益 (shareholders_equity)
- 流动资产 (current_assets)
- 流动负债 (current_liabilities)
- 现金及等价物 (cash_and_equivalents)
- 应收账款 (accounts_receivable)
- 存货 (inventory)
- 固定资产 (fixed_assets)
- 短期借款 (short_term_debt)
- 长期借款 (long_term_debt)

---

### 4. cash_flow (现金流量表) ⚠️

**覆盖范围**:
- **股票数量**: 仅29只 ❌

**数据质量**: ❌ 严重不足
- 覆盖率极低 (0.5%)
- **不建议使用此表**

**主要字段**:
- 经营活动现金流
- 投资活动现金流
- 筹资活动现金流

---

## 🎯 盘后复盘系统可用数据

### ✅ 可以使用的财务数据

#### 1. financial_indicators 表
**推荐使用的指标**:

```python
# 盈利能力
roe                    # 净资产收益率 (98.9%完整) ⭐
net_margin             # 净利率
gross_margin           # 毛利率
eps                    # 每股收益 (99.98%完整) ⭐

# 偿债能力
debt_to_asset_ratio    # 资产负债率 (99.96%完整) ⭐
current_ratio          # 流动比率
quick_ratio            # 速动比率

# 估值指标
pe_ratio               # 市盈率
pb_ratio               # 市净率
```

#### 2. income_statement 表
**推荐使用的字段**:

```python
revenue                # 营业收入
net_profit             # 净利润
operating_profit       # 营业利润
gross_profit           # 毛利润
```

---

## 📈 数据使用建议

### 1. 筛选优质股票

**推荐条件** (基于可用数据):

```sql
-- 筛选ROE > 15%、债资比 < 60%的股票
SELECT 
    fi.code,
    sb.name,
    fi.roe,
    fi.debt_to_asset_ratio,
    fi.eps
FROM financial_indicators fi
JOIN stock_basic sb ON fi.code = sb.code
WHERE fi.report_date = '2024-12-31'  -- 使用最新年报
  AND fi.roe > 15                     -- ROE > 15%
  AND fi.roe < 50                     -- 排除异常值
  AND fi.debt_to_asset_ratio < 60    -- 债资比 < 60%
ORDER BY fi.roe DESC;
```

**结果示例**:
```
code   | name       | ROE    | 债资比  | EPS
-------|-----------|--------|--------|-------
603202 | 天有为     | 49.40% | 43.95% | -
301004 | 嘉益股份   | 46.64% | 30.78% | -
600149 | 廊坊发展   | 44.77% | 48.81% | -
002247 | 聚力文化   | 42.39% | 32.76% | -
002395 | 双象股份   | 41.58% | 40.23% | -
300502 | 新易盛     | 41.00% | 32.11% | -
002847 | 盐津铺子   | 40.86% | 50.90% | -
603929 | 亚翔集成   | 40.41% | 54.20% | -
600809 | 山西汾酒   | 39.68% | 34.19% | -
605117 | 德业股份   | 39.24% | 37.45% | -
```

### 2. 报告期选择

**推荐使用年报数据** (12-31):
- ✅ 数据最完整 (100%覆盖)
- ✅ 数据最可靠
- ✅ 可比性强

**季报数据注意事项**:
- 一季报/三季报: 覆盖率 ~98%
- 半年报: 覆盖率 100%
- 季报数据可能有季节性波动

### 3. 数据时效性

**最新可用数据**:
- 2025-09-30 (三季报) - 最新
- 2024-12-31 (年报) - 推荐使用 ⭐
- 2024-06-30 (半年报)

**建议**:
- 日常筛选: 使用最新年报 (2024-12-31)
- 实时监控: 使用最新季报 (2025-09-30)

---

## ⚠️ 数据限制

### 1. 不可用的数据

❌ **balance_sheet** (资产负债表)
- 仅31只股票有数据
- 覆盖率 < 1%
- **不要使用**

❌ **cash_flow** (现金流量表)
- 仅29只股票有数据
- 覆盖率 < 1%
- **不要使用**

❌ **ROA** (总资产收益率)
- financial_indicators表中此字段为空
- **不要使用**

### 2. 数据异常值

**注意过滤异常值**:
```sql
-- 某些股票ROE异常高 (> 100%)
-- 可能是数据错误或特殊情况
WHERE roe > 15 AND roe < 50  -- 合理范围
```

**异常值示例**:
```
000908 | ROE: 2684.86%  -- 明显异常
600813 | ROE: 2564.53%  -- 明显异常
600579 | ROE: 572.73%   -- 明显异常
```

---

## 🔍 数据验证

### 验证查询

```sql
-- 1. 检查最新报告期的数据量
SELECT report_date, COUNT(*) as count
FROM financial_indicators
GROUP BY report_date
ORDER BY report_date DESC
LIMIT 5;

-- 2. 检查某只股票的历史数据
SELECT code, report_date, roe, debt_to_asset_ratio, eps
FROM financial_indicators
WHERE code = '600519'
ORDER BY report_date DESC
LIMIT 10;

-- 3. 检查数据完整性
SELECT 
    COUNT(*) as total,
    COUNT(roe) as has_roe,
    COUNT(debt_to_asset_ratio) as has_debt,
    COUNT(eps) as has_eps
FROM financial_indicators
WHERE report_date = '2024-12-31';
```

---

## 💡 盘后复盘系统建议

### 明日锦囊模块

**可以使用的财务筛选条件**:

```python
# ✅ 推荐使用
def filter_by_financials(stocks):
    """基于财务指标筛选股票"""
    return stocks.query("""
        roe > 10 and roe < 50 and
        debt_to_asset_ratio < 60 and
        eps > 0
    """)
```

**不要使用的条件**:

```python
# ❌ 不要使用
# roa > 5  # 数据缺失
# total_assets > 1e10  # balance_sheet数据不足
# operating_cash_flow > 0  # cash_flow数据不足
```

### 数据更新策略

**建议**:
1. 使用最新年报数据 (2024-12-31) 作为基准
2. 季报发布后及时更新
3. 设置数据有效期检查

```python
def get_latest_financial_data(code):
    """获取最新财务数据"""
    # 优先使用最新年报
    data = db.query("""
        SELECT * FROM financial_indicators
        WHERE code = ?
          AND report_date LIKE '%-12-31'
        ORDER BY report_date DESC
        LIMIT 1
    """, (code,))
    return data
```

---

## ✅ 总结

### 可用数据 ✅

| 数据表 | 覆盖率 | 推荐使用 | 备注 |
|--------|--------|---------|------|
| financial_indicators | 98%+ | ✅ 强烈推荐 | ROE、债资比、EPS完整 |
| income_statement | 98%+ | ✅ 推荐 | 营收、利润数据完整 |
| market_cap_data | 100% | ✅ 推荐 | 市值、PE、PB实时数据 |
| daily_data | 100% | ✅ 推荐 | 日线数据完整 |

### 不可用数据 ❌

| 数据表 | 覆盖率 | 推荐使用 | 备注 |
|--------|--------|---------|------|
| balance_sheet | < 1% | ❌ 不推荐 | 数据严重不足 |
| cash_flow | < 1% | ❌ 不推荐 | 数据严重不足 |

### 核心结论

**盘后复盘系统可以使用的财务数据**:
1. ✅ ROE (净资产收益率) - 98.9%完整
2. ✅ 债资比 (资产负债率) - 99.96%完整
3. ✅ EPS (每股收益) - 99.98%完整
4. ✅ 净利率、毛利率
5. ✅ 流动比率、速动比率
6. ✅ PE、PB (从market_cap_data获取)

**足够支持明日锦囊模块的财务筛选功能！** 🎉

---

## 📚 相关文档

- `DATA_STRUCTURE_GUIDE.md` - 完整数据结构指南
- `docs/FINANCIAL_DATA_README.md` - 财务数据说明
- `src/data/financial_fetcher.py` - 财务数据获取工具

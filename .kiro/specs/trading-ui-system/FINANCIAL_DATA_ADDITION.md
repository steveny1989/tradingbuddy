# 财务数据功能添加说明

## 概述

本文档说明了在Trading UI System spec中新增的财务数据功能。该功能允许用户查看和分析公司的财务报表和关键财务指标，支持基本面分析和价值投资决策。

## 新增需求 (Requirements)

### Requirement 13: 财务数据查看

**目标**: 为用户提供完整的财务数据查看功能

**核心功能**:
1. 三大财务报表展示（资产负债表、利润表、现金流量表）
2. 关键财务指标展示：
   - 盈利能力：ROE、ROA、毛利率、净利率、营业利润率
   - 偿债能力：资产负债率、流动比率、速动比率
   - 估值指标：PE、PB、PS
   - 成长性指标：营收增长率、净利润增长率、ROE增长率
3. 报告期选择（季报/年报）
4. 财务数据时间序列图表（最近8个季度）
5. 同行业公司财务指标对比（可选）
6. 友好的无数据提示

### Requirement 14: 财务数据管理

**目标**: 提供财务数据的同步和管理功能

**核心功能**:
1. 财务数据同步状态展示
2. 手动触发财务数据同步
3. 实时同步进度显示
4. 同步结果统计和错误处理
5. 数据覆盖率和更新时间展示

## 新增设计 (Design)

### 后端API端点

```
GET  /api/stocks/{code}/financials
     - 获取财务报表数据
     - 支持报表类型和报告期筛选

GET  /api/stocks/{code}/indicators/financial
     - 获取财务分析指标
     - 返回盈利、偿债、估值、成长性指标

POST /api/data/sync/financials
     - 触发财务数据同步任务

GET  /api/data/financials-status
     - 获取财务数据同步状态
```

### 前端组件

1. **FinancialDataPage**: 财务数据主页面（股票详情页的标签页）
2. **FinancialStatementsTable**: 财务报表表格组件
3. **FinancialIndicatorsCard**: 财务指标卡片组件
4. **FinancialIndicatorsChart**: 财务指标图表组件
5. **PeriodSelector**: 报告期选择器组件

### 数据模型

#### 数据库表结构

```sql
-- 资产负债表
financial_balance_sheet (
    code, report_date, period_type,
    total_assets, total_liabilities, total_equity,
    current_assets, current_liabilities,
    cash, accounts_receivable, inventory,
    fixed_assets, intangible_assets
)

-- 利润表
financial_income_statement (
    code, report_date, period_type,
    revenue, operating_cost, gross_profit,
    operating_profit, net_profit, eps
)

-- 现金流量表
financial_cash_flow (
    code, report_date, period_type,
    operating_cash_flow, investing_cash_flow,
    financing_cash_flow, net_cash_flow
)

-- 财务指标
financial_indicators (
    code, report_date, period_type,
    roe, roa, gross_margin, net_margin, operating_margin,
    debt_to_asset, current_ratio, quick_ratio,
    pe, pb, ps,
    revenue_growth, profit_growth, roe_growth
)

-- 同步状态
financial_sync_status (
    code, last_sync, status,
    latest_report_date, error_message
)
```

#### TypeScript接口

```typescript
interface FinancialStatement {
  report_date: string;
  report_type: 'balance_sheet' | 'income_statement' | 'cash_flow';
  period_type: 'quarterly' | 'annual';
  items: FinancialItems;
}

interface FinancialIndicators {
  report_date: string;
  period_type: 'quarterly' | 'annual';
  profitability: { roe, roa, gross_margin, net_margin, operating_margin };
  solvency: { debt_to_asset, current_ratio, quick_ratio };
  valuation: { pe, pb, ps };
  growth: { revenue_growth, profit_growth, roe_growth };
}
```

## 新增任务 (Tasks)

### Task 20: 财务数据后端API实现

- **20.1**: 实现财务报表API
- **20.2**: 实现财务指标API
- **20.3**: 实现财务数据同步API
- **20.4**: 编写财务数据API的单元测试（可选）

### Task 21: 财务数据前端功能实现

- **21.1**: 实现财务数据页面
- **21.2**: 实现财务指标展示
- **21.3**: 实现财务数据图表
- **21.4**: 实现财务数据管理功能
- **21.5**: 编写财务数据组件的单元测试（可选）
- **21.6**: 编写财务数据的属性测试（可选）

### Task 22: Checkpoint - 财务数据功能完成

验证所有财务数据功能正常工作

## 新增Correctness Properties

**Property 38**: 财务报表显示所有必需字段
- 验证报表数据完整性

**Property 39**: 财务指标显示所有必需类别
- 验证四大类指标（盈利、偿债、估值、成长）都存在

**Property 40**: 财务数据时间序列图表正确渲染
- 验证图表数据格式和渲染逻辑

**Property 41**: 财务同步状态显示所有必需字段
- 验证同步状态表格数据完整性

## 实现优先级

### 高优先级（MVP必需）
1. 财务报表API和数据库表结构
2. 财务指标API
3. 基础财务数据展示页面
4. 财务指标卡片展示

### 中优先级（增强功能）
1. 财务数据时间序列图表
2. 财务数据同步管理功能
3. 报告期切换功能

### 低优先级（可选功能）
1. 同行业公司对比
2. 财务数据导出功能
3. 高级财务分析工具

## 技术依赖

### 后端
- 需要实现财务数据获取模块（`src/data/financial_fetcher.py`）
- 需要数据库迁移脚本创建新表
- 需要集成财务数据API（如Tushare、AKShare等）

### 前端
- 使用ECharts渲染财务指标图表
- 使用Ant Design Table组件展示财务报表
- 需要实现数据格式化工具（金额、百分比等）

## 数据来源建议

1. **Tushare Pro**: 提供完整的财务数据API
   - 资产负债表、利润表、现金流量表
   - 财务指标数据
   - 需要积分或付费

2. **AKShare**: 免费开源财务数据
   - 东方财富网财务数据
   - 新浪财经财务数据
   - 数据质量较好

3. **BaoStock**: 免费证券数据平台
   - 提供基础财务数据
   - 数据更新及时

## 注意事项

1. **数据质量**: 财务数据可能存在缺失或错误，需要做好数据验证和异常处理
2. **更新频率**: 财务数据通常季度更新，不需要每日同步
3. **存储空间**: 财务数据量较大，需要考虑数据库存储优化
4. **计算指标**: 部分财务指标需要根据报表数据计算，确保计算逻辑正确
5. **历史数据**: 建议至少保留最近3年的财务数据用于趋势分析

## 后续扩展方向

1. 财务数据预警功能（如ROE下降、负债率过高等）
2. 财务健康度评分系统
3. 基于财务指标的选股策略
4. 财务数据对比分析工具
5. 财务报表深度分析（杜邦分析等）

## 总结

通过添加财务数据功能，Trading UI System将支持更全面的股票分析能力，帮助用户从技术面和基本面两个维度进行投资决策。该功能的实现将显著提升系统的专业性和实用性。

# Requirements Document: 股票综合诊断系统

## Introduction

实现一个统一的股票综合诊断系统，像医生看病一样，从多个维度（技术面、基本面、行业面、资金面、大盘对比）对股票进行全面分析，生成易懂的诊断报告和投资建议。

## Glossary

- **Stock Diagnosis**: 股票诊断，对股票进行多维度综合分析
- **Technical Analysis**: 技术面分析，基于K线、成交量、技术指标
- **Fundamental Analysis**: 基本面分析，基于财务报表和财务指标
- **Sector Analysis**: 行业面分析，基于行业归属和板块表现
- **Capital Analysis**: 资金面分析，基于北向资金和主力资金流向
- **Market Comparison**: 大盘对比，个股表现与大盘/行业的对比
- **Diagnosis Report**: 诊断报告，综合各维度分析的最终报告

## Requirements

### Requirement 1: 技术面分析 (Technical Analysis)

**User Story**: 作为投资者，我想要了解股票的技术面状况，以便判断短期走势和买卖时机

#### Acceptance Criteria

1. THE System SHALL analyze K-line patterns using existing candlestick pattern recognition
2. THE System SHALL calculate technical indicators (MA20, RSI, volume ratio)
3. THE System SHALL identify current trend direction (上涨/下跌/震荡)
4. THE System SHALL provide support and resistance levels
5. THE System SHALL generate human-readable technical analysis summary
6. WHEN technical indicators are bullish, THE System SHALL signal "技术面向好" (Green)
7. WHEN technical indicators are bearish, THE System SHALL signal "技术面转弱" (Red)
8. WHEN technical indicators are mixed, THE System SHALL signal "技术面中性" (Yellow)

---

### Requirement 2: 基本面分析 (Fundamental Analysis)

**User Story**: 作为投资者，我想要了解股票的基本面质量，以便判断长期投资价值

#### Acceptance Criteria

1. THE System SHALL retrieve key financial indicators (PE, PB, ROE, ROA, 净利润率)
2. THE System SHALL compare financial indicators with industry averages
3. THE System SHALL analyze profitability trends (同比/环比增长)
4. THE System SHALL evaluate financial health (资产负债率, 流动比率)
5. THE System SHALL generate human-readable fundamental analysis summary
6. WHEN fundamentals are strong, THE System SHALL signal "基本面优秀" (Green)
7. WHEN fundamentals are weak, THE System SHALL signal "基本面较差" (Red)
8. WHEN fundamentals are average, THE System SHALL signal "基本面一般" (Yellow)

---

### Requirement 3: 行业面分析 (Sector Analysis)

**User Story**: 作为投资者，我想要了解股票所在行业的表现，以便判断板块机会

#### Acceptance Criteria

1. THE System SHALL identify stock's industry classification
2. THE System SHALL retrieve industry performance ranking
3. THE System SHALL calculate stock's relative strength vs industry
4. THE System SHALL analyze sector correlation
5. THE System SHALL provide same-industry stock recommendations
6. WHEN industry is top-performing, THE System SHALL signal "行业强势" (Green)
7. WHEN industry is underperforming, THE System SHALL signal "行业疲软" (Red)
8. WHEN industry is average, THE System SHALL signal "行业中性" (Yellow)

---

### Requirement 4: 资金面分析 (Capital Analysis)

**User Story**: 作为投资者，我想要了解资金流向，以便判断主力动向

#### Acceptance Criteria

1. THE System SHALL retrieve northbound capital holdings and changes
2. THE System SHALL retrieve main capital flow (主力资金流向)
3. THE System SHALL analyze capital inflow/outflow trends
4. THE System SHALL identify institutional buying/selling signals
5. THE System SHALL generate human-readable capital analysis summary
6. WHEN capital is flowing in, THE System SHALL signal "资金流入" (Green)
7. WHEN capital is flowing out, THE System SHALL signal "资金流出" (Red)
8. WHEN capital flow is neutral, THE System SHALL signal "资金观望" (Yellow)

---

### Requirement 5: 大盘对比分析 (Market Comparison)

**User Story**: 作为投资者，我想要了解个股相对大盘的表现，以便判断相对强弱

#### Acceptance Criteria

1. THE System SHALL retrieve major market indices (上证指数, 深证成指)
2. THE System SHALL calculate stock's performance vs market indices
3. THE System SHALL calculate stock's beta (相对大盘波动率)
4. THE System SHALL identify if stock is outperforming or underperforming market
5. THE System SHALL generate human-readable market comparison summary
6. WHEN stock outperforms market, THE System SHALL signal "跑赢大盘" (Green)
7. WHEN stock underperforms market, THE System SHALL signal "跑输大盘" (Red)
8. WHEN stock matches market, THE System SHALL signal "与大盘同步" (Yellow)

---

### Requirement 6: 综合诊断报告 (Comprehensive Diagnosis Report)

**User Story**: 作为用户，我想要看到一个综合诊断报告，以便快速了解股票的整体状况

#### Acceptance Criteria

1. THE System SHALL integrate all five analysis dimensions (技术/基本/行业/资金/大盘)
2. THE System SHALL generate an overall health score (0-100)
3. THE System SHALL provide a综合评级 (优秀/良好/一般/较差/很差)
4. THE System SHALL highlight key strengths and weaknesses
5. THE System SHALL provide actionable investment suggestions
6. THE System SHALL use traffic light colors (🟢🟡🔴) for visual clarity
7. THE System SHALL generate human-readable summary in plain Chinese
8. THE System SHALL support exporting report as JSON/HTML

---

### Requirement 7: 数据集成 (Data Integration)

**User Story**: 作为系统，我需要整合所有已有的分析模块，以便生成综合诊断

#### Acceptance Criteria

1. THE System SHALL reuse existing candlestick_patterns module
2. THE System SHALL reuse existing portfolio_health module (technical indicators)
3. THE System SHALL reuse existing sector_analysis module
4. THE System SHALL reuse existing capital_analysis module
5. THE System SHALL retrieve market index data from daily_data table
6. THE System SHALL handle missing data gracefully with warnings
7. THE System SHALL use most recent available data for each dimension

---

### Requirement 8: 性能与可扩展性 (Performance & Scalability)

**User Story**: 作为系统，我需要高效地生成诊断报告，以便支持实时查询

#### Acceptance Criteria

1. THE System SHALL generate single stock diagnosis in < 200ms
2. THE System SHALL support batch diagnosis of 50 stocks in < 5 seconds
3. THE System SHALL cache diagnosis results for 1 hour
4. THE System SHALL use database indexes for efficient queries
5. THE System SHALL support parallel processing for batch requests

---

### Requirement 9: API接口 (API Endpoints)

**User Story**: 作为开发者，我需要API接口来获取诊断报告，以便集成到前端

#### Acceptance Criteria

1. THE System SHALL provide REST API endpoint `/api/diagnosis/{code}`
2. THE System SHALL provide batch endpoint `/api/diagnosis/batch`
3. THE System SHALL return JSON format with all analysis dimensions
4. THE System SHALL include visual metadata (colors, scores, messages)
5. THE System SHALL support filtering by analysis dimension
6. THE System SHALL provide error responses for invalid stock codes

---

## Non-Functional Requirements

### Performance
- Single stock diagnosis: < 200ms
- Batch 50 stocks: < 5 seconds
- API response time: < 300ms
- Cache TTL: 1 hour

### Data Quality
- Use most recent data from each source
- Handle missing data with clear warnings
- Validate data ranges and outliers
- Provide data freshness timestamps

### Usability
- Human-readable Chinese explanations
- Clear visual indicators (🟢🟡🔴)
- Actionable investment suggestions
- Simple overall health score (0-100)

### Maintainability
- Reuse existing analysis modules
- Modular dimension analyzers
- Easy to add new analysis dimensions
- Well-documented integration points

---

## Success Metrics

1. **Coverage**: 95%+ of stocks have valid diagnosis reports
2. **Performance**: 95%+ of API calls respond in < 300ms
3. **Accuracy**: Diagnosis matches manual analysis
4. **User Engagement**: Users view diagnosis for 60%+ of stock searches
5. **Module Reuse**: 100% reuse of existing analysis modules

---

## Out of Scope (Future Enhancements)

1. Real-time intraday updates
2. Historical diagnosis tracking
3. Custom user-defined weights for dimensions
4. AI-powered prediction models
5. Social sentiment integration
6. News event impact analysis
7. Portfolio-level diagnosis
8. Automated trading signals

---

*Requirements Version: 1.0*  
*Date: 2026-01-04*

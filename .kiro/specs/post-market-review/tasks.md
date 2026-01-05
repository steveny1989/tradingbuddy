# Tasks: 盘后复盘系统实现

## Overview

本文档将盘后复盘系统的实现拆解为可执行的任务，按照优先级和依赖关系组织。

**实施策略**: MVP优先，分3个阶段实现

---

## Phase 1: MVP核心功能 (Week 1-2)

### Task 1.1: 数据库表设计

**Priority**: P0 (必须)  
**Estimated Time**: 2 hours  
**Dependencies**: None

**Description**: 创建盘后复盘系统所需的数据库表

**Acceptance Criteria**:
- [ ] 创建 `post_market_reviews` 表
- [ ] 创建 `user_portfolios` 表
- [ ] 创建 `actionable_insights` 表
- [ ] 添加必要的索引
- [ ] 编写数据库迁移脚本

**Files to Create/Modify**:
- `src/data/db_migrations.py` (add new migration)
- `src/data/database.py` (add table creation methods)

**Implementation Steps**:
1. 在 `db_migrations.py` 中添加新的迁移函数
2. 创建3个表的SQL语句
3. 添加索引优化查询性能
4. 测试迁移脚本

---

### Task 1.2: 市场情绪计算器

**Priority**: P0 (必须)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 1.1

**Description**: 实现市场情绪计算逻辑

**Acceptance Criteria**:
- [ ] 实现 `MarketSentimentCalculator` 类
- [ ] 计算涨跌停数量
- [ ] 计算连板高度
- [ ] 计算两市成交额
- [ ] 根据规则判断市场情绪（hot/cold/neutral）
- [ ] 生成一句话解释

**Files to Create/Modify**:
- `src/business/post_market/market_sentiment.py` (new)
- `src/business/post_market/__init__.py` (new)
- `src/business/post_market/models.py` (new)

**Implementation Steps**:
1. 创建 `MarketSentiment` 数据模型
2. 实现涨跌停统计（使用SQL聚合查询）
3. 实现连板高度计算
4. 实现成交额统计
5. 实现情绪判断逻辑
6. 编写单元测试

---

### Task 1.3: 持仓健康检查器 ✅

**Priority**: P0 (必须)  
**Estimated Time**: 6 hours  
**Dependencies**: Task 1.1  
**Status**: ✅ 完成 (2026-01-04)

**Description**: 实现持仓健康检查逻辑，使用简单的技术指标（MA20偏离度、RSI、量比）

**Acceptance Criteria**:
- [x] 实现 `PortfolioHealthChecker` 类
- [x] 实现 `TechnicalIndicators` 技术指标计算器
- [x] 计算技术指标（MA20、RSI、量比）
- [x] 综合判断健康状态（green/yellow/red）
- [x] 生成人话建议文案
- [x] 支持单只股票检查
- [x] 支持批量持仓检查
- [x] 编写测试脚本和示例

**Files Created**:
- `src/business/post_market/portfolio_health.py` ✅
- `test_portfolio_health.py` ✅
- `examples/portfolio_health_example.py` ✅
- `PORTFOLIO_HEALTH_IMPLEMENTATION.md` ✅

**Implementation Completed**:
1. ✅ 创建 `PortfolioHealth` 数据模型
2. ✅ 实现技术指标计算（MA20、RSI、量比）
3. ✅ 实现红绿灯健康状态判断逻辑
4. ✅ 实现人话建议文案生成
5. ✅ 编写完整的测试和示例
6. ✅ 创建实现文档

---

### Task 1.4: 复盘报告生成器

**Priority**: P0 (必须)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 1.2, Task 1.3

**Description**: 实现复盘报告生成的主流程

**Acceptance Criteria**:
- [ ] 实现 `PostMarketReviewGenerator` 类
- [ ] 调用市场情绪计算器
- [ ] 调用持仓健康检查器（如果用户有持仓）
- [ ] 生成报告并保存到数据库
- [ ] 处理异常和重试

**Files to Create/Modify**:
- `src/business/post_market/review_generator.py` (new)

**Implementation Steps**:
1. 创建 `PostMarketReview` 数据模型
2. 实现报告生成主流程
3. 集成市场情绪计算
4. 集成持仓健康检查
5. 实现数据库保存逻辑
6. 添加异常处理和日志
7. 编写集成测试

---

### Task 1.5: 后端API实现

**Priority**: P0 (必须)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 1.4

**Description**: 实现盘后复盘相关的API接口

**Acceptance Criteria**:
- [ ] 实现 `GET /api/post-market-review` 接口
- [ ] 实现 `POST /api/portfolio/import` 接口
- [ ] 实现 `POST /api/post-market-review/generate` 接口（测试用）
- [ ] 添加错误处理和参数验证
- [ ] 添加API文档

**Files to Create/Modify**:
- `src/web/routes/post_market_review.py` (new)
- `src/web/app.py` (register blueprint)

**Implementation Steps**:
1. 创建 `post_market_review` blueprint
2. 实现获取报告接口
3. 实现导入持仓接口
4. 实现手动生成接口
5. 添加参数验证
6. 编写API测试

---

### Task 1.6: 前端页面框架

**Priority**: P0 (必须)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 1.5

**Description**: 创建盘后复盘页面的基础框架

**Acceptance Criteria**:
- [ ] 创建 `PostMarketReview` 页面组件
- [ ] 实现数据加载逻辑
- [ ] 添加加载状态和错误处理
- [ ] 添加路由配置

**Files to Create/Modify**:
- `frontend/src/pages/PostMarketReview.tsx` (new)
- `frontend/src/pages/PostMarketReview.css` (new)
- `frontend/src/App.tsx` (add route)

**Implementation Steps**:
1. 创建页面组件
2. 实现API调用
3. 添加加载和错误状态
4. 配置路由
5. 测试页面加载

---

### Task 1.7: 市场体温计组件

**Priority**: P0 (必须)  
**Estimated Time**: 3 hours  
**Dependencies**: Task 1.6

**Description**: 实现市场情绪展示组件

**Acceptance Criteria**:
- [ ] 创建 `MarketSentiment` 组件
- [ ] 实现三种状态的视觉区分（红/蓝/灰）
- [ ] 显示情绪状态和建议
- [ ] 显示关键指标（涨停数、跌停数、成交额）
- [ ] 响应式设计

**Files to Create/Modify**:
- `frontend/src/components/post_market/MarketSentiment.tsx` (new)
- `frontend/src/components/post_market/MarketSentiment.css` (new)

**Implementation Steps**:
1. 创建组件结构
2. 实现状态颜色映射
3. 实现指标展示
4. 添加样式
5. 测试不同状态的显示

---

### Task 1.8: 持仓体检组件

**Priority**: P0 (必须)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 1.6

**Description**: 实现持仓健康展示组件

**Acceptance Criteria**:
- [ ] 创建 `PortfolioHealth` 组件
- [ ] 实现红绿灯状态显示
- [ ] 显示股票信息和关键指标
- [ ] 显示建议文案
- [ ] 按危险程度排序
- [ ] 实现导入持仓功能

**Files to Create/Modify**:
- `frontend/src/components/post_market/PortfolioHealth.tsx` (new)
- `frontend/src/components/post_market/PortfolioHealth.css` (new)
- `frontend/src/components/post_market/PortfolioImportModal.tsx` (new)

**Implementation Steps**:
1. 创建组件结构
2. 实现红绿灯显示
3. 实现股票列表
4. 创建导入模态框
5. 实现导入逻辑
6. 添加样式
7. 测试导入和显示

---

### Task 1.9: 自动触发调度器

**Priority**: P0 (必须)  
**Estimated Time**: 3 hours  
**Dependencies**: Task 1.4

**Description**: 实现每日自动触发复盘报告生成

**Acceptance Criteria**:
- [ ] 创建调度器脚本
- [ ] 每天16:05自动触发
- [ ] 检查是否为交易日
- [ ] 实现重试机制
- [ ] 实现超时处理
- [ ] 添加告警通知

**Files to Create/Modify**:
- `scripts/post_market_scheduler.py` (new)
- `scripts/start_scheduler.sh` (new)

**Implementation Steps**:
1. 创建调度器脚本
2. 使用 `schedule` 库设置定时任务
3. 实现交易日检查
4. 添加重试逻辑
5. 添加超时处理
6. 配置告警通知
7. 测试调度器

---

### Task 1.10: MVP测试和优化

**Priority**: P0 (必须)  
**Estimated Time**: 4 hours  
**Dependencies**: All above tasks

**Description**: 端到端测试MVP功能，修复bug，优化性能

**Acceptance Criteria**:
- [ ] 完整的端到端测试
- [ ] 修复发现的bug
- [ ] 性能优化（页面加载 < 3秒）
- [ ] 添加缓存机制
- [ ] 编写用户文档

**Files to Create/Modify**:
- `tests/test_post_market_review_e2e.py` (new)
- `docs/POST_MARKET_REVIEW_USER_GUIDE.md` (new)

**Implementation Steps**:
1. 编写端到端测试脚本
2. 运行完整流程测试
3. 修复发现的bug
4. 添加缓存优化
5. 性能测试和优化
6. 编写用户文档

---

## Phase 2: 明日锦囊功能 (Week 3-4)

### Task 2.1: 回测结果数据模型

**Priority**: P1 (应该有)  
**Estimated Time**: 2 hours  
**Dependencies**: Task 1.4

**Description**: 定义回测结果的数据模型

**Acceptance Criteria**:
- [ ] 创建 `BacktestResult` 数据模型
- [ ] 定义策略评分逻辑
- [ ] 定义动量/防御/稳定性得分

**Files to Create/Modify**:
- `src/business/post_market/models.py` (update)

---

### Task 2.2: 明日锦囊生成器

**Priority**: P1 (应该有)  
**Estimated Time**: 8 hours  
**Dependencies**: Task 2.1

**Description**: 实现明日锦囊生成逻辑，集成回测引擎

**Acceptance Criteria**:
- [ ] 实现 `ActionableInsightsGenerator` 类
- [ ] 运行 `ma_crossover` 策略回测
- [ ] 运行 `volume_shrink` 策略回测
- [ ] 计算历史胜率和收益率
- [ ] 结合市场情绪筛选推荐
- [ ] 生成Top 3推荐

**Files to Create/Modify**:
- `src/business/post_market/actionable_insights.py` (new)

**Implementation Steps**:
1. 创建生成器类
2. 集成回测引擎
3. 实现策略回测逻辑
4. 实现胜率计算
5. 实现市场情绪匹配
6. 实现综合评分
7. 编写单元测试

---

### Task 2.3: 明日锦囊API

**Priority**: P1 (应该有)  
**Estimated Time**: 2 hours  
**Dependencies**: Task 2.2

**Description**: 将明日锦囊集成到API中

**Acceptance Criteria**:
- [ ] 在报告生成流程中调用明日锦囊生成器
- [ ] 在API响应中包含明日锦囊数据
- [ ] 添加API测试

**Files to Create/Modify**:
- `src/business/post_market/review_generator.py` (update)
- `src/web/routes/post_market_review.py` (update)

---

### Task 2.4: 明日锦囊组件

**Priority**: P1 (应该有)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 2.3

**Description**: 实现明日锦囊展示组件

**Acceptance Criteria**:
- [ ] 创建 `ActionableInsights` 组件
- [ ] 显示Top 3推荐
- [ ] 显示历史胜率和收益率
- [ ] 显示推荐股票
- [ ] 实现"加入明日关注"按钮
- [ ] 实现"设置闹钟"按钮

**Files to Create/Modify**:
- `frontend/src/components/post_market/ActionableInsights.tsx` (new)
- `frontend/src/components/post_market/ActionableInsights.css` (new)

---

### Task 2.5: 历史胜率验证

**Priority**: P1 (应该有)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 2.2

**Description**: 实现历史胜率验证逻辑

**Acceptance Criteria**:
- [ ] 计算30天、90天、1年胜率
- [ ] 过滤低胜率推荐（< 50%）
- [ ] 显示推荐次数和成功次数
- [ ] 每周更新历史数据

**Files to Create/Modify**:
- `src/business/post_market/win_rate_calculator.py` (new)

---

## Phase 3: 高级功能 (Week 5-6)

### Task 3.1: 明日提醒功能

**Priority**: P2 (可以有)  
**Estimated Time**: 6 hours  
**Dependencies**: Task 2.4

**Description**: 实现开盘前提醒功能

**Acceptance Criteria**:
- [ ] 实现 `POST /api/insights/subscribe` 接口
- [ ] 支持多种通知方式（App推送、邮件）
- [ ] 在开盘前15分钟发送通知
- [ ] 允许用户自定义提醒时间
- [ ] 记录提醒发送状态

**Files to Create/Modify**:
- `src/web/routes/post_market_review.py` (update)
- `src/business/notifications/reminder_service.py` (new)
- `scripts/reminder_scheduler.py` (new)

---

### Task 3.2: 历史复盘查看

**Priority**: P2 (可以有)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 1.5

**Description**: 实现查看历史复盘报告功能

**Acceptance Criteria**:
- [ ] 实现 `GET /api/post-market-review/history` 接口
- [ ] 支持日期范围查询
- [ ] 前端添加历史查看页面
- [ ] 支持日期选择器

**Files to Create/Modify**:
- `src/web/routes/post_market_review.py` (update)
- `frontend/src/pages/PostMarketReviewHistory.tsx` (new)

---

### Task 3.3: 一键导出功能

**Priority**: P2 (可以有)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 1.6

**Description**: 实现复盘报告导出功能

**Acceptance Criteria**:
- [ ] 支持导出为PDF
- [ ] 支持导出为图片（用于分享）
- [ ] 添加导出按钮
- [ ] 优化导出格式

**Files to Create/Modify**:
- `src/business/post_market/report_exporter.py` (new)
- `frontend/src/components/post_market/ExportButton.tsx` (new)

---

### Task 3.4: KPI监控系统

**Priority**: P3 (未来考虑)  
**Estimated Time**: 8 hours  
**Dependencies**: Task 1.10

**Description**: 实现产品KPI监控

**Acceptance Criteria**:
- [ ] 记录PMU（晚间活跃用户）
- [ ] 记录Decision Conversion（决策转化率）
- [ ] 记录Average Drawdown（平均回撤）
- [ ] 每日生成KPI报告
- [ ] 添加告警机制

**Files to Create/Modify**:
- `src/business/analytics/kpi_tracker.py` (new)
- `scripts/generate_kpi_report.py` (new)

---

## Code Cleanup Tasks

### Task C.1: 归档诊断模块

**Priority**: P1 (应该有)  
**Estimated Time**: 2 hours  
**Dependencies**: Task 1.10

**Description**: 将诊断模块移动到archive目录

**Acceptance Criteria**:
- [ ] 移动 `src/business/diagnosis/` 到 `archive/diagnosis/`
- [ ] 移动 `src/web/routes/diagnosis.py` 到 `archive/diagnosis/`
- [ ] 移动前端诊断组件到 `archive/diagnosis/components/`
- [ ] 移动相关文档到 `archive/docs/`
- [ ] 更新导入引用

**Files to Move**:
- `src/business/diagnosis/` → `archive/diagnosis/`
- `src/web/routes/diagnosis.py` → `archive/diagnosis/`
- `frontend/src/pages/StockDiagnosis.tsx` → `archive/diagnosis/`
- `frontend/src/components/diagnosis/` → `archive/diagnosis/components/`
- `DIAGNOSIS_*.md` → `archive/docs/`

---

### Task C.2: 归档选股器模块

**Priority**: P1 (应该有)  
**Estimated Time**: 2 hours  
**Dependencies**: Task 1.10

**Description**: 将选股器模块移动到archive目录

**Acceptance Criteria**:
- [ ] 移动 `src/web/routes/picker.py` 到 `archive/picker/`
- [ ] 移动前端选股器组件到 `archive/picker/components/`
- [ ] 移动相关文档到 `archive/docs/`
- [ ] 更新导入引用

**Files to Move**:
- `src/web/routes/picker.py` → `archive/picker/`
- `frontend/src/pages/SimplePicker.premium.tsx` → `archive/picker/`
- `frontend/src/components/picker/` → `archive/picker/components/`

---

### Task C.3: 归档其他策略

**Priority**: P1 (应该有)  
**Estimated Time**: 1 hour  
**Dependencies**: Task 1.10

**Description**: 将不需要的策略移动到archive目录

**Acceptance Criteria**:
- [ ] 移动 `src/business/strategies/reverse_value.py` 到 `archive/strategies/`
- [ ] 移动相关文档到 `archive/docs/`

**Files to Move**:
- `src/business/strategies/reverse_value.py` → `archive/strategies/`
- `REVERSE_VALUE_*.md` → `archive/docs/`
- `HOWARD_MARKS_*.md` → `archive/docs/`

---

## Testing Tasks

### Task T.1: 单元测试

**Priority**: P0 (必须)  
**Estimated Time**: 8 hours  
**Dependencies**: Phase 1 tasks

**Description**: 为所有核心模块编写单元测试

**Acceptance Criteria**:
- [ ] 测试市场情绪计算器
- [ ] 测试持仓健康检查器
- [ ] 测试明日锦囊生成器
- [ ] 测试复盘报告生成器
- [ ] 代码覆盖率 > 80%

**Files to Create**:
- `tests/test_market_sentiment.py`
- `tests/test_portfolio_health.py`
- `tests/test_actionable_insights.py`
- `tests/test_review_generator.py`

---

### Task T.2: API测试

**Priority**: P0 (必须)  
**Estimated Time**: 4 hours  
**Dependencies**: Task 1.5

**Description**: 为所有API接口编写测试

**Acceptance Criteria**:
- [ ] 测试获取报告接口
- [ ] 测试导入持仓接口
- [ ] 测试手动生成接口
- [ ] 测试错误处理

**Files to Create**:
- `tests/test_post_market_review_api.py`

---

### Task T.3: 端到端测试

**Priority**: P0 (必须)  
**Estimated Time**: 4 hours  
**Dependencies**: Phase 1 tasks

**Description**: 编写完整流程的端到端测试

**Acceptance Criteria**:
- [ ] 测试完整的报告生成流程
- [ ] 测试前端页面加载
- [ ] 测试用户交互
- [ ] 测试调度器触发

**Files to Create**:
- `tests/test_post_market_review_e2e.py`

---

## Documentation Tasks

### Task D.1: API文档

**Priority**: P0 (必须)  
**Estimated Time**: 2 hours  
**Dependencies**: Task 1.5

**Description**: 编写API文档

**Files to Create**:
- `docs/POST_MARKET_REVIEW_API.md`

---

### Task D.2: 用户指南

**Priority**: P0 (必须)  
**Estimated Time**: 2 hours  
**Dependencies**: Task 1.10

**Description**: 编写用户使用指南

**Files to Create**:
- `docs/POST_MARKET_REVIEW_USER_GUIDE.md`

---

### Task D.3: 开发者文档

**Priority**: P1 (应该有)  
**Estimated Time**: 2 hours  
**Dependencies**: Task 1.10

**Description**: 编写开发者文档

**Files to Create**:
- `docs/POST_MARKET_REVIEW_DEVELOPER_GUIDE.md`

---

## Summary

### Phase 1 (MVP): 10 tasks, ~38 hours
- 核心功能：市场情绪、持仓健康、自动触发
- 目标：2周内完成可用的MVP

### Phase 2 (明日锦囊): 5 tasks, ~20 hours
- 高级功能：明日锦囊、历史胜率验证
- 目标：2周内完成完整功能

### Phase 3 (扩展): 4 tasks, ~22 hours
- 扩展功能：提醒、历史查看、导出、KPI监控
- 目标：2周内完成高级功能

### Cleanup: 3 tasks, ~5 hours
- 代码清理：归档不需要的模块

### Testing: 3 tasks, ~16 hours
- 测试：单元测试、API测试、端到端测试

### Documentation: 3 tasks, ~6 hours
- 文档：API文档、用户指南、开发者文档

**Total Estimated Time**: ~107 hours (~13 working days)

---

## Next Steps

1. Review and approve this task breakdown
2. Start with Phase 1 MVP tasks
3. Complete Task 1.1 (Database Design) first
4. Then proceed with parallel development of backend and frontend
5. Test and iterate

Ready to start implementation! 🚀

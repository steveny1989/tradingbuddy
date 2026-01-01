# Implementation Plan: Trading UI System

## Overview

本实现计划将TradingBuddy UI System分解为可执行的开发任务。采用前后端并行开发的方式，先搭建基础架构，再逐步实现各个功能模块。每个任务都明确引用了相关的需求条款，确保实现的可追溯性。

## Tasks

- [x] 1. 项目初始化和基础架构搭建
  - 创建前端项目结构（React + Vite + TypeScript）
  - 创建后端项目结构（Flask + Blueprint）
  - 配置开发环境和构建工具
  - 设置代码规范（ESLint, Prettier, Black）
  - _Requirements: 所有需求的基础_

- [x] 2. 后端API基础框架
  - [x] 2.1 实现Flask应用主入口和配置
    - 创建 `src/web/app.py` 主应用文件
    - 配置CORS、日志、错误处理
    - 设置开发和生产环境配置
    - _Requirements: 11.1_

  - [x] 2.2 实现统一的API响应格式和错误处理
    - 创建响应辅助函数（success_response, error_response）
    - 实现全局异常处理器
    - 定义标准错误码
    - _Requirements: 11.10_

  - [x] 2.3 编写API错误响应格式的属性测试
    - **Property 37: API error responses follow standard format**
    - **Validates: Requirements 11.10**

- [x] 3. 股票数据API实现
  - [x] 3.1 实现股票列表API
    - 创建 `/api/stocks` GET端点
    - 支持分页、市场筛选、市值范围筛选
    - 连接现有的 `StockDatabase.get_stock_list()`
    - _Requirements: 2.1, 11.2_

  - [x] 3.2 实现股票详情API
    - 创建 `/api/stocks/{code}` GET端点
    - 返回股票基本信息、市值、行业
    - _Requirements: 2.3, 11.3_

  - [x] 3.3 实现日线数据API
    - 创建 `/api/stocks/{code}/daily` GET端点
    - 支持日期范围筛选
    - 连接现有的 `StockDatabase.get_daily_data()`
    - _Requirements: 2.4, 2.7, 11.4_

  - [x] 3.4 实现技术指标计算API
    - 创建 `/api/stocks/{code}/indicators` GET端点
    - 计算MA5, MA10, MA20, MA60
    - _Requirements: 2.5_

  - [x] 3.5 编写股票API的单元测试
    - 测试各个端点的正常响应
    - 测试参数验证
    - 测试错误情况（股票不存在等）
    - _Requirements: 2.1, 2.3, 2.4, 2.5_

- [x] 4. 策略管理API实现
  - [x] 4.1 实现策略列表API
    - 创建 `/api/strategies` GET端点
    - 返回所有可用策略及其配置参数
    - 连接现有的策略类（VolumeShrinkStrategy, MACrossoverStrategy）
    - _Requirements: 3.1, 11.5_

  - [x] 4.2 实现策略详情和配置API
    - 创建 `/api/strategies/{id}` GET端点
    - 创建 `/api/strategies/{id}/config` GET/PUT端点
    - 实现参数验证逻辑
    - _Requirements: 3.2, 3.3, 3.6_

  - [x] 4.3 实现回测执行API
    - 创建 `/api/strategies/{id}/backtest` POST端点
    - 异步执行回测任务
    - 返回任务ID和状态
    - 连接现有的 `BacktestEngine`
    - _Requirements: 3.4, 11.6_

  - [ ] 4.4 编写策略API的单元测试
    - 测试策略列表返回
    - 测试参数验证
    - 测试回测任务创建
    - _Requirements: 3.1, 3.2, 3.4, 3.6_

- [ ] 5. 回测结果API实现
  - [x] 5.1 实现回测历史列表API
    - 创建 `/api/backtest` GET端点
    - 支持分页和策略筛选
    - 从数据库读取历史回测记录
    - _Requirements: 4.1, 11.7_

  - [ ] 5.2 实现回测详情API
    - 创建 `/api/backtest/{id}` GET端点
    - 返回完整的回测结果（指标、曲线、交易记录）
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6_

  - [ ] 5.3 实现交易记录导出API
    - 创建 `/api/backtest/{id}/export` GET端点
    - 生成CSV文件下载
    - _Requirements: 4.7_

  - [ ]* 5.4 编写回测API的单元测试
    - 测试回测列表返回
    - 测试回测详情返回
    - 测试CSV导出功能
    - _Requirements: 4.1, 4.2, 4.7_

- [ ] 6. 模拟盘API实现
  - [ ] 6.1 实现模拟盘状态API
    - 创建 `/api/paper-trading/status` GET端点
    - 返回账户状态、持仓、今日交易
    - 连接现有的模拟盘系统
    - _Requirements: 5.1, 5.2, 5.3, 11.8_

  - [ ] 6.2 实现模拟盘控制API
    - 创建 `/api/paper-trading/start` POST端点
    - 创建 `/api/paper-trading/stop` POST端点
    - 创建 `/api/paper-trading/reset` POST端点
    - _Requirements: 5.7, 5.8_

  - [ ] 6.3 实现模拟盘绩效API
    - 创建 `/api/paper-trading/performance` GET端点
    - 返回资金曲线和绩效指标
    - _Requirements: 5.4_

  - [x] 6.4 编写模拟盘API的单元测试
    - 测试状态查询
    - 测试启动/停止/重置操作
    - 测试绩效数据返回
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.7, 5.8_

- [ ] 7. 数据管理API实现
  - [ ] 7.1 实现数据同步状态API
    - 创建 `/api/data/status` GET端点
    - 创建 `/api/data/stocks-status` GET端点
    - 返回数据库状态和每只股票的同步状态
    - _Requirements: 1.2, 6.1, 6.2_

  - [ ] 7.2 实现数据同步控制API
    - 创建 `/api/data/sync` POST端点
    - 创建 `/api/data/sync/{task_id}` GET端点
    - 支持全量和增量同步
    - 实现异步任务和进度跟踪
    - 连接现有的 `DataFetcher`
    - _Requirements: 6.3, 6.4, 6.5, 6.6, 6.7, 11.9_

  - [ ]* 7.3 编写数据管理API的单元测试
    - 测试状态查询
    - 测试同步任务创建
    - 测试进度跟踪
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

- [ ] 8. 仪表板API实现
  - [x] 8.1 实现仪表板摘要API
    - 创建 `/api/dashboard/summary` GET端点
    - 聚合数据库状态、模拟盘状态、最近回测
    - _Requirements: 1.2, 1.3, 1.4_

  - [ ]* 8.2 编写仪表板API的单元测试
    - 测试摘要数据返回
    - 测试数据聚合逻辑
    - _Requirements: 1.2, 1.3, 1.4_

- [ ] 9. Checkpoint - 后端API完成
  - 确保所有API端点正常工作
  - 运行所有后端测试
  - 测试API文档和示例
  - 询问用户是否有问题

- [ ] 10. 前端项目初始化
  - [x] 10.1 创建React项目和基础配置
    - 使用Vite创建TypeScript项目
    - 安装依赖（React Router, Ant Design, ECharts, Axios）
    - 配置路由和状态管理
    - _Requirements: 所有前端需求的基础_

  - [x] 10.2 创建布局组件
    - 实现 `AppLayout` 主布局组件
    - 实现 `Sidebar` 侧边导航组件
    - 实现 `Header` 顶部导航组件
    - _Requirements: 12.2, 12.3_

  - [x] 10.3 实现通用组件
    - 实现 `LoadingSpinner` 加载指示器
    - 实现 `ErrorBoundary` 错误边界
    - 实现 `ConfirmDialog` 确认对话框
    - 配置 `Notification` 通知组件
    - _Requirements: 9.2, 10.1, 10.2, 10.3, 10.6_

  - [ ]* 10.4 编写布局和通用组件的单元测试
    - 测试布局组件渲染
    - 测试导航菜单内容
    - 测试错误边界捕获
    - _Requirements: 12.2, 12.3, 10.6_

  - [ ]* 10.5 编写导航菜单的属性测试
    - **Property 32: Navigation menu contains all main sections**
    - **Validates: Requirements 12.3**

- [ ] 11. 仪表板页面实现
  - [x] 11.1 实现Dashboard页面组件
    - 创建 `DashboardPage` 主组件
    - 实现 `SystemStatusCard` 数据库状态卡片
    - 实现 `PaperTradingCard` 模拟盘概览卡片
    - 实现 `RecentBacktestCard` 最近回测卡片
    - 集成 `/api/dashboard/summary` API
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

  - [ ]* 11.2 编写Dashboard组件的单元测试
    - 测试页面渲染
    - 测试各个卡片显示
    - 测试数据加载状态
    - _Requirements: 1.1, 1.2, 1.3, 1.4_

  - [ ]* 11.3 编写Dashboard显示属性测试
    - **Property 1: Dashboard displays all required database status fields**
    - **Property 2: Dashboard displays all required paper trading fields**
    - **Property 3: Dashboard displays all required backtest summary fields**
    - **Validates: Requirements 1.2, 1.3, 1.4**

- [ ] 12. 股票浏览功能实现
  - [x] 12.1 实现股票列表页面
    - 创建 `StockListPage` 主组件
    - 实现 `StockTable` 表格组件（支持排序、筛选、分页）
    - 实现 `SearchBar` 搜索组件
    - 实现 `FilterPanel` 筛选面板
    - 集成 `/api/stocks` API
    - _Requirements: 2.1, 2.2, 12.7, 12.8_

  - [ ] 12.2 实现股票详情页面
    - 创建 `StockDetailPage` 主组件
    - 实现 `StockInfo` 基本信息组件
    - 实现 `TechnicalIndicators` 技术指标组件
    - 集成 `/api/stocks/{code}` API
    - _Requirements: 2.3_

  - [ ] 12.3 实现K线图组件
    - 创建 `KLineChart` 图表组件
    - 使用ECharts渲染K线图和成交量
    - 支持技术指标叠加（MA5, MA10, MA20, MA60）
    - 实现时间范围选择器
    - 实现缩放和平移功能
    - 集成 `/api/stocks/{code}/daily` API
    - _Requirements: 2.4, 2.5, 2.6, 2.7, 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

  - [ ]* 12.4 编写股票浏览组件的单元测试
    - 测试股票列表渲染
    - 测试搜索功能
    - 测试详情页面渲染
    - 测试K线图渲染
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ]* 12.5 编写股票浏览的属性测试
    - **Property 4: Stock list displays all required fields**
    - **Property 5: Stock search filters correctly**
    - **Property 6: K-line chart includes all technical indicators**
    - **Property 7: Time range change updates chart data**
    - **Property 18: K-line chart renders with correct data format**
    - **Property 19: Chart supports all moving average indicators**
    - **Property 20: Chart uses configurable color scheme**
    - **Validates: Requirements 2.1, 2.2, 2.5, 2.7, 7.1, 7.3, 7.7**

- [ ] 13. 策略管理功能实现
  - [ ] 13.1 实现策略列表页面
    - 创建 `StrategyListPage` 主组件
    - 实现 `StrategyCard` 策略卡片组件
    - 实现 `StrategyConfigModal` 配置对话框
    - 集成 `/api/strategies` API
    - _Requirements: 3.1, 3.2, 3.3_

  - [ ] 13.2 实现策略配置和回测功能
    - 实现参数配置表单
    - 实现表单验证
    - 实现回测执行按钮和进度显示
    - 实现策略启用/禁用开关
    - 集成 `/api/strategies/{id}/backtest` API
    - _Requirements: 3.3, 3.4, 3.5, 3.6_

  - [ ]* 13.3 编写策略管理组件的单元测试
    - 测试策略列表渲染
    - 测试配置对话框
    - 测试表单验证
    - 测试回测触发
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.6_

  - [ ]* 13.4 编写策略管理的属性测试
    - **Property 8: Strategy list displays all required fields**
    - **Property 9: Invalid strategy parameters show validation errors**
    - **Validates: Requirements 3.1, 3.6**

- [ ] 14. 回测结果功能实现
  - [ ] 14.1 实现回测历史列表页面
    - 创建 `BacktestListPage` 主组件
    - 实现回测记录表格
    - 集成 `/api/backtest` API
    - _Requirements: 4.1_

  - [ ] 14.2 实现回测详情页面
    - 创建 `BacktestResultPage` 主组件
    - 实现 `PerformanceMetrics` 绩效指标组件
    - 实现 `EquityCurve` 资金曲线图组件
    - 实现 `TradeTable` 交易记录表格
    - 实现CSV导出功能
    - 集成 `/api/backtest/{id}` API
    - _Requirements: 4.2, 4.3, 4.4, 4.5, 4.6, 4.7, 4.8_

  - [ ]* 14.3 编写回测结果组件的单元测试
    - 测试回测列表渲染
    - 测试详情页面渲染
    - 测试绩效指标显示
    - 测试交易记录表格
    - 测试CSV导出
    - _Requirements: 4.1, 4.2, 4.3, 4.6, 4.7_

  - [ ]* 14.4 编写回测结果的属性测试
    - **Property 10: Backtest list displays all required fields**
    - **Property 11: Backtest metrics display all required indicators**
    - **Property 12: Trade table displays all required fields**
    - **Validates: Requirements 4.1, 4.3, 4.6**

- [ ] 15. 模拟盘监控功能实现
  - [ ] 15.1 实现模拟盘监控页面
    - 创建 `PaperTradingPage` 主组件
    - 实现 `AccountSummary` 账户概览组件
    - 实现 `PositionTable` 持仓列表组件
    - 实现 `TradeHistory` 交易历史组件
    - 实现历史绩效曲线图
    - 集成 `/api/paper-trading/status` API
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

  - [ ] 15.2 实现模拟盘控制功能
    - 实现自动刷新机制（30秒）
    - 实现手动刷新按钮
    - 实现启动/停止按钮
    - 实现重置账户功能（带确认对话框）
    - 集成控制API
    - _Requirements: 5.5, 5.6, 5.7, 5.8_

  - [ ]* 15.3 编写模拟盘监控组件的单元测试
    - 测试页面渲染
    - 测试账户概览显示
    - 测试持仓列表显示
    - 测试交易历史显示
    - 测试控制按钮
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.6, 5.7, 5.8_

  - [ ]* 15.4 编写模拟盘监控的属性测试
    - **Property 13: Paper trading account displays all required fields**
    - **Property 14: Position list displays all required fields**
    - **Property 15: Today's trades display all required fields**
    - **Property 16: Paper trading auto-refresh triggers correctly**
    - **Validates: Requirements 5.1, 5.2, 5.3, 5.5**

- [ ] 16. 数据管理功能实现
  - [ ] 16.1 实现数据管理页面
    - 创建 `DataManagementPage` 主组件
    - 实现 `SyncStatusTable` 同步状态表格
    - 实现 `SyncControlPanel` 控制面板
    - 实现进度条和状态显示
    - 集成数据管理API
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [ ]* 16.2 编写数据管理组件的单元测试
    - 测试页面渲染
    - 测试同步状态表格
    - 测试控制按钮
    - 测试进度显示
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 16.3 编写数据管理的属性测试
    - **Property 17: Sync status table displays all required fields**
    - **Validates: Requirements 6.2**

- [ ] 17. 响应式设计和性能优化
  - [ ] 17.1 实现响应式布局
    - 添加媒体查询和断点
    - 实现移动端布局
    - 调整触摸友好的按钮尺寸
    - 隐藏移动端次要功能
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6_

  - [ ] 17.2 实现性能优化
    - 实现分页和虚拟滚动
    - 实现数据缓存机制
    - 实现图表数据抽样
    - 实现组件懒加载
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5, 9.6_

  - [ ]* 17.3 编写响应式和性能的属性测试
    - **Property 21: Responsive layout switches at correct breakpoint**
    - **Property 22: Touch-friendly button sizes**
    - **Property 23: Mobile layout hides secondary features**
    - **Property 24: Long lists use pagination**
    - **Property 25: Stock data is cached to avoid duplicate requests**
    - **Property 26: Large chart datasets use data sampling**
    - **Property 27: Lazy loading for large components**
    - **Validates: Requirements 8.4, 8.5, 8.6, 9.3, 9.4, 9.5, 9.6**

- [ ] 18. 错误处理和用户反馈
  - [ ] 18.1 实现全局错误处理
    - 配置Axios拦截器处理API错误
    - 实现友好的错误提示
    - 实现离线检测和提示
    - _Requirements: 10.1, 10.5_

  - [ ] 18.2 实现用户反馈机制
    - 实现成功通知（自动消失）
    - 实现危险操作确认对话框
    - 实现表单验证错误提示
    - 实现加载状态和按钮禁用
    - _Requirements: 10.2, 10.3, 10.4, 12.4_

  - [ ]* 18.3 编写错误处理和反馈的属性测试
    - **Property 28: API errors display friendly messages**
    - **Property 29: Success notifications auto-dismiss**
    - **Property 30: Dangerous operations show confirmation**
    - **Property 31: Form validation shows specific errors**
    - **Property 33: Loading operations disable buttons**
    - **Validates: Requirements 10.1, 10.2, 10.3, 10.4, 12.4**

- [ ] 19. 用户体验优化
  - [ ] 19.1 实现用户偏好设置
    - 实现本地存储保存偏好
    - 实现图表配色切换
    - 实现默认时间范围设置
    - _Requirements: 12.5_

  - [ ] 19.2 实现键盘快捷键
    - 实现搜索框快捷键（/）
    - 实现其他常用快捷键
    - _Requirements: 12.6_

  - [ ]* 19.3 编写用户体验的属性测试
    - **Property 34: User preferences persist to local storage**
    - **Property 35: Table sorting works correctly**
    - **Property 36: Table filtering works correctly**
    - **Validates: Requirements 12.5, 12.7, 12.8**

- [ ] 20. 财务数据后端API实现
  - [ ] 20.1 实现财务报表API
    - 创建 `/api/stocks/{code}/financials` GET端点
    - 支持报表类型筛选（资产负债表、利润表、现金流量表）
    - 支持报告期类型筛选（季报、年报）
    - 连接财务数据库表
    - _Requirements: 11.11, 13.2_

  - [ ] 20.2 实现财务指标API
    - 创建 `/api/stocks/{code}/indicators/financial` GET端点
    - 返回盈利能力、偿债能力、估值、成长性指标
    - 支持时间序列查询
    - _Requirements: 11.12, 13.3, 13.4, 13.5_

  - [ ] 20.3 实现财务数据同步API
    - 创建 `/api/data/sync/financials` POST端点
    - 创建 `/api/data/financials-status` GET端点
    - 实现异步财务数据同步任务
    - 连接财务数据获取模块
    - _Requirements: 11.13, 14.1, 14.2, 14.3_

  - [ ]* 20.4 编写财务数据API的单元测试
    - 测试财务报表API返回
    - 测试财务指标API返回
    - 测试同步任务创建
    - 测试数据格式验证
    - _Requirements: 13.2, 13.3, 14.2_

- [ ] 21. 财务数据前端功能实现
  - [ ] 21.1 实现财务数据页面
    - 创建 `FinancialDataPage` 主组件（作为股票详情页的标签页）
    - 实现 `FinancialStatementsTable` 财务报表表格
    - 实现 `PeriodSelector` 报告期选择器
    - 集成财务报表API
    - _Requirements: 13.1, 13.2, 13.6_

  - [ ] 21.2 实现财务指标展示
    - 实现 `FinancialIndicatorsCard` 指标卡片组件
    - 展示盈利能力指标（ROE、ROA、毛利率、净利率）
    - 展示偿债能力指标（资产负债率、流动比率、速动比率）
    - 展示估值指标（PE、PB、PS）
    - 展示成长性指标（营收增长率、净利润增长率）
    - _Requirements: 13.3, 13.4, 13.5_

  - [ ] 21.3 实现财务数据图表
    - 创建 `FinancialIndicatorsChart` 图表组件
    - 使用ECharts渲染时间序列图表
    - 支持多指标对比
    - 支持最近8个季度数据展示
    - _Requirements: 13.7_

  - [ ] 21.4 实现财务数据管理功能
    - 在数据管理页面添加财务数据同步状态表格
    - 实现"同步财务数据"按钮
    - 实现财务数据同步进度显示
    - 集成财务数据同步API
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7_

  - [ ]* 21.5 编写财务数据组件的单元测试
    - 测试财务报表表格渲染
    - 测试财务指标卡片显示
    - 测试图表渲染
    - 测试报告期切换
    - _Requirements: 13.2, 13.3, 13.7_

  - [ ]* 21.6 编写财务数据的属性测试
    - **Property 38: Financial statements display all required fields**
    - **Property 39: Financial indicators display all required categories**
    - **Property 40: Financial data time series chart renders correctly**
    - **Property 41: Financial sync status displays all required fields**
    - **Validates: Requirements 13.2, 13.3, 13.7, 14.2**

- [ ] 22. Checkpoint - 财务数据功能完成
  - 确保所有财务数据API正常工作
  - 运行所有财务数据相关测试
  - 测试财务数据同步功能
  - 验证前端财务数据展示
  - 询问用户是否有问题

- [ ] 23. Final Checkpoint - 集成测试和部署准备
  - 运行所有前端和后端测试
  - 进行端到端集成测试
  - 检查所有功能是否正常工作（包括财务数据）
  - 优化性能和加载速度
  - 准备生产环境配置
  - 编写部署文档
  - 询问用户是否有问题

## Notes

- 任务标记 `*` 的为可选任务，可以跳过以加快MVP开发
- 每个任务都引用了具体的需求条款，确保实现的可追溯性
- Checkpoint任务用于阶段性验证，确保增量开发的质量
- 属性测试使用fast-check（前端）和Hypothesis（后端），每个测试至少运行100次
- 单元测试和属性测试是互补的，共同保证代码质量

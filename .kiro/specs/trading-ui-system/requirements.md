# Requirements Document - Trading UI System

## Introduction

TradingBuddy量化交易系统的Web用户界面，为用户提供直观的数据查看、策略管理、回测分析和模拟盘监控功能。系统采用现代Web技术栈，提供响应式、交互式的用户体验。

## Glossary

- **UI_System**: 用户界面系统，提供Web界面访问TradingBuddy功能
- **Dashboard**: 仪表板，展示系统概览和关键指标
- **Strategy_Manager**: 策略管理器，管理和配置交易策略
- **Backtest_Viewer**: 回测查看器，展示回测结果和分析
- **Paper_Trading_Monitor**: 模拟盘监控器，实时监控模拟交易
- **Stock_Explorer**: 股票浏览器，查看和分析个股数据
- **Chart_Component**: 图表组件，渲染K线图和技术指标
- **Data_Sync_Status**: 数据同步状态，显示数据更新进度
- **Backend_API**: 后端API，连接业务层和数据层
- **Session**: 用户会话，管理用户状态
- **Financial_Data**: 财务数据，包括三大报表和财务指标
- **Balance_Sheet**: 资产负债表，展示公司资产、负债和所有者权益
- **Income_Statement**: 利润表，展示公司收入、成本和利润
- **Cash_Flow_Statement**: 现金流量表，展示公司现金流入流出
- **Financial_Indicators**: 财务指标，包括盈利能力、偿债能力、成长性等指标

## Requirements

### Requirement 1: 系统仪表板

**User Story:** 作为量化交易者，我想看到系统的整体状态和关键指标，以便快速了解系统运行情况。

#### Acceptance Criteria

1. WHEN 用户访问首页 THEN THE UI_System SHALL 显示仪表板页面
2. THE Dashboard SHALL 展示数据库状态（股票数量、最新更新时间、数据完整性）
3. THE Dashboard SHALL 展示模拟盘概览（账户余额、持仓数量、当日收益率）
4. THE Dashboard SHALL 展示最近回测结果摘要（策略名称、收益率、最大回撤）
5. WHEN 数据同步正在进行 THEN THE Dashboard SHALL 显示实时进度条和状态信息

### Requirement 2: 股票数据浏览

**User Story:** 作为量化交易者，我想浏览和查询股票数据，以便分析个股表现和技术形态。

#### Acceptance Criteria

1. THE Stock_Explorer SHALL 提供股票列表视图，显示代码、名称、市值、行业
2. WHEN 用户输入股票代码或名称 THEN THE Stock_Explorer SHALL 过滤并显示匹配结果
3. WHEN 用户选择一只股票 THEN THE Stock_Explorer SHALL 显示该股票的详细信息页面
4. THE Stock_Explorer SHALL 在详细页面展示K线图（日线数据）
5. THE Stock_Explorer SHALL 在K线图上叠加技术指标（MA5、MA10、MA20、成交量）
6. THE Stock_Explorer SHALL 提供时间范围选择器（1个月、3个月、6个月、1年、全部）
7. WHEN 用户调整时间范围 THEN THE Chart_Component SHALL 更新显示对应时间段的数据

### Requirement 3: 策略管理

**User Story:** 作为策略开发者，我想管理和配置交易策略，以便运行回测和模拟交易。

#### Acceptance Criteria

1. THE Strategy_Manager SHALL 显示所有可用策略列表（名称、类型、描述）
2. WHEN 用户选择一个策略 THEN THE Strategy_Manager SHALL 显示策略详细信息和参数配置界面
3. THE Strategy_Manager SHALL 允许用户修改策略参数（股票池范围、技术指标参数）
4. WHEN 用户点击"运行回测"按钮 THEN THE Strategy_Manager SHALL 触发回测任务并显示进度
5. THE Strategy_Manager SHALL 提供策略启用/禁用开关，用于模拟盘交易
6. WHEN 策略参数无效 THEN THE Strategy_Manager SHALL 显示验证错误信息

### Requirement 4: 回测结果展示

**User Story:** 作为量化交易者，我想查看详细的回测结果，以便评估策略表现和优化参数。

#### Acceptance Criteria

1. THE Backtest_Viewer SHALL 显示回测历史列表（策略名称、时间范围、收益率、回撤）
2. WHEN 用户选择一个回测记录 THEN THE Backtest_Viewer SHALL 显示详细结果页面
3. THE Backtest_Viewer SHALL 展示关键绩效指标（总收益率、年化收益率、最大回撤、夏普比率、胜率）
4. THE Backtest_Viewer SHALL 展示资金曲线图（账户价值随时间变化）
5. THE Backtest_Viewer SHALL 展示回撤曲线图（回撤百分比随时间变化）
6. THE Backtest_Viewer SHALL 展示交易记录表格（日期、股票、操作、价格、数量、盈亏）
7. THE Backtest_Viewer SHALL 提供交易记录导出功能（CSV格式）
8. WHEN 用户点击交易记录中的股票 THEN THE Backtest_Viewer SHALL 跳转到该股票的详细页面

### Requirement 5: 模拟盘监控

**User Story:** 作为量化交易者，我想实时监控模拟盘交易，以便验证策略在实盘环境的表现。

#### Acceptance Criteria

1. THE Paper_Trading_Monitor SHALL 显示账户概览（总资产、可用资金、持仓市值、当日盈亏）
2. THE Paper_Trading_Monitor SHALL 显示持仓列表（股票代码、名称、数量、成本价、现价、盈亏）
3. THE Paper_Trading_Monitor SHALL 显示今日交易记录（时间、股票、操作、价格、数量）
4. THE Paper_Trading_Monitor SHALL 显示历史绩效曲线（账户价值随时间变化）
5. WHEN 模拟盘正在运行 THEN THE Paper_Trading_Monitor SHALL 每30秒自动刷新数据
6. THE Paper_Trading_Monitor SHALL 提供手动刷新按钮
7. THE Paper_Trading_Monitor SHALL 提供启动/停止模拟盘的控制按钮
8. WHEN 用户点击"重置账户"按钮 THEN THE Paper_Trading_Monitor SHALL 显示确认对话框并执行重置

### Requirement 6: 数据管理

**User Story:** 作为系统管理员，我想管理数据同步和更新，以便保持数据的完整性和时效性。

#### Acceptance Criteria

1. THE UI_System SHALL 提供数据管理页面，显示数据同步状态
2. THE Data_Sync_Status SHALL 显示每只股票的同步状态（已同步、同步中、失败）
3. THE UI_System SHALL 提供"全量下载"按钮，触发全市场数据下载
4. THE UI_System SHALL 提供"增量更新"按钮，触发每日数据更新
5. WHEN 数据同步任务运行时 THEN THE Data_Sync_Status SHALL 显示实时进度（已完成/总数、当前股票）
6. WHEN 数据同步完成 THEN THE UI_System SHALL 显示成功通知和统计信息
7. IF 数据同步失败 THEN THE UI_System SHALL 显示错误信息和失败的股票列表

### Requirement 7: 图表可视化

**User Story:** 作为量化交易者，我想看到专业的金融图表，以便进行技术分析。

#### Acceptance Criteria

1. THE Chart_Component SHALL 渲染K线图（开盘价、收盘价、最高价、最低价）
2. THE Chart_Component SHALL 在K线图下方显示成交量柱状图
3. THE Chart_Component SHALL 支持叠加移动平均线（MA5、MA10、MA20、MA60）
4. THE Chart_Component SHALL 提供缩放功能（鼠标滚轮或触摸手势）
5. THE Chart_Component SHALL 提供平移功能（鼠标拖拽或触摸滑动）
6. WHEN 用户悬停在K线上 THEN THE Chart_Component SHALL 显示该日期的详细数据（日期、开高低收、成交量）
7. THE Chart_Component SHALL 使用专业的配色方案（涨红跌绿或涨绿跌红，可配置）

### Requirement 8: 响应式设计

**User Story:** 作为用户，我想在不同设备上使用系统，以便随时随地访问交易数据。

#### Acceptance Criteria

1. THE UI_System SHALL 在桌面浏览器上提供完整功能
2. THE UI_System SHALL 在平板设备上自动调整布局
3. THE UI_System SHALL 在手机浏览器上提供简化的移动版界面
4. WHEN 屏幕宽度小于768px THEN THE UI_System SHALL 切换到移动布局
5. THE UI_System SHALL 确保所有交互元素在触摸屏上可用（按钮大小≥44px）
6. THE UI_System SHALL 在移动设备上隐藏次要功能，保留核心功能

### Requirement 9: 性能和加载

**User Story:** 作为用户，我想快速加载页面和数据，以便高效使用系统。

#### Acceptance Criteria

1. WHEN 用户访问任何页面 THEN THE UI_System SHALL 在2秒内显示页面框架
2. WHEN 加载大量数据时 THEN THE UI_System SHALL 显示加载指示器
3. THE UI_System SHALL 使用分页或虚拟滚动处理长列表（每页50-100条）
4. THE UI_System SHALL 缓存已加载的股票数据，避免重复请求
5. WHEN 图表数据超过1000个数据点 THEN THE Chart_Component SHALL 使用数据抽样或聚合
6. THE UI_System SHALL 使用懒加载技术，按需加载图表库和大型组件

### Requirement 10: 错误处理和用户反馈

**User Story:** 作为用户，我想了解系统状态和操作结果，以便正确使用系统。

#### Acceptance Criteria

1. WHEN 后端API请求失败 THEN THE UI_System SHALL 显示友好的错误提示
2. WHEN 用户执行操作成功 THEN THE UI_System SHALL 显示成功通知（3秒后自动消失）
3. WHEN 用户执行危险操作（如重置账户）THEN THE UI_System SHALL 显示确认对话框
4. THE UI_System SHALL 在表单验证失败时显示具体的错误信息
5. WHEN 网络连接断开 THEN THE UI_System SHALL 显示离线提示并禁用需要网络的功能
6. THE UI_System SHALL 提供全局错误边界，捕获未处理的异常并显示错误页面

### Requirement 11: 后端API集成

**User Story:** 作为开发者，我想要清晰的前后端接口，以便实现UI功能。

#### Acceptance Criteria

1. THE Backend_API SHALL 提供RESTful接口，返回JSON格式数据
2. THE Backend_API SHALL 提供股票列表接口（GET /api/stocks）
3. THE Backend_API SHALL 提供股票详情接口（GET /api/stocks/{code}）
4. THE Backend_API SHALL 提供日线数据接口（GET /api/stocks/{code}/daily）
5. THE Backend_API SHALL 提供策略列表接口（GET /api/strategies）
6. THE Backend_API SHALL 提供回测执行接口（POST /api/backtest）
7. THE Backend_API SHALL 提供回测结果接口（GET /api/backtest/{id}）
8. THE Backend_API SHALL 提供模拟盘状态接口（GET /api/paper-trading/status）
9. THE Backend_API SHALL 提供数据同步接口（POST /api/data/sync）
10. WHEN API请求失败 THEN THE Backend_API SHALL 返回标准错误格式（状态码、错误消息、错误代码）
11. THE Backend_API SHALL 提供财务数据接口（GET /api/stocks/{code}/financials）
12. THE Backend_API SHALL 提供财务指标接口（GET /api/stocks/{code}/indicators/financial）
13. THE Backend_API SHALL 提供财务数据同步接口（POST /api/data/sync/financials）

### Requirement 12: 用户体验优化

**User Story:** 作为用户，我想要流畅和直观的操作体验，以便高效完成任务。

#### Acceptance Criteria

1. THE UI_System SHALL 使用一致的视觉设计语言（颜色、字体、间距）
2. THE UI_System SHALL 提供面包屑导航，显示当前位置
3. THE UI_System SHALL 在侧边栏提供主导航菜单（仪表板、股票、策略、回测、模拟盘、数据）
4. WHEN 用户执行耗时操作 THEN THE UI_System SHALL 禁用操作按钮并显示加载状态
5. THE UI_System SHALL 保存用户的偏好设置（图表配色、默认时间范围）到浏览器本地存储
6. THE UI_System SHALL 提供键盘快捷键（如按"/"聚焦搜索框）
7. THE UI_System SHALL 在表格中提供排序功能（点击列标题）
8. THE UI_System SHALL 在表格中提供筛选功能（输入框或下拉菜单）

### Requirement 13: 财务数据查看

**User Story:** 作为量化交易者，我想查看公司的财务报表和分析指标，以便进行基本面分析和价值投资。

#### Acceptance Criteria

1. THE Stock_Explorer SHALL 在股票详情页面提供财务数据标签页
2. THE Stock_Explorer SHALL 展示三大财务报表（资产负债表、利润表、现金流量表）
3. THE Stock_Explorer SHALL 展示关键财务指标（ROE、ROA、毛利率、净利率、资产负债率、流动比率、速动比率）
4. THE Stock_Explorer SHALL 展示估值指标（PE、PB、PS、市净率、市销率）
5. THE Stock_Explorer SHALL 展示成长性指标（营收增长率、净利润增长率、ROE增长率）
6. WHEN 用户选择报告期 THEN THE Stock_Explorer SHALL 显示对应期间的财务数据
7. THE Stock_Explorer SHALL 提供财务数据的时间序列图表（最近8个季度）
8. THE Stock_Explorer SHALL 支持同行业公司财务指标对比
9. WHEN 财务数据不可用 THEN THE Stock_Explorer SHALL 显示友好提示信息

### Requirement 14: 财务数据管理

**User Story:** 作为系统管理员，我想管理财务数据的同步和更新，以便保持财务数据的完整性和时效性。

#### Acceptance Criteria

1. THE UI_System SHALL 在数据管理页面显示财务数据同步状态
2. THE Data_Sync_Status SHALL 显示每只股票的财务数据同步状态（已同步、同步中、失败、无数据）
3. THE UI_System SHALL 提供"同步财务数据"按钮，触发财务数据下载
4. WHEN 财务数据同步任务运行时 THEN THE Data_Sync_Status SHALL 显示实时进度
5. WHEN 财务数据同步完成 THEN THE UI_System SHALL 显示成功通知和统计信息
6. IF 财务数据同步失败 THEN THE UI_System SHALL 显示错误信息和失败的股票列表
7. THE UI_System SHALL 显示财务数据的最后更新时间和数据覆盖率

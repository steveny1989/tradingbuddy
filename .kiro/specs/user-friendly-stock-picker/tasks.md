# Implementation Plan: 极简选股助手

## Overview

本实现计划将"极简选股助手"分解为可执行的开发任务。系统作为产品化封装层，复用现有的技术基础设施（评分引擎、策略扫描器、数据获取器），为普通股民提供极简的选股体验。

实现策略：
1. 先实现后端 API 层（封装现有能力）
2. 再实现前端 UI 组件（极简交互）
3. 最后集成测试和优化

## Tasks

- [x] 1. 后端 API 基础架构
  - [x] 1.1 创建 picker 路由模块
    - 创建 `src/web/routes/picker.py` 文件
    - 注册 Blueprint 到主应用
    - 配置 CORS 和错误处理
    - _Requirements: 所有后端需求的基础_

  - [x] 1.2 实现统一的错误消息转换
    - 创建 `make_error_friendly()` 函数
    - 定义技术术语到友好消息的映射表
    - 实现错误响应包装器
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5_

  - [ ]* 1.3 编写错误消息友好性的属性测试
    - **Property 27: Error messages are user-friendly**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5**

- [x] 2. 金牌策略配置和封装
  - [x] 2.1 定义金牌策略配置
    - 在 `picker.py` 中定义 `GOLDEN_STRATEGIES` 字典
    - 配置"低位放量突破"策略（基于 VolumeShrinkStrategy）
    - 配置"多头排列启动"策略（基于 MACrossoverStrategy）
    - 添加策略元数据（名称、描述、适合人群）
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [x] 2.2 实现策略列表 API
    - 创建 `GET /api/picker/strategies` 端点
    - 返回金牌策略列表（隐藏技术参数）
    - 包含历史表现数据（胜率、收益率、回撤）
    - _Requirements: 2.5, 2.6, 2.7_

  - [ ]* 2.3 编写策略列表的单元测试
    - 测试策略数量（应该是 3 个）
    - 测试策略名称（低位放量突破、多头排列启动、回踩支撑买入）
    - 测试返回字段完整性
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [x] 3. 今日精选功能实现
  - [x] 3.1 实现每日扫描逻辑
    - 创建 `scan_daily_picks()` 函数
    - 调用策略扫描器扫描全市场
    - 计算信号强度分数（0-100）
    - 生成大白话选股理由
    - _Requirements: 3.1, 3.2_

  - [x] 3.2 实现选股理由生成器
    - 创建 `generate_plain_reason()` 函数
    - 将技术指标转换为大白话（如"成交量放大 2.3 倍"）
    - 避免使用技术术语（MA5、MA20 等）
    - _Requirements: 3.7_

  - [x] 3.3 实现今日精选 API
    - 创建 `GET /api/picker/daily-picks` 端点
    - 从缓存表读取扫描结果
    - 按信号强度降序排列
    - 过滤低于 30 分的信号
    - 返回前 10 只股票
    - _Requirements: 3.3, 3.4, 3.8, 3.9_

  - [ ]* 3.4 编写今日精选的单元测试
    - 测试返回数量（最多 10 只）
    - 测试字段完整性（code, name, price, confidence_score, reason）
    - 测试排序逻辑
    - _Requirements: 3.3, 3.4_

  - [ ]* 3.5 编写今日精选的属性测试
    - **Property 8: Daily picks sorted by confidence score**
    - **Property 9: Low score signals filtered**
    - **Property 12: Reason uses plain language**
    - **Validates: Requirements 3.7, 3.8, 3.9**

- [ ] 4. 自选股监控功能实现
  - [x] 4.1 实现自选股数据 API
    - 创建 `POST /api/picker/watchlist` 端点
    - 接收股票代码列表（从前端 localStorage 传来）
    - 查询当前价格和涨跌幅
    - 计算信号状态（买入/卖出/观望）
    - **修复了股票代码格式问题：确保传递完整代码（如 sz.301042）给 get_daily_data()**
    - _Requirements: 4.3, 4.4_

  - [x] 4.2 实现信号灯逻辑
    - 创建 `calculate_signal()` 函数
    - 基于技术指标判断买入/卖出/观望
    - 返回信号类型和标签文本
    - 创建 `calculate_alerts()` 函数用于止损止盈预警
    - **修复了代码格式处理：不再错误地移除市场前缀**
    - _Requirements: 4.5, 4.6, 4.7_

  - [ ]* 4.3 编写自选股的单元测试
    - 测试字段完整性
    - 测试信号计算逻辑
    - _Requirements: 4.4, 4.5_

  - [ ]* 4.4 编写信号灯的属性测试
    - **Property 11: Signal strength color mapping**
    - **Property 15: Signal label display**
    - **Validates: Requirements 4.5, 4.6, 4.7**

- [x] 5. 止损止盈预警功能实现
  - [x] 5.1 实现止损止盈计算逻辑
    - 创建 `calculate_alerts()` 函数
    - 比较当前价格与止损/止盈线
    - 生成预警消息（建议操作、当前价格、目标价格）
    - _Requirements: 5.4, 5.5, 5.7, 5.8_

  - [x] 5.2 在自选股 API 中集成预警
    - 在 `GET /api/picker/watchlist` 响应中包含 alert 字段
    - 为触发预警的股票添加预警信息
    - _Requirements: 5.4, 5.5_

  - [ ]* 5.3 编写止损止盈的属性测试
    - **Property 18: Stop loss alert display**
    - **Property 19: Take profit alert display**
    - **Property 20: Alert contains price information**
    - **Validates: Requirements 5.4, 5.5, 5.7, 5.8**

- [x] 6. 策略历史表现功能实现
  - [x] 6.1 实现策略表现计算逻辑
    - 创建 `calculate_strategy_performance()` 函数
    - 从历史信号表计算胜率
    - 计算平均收益率和最大回撤
    - 生成资金曲线数据
    - _Requirements: 6.3, 6.4, 6.5, 6.6_

  - [x] 6.2 实现策略表现 API
    - 创建 `GET /api/picker/strategies/{id}/performance` 端点
    - 返回策略详细表现数据
    - 包含历史选股记录（成功/失败标注）
    - _Requirements: 6.2, 6.7, 6.8_

  - [ ]* 6.3 编写策略表现的单元测试
    - 测试胜率计算
    - 测试收益率计算
    - 测试回撤计算
    - _Requirements: 6.3, 6.4, 6.5_

  - [ ]* 6.4 编写策略表现的属性测试
    - **Property 21: Strategy performance contains required fields**
    - **Property 22: Historical picks labeled success/failure**
    - **Validates: Requirements 6.3, 6.4, 6.5, 6.8**

- [ ] 7. 一键数据同步功能实现
  - [x] 7.1 实现同步触发 API
    - 创建 `POST /api/picker/sync` 端点
    - 触发异步数据同步任务
    - 返回任务 ID
    - _Requirements: 1.2_

  - [x] 7.2 实现同步进度查询 API
    - 创建 `GET /api/picker/sync/{task_id}` 端点
    - 返回同步进度（百分比、当前股票）
    - 返回错误信息（如果有）
    - _Requirements: 1.3, 1.4, 1.5_

  - [x] 7.3 实现同步状态查询 API
    - 创建 `GET /api/picker/sync/status` 端点
    - 返回最后更新时间
    - 计算警告级别（none/yellow/red）
    - _Requirements: 1.6, 1.7, 1.8_

  - [ ]* 7.4 编写同步功能的单元测试
    - 测试任务创建
    - 测试进度查询
    - 测试状态查询
    - _Requirements: 1.2, 1.3, 1.6_

  - [ ]* 7.5 编写同步状态的属性测试
    - **Property 5: Data update time warning**
    - **Validates: Requirements 1.7, 1.8**

- [ ] 8. Checkpoint - 后端 API 完成
  - 确保所有 API 端点正常工作
  - 运行所有后端测试
  - 测试 API 文档和示例
  - 询问用户是否有问题


- [x] 9. 前端项目结构调整
  - [x] 9.1 创建极简选股助手页面组件
    - 创建 `frontend/src/pages/SimplePicker.tsx` 主页面
    - 创建 `frontend/src/components/picker/` 目录
    - 配置路由（将 `/` 指向 SimplePicker）
    - _Requirements: 7.1_

  - [x] 9.2 创建通用工具函数
    - 创建 `frontend/src/utils/picker.ts`
    - 实现信号强度到颜色的映射函数
    - 实现技术术语过滤函数
    - 实现价格格式化函数
    - _Requirements: 3.5, 2.8_

  - [ ]* 9.3 编写工具函数的属性测试
    - **Property 11: Signal strength color mapping**
    - **Property 7: Technical parameters hidden**
    - **Validates: Requirements 3.5, 2.8**

- [x] 10. 一键同步按钮组件
  - [x] 10.1 实现 OneSyncButton 组件
    - 创建 `frontend/src/components/picker/OneSyncButton.tsx`
    - 实现点击触发同步逻辑
    - 显示同步进度条
    - 显示当前状态文本
    - 根据最后更新时间显示警告
    - _Requirements: 1.1, 1.2, 1.3, 1.6, 1.7, 1.8_

  - [ ]* 10.2 编写 OneSyncButton 的单元测试
    - 测试按钮渲染
    - 测试点击事件
    - 测试进度显示
    - 测试警告显示
    - _Requirements: 1.1, 1.2, 1.3_

  - [ ]* 10.3 编写同步功能的属性测试
    - **Property 1: One-click sync triggers data update**
    - **Property 2: Sync progress display**
    - **Property 3: Sync completion display**
    - **Property 4: Sync failure friendly error**
    - **Property 5: Data update time warning**
    - **Validates: Requirements 1.2, 1.3, 1.4, 1.5, 1.7, 1.8**

- [x] 11. 今日精选卡片组件
  - [x] 11.1 实现 DailyPicksCard 组件
    - 创建 `frontend/src/components/picker/DailyPicksCard.tsx`
    - 显示前 10 只股票
    - 用颜色标识信号强度
    - 显示股票代码、名称、价格、信号强度
    - 点击股票跳转到详情页
    - _Requirements: 3.3, 3.4, 3.5, 3.6_

  - [x] 11.2 实现选股理由显示
    - 在卡片中显示大白话选股理由
    - 确保不包含技术术语
    - _Requirements: 3.7_

  - [ ]* 11.3 编写 DailyPicksCard 的单元测试
    - 测试卡片渲染
    - 测试股票数量限制（最多 10 只）
    - 测试字段显示
    - 测试点击事件
    - _Requirements: 3.3, 3.4, 3.6_

  - [ ]* 11.4 编写今日精选的属性测试
    - **Property 10: Daily picks display required fields**
    - **Property 11: Signal strength color mapping**
    - **Property 12: Reason uses plain language**
    - **Validates: Requirements 3.4, 3.5, 3.7**

- [x] 12. 自选股监控卡片组件
  - [x] 12.1 实现 WatchlistCard 组件
    - 创建 `frontend/src/components/picker/WatchlistCard.tsx`
    - 显示自选股列表
    - 显示当前价格、涨跌幅、信号灯
    - 显示添加时间和添加时价格
    - 显示止损止盈进度条
    - 支持移除股票
    - _Requirements: 4.3, 4.4, 4.8, 4.9_

  - [x] 12.2 实现 SignalLight 组件
    - 创建 `frontend/src/components/picker/SignalLight.tsx`
    - 用红绿灯表示买卖建议
    - 显示"买入"/"卖出"/"观望"标签
    - _Requirements: 4.5, 4.6, 4.7_

  - [x] 12.3 实现止损止盈预警显示
    - 在 WatchlistCard 中显示预警
    - 红色警告（止损）和绿色提示（止盈）
    - 显示建议操作、当前价格、目标价格
    - _Requirements: 5.4, 5.5, 5.6, 5.7, 5.8_

  - [ ]* 12.4 编写 WatchlistCard 的单元测试
    - 测试卡片渲染
    - 测试字段显示
    - 测试移除功能
    - 测试预警显示
    - _Requirements: 4.3, 4.4, 4.8, 5.4, 5.5_

  - [ ]* 12.5 编写自选股的属性测试
    - **Property 13: Add to watchlist updates list**
    - **Property 14: Watchlist displays required fields**
    - **Property 15: Signal label display**
    - **Property 16: Remove from watchlist updates list**
    - **Property 17: Default stop loss/take profit settings**
    - **Property 18: Stop loss alert display**
    - **Property 19: Take profit alert display**
    - **Property 20: Alert contains price information**
    - **Validates: Requirements 4.2, 4.4, 4.6, 4.7, 4.8, 4.9, 5.2, 5.4, 5.5, 5.7, 5.8**

- [x] 13. 策略表现卡片组件
  - [x] 13.1 实现 StrategyPerformanceCard 组件
    - 创建 `frontend/src/components/picker/StrategyPerformanceCard.tsx`
    - 显示金牌策略列表
    - 显示胜率、平均收益率、最大回撤
    - 用图表展示资金曲线
    - 点击策略显示历史选股记录
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7_

  - [x] 13.2 实现历史选股记录显示
    - 显示历史选股列表
    - 标注"成功"和"失败"
    - 显示数据来源说明
    - _Requirements: 6.7, 6.8, 6.9_

  - [ ]* 13.3 编写 StrategyPerformanceCard 的单元测试
    - 测试卡片渲染
    - 测试字段显示
    - 测试图表渲染
    - 测试历史记录显示
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [ ]* 13.4 编写策略表现的属性测试
    - **Property 21: Strategy performance contains required fields**
    - **Property 22: Historical picks labeled success/failure**
    - **Validates: Requirements 6.3, 6.4, 6.5, 6.8**

- [ ] 14. 极简仪表板页面集成
  - [x] 14.1 实现 SimplePicker 主页面
    - 创建 `frontend/src/pages/SimplePicker.tsx`
    - 集成 OneSyncButton
    - 集成 DailyPicksCard
    - 集成 WatchlistCard
    - 集成 StrategyPerformanceCard
    - 只显示 3 个核心模块
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

  - [x] 14.2 实现数据加载逻辑
    - 从 API 加载今日精选
    - 从 localStorage 读取自选股代码
    - 从 API 加载自选股数据
    - 从 API 加载策略表现
    - _Requirements: 3.2, 4.3, 6.2_

  - [x] 14.3 隐藏技术细节
    - 不显示数据库状态
    - 不显示 API 调用信息
    - 使用大字体和清晰图标
    - 使用红绿配色（涨红跌绿）
    - _Requirements: 7.5, 7.6, 7.7_

  - [ ]* 14.4 编写仪表板的单元测试
    - 测试页面渲染
    - 测试模块数量（应该是 3 个）
    - 测试数据加载
    - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 15. 股票详情页增强
  - [x] 15.1 实现 SimpleStockDetail 页面
    - 创建 `frontend/src/pages/SimpleStockDetail.tsx`
    - 显示股票名称、代码、当前价格、涨跌幅
    - 显示 K 线图（最近 3 个月）
    - 在 K 线图上标注买入/卖出信号点
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [x] 15.2 实现选股理由和关键指标卡片
    - 创建 ReasonCard 组件（显示大白话选股理由）
    - 创建 KeyMetricsCard 组件（显示关键指标）
    - 提供"加入自选"按钮
    - 提供"查看更多历史"按钮
    - _Requirements: 8.5, 8.6, 8.7, 8.8_

  - [ ]* 15.3 编写股票详情页的单元测试
    - 测试页面渲染
    - 测试字段显示
    - 测试 K 线图渲染
    - 测试信号点标注
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ]* 15.4 编写股票详情页的属性测试
    - **Property 8.1: Stock detail page navigation**
    - **Property 8.2: Stock detail displays required fields**
    - **Property 8.4: K-line chart signal annotations**
    - **Validates: Requirements 8.1, 8.2, 8.4**

- [ ] 16. 响应式设计和移动端适配
  - [ ] 16.1 实现响应式布局
    - 添加媒体查询（断点 768px）
    - 移动端使用单列布局
    - 移动端放大按钮尺寸（至少 44px）
    - 移动端隐藏次要信息
    - _Requirements: 9.1, 9.2, 9.3, 9.4, 9.5_

  - [ ] 16.2 实现移动端交互
    - 支持下拉刷新
    - 支持左右滑动切换股票
    - _Requirements: 9.6, 9.7_

  - [ ]* 16.3 编写响应式设计的属性测试
    - **Property 23: Responsive layout switches**
    - **Property 24: Mobile button sizes**
    - **Validates: Requirements 9.2, 9.4**

- [ ] 17. 新手引导功能
  - [ ] 17.1 实现 OnboardingGuide 组件
    - 创建 `frontend/src/components/picker/OnboardingGuide.tsx`
    - 检查 localStorage 中的 `onboarding_completed` 标记
    - 显示 4 个引导步骤
    - 解释金牌策略、今日精选、止损止盈
    - 提供"跳过引导"和"下一步"按钮
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

  - [ ] 17.2 实现引导完成逻辑
    - 完成引导后设置 localStorage 标记
    - 提供"重新查看引导"入口（在设置页面）
    - _Requirements: 10.6, 10.7_

  - [ ]* 17.3 编写新手引导的单元测试
    - 测试引导显示逻辑
    - 测试步骤切换
    - 测试跳过功能
    - 测试完成标记
    - _Requirements: 10.1, 10.5, 10.7_

  - [ ]* 17.4 编写新手引导的属性测试
    - **Property 25: First visit shows onboarding**
    - **Property 26: Onboarding completion sets flag**
    - **Validates: Requirements 10.1, 10.7**

- [ ] 18. 错误处理和用户反馈
  - [ ] 18.1 实现全局错误处理
    - 配置 Axios 拦截器
    - 将所有错误转换为友好消息
    - 显示"联系客服"按钮
    - 实现离线检测和提示
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6_

  - [ ] 18.2 实现维护公告显示
    - 检测维护状态
    - 显示维护公告和预计恢复时间
    - _Requirements: 11.7_

  - [ ] 18.3 实现加载状态优化
    - 使用骨架屏代替空白页面
    - 超过 3 秒显示加载提示
    - _Requirements: 12.6, 12.7_

  - [ ]* 18.4 编写错误处理的属性测试
    - **Property 27: Error messages are user-friendly**
    - **Property 28: Error messages include support button**
    - **Property 29: Long loading shows indicator**
    - **Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 12.6**

- [ ] 19. 性能优化
  - [ ] 19.1 实现数据缓存机制
    - 使用 React Context 缓存今日精选
    - 使用 localStorage 缓存自选股
    - 避免重复 API 请求
    - _Requirements: 12.4_

  - [ ] 19.2 实现后台预加载
    - 预加载今日精选数据
    - 预加载策略表现数据
    - _Requirements: 12.5_

  - [ ]* 19.3 性能测试（可选）
    - 测试首页加载时间（目标 < 2 秒）
    - 测试详情页加载时间（目标 < 1 秒）
    - 测试策略切换时间（目标 < 1 秒）
    - _Requirements: 12.1, 12.2, 12.3_

- [ ] 20. Checkpoint - 前端功能完成
  - 确保所有前端组件正常工作
  - 运行所有前端测试
  - 测试响应式布局
  - 测试移动端交互
  - 询问用户是否有问题

- [ ] 21. 集成测试和端到端测试
  - [ ] 21.1 实现关键用户流程测试
    - 测试一键同步流程
    - 测试查看今日精选流程
    - 测试加入自选流程
    - 测试止损止盈预警流程
    - 测试查看策略表现流程
    - _Requirements: 所有需求_

  - [ ]* 21.2 编写集成测试
    - 测试前后端 API 集成
    - 测试数据流完整性
    - 测试错误处理链路
    - _Requirements: 所有需求_

- [ ] 22. 文档和部署准备
  - [ ] 22.1 编写用户文档
    - 编写"快速开始"指南
    - 编写"金牌策略"说明
    - 编写"常见问题"FAQ
    - _Requirements: 所有需求_

  - [ ] 22.2 编写开发文档
    - 更新 API 文档
    - 更新组件文档
    - 更新部署文档
    - _Requirements: 所有需求_

  - [ ] 22.3 准备生产环境配置
    - 配置生产环境变量
    - 配置 CORS 策略
    - 配置错误日志
    - _Requirements: 所有需求_

- [ ] 23. Final Checkpoint - 系统完整性验证
  - 运行所有测试（单元测试 + 属性测试 + 集成测试）
  - 验证所有功能正常工作
  - 验证移动端体验
  - 验证错误处理
  - 验证性能指标
  - 询问用户是否有问题

## Notes

- 任务标记 `*` 的为可选任务，可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求条款，确保实现的可追溯性
- Checkpoint 任务用于阶段性验证，确保增量开发的质量
- 属性测试使用 fast-check（前端）和 Hypothesis（后端），每个测试至少运行 100 次
- 单元测试和属性测试是互补的，共同保证代码质量
- 优先实现核心功能（今日精选、自选监控、策略表现），再实现辅助功能（新手引导、移动端优化）


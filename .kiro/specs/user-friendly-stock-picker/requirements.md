# Requirements Document - 极简选股助手

## Introduction

TradingBuddy 极简选股助手是一个面向 99% 不懂技术的中国股民的傻瓜式选股工具。系统将复杂的量化逻辑、数据同步和技术分析全部"折叠"在后台，只给用户呈现最直观、最有价值的选股信号。

产品定位："懂你的选股直觉" - 让普通股民也能享受专业量化选股的能力。

核心理念：
- **极简交互**：一键操作，零配置
- **直觉化呈现**：用颜色和信号灯代替复杂参数
- **决策辅助**：提供建议而非指令，用户保持主动权
- **持续学习**：展示历史表现，建立信任

## Glossary

- **Stock_Picker**: 选股助手，系统的核心引擎
- **Golden_Strategy**: 金牌策略，预设的高质量选股模板
- **Daily_Radar**: 每日选股雷达，自动扫描并推荐股票
- **Signal_Light**: 信号灯，用红绿灯表示买卖建议
- **Watchlist**: 自选监控，用户关注的股票列表
- **Strategy_Performance**: 策略表现，历史选股的回测结果
- **One_Click_Sync**: 一键同步，自动更新所有数据
- **Stop_Loss_Alert**: 止损预警，触发止损条件时的提醒
- **Take_Profit_Alert**: 止盈预警，触发止盈条件时的提醒
- **Confidence_Score**: 信号强度，0-100 的评分，表示选股质量

## Requirements

### Requirement 1: 一键数据同步

**User Story:** 作为普通股民，我不想关心什么是数据库或 API，我只想点一个按钮就能确保数据是最新的。

#### Acceptance Criteria

1. THE Stock_Picker SHALL 在首页提供"一键同步"按钮
2. WHEN 用户点击"一键同步"按钮 THEN THE Stock_Picker SHALL 自动执行增量数据更新
3. WHEN 数据同步进行中 THEN THE Stock_Picker SHALL 显示进度条和当前状态（如"正在更新 600000.SH"）
4. WHEN 数据同步完成 THEN THE Stock_Picker SHALL 显示成功提示和更新统计（如"已更新 5000 只股票"）
5. IF 数据同步失败 THEN THE Stock_Picker SHALL 显示友好的错误提示（如"网络不稳定，请稍后重试"）
6. THE Stock_Picker SHALL 在首页显示"最后更新时间"
7. WHEN 数据超过 1 天未更新 THEN THE Stock_Picker SHALL 在首页显示黄色提醒
8. WHEN 数据超过 3 天未更新 THEN THE Stock_Picker SHALL 在首页显示红色警告

### Requirement 2: 金牌策略模板

**User Story:** 作为普通股民，我不懂什么是 MA5 或 MA20，我只想选择一个听起来靠谱的策略，比如"低位放量突破"。

#### Acceptance Criteria

1. THE Stock_Picker SHALL 提供 3 个预设的金牌策略模板
2. THE Golden_Strategy SHALL 包含"低位放量突破"策略
3. THE Golden_Strategy SHALL 包含"多头排列启动"策略
4. THE Golden_Strategy SHALL 包含"回踩支撑买入"策略
5. WHEN 用户查看策略列表 THEN THE Stock_Picker SHALL 显示策略名称、一句话描述、历史胜率
6. WHEN 用户选择一个策略 THEN THE Stock_Picker SHALL 显示该策略的详细说明（用大白话）
7. THE Stock_Picker SHALL 为每个策略显示"适合人群"标签（如"稳健型"、"激进型"）
8. THE Stock_Picker SHALL 隐藏所有技术参数（MA5、MA20 等），用户无需配置

### Requirement 3: 每日选股雷达

**User Story:** 作为普通股民，我希望每天打开系统就能看到今天有哪些股票符合我选择的策略，而不需要手动扫描。

#### Acceptance Criteria

1. THE Daily_Radar SHALL 每日收盘后自动扫描全市场股票
2. WHEN 扫描完成 THEN THE Daily_Radar SHALL 生成"今日精选"列表
3. THE Daily_Radar SHALL 在首页显示"今日精选"卡片，展示前 10 只股票
4. WHEN 用户查看今日精选 THEN THE Stock_Picker SHALL 显示股票代码、名称、当前价格、信号强度
5. THE Stock_Picker SHALL 用颜色标识信号强度（绿色=强，黄色=中，灰色=弱）
6. WHEN 用户点击某只股票 THEN THE Stock_Picker SHALL 显示详情页，包含 K 线图和选股理由
7. THE Stock_Picker SHALL 在选股理由中用大白话解释（如"成交量突然放大 2.3 倍，可能有资金进场"）
8. THE Daily_Radar SHALL 按信号强度降序排列股票
9. WHEN 信号强度低于 30 分 THEN THE Daily_Radar SHALL 不展示该股票

### Requirement 4: 自选股监控

**User Story:** 作为普通股民，我想把感兴趣的股票加入自选，并实时看到它们的买卖信号。

#### Acceptance Criteria

1. THE Stock_Picker SHALL 提供"加入自选"按钮
2. WHEN 用户点击"加入自选" THEN THE Stock_Picker SHALL 将股票添加到 Watchlist
3. THE Stock_Picker SHALL 在首页显示"我的自选"卡片
4. WHEN 用户查看自选列表 THEN THE Stock_Picker SHALL 显示每只股票的当前价格、涨跌幅、信号灯
5. THE Signal_Light SHALL 用红绿灯表示建议（绿灯=可以买入，黄灯=观望，红灯=建议卖出）
6. WHEN 自选股触发买入信号 THEN THE Stock_Picker SHALL 在信号灯旁显示"买入"标签
7. WHEN 自选股触发卖出信号 THEN THE Stock_Picker SHALL 在信号灯旁显示"卖出"标签
8. THE Stock_Picker SHALL 支持从自选列表中移除股票
9. THE Stock_Picker SHALL 在自选列表中显示"添加时间"和"添加时价格"

### Requirement 5: 止损止盈预警

**User Story:** 作为普通股民，我经常"拿不住"或"舍不得卖"，我希望系统能提醒我什么时候该止损或止盈。

#### Acceptance Criteria

1. THE Stock_Picker SHALL 为自选股提供止损止盈设置
2. WHEN 用户添加自选股 THEN THE Stock_Picker SHALL 自动设置默认止损（-10%）和止盈（+20%）
3. THE Stock_Picker SHALL 允许用户自定义止损止盈百分比
4. WHEN 自选股价格触及止损线 THEN THE Stop_Loss_Alert SHALL 在首页显示红色警告
5. WHEN 自选股价格触及止盈线 THEN THE Take_Profit_Alert SHALL 在首页显示绿色提示
6. THE Stock_Picker SHALL 在自选列表中用进度条显示当前盈亏（距离止损/止盈的位置）
7. WHEN 触发预警 THEN THE Stock_Picker SHALL 在预警中显示"建议操作"（如"建议止损卖出"）
8. THE Stock_Picker SHALL 在预警中显示"当前价格"和"目标价格"

### Requirement 6: 策略历史表现

**User Story:** 作为普通股民，我想知道这些策略过去表现如何，这样我才能相信它们。

#### Acceptance Criteria

1. THE Stock_Picker SHALL 在首页显示"策略表现"卡片
2. WHEN 用户查看策略表现 THEN THE Stock_Picker SHALL 显示每个金牌策略的历史数据
3. THE Strategy_Performance SHALL 显示"近 30 天胜率"（选中的股票有多少上涨）
4. THE Strategy_Performance SHALL 显示"平均收益率"（选中的股票平均涨了多少）
5. THE Strategy_Performance SHALL 显示"最大回撤"（最差的情况亏了多少）
6. THE Stock_Picker SHALL 用图表展示策略的资金曲线（如果按这个策略操作，账户价值如何变化）
7. WHEN 用户点击某个策略 THEN THE Stock_Picker SHALL 显示该策略的历史选股记录
8. THE Stock_Picker SHALL 在历史记录中标注"成功"（上涨）和"失败"（下跌）的股票
9. THE Stock_Picker SHALL 显示"数据来源"说明（如"基于 2024 年 1 月至今的回测数据"）

### Requirement 7: 极简仪表板

**User Story:** 作为普通股民，我希望首页只显示最重要的信息，不要有太多干扰。

#### Acceptance Criteria

1. THE Stock_Picker SHALL 在首页只显示 3 个核心模块
2. THE Stock_Picker SHALL 在首页顶部显示"今日精选股票"模块
3. THE Stock_Picker SHALL 在首页中部显示"我的自选监控"模块
4. THE Stock_Picker SHALL 在首页底部显示"策略历史表现"模块
5. THE Stock_Picker SHALL 隐藏所有技术细节（数据库状态、API 调用等）
6. THE Stock_Picker SHALL 使用大字体和清晰的图标
7. THE Stock_Picker SHALL 使用红绿配色（涨红跌绿，符合中国股民习惯）
8. WHEN 首页加载时 THEN THE Stock_Picker SHALL 在 2 秒内显示所有核心内容

### Requirement 8: 股票详情页

**User Story:** 作为普通股民，当我点击某只股票时，我想看到它的 K 线图、选股理由和关键指标。

#### Acceptance Criteria

1. WHEN 用户点击股票 THEN THE Stock_Picker SHALL 显示股票详情页
2. THE Stock_Picker SHALL 在详情页顶部显示股票名称、代码、当前价格、涨跌幅
3. THE Stock_Picker SHALL 在详情页显示 K 线图（最近 3 个月）
4. THE Stock_Picker SHALL 在 K 线图上标注买入/卖出信号点
5. THE Stock_Picker SHALL 在详情页显示"选股理由"卡片（用大白话）
6. THE Stock_Picker SHALL 在详情页显示"关键指标"卡片（成交量、均线、市值等）
7. THE Stock_Picker SHALL 在详情页提供"加入自选"按钮
8. THE Stock_Picker SHALL 在详情页提供"查看更多历史"按钮（跳转到完整 K 线图）

### Requirement 9: 移动端适配

**User Story:** 作为普通股民，我经常在手机上看股票，我希望系统在手机上也能流畅使用。

#### Acceptance Criteria

1. THE Stock_Picker SHALL 在移动端自动调整布局
2. WHEN 屏幕宽度小于 768px THEN THE Stock_Picker SHALL 切换到移动布局
3. THE Stock_Picker SHALL 在移动端使用单列布局
4. THE Stock_Picker SHALL 在移动端放大按钮尺寸（至少 44px）
5. THE Stock_Picker SHALL 在移动端隐藏次要信息（如详细的回测数据）
6. THE Stock_Picker SHALL 在移动端支持下拉刷新
7. THE Stock_Picker SHALL 在移动端支持左右滑动切换股票

### Requirement 10: 新手引导

**User Story:** 作为第一次使用的股民，我希望系统能告诉我如何开始使用。

#### Acceptance Criteria

1. WHEN 用户首次访问 THEN THE Stock_Picker SHALL 显示欢迎引导页
2. THE Stock_Picker SHALL 在引导页解释"什么是金牌策略"
3. THE Stock_Picker SHALL 在引导页解释"如何使用每日精选"
4. THE Stock_Picker SHALL 在引导页解释"如何设置止损止盈"
5. THE Stock_Picker SHALL 提供"跳过引导"按钮
6. THE Stock_Picker SHALL 提供"重新查看引导"入口（在设置页面）
7. WHEN 用户完成引导 THEN THE Stock_Picker SHALL 记住用户状态，不再显示引导

### Requirement 11: 错误处理和友好提示

**User Story:** 作为普通股民，当系统出错时，我希望看到我能理解的提示，而不是技术错误信息。

#### Acceptance Criteria

1. WHEN 网络请求失败 THEN THE Stock_Picker SHALL 显示"网络不稳定，请稍后重试"
2. WHEN 数据加载失败 THEN THE Stock_Picker SHALL 显示"数据加载失败，点击重试"
3. WHEN 股票代码不存在 THEN THE Stock_Picker SHALL 显示"未找到该股票"
4. WHEN 数据正在同步 THEN THE Stock_Picker SHALL 显示"数据更新中，请稍候"
5. THE Stock_Picker SHALL 避免显示技术术语（如"API 错误"、"数据库连接失败"）
6. THE Stock_Picker SHALL 在错误提示中提供"联系客服"按钮
7. WHEN 系统维护时 THEN THE Stock_Picker SHALL 显示维护公告和预计恢复时间

### Requirement 12: 性能和响应速度

**User Story:** 作为普通股民，我希望系统反应迅速，不要让我等太久。

#### Acceptance Criteria

1. WHEN 用户访问首页 THEN THE Stock_Picker SHALL 在 2 秒内显示核心内容
2. WHEN 用户点击股票 THEN THE Stock_Picker SHALL 在 1 秒内显示详情页
3. WHEN 用户切换策略 THEN THE Stock_Picker SHALL 在 1 秒内更新选股列表
4. THE Stock_Picker SHALL 使用缓存机制，避免重复加载相同数据
5. THE Stock_Picker SHALL 在后台预加载常用数据（如今日精选）
6. WHEN 数据加载超过 3 秒 THEN THE Stock_Picker SHALL 显示加载提示
7. THE Stock_Picker SHALL 使用骨架屏而非空白页面


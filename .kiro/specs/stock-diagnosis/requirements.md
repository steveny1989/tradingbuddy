# Requirements Document - 个股诊断系统

## Introduction

个股诊断系统（Stock Diagnosis System）是 TradingBuddy 的"决策验证器"模块。当用户从朋友、社交媒体或其他渠道获得股票推荐时，系统提供客观、快速的多维度分析，帮助用户做出理性判断。

产品定位："你的交易医生" - 不是告诉你买什么，而是帮你验证别人推荐的是否靠谱。

核心场景：
- 朋友推荐了一只股票，我该不该买？
- 看到一个"小道消息"，这只股票真的有机会吗？
- 持有的股票，现在该继续拿着还是卖出？
- 多只股票在纠结，哪只更值得优先关注？

设计原则：
- **客观中立**：只看数据，不带情绪
- **快速响应**：3 秒内给出诊断结果
- **大白话**：用普通人能理解的语言解释
- **风险优先**：先告诉用户风险，再说机会

## Glossary

- **Stock_Diagnosis_Engine**: 个股诊断引擎，系统核心组件
- **Multi_Dimension_Scorer**: 多维度评分器，从技术、资金、市场环境等维度打分
- **Signal_Light_Evaluator**: 信号灯评估器，给出红绿灯建议
- **Plain_Language_Generator**: 大白话生成器，将技术指标转换为自然语言
- **Risk_Calculator**: 风险计算器，计算止损止盈价位
- **Comparison_Engine**: 对比引擎，支持多只股票横向对比
- **Diagnosis_Report**: 诊断报告，包含评分、信号灯、理由、风险指南的完整输出
- **Technical_Score**: 技术面评分（0-100），基于均线、成交量、形态等
- **Liquidity_Score**: 流动性评分（0-100），基于成交额、换手率等
- **Market_Environment_Score**: 市场环境评分（0-100），基于大盘状态、板块表现等
- **Overall_Score**: 综合评分（0-100），技术面 60% + 流动性 20% + 市场环境 20%
- **Risk_Level**: 风险等级，分为低风险、中风险、高风险、极高风险

## Requirements

### Requirement 1: 快速诊断入口

**User Story:** 作为投资者，我希望能够快速输入股票代码或名称，立即获得诊断结果。

#### Acceptance Criteria

1. THE Stock_Diagnosis_Engine SHALL 提供搜索框接受股票代码或名称输入
2. WHEN 用户输入股票代码（如 600000 或 sh.600000）THEN THE System SHALL 自动识别并标准化
3. WHEN 用户输入股票名称（如"浦发银行"）THEN THE System SHALL 自动匹配到正确代码
4. WHEN 用户输入模糊关键词 THEN THE System SHALL 提供候选列表供选择
5. WHEN 用户提交诊断请求 THEN THE System SHALL 在 3 秒内返回诊断报告
6. THE System SHALL 支持通过 URL 参数直接访问诊断页面（如 /diagnosis?code=sh.600000）
7. THE System SHALL 在首页提供"个股诊断"入口按钮

### Requirement 2: 多维度评分系统

**User Story:** 作为投资者，我希望看到股票在不同维度的评分，以便全面了解其质量。

#### Acceptance Criteria

1. WHEN Multi_Dimension_Scorer 计算评分时 THEN THE System SHALL 生成技术面评分（0-100）
2. WHEN Multi_Dimension_Scorer 计算评分时 THEN THE System SHALL 生成流动性评分（0-100）
3. WHEN Multi_Dimension_Scorer 计算评分时 THEN THE System SHALL 生成市场环境评分（0-100）
4. WHEN Multi_Dimension_Scorer 计算评分时 THEN THE System SHALL 生成综合评分（加权平均）
5. THE System SHALL 使用 60% 技术面 + 20% 流动性 + 20% 市场环境的权重计算综合评分
6. WHEN 返回诊断报告时 THEN THE System SHALL 包含所有四个维度的评分
7. THE System SHALL 用雷达图或柱状图可视化展示多维度评分
8. WHEN 某个维度数据缺失时 THEN THE System SHALL 标注"数据不足"并降低该维度权重

### Requirement 3: 技术面评分逻辑

**User Story:** 作为投资者，我希望系统能够评估股票的技术形态是否健康。

#### Acceptance Criteria

1. WHEN 计算技术面评分时 THEN THE System SHALL 检查是否符合金牌策略（如均线多头排列）
2. WHEN 计算技术面评分时 THEN THE System SHALL 检查成交量变化（放量加分，缩量减分）
3. WHEN 计算技术面评分时 THEN THE System SHALL 检查价格位置（突破加分，破位减分）
4. WHEN 计算技术面评分时 THEN THE System SHALL 检查 MACD、RSI 等辅助指标
5. WHEN 股票符合"放量突破"形态 THEN THE System SHALL 给予 80 分以上技术评分
6. WHEN 股票出现"死叉"或"无量阴跌" THEN THE System SHALL 给予 30 分以下技术评分
7. WHEN 股票处于横盘整理 THEN THE System SHALL 给予 40-60 分中性评分
8. THE System SHALL 在评分中考虑最近 5 个交易日的趋势强度

### Requirement 4: 流动性评分逻辑

**User Story:** 作为投资者，我希望系统能够识别"死水股"，避免流动性陷阱。

#### Acceptance Criteria

1. WHEN 计算流动性评分时 THEN THE System SHALL 检查日均成交额
2. WHEN 日均成交额大于 5 亿 THEN THE System SHALL 给予 80 分以上流动性评分
3. WHEN 日均成交额在 1-5 亿之间 THEN THE System SHALL 给予 60-80 分流动性评分
4. WHEN 日均成交额小于 1 亿 THEN THE System SHALL 给予 40 分以下流动性评分并标注"流动性不足"
5. WHEN 日均成交额小于 5000 万 THEN THE System SHALL 给予 20 分以下流动性评分并标注"死水股"
6. THE System SHALL 检查换手率（过高或过低都减分）
7. THE System SHALL 检查最近 5 日成交额的稳定性（波动过大减分）
8. WHEN 流动性评分低于 40 THEN THE System SHALL 在诊断报告中显著标注流动性风险

### Requirement 5: 市场环境评分逻辑

**User Story:** 作为投资者，我希望系统能够告诉我当前市场环境是否适合操作这只股票。

#### Acceptance Criteria

1. WHEN 计算市场环境评分时 THEN THE System SHALL 检查大盘（上证指数）是否在 20 日均线以上
2. WHEN 大盘在 20 日均线以上 THEN THE System SHALL 给予 70 分以上市场环境评分
3. WHEN 大盘在 20 日均线以下 THEN THE System SHALL 给予 50 分以下市场环境评分
4. WHEN 计算市场环境评分时 THEN THE System SHALL 检查股票所属板块的表现
5. WHEN 板块整体上涨 THEN THE System SHALL 增加市场环境评分
6. WHEN 板块整体下跌 THEN THE System SHALL 降低市场环境评分
7. THE System SHALL 检查市场成交量（市场活跃度）
8. WHEN 市场环境评分低于 40 THEN THE System SHALL 建议"等待更好的市场时机"

### Requirement 6: 信号灯评价系统

**User Story:** 作为投资者，我希望看到一个直观的红绿灯，快速了解该买入、观望还是卖出。

#### Acceptance Criteria

1. WHEN Signal_Light_Evaluator 生成信号灯时 THEN THE System SHALL 基于综合评分判断
2. WHEN 综合评分 >= 70 THEN THE System SHALL 显示绿灯（建议关注或买入）
3. WHEN 综合评分在 40-70 之间 THEN THE System SHALL 显示黄灯（建议观望）
4. WHEN 综合评分 < 40 THEN THE System SHALL 显示红灯（建议回避或卖出）
5. THE System SHALL 在信号灯旁显示文字说明（如"绿灯：技术形态良好，可以关注"）
6. WHEN 存在重大风险因素时 THEN THE System SHALL 强制显示红灯（即使评分较高）
7. THE System SHALL 列出触发当前信号灯的关键因素（如"成交量放大 2.3 倍"）
8. THE System SHALL 在信号灯下方显示"信号强度"百分比

### Requirement 7: 大白话诊断意见

**User Story:** 作为投资者，我希望看到用普通话解释的诊断结果，而不是技术术语。

#### Acceptance Criteria

1. WHEN Plain_Language_Generator 生成诊断意见时 THEN THE System SHALL 使用自然语言描述
2. THE System SHALL 避免使用技术术语（如"MA5 上穿 MA20"），改用"短期均线突破长期均线"
3. THE System SHALL 在诊断意见中包含"当前状态"描述（如"股价正在突破前期高点"）
4. THE System SHALL 在诊断意见中包含"关键指标"描述（如"成交量比平时放大了 2 倍多"）
5. THE System SHALL 在诊断意见中包含"建议操作"（如"可以考虑小仓位试探"）
6. WHEN 评分较低时 THEN THE System SHALL 明确说明原因（如"成交量严重萎缩，资金流出明显"）
7. WHEN 评分较高时 THEN THE System SHALL 说明优势（如"符合放量突破形态，且处于优质市值区间"）
8. THE System SHALL 在诊断意见中包含"风险提示"（如"注意大盘环境较弱"）

### Requirement 8: 风险管理指南

**User Story:** 作为投资者，我希望系统能够告诉我如果买入，应该在什么价位止损和止盈。

#### Acceptance Criteria

1. WHEN Risk_Calculator 计算风险指南时 THEN THE System SHALL 基于当前价格计算止损价位
2. WHEN Risk_Calculator 计算风险指南时 THEN THE System SHALL 基于当前价格计算止盈价位
3. THE System SHALL 使用 -8% 作为默认止损比例
4. THE System SHALL 使用 +15% 作为默认止盈比例
5. THE System SHALL 在诊断报告中显示具体的止损价格（如"止损价：8.50 元"）
6. THE System SHALL 在诊断报告中显示具体的止盈价格（如"止盈价：10.50 元"）
7. THE System SHALL 计算并显示预期盈亏比（如"盈亏比 1.88:1"）
8. THE System SHALL 根据股票波动率调整止损止盈比例（高波动股票放宽止损）
9. WHEN 股票属于 ST 股或高风险股 THEN THE System SHALL 建议更严格的止损（如 -5%）

### Requirement 9: 反面证据和风险预警

**User Story:** 作为投资者，我希望系统能够主动告诉我这只股票的风险点，即使评分较高。

#### Acceptance Criteria

1. THE System SHALL 检查股票是否为 ST 股或 *ST 股
2. WHEN 股票为 ST 股 THEN THE System SHALL 显示"高风险预警：该股票存在退市风险"
3. THE System SHALL 检查股票是否连续两年亏损
4. WHEN 股票连续亏损 THEN THE System SHALL 显示"财务风险：公司连续亏损"
5. THE System SHALL 检查股票是否存在重大诉讼或监管处罚
6. THE System SHALL 检查股票是否处于停牌或即将停牌状态
7. THE System SHALL 检查股票是否在近期有大股东减持
8. WHEN 存在任何高风险因素 THEN THE System SHALL 在诊断报告顶部显著标注
9. THE System SHALL 在风险预警中使用红色背景和警告图标
10. WHEN 风险等级为"极高风险" THEN THE System SHALL 建议"不建议操作"

### Requirement 10: 历史表现参考

**User Story:** 作为投资者，我希望看到这只股票在过去的表现，以及系统历史上对它的诊断准确率。

#### Acceptance Criteria

1. THE System SHALL 显示股票最近 3 个月的涨跌幅
2. THE System SHALL 显示股票最近 1 年的涨跌幅
3. THE System SHALL 显示股票相对于大盘的超额收益
4. WHEN 系统曾经对该股票发出过信号 THEN THE System SHALL 显示历史信号的表现
5. THE System SHALL 显示"如果按上次信号买入，现在盈亏多少"
6. THE System SHALL 显示该股票历史上触发信号的次数和胜率
7. THE System SHALL 在 K 线图上标注历史信号点位
8. WHEN 历史信号表现不佳 THEN THE System SHALL 在诊断报告中提示"该股票历史信号准确率较低"

### Requirement 11: 多股票对比功能

**User Story:** 作为投资者，当我在多只股票之间纠结时，我希望系统能够帮我横向对比，告诉我哪只更值得优先关注。

#### Acceptance Criteria

1. THE Comparison_Engine SHALL 支持同时诊断最多 5 只股票
2. WHEN 用户提交多只股票 THEN THE System SHALL 生成对比表格
3. THE System SHALL 在对比表格中显示每只股票的综合评分
4. THE System SHALL 在对比表格中显示每只股票的信号灯
5. THE System SHALL 在对比表格中显示每只股票的关键指标（成交额、涨跌幅等）
6. THE System SHALL 自动按综合评分降序排列股票
7. THE System SHALL 高亮显示评分最高的股票
8. THE System SHALL 在对比结果中给出"优先级建议"（如"建议优先关注 600000.SH"）
9. THE System SHALL 支持导出对比结果为图片或 PDF

### Requirement 12: 诊断报告可分享

**User Story:** 作为投资者，我希望能够将诊断报告分享给推荐股票的朋友，用数据说话。

#### Acceptance Criteria

1. THE System SHALL 为每个诊断报告生成唯一的分享链接
2. THE System SHALL 支持生成诊断报告的图片卡片
3. THE System SHALL 在图片卡片中包含股票名称、综合评分、信号灯、核心理由
4. THE System SHALL 在图片卡片底部显示"由 TradingBuddy 生成"水印
5. THE System SHALL 支持一键复制分享链接
6. THE System SHALL 支持一键保存图片到本地
7. WHEN 用户访问分享链接 THEN THE System SHALL 显示完整的诊断报告
8. THE System SHALL 在分享页面显示"数据生成时间"和"有效期"（如 24 小时）
9. THE System SHALL 在分享页面底部显示免责声明

### Requirement 13: 实时数据更新

**User Story:** 作为投资者，我希望诊断结果基于最新的数据，而不是过时的信息。

#### Acceptance Criteria

1. WHEN 用户请求诊断 THEN THE System SHALL 检查数据是否为最新
2. WHEN 数据超过 1 天未更新 THEN THE System SHALL 在诊断报告中显示"数据可能不是最新"警告
3. THE System SHALL 在诊断报告中显示"数据更新时间"
4. THE System SHALL 支持"刷新数据"按钮，触发增量更新
5. WHEN 用户点击"刷新数据" THEN THE System SHALL 更新该股票的最新数据并重新诊断
6. THE System SHALL 在盘中时段每 5 分钟自动刷新数据（可选功能）
7. THE System SHALL 在收盘后自动触发全量数据更新

### Requirement 14: 诊断历史记录

**User Story:** 作为投资者，我希望能够查看我之前诊断过的股票，方便回顾和对比。

#### Acceptance Criteria

1. THE System SHALL 记录用户的诊断历史
2. THE System SHALL 在"诊断历史"页面显示最近 30 次诊断记录
3. THE System SHALL 在历史记录中显示股票名称、诊断时间、当时评分、当时价格
4. THE System SHALL 在历史记录中显示"当前价格"和"涨跌幅"（相对于诊断时）
5. THE System SHALL 支持点击历史记录重新查看当时的诊断报告
6. THE System SHALL 支持点击历史记录生成"最新诊断"
7. THE System SHALL 在历史记录中标注"诊断准确"或"诊断失误"（基于后续表现）
8. THE System SHALL 支持删除诊断历史记录

### Requirement 15: 移动端优化

**User Story:** 作为投资者，我经常在手机上查看股票，我希望诊断功能在手机上也能流畅使用。

#### Acceptance Criteria

1. THE System SHALL 在移动端自动调整诊断报告布局
2. THE System SHALL 在移动端使用单列布局展示评分和信号灯
3. THE System SHALL 在移动端放大关键信息（评分、信号灯）的显示尺寸
4. THE System SHALL 在移动端支持左右滑动查看多维度评分
5. THE System SHALL 在移动端支持下拉刷新数据
6. THE System SHALL 在移动端优化图片卡片生成（适配手机屏幕）
7. THE System SHALL 在移动端支持长按保存诊断报告图片

### Requirement 16: 性能和响应速度

**User Story:** 作为投资者，我希望诊断结果能够快速返回，不要让我等太久。

#### Acceptance Criteria

1. WHEN 用户提交诊断请求 THEN THE System SHALL 在 3 秒内返回诊断报告
2. THE System SHALL 使用缓存机制，避免重复计算相同股票的诊断
3. THE System SHALL 在后台预加载常用股票的数据
4. WHEN 诊断计算超过 3 秒 THEN THE System SHALL 显示"正在分析中"提示
5. THE System SHALL 优先计算并返回核心评分，然后异步加载详细数据
6. THE System SHALL 使用 CDN 加速图片卡片的生成和分享

### Requirement 17: 错误处理和友好提示

**User Story:** 作为投资者，当系统无法诊断某只股票时，我希望看到清晰的原因说明。

#### Acceptance Criteria

1. WHEN 股票代码不存在 THEN THE System SHALL 显示"未找到该股票，请检查代码"
2. WHEN 股票数据不足 THEN THE System SHALL 显示"该股票数据不足，无法生成诊断报告"
3. WHEN 股票已退市 THEN THE System SHALL 显示"该股票已退市"
4. WHEN 股票处于停牌状态 THEN THE System SHALL 显示"该股票当前停牌，诊断结果可能不准确"
5. WHEN 网络请求失败 THEN THE System SHALL 显示"网络不稳定，请稍后重试"
6. THE System SHALL 在错误提示中提供"重试"按钮
7. THE System SHALL 避免显示技术错误信息（如"API 500 错误"）

### Requirement 18: 合规性和免责声明

**User Story:** 作为系统运营者，我希望在诊断报告中显著展示免责声明，符合监管要求。

#### Acceptance Criteria

1. THE System SHALL 在诊断报告顶部显示免责声明
2. THE System SHALL 在免责声明中包含"本诊断仅供参考，不构成投资建议"
3. THE System SHALL 在免责声明中包含"投资者据此操作，风险自担"
4. THE System SHALL 在免责声明中包含"历史表现不代表未来收益"
5. THE System SHALL 在分享的图片卡片中包含简化版免责声明
6. THE System SHALL 在首次使用诊断功能时弹出完整免责声明，要求用户确认
7. THE System SHALL 记录用户的免责声明确认状态

### Requirement 19: 数据来源透明

**User Story:** 作为投资者，我希望知道诊断结果基于哪些数据源，以便评估其可信度。

#### Acceptance Criteria

1. THE System SHALL 在诊断报告底部显示"数据来源"说明
2. THE System SHALL 在数据来源中列出使用的数据接口（如"同花顺 API"）
3. THE System SHALL 在数据来源中显示数据更新时间
4. THE System SHALL 在数据来源中显示数据覆盖范围（如"最近 3 个月 K 线数据"）
5. WHEN 使用第三方数据时 THEN THE System SHALL 标注数据提供方
6. THE System SHALL 提供"数据质量"评级（如"数据完整度 95%"）

### Requirement 20: A/B 测试和持续优化

**User Story:** 作为产品经理，我希望能够追踪诊断功能的使用情况和准确率，以便持续优化。

#### Acceptance Criteria

1. THE System SHALL 记录每次诊断请求的股票代码、评分、信号灯
2. THE System SHALL 记录用户是否采纳了诊断建议（通过后续行为推断）
3. THE System SHALL 定期计算诊断准确率（诊断后 N 天的实际表现）
4. THE System SHALL 支持 A/B 测试不同的评分算法
5. THE System SHALL 生成诊断功能的使用报告（如"本周诊断 1000 次，准确率 68%"）
6. THE System SHALL 识别诊断失误的案例，用于算法优化
7. THE System SHALL 支持导出诊断数据用于离线分析

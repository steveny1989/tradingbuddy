# Requirements Document: 盘后复盘系统

## Introduction

TradingBuddy 盘后复盘系统是一个"傻瓜式"的投资决策辅助工具，让用户在5分钟内完成每日复盘，无需理解复杂的技术指标。

**核心理念：**
- 拒绝堆砌数据
- 一键式操作
- 人类可读的结论
- 自动化触发

**目标用户：**
- 上班族投资者（晚上8-11点使用）
- 不懂技术指标的普通投资者
- 需要快速决策的短线交易者

## Glossary

- **System**: 盘后复盘系统
- **Market_Sentiment_Module**: 市场情绪模块（市场"体温计"）
- **Portfolio_Health_Module**: 持仓健康模块（持仓"自动体检"）
- **Actionable_Insights_Module**: 明日锦囊模块
- **PMU**: Post-Market Users，晚间活跃用户
- **Decision_Conversion**: 决策转化率
- **CAGR**: Compound Annual Growth Rate，复合年增长率
- **Alpha**: 超额收益

---

## Requirements

### Requirement 1: 市场情绪模块（市场"体温计"）

**User Story:** 作为投资者，我想一眼看懂当前市场情绪，所以我能快速决定明天是否操作。

#### Acceptance Criteria

1. WHEN 用户打开盘后复盘页面 THEN THE System SHALL 显示市场情绪状态（三种之一）
2. THE System SHALL 计算涨跌停比、连板高度、两市成交额
3. THE System SHALL 将市场情绪分为三种状态：
   - "情绪火热（大胆操作）"
   - "情绪冰点（等待机会）"
   - "情绪平淡（按兵不动）"
4. WHEN 市场涨停股票数 > 100 AND 连板高度 > 5 AND 成交额 > 1万亿 THEN THE System SHALL 显示"情绪火热"
5. WHEN 市场跌停股票数 > 100 OR 成交额 < 5000亿 THEN THE System SHALL 显示"情绪冰点"
6. WHEN 市场情绪不满足火热或冰点条件 THEN THE System SHALL 显示"情绪平淡"
7. THE System SHALL 用颜色区分状态：红色（火热）、蓝色（冰点）、灰色（平淡）
8. THE System SHALL 显示一句话解释（如："今日涨停100+，连板高度7板，资金活跃"）

---

### Requirement 2: 持仓健康模块（持仓"自动体检"）

**User Story:** 作为投资者，我想知道我的持仓是否健康，所以我能及时止损或持有。

#### Acceptance Criteria

1. WHEN 用户导入持仓列表 THEN THE System SHALL 对每只股票进行健康检查
2. THE System SHALL 使用 ma_crossover 策略判断趋势
3. THE System SHALL 使用 volume_shrink 策略判断缩量情况
4. THE System SHALL 为每只股票显示三种状态之一：
   - 🟢 绿灯（健康）："趋势向上，建议继续持有"
   - 🟡 黄灯（警示）："出现缩量滞涨，建议减仓规避风险"
   - 🔴 红灯（危险）："破位下跌，触发系统止损阈值"
5. WHEN 股价在20日均线以上 AND 成交量正常 THEN THE System SHALL 显示绿灯
6. WHEN 股价在20日均线附近 AND 成交量萎缩 > 30% THEN THE System SHALL 显示黄灯
7. WHEN 股价跌破20日均线 AND 跌幅 > 5% THEN THE System SHALL 显示红灯
8. THE System SHALL 按危险程度排序（红灯优先显示）
9. THE System SHALL 显示每只股票的关键指标：现价、涨跌幅、20日均线偏离度

---

### Requirement 3: 明日锦囊模块

**User Story:** 作为投资者，我想知道明天有哪些机会，所以我能提前做好准备。

#### Acceptance Criteria

1. WHEN 盘后复盘生成完成 THEN THE System SHALL 推荐3个明日最具Alpha潜力的方向
2. THE System SHALL 基于回测引擎筛选高胜率板块或个股
3. THE System SHALL 为每个推荐附带一句话理由（如："国产替代逻辑加强，资金流入明显"）
4. THE System SHALL 显示历史胜率指标（如："过去30天胜率65%"）
5. WHEN 某个方向的历史CAGR < 10% THEN THE System SHALL NOT 推荐该方向
6. THE System SHALL 优先推荐符合当前市场情绪的方向
7. THE System SHALL 提供"加入明日关注"按钮
8. THE System SHALL 提供"设置闹钟"按钮（开盘前提醒）

---

### Requirement 4: 自动触发机制

**User Story:** 作为系统管理员，我想让复盘报告自动生成，所以用户晚上打开就能看到。

#### Acceptance Criteria

1. THE System SHALL 在每个交易日下午4:00自动触发数据同步
2. WHEN 数据同步完成 THEN THE System SHALL 自动触发回测引擎
3. THE System SHALL 在晚上8:00前完成所有复盘报告生成
4. WHEN 报告生成失败 THEN THE System SHALL 发送告警通知
5. THE System SHALL 记录每次生成的时间和状态
6. THE System SHALL 支持手动触发复盘生成（用于测试）

---

### Requirement 5: 数据质量保证

**User Story:** 作为系统管理员，我想确保推荐的股票质量高，所以用户不会买到垃圾股。

#### Acceptance Criteria

1. THE System SHALL 过滤流动性不足的股票（日成交额 < 1000万）
2. THE System SHALL 过滤ST股票和退市风险股票
3. THE System SHALL 过滤涨跌幅异常的股票（单日涨跌幅 > 15%且无基本面支撑）
4. THE System SHALL 使用 data_validator 验证数据完整性
5. WHEN 数据质量不达标 THEN THE System SHALL 标记为"数据异常，暂不推荐"
6. THE System SHALL 记录被过滤的股票及原因

---

### Requirement 6: 历史胜率验证

**User Story:** 作为投资者，我想知道系统推荐的历史准确率，所以我能判断是否值得信任。

#### Acceptance Criteria

1. THE System SHALL 为每个推荐显示历史胜率
2. THE System SHALL 计算过去30天、90天、1年的胜率
3. WHEN 历史胜率 < 50% THEN THE System SHALL NOT 推荐
4. THE System SHALL 显示平均收益率和最大回撤
5. THE System SHALL 显示推荐次数和成功次数
6. THE System SHALL 每周更新历史胜率数据

---

### Requirement 7: 用户交互体验

**User Story:** 作为投资者，我想快速完成复盘，所以我能在5分钟内做出决策。

#### Acceptance Criteria

1. THE System SHALL 在3秒内加载完整复盘页面
2. THE System SHALL 使用大字体和清晰的颜色区分
3. THE System SHALL 避免使用技术术语（如RSI、MACD等）
4. THE System SHALL 提供"一键导出"功能（PDF或图片）
5. THE System SHALL 支持移动端适配
6. THE System SHALL 提供"历史复盘"查看功能（查看过去的复盘报告）

---

### Requirement 8: 性能指标监控

**User Story:** 作为产品经理，我想监控系统的关键指标，所以我能持续优化产品。

#### Acceptance Criteria

1. THE System SHALL 记录PMU（晚间8-11点活跃用户占比）
2. THE System SHALL 记录Decision_Conversion（决策转化率）
3. THE System SHALL 记录Average_Drawdown（平均回撤）
4. THE System SHALL 每日生成KPI报告
5. THE System SHALL 对比用户账户回撤与市场平均水平
6. WHEN Decision_Conversion < 30% THEN THE System SHALL 触发产品优化告警
7. THE System SHALL 记录用户停留时长和点击路径

---

### Requirement 9: 持仓导入功能

**User Story:** 作为投资者，我想快速导入我的持仓，所以系统能帮我体检。

#### Acceptance Criteria

1. THE System SHALL 支持手动输入股票代码
2. THE System SHALL 支持CSV文件导入
3. THE System SHALL 支持从券商账户同步（如果可能）
4. THE System SHALL 验证股票代码有效性
5. WHEN 股票代码无效 THEN THE System SHALL 提示用户并跳过
6. THE System SHALL 保存用户的持仓列表（下次自动加载）
7. THE System SHALL 支持编辑和删除持仓

---

### Requirement 10: 明日提醒功能

**User Story:** 作为投资者，我想在开盘前收到提醒，所以我不会错过机会。

#### Acceptance Criteria

1. WHEN 用户点击"设置闹钟" THEN THE System SHALL 在开盘前15分钟发送通知
2. THE System SHALL 支持多种通知方式：App推送、短信、邮件
3. THE System SHALL 在通知中包含关键信息：股票代码、推荐理由、当前价格
4. THE System SHALL 允许用户自定义提醒时间
5. THE System SHALL 允许用户关闭提醒功能
6. THE System SHALL 记录提醒发送状态

---

## 特殊要求

### 解析器和序列化器要求

**Parser Requirements:**
- THE System SHALL 解析市场数据（涨跌停、成交额等）
- THE System SHALL 解析用户持仓数据（CSV格式）
- THE System SHALL 验证数据格式的正确性

**Serializer Requirements:**
- THE System SHALL 将复盘报告序列化为JSON格式
- THE System SHALL 支持导出为PDF格式
- THE System SHALL 支持导出为图片格式（用于分享）

**Round-trip Property:**
- FOR ALL 复盘报告，序列化后再反序列化应得到相同的数据结构

---

## 非功能性需求

### 性能要求
- 复盘报告生成时间 < 5分钟
- 页面加载时间 < 3秒
- 支持1000+并发用户

### 可靠性要求
- 系统可用性 > 99.5%
- 数据准确性 > 99%
- 自动重试机制（失败后自动重试3次）

### 安全性要求
- 用户持仓数据加密存储
- API接口需要身份验证
- 防止数据泄露

---

## 成功指标（KPIs）

1. **PMU (Post-Market Users)**: 晚间8-11点活跃用户占比 > 40%
2. **Decision Conversion**: 决策转化率 > 30%
3. **Average Drawdown**: 用户平均回撤 < 市场平均水平
4. **User Retention**: 7日留存率 > 50%
5. **Average Session Time**: 平均停留时长 > 5分钟

---

## 技术约束

1. 必须使用现有的 `ma_crossover` 和 `volume_shrink` 策略
2. 必须使用现有的 `BacktestEngine` 进行回测
3. 必须使用现有的 `data_validator` 进行数据验证
4. 必须在下午4:00自动触发
5. 必须在晚上8:00前完成生成

---

## 优先级

**P0 (必须有):**
- Requirement 1: 市场情绪模块
- Requirement 2: 持仓健康模块
- Requirement 4: 自动触发机制

**P1 (应该有):**
- Requirement 3: 明日锦囊模块
- Requirement 5: 数据质量保证
- Requirement 6: 历史胜率验证

**P2 (可以有):**
- Requirement 7: 用户交互体验优化
- Requirement 9: 持仓导入功能
- Requirement 10: 明日提醒功能

**P3 (未来考虑):**
- Requirement 8: 性能指标监控（先手动监控）

# Requirements Document

## Introduction

本文档定义了"AI 选股评分与决策辅助系统"的需求。该系统旨在将现有的二元信号选股机制升级为基于评分的智能决策支持系统，为用户提供更精细、可解释的选股建议。

系统核心目标：
- 从"满足/不满足"的二元判断转向"信号强度评分"
- 提供可解释的选股理由和关键指标快照
- 支持多因子联动筛选和历史信号追踪
- 为用户提供决策参考而非交易指令

## Glossary

- **Stock_Scoring_Engine**: 股票评分引擎，负责计算信号强度分数
- **Signal_Explainer**: 信号解释器，生成选股理由的自然语言描述
- **Multi_Factor_Filter**: 多因子筛选器，支持技术面+基本面联动筛选
- **Signal_History_Tracker**: 信号历史追踪器，记录和验证历史选股效果
- **Strategy_Scanner**: 策略扫描器，执行股票池扫描并生成信号
- **API_Layer**: API 层，为前端提供选股数据接口
- **Signal**: 选股信号，包含股票代码、日期、价格、评分、理由等信息
- **Confidence_Score**: 置信度分数，表示信号强度（0-100）
- **Hit_Rate**: 命中率，历史信号的有效性统计指标

## Requirements

### Requirement 1: 信号评分系统

**User Story:** 作为投资者，我希望看到每个选股信号的强度评分，以便我能够优先关注高质量的机会。

#### Acceptance Criteria

1. WHEN Stock_Scoring_Engine 计算信号时，THE System SHALL 生成一个 0-100 的置信度分数
2. WHEN 计算置信度分数时，THE System SHALL 综合考虑成交量放大倍数、均线角度、大盘环境等多个因子
3. WHEN 返回选股结果时，THE System SHALL 按照置信度分数降序排列
4. WHEN 置信度分数低于 30 时，THE System SHALL 过滤该信号不予展示
5. WHEN 用户查询信号列表时，THE System SHALL 在每个信号中包含 confidence_score 字段

### Requirement 2: 信号可解释性

**User Story:** 作为投资者，我希望了解为什么系统推荐某只股票，以便我能够理解选股逻辑并做出判断。

#### Acceptance Criteria

1. WHEN Signal_Explainer 生成选股理由时，THE System SHALL 输出自然语言描述
2. WHEN 生成选股理由时，THE System SHALL 包含触发条件（如"5日线上穿20日线"）
3. WHEN 生成选股理由时，THE System SHALL 包含关键指标数值（如"成交量放大2.3倍"）
4. WHEN 返回信号时，THE System SHALL 包含 reason 字段存储选股理由
5. WHEN 返回信号时，THE System SHALL 包含关键指标快照（ma_short, ma_long, volume_ratio 等）

### Requirement 3: 多因子联动筛选

**User Story:** 作为投资者，我希望能够按照多个维度筛选股票，以便找到符合我特定需求的标的。

#### Acceptance Criteria

1. WHEN Multi_Factor_Filter 执行筛选时，THE System SHALL 支持按行业分类筛选
2. WHEN Multi_Factor_Filter 执行筛选时，THE System SHALL 支持按市盈率范围筛选
3. WHEN Multi_Factor_Filter 执行筛选时，THE System SHALL 支持按近期涨跌幅筛选
4. WHEN Multi_Factor_Filter 执行筛选时，THE System SHALL 支持按市值范围筛选
5. WHEN Multi_Factor_Filter 执行筛选时，THE System SHALL 支持按流动性指标筛选
6. WHEN 用户提供多个筛选条件时，THE System SHALL 应用所有条件的交集
7. WHEN 基本面数据缺失时，THE System SHALL 跳过该股票而不是报错

### Requirement 4: 历史信号追踪与验证

**User Story:** 作为投资者，我希望看到历史选股信号的表现，以便评估策略的有效性。

#### Acceptance Criteria

1. WHEN Signal_History_Tracker 记录信号时，THE System SHALL 将信号存储到 strategy_signals 表
2. WHEN 存储信号时，THE System SHALL 记录股票代码、日期、价格、评分、策略名称
3. WHEN 用户查询历史信号时，THE System SHALL 计算信号发出后 N 天的实际涨跌幅
4. WHEN 计算历史表现时，THE System SHALL 支持 3 天、5 天、10 天等多个时间窗口
5. WHEN 展示历史信号时，THE System SHALL 显示命中率（上涨概率）和平均收益率
6. WHEN 信号发出超过 10 个交易日时，THE System SHALL 自动计算并更新其表现数据

### Requirement 5: 异步扫描与缓存

**User Story:** 作为系统管理员，我希望选股扫描在后台自动执行，以便 API 响应速度快且不超时。

#### Acceptance Criteria

1. WHEN Strategy_Scanner 执行扫描时，THE System SHALL 在后台线程中运行
2. WHEN 扫描完成时，THE System SHALL 将结果存储到 scan_results 表
3. WHEN API_Layer 接收查询请求时，THE System SHALL 从缓存表读取结果而非实时扫描
4. WHEN 扫描任务失败时，THE System SHALL 记录错误日志并保留上次成功的结果
5. WHEN 每日收盘后，THE System SHALL 自动触发扫描任务
6. WHEN 用户手动触发扫描时，THE System SHALL 返回任务 ID 供查询进度

### Requirement 6: 增强的 API 接口

**User Story:** 作为前端开发者，我希望 API 提供丰富的筛选和排序选项，以便构建灵活的用户界面。

#### Acceptance Criteria

1. WHEN API_Layer 处理 GET /api/signals 请求时，THE System SHALL 支持按策略类型筛选
2. WHEN API_Layer 处理 GET /api/signals 请求时，THE System SHALL 支持按置信度分数范围筛选
3. WHEN API_Layer 处理 GET /api/signals 请求时，THE System SHALL 支持按日期范围筛选
4. WHEN API_Layer 处理 GET /api/signals 请求时，THE System SHALL 支持多种排序方式（评分、涨跌幅、市值）
5. WHEN API_Layer 处理 GET /api/signals/:id/history 请求时，THE System SHALL 返回该信号的历史表现
6. WHEN API_Layer 处理 GET /api/signals/stats 请求时，THE System SHALL 返回策略整体统计数据
7. WHEN API 返回错误时，THE System SHALL 提供清晰的错误代码和描述

### Requirement 7: 基本面数据集成

**User Story:** 作为投资者，我希望选股时能够排除财务状况不佳的公司，以便降低投资风险。

#### Acceptance Criteria

1. WHEN Multi_Factor_Filter 检查基本面时，THE System SHALL 排除连续两年亏损的股票
2. WHEN Multi_Factor_Filter 检查基本面时，THE System SHALL 排除资产负债率超过 80% 的股票
3. WHEN Multi_Factor_Filter 检查基本面时，THE System SHALL 排除商誉占净资产比例超过 50% 的股票
4. WHEN 基本面数据不可用时，THE System SHALL 记录警告但继续处理
5. WHEN 用户启用基本面过滤时，THE System SHALL 在 API 响应中标注已应用的过滤器

### Requirement 8: 合规性声明

**User Story:** 作为系统运营者，我希望在所有用户界面显著位置展示免责声明，以便符合监管要求。

#### Acceptance Criteria

1. WHEN API_Layer 返回选股信号时，THE System SHALL 在响应中包含 disclaimer 字段
2. WHEN 生成免责声明时，THE System SHALL 包含"本工具仅供科研与数据参考"的文字
3. WHEN 生成免责声明时，THE System SHALL 包含"不构成任何投资建议"的文字
4. WHEN 生成免责声明时，THE System SHALL 包含"投资者据此操作，风险自担"的文字
5. WHEN 前端展示选股结果时，THE System SHALL 在页面显著位置展示免责声明

### Requirement 9: 性能优化

**User Story:** 作为系统管理员，我希望扫描大规模股票池时系统保持高效，以便及时提供选股结果。

#### Acceptance Criteria

1. WHEN Strategy_Scanner 扫描超过 1000 只股票时，THE System SHALL 在 5 分钟内完成
2. WHEN 数据库查询历史数据时，THE System SHALL 使用索引优化查询速度
3. WHEN 计算技术指标时，THE System SHALL 使用向量化计算而非循环
4. WHEN API 响应时间超过 2 秒时，THE System SHALL 记录性能警告日志
5. WHEN 系统负载过高时，THE System SHALL 限制并发扫描任务数量

### Requirement 10: 数据持久化

**User Story:** 作为数据分析师，我希望系统保存所有历史信号和扫描结果，以便进行回测和策略优化。

#### Acceptance Criteria

1. WHEN 扫描完成时，THE System SHALL 将所有信号存储到 strategy_signals 表
2. WHEN 存储信号时，THE System SHALL 包含完整的指标快照（ma_short, ma_long, volume_ratio 等）
3. WHEN 存储信号时，THE System SHALL 记录扫描时间戳和策略参数
4. WHEN 数据库写入失败时，THE System SHALL 重试最多 3 次
5. WHEN 历史数据超过 1 年时，THE System SHALL 提供归档功能

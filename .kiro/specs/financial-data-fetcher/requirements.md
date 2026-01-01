# Requirements Document - Financial Data Fetcher System

## Introduction

财务数据采集系统负责从外部数据源（新浪财经API）获取上市公司的三大财务报表（资产负债表、利润表、现金流量表）和财务指标数据，并存储到本地数据库。系统需要具备健壮的错误处理、准确的状态跟踪、以及高效的批量下载能力。

## Glossary

- **Financial_Fetcher**: 财务数据采集器，负责从API获取财务数据
- **Balance_Sheet**: 资产负债表，记录公司资产、负债和所有者权益
- **Income_Statement**: 利润表，记录公司收入、成本和利润
- **Cash_Flow_Statement**: 现金流量表，记录公司现金流入流出
- **Financial_Indicators**: 财务指标，包括盈利能力、偿债能力等计算指标
- **Data_Source**: 数据源，指新浪财经API
- **Batch_Download**: 批量下载，指一次性下载多只股票的财务数据
- **Success_Status**: 成功状态，指至少有一张报表成功获取并保存
- **Failure_Status**: 失败状态，指所有报表都获取失败或为空
- **Empty_Data**: 空数据，指API返回空响应或无效数据
- **API_Error**: API错误，指网络错误、JSON解析错误等技术性错误
- **Stock_Database**: 股票数据库，存储所有财务数据

## Requirements

### Requirement 1: 准确的成功/失败判定

**User Story:** 作为系统管理员，我想准确知道哪些股票的财务数据下载成功，哪些失败，以便进行数据质量管理和问题排查。

#### Acceptance Criteria

1. WHEN 至少有一张财务报表成功获取并保存 THEN THE Financial_Fetcher SHALL 标记该股票为成功状态
2. WHEN 所有财务报表都获取失败或返回空数据 THEN THE Financial_Fetcher SHALL 标记该股票为失败状态
3. THE Financial_Fetcher SHALL 在结果字典中包含`has_data`标志，指示是否有任何数据被保存
4. WHEN 股票标记为失败 THEN THE Financial_Fetcher SHALL 记录警告日志说明原因
5. THE Financial_Fetcher SHALL 区分"API错误"和"股票无数据"两种失败情况

### Requirement 2: 详细的错误分类和日志

**User Story:** 作为开发者，我想了解数据获取失败的具体原因，以便优化系统和排查问题。

#### Acceptance Criteria

1. WHEN API返回JSON解析错误 THEN THE Financial_Fetcher SHALL 记录为"API_ERROR"类型
2. WHEN API返回空数据 THEN THE Financial_Fetcher SHALL 记录为"EMPTY_DATA"类型
3. WHEN 网络连接失败 THEN THE Financial_Fetcher SHALL 记录为"NETWORK_ERROR"类型
4. THE Financial_Fetcher SHALL 在结果字典中包含`error_type`字段
5. THE Financial_Fetcher SHALL 在结果字典中包含`error_details`字段，记录具体错误信息
6. THE Financial_Fetcher SHALL 为每种错误类型使用不同的日志级别（ERROR vs WARNING）

### Requirement 3: 批量下载统计准确性

**User Story:** 作为系统管理员，我想看到准确的批量下载统计数据，以便评估数据覆盖率和下载质量。

#### Acceptance Criteria

1. THE Financial_Fetcher SHALL 统计真正成功的股票数量（有数据保存）
2. THE Financial_Fetcher SHALL 统计失败的股票数量（无任何数据）
3. THE Financial_Fetcher SHALL 统计每种失败类型的数量（API错误、空数据、网络错误）
4. THE Financial_Fetcher SHALL 在批量下载完成后输出详细统计报告
5. THE Financial_Fetcher SHALL 记录失败股票的代码列表，按失败类型分组

### Requirement 4: 财务指标计算

**User Story:** 作为量化交易者，我想获得计算好的财务指标，因为API不提供这些数据。

#### Acceptance Criteria

1. THE Financial_Fetcher SHALL 从三大报表计算ROE（净资产收益率）
2. THE Financial_Fetcher SHALL 从三大报表计算ROA（总资产收益率）
3. THE Financial_Fetcher SHALL 从三大报表计算毛利率
4. THE Financial_Fetcher SHALL 从三大报表计算净利率
5. THE Financial_Fetcher SHALL 从三大报表计算资产负债率
6. THE Financial_Fetcher SHALL 从三大报表计算流动比率
7. THE Financial_Fetcher SHALL 从三大报表计算速动比率
8. WHEN 计算所需的数据字段缺失或为零 THEN THE Financial_Fetcher SHALL 返回None而不是抛出异常
9. THE Financial_Fetcher SHALL 将计算结果保存到financial_indicators表

### Requirement 5: 重试机制

**User Story:** 作为系统管理员，我想对临时性失败进行自动重试，以便提高数据获取成功率。

#### Acceptance Criteria

1. WHEN API返回网络错误 THEN THE Financial_Fetcher SHALL 自动重试最多3次
2. WHEN API返回JSON解析错误 THEN THE Financial_Fetcher SHALL 自动重试最多2次
3. THE Financial_Fetcher SHALL 在重试之间等待递增的时间（1秒、2秒、4秒）
4. WHEN 重试次数耗尽仍失败 THEN THE Financial_Fetcher SHALL 标记为最终失败
5. THE Financial_Fetcher SHALL 记录每次重试的日志

### Requirement 6: 失败股票重新下载

**User Story:** 作为系统管理员，我想能够重新下载失败的股票，而不是重新下载全部数据。

#### Acceptance Criteria

1. THE Financial_Fetcher SHALL 提供方法获取失败股票列表
2. THE Financial_Fetcher SHALL 提供方法仅下载指定的股票列表
3. THE Financial_Fetcher SHALL 在批量下载完成后保存失败股票列表到文件
4. THE Financial_Fetcher SHALL 提供命令行参数支持从失败列表文件重新下载

### Requirement 7: 数据完整性验证

**User Story:** 作为数据分析师，我想确保保存的财务数据是完整和有效的，以便进行可靠的分析。

#### Acceptance Criteria

1. THE Financial_Fetcher SHALL 验证报告日期格式正确（YYYY-MM-DD）
2. THE Financial_Fetcher SHALL 验证数值字段可以转换为float类型
3. THE Financial_Fetcher SHALL 拒绝保存全部字段都为None的记录
4. THE Financial_Fetcher SHALL 验证报告期类型正确（Q1、Q2、Q3、annual）
5. WHEN 数据验证失败 THEN THE Financial_Fetcher SHALL 记录警告并跳过该记录

### Requirement 8: 性能优化

**User Story:** 作为系统管理员，我想提高批量下载的效率，以便更快完成全市场数据更新。

#### Acceptance Criteria

1. THE Financial_Fetcher SHALL 使用合理的API限速策略（每只股票2秒）
2. THE Financial_Fetcher SHALL 每10只股票额外休息2秒，避免触发API限流
3. THE Financial_Fetcher SHALL 使用批量数据库插入，而不是逐条插入
4. THE Financial_Fetcher SHALL 显示实时进度条，包括速度和预计剩余时间
5. THE Financial_Fetcher SHALL 支持断点续传（从上次中断的位置继续）

### Requirement 9: 数据更新策略

**User Story:** 作为系统管理员，我想智能地更新财务数据，避免重复下载已有数据。

#### Acceptance Criteria

1. THE Financial_Fetcher SHALL 检查股票是否已有财务数据
2. WHEN 股票已有数据且距离上次更新不足7天 THEN THE Financial_Fetcher SHALL 跳过该股票
3. THE Financial_Fetcher SHALL 提供"强制更新"选项，忽略已有数据
4. THE Financial_Fetcher SHALL 只更新最新的报告期数据（增量更新）
5. THE Financial_Fetcher SHALL 记录每只股票的最后更新时间

### Requirement 10: 监控和告警

**User Story:** 作为系统管理员，我想监控财务数据采集的健康状态，以便及时发现和解决问题。

#### Acceptance Criteria

1. THE Financial_Fetcher SHALL 记录每次批量下载的开始和结束时间
2. THE Financial_Fetcher SHALL 计算并记录平均下载速度（股票/秒）
3. WHEN 失败率超过20% THEN THE Financial_Fetcher SHALL 记录ERROR级别日志
4. THE Financial_Fetcher SHALL 生成下载报告文件，包含所有统计信息
5. THE Financial_Fetcher SHALL 提供健康检查接口，返回最近一次下载的状态


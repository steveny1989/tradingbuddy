# Implementation Plan: Financial Data Fetcher System

## Overview

本实施计划将现有的财务数据采集系统重构为更健壮、可维护的架构。重点改进错误处理、状态跟踪、重试机制和财务指标计算。所有改进将基于Python实现，使用Hypothesis进行property-based testing。

## Tasks

- [ ] 1. 创建核心数据模型和枚举类型
  - 定义ErrorType枚举（API_ERROR, NETWORK_ERROR, EMPTY_DATA等）
  - 定义FetchStatus枚举（NOT_STARTED, IN_PROGRESS, SUCCESS, FAILED, SKIPPED）
  - 创建FetchResult dataclass
  - 创建BatchResult dataclass
  - 创建ValidationResult dataclass
  - _Requirements: 1.3, 2.4, 2.5_

- [ ]* 1.1 为数据模型编写单元测试
  - 测试dataclass实例化
  - 测试枚举值有效性
  - _Requirements: 1.3, 2.4, 2.5_

- [ ] 2. 实现ErrorClassifier错误分类器
  - [ ] 2.1 实现classify_error方法
    - 根据异常类型分类错误
    - 处理JSONDecodeError → API_ERROR
    - 处理网络相关异常 → NETWORK_ERROR
    - 处理空DataFrame → EMPTY_DATA
    - _Requirements: 1.5, 2.1, 2.2, 2.3_

  - [ ] 2.2 实现should_retry方法
    - API_ERROR和NETWORK_ERROR返回True
    - 其他错误类型返回False
    - _Requirements: 5.1, 5.2_

  - [ ] 2.3 实现get_retry_count方法
    - NETWORK_ERROR返回3
    - API_ERROR返回2
    - 其他返回0
    - _Requirements: 5.1, 5.2_

  - [ ]* 2.4 编写ErrorClassifier的单元测试
    - 测试各种异常类型的分类
    - 测试重试决策逻辑
    - _Requirements: 1.5, 2.1, 2.2, 2.3_

- [ ] 3. 实现DataValidator数据验证器
  - [ ] 3.1 实现validate_report_date方法
    - 验证日期格式YYYY-MM-DD
    - 验证年月日的有效性
    - _Requirements: 7.1_

  - [ ]* 3.2 编写日期验证的property test
    - **Property 10: Date format validation**
    - **Validates: Requirements 7.1**

  - [ ] 3.3 实现validate_numeric_field方法
    - 检查值是否可转换为float
    - 处理None、空字符串、非数值字符串
    - _Requirements: 7.2_

  - [ ]* 3.4 编写数值验证的property test
    - **Property: Numeric field validation**
    - **Validates: Requirements 7.2**

  - [ ] 3.5 实现validate_report_type方法
    - 验证报告类型为Q1/Q2/Q3/annual之一
    - _Requirements: 7.4_

  - [ ]* 3.6 编写报告类型验证的property test
    - **Property 11: Report type validation**
    - **Validates: Requirements 7.4**

  - [ ] 3.7 实现has_valid_data方法
    - 检查DataFrame是否有至少一个非None值
    - _Requirements: 7.3_

  - [ ]* 3.8 编写all-None记录拒绝的property test
    - **Property 12: All-None record rejection**
    - **Validates: Requirements 7.3**

- [ ] 4. 实现FinancialCalculator财务指标计算器
  - [ ] 4.1 实现calculate_roe方法
    - 公式: ROE = (net_profit / shareholders_equity) * 100
    - 处理None和零除错误，返回None
    - _Requirements: 4.1, 4.8_

  - [ ]* 4.2 编写ROE计算的property test
    - **Property 7: ROE calculation correctness**
    - **Validates: Requirements 4.1**

  - [ ] 4.3 实现calculate_roa方法
    - 公式: ROA = (net_profit / total_assets) * 100
    - 处理None和零除错误
    - _Requirements: 4.2, 4.8_

  - [ ] 4.4 实现calculate_gross_margin方法
    - 公式: gross_margin = ((revenue - cost) / revenue) * 100
    - 处理None和零除错误
    - _Requirements: 4.3, 4.8_

  - [ ] 4.5 实现calculate_net_margin方法
    - 公式: net_margin = (net_profit / revenue) * 100
    - 处理None和零除错误
    - _Requirements: 4.4, 4.8_

  - [ ] 4.6 实现calculate_debt_ratio方法
    - 公式: debt_ratio = (liabilities / assets) * 100
    - 处理None和零除错误
    - _Requirements: 4.5, 4.8_

  - [ ] 4.7 实现calculate_current_ratio方法
    - 公式: current_ratio = current_assets / current_liabilities
    - 处理None和零除错误
    - _Requirements: 4.6, 4.8_

  - [ ]* 4.8 编写流动比率计算的property test
    - **Property 8: Current ratio calculation correctness**
    - **Validates: Requirements 4.6**

  - [ ] 4.9 实现calculate_quick_ratio方法
    - 公式: quick_ratio = (current_assets - inventory) / current_liabilities
    - 处理None和零除错误
    - _Requirements: 4.7, 4.8_

  - [ ]* 4.10 编写速动比率计算的property test
    - **Property 9: Quick ratio calculation correctness**
    - **Validates: Requirements 4.7**

  - [ ] 4.11 实现calculate_indicators方法
    - 整合所有计算方法
    - 从三大报表DataFrame提取数据并计算
    - 返回包含所有指标的DataFrame
    - _Requirements: 4.1-4.7, 4.9_

  - [ ]* 4.12 编写安全计算的property test
    - **Property 6: Financial indicator calculations are safe**
    - **Validates: Requirements 4.8**

- [ ] 5. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，询问用户是否有问题

- [ ] 6. 实现StatementFetcher报表获取器（重构现有代码）
  - [ ] 6.1 添加重试机制到fetch_balance_sheet
    - 使用_retry_with_backoff包装API调用
    - 记录重试日志
    - 返回FetchResult而不是DataFrame
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [ ] 6.2 添加重试机制到fetch_income_statement
    - 同样的重试逻辑
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [ ] 6.3 添加重试机制到fetch_cash_flow
    - 同样的重试逻辑
    - _Requirements: 5.1, 5.2, 5.3, 5.5_

  - [ ] 6.4 实现_retry_with_backoff方法
    - 指数退避策略（1s, 2s, 4s）
    - 使用ErrorClassifier判断是否重试
    - 记录每次重试
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 6.5 编写重试机制的单元测试
    - 测试网络错误重试3次
    - 测试API错误重试2次
    - 测试退避时间间隔
    - 测试最终失败标记
    - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 7. 重构FinancialDataFetcher主类
  - [ ] 7.1 更新fetch_all_financial_data方法
    - 使用新的FetchResult返回类型
    - 添加error_type和error_details字段
    - 实现准确的成功判定（has_data标志）
    - 调用FinancialCalculator计算指标
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.9_

  - [ ]* 7.2 编写成功判定的property test
    - **Property 1: Success determination based on data presence**
    - **Validates: Requirements 1.1, 1.2**

  - [ ]* 7.3 编写结果结构完整性的property test
    - **Property 2: Result structure completeness**
    - **Validates: Requirements 1.3, 2.4, 2.5**

  - [ ]* 7.4 编写错误分类的property test
    - **Property 3: Error type classification**
    - **Validates: Requirements 1.5, 2.1, 2.2, 2.3**

- [ ] 8. 实现ProgressTracker进度跟踪器
  - [ ] 8.1 实现基本进度跟踪
    - 初始化计数器（total, success, failed）
    - 按错误类型统计失败（error_stats）
    - 记录失败股票列表（failed_stocks）
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

  - [ ] 8.2 实现update方法
    - 更新成功/失败计数
    - 更新错误类型统计
    - 添加失败股票到对应列表
    - _Requirements: 3.1, 3.2, 3.3, 3.5_

  - [ ] 8.3 实现get_statistics方法
    - 返回完整统计信息
    - 计算成功率
    - 计算平均速度
    - _Requirements: 3.1, 3.2, 3.3, 10.2_

  - [ ]* 8.4 编写批量统计准确性的property test
    - **Property 4: Batch statistics accuracy**
    - **Validates: Requirements 3.1, 3.2, 3.3**

  - [ ]* 8.5 编写失败股票分组的property test
    - **Property 5: Failed stocks grouping**
    - **Validates: Requirements 3.5**

  - [ ] 8.6 实现save_report方法
    - 生成包含所有统计信息的报告文件
    - JSON格式，包含时间戳、计数、错误统计
    - _Requirements: 3.4, 10.4_

  - [ ]* 8.7 编写报告文件生成的property test
    - **Property 18: Report file generation**
    - **Validates: Requirements 3.4, 10.4**

  - [ ] 8.8 实现save_failed_list方法
    - 保存失败股票列表到JSON文件
    - 按错误类型分组
    - _Requirements: 6.3_

  - [ ]* 8.9 编写失败列表文件生成的property test
    - **Property 19: Failed list file generation**
    - **Validates: Requirements 6.3**

- [ ] 9. Checkpoint - 确保所有测试通过
  - 确保所有测试通过，询问用户是否有问题

- [ ] 10. 更新batch_fetch_financial_data方法
  - [ ] 10.1 集成ProgressTracker
    - 创建ProgressTracker实例
    - 在每次fetch后更新进度
    - 生成最终报告和失败列表
    - _Requirements: 3.1-3.5, 10.1, 10.4_

  - [ ] 10.2 添加force_update参数
    - 检查股票最后更新时间
    - 如果<7天且非force_update则跳过
    - _Requirements: 9.1, 9.2, 9.3_

  - [ ]* 10.3 编写更新频率强制的property test
    - **Property 13: Update frequency enforcement**
    - **Validates: Requirements 9.2, 9.3**

  - [ ] 10.4 添加resume_from参数
    - 支持从指定股票代码继续
    - 跳过已处理的股票
    - _Requirements: 8.5_

  - [ ] 10.5 添加高失败率告警
    - 计算失败率
    - 如果>20%记录ERROR日志
    - _Requirements: 10.3_

  - [ ]* 10.6 编写高失败率告警的property test
    - **Property 16: High failure rate alerting**
    - **Validates: Requirements 10.3**

  - [ ] 10.7 记录时间戳和计算速度
    - 记录start_time和end_time
    - 计算avg_speed
    - _Requirements: 10.1, 10.2_

  - [ ]* 10.8 编写时间戳记录的property test
    - **Property 14: Timestamp recording**
    - **Validates: Requirements 9.5, 10.1**

  - [ ]* 10.9 编写平均速度计算的property test
    - **Property 15: Average speed calculation**
    - **Validates: Requirements 10.2**

  - [ ]* 10.10 编写自定义股票列表处理的property test
    - **Property 17: Custom stock list processing**
    - **Validates: Requirements 6.2**

- [ ] 11. 实现retry_failed_stocks方法
  - 读取失败列表JSON文件
  - 提取所有失败股票代码
  - 调用batch_fetch_financial_data重新下载
  - _Requirements: 6.1, 6.2, 6.4_

- [ ]* 11.1 编写失败重试功能的单元测试
  - 测试从文件读取失败列表
  - 测试只处理失败的股票
  - _Requirements: 6.1, 6.2, 6.4_

- [ ] 12. 更新数据库方法以记录更新时间
  - [ ] 12.1 修改save_balance_sheet添加updated_at
    - 在保存时记录当前时间戳
    - _Requirements: 9.5_

  - [ ] 12.2 修改save_income_statement添加updated_at
    - 同样记录时间戳
    - _Requirements: 9.5_

  - [ ] 12.3 修改save_cash_flow添加updated_at
    - 同样记录时间戳
    - _Requirements: 9.5_

  - [ ] 12.4 修改save_financial_indicators添加updated_at
    - 同样记录时间戳
    - _Requirements: 9.5_

  - [ ] 12.5 添加get_last_update_time方法
    - 查询股票最后更新时间
    - 用于判断是否需要更新
    - _Requirements: 9.1, 9.2_

- [ ] 13. 更新CLI工具（tools/fetch_financial_data.py）
  - [ ] 13.1 添加--force参数
    - 支持强制更新
    - _Requirements: 9.3_

  - [ ] 13.2 添加--resume-from参数
    - 支持断点续传
    - _Requirements: 8.5_

  - [ ] 13.3 添加--retry-failed参数
    - 支持从失败列表重试
    - _Requirements: 6.4_

  - [ ] 13.4 添加--codes参数
    - 支持指定股票列表
    - _Requirements: 6.2_

  - [ ]* 13.5 编写CLI参数解析的单元测试
    - 测试各种参数组合
    - _Requirements: 6.2, 6.4, 8.5, 9.3_

- [ ] 14. 实现健康检查接口
  - 创建health_check函数
  - 返回最近一次批量下载状态
  - 返回数据库统计信息
  - _Requirements: 10.5_

- [ ]* 14.1 编写健康检查的单元测试
  - 测试返回格式
  - 测试状态判定逻辑
  - _Requirements: 10.5_

- [ ] 15. 更新文档
  - [ ] 15.1 更新FINANCIAL_DATA_README.md
    - 添加新功能说明
    - 添加错误处理说明
    - 添加CLI参数说明

  - [ ] 15.2 更新FINANCIAL_DATA_QUICKSTART.md
    - 添加常见使用场景
    - 添加故障排查指南

  - [ ] 15.3 创建FINANCIAL_DATA_API.md
    - 文档化所有公共API
    - 添加代码示例

- [ ] 16. 最终集成测试
  - [ ] 16.1 测试完整的批量下载流程
    - 使用小样本（10只股票）
    - 验证所有功能正常工作

  - [ ] 16.2 测试失败重试流程
    - 模拟部分失败
    - 验证失败列表生成
    - 验证重试功能

  - [ ] 16.3 测试断点续传
    - 中断批量下载
    - 使用resume-from继续
    - 验证无重复下载

  - [ ] 16.4 测试强制更新
    - 对已有数据的股票使用force_update
    - 验证数据被更新

- [ ] 17. 最终checkpoint - 确保所有测试通过
  - 运行完整测试套件
  - 确保所有property tests通过（100次迭代）
  - 询问用户是否准备部署

## Notes

- 任务标记`*`的为可选任务（主要是测试相关）
- 每个任务都引用了具体的需求编号以便追溯
- Checkpoint任务确保增量验证
- Property tests使用Hypothesis框架，最少100次迭代
- 重点改进：错误处理、状态跟踪、重试机制、财务指标计算


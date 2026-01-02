# Implementation Plan: AI 选股评分与决策辅助系统

## Overview

本实施计划将现有的二元信号选股机制升级为基于评分的智能决策支持系统。实施分为 8 个主要阶段，每个阶段都包含核心实现和可选的测试任务。

## Tasks

- [x] 1. 数据库扩展与表结构创建
  - 创建 strategy_signals 表用于存储历史信号
  - 创建 scan_results 表用于缓存扫描结果
  - 创建 scan_tasks 表用于管理异步任务
  - 为 market_cap_data 表添加 industry 字段
  - 创建必要的索引以优化查询性能
  - _Requirements: 4.1, 4.2, 5.2, 5.3, 10.1, 10.2_

- [ ]* 1.1 编写数据库迁移脚本的单元测试
  - 测试表创建逻辑
  - 测试索引创建逻辑
  - 测试数据迁移的幂等性
  - _Requirements: 10.4_

- [ ] 2. 实现评分引擎（Stock Scoring Engine）
  - [x] 2.1 创建 StockScoringEngine 类
    - 实现 calculate_score 方法
    - 实现各因子计算逻辑（成交量、均线角度、大盘环境、流动性、基本面）
    - 实现因子加权算法
    - _Requirements: 1.1, 1.2_

  - [ ]* 2.2 编写评分引擎的属性测试
    - **Property 1: 评分范围有效性**
    - **Validates: Requirements 1.1**

  - [ ]* 2.3 编写评分引擎的属性测试
    - **Property 2: 评分单调性**
    - **Validates: Requirements 1.2**

  - [ ]* 2.4 编写评分引擎的单元测试
    - 测试边界值（0, 100）
    - 测试异常输入处理
    - 测试各因子权重
    - _Requirements: 1.1, 1.2_

- [ ] 3. 实现信号解释器（Signal Explainer）
  - [ ] 3.1 创建 SignalExplainer 类
    - 实现 generate_reason 方法
    - 实现自然语言模板系统
    - 支持多种策略类型的理由生成
    - _Requirements: 2.1, 2.2, 2.3, 2.4_

  - [ ]* 3.2 编写信号解释器的属性测试
    - **Property 5: 理由字段完整性**
    - **Validates: Requirements 2.1, 2.2, 2.3, 2.4**

  - [ ]* 3.3 编写信号解释器的单元测试
    - 测试关键词包含
    - 测试空值处理
    - 测试不同策略类型
    - _Requirements: 2.1, 2.2, 2.3_

- [ ] 4. 实现多因子筛选器（Multi-Factor Filter）
  - [ ] 4.1 创建 MultiFactorFilter 类
    - 实现 apply_filters 方法（技术面筛选）
    - 实现 apply_fundamental_filters 方法（基本面筛选）
    - 支持行业、市盈率、涨跌幅、市值、流动性等多维度筛选
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_

  - [ ] 4.2 实现基本面过滤规则
    - 排除连续两年亏损的股票
    - 排除资产负债率 > 80% 的股票
    - 排除商誉占净资产比例 > 50% 的股票
    - 排除 ST、*ST 股票
    - _Requirements: 7.1, 7.2, 7.3_

  - [ ]* 4.3 编写多因子筛选器的属性测试
    - **Property 6: 多因子筛选交集性**
    - **Validates: Requirements 3.6**

  - [ ]* 4.4 编写多因子筛选器的属性测试
    - **Property 7: 基本面数据缺失容错**
    - **Validates: Requirements 3.7**

  - [ ]* 4.5 编写多因子筛选器的属性测试
    - **Property 13: 基本面过滤规则**
    - **Validates: Requirements 7.1, 7.2, 7.3**

  - [ ]* 4.6 编写多因子筛选器的单元测试
    - 测试单一条件筛选
    - 测试多条件交集
    - 测试基本面数据缺失处理
    - _Requirements: 3.6, 3.7, 7.4_

- [ ] 5. Checkpoint - 核心组件验证
  - 确保评分引擎、信号解释器、多因子筛选器的所有测试通过
  - 验证各组件接口符合设计文档
  - 如有问题，请向用户反馈

- [ ] 6. 实现历史追踪器（Signal History Tracker）
  - [ ] 6.1 创建 SignalHistoryTracker 类
    - 实现 save_signal 方法
    - 实现 calculate_performance 方法（计算 3/5/10 天表现）
    - 实现 get_strategy_stats 方法（策略统计）
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

  - [ ] 6.2 实现定时任务更新历史表现
    - 创建后台任务定期计算信号表现
    - 更新 strategy_signals 表的 return_3d, return_5d, return_10d 字段
    - _Requirements: 4.6_

  - [ ]* 6.3 编写历史追踪器的属性测试
    - **Property 8: 历史信号持久化**
    - **Validates: Requirements 4.1, 4.2**

  - [ ]* 6.4 编写历史追踪器的属性测试
    - **Property 9: 表现计算准确性**
    - **Validates: Requirements 4.3, 4.4**

  - [ ]* 6.5 编写历史追踪器的单元测试
    - 测试信号保存逻辑
    - 测试表现计算逻辑
    - 测试统计数据生成
    - _Requirements: 4.1, 4.3, 4.5_

- [ ] 7. 增强策略扫描器（Strategy Scanner）
  - [ ] 7.1 扩展 BaseStrategy 类
    - 添加 scan_with_scoring 方法
    - 集成评分引擎和信号解释器
    - 支持基本面过滤开关
    - _Requirements: 1.1, 1.2, 2.1, 2.4_

  - [ ] 7.2 更新 MACrossoverStrategy 类
    - 修改 check_signal 方法返回增强的信号字典
    - 集成评分引擎计算置信度分数
    - 集成信号解释器生成选股理由
    - 添加基本面数据查询和过滤
    - _Requirements: 1.1, 1.2, 1.5, 2.1, 2.4, 2.5_

  - [ ]* 7.3 编写策略扫描器的属性测试
    - **Property 3: 低分信号过滤**
    - **Validates: Requirements 1.4**

  - [ ]* 7.4 编写策略扫描器的属性测试
    - **Property 4: 信号排序正确性**
    - **Validates: Requirements 1.3**

  - [ ]* 7.5 编写策略扫描器的属性测试
    - **Property 15: 性能指标快照完整性**
    - **Validates: Requirements 10.2**

  - [ ]* 7.6 编写策略扫描器的单元测试
    - 测试信号生成逻辑
    - 测试评分和理由集成
    - 测试基本面过滤集成
    - _Requirements: 1.1, 2.1, 7.1_

- [ ] 8. 实现异步扫描器（Async Scanner）
  - [ ] 8.1 创建 AsyncScanner 类
    - 实现 trigger_scan 方法（触发异步任务）
    - 实现 get_scan_status 方法（查询任务状态）
    - 使用 threading 或 multiprocessing 实现后台扫描
    - 将扫描结果存储到 scan_results 表
    - _Requirements: 5.1, 5.2, 5.3_

  - [ ] 8.2 实现定时调度器
    - 创建每日收盘后自动触发扫描的调度器
    - 支持多策略并行扫描
    - 实现任务队列管理
    - _Requirements: 5.5_

  - [ ]* 8.3 编写异步扫描器的属性测试
    - **Property 10: 缓存读取优先**
    - **Validates: Requirements 5.3**

  - [ ]* 8.4 编写异步扫描器的属性测试
    - **Property 11: 扫描任务幂等性**
    - **Validates: Requirements 5.1, 5.2**

  - [ ]* 8.5 编写异步扫描器的单元测试
    - 测试任务创建和状态管理
    - 测试扫描结果缓存
    - 测试错误处理和重试
    - _Requirements: 5.1, 5.2, 5.4_

- [ ] 9. Checkpoint - 后台任务验证
  - 确保异步扫描器和历史追踪器的所有测试通过
  - 手动触发扫描任务，验证结果正确存储
  - 验证定时任务正常运行
  - 如有问题，请向用户反馈

- [ ] 10. 实现增强的 API 接口
  - [ ] 10.1 创建 /api/signals 接口
    - 支持按策略类型筛选
    - 支持按置信度分数范围筛选
    - 支持按日期范围筛选
    - 支持多种排序方式（评分、涨跌幅、市值）
    - 从 scan_results 表读取缓存数据
    - 应用多因子筛选器
    - _Requirements: 6.1, 6.2, 6.3, 6.4_

  - [ ] 10.2 创建 /api/signals/:id/history 接口
    - 返回指定信号的历史表现
    - 包含 3/5/10 天的收益率和命中情况
    - _Requirements: 6.5_

  - [ ] 10.3 创建 /api/signals/stats 接口
    - 返回策略整体统计数据
    - 包含命中率、平均收益率、最佳/最差信号
    - _Requirements: 6.6_

  - [ ] 10.4 创建 /api/scan/trigger 接口
    - 支持手动触发扫描任务
    - 返回任务 ID
    - _Requirements: 5.6_

  - [ ] 10.5 创建 /api/scan/status/:task_id 接口
    - 查询扫描任务状态和进度
    - _Requirements: 5.6_

  - [ ] 10.6 在所有 API 响应中添加免责声明
    - 在响应字典中添加 disclaimer 字段
    - 内容包含"本工具仅供科研与数据参考，不构成任何投资建议"
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

  - [ ]* 10.7 编写 API 接口的属性测试
    - **Property 12: 免责声明存在性**
    - **Validates: Requirements 8.1, 8.2, 8.3, 8.4**

  - [ ]* 10.8 编写 API 接口的单元测试
    - 测试参数验证
    - 测试筛选和排序逻辑
    - 测试错误处理
    - 测试免责声明包含
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.7, 8.1_

- [ ] 11. 实现数据库写入重试机制
  - [ ] 11.1 创建数据库操作装饰器
    - 实现自动重试逻辑（最多 3 次）
    - 记录重试日志
    - 应用到所有数据库写入操作
    - _Requirements: 10.4_

  - [ ]* 11.2 编写重试机制的属性测试
    - **Property 14: 数据库写入重试**
    - **Validates: Requirements 10.4**

  - [ ]* 11.3 编写重试机制的单元测试
    - 测试重试次数
    - 测试重试间隔
    - 测试最终失败处理
    - _Requirements: 10.4_

- [ ] 12. 性能优化
  - [ ] 12.1 优化数据库查询
    - 使用批量查询替代循环查询
    - 添加必要的索引
    - 使用 explain 分析慢查询
    - _Requirements: 9.2_

  - [ ] 12.2 优化技术指标计算
    - 使用 pandas 向量化操作
    - 避免 Python 循环
    - 缓存中间计算结果
    - _Requirements: 9.3_

  - [ ] 12.3 实现性能监控
    - 记录 API 响应时间
    - 记录扫描耗时
    - 当响应时间超过 2 秒时记录警告
    - _Requirements: 9.4_

  - [ ]* 12.4 编写性能测试
    - 测试扫描 1000 只股票在 5 分钟内完成
    - 测试 API 响应时间在 2 秒内
    - _Requirements: 9.1, 9.4_

- [ ] 13. Checkpoint - API 和性能验证
  - 确保所有 API 接口测试通过
  - 使用 Postman 或 curl 手动测试所有接口
  - 验证性能指标符合要求
  - 如有问题，请向用户反馈

- [ ] 14. 前端集成（可选）
  - [ ] 14.1 更新前端 API 服务
    - 添加 signals 相关的 API 调用函数
    - 添加 scan 相关的 API 调用函数
    - _Requirements: 6.1, 6.5, 6.6_

  - [ ] 14.2 创建选股信号列表页面
    - 展示信号列表（代码、名称、日期、价格、评分、理由）
    - 支持多因子筛选（行业、市盈率、涨跌幅等）
    - 支持排序（评分、涨跌幅、市值）
    - 显示免责声明
    - _Requirements: 1.3, 1.5, 2.4, 3.1, 3.2, 3.3, 3.4, 3.5, 6.1, 6.4, 8.5_

  - [ ] 14.3 创建信号详情页面
    - 展示信号的完整信息
    - 展示历史表现（3/5/10 天收益率）
    - 展示技术指标快照
    - 展示基本面指标快照
    - _Requirements: 2.5, 4.3, 4.4, 6.5_

  - [ ] 14.4 创建策略统计页面
    - 展示策略整体统计数据
    - 展示命中率和平均收益率
    - 展示最佳/最差信号
    - _Requirements: 4.5, 6.6_

  - [ ]* 14.5 编写前端组件的单元测试
    - 测试信号列表渲染
    - 测试筛选和排序功能
    - 测试免责声明显示
    - _Requirements: 8.5_

- [ ] 15. 文档和示例
  - [ ] 15.1 编写 API 文档
    - 记录所有接口的请求/响应格式
    - 提供 curl 示例
    - 说明错误代码和处理方式
    - _Requirements: 6.7_

  - [ ] 15.2 编写使用指南
    - 说明如何触发扫描
    - 说明如何查询信号
    - 说明如何解读评分和理由
    - 说明如何查看历史表现
    - _Requirements: 1.1, 2.1, 4.3_

  - [ ] 15.3 创建示例脚本
    - 提供完整的扫描示例
    - 提供 API 调用示例
    - 提供数据分析示例
    - _Requirements: 1.1, 2.1, 4.3, 6.1_

- [ ] 16. 最终集成测试
  - 端到端测试：触发扫描 → 查询信号 → 查看历史表现
  - 验证所有正确性属性
  - 验证性能指标
  - 验证免责声明在所有界面显示
  - 确保所有测试通过，向用户确认系统可以上线

## Notes

- 任务标记 `*` 的为可选测试任务，可以跳过以加快 MVP 开发
- 每个任务都引用了具体的需求编号，便于追溯
- Checkpoint 任务用于阶段性验证，确保质量
- 属性测试使用 Hypothesis 框架，最少 100 次迭代
- 单元测试使用 pytest 框架
- 前端集成为可选任务，可以先完成后端再考虑前端

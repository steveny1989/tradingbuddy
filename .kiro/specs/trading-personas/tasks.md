# Implementation Plan: 股票综合诊断系统

## Overview

实现一个统一的股票综合诊断系统，整合现有的技术面、行业面、资金面分析模块，新增基本面和大盘对比分析，生成综合诊断报告。

## Tasks

- [x] 1. 创建项目结构和数据模型
  - 创建 `src/business/diagnosis/` 目录
  - 创建 `__init__.py` 模块导出
  - 实现 `models.py` 数据模型 (DimensionAnalysis, DiagnosisReport)
  - 创建测试目录 `tests/diagnosis/`
  - _Requirements: 6.1_

- [x] 2. 实现基本面分析器 (Fundamental Analyzer)
  - [x] 2.1 创建 `fundamental_analyzer.py` 基础结构
    - 实现 `__init__(db_path)` 方法
    - 实现数据库连接和查询方法
    - _Requirements: 2.1_

  - [x] 2.2 实现财务指标获取
    - 从 financial_indicators 表获取 PE, PB, ROE, ROA
    - 从 income_statement 表获取净利润、营业收入
    - 从 balance_sheet 表获取资产负债率、流动比率
    - 计算同比/环比增长率
    - _Requirements: 2.1, 2.2_

  - [x] 2.3 实现行业对比逻辑
    - 获取同行业股票的财务指标
    - 计算行业平均值
    - 计算个股在行业内的百分位排名
    - _Requirements: 2.2_

  - [x] 2.4 实现基本面评分算法
    - ROE评分 (>15%高分, <5%低分)
    - 盈利增长评分 (>10%高分, <0%低分)
    - PE合理性评分 (与行业平均对比)
    - 财务健康评分 (负债率、流动比率)
    - 综合计算 0-100 分数
    - _Requirements: 2.3, 2.5, 2.6, 2.7, 2.8_

  - [x] 2.5 生成人话描述
    - 根据评分生成状态 (green/yellow/red)
    - 生成易懂的中文描述
    - _Requirements: 2.5, 2.8_

  - [ ]* 2.6 编写基本面分析器单元测试
    - 测试财务指标获取
    - 测试行业对比计算
    - 测试评分算法
    - 测试缺失数据处理
    - _Requirements: 2.1-2.8_

- [x] 3. 实现大盘对比分析器 (Market Comparison Analyzer)
  - [x] 3.1 创建 `market_comparison.py` 基础结构
    - 实现 `__init__(db_path)` 方法
    - 实现数据库连接和查询方法
    - _Requirements: 5.1_

  - [x] 3.2 实现个股收益率计算
    - 从 daily_data 获取历史价格
    - 计算 N 日收益率 (默认30日)
    - _Requirements: 5.2_

  - [x] 3.3 实现大盘指数收益率计算
    - 获取上证指数 (000001.SH) 收益率
    - 获取深证成指 (399001.SZ) 收益率
    - _Requirements: 5.1, 5.2_

  - [x] 3.4 实现相对表现计算
    - 计算跑赢/跑输大盘幅度
    - 计算 Beta (相对大盘波动率)
    - 判断相对强弱 (strong/weak/neutral)
    - _Requirements: 5.3, 5.4_

  - [x] 3.5 实现评分算法
    - 跑赢大盘 >5% = 高分
    - 跑赢大盘 0-5% = 中等分
    - 跑输大盘 = 低分
    - Beta 适中加分
    - _Requirements: 5.6, 5.7, 5.8_

  - [x] 3.6 生成人话描述
    - 根据评分生成状态
    - 生成易懂的中文描述
    - _Requirements: 5.5, 5.8_

  - [ ]* 3.7 编写大盘对比分析器单元测试
    - 测试收益率计算
    - 测试相对表现计算
    - 测试评分算法
    - 测试缺失数据处理
    - _Requirements: 5.1-5.8_

- [x] 4. 实现技术面分析器适配层
  - [x] 4.1 创建 `technical_analyzer.py` 适配器
    - 封装 candlestick_patterns 模块
    - 封装 portfolio_health 模块
    - 统一返回格式
    - _Requirements: 1.1, 1.2, 7.1, 7.2_

  - [x] 4.2 实现技术面评分算法
    - 趋势评分 (上涨=高分, 下跌=低分)
    - RSI 评分 (30-70健康区间)
    - 成交量评分 (放量=加分)
    - K线形态评分 (看涨形态=加分)
    - 综合计算 0-100 分数
    - _Requirements: 1.3, 1.6, 1.7, 1.8_

  - [x] 4.3 生成人话描述
    - 根据评分生成状态
    - 整合K线形态描述
    - 生成易懂的中文总结
    - _Requirements: 1.5_

  - [ ]* 4.4 编写技术面分析器单元测试
    - 测试模块封装
    - 测试评分算法
    - 测试描述生成
    - _Requirements: 1.1-1.8_

- [ ] 5. Checkpoint - 确保所有分析器测试通过
  - 确保所有测试通过，如有问题询问用户

- [ ] 6. 实现诊断引擎 (Diagnosis Engine)
  - [ ] 6.1 创建 `diagnosis_engine.py` 核心协调器
    - 实现 `__init__(db_path, cache_ttl)` 方法
    - 初始化所有5个分析器
    - 设置缓存 (TTL=1小时)
    - _Requirements: 6.1, 8.3_

  - [ ] 6.2 实现单股诊断逻辑
    - 实现 `diagnose(code)` 方法
    - 检查缓存，命中则返回
    - 并行调用5个分析器 (ThreadPoolExecutor)
    - 处理分析器失败情况 (graceful degradation)
    - _Requirements: 6.1, 6.2, 7.6_

  - [ ] 6.3 实现综合评分计算
    - 计算加权平均分 (技术20% + 基本30% + 行业15% + 资金20% + 大盘15%)
    - 处理缺失维度的权重重新分配
    - 生成评级 (优秀/良好/一般/较差/很差)
    - 生成状态 (green/yellow/red)
    - _Requirements: 6.2, 6.3_

  - [ ] 6.4 实现优劣势和建议生成
    - 识别优势维度 (score >= 75)
    - 识别劣势维度 (score < 50)
    - 根据各维度状态生成投资建议
    - 生成综合总结
    - _Requirements: 6.4, 6.5_

  - [ ] 6.5 实现缓存管理
    - 缓存诊断结果 (key: code, TTL: 1小时)
    - 实现 `clear_cache(code)` 方法
    - 实现 LRU 淘汰策略
    - _Requirements: 8.3_

  - [ ] 6.6 实现批量诊断
    - 实现 `diagnose_batch(codes)` 方法
    - 并行处理多只股票
    - 复用缓存
    - _Requirements: 8.2_

  - [ ]* 6.7 编写诊断引擎单元测试
    - 测试单股诊断流程
    - 测试综合评分计算
    - 测试优劣势识别
    - 测试缓存功能
    - 测试批量诊断
    - 测试容错处理
    - _Requirements: 6.1-6.8, 8.1-8.5_

- [ ] 7. 实现 REST API 端点
  - [ ] 7.1 创建 `src/web/routes/diagnosis.py` Flask blueprint
    - 设置 Flask blueprint for /api/diagnosis
    - 初始化 DiagnosisEngine 实例
    - _Requirements: 9.1_

  - [ ] 7.2 实现 GET /api/diagnosis/{code} 端点
    - 解析股票代码
    - 调用 diagnosis_engine.diagnose(code)
    - 返回 JSON 格式诊断报告
    - 处理错误 (404, 500)
    - _Requirements: 9.1, 9.3, 9.4, 9.6_

  - [ ] 7.3 实现 POST /api/diagnosis/batch 端点
    - 解析股票代码列表
    - 验证输入 (最多50只股票)
    - 调用 diagnosis_engine.diagnose_batch(codes)
    - 返回 JSON 数组
    - _Requirements: 9.2, 9.3, 9.4_

  - [ ] 7.4 在主 Flask app 中注册 blueprint
    - 在 src/web/app.py 导入 diagnosis blueprint
    - 注册 app.register_blueprint()
    - _Requirements: 9.1_

  - [ ]* 7.5 编写 API 集成测试
    - 测试 GET /api/diagnosis/{code} 正常情况
    - 测试 GET /api/diagnosis/{code} 错误情况
    - 测试 POST /api/diagnosis/batch
    - 测试响应格式
    - 测试性能 (响应时间 < 300ms)
    - _Requirements: 9.1-9.6_

- [x] 8. Checkpoint - 确保所有 API 测试通过
  - 确保所有测试通过，如有问题询问用户

- [ ] 9. 创建示例和文档
  - [ ] 9.1 创建 `examples/diagnosis_example.py`
    - 示例: 单股诊断
    - 示例: 批量诊断
    - 示例: 处理缺失数据
    - 打印格式化的诊断报告
    - _Requirements: 6.1-6.8_

  - [x] 9.2 创建 `tools/test_diagnosis.py` 手动测试工具
    - 测试所有分析器
    - 测试诊断引擎
    - 测试 API 端点
    - 打印详细结果
    - _Requirements: 6.1-6.8_

- [ ] 10. 性能优化和验证
  - [ ] 10.1 验证数据库索引
    - 确认 daily_data(code, date) 索引
    - 确认 financial_indicators(code, report_date) 索引
    - 确认 industry_data(code) 索引
    - 确认 capital_flow(code, date) 索引
    - _Requirements: 8.4_

  - [ ] 10.2 性能基准测试
    - 测试单股诊断时间 (目标 < 200ms)
    - 测试批量50股时间 (目标 < 5秒)
    - 测试 API 响应时间 (目标 < 300ms)
    - 测试缓存命中率
    - _Requirements: 8.1, 8.2_

  - [ ]* 10.3 编写性能测试
    - 测试单股性能 < 200ms
    - 测试批量50股 < 5秒
    - 测试缓存效果
    - 测试并行处理加速
    - _Requirements: 8.1, 8.2, 8.5_

- [ ] 11. Final checkpoint - 确保所有测试通过
  - 确保所有测试通过，如有问题询问用户

## Notes

- 任务标记 `*` 的为可选任务，可跳过以加快 MVP 开发
- 每个任务都引用了具体的需求编号，便于追溯
- Checkpoint 确保增量验证
- 单元测试验证具体功能
- 集成测试验证端到端流程
- 性能测试确保满足速度要求

## 模块复用总结

**复用现有模块** (无需修改):
- `candlestick_patterns.py` - K线形态识别
- `portfolio_health.py` - 技术指标计算
- `sector_analysis.py` - 行业面分析
- `capital_analysis.py` - 资金面分析

**新建模块** (需要实现):
- `diagnosis_engine.py` - 核心协调器
- `fundamental_analyzer.py` - 基本面分析器
- `market_comparison.py` - 大盘对比分析器
- `technical_analyzer.py` - 技术面适配器 (封装现有模块)

**API 层**:
- `src/web/routes/diagnosis.py` - REST API 端点

## 测试总结

**单元测试**:
- 基本面分析器: 财务指标、行业对比、评分算法
- 大盘对比分析器: 收益率计算、相对表现、评分算法
- 技术面适配器: 模块封装、评分算法
- 诊断引擎: 综合评分、优劣势识别、缓存、容错

**集成测试**:
- API 端点: 正常/异常情况、响应格式
- 端到端流程: 从 API 到数据库的完整链路

**性能测试**:
- 单股诊断 < 200ms
- 批量50股 < 5秒
- API 响应 < 300ms
- 缓存命中率 > 70%

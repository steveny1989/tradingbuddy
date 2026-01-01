# Paper Trading API Tests

## Overview

This document describes the unit tests for the Paper Trading API endpoints (Task 6.4).

## Test Coverage

### Requirements Covered

- **Requirement 5.1**: 账户状态显示（总资产、可用资金、持仓市值、当日盈亏）
- **Requirement 5.2**: 持仓列表显示（股票代码、名称、数量、成本价、现价、盈亏）
- **Requirement 5.3**: 今日交易记录显示（时间、股票、操作、价格、数量）
- **Requirement 5.4**: 历史绩效曲线（账户价值随时间变化）
- **Requirement 5.7**: 启动/停止模拟盘控制
- **Requirement 5.8**: 重置账户功能
- **Requirement 11.8**: 模拟盘状态API接口

## Test Structure

### 1. TestPaperTradingStatusAPI (6 tests)
Tests for `/api/paper-trading/status` endpoint

- `test_get_status_success`: 基本状态查询功能
- `test_get_status_account_fields`: 验证账户字段完整性 (Req 5.1)
- `test_get_status_positions_fields`: 验证持仓字段完整性 (Req 5.2)
- `test_get_status_today_trades_fields`: 验证交易记录字段完整性 (Req 5.3)
- `test_get_status_when_not_running`: 未运行状态的处理
- `test_get_status_data_types`: 数据类型验证

### 2. TestPaperTradingControlAPI (10 tests)
Tests for control endpoints: `/api/paper-trading/start`, `/stop`, `/reset`

**Start Endpoint Tests:**
- `test_start_paper_trading_success`: 成功启动 (Req 5.7)
- `test_start_paper_trading_missing_params`: 缺少必需参数
- `test_start_paper_trading_invalid_capital`: 无效的初始资金
- `test_start_paper_trading_invalid_strategy`: 无效的策略ID
- `test_start_paper_trading_already_running`: 重复启动处理

**Stop Endpoint Tests:**
- `test_stop_paper_trading_success`: 成功停止 (Req 5.7)
- `test_stop_paper_trading_when_not_running`: 停止未运行的模拟盘

**Reset Endpoint Tests:**
- `test_reset_paper_trading_success`: 成功重置 (Req 5.8)
- `test_reset_paper_trading_confirmation`: 重置确认机制
- `test_reset_paper_trading_clears_data`: 验证数据清空

### 3. TestPaperTradingPerformanceAPI (8 tests)
Tests for `/api/paper-trading/performance` endpoint

- `test_get_performance_success`: 基本绩效查询功能
- `test_get_performance_equity_curve`: 资金曲线数据格式 (Req 5.4)
- `test_get_performance_metrics`: 绩效指标完整性
- `test_get_performance_with_date_range`: 日期范围筛选
- `test_get_performance_invalid_date`: 无效日期处理
- `test_get_performance_when_not_running`: 未运行状态处理
- `test_get_performance_data_consistency`: 数据一致性验证
- `test_get_performance_metrics_calculation`: 指标计算合理性

### 4. TestPaperTradingAPIIntegration (3 tests)
Integration tests for complete workflows

- `test_full_lifecycle`: 完整生命周期测试（启动→状态→绩效→停止→重置）
- `test_status_reflects_control_operations`: 状态反映控制操作
- `test_error_handling_consistency`: 错误处理一致性

## Test Status

**Current Status**: ❌ 26 failed, 1 passed

All tests are currently failing with 404 errors because the Paper Trading API endpoints have not been implemented yet (Tasks 6.1-6.3 are pending).

**Expected Status After Implementation**: ✅ All tests should pass

## Running the Tests

```bash
# Run all paper trading tests
python3 -m pytest src/web/tests/test_paper_trading_api.py -v

# Run specific test class
python3 -m pytest src/web/tests/test_paper_trading_api.py::TestPaperTradingStatusAPI -v

# Run specific test
python3 -m pytest src/web/tests/test_paper_trading_api.py::TestPaperTradingStatusAPI::test_get_status_success -v
```

## Dependencies

These tests depend on:
- Task 6.1: Implementation of `/api/paper-trading/status` endpoint
- Task 6.2: Implementation of `/api/paper-trading/start`, `/stop`, `/reset` endpoints
- Task 6.3: Implementation of `/api/paper-trading/performance` endpoint

## Test Data

The tests use pytest fixtures to create mock data:
- `mock_account_data`: Sample account information
- `mock_positions_data`: Sample position holdings
- `mock_trades_data`: Sample trade records
- `test_data_dir`: Temporary directory for test data

## Notes

1. **Test-Driven Development**: These tests were written before the API implementation, following TDD principles
2. **Comprehensive Coverage**: Tests cover success cases, error cases, edge cases, and integration scenarios
3. **Requirements Traceability**: Each test is mapped to specific requirements
4. **Minimal Mocking**: Tests are designed to work with real API responses, not mocks
5. **Error Handling**: Tests verify consistent error response format across all endpoints

## Next Steps

1. Complete Task 6.1: Implement Paper Trading Status API
2. Complete Task 6.2: Implement Paper Trading Control API
3. Complete Task 6.3: Implement Paper Trading Performance API
4. Re-run these tests to verify implementation
5. Fix any failing tests based on actual API behavior

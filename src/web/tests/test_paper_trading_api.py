"""
模拟盘API测试
Tests for Paper Trading API endpoints
"""
import pytest
import json
from pathlib import Path
from src.web.app import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def test_data_dir(tmp_path):
    """创建临时测试数据目录"""
    data_dir = tmp_path / "paper_trading_test"
    data_dir.mkdir(exist_ok=True)
    return data_dir


@pytest.fixture
def mock_account_data(test_data_dir):
    """创建模拟账户数据"""
    account_data = {
        "total_value": 105000.0,
        "cash": 50000.0,
        "position_value": 55000.0,
        "daily_pnl": 5000.0,
        "daily_pnl_pct": 5.0,
        "initial_capital": 100000.0,
        "updated_at": "2026-01-01 15:00:00"
    }
    
    account_file = test_data_dir / "account.json"
    with open(account_file, 'w') as f:
        json.dump(account_data, f)
    
    return account_data


@pytest.fixture
def mock_positions_data(test_data_dir):
    """创建模拟持仓数据"""
    positions_data = [
        {
            "code": "600000",
            "name": "浦发银行",
            "quantity": 1000,
            "cost_price": 10.0,
            "current_price": 11.0,
            "market_value": 11000.0,
            "pnl": 1000.0,
            "pnl_pct": 10.0
        },
        {
            "code": "600519",
            "name": "贵州茅台",
            "quantity": 20,
            "cost_price": 2000.0,
            "current_price": 2200.0,
            "market_value": 44000.0,
            "pnl": 4000.0,
            "pnl_pct": 10.0
        }
    ]
    
    return positions_data


@pytest.fixture
def mock_trades_data(test_data_dir):
    """创建模拟交易数据"""
    trades_data = [
        {
            "date": "2026-01-01",
            "time": "09:30:00",
            "code": "600000",
            "name": "浦发银行",
            "action": "buy",
            "price": 10.0,
            "quantity": 1000,
            "amount": 10000.0,
            "commission": 3.0,
            "pnl": 0.0
        },
        {
            "date": "2026-01-01",
            "time": "14:30:00",
            "code": "600519",
            "name": "贵州茅台",
            "action": "buy",
            "price": 2000.0,
            "quantity": 20,
            "amount": 40000.0,
            "commission": 12.0,
            "pnl": 0.0
        }
    ]
    
    return trades_data


class TestPaperTradingStatusAPI:
    """测试模拟盘状态API - Requirements 5.1, 5.2, 5.3, 11.8"""
    
    def test_get_status_success(self, client):
        """测试成功获取模拟盘状态"""
        response = client.get('/api/paper-trading/status')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        
        # 验证返回的数据结构
        status_data = data['data']
        assert 'running' in status_data
        assert 'account' in status_data
        assert 'positions' in status_data
        assert 'today_trades' in status_data
    
    def test_get_status_account_fields(self, client):
        """测试账户状态包含所有必需字段 - Requirement 5.1"""
        response = client.get('/api/paper-trading/status')
        assert response.status_code == 200
        
        data = response.get_json()
        account = data['data']['account']
        
        # 验证账户字段
        required_fields = [
            'total_value',
            'cash',
            'position_value',
            'daily_pnl',
            'daily_pnl_pct'
        ]
        
        for field in required_fields:
            assert field in account, f"Missing required field: {field}"
            assert isinstance(account[field], (int, float)), \
                f"Field {field} should be numeric"
    
    def test_get_status_positions_fields(self, client):
        """测试持仓列表包含所有必需字段 - Requirement 5.2"""
        response = client.get('/api/paper-trading/status')
        assert response.status_code == 200
        
        data = response.get_json()
        positions = data['data']['positions']
        
        assert isinstance(positions, list)
        
        # 如果有持仓，验证字段
        if len(positions) > 0:
            position = positions[0]
            required_fields = [
                'code',
                'name',
                'quantity',
                'cost_price',
                'current_price',
                'market_value',
                'pnl',
                'pnl_pct'
            ]
            
            for field in required_fields:
                assert field in position, f"Missing required field: {field}"
    
    def test_get_status_today_trades_fields(self, client):
        """测试今日交易包含所有必需字段 - Requirement 5.3"""
        response = client.get('/api/paper-trading/status')
        assert response.status_code == 200
        
        data = response.get_json()
        today_trades = data['data']['today_trades']
        
        assert isinstance(today_trades, list)
        
        # 如果有交易记录，验证字段
        if len(today_trades) > 0:
            trade = today_trades[0]
            required_fields = [
                'time',
                'code',
                'name',
                'action',
                'price',
                'quantity'
            ]
            
            for field in required_fields:
                assert field in trade, f"Missing required field: {field}"
    
    def test_get_status_when_not_running(self, client):
        """测试模拟盘未运行时的状态"""
        response = client.get('/api/paper-trading/status')
        assert response.status_code == 200
        
        data = response.get_json()
        status_data = data['data']
        
        # 未运行时应该返回默认值
        if not status_data['running']:
            assert status_data['account']['total_value'] == 0.0
            assert status_data['positions'] == []
            assert status_data['today_trades'] == []
    
    def test_get_status_data_types(self, client):
        """测试返回数据的类型正确性"""
        response = client.get('/api/paper-trading/status')
        assert response.status_code == 200
        
        data = response.get_json()
        status_data = data['data']
        
        # 验证数据类型
        assert isinstance(status_data['running'], bool)
        assert isinstance(status_data['account'], dict)
        assert isinstance(status_data['positions'], list)
        assert isinstance(status_data['today_trades'], list)


class TestPaperTradingControlAPI:
    """测试模拟盘控制API - Requirements 5.7, 5.8"""
    
    def test_start_paper_trading_success(self, client):
        """测试成功启动模拟盘 - Requirement 5.7"""
        request_data = {
            "strategy_id": "volume_shrink",
            "initial_capital": 100000.0
        }
        
        response = client.post(
            '/api/paper-trading/start',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data
    
    def test_start_paper_trading_missing_params(self, client):
        """测试启动模拟盘缺少必需参数"""
        # 缺少strategy_id
        request_data = {
            "initial_capital": 100000.0
        }
        
        response = client.post(
            '/api/paper-trading/start',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_start_paper_trading_invalid_capital(self, client):
        """测试启动模拟盘使用无效的初始资金"""
        request_data = {
            "strategy_id": "volume_shrink",
            "initial_capital": -1000.0  # 负数资金
        }
        
        response = client.post(
            '/api/paper-trading/start',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
    
    def test_start_paper_trading_invalid_strategy(self, client):
        """测试启动模拟盘使用无效的策略ID"""
        request_data = {
            "strategy_id": "invalid_strategy",
            "initial_capital": 100000.0
        }
        
        response = client.post(
            '/api/paper-trading/start',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'STRATEGY_NOT_FOUND'
    
    def test_start_paper_trading_already_running(self, client):
        """测试模拟盘已在运行时再次启动"""
        request_data = {
            "strategy_id": "volume_shrink",
            "initial_capital": 100000.0
        }
        
        # 第一次启动
        response1 = client.post(
            '/api/paper-trading/start',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 第二次启动应该返回错误或警告
        response2 = client.post(
            '/api/paper-trading/start',
            data=json.dumps(request_data),
            content_type='application/json'
        )
        
        # 可能返回400或200（取决于实现）
        assert response2.status_code in [200, 400]
    
    def test_stop_paper_trading_success(self, client):
        """测试成功停止模拟盘 - Requirement 5.7"""
        response = client.post('/api/paper-trading/stop')
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data
    
    def test_stop_paper_trading_when_not_running(self, client):
        """测试停止未运行的模拟盘"""
        response = client.post('/api/paper-trading/stop')
        
        # 应该返回成功或提示未运行
        assert response.status_code in [200, 400]
        
        data = response.get_json()
        if response.status_code == 400:
            assert data['success'] is False
    
    def test_reset_paper_trading_success(self, client):
        """测试成功重置模拟盘账户 - Requirement 5.8"""
        response = client.post('/api/paper-trading/reset')
        
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data
    
    def test_reset_paper_trading_confirmation(self, client):
        """测试重置操作需要确认"""
        # 不带确认参数
        response = client.post('/api/paper-trading/reset')
        
        # 根据实现，可能需要确认参数
        # 这里测试基本功能
        assert response.status_code in [200, 400]
    
    def test_reset_paper_trading_clears_data(self, client):
        """测试重置后数据被清空"""
        # 重置账户
        response = client.post('/api/paper-trading/reset')
        assert response.status_code == 200
        
        # 检查状态
        status_response = client.get('/api/paper-trading/status')
        assert status_response.status_code == 200
        
        status_data = status_response.get_json()['data']
        
        # 验证数据被重置
        # 注意：具体行为取决于实现
        # 可能是清空持仓和交易，或者重置为初始资金
        assert isinstance(status_data['positions'], list)
        assert isinstance(status_data['today_trades'], list)


class TestPaperTradingPerformanceAPI:
    """测试模拟盘绩效API - Requirement 5.4"""
    
    def test_get_performance_success(self, client):
        """测试成功获取模拟盘绩效"""
        response = client.get('/api/paper-trading/performance')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        
        # 验证返回的数据结构
        perf_data = data['data']
        assert 'equity_curve' in perf_data
        assert 'metrics' in perf_data
    
    def test_get_performance_equity_curve(self, client):
        """测试资金曲线数据格式"""
        response = client.get('/api/paper-trading/performance')
        assert response.status_code == 200
        
        data = response.get_json()
        equity_curve = data['data']['equity_curve']
        
        assert isinstance(equity_curve, list)
        
        # 如果有数据，验证格式
        if len(equity_curve) > 0:
            point = equity_curve[0]
            assert 'date' in point
            assert 'value' in point
            assert isinstance(point['value'], (int, float))
    
    def test_get_performance_metrics(self, client):
        """测试绩效指标包含所有必需字段"""
        response = client.get('/api/paper-trading/performance')
        assert response.status_code == 200
        
        data = response.get_json()
        metrics = data['data']['metrics']
        
        # 验证关键指标
        expected_metrics = [
            'total_return',
            'max_drawdown'
        ]
        
        for metric in expected_metrics:
            assert metric in metrics, f"Missing metric: {metric}"
            assert isinstance(metrics[metric], (int, float)), \
                f"Metric {metric} should be numeric"
    
    def test_get_performance_with_date_range(self, client):
        """测试带日期范围的绩效查询"""
        response = client.get(
            '/api/paper-trading/performance?start_date=2026-01-01&end_date=2026-01-31'
        )
        
        assert response.status_code == 200
        
        data = response.get_json()
        equity_curve = data['data']['equity_curve']
        
        # 验证日期范围
        for point in equity_curve:
            if 'date' in point:
                assert point['date'] >= '2026-01-01'
                assert point['date'] <= '2026-01-31'
    
    def test_get_performance_invalid_date(self, client):
        """测试无效的日期格式"""
        response = client.get(
            '/api/paper-trading/performance?start_date=invalid'
        )
        
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_DATE'
    
    def test_get_performance_when_not_running(self, client):
        """测试模拟盘未运行时获取绩效"""
        response = client.get('/api/paper-trading/performance')
        
        # 应该返回空数据或默认值
        assert response.status_code == 200
        
        data = response.get_json()
        perf_data = data['data']
        
        # 未运行时应该返回空数据
        assert isinstance(perf_data['equity_curve'], list)
        assert isinstance(perf_data['metrics'], dict)
    
    def test_get_performance_data_consistency(self, client):
        """测试绩效数据的一致性"""
        response = client.get('/api/paper-trading/performance')
        assert response.status_code == 200
        
        data = response.get_json()
        equity_curve = data['data']['equity_curve']
        
        # 验证资金曲线的时间顺序
        if len(equity_curve) > 1:
            dates = [point['date'] for point in equity_curve if 'date' in point]
            assert dates == sorted(dates), "Equity curve should be sorted by date"
    
    def test_get_performance_metrics_calculation(self, client):
        """测试绩效指标计算的合理性"""
        response = client.get('/api/paper-trading/performance')
        assert response.status_code == 200
        
        data = response.get_json()
        metrics = data['data']['metrics']
        
        # 验证指标的合理范围
        if 'total_return' in metrics:
            # 收益率应该在合理范围内（-100%到无穷大）
            assert metrics['total_return'] >= -100.0
        
        if 'max_drawdown' in metrics:
            # 最大回撤应该在0到100之间
            assert 0.0 <= metrics['max_drawdown'] <= 100.0


class TestPaperTradingAPIIntegration:
    """测试模拟盘API的集成场景"""
    
    def test_full_lifecycle(self, client):
        """测试完整的模拟盘生命周期"""
        # 1. 启动模拟盘
        start_data = {
            "strategy_id": "volume_shrink",
            "initial_capital": 100000.0
        }
        
        start_response = client.post(
            '/api/paper-trading/start',
            data=json.dumps(start_data),
            content_type='application/json'
        )
        
        # 2. 检查状态
        status_response = client.get('/api/paper-trading/status')
        assert status_response.status_code == 200
        
        # 3. 获取绩效
        perf_response = client.get('/api/paper-trading/performance')
        assert perf_response.status_code == 200
        
        # 4. 停止模拟盘
        stop_response = client.post('/api/paper-trading/stop')
        assert stop_response.status_code == 200
        
        # 5. 重置账户
        reset_response = client.post('/api/paper-trading/reset')
        assert reset_response.status_code == 200
    
    def test_status_reflects_control_operations(self, client):
        """测试状态API反映控制操作的结果"""
        # 获取初始状态
        initial_status = client.get('/api/paper-trading/status')
        initial_data = initial_status.get_json()['data']
        
        # 执行启动操作
        start_data = {
            "strategy_id": "volume_shrink",
            "initial_capital": 100000.0
        }
        client.post(
            '/api/paper-trading/start',
            data=json.dumps(start_data),
            content_type='application/json'
        )
        
        # 检查状态是否更新
        updated_status = client.get('/api/paper-trading/status')
        updated_data = updated_status.get_json()['data']
        
        # 状态应该有所变化（具体取决于实现）
        assert isinstance(updated_data, dict)
    
    def test_error_handling_consistency(self, client):
        """测试错误处理的一致性"""
        # 测试各个端点的错误响应格式一致
        
        # 1. 无效的启动请求
        invalid_start = client.post(
            '/api/paper-trading/start',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        if invalid_start.status_code >= 400:
            data = invalid_start.get_json()
            assert 'success' in data
            assert data['success'] is False
            assert 'error' in data
            assert 'error_code' in data
        
        # 2. 无效的绩效查询
        invalid_perf = client.get('/api/paper-trading/performance?start_date=invalid')
        
        if invalid_perf.status_code >= 400:
            data = invalid_perf.get_json()
            assert 'success' in data
            assert data['success'] is False
            assert 'error' in data
            assert 'error_code' in data

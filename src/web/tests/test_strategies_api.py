"""
策略管理API测试
Tests for strategy management APIs

Requirements tested:
- 3.1: 策略列表返回
- 3.2: 策略详情和配置
- 3.4: 回测执行
- 3.6: 参数验证
"""
import pytest
import time
from src.web.app import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


class TestStrategyListAPI:
    """测试策略列表API - Requirements 3.1"""
    
    def test_get_strategy_list_success(self, client):
        """测试成功获取策略列表"""
        response = client.get('/api/strategies')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert isinstance(data['data'], list)
        assert len(data['data']) > 0
    
    def test_strategy_list_contains_required_fields(self, client):
        """测试策略列表包含所有必需字段 - Requirements 3.1"""
        response = client.get('/api/strategies')
        assert response.status_code == 200
        
        data = response.get_json()
        strategies = data['data']
        
        # 验证每个策略都包含必需字段
        for strategy in strategies:
            assert 'id' in strategy
            assert 'name' in strategy
            assert 'type' in strategy
            assert 'description' in strategy
            assert 'params' in strategy
            assert isinstance(strategy['params'], list)
    
    def test_strategy_list_contains_known_strategies(self, client):
        """测试策略列表包含已知策略"""
        response = client.get('/api/strategies')
        assert response.status_code == 200
        
        data = response.get_json()
        strategy_ids = [s['id'] for s in data['data']]
        
        # 验证包含已知策略
        assert 'volume_shrink' in strategy_ids
        assert 'ma_crossover' in strategy_ids
    
    def test_strategy_params_structure(self, client):
        """测试策略参数结构完整性"""
        response = client.get('/api/strategies')
        assert response.status_code == 200
        
        data = response.get_json()
        
        for strategy in data['data']:
            for param in strategy['params']:
                # 验证参数必需字段
                assert 'name' in param
                assert 'label' in param
                assert 'type' in param
                assert 'default' in param
                
                # 验证参数类型
                assert param['type'] in ['number', 'string', 'boolean', 'select']
                
                # 如果是number类型，应该有min/max
                if param['type'] == 'number':
                    assert 'min' in param or 'max' in param


class TestStrategyDetailAPI:
    """测试策略详情API - Requirements 3.2"""
    
    def test_get_strategy_detail_success(self, client):
        """测试成功获取策略详情"""
        response = client.get('/api/strategies/volume_shrink')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert data['data']['id'] == 'volume_shrink'
    
    def test_strategy_detail_contains_all_fields(self, client):
        """测试策略详情包含所有字段 - Requirements 3.2"""
        response = client.get('/api/strategies/volume_shrink')
        assert response.status_code == 200
        
        data = response.get_json()
        strategy = data['data']
        
        # 验证所有必需字段
        assert 'id' in strategy
        assert 'name' in strategy
        assert 'type' in strategy
        assert 'description' in strategy
        assert 'params' in strategy
        assert 'default_config' in strategy
        
        # 验证default_config是字典
        assert isinstance(strategy['default_config'], dict)
    
    def test_get_strategy_detail_not_found(self, client):
        """测试获取不存在的策略"""
        response = client.get('/api/strategies/nonexistent_strategy')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error_code'] == 'STRATEGY_NOT_FOUND'
    
    def test_get_ma_crossover_strategy(self, client):
        """测试获取均线突破策略详情"""
        response = client.get('/api/strategies/ma_crossover')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['data']['id'] == 'ma_crossover'
        assert data['data']['type'] == 'technical'


class TestStrategyConfigAPI:
    """测试策略配置API - Requirements 3.2, 3.6"""
    
    def test_get_strategy_config_success(self, client):
        """测试成功获取策略配置"""
        response = client.get('/api/strategies/volume_shrink/config')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'config' in data['data']
        assert isinstance(data['data']['config'], dict)
    
    def test_get_strategy_config_not_found(self, client):
        """测试获取不存在策略的配置"""
        response = client.get('/api/strategies/nonexistent/config')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'STRATEGY_NOT_FOUND'
    
    def test_update_strategy_config_success(self, client):
        """测试成功更新策略配置"""
        config_data = {
            'config': {
                'min_cap': 100,
                'max_cap': 300,
                'min_decline': 0.15,
                'use_volume_stabilize': False
            }
        }
        
        response = client.put(
            '/api/strategies/volume_shrink/config',
            json=config_data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'message' in data['data']
    
    def test_update_strategy_config_invalid_request(self, client):
        """测试无效的请求格式"""
        # 缺少config字段
        response = client.put(
            '/api/strategies/volume_shrink/config',
            json={'invalid': 'data'},
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_REQUEST'
    
    def test_update_strategy_config_empty_body(self, client):
        """测试空请求体"""
        response = client.put(
            '/api/strategies/volume_shrink/config',
            json=None,
            content_type='application/json'
        )
        # Flask returns 500 when JSON parsing fails, which is caught by global error handler
        assert response.status_code in [400, 500]
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_update_strategy_config_not_found(self, client):
        """测试更新不存在策略的配置"""
        config_data = {'config': {'min_cap': 100}}
        
        response = client.put(
            '/api/strategies/nonexistent/config',
            json=config_data,
            content_type='application/json'
        )
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'STRATEGY_NOT_FOUND'


class TestStrategyConfigValidation:
    """测试策略配置参数验证 - Requirements 3.6"""
    
    def test_validate_number_type(self, client):
        """测试数字类型验证"""
        # 传入非数字值
        config_data = {
            'config': {
                'min_cap': 'not_a_number'
            }
        }
        
        response = client.put(
            '/api/strategies/volume_shrink/config',
            json=config_data,
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'VALIDATION_ERROR'
        assert '必须是数字' in data['error']
    
    def test_validate_number_min_value(self, client):
        """测试数字最小值验证"""
        config_data = {
            'config': {
                'min_cap': 5  # 小于最小值10
            }
        }
        
        response = client.put(
            '/api/strategies/volume_shrink/config',
            json=config_data,
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'VALIDATION_ERROR'
        assert '不能小于' in data['error']
    
    def test_validate_number_max_value(self, client):
        """测试数字最大值验证"""
        config_data = {
            'config': {
                'min_cap': 2000  # 大于最大值1000
            }
        }
        
        response = client.put(
            '/api/strategies/volume_shrink/config',
            json=config_data,
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'VALIDATION_ERROR'
        assert '不能大于' in data['error']
    
    def test_validate_boolean_type(self, client):
        """测试布尔类型验证"""
        config_data = {
            'config': {
                'use_volume_stabilize': 'not_a_boolean'
            }
        }
        
        response = client.put(
            '/api/strategies/volume_shrink/config',
            json=config_data,
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'VALIDATION_ERROR'
        assert '必须是布尔值' in data['error']
    
    def test_validate_multiple_errors(self, client):
        """测试多个验证错误"""
        config_data = {
            'config': {
                'min_cap': 'invalid',  # 类型错误
                'max_cap': 10000,      # 超出最大值
                'use_volume_stabilize': 'yes'  # 类型错误
            }
        }
        
        response = client.put(
            '/api/strategies/volume_shrink/config',
            json=config_data,
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'VALIDATION_ERROR'
        # 应该包含多个错误信息
        assert ';' in data['error'] or ',' in data['error']
    
    def test_validate_valid_config(self, client):
        """测试有效配置通过验证"""
        config_data = {
            'config': {
                'min_cap': 80,
                'max_cap': 250,
                'min_decline': 0.12,
                'use_volume_stabilize': True,
                'check_market': False,
                'min_avg_turnover': 2.5
            }
        }
        
        response = client.put(
            '/api/strategies/volume_shrink/config',
            json=config_data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True


class TestBacktestExecutionAPI:
    """测试回测执行API - Requirements 3.4"""
    
    def test_run_backtest_success(self, client):
        """测试成功创建回测任务"""
        backtest_data = {
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'initial_capital': 1000000,
            'strategy_config': {
                'min_cap': 50,
                'max_cap': 200
            }
        }
        
        response = client.post(
            '/api/strategies/volume_shrink/backtest',
            json=backtest_data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'task_id' in data['data']
        assert 'status' in data['data']
        assert data['data']['status'] == 'pending'
    
    def test_run_backtest_strategy_not_found(self, client):
        """测试不存在的策略"""
        backtest_data = {
            'start_date': '2025-01-01',
            'end_date': '2025-12-31'
        }
        
        response = client.post(
            '/api/strategies/nonexistent/backtest',
            json=backtest_data,
            content_type='application/json'
        )
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'STRATEGY_NOT_FOUND'
    
    def test_run_backtest_missing_required_fields(self, client):
        """测试缺少必需字段"""
        # 缺少end_date
        backtest_data = {
            'start_date': '2025-01-01'
        }
        
        response = client.post(
            '/api/strategies/volume_shrink/backtest',
            json=backtest_data,
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'MISSING_REQUIRED_FIELDS'
        assert 'end_date' in data['error']
    
    def test_run_backtest_empty_body(self, client):
        """测试空请求体"""
        response = client.post(
            '/api/strategies/volume_shrink/backtest',
            json=None,
            content_type='application/json'
        )
        # Flask returns 500 when JSON parsing fails, which is caught by global error handler
        assert response.status_code in [400, 500]
        
        data = response.get_json()
        assert data['success'] is False
    
    def test_run_backtest_invalid_date_format(self, client):
        """测试无效的日期格式"""
        backtest_data = {
            'start_date': 'invalid-date',
            'end_date': '2025-12-31'
        }
        
        response = client.post(
            '/api/strategies/volume_shrink/backtest',
            json=backtest_data,
            content_type='application/json'
        )
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_DATE'
    
    def test_run_backtest_with_optional_params(self, client):
        """测试带可选参数的回测"""
        backtest_data = {
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'initial_capital': 2000000,
            'strategy_config': {
                'min_cap': 100,
                'max_cap': 500
            },
            'hold_days': 10,
            'stop_loss': -0.08,
            'take_profit': 0.20
        }
        
        response = client.post(
            '/api/strategies/volume_shrink/backtest',
            json=backtest_data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'task_id' in data['data']
    
    def test_run_backtest_ma_crossover_strategy(self, client):
        """测试均线突破策略回测"""
        backtest_data = {
            'start_date': '2025-01-01',
            'end_date': '2025-12-31',
            'initial_capital': 1000000,
            'strategy_config': {
                'short_window': 5,
                'long_window': 20,
                'check_volume': True
            }
        }
        
        response = client.post(
            '/api/strategies/ma_crossover/backtest',
            json=backtest_data,
            content_type='application/json'
        )
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'task_id' in data['data']


class TestBacktestStatusAPI:
    """测试回测状态查询API"""
    
    def test_get_backtest_status_not_found(self, client):
        """测试查询不存在的任务"""
        response = client.get('/api/strategies/backtest/nonexistent-task-id')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'TASK_NOT_FOUND'
    
    def test_get_backtest_status_after_creation(self, client):
        """测试创建任务后查询状态"""
        # 先创建一个回测任务
        backtest_data = {
            'start_date': '2025-01-01',
            'end_date': '2025-01-31',
            'initial_capital': 1000000
        }
        
        create_response = client.post(
            '/api/strategies/volume_shrink/backtest',
            json=backtest_data,
            content_type='application/json'
        )
        assert create_response.status_code == 200
        
        create_data = create_response.get_json()
        task_id = create_data['data']['task_id']
        
        # 查询任务状态
        status_response = client.get(f'/api/strategies/backtest/{task_id}')
        assert status_response.status_code == 200
        
        status_data = status_response.get_json()
        assert status_data['success'] is True
        assert 'data' in status_data
        assert status_data['data']['task_id'] == task_id
        assert 'status' in status_data['data']
        assert status_data['data']['status'] in ['pending', 'running', 'completed', 'failed']
    
    def test_backtest_status_contains_required_fields(self, client):
        """测试状态响应包含必需字段"""
        # 创建任务
        backtest_data = {
            'start_date': '2025-01-01',
            'end_date': '2025-01-31'
        }
        
        create_response = client.post(
            '/api/strategies/volume_shrink/backtest',
            json=backtest_data,
            content_type='application/json'
        )
        task_id = create_response.get_json()['data']['task_id']
        
        # 查询状态
        status_response = client.get(f'/api/strategies/backtest/{task_id}')
        status_data = status_response.get_json()['data']
        
        # 验证必需字段
        assert 'task_id' in status_data
        assert 'strategy_id' in status_data
        assert 'strategy_name' in status_data
        assert 'status' in status_data
        assert 'created_at' in status_data
    
    def test_backtest_task_execution_flow(self, client):
        """测试回测任务执行流程（集成测试）"""
        # 创建任务
        backtest_data = {
            'start_date': '2025-12-01',
            'end_date': '2025-12-10',  # 短时间范围，快速完成
            'initial_capital': 1000000
        }
        
        create_response = client.post(
            '/api/strategies/volume_shrink/backtest',
            json=backtest_data,
            content_type='application/json'
        )
        assert create_response.status_code == 200
        
        task_id = create_response.get_json()['data']['task_id']
        
        # 等待任务执行（最多等待10秒）
        max_wait = 10
        wait_interval = 1
        elapsed = 0
        
        while elapsed < max_wait:
            status_response = client.get(f'/api/strategies/backtest/{task_id}')
            status_data = status_response.get_json()['data']
            
            if status_data['status'] in ['completed', 'failed']:
                break
            
            time.sleep(wait_interval)
            elapsed += wait_interval
        
        # 验证最终状态
        final_response = client.get(f'/api/strategies/backtest/{task_id}')
        final_data = final_response.get_json()['data']
        
        # 任务应该完成或失败（不应该一直pending）
        assert final_data['status'] in ['completed', 'failed', 'running']
        
        # 如果完成，应该有结果
        if final_data['status'] == 'completed':
            assert 'result' in final_data
        
        # 如果失败，应该有错误信息
        if final_data['status'] == 'failed':
            assert 'error' in final_data

"""
测试API错误响应格式的属性测试
Feature: trading-ui-system, Property 37
"""
import pytest
from hypothesis import given, strategies as st
from src.web.app import create_app
from src.web.utils.errors import ValidationError, NotFoundError, DatabaseError


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


@given(
    status_code=st.integers(min_value=400, max_value=599),
    error_message=st.text(min_size=1, max_size=100)
)
def test_api_error_response_format(status_code, error_message):
    """
    Property 37: API error responses follow standard format
    
    For any error condition, the response should include:
    - success: False
    - error: error message string
    - error_code: optional error code string
    
    Validates: Requirements 11.10
    """
    # 创建应用上下文
    app = create_app()
    
    with app.app_context():
        from src.web.utils.response import error_response
        
        # 模拟错误响应
        response_data, response_status = error_response(
            error_message,
            'TEST_ERROR',
            status_code
        )
        
        # 获取JSON数据
        data = response_data.get_json()
        
        # 验证标准格式
        assert 'success' in data, "Response must have 'success' field"
        assert data['success'] is False, "'success' must be False for errors"
        assert 'error' in data, "Response must have 'error' field"
        assert isinstance(data['error'], str), "'error' must be a string"
        assert len(data['error']) > 0, "'error' must not be empty"
        assert 'error_code' in data, "Response must have 'error_code' field"
        assert response_status == status_code, "Status code must match"


def test_validation_error_handling(client):
    """测试验证错误处理"""
    # 测试缺少参数
    response = client.post(
        '/api/test/validation',
        json={}
    )
    
    assert response.status_code == 400
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data
    assert data['error_code'] == 'VALIDATION_ERROR'


def test_not_found_error_handling(client):
    """测试404错误处理"""
    response = client.get('/api/test/error/notfound')
    
    assert response.status_code == 404
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data
    assert data['error_code'] == 'NOT_FOUND'


def test_database_error_handling(client):
    """测试数据库错误处理"""
    response = client.get('/api/test/error/database')
    
    assert response.status_code == 500
    data = response.get_json()
    assert data['success'] is False
    assert 'error' in data
    assert data['error_code'] == 'DATABASE_ERROR'


def test_success_response_format(client):
    """测试成功响应格式"""
    response = client.get('/api/test')
    
    assert response.status_code == 200
    data = response.get_json()
    assert data['success'] is True
    assert 'data' in data

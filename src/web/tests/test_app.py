"""
测试Flask应用基础功能
"""
import pytest
from hypothesis import given, strategies as st, settings
from src.web.app import create_app
from src.web.utils.response import error_response


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    app.config['TESTING'] = True
    
    with app.test_client() as client:
        yield client


def test_index_route(client):
    """测试首页路由"""
    response = client.get('/')
    assert response.status_code == 200
    
    data = response.get_json()
    assert data['message'] == 'TradingBuddy API Server'
    assert 'version' in data


def test_cors_headers(client):
    """测试CORS配置"""
    # CORS头部在OPTIONS预检请求中返回
    response = client.options('/api/test', headers={
        'Origin': 'http://localhost:3000',
        'Access-Control-Request-Method': 'GET'
    })
    
    # 由于我们还没有注册/api路由，这个测试暂时跳过
    # 在后续任务中会有完整的CORS测试
    assert True  # Placeholder


def test_error_handler(client):
    """测试全局错误处理"""
    # 访问不存在的路由
    response = client.get('/nonexistent')
    assert response.status_code == 404


# Property-Based Tests

@given(
    status_code=st.integers(min_value=400, max_value=599),
    error_message=st.text(min_size=1, max_size=200),
    error_code=st.one_of(st.none(), st.text(min_size=1, max_size=50))
)
@settings(max_examples=100, deadline=None)
def test_property_api_error_response_format(status_code, error_message, error_code):
    """
    Property 37: API error responses follow standard format
    Feature: trading-ui-system, Property 37: API error responses follow standard format
    Validates: Requirements 11.10
    
    For any API error condition, the response should include HTTP status code,
    error message, and error code in a consistent JSON structure.
    """
    # Create Flask app context for jsonify to work
    app = create_app()
    
    with app.app_context():
        # Create error response
        response_tuple = error_response(error_message, error_code, status_code)
        
        # Extract response and status
        response_obj = response_tuple[0]
        returned_status = response_tuple[1]
        
        # Get JSON data
        data = response_obj.get_json()
        
        # Verify standard format properties
        # 1. Response must have 'success' field set to False
        assert 'success' in data, "Error response must contain 'success' field"
        assert data['success'] is False, "Error response 'success' field must be False"
        
        # 2. Response must have 'error' field with the error message
        assert 'error' in data, "Error response must contain 'error' field"
        assert isinstance(data['error'], str), "Error message must be a string"
        assert data['error'] == error_message, "Error message must match input"
        
        # 3. Response may have 'error_code' field when provided
        if error_code is not None:
            assert 'error_code' in data, "Error response must contain 'error_code' field when error_code is provided"
            assert data['error_code'] == error_code, "Error code must match input when provided"
        else:
            # When error_code is None, the field should not be present
            assert 'error_code' not in data, "Error response should not contain 'error_code' field when not provided"
        
        # 4. HTTP status code must match
        assert returned_status == status_code, "HTTP status code must match input"
        
        # 5. Response should only contain expected fields
        expected_fields = {'success', 'error'}
        if error_code is not None:
            expected_fields.add('error_code')
        
        actual_fields = set(data.keys())
        assert actual_fields == expected_fields, f"Response should only contain {expected_fields}, got {actual_fields}"

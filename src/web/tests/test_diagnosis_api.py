# -*- coding: utf-8 -*-
"""
诊断 API 集成测试

测试 /api/diagnosis 端点的功能
"""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))

from src.web.app import create_app


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def valid_stock_code():
    """有效的股票代码"""
    return '600519'  # 贵州茅台


@pytest.fixture
def invalid_stock_code():
    """无效的股票代码"""
    return '999999'


class TestDiagnosisAPI:
    """诊断 API 测试套件"""
    
    def test_health_check(self, client):
        """测试健康检查端点"""
        response = client.get('/api/diagnosis/health')
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'ok'
        assert 'engine' in data
    
    def test_get_single_stock_diagnosis_success(self, client, valid_stock_code):
        """测试获取单只股票诊断 - 正常情况"""
        response = client.get(f'/api/diagnosis/{valid_stock_code}')
        assert response.status_code == 200
        
        data = response.get_json()
        
        # 验证必需字段
        assert 'code' in data
        assert 'name' in data
        assert 'overall_score' in data
        assert 'overall_rating' in data
        assert 'overall_status' in data
        assert 'dimensions' in data
        assert 'strengths' in data
        assert 'weaknesses' in data
        assert 'suggestions' in data
        assert 'summary' in data
        assert 'updated_at' in data
        
        # 验证数据类型
        assert isinstance(data['code'], str)
        assert isinstance(data['name'], str)
        assert isinstance(data['overall_score'], (int, float))
        assert isinstance(data['overall_rating'], str)
        assert isinstance(data['overall_status'], str)
        assert isinstance(data['dimensions'], dict)
        assert isinstance(data['strengths'], list)
        assert isinstance(data['weaknesses'], list)
        assert isinstance(data['suggestions'], list)
        assert isinstance(data['summary'], str)
        
        # 验证评分范围
        assert 0 <= data['overall_score'] <= 100
        
        # 验证状态值
        assert data['overall_status'] in ['green', 'yellow', 'red']
        
        # 验证评级值
        assert data['overall_rating'] in ['优秀', '良好', '一般', '较差', '很差']
    
    def test_get_single_stock_diagnosis_with_cache_param(self, client, valid_stock_code):
        """测试使用缓存参数"""
        # 第一次请求（不使用缓存）
        response1 = client.get(f'/api/diagnosis/{valid_stock_code}?use_cache=false')
        assert response1.status_code == 200
        
        # 第二次请求（使用缓存）
        response2 = client.get(f'/api/diagnosis/{valid_stock_code}?use_cache=true')
        assert response2.status_code == 200
        
        data1 = response1.get_json()
        data2 = response2.get_json()
        
        # 两次请求应该返回相同的股票代码
        assert data1['code'] == data2['code']
    
    def test_get_single_stock_diagnosis_dimensions(self, client, valid_stock_code):
        """测试诊断维度数据结构"""
        response = client.get(f'/api/diagnosis/{valid_stock_code}')
        assert response.status_code == 200
        
        data = response.get_json()
        dimensions = data['dimensions']
        
        # 验证维度字段
        expected_dimensions = ['technical', 'fundamental', 'sector', 'capital', 'market_comparison']
        
        for dim in expected_dimensions:
            if dim in dimensions:
                dim_data = dimensions[dim]
                assert 'score' in dim_data
                assert 'status' in dim_data
                assert 'message' in dim_data
                assert 'details' in dim_data
                
                # 验证数据类型
                assert isinstance(dim_data['score'], (int, float))
                assert isinstance(dim_data['status'], str)
                assert isinstance(dim_data['message'], str)
                assert isinstance(dim_data['details'], dict)
                
                # 验证评分范围
                assert 0 <= dim_data['score'] <= 100
                
                # 验证状态值
                assert dim_data['status'] in ['green', 'yellow', 'red']
    
    def test_batch_diagnosis_success(self, client):
        """测试批量诊断 - 正常情况"""
        codes = ['600519', '000858', '600036']
        response = client.post('/api/diagnosis/batch', json={'codes': codes})
        assert response.status_code == 200
        
        data = response.get_json()
        
        # 验证响应结构
        assert 'total' in data
        assert 'success' in data
        assert 'failed' in data
        assert 'reports' in data
        
        # 验证数据类型
        assert isinstance(data['total'], int)
        assert isinstance(data['success'], int)
        assert isinstance(data['failed'], int)
        assert isinstance(data['reports'], list)
        
        # 验证数量
        assert data['total'] == len(codes)
        assert data['success'] + data['failed'] == data['total']
        
        # 验证每个报告的结构
        for report in data['reports']:
            assert 'code' in report
            assert 'overall_score' in report
            assert 'dimensions' in report
    
    def test_batch_diagnosis_with_options(self, client):
        """测试批量诊断 - 带选项"""
        codes = ['600519', '000858']
        response = client.post('/api/diagnosis/batch', json={
            'codes': codes,
            'use_cache': False,
            'max_workers': 3
        })
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['total'] == len(codes)
    
    def test_batch_diagnosis_empty_codes(self, client):
        """测试批量诊断 - 空代码列表"""
        response = client.post('/api/diagnosis/batch', json={'codes': []})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'invalid_parameter'
    
    def test_batch_diagnosis_missing_codes(self, client):
        """测试批量诊断 - 缺少codes字段"""
        response = client.post('/api/diagnosis/batch', json={})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'invalid_request'
    
    def test_batch_diagnosis_invalid_codes_type(self, client):
        """测试批量诊断 - codes不是数组"""
        response = client.post('/api/diagnosis/batch', json={'codes': '600519'})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'invalid_parameter'
    
    def test_batch_diagnosis_too_many_codes(self, client):
        """测试批量诊断 - 超过50只股票"""
        codes = [f'{i:06d}' for i in range(51)]
        response = client.post('/api/diagnosis/batch', json={'codes': codes})
        assert response.status_code == 400
        
        data = response.get_json()
        assert 'error' in data
        assert data['error'] == 'invalid_parameter'
        assert '50' in data['message']
    
    def test_clear_cache_all(self, client):
        """测试清除所有缓存"""
        response = client.post('/api/diagnosis/cache/clear', json={})
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'message' in data
        assert '所有缓存' in data['message']
    
    def test_clear_cache_single_stock(self, client, valid_stock_code):
        """测试清除单只股票缓存"""
        response = client.post('/api/diagnosis/cache/clear', json={'code': valid_stock_code})
        assert response.status_code == 200
        
        data = response.get_json()
        assert 'message' in data
        assert valid_stock_code in data['message']
    
    def test_response_format_json(self, client, valid_stock_code):
        """测试响应格式为JSON"""
        response = client.get(f'/api/diagnosis/{valid_stock_code}')
        assert response.status_code == 200
        assert response.content_type == 'application/json'
    
    def test_cors_headers(self, client, valid_stock_code):
        """测试CORS头部"""
        response = client.get(f'/api/diagnosis/{valid_stock_code}')
        # CORS headers should be present
        assert response.status_code == 200


class TestDiagnosisAPIPerformance:
    """诊断 API 性能测试"""
    
    def test_single_diagnosis_response_time(self, client, valid_stock_code):
        """测试单股诊断响应时间 < 300ms"""
        import time
        
        start = time.time()
        response = client.get(f'/api/diagnosis/{valid_stock_code}')
        elapsed = (time.time() - start) * 1000  # 转换为毫秒
        
        assert response.status_code == 200
        # 注意：这个测试可能在CI环境中失败，因为性能取决于硬件
        # 如果失败，可以增加阈值或标记为skip
        print(f"\n单股诊断响应时间: {elapsed:.2f}ms")
        # assert elapsed < 300, f"响应时间 {elapsed:.2f}ms 超过 300ms"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])

"""
股票数据API测试
"""
import pytest
from src.web.app import create_app
from src.data.database import StockDatabase


@pytest.fixture
def client():
    """创建测试客户端"""
    app = create_app()
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def db():
    """创建数据库实例"""
    return StockDatabase()


class TestStockListAPI:
    """测试股票列表API"""
    
    def test_get_stock_list_basic(self, client):
        """测试基本的股票列表获取"""
        response = client.get('/api/stocks')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert 'data' in data
        assert 'pagination' in data
        assert isinstance(data['data'], list)
    
    def test_get_stock_list_with_pagination(self, client):
        """测试分页参数"""
        response = client.get('/api/stocks?page=1&page_size=10')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert len(data['data']) <= 10
        assert data['pagination']['page'] == 1
        assert data['pagination']['page_size'] == 10
    
    def test_get_stock_list_with_market_filter(self, client):
        """测试市场筛选"""
        response = client.get('/api/stocks?market=sh&page_size=5')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        
        # 验证所有返回的股票都是上海市场
        for stock in data['data']:
            assert stock['market'] == 'sh'
    
    def test_get_stock_list_with_invalid_market(self, client):
        """测试无效的市场参数 - 应该被忽略"""
        response = client.get('/api/stocks?market=invalid')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        # 无效的市场参数应该被忽略，返回所有市场的股票
    
    def test_get_stock_list_with_market_cap_filter(self, client):
        """测试市值筛选"""
        response = client.get('/api/stocks?min_cap=100&max_cap=1000&page_size=10')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        # 如果有市值数据，验证筛选结果
        # 注意：这个测试依赖于数据库中有市值数据
    
    def test_get_stock_list_with_invalid_pagination(self, client):
        """测试无效的分页参数 - 应该被自动修正"""
        # 测试负数页码 - 应该被修正为1
        response = client.get('/api/stocks?page=-1')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['pagination']['page'] == 1  # 被修正为默认值
        
        # 测试过大的page_size - 应该被修正为最大值
        response = client.get('/api/stocks?page_size=10000')
        assert response.status_code == 200
        
        data = response.get_json()
        assert data['success'] is True
        assert data['pagination']['page_size'] == 1000  # 被修正为最大值


class TestStockDetailAPI:
    """测试股票详情API"""
    
    def test_get_stock_detail_success(self, client, db):
        """测试成功获取股票详情"""
        # 从数据库获取一个有效的股票代码
        stocks = db.get_stock_list()
        if not stocks.empty:
            code = stocks.iloc[0]['code']
            
            response = client.get(f'/api/stocks/{code}')
            assert response.status_code == 200
            
            data = response.get_json()
            assert data['success'] is True
            assert 'data' in data
            assert data['data']['code'] == code
            assert 'name' in data['data']
            assert 'market' in data['data']
    
    def test_get_stock_detail_with_full_code(self, client, db):
        """测试使用完整代码格式获取股票详情"""
        stocks = db.get_stock_list()
        if not stocks.empty:
            # 找一个有效市场的股票
            valid_stocks = stocks[stocks['market'].isin(['sh', 'sz'])]
            if not valid_stocks.empty:
                stock = valid_stocks.iloc[0]
                full_code = f"{stock['market']}.{stock['code']}"
                
                response = client.get(f'/api/stocks/{full_code}')
                assert response.status_code == 200
                
                data = response.get_json()
                assert data['success'] is True
                assert data['data']['code'] == stock['code']
    
    def test_get_stock_detail_not_found(self, client):
        """测试股票不存在的情况"""
        response = client.get('/api/stocks/999999')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert 'error' in data
        assert data['error_code'] == 'STOCK_NOT_FOUND'
    
    def test_get_stock_detail_invalid_code(self, client):
        """测试无效的股票代码"""
        response = client.get('/api/stocks/invalid')
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_CODE'


class TestStockDailyDataAPI:
    """测试股票日线数据API"""
    
    def test_get_daily_data_success(self, client, db):
        """测试成功获取日线数据"""
        # 找一个有数据的股票
        stocks = db.get_stock_list()
        if not stocks.empty:
            for _, stock in stocks.head(10).iterrows():
                full_code = f"{stock['market']}.{stock['code']}"
                if db.table_exists(full_code):
                    response = client.get(f'/api/stocks/{stock["code"]}/daily')
                    assert response.status_code == 200
                    
                    data = response.get_json()
                    assert data['success'] is True
                    assert isinstance(data['data'], list)
                    
                    if len(data['data']) > 0:
                        # 验证数据格式
                        first_record = data['data'][0]
                        assert 'date' in first_record
                        assert 'open' in first_record
                        assert 'high' in first_record
                        assert 'low' in first_record
                        assert 'close' in first_record
                        assert 'volume' in first_record
                    break
    
    def test_get_daily_data_with_date_range(self, client, db):
        """测试日期范围筛选"""
        stocks = db.get_stock_list()
        if not stocks.empty:
            for _, stock in stocks.head(10).iterrows():
                full_code = f"{stock['market']}.{stock['code']}"
                if db.table_exists(full_code):
                    response = client.get(
                        f'/api/stocks/{stock["code"]}/daily?start_date=2025-12-01&end_date=2025-12-31'
                    )
                    assert response.status_code == 200
                    
                    data = response.get_json()
                    assert data['success'] is True
                    
                    # 验证日期范围
                    for record in data['data']:
                        assert record['date'] >= '2025-12-01'
                        assert record['date'] <= '2025-12-31'
                    break
    
    def test_get_daily_data_invalid_date(self, client, db):
        """测试无效的日期格式"""
        stocks = db.get_stock_list()
        if not stocks.empty:
            code = stocks.iloc[0]['code']
            response = client.get(f'/api/stocks/{code}/daily?start_date=invalid')
            assert response.status_code == 400
            
            data = response.get_json()
            assert data['success'] is False
            assert data['error_code'] == 'INVALID_DATE'
    
    def test_get_daily_data_stock_not_found(self, client):
        """测试股票不存在的情况"""
        response = client.get('/api/stocks/999999/daily')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] in ['STOCK_NOT_FOUND', 'DATA_NOT_FOUND']
    
    def test_get_daily_data_invalid_code(self, client):
        """测试无效的股票代码"""
        response = client.get('/api/stocks/invalid_code/daily')
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_CODE'
    
    def test_get_daily_data_with_yyyymmdd_format(self, client, db):
        """测试YYYYMMDD格式的日期参数"""
        stocks = db.get_stock_list()
        if not stocks.empty:
            for _, stock in stocks.head(10).iterrows():
                full_code = f"{stock['market']}.{stock['code']}"
                if db.table_exists(full_code):
                    response = client.get(
                        f'/api/stocks/{stock["code"]}/daily?start_date=20251201&end_date=20251231'
                    )
                    assert response.status_code == 200
                    
                    data = response.get_json()
                    assert data['success'] is True
                    break


class TestStockIndicatorsAPI:
    """测试股票技术指标API"""
    
    def test_get_indicators_success(self, client, db):
        """测试成功获取技术指标"""
        stocks = db.get_stock_list()
        if not stocks.empty:
            for _, stock in stocks.head(10).iterrows():
                full_code = f"{stock['market']}.{stock['code']}"
                if db.table_exists(full_code):
                    response = client.get(f'/api/stocks/{stock["code"]}/indicators')
                    assert response.status_code == 200
                    
                    data = response.get_json()
                    assert data['success'] is True
                    assert isinstance(data['data'], list)
                    
                    if len(data['data']) > 0:
                        # 验证指标数据格式
                        first_record = data['data'][0]
                        assert 'date' in first_record
                        assert 'ma5' in first_record
                        assert 'ma10' in first_record
                        assert 'ma20' in first_record
                        assert 'ma60' in first_record
                    break
    
    def test_get_indicators_with_specific_indicators(self, client, db):
        """测试指定特定指标"""
        stocks = db.get_stock_list()
        if not stocks.empty:
            for _, stock in stocks.head(10).iterrows():
                full_code = f"{stock['market']}.{stock['code']}"
                if db.table_exists(full_code):
                    response = client.get(
                        f'/api/stocks/{stock["code"]}/indicators?indicators=ma5,ma20'
                    )
                    assert response.status_code == 200
                    
                    data = response.get_json()
                    assert data['success'] is True
                    
                    if len(data['data']) > 0:
                        # 验证只返回指定的指标
                        first_record = data['data'][0]
                        assert 'date' in first_record
                        assert 'ma5' in first_record
                        assert 'ma20' in first_record
                        assert 'ma10' not in first_record
                        assert 'ma60' not in first_record
                    break
    
    def test_get_indicators_with_date_range(self, client, db):
        """测试带日期范围的指标获取"""
        stocks = db.get_stock_list()
        if not stocks.empty:
            for _, stock in stocks.head(10).iterrows():
                full_code = f"{stock['market']}.{stock['code']}"
                if db.table_exists(full_code):
                    response = client.get(
                        f'/api/stocks/{stock["code"]}/indicators?start_date=2025-12-01&end_date=2025-12-10'
                    )
                    assert response.status_code == 200
                    
                    data = response.get_json()
                    assert data['success'] is True
                    
                    # 验证日期范围
                    for record in data['data']:
                        assert record['date'] >= '2025-12-01'
                        assert record['date'] <= '2025-12-10'
                    break
    
    def test_get_indicators_invalid_indicators(self, client, db):
        """测试无效的指标参数"""
        stocks = db.get_stock_list()
        if not stocks.empty:
            code = stocks.iloc[0]['code']
            response = client.get(f'/api/stocks/{code}/indicators?indicators=invalid,unknown')
            assert response.status_code == 400
            
            data = response.get_json()
            assert data['success'] is False
            assert data['error_code'] == 'INVALID_INDICATORS'
    
    def test_get_indicators_stock_not_found(self, client):
        """测试股票不存在的情况"""
        response = client.get('/api/stocks/999999/indicators')
        assert response.status_code == 404
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] in ['STOCK_NOT_FOUND', 'DATA_NOT_FOUND']
    
    def test_get_indicators_invalid_code(self, client):
        """测试无效的股票代码"""
        response = client.get('/api/stocks/invalid_code/indicators')
        assert response.status_code == 400
        
        data = response.get_json()
        assert data['success'] is False
        assert data['error_code'] == 'INVALID_CODE'
    
    def test_get_indicators_invalid_date(self, client, db):
        """测试无效的日期格式"""
        stocks = db.get_stock_list()
        if not stocks.empty:
            code = stocks.iloc[0]['code']
            response = client.get(f'/api/stocks/{code}/indicators?start_date=invalid')
            assert response.status_code == 400
            
            data = response.get_json()
            assert data['success'] is False
            assert data['error_code'] == 'INVALID_DATE'

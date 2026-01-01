"""
测试工具函数
"""
import pytest
from src.web.utils.validation import (
    is_valid_stock_code,
    is_valid_date,
    validate_pagination,
    validate_market
)


class TestValidation:
    """测试验证函数"""
    
    def test_valid_stock_codes(self):
        """测试有效的股票代码"""
        assert is_valid_stock_code('600000') is True
        assert is_valid_stock_code('sh.600000') is True
        assert is_valid_stock_code('sz.000001') is True
    
    def test_invalid_stock_codes(self):
        """测试无效的股票代码"""
        assert is_valid_stock_code('') is False
        assert is_valid_stock_code('abc') is False
        assert is_valid_stock_code('12345') is False
        assert is_valid_stock_code('1234567') is False
    
    def test_valid_dates(self):
        """测试有效的日期"""
        assert is_valid_date('2024-01-01') is True
        assert is_valid_date('20240101') is True
    
    def test_invalid_dates(self):
        """测试无效的日期"""
        assert is_valid_date('') is False
        assert is_valid_date('2024-13-01') is False
        assert is_valid_date('abc') is False
    
    def test_validate_pagination(self):
        """测试分页验证"""
        # 正常情况
        page, page_size = validate_pagination(1, 50)
        assert page == 1
        assert page_size == 50
        
        # 默认值
        page, page_size = validate_pagination(None, None)
        assert page == 1
        assert page_size == 50
        
        # 边界情况
        page, page_size = validate_pagination(0, 0)
        assert page == 1
        assert page_size == 50
        
        # 超过最大值
        page, page_size = validate_pagination(1, 2000)
        assert page_size == 1000
    
    def test_validate_market(self):
        """测试市场验证"""
        assert validate_market('sh') == 'sh'
        assert validate_market('SH') == 'sh'
        assert validate_market('sz') == 'sz'
        assert validate_market('invalid') is None
        assert validate_market(None) is None

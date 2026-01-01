"""
请求参数验证工具
"""
import re
from datetime import datetime
from typing import Optional


def is_valid_stock_code(code: str) -> bool:
    """
    验证股票代码格式
    
    Args:
        code: 股票代码（如 "600000" 或 "sh.600000"）
        
    Returns:
        是否有效
    """
    if not code:
        return False
    
    # 支持两种格式: "600000" 或 "sh.600000"
    pattern = r'^(sh\.|sz\.)?[0-9]{6}$'
    return bool(re.match(pattern, code))


def is_valid_date(date_str: str) -> bool:
    """
    验证日期格式
    
    Args:
        date_str: 日期字符串（YYYY-MM-DD 或 YYYYMMDD）
        
    Returns:
        是否有效
    """
    if not date_str:
        return False
    
    # 尝试两种格式
    formats = ['%Y-%m-%d', '%Y%m%d']
    
    for fmt in formats:
        try:
            datetime.strptime(date_str, fmt)
            return True
        except ValueError:
            continue
    
    return False


def validate_pagination(page: Optional[int], page_size: Optional[int]) -> tuple:
    """
    验证分页参数
    
    Args:
        page: 页码
        page_size: 每页大小
        
    Returns:
        (validated_page, validated_page_size)
    """
    # 默认值
    default_page = 1
    default_page_size = 50
    max_page_size = 1000
    
    # 验证page
    if page is None or page < 1:
        page = default_page
    
    # 验证page_size
    if page_size is None or page_size < 1:
        page_size = default_page_size
    elif page_size > max_page_size:
        page_size = max_page_size
    
    return page, page_size


def validate_market(market: Optional[str]) -> Optional[str]:
    """
    验证市场参数
    
    Args:
        market: 市场代码（sh/sz）
        
    Returns:
        验证后的市场代码，无效则返回None
    """
    if market is None:
        return None
    
    market = market.lower()
    if market in ['sh', 'sz']:
        return market
    
    return None
